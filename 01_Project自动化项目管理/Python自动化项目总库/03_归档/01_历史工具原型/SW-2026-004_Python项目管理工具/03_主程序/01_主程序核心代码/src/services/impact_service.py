# -*- coding: utf-8 -*-
"""
影响分析服务
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.dao.change_dao import ChangeDAO
from src.models.impact import ImpactAssessment
from src.core.constants import ImpactLevel, ChangeType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ImpactService:
    """影响分析服务"""
    
    @staticmethod
    def analyze_impact(change_id: str) -> Dict:
        """分析变更影响"""
        try:
            # 1. 获取变更信息
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return {"error": "变更单不存在"}
            
            # 2. 分析影响范围
            affected_components = ImpactService._analyze_affected_components(change.type, change.description)
            
            # 3. 评估风险等级
            risk_level = ImpactService._assess_risk_level(change.type, affected_components)
            
            # 4. 生成缓解措施
            mitigation_plan = ImpactService._generate_mitigation_plan(risk_level, affected_components)
            
            # 5. 保存影响评估结果
            assessment_id = f"IMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            assessment = ImpactAssessment(
                assessment_id=assessment_id,
                change_id=change_id,
                affected_components=affected_components,
                risk_level=risk_level,
                mitigation_plan=mitigation_plan
            )
            
            # 这里需要实现保存逻辑，暂时返回结果
            
            return {
                "assessment_id": assessment_id,
                "change_id": change_id,
                "affected_components": affected_components,
                "risk_level": risk_level.value,
                "mitigation_plan": mitigation_plan,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"分析变更影响失败: {e}")
            return {"error": f"分析变更影响失败: {str(e)}"}
    
    @staticmethod
    def _analyze_affected_components(change_type: str, description: str) -> List[Dict]:
        """分析受影响的组件"""
        components = []
        
        # 根据变更类型分析影响范围
        if change_type == ChangeType.CODE.value:
            components.append({"type": "code", "description": "源代码"})
            components.append({"type": "tests", "description": "测试代码"})
            if "API" in description or "接口" in description:
                components.append({"type": "api", "description": "API接口"})
        elif change_type == ChangeType.CONFIG.value:
            components.append({"type": "config", "description": "配置文件"})
            components.append({"type": "deployment", "description": "部署配置"})
        elif change_type == ChangeType.DEPENDENCY.value:
            components.append({"type": "dependencies", "description": "依赖包"})
            components.append({"type": "build", "description": "构建过程"})
        elif change_type == ChangeType.DOCUMENT.value:
            components.append({"type": "documents", "description": "文档"})
        elif change_type == ChangeType.STRUCTURE.value:
            components.append({"type": "structure", "description": "项目结构"})
            components.append({"type": "build", "description": "构建配置"})
        elif change_type == ChangeType.TEMPLATE.value:
            components.append({"type": "templates", "description": "模板文件"})
            components.append({"type": "projects", "description": "使用该模板的项目"})
        elif change_type == ChangeType.PLUGIN.value:
            components.append({"type": "plugins", "description": "插件系统"})
            components.append({"type": "projects", "description": "使用该插件的项目"})
        
        return components
    
    @staticmethod
    def _assess_risk_level(change_type: str, affected_components: List[Dict]) -> ImpactLevel:
        """评估风险等级"""
        # 基于变更类型和受影响组件数量评估风险
        component_count = len(affected_components)
        
        if change_type in [ChangeType.CODE.value, ChangeType.DEPENDENCY.value, ChangeType.STRUCTURE.value]:
            if component_count >= 3:
                return ImpactLevel.HIGH
            elif component_count >= 2:
                return ImpactLevel.MEDIUM
            else:
                return ImpactLevel.LOW
        elif change_type in [ChangeType.CONFIG.value, ChangeType.PLUGIN.value, ChangeType.TEMPLATE.value]:
            if component_count >= 2:
                return ImpactLevel.MEDIUM
            else:
                return ImpactLevel.LOW
        else:
            return ImpactLevel.LOW
    
    @staticmethod
    def _generate_mitigation_plan(risk_level: ImpactLevel, affected_components: List[Dict]) -> str:
        """生成缓解措施"""
        plan = []
        
        if risk_level == ImpactLevel.HIGH:
            plan.append("1. 进行全面的回归测试")
            plan.append("2. 制定详细的回滚计划")
            plan.append("3. 安排专人监控变更后的系统状态")
            plan.append("4. 提前通知相关团队和用户")
        elif risk_level == ImpactLevel.MEDIUM:
            plan.append("1. 进行相关模块的测试")
            plan.append("2. 准备回滚方案")
            plan.append("3. 通知相关团队")
        else:
            plan.append("1. 进行常规测试")
            plan.append("2. 记录变更内容")
        
        # 根据受影响组件添加特定措施
        for component in affected_components:
            if component["type"] == "api":
                plan.append("3. 验证API接口兼容性")
            elif component["type"] == "dependencies":
                plan.append("3. 检查依赖包版本兼容性")
            elif component["type"] == "plugins":
                plan.append("3. 验证插件功能完整性")
        
        return "\n".join(plan)
