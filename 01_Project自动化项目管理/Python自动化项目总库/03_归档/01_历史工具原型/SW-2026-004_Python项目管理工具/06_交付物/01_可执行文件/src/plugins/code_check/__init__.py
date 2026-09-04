# -*- coding: utf-8 -*-
"""
代码规范检查插件
"""
import re
from pathlib import Path
from src.utils.file_utils import read_file
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeCheckPlugin:
    """代码规范检查插件"""
    
    plugin_id = "code_check"
    
    def __init__(self):
        self.name = "代码规范检查"
        self.version = "1.0.0"
        self.author = "Trae AI"
        self.description = "检查Python代码是否符合PEP8规范"
        self.config = {}
        
        # PEP8规则
        self.rules = [
            {
                "id": "E001",
                "name": "行长度超过120字符",
                "pattern": r".{121,}",
                "level": "warning",
                "message": "行长度超过120字符"
            },
            {
                "id": "E002",
                "name": "使用制表符缩进",
                "pattern": r"^\t+",
                "level": "error",
                "message": "不允许使用制表符缩进，请使用4个空格"
            },
            {
                "id": "E003",
                "name": "文件末尾缺少空行",
                "pattern": r".*\S$",
                "level": "warning",
                "message": "文件末尾需要有一个空行"
            },
            {
                "id": "E004",
                "name": "行尾空格",
                "pattern": r" +$",
                "level": "warning",
                "message": "行尾存在多余空格"
            }
        ]
    
    def initialize(self, config: dict) -> bool:
        """初始化插件"""
        self.config = config or {}
        logger.info(f"代码规范检查插件初始化完成")
        return True
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def check_file(self, file_path: str) -> list:
        """检查单个文件"""
        results = []
        try:
            content = read_file(file_path)
            lines = content.split("\n")
            
            for line_num, line in enumerate(lines, 1):
                for rule in self.rules:
                    if re.search(rule["pattern"], line):
                        results.append({
                            "rule": rule["id"],
                            "rule_name": rule["name"],
                            "level": rule["level"],
                            "message": rule["message"],
                            "path": file_path,
                            "line": line_num
                        })
            
            # 检查文件末尾空行
            if len(lines) > 0 and lines[-1].strip() != "":
                results.append({
                    "rule": "E003",
                    "rule_name": "文件末尾缺少空行",
                    "level": "warning",
                    "message": "文件末尾需要有一个空行",
                    "path": file_path,
                    "line": len(lines)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")
            return []
    
    def check_project(self, project_path: str, check_types: list = None) -> list:
        """检查整个项目"""
        results = []
        project_dir = Path(project_path)
        
        # 只检查Python文件
        for py_file in project_dir.rglob("*.py"):
            # 排除不需要检查的目录
            if any(part in [".git", "__pycache__", "venv", "node_modules", ".idea"] for part in py_file.parts):
                continue
            
            file_results = self.check_file(str(py_file))
            results.extend(file_results)
        
        return results
    
    def get_actions(self) -> list:
        """获取支持的操作"""
        return [
            {
                "id": "check_project",
                "name": "检查项目代码规范",
                "description": "检查整个项目的Python代码是否符合PEP8规范"
            },
            {
                "id": "check_file",
                "name": "检查单个文件",
                "description": "检查单个Python文件的代码规范"
            }
        ]
    
    def execute_action(self, action: str, params: dict) -> tuple[dict, str]:
        """执行操作"""
        if action == "check_project":
            if "project_path" not in params:
                return None, "缺少参数: project_path"
            
            results = self.check_project(params["project_path"], params.get("check_types"))
            return {
                "results": results,
                "count": len(results),
                "errors": sum(1 for r in results if r["level"] == "error"),
                "warnings": sum(1 for r in results if r["level"] == "warning")
            }, ""
        
        elif action == "check_file":
            if "file_path" not in params:
                return None, "缺少参数: file_path"
            
            results = self.check_file(params["file_path"])
            return {
                "results": results,
                "count": len(results),
                "errors": sum(1 for r in results if r["level"] == "error"),
                "warnings": sum(1 for r in results if r["level"] == "warning")
            }, ""
        
        else:
            return None, f"不支持的操作: {action}"
