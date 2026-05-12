# -*- coding: utf-8 -*-
"""
总库管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.library_service import LibraryService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("libraries", __name__)

@bp.route("", methods=["POST"])
def create_library():
    """创建总库"""
    data = request.get_json()
    
    required_fields = ["name", "root_path"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    library, error = LibraryService.create_library(
        name=data["name"],
        root_path=data["root_path"],
        description=data.get("description")
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "总库创建成功",
        "data": {
            "library": library.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("", methods=["GET"])
def list_libraries():
    """获取总库列表"""
    status = request.args.get("status")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    
    libraries, total = LibraryService.list_libraries(
        status=status,
        keyword=keyword,
        page=page,
        size=size
    )
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "libraries": [l.to_dict() for l in libraries],
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>", methods=["GET"])
def get_library(library_id):
    """获取总库详情"""
    library = LibraryService.get_library(library_id)
    if not library:
        return jsonify({
            "code": 404,
            "message": "总库不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    # 补充统计信息
    library_dict = library.to_dict()
    library_dict["statistics"] = LibraryService.get_library_statistics(library_id)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "library": library_dict
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>", methods=["PUT"])
def update_library(library_id):
    """更新总库信息"""
    data = request.get_json()
    
    library, error = LibraryService.update_library(library_id, data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not library:
        return jsonify({
            "code": 404,
            "message": "总库不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "更新成功",
        "data": {
            "library": library.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>", methods=["DELETE"])
def delete_library(library_id):
    """删除总库"""
    success, error = LibraryService.delete_library(library_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "总库不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "删除成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/projects", methods=["GET"])
def list_library_projects(library_id):
    """获取总库中的项目列表"""
    category_id = request.args.get("category_id")
    status = request.args.get("status")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    
    projects, total = LibraryService.list_library_projects(
        library_id=library_id,
        category_id=category_id,
        status=status,
        keyword=keyword,
        page=page,
        size=size
    )
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "projects": [p.to_dict() for p in projects],
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/projects", methods=["POST"])
def add_project_to_library(library_id):
    """将项目添加到总库"""
    data = request.get_json()
    
    required_fields = ["project_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    success, error = LibraryService.add_project_to_library(
        library_id=library_id,
        project_id=data["project_id"],
        category_id=data.get("category_id")
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "项目添加成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/projects/<project_id>", methods=["DELETE"])
def remove_project_from_library(library_id, project_id):
    """从总库中移除项目"""
    success, error = LibraryService.remove_project_from_library(
        library_id=library_id,
        project_id=project_id
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "项目移除成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/categories", methods=["GET"])
def list_categories(library_id):
    """获取总库的分类列表"""
    categories = LibraryService.list_categories(library_id)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "categories": [c.to_dict() for c in categories]
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/categories", methods=["POST"])
def create_category(library_id):
    """创建分类"""
    data = request.get_json()
    
    required_fields = ["name"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    category, error = LibraryService.create_category(
        library_id=library_id,
        name=data["name"],
        description=data.get("description"),
        parent_id=data.get("parent_id")
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "分类创建成功",
        "data": {
            "category": category.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("/<library_id>/scan", methods=["POST"])
def scan_and_import_projects(library_id):
    """扫描并导入项目到总库"""
    data = request.get_json()
    
    required_fields = ["scan_path", "business_line", "template_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    success_projects, failed_projects = LibraryService.scan_and_import_projects(
        library_id=library_id,
        scan_path=data["scan_path"],
        business_line=data["business_line"],
        template_id=data["template_id"],
        category_id=data.get("category_id")
    )
    
    return jsonify({
        "code": 200,
        "message": "扫描完成",
        "data": {
            "success_count": len(success_projects),
            "failed_count": len(failed_projects),
            "success_projects": [p.to_dict() for p in success_projects],
            "failed_projects": failed_projects
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<library_id>/statistics", methods=["GET"])
def get_library_statistics(library_id):
    """获取总库统计信息"""
    stats = LibraryService.get_library_statistics(library_id)
    
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })
