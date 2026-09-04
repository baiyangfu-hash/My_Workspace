# -*- coding: utf-8 -*-
"""
项目进度管理服务
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from src.models.milestone import Milestone
from src.models.task import Task
from src.dao.milestone_dao import MilestoneDAO
from src.dao.task_dao import TaskDAO
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

MILESTONE_STATUS_NAMES = {
    "pending": "待开始",
    "in_progress": "进行中",
    "completed": "已完成",
    "delayed": "已延期"
}

TASK_STATUS_NAMES = {
    "pending": "待开始",
    "in_progress": "进行中",
    "completed": "已完成",
    "delayed": "已延期"
}

PRIORITY_NAMES = {
    "high": "高",
    "medium": "中",
    "low": "低"
}

class ProgressService:
    """项目进度管理服务"""
    
    @staticmethod
    def create_milestone(
        project_id: str,
        name: str,
        description: str = "",
        start_date: date = None,
        end_date: date = None,
        sequence: int = 0
    ) -> tuple[Optional[Milestone], str]:
        """创建里程碑"""
        try:
            if not name or not name.strip():
                return None, "里程碑名称不能为空"
            
            milestone_id = f"MS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            
            milestone = Milestone(
                milestone_id=milestone_id,
                project_id=project_id,
                name=name.strip(),
                description=description,
                start_date=start_date,
                end_date=end_date,
                status="pending",
                progress=0,
                sequence=sequence
            )
            
            created = MilestoneDAO.create(milestone)
            logger.info(f"里程碑创建成功: {milestone_id} {name}")
            return created, ""
            
        except Exception as e:
            logger.exception(f"创建里程碑失败: {e}")
            return None, f"创建里程碑失败: {str(e)}"
    
    @staticmethod
    def get_milestone(milestone_id: str) -> Optional[Milestone]:
        """获取里程碑详情"""
        return MilestoneDAO.get_by_id(milestone_id)
    
    @staticmethod
    def list_milestones(project_id: str) -> List[Milestone]:
        """查询项目里程碑列表"""
        return MilestoneDAO.list_by_project(project_id)
    
    @staticmethod
    def update_milestone(milestone_id: str, data: dict) -> tuple[Optional[Milestone], str]:
        """更新里程碑"""
        try:
            milestone = MilestoneDAO.get_by_id(milestone_id)
            if not milestone:
                return None, "里程碑不存在"
            
            if "name" in data:
                milestone.name = data["name"]
            if "description" in data:
                milestone.description = data["description"]
            if "start_date" in data:
                milestone.start_date = data["start_date"]
            if "end_date" in data:
                milestone.end_date = data["end_date"]
            if "status" in data:
                milestone.status = data["status"]
            if "progress" in data:
                milestone.progress = data["progress"]
            if "sequence" in data:
                milestone.sequence = data["sequence"]
            
            updated = MilestoneDAO.update(milestone)
            logger.info(f"里程碑更新成功: {milestone_id}")
            return updated, ""
            
        except Exception as e:
            logger.exception(f"更新里程碑失败: {e}")
            return None, f"更新里程碑失败: {str(e)}"
    
    @staticmethod
    def delete_milestone(milestone_id: str) -> tuple[bool, str]:
        """删除里程碑"""
        try:
            tasks = TaskDAO.list_by_milestone(milestone_id)
            for task in tasks:
                TaskDAO.delete(task.task_id)
            
            success = MilestoneDAO.delete(milestone_id)
            if success:
                logger.info(f"里程碑删除成功: {milestone_id}")
            return success, "" if success else "里程碑不存在"
            
        except Exception as e:
            logger.exception(f"删除里程碑失败: {e}")
            return False, f"删除里程碑失败: {str(e)}"
    
    @staticmethod
    def create_task(
        project_id: str,
        name: str,
        milestone_id: str = None,
        parent_id: str = None,
        description: str = "",
        assignee: str = "",
        start_date: date = None,
        end_date: date = None,
        priority: str = "medium",
        sequence: int = 0
    ) -> tuple[Optional[Task], str]:
        """创建任务"""
        try:
            if not name or not name.strip():
                return None, "任务名称不能为空"
            
            task_id = f"TSK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            
            task = Task(
                task_id=task_id,
                project_id=project_id,
                milestone_id=milestone_id,
                parent_id=parent_id,
                name=name.strip(),
                description=description,
                assignee=assignee,
                start_date=start_date,
                end_date=end_date,
                status="pending",
                progress=0,
                priority=priority,
                sequence=sequence
            )
            
            created = TaskDAO.create(task)
            logger.info(f"任务创建成功: {task_id} {name}")
            return created, ""
            
        except Exception as e:
            logger.exception(f"创建任务失败: {e}")
            return None, f"创建任务失败: {str(e)}"
    
    @staticmethod
    def get_task(task_id: str) -> Optional[Task]:
        """获取任务详情"""
        return TaskDAO.get_by_id(task_id)
    
    @staticmethod
    def list_tasks(project_id: str, milestone_id: str = None) -> List[Task]:
        """查询任务列表"""
        if milestone_id:
            return TaskDAO.list_by_milestone(milestone_id)
        return TaskDAO.list_by_project(project_id)
    
    @staticmethod
    def update_task(task_id: str, data: dict) -> tuple[Optional[Task], str]:
        """更新任务"""
        try:
            task = TaskDAO.get_by_id(task_id)
            if not task:
                return None, "任务不存在"
            
            if "name" in data:
                task.name = data["name"]
            if "description" in data:
                task.description = data["description"]
            if "assignee" in data:
                task.assignee = data["assignee"]
            if "start_date" in data:
                task.start_date = data["start_date"]
            if "end_date" in data:
                task.end_date = data["end_date"]
            if "status" in data:
                task.status = data["status"]
            if "progress" in data:
                task.progress = data["progress"]
            if "priority" in data:
                task.priority = data["priority"]
            if "sequence" in data:
                task.sequence = data["sequence"]
            
            updated = TaskDAO.update(task)
            
            if task.milestone_id:
                ProgressService._update_milestone_progress(task.milestone_id)
            
            logger.info(f"任务更新成功: {task_id}")
            return updated, ""
            
        except Exception as e:
            logger.exception(f"更新任务失败: {e}")
            return None, f"更新任务失败: {str(e)}"
    
    @staticmethod
    def delete_task(task_id: str) -> tuple[bool, str]:
        """删除任务"""
        try:
            task = TaskDAO.get_by_id(task_id)
            if not task:
                return False, "任务不存在"
            
            milestone_id = task.milestone_id
            
            success = TaskDAO.delete(task_id)
            
            if success and milestone_id:
                ProgressService._update_milestone_progress(milestone_id)
            
            logger.info(f"任务删除成功: {task_id}")
            return success, ""
            
        except Exception as e:
            logger.exception(f"删除任务失败: {e}")
            return False, f"删除任务失败: {str(e)}"
    
    @staticmethod
    def _update_milestone_progress(milestone_id: str):
        """更新里程碑进度"""
        tasks = TaskDAO.list_by_milestone(milestone_id)
        if tasks:
            total_progress = sum(t.progress for t in tasks)
            avg_progress = total_progress // len(tasks)
            
            milestone = MilestoneDAO.get_by_id(milestone_id)
            if milestone:
                milestone.progress = avg_progress
                
                all_completed = all(t.status == "completed" for t in tasks)
                any_in_progress = any(t.status == "in_progress" for t in tasks)
                
                if all_completed:
                    milestone.status = "completed"
                elif any_in_progress:
                    milestone.status = "in_progress"
                
                MilestoneDAO.update(milestone)
    
    @staticmethod
    def get_gantt_data(project_id: str) -> Dict[str, Any]:
        """获取甘特图数据"""
        milestones = ProgressService.list_milestones(project_id)
        
        gantt_data = {
            "milestones": [],
            "tasks": []
        }
        
        for ms in milestones:
            ms_data = {
                "id": ms.milestone_id,
                "name": ms.name,
                "start_date": ms.start_date.isoformat() if ms.start_date else None,
                "end_date": ms.end_date.isoformat() if ms.end_date else None,
                "status": ms.status,
                "status_name": MILESTONE_STATUS_NAMES.get(ms.status, ms.status),
                "progress": ms.progress
            }
            gantt_data["milestones"].append(ms_data)
            
            tasks = TaskDAO.list_by_milestone(ms.milestone_id)
            for task in tasks:
                task_data = {
                    "id": task.task_id,
                    "milestone_id": ms.milestone_id,
                    "name": task.name,
                    "start_date": task.start_date.isoformat() if task.start_date else None,
                    "end_date": task.end_date.isoformat() if task.end_date else None,
                    "status": task.status,
                    "status_name": TASK_STATUS_NAMES.get(task.status, task.status),
                    "progress": task.progress,
                    "assignee": task.assignee,
                    "priority": task.priority,
                    "priority_name": PRIORITY_NAMES.get(task.priority, task.priority)
                }
                gantt_data["tasks"].append(task_data)
        
        return gantt_data
    
    @staticmethod
    def get_statistics(project_id: str) -> Dict[str, Any]:
        """获取项目进度统计"""
        milestones = ProgressService.list_milestones(project_id)
        tasks = TaskDAO.list_by_project(project_id)
        
        ms_stats = {
            "total": len(milestones),
            "pending": sum(1 for m in milestones if m.status == "pending"),
            "in_progress": sum(1 for m in milestones if m.status == "in_progress"),
            "completed": sum(1 for m in milestones if m.status == "completed"),
            "delayed": sum(1 for m in milestones if m.status == "delayed")
        }
        
        task_stats = {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.status == "pending"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "delayed": sum(1 for t in tasks if t.status == "delayed")
        }
        
        total_progress = sum(t.progress for t in tasks) if tasks else 0
        avg_progress = total_progress // len(tasks) if tasks else 0
        
        return {
            "milestones": ms_stats,
            "tasks": task_stats,
            "overall_progress": avg_progress
        }
