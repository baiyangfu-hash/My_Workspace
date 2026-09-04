# -*- coding: utf-8 -*-
"""
规范管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.spec_service import SpecService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("specs", __name__)

@bp.route("", methods=["GET"])
def list_specs():
    """获取规范列表"""
    category = request.args.get("category")
    keyword = request.args.get("keyword")
    
    specs = SpecService.list_specs(category=category, keyword=keyword)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "specs": [s.to_dict() for s in specs],
            "total": len(specs)
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<spec_id>", methods=["GET"])
def get_spec(spec_id):
    """获取规范详情"""
    spec = SpecService.get_spec(spec_id)
    if not spec:
        return jsonify({
            "code": 404,
            "message": "规范不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "spec": spec.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<spec_id>/content", methods=["GET"])
def get_spec_content(spec_id):
    """获取规范内容"""
    content, error = SpecService.get_spec_content(spec_id)
    if error:
        return jsonify({
            "code": 404,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "content": content
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("", methods=["POST"])
def create_spec():
    """创建新规范"""
    data = request.get_json()
    
    spec, error = SpecService.create_spec(data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "规范创建成功",
        "data": {
            "spec": spec.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201
