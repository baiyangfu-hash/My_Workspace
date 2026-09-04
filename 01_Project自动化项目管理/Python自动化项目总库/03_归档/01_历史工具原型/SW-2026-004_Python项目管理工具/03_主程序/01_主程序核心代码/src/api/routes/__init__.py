# -*- coding: utf-8 -*-
"""
API路由模块
"""
from flask import Blueprint

from .projects import bp as projects_bp
from .templates import bp as templates_bp
from .plugins import bp as plugins_bp
from .specs import bp as specs_bp
from .libraries import bp as libraries_bp
from .library_changes import bp as library_changes_bp
from .library_dashboard import bp as library_dashboard_bp
from .defects import defects_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(projects_bp, url_prefix='/projects')
api_bp.register_blueprint(templates_bp, url_prefix='/templates')
api_bp.register_blueprint(plugins_bp, url_prefix='/plugins')
api_bp.register_blueprint(specs_bp, url_prefix='/specs')
api_bp.register_blueprint(libraries_bp, url_prefix='/libraries')
api_bp.register_blueprint(library_changes_bp, url_prefix='/library-changes')
api_bp.register_blueprint(library_dashboard_bp, url_prefix='/library-dashboard')
api_bp.register_blueprint(defects_bp, url_prefix='/defects')
