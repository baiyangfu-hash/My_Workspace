# -*- coding: utf-8 -*-
"""
构建与部署服务
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.utils.logger import setup_logger
from src.utils.path_utils import ensure_directory

logger = setup_logger(__name__)

class BuildDeployService:
    """构建与部署服务类"""
    
    @staticmethod
    def build_project(project_path: str, output_dir: Optional[str] = None) -> tuple[bool, str, Optional[str]]:
        """
        构建项目
        
        Args:
            project_path: 项目路径
            output_dir: 输出目录，默认为项目路径下的dist目录
            
        Returns:
            (成功标志, 错误信息, 构建结果路径)
        """
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                logger.error(f"项目路径不存在: {project_path}")
                return False, f"项目路径不存在: {project_path}", None
            
            # 确定输出目录
            if output_dir:
                output_dir = Path(output_dir)
            else:
                output_dir = project_path / "dist"
            
            # 确保输出目录存在
            ensure_directory(output_dir)
            logger.info(f"输出目录已准备: {output_dir}")
            
            # 检查项目类型
            is_python_project = False
            
            # 检查是否为Python项目
            if (project_path / "setup.py").exists():
                is_python_project = True
                logger.info("检测到 setup.py，使用setup.py构建")
            elif (project_path / "pyproject.toml").exists():
                is_python_project = True
                logger.info("检测到 pyproject.toml，使用pip构建")
            elif (project_path / "__init__.py").exists():
                is_python_project = True
                logger.info("检测到 __init__.py，创建zip包")
            
            if is_python_project:
                # 构建Python项目
                return BuildDeployService._build_python_project(project_path, output_dir)
            else:
                logger.warning(f"不支持的项目类型: {project_path}")
                return False, "不支持的项目类型（需要setup.py/pyproject.toml/__init__.py）", None
                
        except Exception as e:
            logger.exception(f"构建项目失败: {e}")
            return False, f"构建项目失败: {str(e)}", None
    
    @staticmethod
    def _build_python_project(project_path: Path, output_dir: Path) -> tuple[bool, str, Optional[str]]:
        """
        构建Python项目
        """
        try:
            # 检查是否有setup.py
            setup_py = project_path / "setup.py"
            if setup_py.exists():
                # 使用setup.py构建
                cmd = [
                    sys.executable, "setup.py", "bdist_wheel",
                    "--dist-dir", str(output_dir)
                ]
                
                logger.info(f"执行构建命令: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    cwd=str(project_path),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return False, f"构建失败: {result.stderr}", None
                
                # 查找构建结果
                wheel_files = list(output_dir.glob("*.whl"))
                if wheel_files:
                    return True, "构建成功", str(wheel_files[0])
                else:
                    return False, "构建成功但未找到输出文件", None
            
            # 检查是否有pyproject.toml
            pyproject_toml = project_path / "pyproject.toml"
            if pyproject_toml.exists():
                # 使用pip构建
                cmd = [
                    sys.executable, "-m", "pip", "wheel",
                    "--wheel-dir", str(output_dir),
                    str(project_path)
                ]
                
                logger.info(f"执行构建命令: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return False, f"构建失败: {result.stderr}", None
                
                # 查找构建结果
                wheel_files = list(output_dir.glob("*.whl"))
                if wheel_files:
                    return True, "构建成功", str(wheel_files[0])
                else:
                    return False, "构建成功但未找到输出文件", None
            
            # 简单Python项目，创建zip包
            return BuildDeployService._create_python_zip(project_path, output_dir)
            
        except Exception as e:
            logger.exception(f"构建Python项目失败: {e}")
            return False, f"构建Python项目失败: {str(e)}", None
    
    @staticmethod
    def _create_python_zip(project_path: Path, output_dir: Path) -> tuple[bool, str, Optional[str]]:
        """
        创建Python项目的zip包
        """
        try:
            import zipfile
            
            # 创建zip文件
            project_name = project_path.name
            zip_path = output_dir / f"{project_name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 遍历项目文件
                for root, dirs, files in os.walk(project_path):
                    # 跳过__pycache__和其他不需要的目录
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', 'build', 'dist', '.git']]
                    
                    for file in files:
                        if file.endswith('.pyc'):
                            continue
                        
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(project_path)
                        zf.write(file_path, rel_path)
            
            return True, "构建成功", str(zip_path)
            
        except Exception as e:
            logger.exception(f"创建Python zip包失败: {e}")
            return False, f"创建Python zip包失败: {str(e)}", None
    
    @staticmethod
    def deploy_project(build_result: str, target_path: str) -> tuple[bool, str]:
        """
        部署项目
        
        Args:
            build_result: 构建结果路径
            target_path: 部署目标路径
            
        Returns:
            (成功标志, 错误信息)
        """
        try:
            build_result = Path(build_result)
            target_path = Path(target_path)
            
            if not build_result.exists():
                return False, f"构建结果不存在: {build_result}"
            
            # 确保目标目录存在
            ensure_directory(target_path)
            
            # 根据构建结果类型进行部署
            if build_result.suffix == '.whl':
                # 安装wheel包
                return BuildDeployService._deploy_wheel(build_result, target_path)
            elif build_result.suffix == '.zip':
                # 解压zip包
                return BuildDeployService._deploy_zip(build_result, target_path)
            else:
                # 直接复制文件
                return BuildDeployService._deploy_copy(build_result, target_path)
                
        except Exception as e:
            logger.exception(f"部署项目失败: {e}")
            return False, f"部署项目失败: {str(e)}"
    
    @staticmethod
    def _deploy_wheel(wheel_path: Path, target_path: Path) -> tuple[bool, str]:
        """
        部署wheel包
        """
        try:
            # 安装wheel包
            cmd = [
                sys.executable, "-m", "pip", "install",
                str(wheel_path),
                "--target", str(target_path)
            ]
            
            logger.info(f"执行部署命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, f"部署失败: {result.stderr}"
            
            return True, "部署成功"
            
        except Exception as e:
            logger.exception(f"部署wheel包失败: {e}")
            return False, f"部署wheel包失败: {str(e)}"
    
    @staticmethod
    def _deploy_zip(zip_path: Path, target_path: Path) -> tuple[bool, str]:
        """
        部署zip包
        """
        try:
            import zipfile
            
            # 解压zip包
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(target_path)
            
            return True, "部署成功"
            
        except Exception as e:
            logger.exception(f"部署zip包失败: {e}")
            return False, f"部署zip包失败: {str(e)}"
    
    @staticmethod
    def _deploy_copy(file_path: Path, target_path: Path) -> tuple[bool, str]:
        """
        直接复制文件
        """
        try:
            # 复制文件到目标目录
            target_file = target_path / file_path.name
            shutil.copy2(file_path, target_file)
            
            return True, "部署成功"
            
        except Exception as e:
            logger.exception(f"复制文件失败: {e}")
            return False, f"复制文件失败: {str(e)}"
    
    @staticmethod
    def build_and_deploy(project_path: str, deploy_path: str) -> tuple[bool, str, Optional[str]]:
        """
        构建并部署项目
        
        Args:
            project_path: 项目路径
            deploy_path: 部署路径
            
        Returns:
            (成功标志, 错误信息, 构建结果路径)
        """
        # 构建项目
        build_success, build_error, build_result = BuildDeployService.build_project(project_path)
        if not build_success:
            return False, f"构建失败: {build_error}", None
        
        # 部署项目
        deploy_success, deploy_error = BuildDeployService.deploy_project(build_result, deploy_path)
        if not deploy_success:
            return False, f"部署失败: {deploy_error}", build_result
        
        return True, "构建和部署成功", build_result
    
    @staticmethod
    def get_build_info(project_path: str) -> Dict:
        """
        获取项目构建信息
        
        Args:
            project_path: 项目路径
            
        Returns:
            构建信息字典
        """
        try:
            project_path = Path(project_path)
            
            info = {
                "项目路径": str(project_path),
                "项目名称": project_path.name,
                "是否存在": project_path.exists(),
                "是否为Python项目": False,
                "构建类型": "未知"
            }
            
            if not project_path.exists():
                return info
            
            # 检查项目类型
            if (project_path / "setup.py").exists():
                info["是否为Python项目"] = True
                info["构建类型"] = "setup.py"
            elif (project_path / "pyproject.toml").exists():
                info["是否为Python项目"] = True
                info["构建类型"] = "pyproject.toml"
            elif (project_path / "__init__.py").exists():
                info["是否为Python项目"] = True
                info["构建类型"] = "Python模块"
            
            return info
            
        except Exception as e:
            logger.exception(f"获取构建信息失败: {e}")
            return {"错误": str(e)}
    
    @staticmethod
    def batch_build(projects: List[str], output_dir: str) -> List[Dict]:
        """
        批量构建项目
        
        Args:
            projects: 项目路径列表
            output_dir: 输出目录
            
        Returns:
            构建结果列表
        """
        results = []
        
        for project_path in projects:
            try:
                success, error, build_result = BuildDeployService.build_project(
                    project_path, output_dir
                )
                results.append({
                    "项目路径": project_path,
                    "成功": success,
                    "错误信息": error,
                    "构建结果": build_result
                })
            except Exception as e:
                logger.exception(f"构建项目 {project_path} 失败: {e}")
                results.append({
                    "项目路径": project_path,
                    "成功": False,
                    "错误信息": str(e),
                    "构建结果": None
                })
        
        return results
    
    @staticmethod
    def batch_deploy(build_results: List[str], deploy_path: str) -> List[Dict]:
        """
        批量部署项目
        
        Args:
            build_results: 构建结果路径列表
            deploy_path: 部署路径
            
        Returns:
            部署结果列表
        """
        results = []
        
        for build_result in build_results:
            try:
                success, error = BuildDeployService.deploy_project(
                    build_result, deploy_path
                )
                results.append({
                    "构建结果": build_result,
                    "成功": success,
                    "错误信息": error
                })
            except Exception as e:
                logger.exception(f"部署项目 {build_result} 失败: {e}")
                results.append({
                    "构建结果": build_result,
                    "成功": False,
                    "错误信息": str(e)
                })
        
        return results