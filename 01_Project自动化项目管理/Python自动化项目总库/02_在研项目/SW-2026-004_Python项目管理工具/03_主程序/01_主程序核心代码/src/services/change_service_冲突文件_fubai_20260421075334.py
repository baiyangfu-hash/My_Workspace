# -*- coding: utf-8 -*-
"""
变更管理服务
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from src.dao.change_dao import ChangeDAO
from src.models.change import Change
from src.core.constants import (
    ChangeStatus, Domain, Nature, Scope,
    DOMAIN_NAMES, NATURE_NAMES, SCOPE_NAMES,
    SCOPE_APPROVAL_MAP,
)
from src.services.impact_service import ImpactService
from src.services.notification_service import NotificationService
from src.services.change_analytics_service import ChangeAnalyticsService
from src.services.approval_service import ApprovalService
from src.services.project_service import ProjectService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChangeService:
    """变更管理服务类"""
    
    @staticmethod
    def create_change(
        project_id: str,
        title: str,
        type: str,
        description: str = "",
        reason: str = "",
        impact: str = "",
        proposer: str = "",
        attachment: list = None
    ) -> tuple[Optional[Change], str]:
        """创建变更单"""
        try:
            if not project_id:
                return None, "项目ID不能为空"
            
            if not title or not title.strip():
                return None, "变更标题不能为空"
            
            if not type:
                return None, "变更类型不能为空"
            
            # 生成变更单ID
            change_id = f"CHG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            change = Change(
                change_id=change_id,
                project_id=project_id,
                title=title.strip(),
                type=type,
                description=description,
                reason=reason,
                impact=impact,
                proposer=proposer,
                attachment=attachment or [],
                status=ChangeStatus.DRAFT
            )
            
            change = ChangeDAO.create(change)
            logger.info(f"变更单创建成功: {change_id} {title}")
            
            # 自动导出变更单文件
            ChangeService.export_change(change.change_id)
            
            return change, ""
            
        except Exception as e:
            logger.exception(f"创建变更单失败: {e}")
            return None, f"创建变更单失败: {str(e)}"
    
    @staticmethod
    def get_change(change_id: str) -> Optional[Change]:
        """获取变更单详情"""
        return ChangeDAO.get_by_id(change_id)
    
    @staticmethod
    def list_changes(
        project_id: str,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Change], int]:
        """查询项目变更单列表"""
        status_enum = ChangeStatus(status) if status else None
        return ChangeDAO.list_by_project(
            project_id=project_id,
            status=status_enum,
            page=page,
            size=size
        )
    
    @staticmethod
    def get_project_changes(project_id: str, **kwargs) -> List[Change]:
        """
        获取项目的变更列表 (兼容性方法)
        
        Args:
            project_id: 项目ID
            **kwargs: 可选过滤条件 (status, page, size)
            
        Returns:
            变更对象列表
        """
        changes, _ = ChangeService.list_changes(
            project_id=project_id,
            **kwargs
        )
        return changes
    
    @staticmethod
    def update_change(change_id: str, data: dict) -> tuple[Optional[Change], str]:
        """更新变更单信息"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return None, "变更单不存在"
            
            if change.status not in [ChangeStatus.DRAFT, ChangeStatus.PENDING]:
                return None, "仅草稿和待审批状态可以修改"
            
            # 不能修改的字段
            protected_fields = ["change_id", "project_id", "status", "approver", "created_at"]
            for field in protected_fields:
                if field in data:
                    del data[field]
            
            updated_change = ChangeDAO.update(change_id, data)
            logger.info(f"变更单更新成功: {change_id}")
            return updated_change, ""
            
        except Exception as e:
            logger.exception(f"更新变更单失败: {e}")
            return None, f"更新变更单失败: {str(e)}"
    
    @staticmethod
    def submit_change(change_id: str) -> tuple[bool, str]:
        """提交变更单审批"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status != ChangeStatus.DRAFT:
                return False, "仅草稿状态可以提交审批"
            
            # 执行影响分析
            impact_result = ImpactService.analyze_impact(change_id)
            if "error" not in impact_result:
                # 更新变更单的影响分析结果
                ChangeDAO.update(change_id, {"impact_analysis": str(impact_result)})
                logger.info(f"变更单影响分析完成: {change_id}")
            
            success = ChangeDAO.update_status(change_id, ChangeStatus.PENDING)
            if success:
                logger.info(f"变更单已提交审批: {change_id}")
                # 发送通知
                NotificationService.notify_change_status(change_id, ChangeStatus.PENDING.value)
            return success, "" if success else "提交失败"
            
        except Exception as e:
            logger.exception(f"提交变更单失败: {e}")
            return False, f"提交变更单失败: {str(e)}"
    
    @staticmethod
    def approve_change(change_id: str, approver: str) -> tuple[bool, str]:
        """审批通过变更单"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status != ChangeStatus.PENDING:
                return False, "仅待审批状态可以审批"
            
            # 记录审批历史
            ApprovalService.create_approval_history(
                change_id=change_id,
                approver=approver,
                action="approve",
                comment="审批通过"
            )
            
            success = ChangeDAO.update_status(change_id, ChangeStatus.APPROVED, approver)
            if success:
                logger.info(f"变更单已通过: {change_id}, 审批人: {approver}")
                # 发送通知
                NotificationService.notify_change_status(change_id, ChangeStatus.APPROVED.value)
            return success, "" if success else "审批失败"
            
        except Exception as e:
            logger.exception(f"审批变更单失败: {e}")
            return False, f"审批变更单失败: {str(e)}"
    
    @staticmethod
    def reject_change(change_id: str, approver: str, reason: str = "") -> tuple[bool, str]:
        """驳回变更单"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status != ChangeStatus.PENDING:
                return False, "仅待审批状态可以驳回"
            
            # 记录审批历史
            ApprovalService.create_approval_history(
                change_id=change_id,
                approver=approver,
                action="reject",
                comment=f"驳回原因: {reason}"
            )
            
            # 更新状态并添加驳回原因
            update_data = {
                "status": ChangeStatus.REJECTED,
                "approver": approver,
                "description": f"{change.description}\n\n驳回原因: {reason}"
            }
            
            updated = ChangeDAO.update(change_id, update_data) is not None
            if updated:
                logger.info(f"变更单已驳回: {change_id}, 审批人: {approver}")
                # 发送通知
                NotificationService.notify_change_status(change_id, ChangeStatus.REJECTED.value)
            return updated, "" if updated else "驳回失败"
            
        except Exception as e:
            logger.exception(f"驳回变更单失败: {e}")
            return False, f"驳回变更单失败: {str(e)}"
    
    @staticmethod
    def start_implement(change_id: str, implementer: str) -> tuple[bool, str]:
        """开始实施变更"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status != ChangeStatus.APPROVED:
                return False, "仅已批准状态可以开始实施"
            
            update_data = {
                "status": ChangeStatus.IMPLEMENTING,
                "implementer": implementer
            }
            
            updated = ChangeDAO.update(change_id, update_data) is not None
            if updated:
                logger.info(f"变更单开始实施: {change_id}, 实施人: {implementer}")
            return updated, "" if updated else "操作失败"
            
        except Exception as e:
            logger.exception(f"开始实施变更失败: {e}")
            return False, f"开始实施变更失败: {str(e)}"
    
    @staticmethod
    def complete_change(change_id: str) -> tuple[bool, str]:
        """完成变更实施"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status != ChangeStatus.IMPLEMENTING:
                return False, "仅实施中状态可以标记完成"
            
            success = ChangeDAO.update_status(change_id, ChangeStatus.COMPLETED)
            if success:
                logger.info(f"变更单已完成: {change_id}")
                # 发送通知
                NotificationService.notify_change_status(change_id, ChangeStatus.COMPLETED.value)
            return success, "" if success else "操作失败"
            
        except Exception as e:
            logger.exception(f"完成变更单失败: {e}")
            return False, f"完成变更单失败: {str(e)}"
    
    @staticmethod
    def cancel_change(change_id: str) -> tuple[bool, str]:
        """取消变更单"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更单不存在"
            
            if change.status in [ChangeStatus.COMPLETED, ChangeStatus.CANCELLED]:
                return False, "已完成或已取消的变更单不能取消"
            
            success = ChangeDAO.update_status(change_id, ChangeStatus.CANCELLED)
            if success:
                logger.info(f"变更单已取消: {change_id}")
            return success, "" if success else "操作失败"
            
        except Exception as e:
            logger.exception(f"取消变更单失败: {e}")
            return False, f"取消变更单失败: {str(e)}"
    
    @staticmethod
    def delete_change(change_id: str) -> tuple[bool, str]:
        """删除变更单"""
        try:
            success = ChangeDAO.delete(change_id)
            if not success:
                return False, "变更单不存在或不是草稿状态"
            
            logger.info(f"变更单已删除: {change_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除变更单失败: {e}")
            return False, f"删除变更单失败: {str(e)}"
    
    @staticmethod
    def get_statistics(project_id: str) -> dict:
        """V2.1.0: 获取项目变更统计 (4D: status + domain + nature + scope)"""
        try:
            dao_stats = ChangeDAO.get_statistics(project_id)

            return {
                "total": dao_stats["total"],

                # 按状态 (原有)
                **{s.value: dao_stats.get(s.value, 0) for s in ChangeStatus},

                # V2.1.0: 按领域 (新增)
                **{f"domain_{d.value}": dao_stats.get(f"domain_{d.value}", 0) for d in Domain},

                # V2.1.0: 按性质 (新增)
                **{f"nature_{n.value}": dao_stats.get(f"nature_{n.value}", 0) for n in Nature},

                # V2.1.0: 按范围 (新增)
                **{f"scope_{s.value}": dao_stats.get(f"scope_{s.value}", 0) for s in Scope},
            }
        except Exception as e:
            logger.exception(f"获取变更统计失败: {e}")
            return {}
    
    @staticmethod
    def export_change(change_id: str, format: str = "markdown", 
                     output_path: str = None) -> tuple[Optional[str], str]:
        """导出变更单"""
        try:
            change = ChangeDAO.get_by_id(change_id)
            if not change:
                return None, "变更单不存在"
            
            # 获取项目信息
            project = ProjectService.get_project(change.project_id)
            if not project:
                return None, "项目不存在"
            
            # 生成变更单内容
            content = ChangeService._generate_change_content(change, project)
            
            # 确定输出路径 (扁平结构: 04_变更管理/01_变更单/)
            if not output_path:
                # 获取该项目已有变更单数量，用于生成序号
                existing_changes, _ = ChangeDAO.list_by_project(change.project_id, page=1, size=1000)
                seq = len(existing_changes) + 1

                # 获取项目编码（fallback: project.name 或 "UNKNOWN"）
                project_code = getattr(project, 'code', None) or getattr(project, 'name', None) or 'UNKNOWN'

                # 生成标准格式的文件名
                filename = f"040_{project_code}_变更单 {seq:03d}_CHG-V2.0.0.md"

                # 扁平目录结构（不再有 CHG-{domain} 子目录）
                change_order_dir = os.path.join(
                    project.path,
                    "00_项目管理",
                    "04_变更管理",
                    "01_变更单"
                )
                os.makedirs(change_order_dir, exist_ok=True)

                output_path = os.path.join(change_order_dir, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"变更单导出成功: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"导出变更单失败: {e}")
            return None, f"导出失败: {str(e)}"
    
    @staticmethod
    def _generate_change_content(change: Change, project) -> str:
        """V2.1.0: 生成变更单内容 (符合 040_通用变更单模板_CHG-V2.0.0)"""
        from src.core.constants import ChangeStatus
        status_names = {
            ChangeStatus.DRAFT: "草稿", ChangeStatus.PENDING: "待审批",
            ChangeStatus.APPROVED: "已批准", ChangeStatus.REJECTED: "已拒绝",
            ChangeStatus.IMPLEMENTING: "实施中", ChangeStatus.COMPLETED: "已完成 ✅",
            ChangeStatus.CANCELLED: "已取消 🚫",
        }
        d = change.to_v2_dict()
        now = datetime.now().strftime('%Y-%m-%d')

        # §6.2 技术领域影响 (7行checklist)
        all_domains = [Domain.ELEC, Domain.MECH, Domain.PLC, Domain.HMI,
                        Domain.SCPT, Domain.DOCU, Domain.SAFE]
        domain_impact_rows = ""
        for dom in all_domains:
            is_affected = (dom == change.domain or
                           any(rc.startswith(f"CHG-{dom.value}") for rc in (change.related_changes or [])))
            mark = "☑是" if is_affected else "☐否"
            impact_note = "(自身)" if dom == change.domain else ""
            domain_impact_rows += f"| {dom.value} | {DOMAIN_NAMES[dom]} | {mark} | {impact_note} |\n"

        # §8 分级审批
        approval_section = ""
        if change.needs_reviewer():
            approval_section = f"""
### 8.1 初审
| 角色 | 审批人 | 审批结果 | 审批意见 | 审批日期 |
|------|--------|----------|----------|----------|
| 项目经理/负责人 | {d['approver'] or '待审批'} | {status_names.get(change.status, '待审')} | | {now} |

### 8.2 复审 ⚠️ ({d['approval_level']} 必需)
| 复审角色 | 复审人 | 复审结果 | 复审意见 | 复审日期 |
|----------|--------|----------|----------|----------|
| **{d['approval_level']}** | {d['reviewer'] or '待指定'} | ☐ 待复审 | | |

> **⚠️ 此变更为{d['scope_display']}级, 按V2.1.0规范必须由**{d['approval_level']}**复审后方可实施。**
"""
        else:
            approval_section = f"""
### 8.1 分级审批
| 审批角色 | 审批人 | 审批结果 | 审批意见 | 审批日期 |
|----------|--------|----------|----------|----------|
| **{d['approval_level']}** | {d['approver'] or '待审批'} | {status_names.get(change.status, '待审')} | | {now} |
"""

        return f"""# 变更单

## 1. 文档基础信息

**文档标题**：{d['domain_name']}变更单 - {d['title']}
**文档版本**：CHG-V2.0.0
**编制日期**：{now}
**编制人**：{d['proposer'] or '[编制人姓名]'}
**变更单编号**：{d['change_id']}
**关联原始记录**：FB-V2-xxx (如有)

## 3. 二维分类

### 3.1 技术领域 (WHO)
| 选项 | 领域名称 | 是否选中 |
|:----:|---------|:-------:|
| ELEC | 电气设计 | {'☑' if d['domain']=='ELEC' else '☐'} |
| MECH | 机械结构 | {'☑' if d['domain']=='MECH' else '☐'} |
| PLC | PLC程序 | {'☑' if d['domain']=='PLC' else '☐'} |
| HMI | HMI程序 | {'☑' if d['domain']=='HMI' else '☐'} |
| SCPT | Python脚本 | {'☑' if d['domain']=='SCPT' else '☐'} |
| DOCU | 工程文档 | {'☑' if d['domain']=='DOCU' else '☐'} |
| SAFE | 安全功能 | {'☑' if d['domain']=='SAFE' else '☐'} |

### 3.2 业务性质 (WHY)
| 选项 | 性质名称 | 是否选中 |
|:----:|---------|:-------:|
| REQ | 需求变更 | {'☑' if d['nature']=='REQ' else '☐'} |
| DEF | 缺陷修复 | {'☑' if d['nature']=='DEF' else '☐'} |
| OPT | 优化改进 | {'☑' if d['nature']=='OPT' else '☐'} |
| CFG | 配置调整 | {'☑' if d['nature']=='CFG' else '☐'} |
| EMRG | 紧急变更 | {'☑' if d['nature']=='EMRG' else '☐'} |

### 3.3 影响范围 (WHERE)
| 范围 | 名称 | 是否选中 | 说明 |
|:----:|-----|:-------:|------|
| LOCAL | 局部 | {'☑' if d['scope']=='LOCAL' else '☐'} | 单个POU/画面/IO点 |
| MODULE | 模块级 | {'☑' if d['scope']=='MODULE' else '☐'} | 单设备/单线/子系统 |
| SYSTEM | 系统级 | {'☑' if d['scope']=='SYSTEM' else '☐'} | 多模块联动/联锁/通讯 |
| CROSS | 跨系统 | {'☑' if d['scope']=='CROSS' else '☐'} | 多子系统(PLC+HMI+电气...) |
| SAFE | 安全相关 | {'☑' if d['scope']=='SAFE' else '☐'} | 急停/SIL/安全功能 |

## 4. 变更原因

### 4.1 变更背景
{d['reason'] or '(无)'}

### 4.2 变更必要性
{(d['description'] or '见§5变更前后对比')}

### 4.3 变更依据
- 项目需求 / 现场调试发现 / 技术优化决策

## 5. 变更内容

### 5.1 变更前 (Before)
```
{d['content_before'] or '(无详细记录)'}
```

### 5.2 变更后 (After)
```
{d['content_after'] or '(无详细记录)'}
```

## 6. 三维影响评估

### 6.1 项目约束影响
| 维度 | 影响等级 | 说明 |
|:----:|:-------:|------|
| Scope(范围) | 中等 | 见§3.3范围定义 |
| Schedule(进度) | 低 | 预计{d['priority']}级优先级处理 |
| Cost(成本) | 无 | 无额外成本 |
| Quality(质量) | 正面 | 提升/修复质量 |
| Risk(风险) | 低 | 已评估风险可控 |

### 6.2 技术领域影响
| 领域代码 | 领域名称 | 是否受影响 | 影响说明 |
|:--------:|---------|:----------:|---------|
{domain_impact_rows}

### 6.3 变更传播链
{(f"```{d['propagation_chain']}```" if d['propagation_chain'] else '> 无传播链 (LOCAL/MODULE级无需填写)')}
{f"\n**关联变更单**: {', '.join(d['related_changes']) if d['related_changes'] > 0 else '无'}" if d['related_changes'] else ''}

## 7. 实施计划

| 序号 | 任务 | 负责人 | 计划日期 | 状态 |
|:----:|------|:------:|:-------:|:----:|
| 1 | 准备工作(备份/环境确认) | {d['implementer'] or 'TBD'} | {now} | ☐ |
| 2 | 执行变更 | {d['implementer'] or 'TBD'} | | ☐ |
| 3 | 验证结果 | {d['implementer'] or 'TBD'} | | ☐ |

{approval_section}

## 9. 实施记录

| 实施日期 | 实施人 | 任务 | 结果 | 备注 |
|:-------:|:------:|:----:|:----:|:----:|
| {(f"{d['implemented_at'][:10] if d.get('implemented_at') else now} | {d['implementer'] or '-'} | 执行变更 | {status_names.get(change.status, '进行中')} | -") if change.status in [ChangeStatus.IMPLEMENTING, ChangeStatus.COMPLETED] else '| (暂无记录) |'}

## 10. 验证结论

### 10.1 验证清单
- [ ] 变更已按批准内容实施
- [ ] 变更达到预期效果
- [ ] 未引入新的问题/回归缺陷
- [ ] 相关文档已同步更新
{(f"- [ ] 关联变更单验证: {', '.join(d['related_changes'])}" if d['related_changes'] else '')}

### 10.2 最终结论
**验证状态**: {status_names.get(change.status, '待验证')}
**验证人**: 系统
**验证日期**: {now}

---

**文档版本**: CHG-V2.0.0
**编制日期**: {now}
**编制人**: {d['proposer'] or '[编制人姓名]'}
**审核人**: {d['reviewer'] or '[审核人姓名]'}"""
    
    @staticmethod
    def generate_ledger(project_id: str, output_path: str = None) -> tuple[Optional[str], str]:
        """生成变更台帐"""
        try:
            # 获取项目信息
            project = ProjectService.get_project(project_id)
            if not project:
                return None, "项目不存在"
            
            # 获取项目所有变更
            changes, total = ChangeDAO.list_by_project(project_id, page=1, size=1000)
            
            # 生成台帐内容
            content = ChangeService._generate_ledger_content(project, changes)
            
            # 确定输出路径 (V2.1.0: 04_变更管理/04_变更记录/041_{code}_版本变更台帐_CHG-V2.1.0.md)
            if not output_path:
                output_path = os.path.join(
                    project.path,
                    "00_项目管理", "04_变更管理", "04_变更记录",
                    f"041_{project.code}_版本变更台帐_CHG-V2.1.0.md"
                )
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"变更台帐生成成功: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成变更台帐失败: {e}")
            return None, f"生成失败: {str(e)}"
    
    @staticmethod
    def _generate_ledger_content(project, changes: List[Change]) -> str:
        """V2.1.0: 生成变更台帐内容 (符合 041_通用版本变更台帐模板_CHG-V2.1.0 引用模式)"""
        from src.core.constants import ChangeStatus, Domain, Nature, Scope
        status_icons = {
            ChangeStatus.DRAFT: "📝", ChangeStatus.PENDING: "⏳",
            ChangeStatus.APPROVED: "✅", ChangeStatus.REJECTED: "❌",
            ChangeStatus.IMPLEMENTING: "🔄", ChangeStatus.COMPLETED: "✅",
            ChangeStatus.CANCELLED: "🚫",
        }
        now = datetime.now().strftime('%Y-%m-%d')

        # ===== §3: 4D统计 (domain × nature × scope × status) =====
        domain_nature_matrix = ""
        for nature in Nature:
            row = f"| {NATURE_NAMES[nature]} |"
            domain_total = 0
            for dom in Domain:
                count = sum(1 for c in changes if c.domain == dom and c.nature == nature)
                domain_total += count
                row += f" {count} |"
            row += f" {domain_total} |\n"
            domain_nature_matrix += row

        # 合计行
        total_row = "| **合计** |"
        grand_total = 0
        for dom in Domain:
            dom_count = sum(1 for c in changes if c.domain == dom)
            total_row += f" **{dom_count}** |"
            grand_total += dom_count
        total_row += f" **{grand_total}** |\n"

        # 按scope统计
        scope_stats = ""
        for scope in Scope:
            count = sum(1 for c in changes if c.scope == scope)
            scope_stats += f"- {SCOPE_NAMES[scope]}: {count}\n"

        # 按status统计
        status_stats = ""
        for status in ChangeStatus:
            count = sum(1 for c in changes if c.status == status)
            status_stats += f"- {status.value}: {count} {status_icons.get(status, '')}\n"

        # ===== §4: 变更记录表格 (引用模式 - 每行=摘要+超链接) =====
        change_records = ""
        # 获取项目编码用于生成标准文件名
        project_code = getattr(project, 'code', None) or getattr(project, 'name', None) or 'UNKNOWN'

        for i, change in enumerate(changes, 1):
            # 扁平结构: 040_{project_code}_变更单 {seq:03d}_CHG-V2.0.0.md
            seq = i
            filename = f"040_{project_code}_变更单 {seq:03d}_CHG-V2.0.0.md"
            link = f"[→ 查看详情](../01_变更单/{filename})"
            domain_name = DOMAIN_NAMES.get(change.domain, str(change.domain)) if hasattr(change, 'domain') else '-'
            nature_name = NATURE_NAMES.get(change.nature, str(change.nature)) if hasattr(change, 'nature') else '-'
            scope_display = change.get_scope_display() if hasattr(change, 'get_scope_display') else (SCOPE_NAMES.get(change.scope, '-') if hasattr(change, 'scope') else '-')
            priority = change.priority or 'P2'
            status_icon = status_icons.get(change.status, '')
            status_text = f"{status_icon} {change.status.value}"
            proposer = change.proposer or '-'
            date_str = change.created_at.strftime('%Y-%m-%d') if change.created_at else '-'

            change_records += f"| {i} | {link} | {domain_name} | {nature_name} | {scope_display} | {change.title} | {priority} | {status_text} | {proposer} | {date_str} |\n"

        # ===== §5: 传播链矩阵 (仅当存在SYSTEM/CROSS/SAFE级变更时显示) =====
        has_high_scope = any(
            hasattr(c, 'scope') and c.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]
            for c in changes
        )
        propagation_section = ""
        if has_high_scope:
            propagation_rows = ""
            for change in changes:
                if hasattr(change, 'scope') and change.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]:
                    if change.related_changes:
                        for related_id in (change.related_changes or []):
                            propagation_rows += f"| {change.change_id} | → | {related_id} | 自动关联 |\n"
                    elif hasattr(change, 'propagation_chain') and change.propagation_chain:
                        propagation_rows += f"| {change.change_id} | → | *(见传播链)* | {change.propagation_chain[:50]}... |\n"

            if propagation_rows:
                propagation_section = f"""
## 5. 变更传播链矩阵

> ⚠️ 检测到{sum(1 for c in changes if hasattr(c, 'scope') and c.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE])}个SYSTEM/CROSS/SAFE级别变更，以下为跨域影响追踪

| 原始变更 | 影响方向 | 受影响变更 | 影响说明 |
|:--------:|:-------:|:----------:|:---------|
{propagation_rows}
"""
            else:
                propagation_section = """
## 5. 变更传播链矩阵

> ⚠️ 检测到SYSTEM/CROSS/SAFE级别变更，但尚未填写传播链信息

| 原始变更 | 影响方向 | 受影响变更 | 影响说明 |
|:--------:|:-------:|:----------:|:---------|
| *(待补充)* | | | |
"""

        return f"""# {project.name} 版本变更台帐

## 1. 文档基础信息

**文档标题**：{project.name} 项目版本变更台帐
**文档版本**：CHG-V2.1.0 (引用模式)
**编制日期**：{now}
**编制人**：系统自动生成
**项目编号**：{project.code}

---

## 2. 台帐说明

本台帐采用**V2.1.0引用模式**：
- 每条变更记录仅包含**摘要信息 + 超链接**
- 详细内容请点击 `[→ CHG-xxx]` 链接查看对应的独立变更单文件
- 变更单位于 `./01_变更单/` 目录下按序号存放（扁平结构）

---

## 3. 多维统计分析

### 3.1 领域×性质分布矩阵

| 性质\\领域 | ELEC | MECH | PLC | HMI | SCPT | DOCU | SAFE | **合计** |
|:-----------|:----:|:----:|:---:|:---:|:----:|:----:|:----:|:--------:|
{domain_nature_matrix}{total_row}

### 3.2 按影响范围统计

{scope_stats}
### 3.3 按状态统计

{status_stats}
**总计**: {len(changes)} 条变更记录

---

## 4. 变更记录清单

| 序号 | → 变更单 | 领域 | 性质 | 范围 | 标题 | 优先级 | 状态 | 提出人 | 日期 |
|:----:|:--------|:----:|:----:|:----:|:-----|:------:|:----:|:------:|:----:|
{change_records}

{propagation_section}
---

## 6. 相关规范引用

| 规范文件 | 版本 | 用途 |
|----------|:----:|:-----|
| [043_通用变更管理目录结构说明](../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/03_变更管理规范/043_通用变更管理目录结构说明_PM-V2.1.0.md) | V2.1.0 | 目录结构与职责定义 |
| [040_通用变更单模板](../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/02_变更单模板/040_通用变更单模板_CHG-V2.0.0.md) | V2.0.0 | 变更单模板格式 |
| [042_通用变更管理流程规范](../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/03_变更管理规范/042_通用变更管理流程规范_PM-V2.0.0.md) | V2.0.0 | 流程与审批规范 |

---

**文档版本**: CHG-V2.1.0
**编制日期**: {now}
**编制人**: 系统自动生成 (SW-2026-004 Python项目管理工具)
**数据来源**: 项目数据库实时导出
"""
    
    @staticmethod
    def update_ledger(project_id: str) -> tuple[Optional[str], str]:
        """更新变更台帐"""
        return ChangeService.generate_ledger(project_id)

    @staticmethod
    def check_propagation_required(change: Change) -> bool:
        """V2.1.0: 检查是否需要填写传播链 (SYSTEM/CROSS/SAFE级必须)"""
        return change.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

    @staticmethod
    def suggest_related_domains(change: Change) -> List[Domain]:
        """V2.1.0: 根据当前domain和scope建议可能受影响的关联领域

        规则示例:
        - PLC + SYSTEM → 可能影响 [HMI, DOCU, SAFE]
        - ELEC + MODULE → 可能影响 [PLC, DOCU]
        - HMI + CROSS → 可能影响 [PLC, SCPT, DOCU]
        """
        PROPAGATION_RULES = {
            (Domain.PLC, Scope.SYSTEM): [Domain.HMI, Domain.DOCU, Domain.SAFE],
            (Domain.PLC, Scope.CROSS): [Domain.ELEC, Domain.MECH, Domain.HMI, Domain.SCPT, Domain.DOCU],
            (Domain.ELEC, Scope.MODULE): [Domain.PLC, Domain.DOCU],
            (Domain.ELEC, Scope.SYSTEM): [Domain.PLC, Domain.SAFE, Domain.DOCU],
            (Domain.MECH, Scope.MODULE): [Domain.ELEC, Domain.DOCU],
            (Domain.HMI, Scope.SYSTEM): [Domain.PLC, Domain.SCPT, Domain.DOCU],
            (Domain.HMI, Scope.CROSS): [Domain.PLC, Domain.SCPT, Domain.DOCU],
            (Domain.SCPT, Scope.SYSTEM): [Domain.DOCU, Domain.HMI],
            (Domain.SCPT, Scope.CROSS): [Domain.PLC, Domain.HMI, Domain.DOCU],
            (Domain.SAFE, Scope.LOCAL): [Domain.PLC, Domain.ELEC],
            (Domain.SAFE, Scope.MODULE): [Domain.PLC, Domain.ELEC, Domain.DOCU],
        }
        return PROPAGATION_RULES.get((change.domain, change.scope), [])
    
    @staticmethod
    def get_changes() -> List[Change]:
        """获取所有变更单（测试用）"""
        try:
            from src.dao.change_dao import ChangeDAO
            changes, _ = ChangeDAO.list_by_project("", page=1, size=100)
            return changes
        except Exception as e:
            logger.exception(f"获取变更单失败: {e}")
            return []
