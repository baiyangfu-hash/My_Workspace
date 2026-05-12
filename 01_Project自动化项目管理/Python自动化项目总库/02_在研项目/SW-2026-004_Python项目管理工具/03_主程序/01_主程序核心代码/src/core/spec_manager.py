# -*- coding: utf-8 -*-
"""
规范管理模块
用于管理项目引用的全局规范版本，检查更新，同步规范
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil


class SpecManager:
    """规范管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化规范管理器
        
        Args:
            config_path: 配置文件路径，默认为 config/spec_version_config.json
        """
        if config_path is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "config" / "spec_version_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.base_path = self._get_base_path()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {}
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _get_base_path(self) -> Path:
        """获取全局规范基础路径"""
        config_dir = self.config_path.parent
        relative_path = self.config.get("全局规范路径", "../../01_全局规范")
        return (config_dir / relative_path).resolve()
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """从文件名中提取版本号"""
        # 匹配版本号格式：V1.0.0 或 v1.0.0
        pattern = r'[Vv](\d+\.\d+\.\d+)'
        match = re.search(pattern, filename)
        if match:
            return f"V{match.group(1)}"
        return ""
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """解析版本号字符串为元组"""
        if not version_str:
            return (0, 0, 0)
        # 移除V前缀
        version_str = version_str.upper().replace('V', '')
        parts = version_str.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        比较两个版本号
        
        Returns:
            -1: version1 < version2
             0: version1 = version2
             1: version1 > version2
        """
        v1 = self._parse_version(version1)
        v2 = self._parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def _get_version_change_type(self, old_version: str, new_version: str) -> str:
        """获取版本变化类型"""
        old = self._parse_version(old_version)
        new = self._parse_version(new_version)
        
        if old[0] != new[0]:
            return "主版本更新"
        elif old[1] != new[1]:
            return "次版本更新"
        elif old[2] != new[2]:
            return "修订更新"
        else:
            return "无变化"
    
    def _find_latest_spec_file(self, spec_dir: Path, spec_name: str) -> Optional[Path]:
        """
        在目录中查找最新的规范文件
        
        Args:
            spec_dir: 规范所在目录
            spec_name: 规范名称（不含版本号）
        
        Returns:
            最新规范文件路径，如果没有找到则返回None
        """
        if not spec_dir.exists():
            return None
        
        # 查找匹配的文件
        pattern = f"{spec_name}*.md"
        matching_files = list(spec_dir.glob(pattern))
        
        if not matching_files:
            return None
        
        # 按版本号排序，返回最新的
        def get_version(file_path):
            return self._parse_version(self._extract_version_from_filename(file_path.name))
        
        return max(matching_files, key=get_version)
    
    def check_updates(self) -> Dict:
        """
        检查规范更新
        
        Returns:
            检查结果字典
        """
        results = {
            "检查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "可更新规范": [],
            "已最新规范": [],
            "未找到规范": [],
            "检查详情": {}
        }
        
        spec_list = self.config.get("规范清单", {})
        
        for spec_name, spec_info in spec_list.items():
            current_version = spec_info.get("当前版本", "")
            spec_path = spec_info.get("规范路径", "")
            
            # 获取规范所在目录
            full_path = self.base_path / spec_path
            spec_dir = full_path.parent
            
            # 从文件名中提取规范名称（不含版本号）
            filename = full_path.name
            # 移除版本号部分，获取基础名称
            base_name = re.sub(r'[_-][Vv]\d+\.\d+\.\d+.*$', '', filename)
            
            # 查找最新的规范文件
            latest_file = self._find_latest_spec_file(spec_dir, base_name)
            
            if latest_file:
                latest_version = self._extract_version_from_filename(latest_file.name)
                
                # 更新配置中的最新版本
                spec_info["最新版本"] = latest_version
                spec_info["最后检查时间"] = results["检查时间"]
                
                # 比较版本
                comparison = self._compare_versions(current_version, latest_version)
                
                if comparison < 0:
                    # 有更新
                    change_type = self._get_version_change_type(current_version, latest_version)
                    spec_info["更新状态"] = f"可更新 ({change_type})"
                    
                    update_info = {
                        "规范名称": spec_name,
                        "规范ID": spec_info.get("规范ID", ""),
                        "当前版本": current_version,
                        "最新版本": latest_version,
                        "更新类型": change_type,
                        "规范路径": str(latest_file.relative_to(self.base_path)),
                        "重要性": spec_info.get("重要性", "中")
                    }
                    results["可更新规范"].append(update_info)
                    results["检查详情"][spec_name] = update_info
                    
                elif comparison == 0:
                    # 已最新
                    spec_info["更新状态"] = "已最新"
                    results["已最新规范"].append({
                        "规范名称": spec_name,
                        "规范ID": spec_info.get("规范ID", ""),
                        "当前版本": current_version,
                        "重要性": spec_info.get("重要性", "中")
                    })
                else:
                    # 本地版本比全局规范新（异常情况）
                    spec_info["更新状态"] = "本地版本较新"
                    results["检查详情"][spec_name] = {
                        "规范名称": spec_name,
                        "状态": "本地版本较新",
                        "当前版本": current_version,
                        "全局版本": latest_version
                    }
            else:
                # 未找到规范文件
                spec_info["更新状态"] = "未找到规范文件"
                spec_info["最后检查时间"] = results["检查时间"]
                results["未找到规范"].append({
                    "规范名称": spec_name,
                    "规范ID": spec_info.get("规范ID", ""),
                    "预期路径": str(spec_path)
                })
        
        # 保存更新后的配置
        self._save_config()
        
        return results
    
    def get_specs_list(self) -> List[Dict]:
        """
        获取规范列表
        
        Returns:
            规范列表，每个规范包含名称、版本、状态等信息
        """
        specs = []
        spec_list = self.config.get("规范清单", {})
        
        for spec_name, spec_info in spec_list.items():
            spec = {
                'id': spec_info.get('规范ID', ''),
                'name': spec_name,
                'current_version': spec_info.get('当前版本', 'N/A'),
                'latest_version': spec_info.get('最新版本', 'N/A'),
                'status': 'unknown'
            }
            
            # 计算状态
            current_version = spec_info.get('当前版本', '')
            latest_version = spec_info.get('最新版本', '')
            
            if not current_version or not latest_version:
                spec['status'] = '未检查'
            elif current_version == latest_version:
                spec['status'] = '已最新'
            else:
                comparison = self._compare_versions(current_version, latest_version)
                if comparison < 0:
                    spec['status'] = '可更新'
                else:
                    spec['status'] = '本地版本较新'
            
            specs.append(spec)
        
        return specs
    
    def get_spec_details(self, spec_name: str) -> Dict:
        """
        获取规范详细信息
        
        Args:
            spec_name: 规范名称
        
        Returns:
            规范详细信息字典
        """
        spec_list = self.config.get("规范清单", {})
        
        if spec_name not in spec_list:
            return {"错误": f"规范 '{spec_name}' 不存在"}
        
        spec_info = spec_list[spec_name].copy()
        
        # 读取规范文件内容摘要
        spec_path = self.base_path / spec_info.get("规范路径", "")
        if spec_path.exists():
            try:
                with open(spec_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取前500个字符作为摘要
                    spec_info["内容摘要"] = content[:500] + "..." if len(content) > 500 else content
            except Exception as e:
                spec_info["内容摘要"] = f"读取失败: {e}"
        else:
            spec_info["内容摘要"] = "文件不存在"
        
        return spec_info
    
    def sync_spec(self, spec_name: str, backup: bool = True) -> Dict:
        """
        同步单个规范到最新版本
        
        Args:
            spec_name: 规范名称
            backup: 是否备份旧版本
        
        Returns:
            同步结果字典
        """
        spec_list = self.config.get("规范清单", {})
        
        if spec_name not in spec_list:
            return {"成功": False, "错误": f"规范 '{spec_name}' 不存在"}
        
        spec_info = spec_list[spec_name]
        current_version = spec_info.get("当前版本", "")
        latest_version = spec_info.get("最新版本", "")
        
        if not latest_version:
            return {"成功": False, "错误": "未找到最新版本，请先执行检查更新"}
        
        if current_version == latest_version:
            return {"成功": True, "消息": "已是最新版本，无需同步"}
        
        # 查找最新规范文件
        spec_path = self.base_path / spec_info.get("规范路径", "")
        spec_dir = spec_path.parent
        filename = spec_path.name
        base_name = re.sub(r'[_-][Vv]\d+\.\d+\.\d+.*$', '', filename)
        latest_file = self._find_latest_spec_file(spec_dir, base_name)
        
        if not latest_file:
            return {"成功": False, "错误": "未找到最新规范文件"}
        
        result = {
            "成功": True,
            "规范名称": spec_name,
            "原版本": current_version,
            "新版本": latest_version,
            "备份路径": None
        }
        
        # 备份旧版本
        if backup and spec_path.exists():
            backup_dir = Path(self.config_path).parent / "backup" / "specs"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_filename = f"{spec_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{spec_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            try:
                shutil.copy2(spec_path, backup_path)
                result["备份路径"] = str(backup_path)
            except Exception as e:
                result["备份警告"] = f"备份失败: {e}"
        
        # 更新配置文件中的版本信息
        spec_info["当前版本"] = latest_version
        spec_info["规范路径"] = str(latest_file.relative_to(self.base_path))
        spec_info["更新状态"] = "已同步"
        spec_info["最后同步时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._save_config()
        
        return result
    
    def sync_all_specs(self, auto_sync: bool = False) -> Dict:
        """
        同步所有可更新的规范
        
        Args:
            auto_sync: 是否自动同步（不提示确认）
        
        Returns:
            同步结果字典
        """
        results = {
            "同步时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "同步成功": [],
            "同步失败": [],
            "无需同步": [],
            "跳过": []
        }
        
        # 先检查更新
        check_results = self.check_updates()
        
        for update_info in check_results.get("可更新规范", []):
            spec_name = update_info["规范名称"]
            change_type = update_info["更新类型"]
            
            # 根据版本变化类型决定是否自动同步
            if auto_sync and change_type == "修订更新":
                # 修订更新可以自动同步
                sync_result = self.sync_spec(spec_name, backup=True)
                if sync_result["成功"]:
                    results["同步成功"].append(sync_result)
                else:
                    results["同步失败"].append({
                        "规范名称": spec_name,
                        "错误": sync_result.get("错误", "未知错误")
                    })
            else:
                # 主版本或次版本更新需要人工确认
                results["跳过"].append({
                    "规范名称": spec_name,
                    "原因": f"{change_type}需要人工确认",
                    "当前版本": update_info["当前版本"],
                    "最新版本": update_info["最新版本"]
                })
        
        # 已最新的规范
        for spec_info in check_results.get("已最新规范", []):
            results["无需同步"].append(spec_info["规范名称"])
        
        return results
    
    def get_update_summary(self) -> str:
        """获取更新摘要信息"""
        check_results = self.check_updates()
        
        summary = []
        summary.append("=" * 60)
        summary.append("规范更新检查摘要")
        summary.append("=" * 60)
        summary.append(f"检查时间: {check_results['检查时间']}")
        summary.append("")
        
        # 可更新规范
        if check_results["可更新规范"]:
            summary.append(f"【可更新规范】({len(check_results['可更新规范'])}个)")
            for spec in check_results["可更新规范"]:
                summary.append(f"  • {spec['规范名称']}: {spec['当前版本']} → {spec['最新版本']} ({spec['更新类型']})")
            summary.append("")
        
        # 已最新规范
        if check_results["已最新规范"]:
            summary.append(f"【已最新规范】({len(check_results['已最新规范'])}个)")
            for spec in check_results["已最新规范"]:
                summary.append(f"  ✓ {spec['规范名称']}: {spec['当前版本']}")
            summary.append("")
        
        # 未找到规范
        if check_results["未找到规范"]:
            summary.append(f"【未找到规范】({len(check_results['未找到规范'])}个)")
            for spec in check_results["未找到规范"]:
                summary.append(f"  ✗ {spec['规范名称']}: {spec['预期路径']}")
            summary.append("")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)


# 便捷函数
def check_spec_updates() -> Dict:
    """检查规范更新的便捷函数"""
    manager = SpecManager()
    return manager.check_updates()


def sync_all_specs(auto_sync: bool = False) -> Dict:
    """同步所有规范的便捷函数"""
    manager = SpecManager()
    return manager.sync_all_specs(auto_sync=auto_sync)


def get_update_summary() -> str:
    """获取更新摘要的便捷函数"""
    manager = SpecManager()
    return manager.get_update_summary()


if __name__ == "__main__":
    # 测试代码
    print("规范管理模块测试")
    print("-" * 60)
    
    manager = SpecManager()
    
    # 检查更新
    print("\n1. 检查规范更新:")
    print(manager.get_update_summary())
    
    # 显示可更新规范详情
    results = manager.check_updates()
    if results["可更新规范"]:
        print("\n2. 可更新规范详情:")
        for spec in results["可更新规范"]:
            print(f"\n  规范: {spec['规范名称']}")
            print(f"  版本: {spec['当前版本']} → {spec['最新版本']}")
            print(f"  类型: {spec['更新类型']}")
            print(f"  重要性: {spec['重要性']}")