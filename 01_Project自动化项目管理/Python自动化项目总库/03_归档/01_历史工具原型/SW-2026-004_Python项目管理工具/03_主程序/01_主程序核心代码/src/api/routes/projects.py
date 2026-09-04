# -*- coding: utf-8 -*-
"""
项目管理API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.project_service import ProjectService
from src.services.check_service import CheckService
from src.services.report_service import ReportService
from src.utils.logger import setup_logger
from src.api.auth import auth_required, role_required

logger = setup_logger(__name__)
bp = Blueprint("projects", __name__)

@bp.route("", methods=["POST"])
@auth_required
@role_required(["admin"])
def create_project():
    """创建新项目"""
    data = request.get_json()
    
    required_fields = ["business_line", "name", "template_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"缺少必填字段: {field}",
                "timestamp": datetime.now().isoformat()
            }), 400
    
    project, error = ProjectService.create_project(
        business_line=data["business_line"],
        name=data["name"],
        template_id=data["template_id"],
        manager=data.get("manager"),
        description=data.get("description"),
        custom_path=data.get("path")
    )
    
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 201,
        "message": "项目创建成功",
        "data": {
            "project": project.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    }), 201

@bp.route("", methods=["GET"])
@auth_required
def list_projects():
    """获取项目列表"""
    status = request.args.get("status")
    business_line = request.args.get("business_line")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 20))
    
    projects, total = ProjectService.list_projects(
        status=status,
        business_line=business_line,
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

@bp.route("/<project_id>", methods=["GET"])
@auth_required
def get_project(project_id):
    """获取项目详情"""
    project = ProjectService.get_project(project_id)
    if not project:
        return jsonify({
            "code": 404,
            "message": "项目不存在",
            "timestamp": datetime.now().isoformat()
        }), 404

    # 修复P2-#17: 补充基本统计信息
    project_dict = project.to_dict()
    project_dict["statistics"] = {
        "total_tasks": len(project.tasks) if hasattr(project, 'tasks') else 0,
        "completed_tasks": len([t for t in project.tasks if hasattr(project, 'tasks') and t.status == 'completed']) if hasattr(project, 'tasks') else 0,
        "total_milestones": len(project.milestones) if hasattr(project, 'milestones') else 0,
        "completed_milestones": len([m for m in project.milestones if hasattr(project, 'milestones') and m.status == 'completed']) if hasattr(project, 'milestones') else 0,
    }
    # 计算任务完成率
    if project_dict["statistics"]["total_tasks"] > 0:
        project_dict["statistics"]["task_completion_rate"] = round(
            project_dict["statistics"]["completed_tasks"] / project_dict["statistics"]["total_tasks"] * 100, 2
        )
    else:
        project_dict["statistics"]["task_completion_rate"] = 0

    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": {
            "project": project_dict
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<project_id>", methods=["PUT"])
@auth_required
@role_required(["admin"])
def update_project(project_id):
    """更新项目信息"""
    data = request.get_json()
    
    project, error = ProjectService.update_project(project_id, data)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not project:
        return jsonify({
            "code": 404,
            "message": "项目不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "更新成功",
        "data": {
            "project": project.to_dict()
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<project_id>", methods=["DELETE"])
@auth_required
@role_required(["admin"])
def delete_project(project_id):
    """删除项目（软删除）"""
    success, error = ProjectService.delete_project(project_id)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    if not success:
        return jsonify({
            "code": 404,
            "message": "项目不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "code": 200,
        "message": "删除成功",
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/generate-code", methods=["GET"])
@auth_required
def generate_project_code():
    """生成项目编号"""
    business_line = request.args.get("business_line")
    if not business_line:
        return jsonify({
            "code": 400,
            "message": "缺少参数: business_line",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    code, error = ProjectService.generate_project_code(business_line)
    if error:
        return jsonify({
            "code": 400,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 400
    
    return jsonify({
        "code": 200,
        "message": "生成成功",
        "data": {
            "project_code": code
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<project_id>/check", methods=["POST"])
@auth_required
def check_project(project_id):
    """执行项目规范检查"""
    project = ProjectService.get_project(project_id)
    if not project:
        return jsonify({
            "code": 404,
            "message": "项目不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    data = request.get_json() or {}
    check_types = data.get("check_types")
    
    result, error = CheckService.check_project(project, check_types)
    if error:
        return jsonify({
            "code": 500,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 500
    
    # 生成报告
    report_path, report_error = ReportService.generate_check_report(project, result)
    
    return jsonify({
        "code": 200,
        "message": "检查完成",
        "data": {
            "report": result.to_dict(),
            "report_path": report_path
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/<project_id>/report", methods=["POST"])
@auth_required
def generate_report(project_id):
    """生成项目报告"""
    project = ProjectService.get_project(project_id)
    if not project:
        return jsonify({
            "code": 404,
            "message": "项目不存在",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    report_path, error = ReportService.generate_project_report(project)
    if error:
        return jsonify({
            "code": 500,
            "message": error,
            "timestamp": datetime.now().isoformat()
        }), 500
    
    return jsonify({
        "code": 200,
        "message": "报告生成成功",
        "data": {
            "report_path": report_path
        },
        "timestamp": datetime.now().isoformat()
    })

@bp.route("/statistics", methods=["GET"])
@auth_required
@role_required(["admin"])
def get_statistics():
    """获取项目统计信息"""
    stats = ProjectService.get_statistics()
    return jsonify({
        "code": 200,
        "message": "查询成功",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    })
