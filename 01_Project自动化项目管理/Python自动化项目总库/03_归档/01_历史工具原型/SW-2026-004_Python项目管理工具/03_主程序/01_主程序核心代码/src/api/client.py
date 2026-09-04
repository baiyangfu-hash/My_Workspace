# -*- coding: utf-8 -*-
"""
API客户端工具，用于AI访问项目管理工具的API接口
"""
import requests
import json
import time
from typing import Dict, Any, Optional, List


class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """初始化API客户端
        
        Args:
            base_url: API服务基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录结果
        """
        url = f"{self.base_url}/api/v1/login"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 200:
                self.token = result["data"]["token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                return result
            else:
                return result
        except Exception as e:
            return {
                "code": 500,
                "message": f"登录失败: {str(e)}",
                "data": None
            }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送API请求
        
        Args:
            method: 请求方法（GET, POST, PUT, DELETE）
            endpoint: API端点
            data: 请求数据
            
        Returns:
            请求结果
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=self.headers, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=self.timeout)
            else:
                return {
                    "code": 400,
                    "message": f"不支持的请求方法: {method}",
                    "data": None
                }
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "code": 500,
                "message": f"请求失败: {str(e)}",
                "data": None
            }
    
    # 项目管理API
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目
        
        Args:
            project_data: 项目数据
            
        Returns:
            创建结果
        """
        return self._request("POST", "/api/v1/projects", project_data)
    
    def get_projects(self) -> Dict[str, Any]:
        """获取项目列表
        
        Returns:
            项目列表
        """
        return self._request("GET", "/api/v1/projects")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """获取项目详情
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目详情
        """
        return self._request("GET", f"/api/v1/projects/{project_id}")
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目
        
        Args:
            project_id: 项目ID
            project_data: 项目数据
            
        Returns:
            更新结果
        """
        return self._request("PUT", f"/api/v1/projects/{project_id}", project_data)
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            删除结果
        """
        return self._request("DELETE", f"/api/v1/projects/{project_id}")
    
    # 模板管理API
    def get_templates(self) -> Dict[str, Any]:
        """获取模板列表
        
        Returns:
            模板列表
        """
        return self._request("GET", "/api/v1/templates")
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """获取模板详情
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板详情
        """
        return self._request("GET", f"/api/v1/templates/{template_id}")
    
    # 插件管理API
    def get_plugins(self) -> Dict[str, Any]:
        """获取插件列表
        
        Returns:
            插件列表
        """
        return self._request("GET", "/api/v1/plugins")
    
    def get_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """获取插件详情
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            插件详情
        """
        return self._request("GET", f"/api/v1/plugins/{plugin_id}")
    
    def install_plugin(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """安装插件
        
        Args:
            plugin_data: 插件数据
            
        Returns:
            安装结果
        """
        return self._request("POST", "/api/v1/plugins", plugin_data)
    
    # 规范管理API
    def get_specs(self) -> Dict[str, Any]:
        """获取规范列表
        
        Returns:
            规范列表
        """
        return self._request("GET", "/api/v1/specs")
    
    def check_spec_updates(self) -> Dict[str, Any]:
        """检查规范更新
        
        Returns:
            检查结果
        """
        return self._request("GET", "/api/v1/specs/check-updates")
    
    def sync_spec(self, spec_name: str) -> Dict[str, Any]:
        """同步规范
        
        Args:
            spec_name: 规范名称
            
        Returns:
            同步结果
        """
        return self._request("POST", f"/api/v1/specs/{spec_name}/sync")
    
    def sync_all_specs(self) -> Dict[str, Any]:
        """同步所有规范
        
        Returns:
            同步结果
        """
        return self._request("POST", "/api/v1/specs/sync-all")
    
    # 健康检查
    def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        Returns:
            健康状态
        """
        return self._request("GET", "/api/v1/health")


class CLIClient:
    """CLI客户端类，用于执行CLI命令"""
    
    def __init__(self, main_script: str = "main.py"):
        """初始化CLI客户端
        
        Args:
            main_script: 主脚本路径
        """
        self.main_script = main_script
    
    def run_command(self, command: str, *args, **kwargs) -> str:
        """执行CLI命令
        
        Args:
            command: 命令名称
            *args: 命令参数
            **kwargs: 命令选项
            
        Returns:
            命令执行结果
        """
        import subprocess
        import shlex
        
        # 使用完整的Python路径
        python_exe = "C:\\Users\\fubai\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"
        cmd_parts = [python_exe, self.main_script, command]
        
        # 添加位置参数
        for arg in args:
            cmd_parts.append(str(arg))
        
        # 添加选项参数
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    cmd_parts.append(f"--{key}")
            else:
                cmd_parts.append(f"--{key}")
                cmd_parts.append(str(value))
        
        cmd = " ".join(cmd_parts)
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n错误: {result.stderr}"
            
            # 添加命令执行信息
            output = f"执行命令: {cmd}\n" + output
            return output
        except Exception as e:
            return f"执行命令失败: {str(e)}"
    
    def check_spec(self, auto_sync: bool = False) -> str:
        """检查规范更新
        
        Args:
            auto_sync: 是否自动同步
            
        Returns:
            检查结果
        """
        return self.run_command("check-spec", auto_sync=auto_sync)
    
    def sync_spec(self, spec_name: Optional[str] = None, no_backup: bool = False) -> str:
        """同步规范
        
        Args:
            spec_name: 规范名称，None表示同步所有
            no_backup: 是否不备份
            
        Returns:
            同步结果
        """
        if spec_name:
            return self.run_command("sync-spec", spec_name=spec_name, no_backup=no_backup)
        else:
            return self.run_command("sync-spec", no_backup=no_backup)
    
    def create_project(self, business_line: str, name: str, template_id: str, 
                      path: Optional[str] = None, manager: Optional[str] = None) -> str:
        """创建项目
        
        Args:
            business_line: 业务线
            name: 项目名称
            template_id: 模板ID
            path: 自定义路径
            manager: 项目负责人
            
        Returns:
            创建结果
        """
        return self.run_command(
            "create-project",
            business_line=business_line,
            name=name,
            template_id=template_id,
            path=path,
            manager=manager
        )
    
    def check_project(self, project_id: str, type: str = "all") -> str:
        """检查项目规范
        
        Args:
            project_id: 项目ID
            type: 检查类型
            
        Returns:
            检查结果
        """
        return self.run_command("check-project", project_id, type=type)
    
    def spec_info(self) -> str:
        """显示规范信息
        
        Returns:
            规范信息
        """
        return self.run_command("spec-info")
    
    def info(self) -> str:
        """显示工具信息
        
        Returns:
            工具信息
        """
        return self.run_command("info")
    
    def version(self) -> str:
        """显示版本信息
        
        Returns:
            版本信息
        """
        return self.run_command("version")


class AIAccessManager:
    """AI访问管理器，整合API和CLI访问"""
    
    def __init__(self, base_url: str = "http://localhost:5000", main_script: str = "main.py"):
        """初始化AI访问管理器
        
        Args:
            base_url: API服务基础URL
            main_script: 主脚本路径
        """
        self.api_client = APIClient(base_url)
        self.cli_client = CLIClient(main_script)
        self.api_running = False
    
    def start_api_service(self) -> str:
        """启动API服务
        
        Returns:
            启动结果
        """
        import subprocess
        import time
        
        try:
            # 启动API服务（后台运行）
            cmd = f"python {self.cli_client.main_script} api"
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # 等待服务启动
            time.sleep(3)
            
            # 检查服务是否正常运行
            try:
                health_result = self.api_client.health_check()
                if health_result.get("status") == "ok":
                    self.api_running = True
                    return "API服务启动成功"
                else:
                    return f"API服务启动失败: {health_result.get('message', '未知错误')}"
            except Exception as e:
                return f"API服务启动失败: {str(e)}"
        except Exception as e:
            return f"启动API服务失败: {str(e)}"
    
    def stop_api_service(self) -> str:
        """停止API服务
        
        Returns:
            停止结果
        """
        import subprocess
        
        try:
            # 查找并终止API服务进程
            result = subprocess.run(
                "taskkill /F /IM python.exe /FI \"WINDOWTITLE eq *api*\"",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "SUCCESS" in result.stdout:
                self.api_running = False
                return "API服务停止成功"
            else:
                return f"API服务停止失败: {result.stdout}"
        except Exception as e:
            return f"停止API服务失败: {str(e)}"
    
    def ensure_api_running(self) -> bool:
        """确保API服务正在运行
        
        Returns:
            是否成功
        """
        if not self.api_running:
            result = self.start_api_service()
            if "成功" in result:
                return True
            else:
                return False
        else:
            # 检查服务是否真的在运行
            try:
                health_result = self.api_client.health_check()
                return health_result.get("status") == "ok"
            except:
                return False
    
    # 项目管理
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目
        
        Args:
            project_data: 项目数据
            
        Returns:
            创建结果
        """
        if self.ensure_api_running():
            return self.api_client.create_project(project_data)
        else:
            # 回退到CLI命令
            if all(key in project_data for key in ["business_line", "name", "template_id"]):
                result = self.cli_client.create_project(
                    business_line=project_data["business_line"],
                    name=project_data["name"],
                    template_id=project_data["template_id"],
                    path=project_data.get("path"),
                    manager=project_data.get("manager")
                )
                return {
                    "code": 200,
                    "message": "项目创建成功",
                    "data": {"output": result}
                }
            else:
                return {
                    "code": 400,
                    "message": "缺少必要的项目数据",
                    "data": None
                }
    
    def get_projects(self) -> Dict[str, Any]:
        """获取项目列表
        
        Returns:
            项目列表
        """
        if self.ensure_api_running():
            return self.api_client.get_projects()
        else:
            return {
                "code": 500,
                "message": "API服务未运行",
                "data": None
            }
    
    # 规范管理
    def check_spec_updates(self, auto_sync: bool = False) -> str:
        """检查规范更新
        
        Args:
            auto_sync: 是否自动同步
            
        Returns:
            检查结果
        """
        return self.cli_client.check_spec(auto_sync=auto_sync)
    
    def sync_specs(self, spec_name: Optional[str] = None) -> str:
        """同步规范
        
        Args:
            spec_name: 规范名称，None表示同步所有
            
        Returns:
            同步结果
        """
        return self.cli_client.sync_spec(spec_name=spec_name)
    
    def get_spec_info(self) -> str:
        """获取规范信息
        
        Returns:
            规范信息
        """
        return self.cli_client.spec_info()
    
    # 系统信息
    def get_tool_info(self) -> str:
        """获取工具信息
        
        Returns:
            工具信息
        """
        return self.cli_client.info()
    
    def get_version(self) -> str:
        """获取版本信息
        
        Returns:
            版本信息
        """
        return self.cli_client.version()


# 示例用法
if __name__ == "__main__":
    # 初始化AI访问管理器
    ai_manager = AIAccessManager()
    
    # 启动API服务
    print(ai_manager.start_api_service())
    
    # 检查API服务状态
    print(ai_manager.ensure_api_running())
    
    # 获取工具信息
    print(ai_manager.get_tool_info())
    
    # 检查规范更新
    print(ai_manager.check_spec_updates())
    
    # 同步规范
    print(ai_manager.sync_specs())
    
    # 获取规范信息
    print(ai_manager.get_spec_info())
    
    # 停止API服务
    print(ai_manager.stop_api_service())
