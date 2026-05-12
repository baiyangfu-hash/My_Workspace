# -*- coding: utf-8 -*-
"""
文档生成插件
"""
from pathlib import Path
from datetime import datetime
from src.utils.file_utils import write_file, read_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentGeneratorPlugin:
    """文档生成插件"""
    
    plugin_id = "document_generator"
    
    def __init__(self):
        self.name = "文档生成器"
        self.version = "1.0.0"
        self.author = "Trae AI"
        self.description = "自动生成项目文档：README、接口文档、CHANGELOG等"
        self.config = {}
    
    def initialize(self, config: dict) -> bool:
        """初始化插件"""
        self.config = config or {}
        logger.info(f"文档生成插件初始化完成")
        return True
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def generate_readme(self, project_info: dict, output_path: str) -> tuple[str, str]:
        """生成README.md"""
        try:
            content = f"""# {project_info['name']}

## 项目信息
- **项目编号**: {project_info.get('code', '')}
- **业务线**: {project_info.get('business_line', '')}
- **负责人**: {project_info.get('manager', '')}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d')}
- **项目描述**: {project_info.get('description', '')}

## 项目结构
```
{project_info.get('structure', '')}
```

## 环境依赖
- Python 3.8+
- 依赖包: 见 requirements.txt

## 安装说明
```bash
pip install -r requirements.txt
```

## 运行说明
```bash
python main.py
```

## 部署说明
待补充

## 版本历史
- v1.0.0: 初始版本
"""
            
            write_file(output_path, content)
            return output_path, ""
            
        except Exception as e:
            logger.error(f"生成README失败: {e}")
            return None, str(e)
    
    def generate_changelog(self, project_path: str, output_path: str) -> tuple[str, str]:
        """生成CHANGELOG.md"""
        try:
            content = f"""# CHANGELOG

## [{datetime.now().strftime('%Y-%m-%d')}] v1.0.0
### Added
- 初始版本发布
- 基础功能实现
"""
            
            write_file(output_path, content)
            return output_path, ""
            
        except Exception as e:
            logger.error(f"生成CHANGELOG失败: {e}")
            return None, str(e)
    
    def get_actions(self) -> list:
        """获取支持的操作"""
        return [
            {
                "id": "generate_readme",
                "name": "生成README文档",
                "description": "自动生成项目README.md文件"
            },
            {
                "id": "generate_changelog",
                "name": "生成CHANGELOG",
                "description": "自动生成版本变更记录"
            }
        ]
    
    def execute_action(self, action: str, params: dict) -> tuple[dict, str]:
        """执行操作"""
        if action == "generate_readme":
            required = ["project_info", "output_path"]
            for field in required:
                if field not in params:
                    return None, f"缺少参数: {field}"
            
            path, error = self.generate_readme(params["project_info"], params["output_path"])
            if error:
                return None, error
            
            return {"output_path": path}, ""
        
        elif action == "generate_changelog":
            required = ["project_path", "output_path"]
            for field in required:
                if field not in params:
                    return None, f"缺少参数: {field}"
            
            path, error = self.generate_changelog(params["project_path"], params["output_path"])
            if error:
                return None, error
            
            return {"output_path": path}, ""
        
        else:
            return None, f"不支持的操作: {action}"
