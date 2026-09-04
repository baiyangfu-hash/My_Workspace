# -*- coding: utf-8 -*-
"""
总库仪表盘API
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from src.services.library_dashboard_service import LibraryDashboardService
from src.services.library_report_service import LibraryReportService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
bp = Blueprint("library_dashboard", __name__)

@bp.route("/<library_id>/overview", methods=["GET"])
def get_library_overview(library_id):
    """获取总库概览信息"""
    try:
        overview = LibraryDashboardService.get_library_overview(library_id)
        if not overview:
            return jsonify({
                "code": 404,
                "message": "总库不存在或获取概览数据失败",
                "timestamp": datetime.now().isoformat()
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "查询成功",
            "data": overview,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"获取总库概览失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取总库概览失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/<library_id>/trends", methods=["GET"])
def get_library_trends(library_id):
    """获取总库趋势数据"""
    try:
        days = int(request.args.get("days", 30))
        trends = LibraryDashboardService.get_library_trends(library_id, days)
        if not trends:
            return jsonify({
                "code": 404,
                "message": "总库不存在或获取趋势数据失败",
                "timestamp": datetime.now().isoformat()
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "查询成功",
            "data": trends,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"获取总库趋势失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取总库趋势失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/<library_id>/health", methods=["GET"])
def get_library_health(library_id):
    """获取总库健康状态"""
    try:
        health = LibraryDashboardService.get_library_health(library_id)
        if not health:
            return jsonify({
                "code": 404,
                "message": "总库不存在或获取健康状态失败",
                "timestamp": datetime.now().isoformat()
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "查询成功",
            "data": health,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"获取总库健康状态失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取总库健康状态失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/<library_id>/reports/overview", methods=["POST"])
def generate_library_overview_report(library_id):
    """生成总库概览报表"""
    try:
        data = request.get_json() or {}
        output_path = data.get("output_path")
        
        report_path, error = LibraryReportService.generate_library_overview_report(library_id, output_path)
        if error:
            return jsonify({
                "code": 400,
                "message": error,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "报表生成成功",
            "data": {
                "report_path": report_path
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"生成总库概览报表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"生成报表失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/<library_id>/reports/statistics", methods=["POST"])
def generate_library_statistics_report(library_id):
    """生成总库统计报表"""
    try:
        data = request.get_json() or {}
        output_path = data.get("output_path")
        
        report_path, error = LibraryReportService.generate_library_statistics_report(library_id, output_path)
        if error:
            return jsonify({
                "code": 400,
                "message": error,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "报表生成成功",
            "data": {
                "report_path": report_path
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"生成总库统计报表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"生成报表失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@bp.route("/<library_id>/reports/trend", methods=["POST"])
def generate_library_trend_report(library_id):
    """生成总库趋势报表"""
    try:
        data = request.get_json() or {}
        output_path = data.get("output_path")
        days = int(data.get("days", 30))
        
        report_path, error = LibraryReportService.generate_library_trend_report(library_id, days, output_path)
        if error:
            return jsonify({
                "code": 400,
                "message": error,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "报表生成成功",
            "data": {
                "report_path": report_path
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception(f"生成总库趋势报表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"生成报表失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500
