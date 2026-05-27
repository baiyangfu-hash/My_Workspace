# -*- coding: utf-8 -*-
"""
全自动化的交付物整理 + 打包脚本

功能概述:
    1. Phase 1: 准备与校验 - 读取版本号、验证三处版本一致性
    2. Phase 2: 数据库预处理 - 同步DB、清理绝对路径、验证数据完整性
    3. Phase 3: PyInstaller 打包 - 编译生成可执行文件
    4. Phase 4: 交付物组装 - 整理交付物目录结构
    5. Phase 5: 归档与记录 - 生成ZIP归档、更新版本记录文档

使用方式:
    python package.py                      # 完整打包
    python package.py --version 2.6.0      # 覆盖版本号（跳过version.py读取）
    python package.py --dry-run            # 试运行（只打印不执行）
    python package.py --clean              # 清理build/dist后重新打包
    python package.py --help               # 帮助信息

作者: 项目组
创建日期: 2026-04-17
"""

import argparse
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

# ============================================================================
# 路径常量定义（硬编码项目结构关键路径）
# ============================================================================

# 源码目录（本脚本所在目录）
SRC_DIR = Path(__file__).resolve().parent

# 项目根目录（回退3级到 SW-2026-004_Python项目管理工具）
PROJECT_ROOT = SRC_DIR.parent.parent.parent

# 源码数据库
SOURCE_DB = SRC_DIR / "data" / "project_manager.db"

# 源码配置目录
SOURCE_CONFIG = SRC_DIR / "config"

# 版本文件
VERSION_FILE = SRC_DIR / "src" / "core" / "version.py"

# PyInstaller 输出目录和文件
DIST_DIR = SRC_DIR / "dist"
EXE_NAME = "Python项目管理工具.exe"
SPEC_FILE = SRC_DIR / "Python项目管理工具.spec"

# 交付物目录
DELIVERY_DIR = PROJECT_ROOT / "06_交付物"
DELIVERY_BIN_DIR = DELIVERY_DIR / "01_可执行文件"
DELIVERY_DOCS_DIR = DELIVERY_DIR / "02_发布说明"
DELIVERY_DATA_DIR = DELIVERY_DIR / "data"          # 备份位置
DELIVERY_PACK_DIR = PROJECT_ROOT / "06_交付物打包"

# ZIP 命名格式
ZIP_PATTERN = "Python自动化项目管理系统_V{version}_{date}.zip"

# 打包版本记录文件
VERSION_RECORD_FILE = DELIVERY_PACK_DIR / "打包版本记录.md"

# 最小EXE大小阈值 (50MB)
MIN_EXE_SIZE_BYTES = 50 * 1024 * 1024

# ============================================================================
# 日志配置
# ============================================================================

def setup_logging() -> logging.Logger:
    """
    配置日志系统，返回主logger实例。

    Returns:
        logging.Logger: 配置好的logger对象
    """
    logger = logging.getLogger("package")
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 格式化器
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-5s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 全局logger实例
log = setup_logging()


# ============================================================================
# 工具函数
# ============================================================================

def format_size(size_bytes: int) -> str:
    """
    将字节数转换为人类可读的文件大小字符串。

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        str: 格式化后的大小字符串，如 "57.95 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def ensure_directory(path: Path, dry_run: bool = False) -> bool:
    """
    确保目录存在，不存在则创建。

    Args:
        path: 目标目录路径
        dry_run: 是否为试运行模式

    Returns:
        bool: 操作是否成功
    """
    if not path.exists():
        if dry_run:
            log.info(f"  [DRY-RUN] 将创建目录: {path}")
            return True
        try:
            path.mkdir(parents=True, exist_ok=True)
            log.info(f"  [OK] 目录已创建: {path}")
            return True
        except OSError as e:
            log.error(f"  [FAIL] 创建目录失败: {path}, 错误: {e}")
            return False
    else:
        log.debug(f"  [SKIP] 目录已存在: {path}")
        return True


def copy_file_safe(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """
    安全复制文件，自动创建目标目录。

    Args:
        src: 源文件路径
        dst: 目标文件路径
        dry_run: 是否为试运行模式

    Returns:
        bool: 操作是否成功
    """
    if not src.exists():
        log.error(f"  [FAIL] 源文件不存在: {src}")
        return False

    # 确保目标目录存在
    dst.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        log.info(f"  [DRY-RUN] 将复制: {src} -> {dst}")
        return True

    try:
        shutil.copy2(src, dst)
        log.info(f"  [OK] 文件已复制: {src.name} -> {dst.parent}")
        return True
    except OSError as e:
        log.error(f"  [FAIL] 复制文件失败: {src} -> {dst}, 错误: {e}")
        return False


# ============================================================================
# Phase 1: 准备与校验
# ============================================================================

def read_version(override_version: Optional[str] = None) -> str:
    """
    从 version.py 读取 VERSION 变量，或使用命令行覆盖值。

    使用正则表达式解析 VERSION = "x.y.z" 格式的版本号。

    Args:
        override_version: 命令行指定的覆盖版本号，为None时从文件读取

    Returns:
        str: 解析出的版本号字符串

    Raises:
        SystemExit: 当无法读取或解析版本号时退出程序
    """
    if override_version:
        log.info(f"使用命令行覆盖版本号: {override_version}")
        # 验证版本号格式
        if not re.match(r'^\d+\.\d+\.\d+$', override_version):
            log.error(f"[FAIL] 版本号格式无效: {override_version}，期望格式 x.y.z")
            sys.exit(1)
        return override_version

    if not VERSION_FILE.exists():
        log.error(f"[FAIL] 版本文件不存在: {VERSION_FILE}")
        sys.exit(1)

    try:
        content = VERSION_FILE.read_text(encoding="utf-8")
        match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1)
            log.info(f"从 version.py 读取版本号: {version}")
            return version
        else:
            log.error("[FAIL] 无法在 version.py 中找到 VERSION 变量")
            sys.exit(1)
    except Exception as e:
        log.error(f"[FAIL] 读取版本文件失败: {e}")
        sys.exit(1)


def verify_version_consistency(version_str: str) -> bool:
    """
    校验三处版本号一致性:
        1. version.py 的 VERSION 变量
        2. config/app_config.json 的 version 字段
        3. 06_交付物/01_可执行文件/config/app_config.json 的 version 字段

    不一致则打印差异详情并返回 False。

    Args:
        version_str: 基准版本号字符串

    Returns:
        bool: 三处版本号是否一致
    """
    log.info("=" * 60)
    log.info("Phase 1: 版本一致性校验")
    log.info("=" * 60)

    discrepancies: List[str] = []

    # 1. 校验 version.py
    try:
        content = VERSION_FILE.read_text(encoding="utf-8")
        match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
        file_version = match.group(1) if match else "未找到"
        if file_version != version_str:
            discrepancies.append(
                f"  - version.py: {file_version} (期望: {version_str})"
            )
        else:
            log.info(f"  [OK] version.py: {file_version}")
    except Exception as e:
        discrepancies.append(f"  - version.py: 读取失败 ({e})")

    # 2. 校验源码 app_config.json
    source_app_config = SOURCE_CONFIG / "app_config.json"
    if source_app_config.exists():
        try:
            with open(source_app_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                config_version = config_data.get("version", "未找到")
                if config_version != version_str:
                    discrepancies.append(
                        f"  - 源码 config/app_config.json: {config_version} "
                        f"(期望: {version_str})"
                    )
                else:
                    log.info(f"  [OK] 源码 config/app_config.json: {config_version}")
        except Exception as e:
            discrepancies.append(
                f"  - 源码 config/app_config.json: 解析失败 ({e})"
            )
    else:
        discrepancies.append("  - 源码 config/app_config.json: 文件不存在")

    # 3. 校验交付物 app_config.json
    delivery_app_config = DELIVERY_BIN_DIR / "config" / "app_config.json"
    if delivery_app_config.exists():
        try:
            with open(delivery_app_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                config_version = config_data.get("version", "未找到")
                if config_version != version_str:
                    discrepancies.append(
                        f"  - 交付物 config/app_config.json: {config_version} "
                        f"(期望: {version_str})"
                    )
                else:
                    log.info(f"  [OK] 交付物 config/app_config.json: {config_version}")
        except Exception as e:
            discrepancies.append(
                f"  - 交付物 config/app_config.json: 解析失败 ({e})"
            )
    else:
        log.warning("  [WARN] 交付物 config/app_config.json: 文件不存在（首次打包正常）")

    # 输出结果
    if discrepancies:
        log.warning("[WARN] 发现以下版本不一致:")
        for disc in discrepancies:
            log.warning(disc)
        return False
    else:
        log.info("[OK] 所有版本号一致: V%s", version_str)
        return True


# ============================================================================
# Phase 2: 数据库预处理
# ============================================================================

def sync_database(dry_run: bool = False) -> bool:
    """
    执行数据库同步与预处理操作:

        Step 1: 复制源码 DB 到两个交付物位置
              - 06_交付物/01_可执行文件/data/project_manager.db
              - 06_交付物/data/project_manager.db (备份)

        Step 2: 清理绝对路径 root_path
              UPDATE libraries SET root_path='' WHERE root_path LIKE '%:%'

        Step 3: 验证数据完整性
              - categories 表记录数 >= 5
              - projects 表记录数 >= 1
              - libraries.root_path 无含盘符的值

    Args:
        dry_run: 是否为试运行模式

    Returns:
        bool: 数据库预处理是否全部成功
    """
    log.info("=" * 60)
    log.info("Phase 2: 数据库预处理")
    log.info("=" * 60)

    success = True

    # Step 1: 验证源码DB是否存在
    if not SOURCE_DB.exists():
        log.error(f"  [FAIL] 源码数据库不存在: {SOURCE_DB}")
        return False
    log.info(f"  [OK] 源码数据库存在: {SOURCE_DB}")

    # Step 2: 复制到交付物位置 1 - 01_可执行文件/data/
    target_db_1 = DELIVERY_BIN_DIR / "data" / "project_manager.db"
    if not copy_file_safe(SOURCE_DB, target_db_1, dry_run=dry_run):
        success = False

    # Step 3: 复制到交付物位置 2 - 06_交付物/data/ (备份)
    target_db_2 = DELIVERY_DATA_DIR / "project_manager.db"
    if not copy_file_safe(SOURCE_DB, target_db_2, dry_run=dry_run):
        success = False

    # Step 4: 清理绝对路径 root_path（对两个目标DB都操作）
    for target_db in [target_db_1, target_db_2]:
        if target_db.exists():
            cleaned_count = clean_root_paths(target_db, dry_run=dry_run)
            if cleaned_count > 0:
                log.info(f"  [OK] {target_db.parent}: 已清理 {cleaned_count} 条绝对路径记录")

    # Step 5: 验证数据完整性（只验证目标DB）
    if target_db_1.exists():
        integrity_ok = verify_database_integrity(target_db_1)
        if not integrity_ok:
            success = False

    if success:
        log.info("[OK] 数据库预处理完成")
    else:
        log.error("[FAIL] 数据库预处理存在问题")

    return success


def clean_root_paths(db_path: Path, dry_run: bool = False) -> int:
    """
    清理数据库中含盘符的 root_path 记录。

    执行 SQL: UPDATE libraries SET root_path='' WHERE root_path LIKE '%:%'

    Args:
        db_path: SQLite 数据库文件路径
        dry_run: 是否为试运行模式

    Returns:
        int: 清理的记录数
    """
    if dry_run:
        log.info(f"  [DRY-RUN] 将清理 {db_path} 中的绝对路径 root_path")
        return 0

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 先查询有多少条需要清理
        cursor.execute(
            "SELECT COUNT(*) FROM libraries WHERE root_path LIKE '%:%'"
        )
        count = cursor.fetchone()[0]

        if count > 0:
            # 执行清理
            cursor.execute(
                "UPDATE libraries SET root_path='' WHERE root_path LIKE '%:%'"
            )
            conn.commit()
            log.debug(f"    已清理 {count} 条 root_path 绝对路径记录")

        conn.close()
        return count
    except sqlite3.Error as e:
        log.error(f"  [FAIL] 清理 root_path 失败: {e}")
        return 0


def verify_database_integrity(db_path: Path) -> bool:
    """
    验证数据库数据完整性:
        - categories 表记录数 >= 5
        - projects 表记录数 >= 1
        - libraries.root_path 无含盘符的值

    Args:
        db_path: 要验证的SQLite数据库路径

    Returns:
        bool: 数据完整性检查是否通过
    """
    log.info(f"  验证数据完整性: {db_path.name}")

    all_passed = True

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 检查 categories 表记录数
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        if cat_count >= 5:
            log.info(f"    [OK] categories 表: {cat_count} 条记录")
        else:
            log.warning(f"    [WARN] categories 表: 仅 {cat_count} 条记录 (期望 >= 5)")
            all_passed = False

        # 检查 projects 表记录数
        cursor.execute("SELECT COUNT(*) FROM projects")
        proj_count = cursor.fetchone()[0]
        if proj_count >= 1:
            log.info(f"    [OK] projects 表: {proj_count} 条记录")
        else:
            log.warning(f"    [WARN] projects 表: 仅 {proj_count} 条记录 (期望 >= 1)")
            all_passed = False

        # 检查 libraries.root_path 是否有含盘符的值
        cursor.execute(
            "SELECT COUNT(*) FROM libraries WHERE root_path LIKE '%:%'"
        )
        bad_path_count = cursor.fetchone()[0]
        if bad_path_count == 0:
            log.info(f"    [OK] libraries.root_path: 无含盘符的值")
        else:
            log.error(
                f"    [FAIL] libraries.root_path: 仍有 {bad_path_count} 条含盘符记录"
            )
            all_passed = False

        conn.close()
    except sqlite3.Error as e:
        log.error(f"    [FAIL] 数据库验证异常: {e}")
        all_passed = False

    return all_passed


# ============================================================================
# Phase 3: PyInstaller 打包
# ============================================================================

def run_pyinstaller(clean: bool = False, dry_run: bool = False) -> Tuple[bool, Optional[int]]:
    """
    执行 PyInstaller 打包流程:

        Step 1: 如果 clean=True，清理 build/ 和 dist/ 目录
        Step 2: 执行 pyinstaller --noconfirm Python项目管理工具.spec
        Step 3: 验证 EXE 存在且大小 > 50MB

    Args:
        clean: 是否先清理 build 和 dist 目录
        dry_run: 是否为试运行模式

    Returns:
        Tuple[bool, Optional[int]]: (是否成功, EXE文件大小字节)，失败时大小为None
    """
    log.info("=" * 60)
    log.info("Phase 3: PyInstaller 打包")
    log.info("=" * 60)

    exe_path = DIST_DIR / EXE_NAME

    # Step 1: 清理旧构建产物
    if clean:
        build_dir = SRC_DIR / "build"
        for dir_to_clean in [build_dir, DIST_DIR]:
            if dir_to_clean.exists():
                if dry_run:
                    log.info(f"  [DRY-RUN] 将删除目录: {dir_to_clean}")
                else:
                    try:
                        shutil.rmtree(dir_to_clean)
                        log.info(f"  [OK] 已清理目录: {dir_to_clean.name}/")
                    except OSError as e:
                        log.error(f"  [FAIL] 清理目录失败: {dir_to_clean}, 错误: {e}")
                        return False, None

    # Step 2: 检查 spec 文件
    if not SPEC_FILE.exists():
        log.error(f"  [FAIL] Spec 文件不存在: {SPEC_FILE}")
        return False, None
    log.info(f"  [OK] Spec 文件存在: {SPEC_FILE.name}")

    # Step 3: 执行 pyinstaller
    if dry_run:
        log.info(
            f"  [DRY-RUN] 将执行: "
            f"pyinstaller --noconfirm \"{SPEC_FILE.name}\""
        )
        # 返回模拟成功
        return True, MIN_EXE_SIZE_BYTES + 1000000

    log.info("  正在执行 PyInstaller 打包...")
    try:
        result = subprocess.run(
            ["pyinstaller", "--noconfirm", str(SPEC_FILE)],
            cwd=str(SRC_DIR),
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )

        if result.returncode != 0:
            log.error(f"  [FAIL] PyInstaller 执行失败 (退出码: {result.returncode})")
            if result.stderr:
                log.error(f"    错误输出:\n{result.stderr[-500:]}")  # 只显示最后500字符
            return False, None

        log.info("  [OK] PyInstaller 执行成功")

    except subprocess.TimeoutExpired:
        log.error("  [FAIL] PyInstaller 执行超时（超过10分钟）")
        return False, None
    except FileNotFoundError:
        log.error("  [FAIL] 未找到 pyinstaller 命令，请确认已安装: pip install pyinstaller")
        return False, None
    except Exception as e:
        log.error(f"  [FAIL] PyInstaller 执行异常: {e}")
        return False, None

    # Step 4: 验证 EXE 文件
    if not exe_path.exists():
        log.error(f"  [FAIL] 生成的 EXE 文件不存在: {exe_path}")
        return False, None

    exe_size = exe_path.stat().st_size
    log.info(f"  [OK] EXE 文件已生成: {EXE_NAME} ({format_size(exe_size)})")

    if exe_size < MIN_EXE_SIZE_BYTES:
        log.warning(
            f"  [WARN] EXE 文件偏小 ({format_size(exe_size)})，"
            f"可能打包不完整（阈值: {format_size(MIN_EXE_SIZE_BYTES)}）"
        )

    return True, exe_size


# ============================================================================
# Phase 4: 交付物组装
# ============================================================================

def assemble_delivery(version: str, dry_run: bool = False) -> bool:
    """
    整理 06_交付物/01_可执行文件/ 目录结构:

        1. 复制 dist/Python项目管理工具.exe → 01_可执行文件/
        2. 确保 config/ 目录有4个JSON文件（从源码config复制）
        3. 确保 data/project_manager.db 已同步清理
        4. 确保 Projects/.gitkeep 存在

    Args:
        version: 当前版本号
        dry_run: 是否为试运行模式

    Returns:
        bool: 组装是否成功
    """
    log.info("=" * 60)
    log.info("Phase 4: 交付物组装")
    log.info("=" * 60)

    success = True

    # 确保基础目录存在
    if not ensure_directory(DELIVERY_BIN_DIR, dry_run=dry_run):
        return False

    # Step 1: 复制 EXE 文件
    exe_src = DIST_DIR / EXE_NAME
    exe_dst = DELIVERY_BIN_DIR / EXE_NAME
    log.info(f"  复制 EXE 文件...")
    if not copy_file_safe(exe_src, exe_dst, dry_run=dry_run):
        success = False

    # Step 2: 同步配置文件（确保4个JSON文件）
    log.info(f"  同步配置文件...")
    config_files = [
        "app_config.json",
        "api_config.json",
        "database_config.json",
        "spec_version_config.json"
    ]
    config_target_dir = DELIVERY_BIN_DIR / "config"

    for cfg_file in config_files:
        cfg_src = SOURCE_CONFIG / cfg_file
        cfg_dst = config_target_dir / cfg_file
        if not copy_file_safe(cfg_src, cfg_dst, dry_run=dry_run):
            success = False

    # Step 3: 更新交付物 app_config.json 的版本号
    delivery_config = config_target_dir / "app_config.json"
    if delivery_config.exists() and not dry_run:
        try:
            with open(delivery_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            old_version = config_data.get("version", "未知")
            config_data["version"] = version
            with open(delivery_config, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            log.info(
                f"  [OK] 交付物 app_config.json 版本号: "
                f"{old_version} -> {version}"
            )
        except Exception as e:
            log.error(f"  [FAIL] 更新交付物版本号失败: {e}")
            success = False

    # Step 4: 确保 Projects/.gitkeep 存在
    projects_dir = DELIVERY_DIR / "Projects"
    gitkeep_file = projects_dir / ".gitkeep"

    if not ensure_directory(projects_dir, dry_run=dry_run):
        success = False

    if not gitkeep_file.exists():
        if dry_run:
            log.info(f"  [DRY-RUN] 将创建: {gitkeep_file}")
        else:
            try:
                gitkeep_file.write_text("", encoding="utf-8")
                log.info(f"  [OK] 已创建: .gitkeep")
            except OSError as e:
                log.error(f"  [FAIL] 创建 .gitkeep 失败: {e}")
                success = False
    else:
        log.debug(f"  [SKIP] .gitkeep 已存在")

    if success:
        log.info("[OK] 交付物组装完成")
    else:
        log.error("[FAIL] 交付物组装存在问题")

    return success


# ============================================================================
# Phase 5: 归档与记录
# ============================================================================

def create_zip_archive(version: str, dry_run: bool = False) -> Tuple[bool, Optional[int]]:
    """
    创建 ZIP 归档并更新版本记录:

        Step 1: 将 06_交付物/01_可执行文件/ 整个目录打包为 ZIP
        Step 2: 放入 06_交付物打包/
        Step 3: 文件名: Python自动化项目管理系统_V{x.y.z}_{YYYYMMDD}.zip
        Step 4: 更新 打包版本记录.md，追加新版本记录

    Args:
        version: 当前版本号
        dry_run: 是否为试运行模式

    Returns:
        Tuple[bool, Optional[int]]: (是否成功, ZIP文件大小字节)
    """
    log.info("=" * 60)
    log.info("Phase 5: 归档与记录")
    log.info("=" * 60)

    # 确保打包目录存在
    if not ensure_directory(DELIVERY_PACK_DIR, dry_run=dry_run):
        return False, None

    # 生成 ZIP 文件名
    today_str = datetime.now().strftime("%Y%m%d")
    zip_filename = ZIP_PATTERN.format(version=version, date=today_str)
    zip_path = DELIVERY_PACK_DIR / zip_filename

    # Step 1: 创建 ZIP 归档
    if zip_path.exists():
        if dry_run:
            log.info(f"  [DRY-RUN] 将覆盖已有 ZIP: {zip_filename}")
        else:
            log.warning(f"  [WARN] ZIP 文件已存在，将被覆盖: {zip_filename}")

    if dry_run:
        log.info(
            f"  [DRY-RUN] 将创建 ZIP: {zip_filename}\n"
            f"           来源: {DELIVERY_BIN_DIR}/"
        )
        zip_size = 60 * 1024 * 1024  # 模拟 60MB
    else:
        try:
            log.info(f"  正在创建 ZIP 归档: {zip_filename}")
            zip_size = create_zip_from_directory(
                DELIVERY_BIN_DIR,
                zip_path,
                arcname_prefix=f"01_可执行文件"
            )
            log.info(f"  [OK] ZIP 归档已创建: {zip_filename} ({format_size(zip_size)})")
        except Exception as e:
            log.error(f"  [FAIL] 创建 ZIP 归档失败: {e}")
            return False, None

    # Step 2: 更新版本记录文档
    update_version_record(version, today_str, zip_filename, zip_size, dry_run=dry_run)

    return True, zip_size


def create_zip_from_directory(
    source_dir: Path,
    output_zip: Path,
    arcname_prefix: str = ""
) -> int:
    """
    将指定目录打包为 ZIP 文件。

    Args:
        source_dir: 要打包的源目录
        output_zip: 输出的 ZIP 文件路径
        arcname_prefix: ZIP 内部路径前缀

    Returns:
        int: ZIP 文件大小（字节）

    Raises:
        OSError: 当写入 ZIP 文件失败时抛出
    """
    file_count = 0
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                # 计算 ZIP 内部的相对路径
                relative = file_path.relative_to(source_dir)
                if arcname_prefix:
                    arc_name = f"{arcname_prefix}/{relative}"
                else:
                    arc_name = str(relative)
                zf.write(file_path, arc_name)
                file_count += 1

    log.info(f"    共打包 {file_count} 个文件")
    return output_zip.stat().st_size


def update_version_record(
    version: str,
    date_str: str,
    zip_filename: str,
    zip_size: int,
    dry_run: bool = False
) -> bool:
    """
    更新 打包版本记录.md，在表格中追加一行新版本记录。

    Args:
        version: 版本号
        date_str: 日期字符串 (YYYYMMDD)
        zip_filename: ZIP 文件名
        zip_size: ZIP 文件大小（字节）
        dry_run: 是否为试运行模式

    Returns:
        bool: 更新是否成功
    """
    if dry_run:
        log.info(
            f"  [DRY-RUN] 将更新版本记录:\n"
            f"           追加行: | V{version} | {date_str[:4]}-{date_str[4:6]}-{date_str[6:]} | "
            f"{zip_filename} | {format_size(zip_size)} | 已发布 |"
        )
        return True

    if not VERSION_RECORD_FILE.exists():
        log.warning(f"  [WARN] 版本记录文件不存在，将新建: {VERSION_RECORD_FILE}")
        record_content = build_new_version_record(version, date_str, zip_filename, zip_size)
    else:
        try:
            existing_content = VERSION_RECORD_FILE.read_text(encoding="utf-8")
            record_content = append_version_row(
                existing_content,
                version,
                date_str,
                zip_filename,
                zip_size
            )
        except Exception as e:
            log.error(f"  [FAIL] 读取版本记录文件失败: {e}")
            return False

    try:
        VERSION_RECORD_FILE.write_text(record_content, encoding="utf-8")
        log.info(f"  [OK] 版本记录已更新: V{version}")
        return True
    except OSError as e:
        log.error(f"  [FAIL] 写入版本记录文件失败: {e}")
        return False


def build_new_version_record(
    version: str,
    date_str: str,
    zip_filename: str,
    zip_size: int
) -> str:
    """
    构建新的版本记录文档内容（当原文件不存在时使用）。

    Args:
        version: 版本号
        date_str: 日期字符串 (YYYYMMDD)
        zip_filename: ZIP 文件名
        zip_size: ZIP 文件大小（字节）

    Returns:
        str: 完整的 Markdown 文档内容
    """
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""# 打包版本记录

> **文档版本**: V1.0.0
> **最后更新**: {now}
> **维护人**: 项目组

---

## 一、已发布版本清单

| 版本号 | 发布日期 | 包文件名 | 大小 | 状态 |
|--------|----------|----------|------|------|
| V{version} | {formatted_date} | {zip_filename} | {format_size(zip_size)} | 已发布 |

"""


def append_version_row(
    existing_content: str,
    version: str,
    date_str: str,
    zip_filename: str,
    zip_size: int
) -> str:
    """
    在现有版本记录文档的表格中追加一行新记录。

    在第一个表格的表头行之后、最后一行之前插入新行。

    Args:
        existing_content: 现有的 Markdown 文档内容
        version: 版本号
        date_str: 日期字符串 (YYYYMMDD)
        zip_filename: ZIP 文件名
        zip_size: ZIP 文件大小（字节）

    Returns:
        str: 追加新行后的完整文档内容
    """
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    # 新增记录行
    new_row = (
        f"| V{version} | {formatted_date} | {zip_filename} "
        f"| {format_size(zip_size)} | 已发布 |\n"
    )

    # 查找表格中的最后一个 "| ... |" 行并在其后插入
    lines = existing_content.split("\n")
    inserted = False
    result_lines = []

    # 定位第一个表格区域
    in_table = False
    table_start_idx = -1

    for i, line in enumerate(lines):
        result_lines.append(line)

        # 检测表格开始
        if "| 版本号 |" in line and "发布日期" in line:
            in_table = True
            table_start_idx = i
            continue

        # 在表格内的数据行之后插入新行
        if in_table and line.startswith("|") and "---" not in line and i > table_start_idx + 1:
            # 检查下一行是否还是表格行或者表格结束
            if i + 1 >= len(lines) or not lines[i + 1].startswith("|"):
                result_lines.append(new_row)
                inserted = True
                in_table = False

    # 如果没有在表格中插入，追加到文件末尾
    if not inserted:
        result_lines.append(new_row)

    return "\n".join(result_lines)


# ============================================================================
# 汇总报告
# ============================================================================

def print_summary_report(results: Dict[str, Any]) -> None:
    """
    输出最终汇总报告，包含所有阶段的关键指标。

    Args:
        results: 包含各阶段结果的字典，键包括:
            - version: 版本号
            - phase1_ok: Phase 1 是否通过
            - phase2_ok: Phase 2 是否通过
            - phase3_ok: Phase 3 是否通过
            - phase4_ok: Phase 4 是否通过
            - phase5_ok: Phase 5 是否通过
            - exe_size: EXE 文件大小（字节），可能为 None
            - zip_size: ZIP 文件大小（字节），可能为 None
            - dry_run: 是否为试运行模式
    """
    log.info("")
    log.info("=" * 60)
    log.info("打包汇总报告")
    log.info("=" * 60)

    mode_str = " (DRY-RUN)" if results.get("dry_run", False) else ""
    log.info(f"  版本号:     V{results['version']}{mode_str}")
    log.info(f"  打包时间:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 各阶段状态
    phases = [
        ("Phase 1: 版本校验", results.get("phase1_ok")),
        ("Phase 2: 数据库预处理", results.get("phase2_ok")),
        ("Phase 3: PyInstaller", results.get("phase3_ok")),
        ("Phase 4: 交付物组装", results.get("phase4_ok")),
        ("Phase 5: 归档记录", results.get("phase5_ok")),
    ]

    log.info("")
    log.info("  各阶段状态:")
    all_ok = True
    for name, status in phases:
        status_str = "[OK]" if status else "[FAIL]"
        status_icon = "PASS" if status else "FAIL"
        log.info(f"    {status_str} {name:20s} ... {status_icon}")
        if not status:
            all_ok = False

    # 文件大小信息
    log.info("")
    log.info("  产出物:")
    exe_size = results.get("exe_size")
    zip_size = results.get("zip_size")

    if exe_size is not None:
        log.info(f"    EXE 大小:   {format_size(exe_size)}")
    else:
        log.info("    EXE 大小:   未生成")
        all_ok = False

    if zip_size is not None:
        log.info(f"    ZIP 大小:   {format_size(zip_size)}")
    else:
        log.info("    ZIP 大小:   未生成")
        all_ok = False

    # 最终结论
    log.info("")
    if all_ok and not results.get("dry_run", False):
        log.info("  [SUCCESS] 全部打包流程完成!")
    elif results.get("dry_run", False):
        log.info("  [DRY-RUN] 试运行完成，以上为预期操作（未实际执行）")
    else:
        log.error("  [FAILED] 打包流程存在问题，请检查上方错误信息")

    log.info("=" * 60)


# ============================================================================
# 参数解析
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数。

    Returns:
        argparse.Namespace: 解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="全自动化的交付物整理 + 打包脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python package.py                     # 完整打包流程
  python package.py --version 2.6.0     # 指定版本号打包
  python package.py --dry-run           # 试运行（仅显示将执行的操作）
  python package.py --clean             # 清理build/dist后重新打包
  python package.py --clean --dry-run   # 清理+试运行
        """
    )

    parser.add_argument(
        "--version",
        type=str,
        default=None,
        metavar="X.Y.Z",
        help="覆盖版本号（跳过从 version.py 读取）"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式：打印每个步骤但不实际执行文件操作"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理 build/ 和 dist/ 目录后重新打包"
    )

    return parser.parse_args()


# ============================================================================
# 主函数
# ============================================================================

def main() -> int:
    """
    主入口函数，按顺序执行完整的打包流程。

    Returns:
        int: 退出码，0 表示成功，非 0 表示失败
    """
    # 解析参数
    args = parse_arguments()
    dry_run = args.dry_run
    clean = args.clean

    # 显示启动信息
    log.info("#" * 60)
    log.info("#  Python项目管理工具 - 自动化打包脚本")
    log.info("#" * 60)
    log.info(f"  模式: {'试运行 (DRY-RUN)' if dry_run else '正式执行'}")
    log.info(f"  清理旧构建: {'是' if clean else '否'}")
    log.info("")

    # 用于收集各阶段结果
    results: Dict[str, Any] = {
        "dry_run": dry_run,
        "version": "",
        "phase1_ok": False,
        "phase2_ok": False,
        "phase3_ok": False,
        "phase4_ok": False,
        "phase5_ok": False,
        "exe_size": None,
        "zip_size": None,
    }

    # ========================================================================
    # Phase 1: 准备与校验
    # ========================================================================
    try:
        results["version"] = read_version(args.version)
        results["phase1_ok"] = verify_version_consistency(results["version"])
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        log.error(f"Phase 1 异常: {e}")
        results["phase1_ok"] = False

    # 版本校验警告但继续执行（不阻断流程）
    if not results["phase1_ok"]:
        log.warning("版本不一致警告：建议修复后重新运行，但将继续执行...")

    # ========================================================================
    # Phase 2: 数据库预处理
    # ========================================================================
    try:
        results["phase2_ok"] = sync_database(dry_run=dry_run)
    except Exception as e:
        log.error(f"Phase 2 异常: {e}")
        results["phase2_ok"] = False

    # 数据库预处理失败则终止
    if not results["phase2_ok"]:
        log.error("数据库预处理失败，终止打包流程")
        print_summary_report(results)
        return 2

    # ========================================================================
    # Phase 3: PyInstaller 打包
    # ========================================================================
    try:
        phase3_success, exe_size = run_pyinstaller(clean=clean, dry_run=dry_run)
        results["phase3_ok"] = phase3_success
        results["exe_size"] = exe_size
    except Exception as e:
        log.error(f"Phase 3 异常: {e}")
        results["phase3_ok"] = False

    # PyInstaller 失败则终止
    if not results["phase3_ok"]:
        log.error("PyInstaller 打包失败，终止打包流程")
        print_summary_report(results)
        return 3

    # ========================================================================
    # Phase 4: 交付物组装
    # ========================================================================
    try:
        results["phase4_ok"] = assemble_delivery(
            results["version"], dry_run=dry_run
        )
    except Exception as e:
        log.error(f"Phase 4 异常: {e}")
        results["phase4_ok"] = False

    # 交付物组装失败则终止
    if not results["phase4_ok"]:
        log.error("交付物组装失败，终止打包流程")
        print_summary_report(results)
        return 4

    # ========================================================================
    # Phase 5: 归档与记录
    # ========================================================================
    try:
        phase5_success, zip_size = create_zip_archive(
            results["version"], dry_run=dry_run
        )
        results["phase5_ok"] = phase5_success
        results["zip_size"] = zip_size
    except Exception as e:
        log.error(f"Phase 5 异常: {e}")
        results["phase5_ok"] = False

    # ========================================================================
    # 输出汇总报告
    # ========================================================================
    print_summary_report(results)

    # 根据整体结果返回退出码
    if all([
        results["phase1_ok"],
        results["phase2_ok"],
        results["phase3_ok"],
        results["phase4_ok"],
        results["phase5_ok"]
    ]):
        return 0
    else:
        return 99


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
