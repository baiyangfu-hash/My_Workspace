# -*- coding: utf-8 -*-
"""
Flask应用入口
"""
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from src.core.config import Config
from src.utils.logger import setup_logger
from src.api.auth import login, auth_required, role_required

logger = setup_logger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config["SECRET_KEY"] = Config.get("api.secret_key", "dev-secret-key")
    app.config["JSON_AS_ASCII"] = False
    
    # 启用CORS
    if Config.get("api.cors_enabled", True):
        CORS(app)
    
    # 请求中间件
    @app.before_request
    def before_request():
        """请求预处理"""
        request.request_id = f"req-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        logger.info(f"[{request.request_id}] {request.method} {request.path}")
    
    # 统一响应格式
    @app.after_request
    def after_request(response):
        """响应后处理"""
        if response.is_json:
            data = response.get_json()
            if isinstance(data, dict) and "code" in data:
                # 已经是标准格式
                return response
            
            # 包装为标准格式
            response.set_data(jsonify({
                "code": 200,
                "message": "操作成功",
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "request_id": request.request_id
            }).data)
        
        return response
    
    # 错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "code": 400,
            "message": "请求参数错误",
            "data": str(error),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "code": 401,
            "message": "未授权访问",
            "data": str(error),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "code": 403,
            "message": "权限不足",
            "data": str(error),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "code": 404,
            "message": "资源不存在",
            "data": str(error),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.exception(f"服务器内部错误: {error}")
        return jsonify({
            "code": 500,
            "message": "服务器内部错误",
            "data": str(error),
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id
        }), 500
    
    # 登录路由
    @app.route("/api/v1/login", methods=["POST"])
    def login_route():
        """用户登录"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "code": 400,
                    "message": "缺少请求参数",
                    "data": None
                }), 400
            
            username = data.get("username")
            password = data.get("password")
            
            if not username or not password:
                return jsonify({
                    "code": 400,
                    "message": "用户名和密码不能为空",
                    "data": None
                }), 400
            
            result = login(username, password)
            if result["success"]:
                return jsonify({
                    "code": 200,
                    "message": result["message"],
                    "data": {
                        "token": result["token"],
                        "user": result["user"]
                    }
                })
            else:
                return jsonify({
                    "code": 401,
                    "message": result["message"],
                    "data": None
                }), 401
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return jsonify({
                "code": 500,
                "message": "登录失败",
                "data": str(e)
            }), 500
    
    # 注册路由
    from api.routes.projects import bp as projects_bp
    from api.routes.templates import bp as templates_bp
    from api.routes.plugins import bp as plugins_bp
    from api.routes.specs import bp as specs_bp
    from api.routes.libraries import bp as libraries_bp
    from api.routes.library_changes import bp as library_changes_bp
    from api.routes.library_dashboard import bp as library_dashboard_bp
    from api.routes.defects import defects_bp
    
    app.register_blueprint(projects_bp, url_prefix="/api/v1/projects")
    app.register_blueprint(templates_bp, url_prefix="/api/v1/templates")
    app.register_blueprint(plugins_bp, url_prefix="/api/v1/plugins")
    app.register_blueprint(specs_bp, url_prefix="/api/v1/specs")
    app.register_blueprint(libraries_bp, url_prefix="/api/v1/libraries")
    app.register_blueprint(library_changes_bp, url_prefix="/api/v1/library-changes")
    app.register_blueprint(library_dashboard_bp, url_prefix="/api/v1/library-dashboard")
    app.register_blueprint(defects_bp, url_prefix="/api/v1/defects")
    
    # 根路径
    @app.route("/api/v1/health")
    def health_check():
        """健康检查"""
        return {
            "status": "ok",
            "version": Config.get("version"),
            "timestamp": datetime.now().isoformat()
        }
    
    logger.info("Flask应用初始化完成")
    return app
