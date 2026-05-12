# -*- coding: utf-8 -*-
"""
插件市场服务

提供插件在线市场功能：浏览、搜索、下载、更新检查
"""
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import urllib.request
import urllib.error

from src.models.plugin import Plugin
from src.dao.plugin_dao import PluginDAO
from src.core.constants import PluginStatus
from src.core.plugin_metadata import PluginMetadata
from src.utils.logger import setup_logger
from src.utils.file_utils import read_json, write_json

logger = setup_logger(__name__)


@dataclass
class RemotePlugin:
    """远程插件信息"""
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    download_url: str
    repository: Optional[str] = None
    homepage: Optional[str] = None
    tags: List[str] = None
    icon: Optional[str] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    changelog: Optional[str] = None
    rating: float = 0.0
    download_count: int = 0
    installed: bool = False
    installed_version: Optional[str] = None
    has_update: bool = False
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PluginMarketService:
    """插件市场服务"""
    
    DEFAULT_MARKET_URL = "https://plugins.example.com/api/v1"
    LOCAL_CACHE_FILE = "plugin_market_cache.json"
    CACHE_EXPIRE_HOURS = 24
    
    def __init__(self, market_url: str = None):
        self.market_url = market_url or self.DEFAULT_MARKET_URL
        self._cache: List[RemotePlugin] = []
        self._cache_time: Optional[datetime] = None
        self._cache_file = Path(__file__).parent.parent.parent / "data" / self.LOCAL_CACHE_FILE
    
    def fetch_remote_plugins(self, force: bool = False) -> List[RemotePlugin]:
        """获取远程插件列表"""
        if not force and self._is_cache_valid():
            return self._cache
        
        try:
            plugins = self._fetch_from_remote()
            self._cache = plugins
            self._cache_time = datetime.now()
            self._save_cache()
            return plugins
        except Exception as e:
            logger.warning(f"从远程获取插件列表失败: {e}，使用本地缓存")
            if self._load_cache():
                return self._cache
            return self._get_demo_plugins()
    
    def _fetch_from_remote(self) -> List[RemotePlugin]:
        """从远程服务器获取插件列表"""
        url = f"{self.market_url}/plugins"
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Python-Project-Manager/1.0',
                'Accept': 'application/json'
            })
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            plugins = []
            for item in data.get('plugins', []):
                plugin = RemotePlugin(
                    plugin_id=item.get('plugin_id', ''),
                    name=item.get('name', ''),
                    version=item.get('version', '1.0.0'),
                    author=item.get('author', ''),
                    description=item.get('description', ''),
                    download_url=item.get('download_url', ''),
                    repository=item.get('repository'),
                    homepage=item.get('homepage'),
                    tags=item.get('tags', []),
                    icon=item.get('icon'),
                    min_app_version=item.get('min_app_version'),
                    max_app_version=item.get('max_app_version'),
                    changelog=item.get('changelog'),
                    rating=item.get('rating', 0.0),
                    download_count=item.get('download_count', 0),
                )
                plugins.append(plugin)
            
            self._mark_installed_plugins(plugins)
            return plugins
            
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络请求失败: {e}")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._cache or not self._cache_time:
            return False
        
        elapsed = datetime.now() - self._cache_time
        return elapsed.total_seconds() < self.CACHE_EXPIRE_HOURS * 3600
    
    def _load_cache(self) -> bool:
        """加载本地缓存"""
        try:
            if self._cache_file.exists():
                data = read_json(self._cache_file)
                self._cache = [RemotePlugin(**p) for p in data.get('plugins', [])]
                self._cache_time = datetime.fromisoformat(data.get('cache_time', datetime.now().isoformat()))
                self._mark_installed_plugins(self._cache)
                return True
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
        return False
    
    def _save_cache(self):
        """保存本地缓存"""
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'cache_time': self._cache_time.isoformat() if self._cache_time else None,
                'plugins': [
                    {
                        'plugin_id': p.plugin_id,
                        'name': p.name,
                        'version': p.version,
                        'author': p.author,
                        'description': p.description,
                        'download_url': p.download_url,
                        'repository': p.repository,
                        'homepage': p.homepage,
                        'tags': p.tags,
                        'icon': p.icon,
                        'min_app_version': p.min_app_version,
                        'max_app_version': p.max_app_version,
                        'changelog': p.changelog,
                        'rating': p.rating,
                        'download_count': p.download_count,
                    }
                    for p in self._cache
                ]
            }
            write_json(self._cache_file, data)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _mark_installed_plugins(self, plugins: List[RemotePlugin]):
        """标记已安装的插件"""
        installed_plugins = PluginDAO.list()
        installed_map = {p.plugin_id: p for p in installed_plugins}
        
        for plugin in plugins:
            if plugin.plugin_id in installed_map:
                plugin.installed = True
                plugin.installed_version = installed_map[plugin.plugin_id].version
                plugin.has_update = self._compare_versions(plugin.version, plugin.installed_version) > 0
    
    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """比较版本号，返回 1 表示 v1>v2，-1 表示 v1<v2，0 表示相等"""
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            for i in range(max(len(parts1), len(parts2))):
                p1 = parts1[i] if i < len(parts1) else 0
                p2 = parts2[i] if i < len(parts2) else 0
                
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            
            return 0
        except Exception:
            return 0
    
    def check_updates(self) -> List[Dict[str, Any]]:
        """检查已安装插件的更新"""
        updates = []
        
        try:
            remote_plugins = self.fetch_remote_plugins()
            
            for plugin in remote_plugins:
                if plugin.has_update:
                    updates.append({
                        'plugin_id': plugin.plugin_id,
                        'name': plugin.name,
                        'current_version': plugin.installed_version,
                        'latest_version': plugin.version,
                        'download_url': plugin.download_url,
                        'changelog': plugin.changelog,
                    })
            
            logger.info(f"检查更新完成，发现 {len(updates)} 个可用更新")
            
        except Exception as e:
            logger.error(f"检查更新失败: {e}")
        
        return updates
    
    def search_plugins(self, keyword: str) -> List[RemotePlugin]:
        """搜索插件"""
        plugins = self.fetch_remote_plugins()
        keyword = keyword.lower()
        
        results = []
        for plugin in plugins:
            if (keyword in plugin.name.lower() or
                keyword in plugin.description.lower() or
                keyword in plugin.author.lower() or
                any(keyword in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        
        return results
    
    def get_plugin_detail(self, plugin_id: str) -> Optional[RemotePlugin]:
        """获取插件详情"""
        plugins = self.fetch_remote_plugins()
        for plugin in plugins:
            if plugin.plugin_id == plugin_id:
                return plugin
        return None
    
    def download_plugin(self, plugin_id: str, download_url: str = None) -> tuple[Optional[str], str]:
        """下载插件包"""
        try:
            plugin = self.get_plugin_detail(plugin_id)
            if not plugin and not download_url:
                return None, "插件不存在"
            
            url = download_url or plugin.download_url
            if not url:
                return None, "没有可用的下载地址"
            
            temp_dir = tempfile.mkdtemp()
            zip_path = Path(temp_dir) / f"{plugin_id}.zip"
            
            logger.info(f"正在下载插件: {plugin_id}")
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Python-Project-Manager/1.0'
            })
            
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(zip_path, 'wb') as f:
                    f.write(response.read())
            
            logger.info(f"插件下载完成: {zip_path}")
            return str(zip_path), ""
            
        except Exception as e:
            logger.exception(f"下载插件失败: {e}")
            return None, f"下载插件失败: {str(e)}"
    
    def install_from_zip(self, zip_path: str, plugins_dir: str = None) -> tuple[Optional[Plugin], str]:
        """从ZIP包安装插件"""
        try:
            if plugins_dir is None:
                plugins_dir = Path(__file__).parent.parent / "plugins"
            else:
                plugins_dir = Path(plugins_dir)
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                temp_dir = tempfile.mkdtemp()
                zf.extractall(temp_dir)
                
                extracted_dir = Path(temp_dir)
                plugin_json = None
                
                for item in extracted_dir.rglob("plugin.json"):
                    plugin_json = item
                    break
                
                if not plugin_json:
                    shutil.rmtree(temp_dir)
                    return None, "ZIP包中未找到plugin.json文件"
                
                plugin_dir = plugin_json.parent
                meta = read_json(plugin_json)
                plugin_id = meta.get('plugin_id')
                
                if not plugin_id:
                    shutil.rmtree(temp_dir)
                    return None, "plugin.json中缺少plugin_id"
                
                target_dir = plugins_dir / plugin_id
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                shutil.copytree(plugin_dir, target_dir)
                shutil.rmtree(temp_dir)
                
                from src.services.plugin_service import PluginService
                plugin, error = PluginService.install_plugin(str(target_dir))
                
                if error:
                    return None, error
                
                logger.info(f"插件安装成功: {plugin_id}")
                return plugin, ""
                
        except Exception as e:
            logger.exception(f"安装插件失败: {e}")
            return None, f"安装插件失败: {str(e)}"
    
    def _get_demo_plugins(self) -> List[RemotePlugin]:
        """获取演示插件列表（离线模式）"""
        demo_data = [
            RemotePlugin(
                plugin_id="code_check",
                name="代码规范检查",
                version="1.1.0",
                author="Trae AI",
                description="检查Python代码是否符合PEP8规范，支持自定义规则",
                download_url="",
                tags=["开发工具", "代码质量"],
                rating=4.5,
                download_count=1250,
            ),
            RemotePlugin(
                plugin_id="document_generator",
                name="文档生成器",
                version="1.2.0",
                author="Trae AI",
                description="自动生成项目文档：README、接口文档、CHANGELOG等",
                download_url="",
                tags=["文档", "自动化"],
                rating=4.2,
                download_count=890,
            ),
            RemotePlugin(
                plugin_id="plc_variable_parser",
                name="PLC变量表解析器",
                version="1.0.0",
                author="Trae AI",
                description="解析和管理PLC变量表，支持Autoshop/Work3/Codesys格式",
                download_url="",
                tags=["PLC", "工控", "变量"],
                rating=4.8,
                download_count=456,
            ),
            RemotePlugin(
                plugin_id="git_helper",
                name="Git助手",
                version="2.0.0",
                author="Community",
                description="Git操作增强工具，提供可视化分支管理、冲突解决等功能",
                download_url="",
                tags=["Git", "版本控制"],
                rating=4.6,
                download_count=2100,
            ),
            RemotePlugin(
                plugin_id="api_tester",
                name="API测试工具",
                version="1.3.0",
                author="Community",
                description="RESTful API测试工具，支持请求构建、响应分析、批量测试",
                download_url="",
                tags=["API", "测试", "HTTP"],
                rating=4.4,
                download_count=1580,
            ),
        ]
        
        self._mark_installed_plugins(demo_data)
        return demo_data
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取插件分类"""
        plugins = self.fetch_remote_plugins()
        
        category_map = {}
        for plugin in plugins:
            for tag in plugin.tags:
                if tag not in category_map:
                    category_map[tag] = {
                        'name': tag,
                        'count': 0,
                        'plugins': []
                    }
                category_map[tag]['count'] += 1
                category_map[tag]['plugins'].append(plugin.plugin_id)
        
        return sorted(category_map.values(), key=lambda x: x['count'], reverse=True)
    
    def get_featured_plugins(self, limit: int = 5) -> List[RemotePlugin]:
        """获取推荐插件"""
        plugins = self.fetch_remote_plugins()
        return sorted(plugins, key=lambda x: x.rating, reverse=True)[:limit]
    
    def get_popular_plugins(self, limit: int = 10) -> List[RemotePlugin]:
        """获取热门插件"""
        plugins = self.fetch_remote_plugins()
        return sorted(plugins, key=lambda x: x.download_count, reverse=True)[:limit]
    
    @staticmethod
    def get_available_plugins(**kwargs) -> List[RemotePlugin]:
        """
        获取可用插件列表 (兼容性方法 - 静态方法)
        
        Args:
            **kwargs: 可选过滤参数
            
        Returns:
            可用插件列表
        """
        market = PluginMarketService()
        return market.fetch_remote_plugins()
