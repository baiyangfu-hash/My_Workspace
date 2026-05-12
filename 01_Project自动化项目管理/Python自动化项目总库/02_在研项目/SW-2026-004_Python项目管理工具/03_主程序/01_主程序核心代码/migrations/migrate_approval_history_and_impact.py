# -*- coding: utf-8 -*-
"""
变更管理模块数据库迁移脚本
创建审批历史表和影响评估表
"""
from sqlalchemy import text
from src.dao.database import db
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def migrate_approval_history():
    """创建审批历史表"""
    sql = """
    CREATE TABLE IF NOT EXISTS approval_histories (
        history_id VARCHAR(32) PRIMARY KEY COMMENT '历史记录ID',
        change_id VARCHAR(32) NOT NULL COMMENT '变更单ID',
        approver VARCHAR(50) NOT NULL COMMENT '审批人',
        action VARCHAR(20) NOT NULL COMMENT '审批动作: approve, reject',
        comment TEXT COMMENT '审批意见',
        approved_at DATETIME COMMENT '审批时间',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_change_id (change_id),
        INDEX idx_approved_at (approved_at),
        FOREIGN KEY (change_id) REFERENCES changes(change_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审批历史表';
    """
    
    try:
        with db.get_session() as session:
            session.execute(text(sql))
            session.commit()
            logger.info("审批历史表创建成功")
            return True
    except Exception as e:
        logger.exception(f"创建审批历史表失败: {e}")
        return False

def migrate_impact_assessment():
    """创建影响评估表"""
    sql = """
    CREATE TABLE IF NOT EXISTS impact_assessments (
        assessment_id VARCHAR(32) PRIMARY KEY COMMENT '评估ID',
        change_id VARCHAR(32) NOT NULL COMMENT '变更单ID',
        affected_components JSON COMMENT '受影响的组件',
        risk_level VARCHAR(20) DEFAULT 'LOW' COMMENT '风险等级: LOW, MEDIUM, HIGH',
        mitigation_plan TEXT COMMENT '缓解措施',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_change_id (change_id),
        INDEX idx_risk_level (risk_level),
        FOREIGN KEY (change_id) REFERENCES changes(change_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='影响评估表';
    """
    
    try:
        with db.get_session() as session:
            session.execute(text(sql))
            session.commit()
            logger.info("影响评估表创建成功")
            return True
    except Exception as e:
        logger.exception(f"创建影响评估表失败: {e}")
        return False

def migrate_all():
    """执行所有迁移"""
    logger.info("开始执行数据库迁移...")
    
    success_count = 0
    total_count = 2
    
    # 创建审批历史表
    if migrate_approval_history():
        success_count += 1
    else:
        logger.error("审批历史表迁移失败")
    
    # 创建影响评估表
    if migrate_impact_assessment():
        success_count += 1
    else:
        logger.error("影响评估表迁移失败")
    
    logger.info(f"数据库迁移完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        logger.info("所有迁移执行成功！")
        return True
    else:
        logger.error(f"部分迁移失败: {total_count - success_count} 个失败")
        return False

if __name__ == "__main__":
    print("开始执行数据库迁移...")
    if migrate_all():
        print("✓ 数据库迁移成功完成！")
        print("\n新增表:")
        print("  - approval_histories (审批历史表)")
        print("  - impact_assessments (影响评估表)")
    else:
        print("✗ 数据库迁移失败，请查看日志")
        exit(1)
