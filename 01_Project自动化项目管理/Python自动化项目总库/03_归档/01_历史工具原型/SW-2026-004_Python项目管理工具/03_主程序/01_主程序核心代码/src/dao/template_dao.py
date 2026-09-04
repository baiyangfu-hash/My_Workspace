# -*- coding: utf-8 -*-
"""
模板数据访问对象
"""
from typing import List, Optional

from .database import db
from src.models.template import Template
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TemplateDAO:
    """模板数据访问类"""
    
    @staticmethod
    def create(template: Template) -> Template:
        """创建新模板"""
        with db.get_session() as session:
            session.add(template)
            session.commit()
            session.refresh(template)
            return template
    
    @staticmethod
    def get_by_id(template_id: str) -> Optional[Template]:
        """根据模板ID查询"""
        with db.get_session() as session:
            return session.query(Template).filter(Template.template_id == template_id).first()
    
    @staticmethod
    def list(
        compiler: Optional[str] = None,
        scene: Optional[str] = None,
        is_builtin: Optional[bool] = None,
        is_active: bool = True,
        business_line: Optional[str] = None
    ) -> List[Template]:
        """查询模板列表"""
        with db.get_session() as session:
            query = session.query(Template).filter(Template.is_active == is_active)
            
            if compiler:
                query = query.filter(Template.compiler == compiler)
            
            if scene:
                query = query.filter(Template.scene == scene)
            
            if is_builtin is not None:
                query = query.filter(Template.is_builtin == is_builtin)
            
            if business_line:
                query = query.filter(Template.business_lines.contains([business_line]))
            
            return query.order_by(Template.is_builtin.desc(), Template.name).all()
    
    @staticmethod
    def update(template_id: str, data: dict) -> Optional[Template]:
        """更新模板信息"""
        with db.get_session() as session:
            template = session.query(Template).filter(Template.template_id == template_id).first()
            if not template:
                return None
            
            template.update_from_dict(data)
            session.commit()
            session.refresh(template)
            return template
    
    @staticmethod
    def delete(template_id: str) -> bool:
        """删除模板（软删除）"""
        with db.get_session() as session:
            template = session.query(Template).filter(Template.template_id == template_id).first()
            if not template or template.is_builtin:  # 内置模板不能删除
                return False
            
            template.is_active = False
            session.commit()
            return True
    
    @staticmethod
    def force_delete(template_id: str) -> bool:
        """强制删除模板（包括内置模板，用于系统管理操作）"""
        with db.get_session() as session:
            template = session.query(Template).filter(Template.template_id == template_id).first()
            if not template:
                return False
            
            session.delete(template)  # 硬删除，从数据库中完全移除
            session.commit()
            return True
    
    @staticmethod
    def exists(template_id: str) -> bool:
        """检查模板是否存在"""
        with db.get_session() as session:
            return session.query(Template).filter(Template.template_id == template_id).first() is not None
    
    @staticmethod
    def count() -> int:
        """统计模板总数"""
        with db.get_session() as session:
            return session.query(Template).filter(Template.is_active == True).count()

    @staticmethod
    def list_all() -> List[Template]:
        """查询所有模板（包括非活跃的）"""
        with db.get_session() as session:
            return session.query(Template).all()
