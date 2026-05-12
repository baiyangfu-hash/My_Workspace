# -*- coding: utf-8 -*-
"""
规范检查服务
"""
import os
from pathlib import Path
from typing import List, Dict, Any

from src.models.project import Project
from src.utils.path_utils import normalize_path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CheckResult:
    """检查结果类"""
    def __init__(self):
        self.total: int = 0
        self.passed: int = 0
        self.warnings: int = 0
        self.errors: int = 0
        self.items: List[Dict[str, Any]] = []
    
    def add_item(self, level: str, rule: str, message: str, path: str = "", line: int = 0):
        """添加检查项"""
        self.total += 1
        if level == "pass":
            self.passed += 1
        elif level == "warning":
            self.warnings += 1
        elif level == "error":
            self.errors += 1
        
        self.items.append({
            "level": level,
            "rule": rule,
            "message": message,
            "path": path,
            "line": line
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "warnings": self.warnings,
                "errors": self.errors,
                "pass_rate": round((self.passed / self.total * 100), 2) if self.total > 0 else 0
            },
            "items": self.items
        }

class CheckService:
    """规范检查服务类"""
    
    @staticmethod
    def check_project(project: Project, check_types: List[str] = None) -> tuple[Optional[CheckResult], str]:
        """执行项目规范检查"""
        try:
            if not project:
                return None, "项目不存在"
            
            project_path = Path(project.path)
            if not project_path.exists():
                return None, "项目路径不存在"
            
            result = CheckResult()
            
            # 默认检查所有类型
            if not check_types:
                check_types = ["directory_structure", "file_naming", "code_style", "documentation"]
            
            # 执行各类检查
            for check_type in check_types:
                if check_type == "directory_structure":
                    CheckService._check_directory_structure(project, result)
                elif check_type == "file_naming":
                    CheckService._check_file_naming(project, result)
                elif check_type == "code_style":
                    CheckService._check_code_style(project, result)
                elif check_type == "documentation":
                    CheckService._check_documentation(project, result)
            
            logger.info(f"项目检查完成: {project.code}, 通过率: {result.to_dict()['summary']['pass_rate']}%")
            return result, ""
            
        except Exception as e:
            logger.exception(f"项目检查失败: {e}")
            return None, f"项目检查失败: {str(e)}"
    
    @staticmethod
    def _check_directory_structure(project: Project, result: CheckResult):
        """检查目录结构"""
        try:
            project_path = Path(project.path)
            
            # 获取项目模板信息
            template_service = __import__('src.services.template_service', fromlist=['TemplateService']).TemplateService
            template = template_service.get_template(project.template_id)
            
            if not template or not template.structure:
                result.add_item(
                    level="warning",
                    rule="目录结构检查",
                    message="未找到模板定义，无法进行目录结构验证",
                    path=project.path
                )
                return
            
            # 检查每个必需目录是否存在
            required_dirs = [item for item in template.structure if item.get("required", False)]
            optional_dirs = [item for item in template.structure if not item.get("required", False)]
            
            # 检查必填目录
            missing_required = []
            for dir_item in required_dirs:
                dir_path = project_path / dir_item["path"]
                if not dir_path.exists():
                    missing_required.append(dir_item["path"])
                    result.add_item(
                        level="error",
                        rule="目录结构-必填目录缺失",
                        message=f"必填目录不存在: {dir_item['path']}",
                        path=str(dir_path)
                    )
                else:
                    result.add_item(
                        level="pass",
                        rule="目录结构-必填目录",
                        message=f"必填目录已创建: {dir_item['path']}",
                        path=str(dir_path)
                    )
            
            # 检查可选目录（仅记录，不作为错误）
            missing_optional = []
            for dir_item in optional_dirs:
                dir_path = project_path / dir_item["path"]
                if not dir_path.exists():
                    missing_optional.append(dir_item["path"])
                    result.add_item(
                        level="warning",
                        rule="目录结构-可选目录缺失",
                        message=f"可选目录不存在: {dir_item['path']}（建议创建）",
                        path=str(dir_path)
                    )
                else:
                    result.add_item(
                        level="pass",
                        rule="目录结构-可选目录",
                        message=f"可选目录已创建: {dir_item['path']}",
                        path=str(dir_path)
                    )
            
            # 生成汇总信息
            total_required = len(required_dirs)
            existing_required = total_required - len(missing_required)
            
            if len(missing_required) == 0:
                result.add_item(
                    level="pass",
                    rule="目录结构完整性",
                    message=f"所有{total_required}个必填目录均已创建，目录结构完整"
                )
            else:
                result.add_item(
                    level="error",
                    rule="目录结构完整性",
                    message=f"缺少{len(missing_required)}个必填目录: {', '.join(missing_required)}"
                )
                
        except Exception as e:
            logger.exception(f"目录结构检查失败: {e}")
            result.add_item(
                level="error",
                rule="目录结构检查",
                message=f"目录结构检查异常: {str(e)}"
            )
    
    @staticmethod
    def _check_file_naming(project: Project, result: CheckResult):
        """检查文件命名规范"""
        import re
        
        try:
            project_path = Path(project.path)
            
            # 定义文件命名规范
            # 1. 文档文件：数字-中文名称_类型-V版本号.扩展名 (如: 0-项目立项表_PROJ-V1.0.0.md)
            # 2. Python文件：小写字母+下划线 (如: main.py, utils.py)
            # 3. 配置文件：全小写或标准名称 (如: .gitignore, requirements.txt)
            # 4. 不允许的字符：空格、特殊符号（除-_./）
            
            naming_rules = {
                "文档文件": {
                    "pattern": r'^\d+-[\u4e00-\u9fa5a-zA-Z]+_[A-Z]+-V[\d.]+\.(md|txt|docx?|pdf)$',
                    "directories": ["00_项目基础信息", "01_项目文档", "02_需求设计", "07_交付文档", "08_项目总结"],
                    "description": "格式应为: 数字-名称_类型-V版本号.扩展名"
                },
                "Python源码": {
                    "pattern": r'^[a-z][a-z0-9_]*\.py$',
                    "extensions": [".py"],
                    "description": "应使用小写字母和下划线"
                },
                "配置文件": {
                    "pattern": r'^[a-zA-Z][a-zA-Z0-9._-]*\.(json|yaml|yml|toml|ini|cfg|conf|txt)$',
                    "extensions": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"],
                    "description": "配置文件命名规范"
                }
            }
            
            # 特殊允许的文件名
            allowed_special_names = [
                '.gitignore', '.gitattributes', '.env', '.editorconfig',
                'README', 'README.md', 'README.txt', 'LICENSE', 'LICENSE.md',
                '__init__.py', 'main.py', 'app.py', 'run.py',
                'requirements.txt', 'setup.py', 'pyproject.toml'
            ]
            
            # 非法字符模式
            illegal_chars_pattern = re.compile(r'[\s!@#$%^&*()+={}\[\]|\\:";\'<>?,]')
            
            # 统计变量
            total_files_checked = 0
            naming_violations = []
            
            # 遍历项目目录中的文件
            for file_path in project_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # 跳过隐藏文件和特定目录
                if any(part.startswith('.') or part == '__pycache__' or part == '.trae' 
                       for part in file_path.parts):
                    continue
                
                filename = file_path.name
                relative_path = str(file_path.relative_to(project_path))
                total_files_checked += 1
                
                # 检查是否为特殊允许的文件名
                if filename in allowed_special_names:
                    result.add_item(
                        level="pass",
                        rule="文件命名-特殊文件",
                        message=f"特殊文件命名正确: {filename}",
                        path=relative_path
                    )
                    continue
                
                # 检查非法字符
                if illegal_chars_pattern.search(filename):
                    naming_violations.append({
                        "path": relative_path,
                        "reason": f"文件名包含非法字符（空格或特殊符号）"
                    })
                    result.add_item(
                        level="error",
                        rule="文件命名-非法字符",
                        message=f"文件名包含非法字符: {filename}，请使用字母、数字、下划线或连字符",
                        path=relative_path
                    )
                    continue
                
                # 根据文件所在目录和扩展名应用不同的规则
                parent_dir = file_path.parent.name
                ext = file_path.suffix.lower()
                
                # 文档目录检查
                is_doc_dir = any(doc_dir in relative_path for doc_dir in ["00_", "01_", "02_", "07_", "08_"])
                
                if is_doc_dir and ext in ['.md', '.txt', '.doc', '.docx', '.pdf']:
                    # 检查文档命名规范
                    pattern = re.compile(naming_rules["文档文件"]["pattern"])
                    if not pattern.match(filename):
                        naming_violations.append({
                            "path": relative_path,
                            "reason": f"不符合文档命名规范（{naming_rules['文档文件']['description']}）"
                        })
                        result.add_item(
                            level="warning",
                            rule="文件命名-文档规范",
                            message=f"文档命名不规范: {filename}，建议格式: 数字-名称_类型-V版本号.扩展名",
                            path=relative_path
                        )
                    else:
                        result.add_item(
                            level="pass",
                            rule="文件命名-文档规范",
                            message=f"文档命名符合规范: {filename}",
                            path=relative_path
                        )
                        
                elif ext == '.py':
                    # 检查Python文件命名
                    pattern = re.compile(naming_rules["Python源码"]["pattern"])
                    if not pattern.match(filename):
                        naming_violations.append({
                            "path": relative_path,
                            "reason": f"不符合Python命名规范（{naming_rules['Python源码']['description']}）"
                        })
                        result.add_item(
                            level="warning",
                            rule="文件命名-Python规范",
                            message=f"Python文件命名不规范: {filename}，建议使用小写字母和下划线",
                            path=relative_path
                        )
                    else:
                        result.add_item(
                            level="pass",
                            rule="文件命名-Python规范",
                            message=f"Python文件命名符合规范: {filename}",
                            path=relative_path
                        )
                        
                else:
                    # 其他文件仅做基本检查
                    result.add_item(
                        level="pass",
                        rule="文件命名-基本检查",
                        message=f"文件命名通过基本检查: {filename}",
                        path=relative_path
                    )
            
            # 生成汇总
            if len(naming_violations) == 0 and total_files_checked > 0:
                result.add_item(
                    level="pass",
                    rule="文件命名总体检查",
                    message=f"共检查{total_files_checked}个文件，所有文件命名均符合规范"
                )
            elif total_files_checked == 0:
                result.add_item(
                    level="warning",
                    rule="文件命名总体检查",
                    message="未发现可检查的文件"
                )
            else:
                result.add_item(
                    level="warning",
                    rule="文件命名总体检查",
                    message=f"共检查{total_files_checked}个文件，发现{len(naming_violations)}个命名不规范问题"
                )
                
        except Exception as e:
            logger.exception(f"文件命名检查失败: {e}")
            result.add_item(
                level="error",
                rule="文件命名检查",
                message=f"文件命名检查异常: {str(e)}"
            )
    
    @staticmethod
    def _check_code_style(project: Project, result: CheckResult):
        """检查代码风格"""
        # TODO: 实现PEP8检查等逻辑
        pass
    
    @staticmethod
    def _check_documentation(project: Project, result: CheckResult):
        """检查文档完整性"""
        try:
            project_path = Path(project.path)
            
            # 1. 检查README文件
            readme_variants = ['README.md', 'README.txt', 'README', 'readme.md', 'readme.txt']
            readme_found = False
            readme_path = None
            
            for variant in readme_variants:
                potential_readme = project_path / variant
                if potential_readme.exists():
                    readme_found = True
                    readme_path = potential_readme
                    
                    # 检查README内容是否为空或过小
                    file_size = potential_readme.stat().st_size
                    if file_size < 50:  # 小于50字节可能内容不完整
                        result.add_item(
                            level="warning",
                            rule="文档完整性-README内容",
                            message=f"README文件存在但内容可能不完整（文件大小: {file_size}字节），建议添加项目说明、安装步骤等基本信息",
                            path=str(potential_readme.relative_to(project_path))
                        )
                    else:
                        result.add_item(
                            level="pass",
                            rule="文档完整性-README文件",
                            message=f"README文件已创建，大小: {file_size}字节",
                            path=str(potential_readme.relative_to(project_path))
                        )
                    break
            
            if not readme_found:
                result.add_item(
                    level="error",
                    rule="文档完整性-README文件",
                    message="未找到README文件。建议在项目根目录创建README.md文件，包含项目简介、安装说明、使用方法等信息",
                    path=project.path
                )
            
            # 2. 检查.gitignore文件
            gitignore_path = project_path / '.gitignore'
            
            if gitignore_path.exists():
                # 检查.gitignore内容是否为空
                content = gitignore_path.read_text(encoding='utf-8', errors='ignore').strip()
                
                if len(content) < 10:  # 内容太少可能不完整
                    result.add_item(
                        level="warning",
                        rule="文档完整性-.gitignore内容",
                        message=".gitignore文件存在但内容可能不完整，建议添加Python相关忽略规则（如__pycache__/、*.pyc等）",
                        path=".gitignore"
                    )
                else:
                    # 检查常见的Python忽略规则
                    common_patterns = ['__pycache__', '*.pyc', '.pyc', '*.pyo']
                    found_patterns = [p for p in common_patterns if p in content]
                    
                    if len(found_patterns) >= 2:
                        result.add_item(
                            level="pass",
                            rule="文档完整性-.gitignore文件",
                            message=f".gitignore文件配置完整，包含{len(found_patterns)}个常见Python忽略规则",
                            path=".gitignore"
                        )
                    else:
                        result.add_item(
                            level="warning",
                            rule="文档完整性-.gitignore内容",
                            message=f".gitignore文件存在但可能缺少常见规则（当前包含: {len(found_patterns)}/{len(common_patterns)}个标准规则）",
                            path=".gitignore"
                        )
            else:
                result.add_item(
                    level="error",
                    rule="文档完整性-.gitignore文件",
                    message="未找到.gitignore文件。建议创建.gitignore以避免提交不必要的文件（如__pycache__、*.pyc、日志文件等）",
                    path=project.path
                )
            
            # 3. 检查项目立项表（项目基础信息）
            proj_info_dir = project_path / "00_项目基础信息"
            if proj_info_dir.exists():
                proj_files = list(proj_info_dir.glob("*项目立项表*.md"))
                if proj_files:
                    result.add_item(
                        level="pass",
                        rule="文档完整性-项目立项表",
                        message=f"项目立项表已创建: {proj_files[0].name}",
                        path=str(proj_files[0].relative_to(project_path))
                    )
                else:
                    result.add_item(
                        level="warning",
                        rule="文档完整性-项目立项表",
                        message="00_项目基础信息目录存在但未找到项目立项表文件",
                        path="00_项目基础信息"
                    )
            else:
                result.add_item(
                    level="warning",
                    rule="文档完整性-项目立项表",
                    message="00_项目基础信息目录不存在，无法验证项目立项表",
                    path=project.path
                )
            
            # 4. 检查需求文档
            doc_dir = project_path / "01_项目文档"
            if doc_dir.exists():
                req_docs = list(doc_dir.glob("*需求*.*"))
                design_docs = list(doc_dir.glob("*设计*.*"))
                
                total_docs = len(req_docs) + len(design_docs)
                if total_docs > 0:
                    result.add_item(
                        level="pass",
                        rule="文档完整性-需求设计文档",
                        message=f"已找到{total_docs}份需求/设计文档（需求:{len(req_docs)}, 设计:{len(design_docs)}）",
                        path="01_项目文档"
                    )
                else:
                    result.add_item(
                        level="warning",
                        rule="文档完整性-需求设计文档",
                        message="01_项目文档目录存在但未找到需求或设计文档",
                        path="01_项目文档"
                    )
            else:
                result.add_item(
                    level="warning",
                    rule="文档完整性-需求设计文档",
                    message="01_项目文档目录不存在，无法验证需求文档",
                    path=project.path
                )
            
            # 5. 文档总体汇总
            essential_docs = {
                "README": readme_found,
                ".gitignore": gitignore_path.exists()
            }
            
            passed_count = sum(1 for v in essential_docs.values() if v)
            total_essential = len(essential_docs)
            
            if passed_count == total_essential:
                result.add_item(
                    level="pass",
                    rule="文档完整性-总体评估",
                    message=f"所有必要文档（{total_essential}/{total_essential}）均已就位，文档完整性良好"
                )
            elif passed_count >= total_essential - 1:
                missing = [k for k, v in essential_docs.items() if not v]
                result.add_item(
                    level="warning",
                    rule="文档完整性-总体评估",
                    message=f"大部分必要文档已就位（{passed_count}/{total_essential}），缺失: {', '.join(missing)}"
                )
            else:
                missing = [k for k, v in essential_docs.items() if not v]
                result.add_item(
                    level="error",
                    rule="文档完整性-总体评估",
                    message=f"多个必要文档缺失（仅{passed_count}/{total_essential}）, 请尽快补充: {', '.join(missing)}"
                )
                
        except Exception as e:
            logger.exception(f"文档完整性检查失败: {e}")
            result.add_item(
                level="error",
                rule="文档完整性检查",
                message=f"文档完整性检查异常: {str(e)}"
            )
    
    @staticmethod
    def run_custom_check(project: Project, rules: List[Dict]) -> tuple[Optional[CheckResult], str]:
        """执行自定义检查规则"""
        try:
            result = CheckResult()
            
            # TODO: 实现自定义规则检查逻辑
            
            return result, ""
        except Exception as e:
            logger.exception(f"自定义检查失败: {e}")
            return None, f"自定义检查失败: {str(e)}"
