# -*- coding: utf-8 -*-
"""
模板管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.template_service import TemplateService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("templates", __name__)

@bp.route("", methods=["GET"])
def list_templates():
    """获取模板列表"""
    compiler = request.args.get("compiler")
    scene = request.args.get("scene")
    is_builtin = request.args.get("is_builtin")
    
    if is_builtin is not None:
        is_builtin = is_builtin.lower() == "true"
    
    templates = TemplateService.list_templates(
        compiler=compiler,
        scene=scene,
        is_builtin=is_builtin
    )
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "templates": [t.to_dict() for t in templates],
            "total": len(templates)
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<template_id>", methods=["GET"])
def get_template(template_id):
    """获取模板详情"""
    template = TemplateService.get_template(template_id)
    if not template:
        return jsonify({
            "code": 404,
            "message": "模板不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "template": template.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("", methods=["POST"])
def create_template():
    """创建自定义模板"""
    data = request.get_json()
    
    template, error = TemplateService.create_template(data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "模板创建成功",
        "data": {
            "template": template.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("/<template_id>", methods=["PUT"])
def update_template(template_id):
    """更新模板信息"""
    data = request.get_json()
    
    template, error = TemplateService.update_template(template_id, data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not template:
        return jsonify({
            "code": 404,
            "message": "模板不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "更新成功",
        "data": {
            "template": template.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<template_id>", methods=["DELETE"])
def delete_template(template_id):
    """删除模板"""
    success, error = TemplateService.delete_template(template_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "模板不存在或为内置模板",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "删除成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<template_id>/export", methods=["GET"])
def export_template(template_id):
    """导出模板"""
    json_data, error = TemplateService.export_template(template_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "导出成功",
        "data": {
            "template_json": json_data
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/import", methods=["POST"])
def import_template():
    """导入模板"""
    data = request.get_json()
    if "template_json" not in data:
        return jsonify({
            "code": 400,
            "message": "缺少参数: template_json",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    template, error = TemplateService.import_template(data["template_json"])
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "导入成功",
        "data": {
            "template": template.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("/validate", methods=["POST"])
def validate_template():
    """验证模板结构"""
    data = request.get_json()
    if "structure" not in data:
        return jsonify({
            "code": 400,
            "message": "缺少参数: structure",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    valid, message = TemplateService.validate_template_structure(data["structure"])
    return jsonify({
        "code": 200,
        "message": message,
        "data": {
            "valid": valid
        },
        "timestamp": datetime.now().isoformat()
    })
