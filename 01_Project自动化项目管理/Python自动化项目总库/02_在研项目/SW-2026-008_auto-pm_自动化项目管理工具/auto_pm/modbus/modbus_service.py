"""PLC-HMI 概念映射：Modbus TCP 联调测试服务（ModbusService）

像 PLC 功能块 FB_Modbus_Master，封装所有 Modbus TCP 通信和仿真逻辑：
- ping_host：网络层 ICMP 探路（系统 ping 命令，模拟返回值）
- connect / disconnect：建立或断开连接（仿真模式 / 真实模式预留）
- read_registers：读取寄存器数据（FC01/02/03/04/17/23）
- write_register：写入寄存器数据（FC05/06/15/16）
- scan_registers：并发扫描探测活跃地址区间
- export_config / import_config：JSON 配置导入导出

V1.0.0（仿真模式优先）：
- 不依赖 pymodbus，完全使用内置仿真信号发生器
- 仿真模式下生成正弦/余弦波形数据模拟真实 PLC 变量
- 真实 pymodbus 连接路径已预留注释，后续版本接入

设计参考：02_设计/Html原型预览/018_UI架构原型_V13.html
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────
# 数据结构定义
# ─────────────────────────────────────────────

@dataclass
class RegisterEntry:
    """单条寄存器数据（对齐 V13 监测表的一行）"""
    address: int          # 物理地址偏移（如：0 → 40001）
    physical: str         # 物理地址显示字符串（如：40001）
    tag: str              # 绑定符号注释（如：DB10.DBW0）
    dec: int              # 十进制值
    hex: str              # 十六进制字符串（如：0x04D2）
    float_decoded: str    # 32位浮点解码结果（如：3.14）
    is_coil: bool = False # 是否为线圈类型（FC01/FC02）


@dataclass
class PingResult:
    """Ping 探测结果"""
    success: bool
    message: str
    latency_ms: float = 0.0


@dataclass
class ModbusReadResult:
    """读取操作结果"""
    success: bool
    message: str
    registers: list[RegisterEntry] = field(default_factory=list)
    tx_hex: str = ""
    rx_hex: str = ""


@dataclass
class ModbusWriteResult:
    """写入操作结果"""
    success: bool
    message: str
    tx_hex: str = ""
    rx_hex: str = ""


@dataclass
class ScanCell:
    """扫描探测器单格结果"""
    offset: int    # 相对起始地址的偏移
    is_active: bool


# ─────────────────────────────────────────────
# 仿真信号发生器
# ─────────────────────────────────────────────

# 预置标签字典（对齐 V13 原型 siemens_fan / temp_monitor 预设）
_PRESET_TAGS: dict[str, list[dict[str, Any]]] = {
    "siemens_fan": [
        {"tag": "Fan_Start_CMD (启动给定)", "val": 1},
        {"tag": "Fan_Speed_SP (转速主给定)", "val": 3600},
        {"tag": "Fan_Status_Run (变频器运行)", "val": 1},
        {"tag": "Fan_Current_A (风机运行电流)", "val": 124},
        {"tag": "Fan_OutTemp_High (机壳排出温度H)", "val": 16540},
        {"tag": "Fan_OutTemp_Low (机壳排出温度L)", "val": 18840},
        {"tag": "Fan_Vibration (电机轴承振动)", "val": 15430},
        {"tag": "Fan_Warn_Code (系统告警字)", "val": 0},
    ],
    "temp_monitor": [
        {"tag": "Temp_Zone1_PT100 (炉温1区)", "val": None},  # None = 动态仿真
        {"tag": "Temp_Zone2_PT100 (炉温2区)", "val": None},
        {"tag": "Temp_Zone3_PT100 (炉温3区)", "val": None},
        {"tag": "Temp_Zone4_PT100 (炉温4区)", "val": 2200},
        {"tag": "Temp_Zone5_PT100 (炉温5区)", "val": 1950},
        {"tag": "Temp_Zone6_PT100 (炉温6区)", "val": 1780},
    ],
}

# 模拟活跃地址（扫描探测器用）
_ACTIVE_OFFSETS: set[int] = {0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 42, 43}


def _sim_val(index: int, preset: str, ts: float) -> tuple[int, str]:
    """生成仿真寄存器值和标签。

    Args:
        index: 寄存器序号（相对起始）
        preset: 预置名（custom/siemens_fan/temp_monitor）
        ts: 当前时间戳（用于波形计算）

    Returns:
        (十进制值, 标签)
    """
    tags = _PRESET_TAGS.get(preset, [])
    if index < len(tags):
        entry = tags[index]
        tag = entry["tag"]
        val = entry["val"]
        if val is None:
            # 动态正弦波形
            val = int(1800 + math.sin(ts / 4.0 + index) * 120)
        return val, tag

    # 自定义：随机波形
    val = int(1200 + math.sin(ts / 3.0 + index * 0.7) * 200)
    tag = f"DB10.DBW{index * 2}"
    return val, tag


def _decode_float_cdab(high: int, low: int) -> str:
    """CDAB（西门子 Word Swap）32位浮点解码。"""
    import struct
    try:
        # CDAB: bytes = [C, D, A, B] → swap words
        raw = (high << 16) | low
        # CDAB 字节序：低16位在高位，高16位在低位（Word Swap）
        swapped = ((raw & 0xFFFF) << 16) | ((raw >> 16) & 0xFFFF)
        result = struct.unpack(">f", swapped.to_bytes(4, "big"))[0]
        if math.isnan(result) or math.isinf(result):
            return "N/A"
        return f"{result:.3f}"
    except Exception:
        return "N/A"


def _build_hex_frame(transaction_id: int, slave: int, fc: int,
                     start: int, count: int) -> str:
    """构建 Modbus TCP 请求帧的 Hex 字符串。"""
    mbap = f"{transaction_id:04X} 0000 0006"
    pdu = f"0{slave:X} {fc:02X} {start:04X} {count:04X}"
    return f"{mbap} {pdu}".upper()


def _build_write_hex_frame(transaction_id: int, slave: int, fc: int,
                            addr: int, value: int) -> str:
    """构建写入请求帧 Hex 字符串。"""
    if fc in (15, 16):
        # 多写：附加字节计数（简化：假设单个值）
        mbap = f"{transaction_id:04X} 0000 0009"
        pdu = f"0{slave:X} {fc:02X} {addr:04X} 0001 02 {value:04X}"
    else:
        mbap = f"{transaction_id:04X} 0000 0006"
        pdu = f"0{slave:X} {fc:02X} {addr:04X} {value:04X}"
    return f"{mbap} {pdu}".upper()


# ─────────────────────────────────────────────
# 核心服务
# ─────────────────────────────────────────────

class ModbusService:
    """Modbus TCP 联调测试核心服务。

    主要特性：
    - 完整的仿真模式（无需 pymodbus 依赖）
    - 系统 ping 链路诊断
    - FC01/02/03/04/17/23 读取
    - FC05/06/15/16 写入
    - 并发寄存器区间扫描
    - JSON 配置导入导出

    PLC-HMI 概念映射：
    - 本类 ≈ FB_Modbus_Master（功能块）
    - connect() ≈ REQ 上升沿触发建立连接
    - read_registers() ≈ SEND/RECV 操作
    """

    def __init__(self) -> None:
        self._connected = False
        self._sim_mode = True
        self._ip = "192.168.1.10"
        self._port = 502
        self._slave_id = 1
        self._transaction_counter = 0

    # ── 内部工具 ─────────────────────────────────────────

    def _next_txn(self) -> int:
        self._transaction_counter = (self._transaction_counter + 1) & 0xFFFF
        return self._transaction_counter

    # ── 网络诊断 ─────────────────────────────────────────

    def ping_host(self, ip: str) -> PingResult:
        """执行 ICMP Ping 诊断。

        仿真模式不调用系统命令，直接返回成功。
        真实模式调用 subprocess ping（Windows/Linux 均兼容）。
        """
        if not ip or ip.strip() in ("0.0.0.0", ""):
            return PingResult(success=False, message="无效的 IP 地址", latency_ms=0)

        if self._sim_mode:
            # 仿真：直接返回成功，模拟 <1ms 延迟
            return PingResult(
                success=True,
                message=f"来自 {ip} 的回复: 字节=32 时间<1ms TTL=64",
                latency_ms=0.5,
            )

        # 真实模式：调用系统 ping
        try:
            param = "-n" if sys.platform == "win32" else "-c"
            result = subprocess.run(
                ["ping", param, "1", "-w", "1000", ip],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return PingResult(success=True, message=f"Ping OK → {ip}", latency_ms=1.0)
            else:
                return PingResult(success=False, message=f"Ping 超时 → {ip}", latency_ms=0)
        except Exception as e:
            return PingResult(success=False, message=f"Ping 异常: {e}", latency_ms=0)

    # ── 连接管理 ─────────────────────────────────────────

    def connect(
        self,
        ip: str,
        port: int,
        slave_id: int,
        sim_mode: bool = True,
    ) -> tuple[bool, str]:
        """建立 Modbus TCP 连接。

        Args:
            ip: 目标 PLC IP
            port: 端口（通常 502）
            slave_id: 站号 / Unit ID
            sim_mode: True=仿真模式, False=真实连接（预留）

        Returns:
            (success, log_message)
        """
        self._ip = ip
        self._port = port
        self._slave_id = slave_id
        self._sim_mode = sim_mode

        if sim_mode:
            self._connected = True
            return True, (
                f"[仿真] TCP Socket 握手成功 → {ip}:{port} (Unit={slave_id})。"
                " 已挂载本地信号发生器，Modbus TCP 端口 502 就绪！"
            )

        # 真实模式预留（后续接入 pymodbus）
        # from pymodbus.client import ModbusTcpClient
        # self._client = ModbusTcpClient(host=ip, port=port, timeout=3)
        # if self._client.connect():
        #     self._connected = True
        #     return True, f"TCP 握手成功 → {ip}:{port}"
        # return False, "连接失败：目标主机拒绝连接"
        self._connected = True
        return True, f"[预留-真实模式] 模拟连接 → {ip}:{port}"

    def disconnect(self) -> None:
        """断开连接，停止所有轮询。"""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ── 读取操作 ─────────────────────────────────────────

    def read_registers(
        self,
        fc: str,
        start: int,
        count: int,
        endian: str = "CDAB",
        preset: str = "custom",
    ) -> ModbusReadResult:
        """读取寄存器数据。

        Args:
            fc: 功能码字符串 ("01"/"02"/"03"/"04"/"17"/"23")
            start: 起始地址偏移
            count: 读取数量
            endian: 浮点字节序 (CDAB/ABCD/BADC/DCBA)
            preset: 预设配置名

        Returns:
            ModbusReadResult
        """
        if not self._connected:
            return ModbusReadResult(success=False, message="未连接设备")

        fc_int = int(fc)
        txn = self._next_txn()
        ts = time.time()

        # FC17：设备描述字（Report Slave ID）
        if fc_int == 17:
            tx_hex = f"{txn:04X} 0000 0002 0{self._slave_id:X} 11".upper()
            rx_payload = "61 75 74 6F 2D 70 6D 20 56 31 2E 30 20 50 4C 43 2D 53 49 4D"
            rx_hex = (
                f"{txn:04X} 0000 001E 0{self._slave_id:X} 11 1A FF 01 {rx_payload}".upper()
            )
            entry = RegisterEntry(
                address=0,
                physical="Slave ID",
                tag="Report Slave ID (FC17) — 设备描述字",
                dec=255,
                hex="0xFF",
                float_decoded="Product: auto-pm V1.0 PLC-SIM | Run=ON | FW=v2.16",
                is_coil=False,
            )
            return ModbusReadResult(
                success=True,
                message="FC17 设备描述字读取成功",
                registers=[entry],
                tx_hex=tx_hex,
                rx_hex=rx_hex,
            )

        is_coil = fc_int in (1, 2)
        tx_hex = _build_hex_frame(txn, self._slave_id, fc_int, start, count)

        entries: list[RegisterEntry] = []
        rx_byte_parts: list[str] = []

        for i in range(count):
            val, tag = _sim_val(i, preset, ts)

            if is_coil:
                val = 1 if val % 2 == 0 else 0
                tag = f"DB10.DBX0.{start + i}"
                hex_str = "0xFF" if val else "0x00"
                float_str = "ON" if val else "OFF"
                rx_byte_parts.append(f"{val:02X}")
            else:
                val = max(0, min(65535, val))
                hex_str = f"0x{val:04X}"
                rx_byte_parts.append(f"{val >> 8:02X}")
                rx_byte_parts.append(f"{val & 0xFF:02X}")

                # 浮点解码（每两个寄存器组合）
                if i % 2 == 0 and i + 1 < count:
                    next_val, _ = _sim_val(i + 1, preset, ts)
                    float_str = _decode_float_cdab(val, max(0, min(65535, next_val)))
                else:
                    float_str = "—"

            # 物理地址前缀
            addr_prefix = {1: 1, 2: 10001, 3: 40001, 4: 30001, 23: 40001}.get(fc_int, 40001)
            physical = str(addr_prefix + start + i)

            entries.append(RegisterEntry(
                address=start + i,
                physical=physical,
                tag=tag,
                dec=val,
                hex=hex_str,
                float_decoded=float_str,
                is_coil=is_coil,
            ))

        byte_count = len(rx_byte_parts)
        rx_header = f"{txn:04X} 0000 {byte_count + 3:04X} 0{self._slave_id:X} {fc_int:02X} {byte_count:02X}"
        rx_hex = f"{rx_header} {' '.join(rx_byte_parts)}".upper()

        return ModbusReadResult(
            success=True,
            message=f"FC{fc_int:02d} 读取成功，共 {count} 个寄存器",
            registers=entries,
            tx_hex=tx_hex,
            rx_hex=rx_hex,
        )

    # ── 写入操作 ─────────────────────────────────────────

    def write_register(
        self,
        write_fc: str,
        addr: int,
        value: int,
    ) -> ModbusWriteResult:
        """写入寄存器数据。

        Args:
            write_fc: 写入功能码 ("05"/"06"/"15"/"16")
            addr: 目标偏移地址
            value: 写入数值

        Returns:
            ModbusWriteResult
        """
        if not self._connected:
            return ModbusWriteResult(success=False, message="未连接设备")

        fc_int = int(write_fc)
        txn = self._next_txn()
        tx_hex = _build_write_hex_frame(txn, self._slave_id, fc_int, addr, value)

        # 仿真：直接返回回显（echo back）
        rx_hex = tx_hex  # FC06 正常回显请求帧

        addr_prefix = {5: 1, 15: 1, 6: 40001, 16: 40001}.get(fc_int, 40001)
        physical = str(addr_prefix + addr)

        return ModbusWriteResult(
            success=True,
            message=f"[FC{fc_int:02d}] 写入物理地址 {physical} = {value} 成功",
            tx_hex=tx_hex,
            rx_hex=rx_hex,
        )

    # ── 寄存器扫描 ───────────────────────────────────────

    def scan_registers(
        self,
        start_offset: int = 0,
        end_offset: int = 99,
    ) -> list[ScanCell]:
        """扫描寄存器区间，返回活跃地址列表。

        仿真模式下按预定义活跃地址集合返回；
        真实模式预留（后续用 FC03 逐地址探测）。

        Args:
            start_offset: 起始偏移
            end_offset: 结束偏移（包含）

        Returns:
            ScanCell 列表
        """
        if not self._connected:
            return []

        cells: list[ScanCell] = []
        for offset in range(start_offset, end_offset + 1):
            is_active = offset in _ACTIVE_OFFSETS
            cells.append(ScanCell(offset=offset, is_active=is_active))
        return cells

    # ── JSON 配置导入导出 ────────────────────────────────

    def export_config(self, path: str) -> tuple[bool, str]:
        """导出当前连接配置为 JSON 文件。"""
        config = {
            "ip": self._ip,
            "port": self._port,
            "slave_id": self._slave_id,
            "sim_mode": self._sim_mode,
            "version": "1.0",
        }
        try:
            Path(path).write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            return True, f"配置已导出至 {path}"
        except Exception as e:
            return False, f"导出失败: {e}"

    def import_config(self, path: str) -> tuple[bool, str, dict[str, Any]]:
        """从 JSON 文件导入连接配置。

        Returns:
            (success, message, config_dict)
        """
        try:
            config = json.loads(Path(path).read_text(encoding="utf-8"))
            self._ip = config.get("ip", self._ip)
            self._port = int(config.get("port", self._port))
            self._slave_id = int(config.get("slave_id", self._slave_id))
            self._sim_mode = bool(config.get("sim_mode", True))
            return True, f"配置已从 {path} 导入", config
        except Exception as e:
            return False, f"导入失败: {e}", {}
