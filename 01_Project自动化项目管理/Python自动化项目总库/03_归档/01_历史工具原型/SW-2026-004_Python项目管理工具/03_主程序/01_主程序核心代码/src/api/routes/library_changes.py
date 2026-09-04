# -*- coding: utf-8 -*-
"""
总库变更管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.library_change_service import LibraryChangeService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("library_changes", __name__)

@bp.route("", methods=["POST"])
def create_library_change():
    """创建总库变更"""
    data = request.get_json()
    
    required_fields = ["library_id", "change_type", "title"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    change, error = LibraryChangeService.create_change(
        library_id=data["library_id"],
        change_type=data["change_type"],
        title=data["title"],
        description=data.get("description"),
        requested_by=data.get("requested_by"),
        impact_assessment=data.get("impact_assessment"),
        implementation_plan=data.get("implementation_plan")
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "总库变更创建成功",
        "data": {
            "change": change.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("", methods=["GET"])
def list_library_changes():
    """获取总库变更列表"""
    library_id = request.args.get("library_id")
    status = request.args.get("status")
    change_type = request.args.get("change_type")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    
    changes, total = LibraryChangeService.list_changes(
        library_id=library_id,
        status=status,
        change_type=change_type,
        keyword=keyword,
        page=page,
        size=size
    )
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "changes": [c.to_dict() for c in changes],
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<change_id>", methods=["GET"])
def get_library_change(change_id):
    """获取总库变更详情"""
    change = LibraryChangeService.get_change(change_id)
    if not change:
        return jsonify({
            "code": 404,
            "message": "变更不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "change": change.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<change_id>", methods=["PUT"])
def update_library_change(change_id):
    """更新总库变更信息"""
    data = request.get_json()
    
    change, error = LibraryChangeService.update_change(change_id, data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not change:
        return jsonify({
            "code": 404,
            "message": "变更不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "更新成功",
        "data": {
            "change": change.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<change_id>", methods=["DELETE"])
def delete_library_change(change_id):
    """删除总库变更"""
    success, error = LibraryChangeService.delete_change(change_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "变更不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "删除成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<change_id>/approve", methods=["POST"])
def approve_library_change(change_id):
    """审批总库变更"""
    data = request.get_json() or {}
    approved_by = data.get("approved_by")
    comments = data.get("comments")
    
    if not approved_by:
        return jsonify({
            "code": 400,
            "message": "缺少审批人",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    success, error = LibraryChangeService.approve_change(change_id, approved_by, comments)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "审批成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<change_id>/reject", methods=["POST"])
def reject_library_change(change_id):
    """拒绝总库变更"""
    data = request.get_json() or {}
    rejected_by = data.get("rejected_by")
    comments = data.get("comments")
    
    if not rejected_by:
        return jsonify({
            "code": 400,
            "message": "缺少拒绝人",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    success, error = LibraryChangeService.reject_change(change_id, rejected_by, comments)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "拒绝成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/statistics", methods=["GET"])
def get_library_change_statistics():
    """获取总库变更统计信息"""
    library_id = request.args.get("library_id")
    stats = LibraryChangeService.get_change_statistics(library_id)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })
