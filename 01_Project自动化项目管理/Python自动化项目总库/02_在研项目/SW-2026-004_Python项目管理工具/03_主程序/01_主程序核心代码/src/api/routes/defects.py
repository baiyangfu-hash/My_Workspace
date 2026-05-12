# -*- coding: utf-8 -*-
"""
缺陷管理API路由
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from src.services.defect_service import DefectService
from src.models.defect import DefectStatus, DefectPriority, DefectSeverity
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# 创建蓝图
defects_bp = Blueprint('defects', __name__)


@defects_bp.route('/defects', methods=['GET'])
def get_defects():
    """获取缺陷列表"""
    try:
        # 获取查询参数
        filters = {}
        if 'status' in request.args:
            filters['status'] = request.args['status']
        if 'priority' in request.args:
            filters['priority'] = request.args['priority']
        if 'severity' in request.args:
            filters['severity'] = request.args['severity']
        if 'project_id' in request.args:
            filters['project_id'] = int(request.args['project_id'])
        if 'library_id' in request.args:
            filters['library_id'] = int(request.args['library_id'])
        if 'reporter' in request.args:
            filters['reporter'] = request.args['reporter']
        if 'assignee' in request.args:
            filters['assignee'] = request.args['assignee']
        if 'keyword' in request.args:
            filters['keyword'] = request.args['keyword']
        
        defects = DefectService.get_defects(**filters)
        return jsonify({
            'success': True,
            'data': [defect.to_dict() for defect in defects],
            'message': '获取缺陷列表成功'
        })
    except Exception as e:
        logger.error(f"获取缺陷列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取缺陷列表失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>', methods=['GET'])
def get_defect(defect_id: int):
    """获取缺陷详情"""
    try:
        defect = DefectService.get_defect(defect_id)
        if defect:
            return jsonify({
                'success': True,
                'data': defect.to_dict(),
                'message': '获取缺陷详情成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取缺陷详情失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取缺陷详情失败: {str(e)}'
        }), 500


@defects_bp.route('/defects', methods=['POST'])
def create_defect():
    """创建缺陷"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        # 验证必填字段
        required_fields = ['title', 'description', 'reporter']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        defect = DefectService.create_defect(data)
        return jsonify({
            'success': True,
            'data': defect.to_dict(),
            'message': '创建缺陷成功'
        }), 201
    except Exception as e:
        logger.error(f"创建缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'创建缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>', methods=['PUT'])
def update_defect(defect_id: int):
    """更新缺陷"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        defect = DefectService.update_defect(defect_id, data)
        if defect:
            return jsonify({
                'success': True,
                'data': defect.to_dict(),
                'message': '更新缺陷成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在'
            }), 404
    except Exception as e:
        logger.error(f"更新缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>', methods=['DELETE'])
def delete_defect(defect_id: int):
    """删除缺陷"""
    try:
        success = DefectService.delete_defect(defect_id)
        if success:
            return jsonify({
                'success': True,
                'message': '删除缺陷成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在'
            }), 404
    except Exception as e:
        logger.error(f"删除缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'删除缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>/status', methods=['PATCH'])
def change_defect_status(defect_id: int):
    """变更缺陷状态"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': '缺少状态参数'
            }), 400
        
        status = data['status']
        defect = DefectService.change_defect_status(defect_id, status)
        if defect:
            return jsonify({
                'success': True,
                'data': defect.to_dict(),
                'message': '变更缺陷状态成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在或状态无效'
            }), 404
    except Exception as e:
        logger.error(f"变更缺陷状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'变更缺陷状态失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>/assign', methods=['PATCH'])
def assign_defect(defect_id: int):
    """分配缺陷"""
    try:
        data = request.get_json()
        if not data or 'assignee' not in data:
            return jsonify({
                'success': False,
                'message': '缺少负责人参数'
            }), 400
        
        assignee = data['assignee']
        defect = DefectService.assign_defect(defect_id, assignee)
        if defect:
            return jsonify({
                'success': True,
                'data': defect.to_dict(),
                'message': '分配缺陷成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在'
            }), 404
    except Exception as e:
        logger.error(f"分配缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'分配缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/<int:defect_id>/resolve', methods=['PATCH'])
def resolve_defect(defect_id: int):
    """解决缺陷"""
    try:
        data = request.get_json()
        if not data or 'resolution' not in data or 'fix_version' not in data:
            return jsonify({
                'success': False,
                'message': '缺少解决方案或修复版本参数'
            }), 400
        
        resolution = data['resolution']
        fix_version = data['fix_version']
        defect = DefectService.resolve_defect(defect_id, resolution, fix_version)
        if defect:
            return jsonify({
                'success': True,
                'data': defect.to_dict(),
                'message': '解决缺陷成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '缺陷不存在'
            }), 404
    except Exception as e:
        logger.error(f"解决缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'解决缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/statistics', methods=['GET'])
def get_defect_statistics():
    """获取缺陷统计信息"""
    try:
        statistics = DefectService.get_defect_statistics()
        return jsonify({
            'success': True,
            'data': statistics,
            'message': '获取缺陷统计信息成功'
        })
    except Exception as e:
        logger.error(f"获取缺陷统计信息失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取缺陷统计信息失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/project/<int:project_id>', methods=['GET'])
def get_defects_by_project(project_id: int):
    """获取项目相关的缺陷"""
    try:
        defects = DefectService.get_defects_by_project(project_id)
        return jsonify({
            'success': True,
            'data': [defect.to_dict() for defect in defects],
            'message': '获取项目缺陷成功'
        })
    except Exception as e:
        logger.error(f"获取项目缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取项目缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/library/<int:library_id>', methods=['GET'])
def get_defects_by_library(library_id: int):
    """获取库相关的缺陷"""
    try:
        defects = DefectService.get_defects_by_library(library_id)
        return jsonify({
            'success': True,
            'data': [defect.to_dict() for defect in defects],
            'message': '获取库缺陷成功'
        })
    except Exception as e:
        logger.error(f"获取库缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取库缺陷失败: {str(e)}'
        }), 500


@defects_bp.route('/defects/search', methods=['GET'])
def search_defects():
    """搜索缺陷"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({
                'success': False,
                'message': '缺少搜索关键词'
            }), 400
        
        defects = DefectService.search_defects(keyword)
        return jsonify({
            'success': True,
            'data': [defect.to_dict() for defect in defects],
            'message': '搜索缺陷成功'
        })
    except Exception as e:
        logger.error(f"搜索缺陷失败: {e}")
        return jsonify({
            'success': False,
            'message': f'搜索缺陷失败: {str(e)}'
        }), 500
