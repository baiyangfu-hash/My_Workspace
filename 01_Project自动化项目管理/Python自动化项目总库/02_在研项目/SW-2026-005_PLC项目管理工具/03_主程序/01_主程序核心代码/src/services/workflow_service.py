# -*- coding: utf-8 -*-
"""
DJ单机项目工作流服务
"""
from __future__ import annotations

from typing import List

from src.core.constants import WORKFLOW_STAGE_DESC, WorkflowStage
from src.models.workflow_checkpoint import WorkflowCheckpoint
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class WorkflowService:
    """根据项目资产生成工作流检查点"""

    STAGE_REQUIREMENTS = {
        WorkflowStage.INITIATION.value: ["doc_req"],
        WorkflowStage.DESIGN.value: ["doc_arc", "doc_dsn"],
        WorkflowStage.DEVELOPMENT.value: ["plc_source", "plc_db"],
        WorkflowStage.COMMISSIONING.value: ["debug_doc"],
        WorkflowStage.TESTING.value: ["plc_test"],
        WorkflowStage.DELIVERY.value: ["doc_delivery"],
        WorkflowStage.MAINTENANCE.value: ["knowledge"],
    }

    @classmethod
    def build_checkpoints(cls, artifact_summary: dict) -> List[WorkflowCheckpoint]:
        """按资产统计构建检查点"""
        checkpoints: List[WorkflowCheckpoint] = []
        for stage, required_assets in cls.STAGE_REQUIREMENTS.items():
            missing = [
                asset_name
                for asset_name in required_assets
                if artifact_summary.get(asset_name, 0) <= 0
            ]
            checkpoints.append(
                WorkflowCheckpoint(
                    stage=stage,
                    label=WORKFLOW_STAGE_DESC[WorkflowStage(stage)],
                    passed=not missing,
                    required_assets=required_assets,
                    missing_assets=missing,
                    notes=[] if not missing else ["缺少必需资产"],
                )
            )
        logger.info(f"已生成 {len(checkpoints)} 个工作流检查点")
        return checkpoints
