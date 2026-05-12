# -*- coding: utf-8 -*-
"""
规范数据访问层
"""
from typing import List, Optional

from sqlalchemy import or_

from .database import Database, db
from src.models.spec import Spec
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SpecDAO:
    """规范数据访问对象"""
    
    @staticmethod
    def create(spec: Spec) -> Spec:
        """创建规范"""
        session = db.get_session()
        try:
            session.add(spec)
            session.commit()
            session.refresh(spec)
            logger.info(f"规范创建成功: {spec.spec_id}")
            return spec
        except Exception as e:
            session.rollback()
            logger.exception(f"创建规范失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(spec_id: str) -> Optional[Spec]:
        """根据规范ID查询"""
        session = db.get_session()
        try:
            spec = session.query(Spec).filter(Spec.spec_id == spec_id).first()
            return spec
        finally:
            session.close()
    
    @staticmethod
    def get_by_pk(id: int) -> Optional[Spec]:
        """根据主键查询"""
        session = db.get_session()
        try:
            spec = session.query(Spec).filter(Spec.id == id).first()
            return spec
        finally:
            session.close()
    
    @staticmethod
    def list_all(category: Optional[str] = None, keyword: Optional[str] = None, 
                 is_active: Optional[bool] = None) -> List[Spec]:
        """查询规范列表"""
        session = db.get_session()
        try:
            query = session.query(Spec)
            
            if category:
                query = query.filter(Spec.category == category)
            
            if keyword:
                query = query.filter(
                    or_(
                        Spec.name.contains(keyword),
                        Spec.content.contains(keyword)
                    )
                )
            
            if is_active is not None:
                query = query.filter(Spec.is_active == is_active)
            
            specs = query.order_by(Spec.category, Spec.name).all()
            return specs
        finally:
            session.close()
    
    @staticmethod
    def list_categories() -> List[str]:
        """查询所有分类"""
        session = db.get_session()
        try:
            from sqlalchemy import distinct
            categories = session.query(distinct(Spec.category)).order_by(Spec.category).all()
            return [c[0] for c in categories]
        finally:
            session.close()
    
    @staticmethod
    def update(spec: Spec) -> Spec:
        """更新规范"""
        session = db.get_session()
        try:
            session.merge(spec)
            session.commit()
            logger.info(f"规范更新成功: {spec.spec_id}")
            return spec
        except Exception as e:
            session.rollback()
            logger.exception(f"更新规范失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete(spec_id: str) -> bool:
        """删除规范"""
        session = db.get_session()
        try:
            spec = session.query(Spec).filter(Spec.spec_id == spec_id).first()
            if spec:
                session.delete(spec)
                session.commit()
                logger.info(f"规范删除成功: {spec_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.exception(f"删除规范失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def count(category: Optional[str] = None) -> int:
        """统计规范数量"""
        session = db.get_session()
        try:
            query = session.query(Spec)
            if category:
                query = query.filter(Spec.category == category)
            return query.count()
        finally:
            session.close()
    
    @staticmethod
    def exists(spec_id: str) -> bool:
        """检查规范是否存在"""
        session = db.get_session()
        try:
            count = session.query(Spec).filter(Spec.spec_id == spec_id).count()
            return count > 0
        finally:
            session.close()
