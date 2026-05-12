# -*- coding: utf-8 -*-
"""
插件管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.plugin_service import PluginService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("plugins", __name__)

@bp.route("", methods=["GET"])
def list_plugins():
    """获取插件列表"""
    status = request.args.get("status")
    
    plugins = PluginService.list_plugins(status=status)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "plugins": [p.to_dict() for p in plugins],
            "total": len(plugins)
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<plugin_id>", methods=["GET"])
def get_plugin(plugin_id):
    """获取插件详情"""
    plugin_info = PluginService.get_plugin(plugin_id)
    if not plugin_info:
        # 从数据库查询
        from dao.plugin_dao import PluginDAO
        plugin = PluginDAO.get_by_id(plugin_id)
        if not plugin:
            return jsonify({
                "code": 404,
                "message": "插件不存在",
                "timestamp": datetime.now().isoformat()
            }), 404
        plugin_dict = plugin.to_dict()
    else:
        plugin = plugin_info["model"]
        plugin_dict = plugin.to_dict()
        # 补充运行时信息
        plugin_dict["is_loaded"] = True
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "plugin": plugin_dict
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/install", methods=["POST"])
def install_plugin():
    """安装插件"""
    data = request.get_json()
    if "plugin_path" not in data:
        return jsonify({
            "code": 400,
            "message": "缺少参数: plugin_path",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    plugin, error = PluginService.install_plugin(data["plugin_path"])
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "插件安装成功",
        "data": {
            "plugin": plugin.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("/<plugin_id>/enable", methods=["PUT"])
def enable_plugin(plugin_id):
    """启用插件"""
    success, error = PluginService.enable_plugin(plugin_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "插件不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "插件已启用",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<plugin_id>/disable", methods=["PUT"])
def disable_plugin(plugin_id):
    """禁用插件"""
    success, error = PluginService.disable_plugin(plugin_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "插件不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "插件已禁用",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<plugin_id>/uninstall", methods=["DELETE"])
def uninstall_plugin(plugin_id):
    """卸载插件"""
    success, error = PluginService.uninstall_plugin(plugin_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "插件不存在或为内置插件",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "插件已卸载",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<plugin_id>/execute", methods=["POST"])
def execute_plugin(plugin_id):
    """执行插件功能"""
    data = request.get_json()
    if "action" not in data:
        return jsonify({
            "code": 400,
            "message": "缺少参数: action",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    result, error = PluginService.execute_plugin(
        plugin_id,
        action=data["action"],
        params=data.get("params", {})
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "执行成功",
        "data": {
            "result": result
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<plugin_id>/config", methods=["PUT"])
def update_config(plugin_id):
    """更新插件配置"""
    data = request.get_json()
    
    success, error = PluginService.update_plugin_config(plugin_id, data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "插件不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "配置更新成功",
        "timestamp": datetime.now().isoformat()
    })
