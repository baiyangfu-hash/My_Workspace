# -*- coding: utf-8 -*-
"""
总库规范管理服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from pathlib import Path

from src.dao.library_dao import LibraryDAO
from src.dao.project_dao import ProjectDAO
from src.services.check_service import CheckService
from src.services.report_service import ReportService
from src.models.project import Project
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibrarySpecService:
    """总库规范管理服务类"""
    
    @staticmethod
    def check_library_specs(library_id: str, check_types: Optional[List[str]] = None) -> tuple[Dict, str]:
        """
        检查总库所有项目的规范符合性
        
        Returns:
            (检查结果, 错误信息