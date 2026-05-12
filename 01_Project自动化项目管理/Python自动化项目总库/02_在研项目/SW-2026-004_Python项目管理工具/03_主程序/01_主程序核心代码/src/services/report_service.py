# -*- coding: utf-8 -*-
"""
报告生成服务
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from src.models.project import Project
from .check_service import CheckResult
from src.utils.file_utils import write_file, write_json
from src.utils.logger import setup_logger
from src.core.constants import BUSINESS_LINE_DESC

logger = setup_logger(__name__)

class ReportService:
    """报告生成服务类"""
    
    @staticmethod
    def generate_check_report(project: Project, check_result: CheckResult, output_path: str = None) -> tuple[Optional[str], str]:
        """生成规范检查报告"""
        try:
            report_data = {
                "report_id": f"RPT-CHECK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "report_type": "规范检查报告",
                "generated_at": datetime.now().isoformat(),
                "project_info": {
                    "id": project.project_id,
                    "code": project.code,
                    "name": project.name,
                    "manager": project.manager
                },
                "result": check_result.to_dict()
            }
            
            # 确定输出路径
            if not output_path:
                report_dir = Path(project.path) / "06_测试相关" / "02_测试报告"
                report_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(report_dir / f"规范检查报告_{datetime.now().strftime('%Y%m%d')}.json")
            
            # 保存JSON报告
            write_json(output_path, report_data)
            
            # 生成Markdown报告
            md_content = ReportService._check_report_to_markdown(report_data)
            md_path = Path(output_path).with_suffix(".md")
            write_file(md_path, md_content)
            
            logger.info(f"检查报告已生成: {output_path}")
            return str(md_path), ""
            
        except Exception as e:
            logger.exception(f"生成检查报告失败: {e}")
            return None, f"生成检查报告失败: {str(e)}"
    
    @staticmethod
    def _check_report_to_markdown(data: Dict) -> str:
        """将检查报告转换为Markdown格式"""
        summary = data["result"]["summary"]
        
        md = f"""# {data["report_type"]}

## 基本信息
- 报告ID: {data["report_id"]}
- 生成时间: {data["generated_at"]}
- 项目编号: {data["project_info"]["code"]}
- 项目名称: {data["project_info"]["name"]}
- 项目负责人: {data["project_info"]["manager"] or "-"}

## 检查概览
| 指标 | 数量 |
|------|------|
| 总检查项 | {summary["total"]} |
| 通过 | {summary["passed"]} |
| 警告 | {summary["warnings"]} |
| 错误 | {summary["errors"]} |
| 通过率 | {summary["pass_rate"]}% |

## 检查详情
"""
        
        # 按级别分组显示
        for level in ["error", "warning", "pass"]:
            items = [item for item in data["result"]["items"] if item["level"] == level]
            if not items:
                continue
            
            level_name = {"error": "❌ 错误", "warning": "⚠️ 警告", "pass": "✅ 通过"}[level]
            md += f"\n### {level_name} ({len(items)}项)\n\n"
            
            for i, item in enumerate(items, 1):
                md += f"{i}. **{item['rule']}**\n"
                md += f"   描述: {item['message']}\n"
                if item.get("path"):
                    md += f"   位置: {item['path']}"
                    if item.get("line", 0) > 0:
                        md += f":{item['line']}"
                    md += "\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def generate_project_report(project: Project, output_path: str = None) -> tuple[Optional[str], str]:
        """生成项目报告"""
        try:
            # 获取项目模板信息以生成更完整的报告
            template_service = __import__('src.services.template_service', fromlist=['TemplateService']).TemplateService
            template = template_service.get_template(project.template_id)
            
            report_data = {
                "report_id": f"RPT-PROJECT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "report_type": "项目状态报告",
                "generated_at": datetime.now().isoformat(),
                "project": project.to_dict(),
                "template_info": {
                    "template_id": project.template_id,
                    "template_name": template.name if template else "未知模板",
                    "structure": template.structure if template else []
                } if template else None
            }
            
            if not output_path:
                report_dir = Path(project.path) / "19_交付物"
                output_path = str(report_dir / f"项目报告_{datetime.now().strftime('%Y%m%d')}.md")
            
            # 生成Markdown内容
            md = f"""# 项目状态报告

## 项目基本信息
- 项目编号: {project.code}
- 项目名称: {project.name}
- 业务线: {project.business_line.value}
- 状态: {project.status.value}
- 负责人: {project.manager or "-"}
- 创建时间: {project.created_at.isoformat()}
- 更新时间: {project.updated_at.isoformat()}

## 项目描述
{project.description or "无"}

## 项目路径
{project.path}

## 模板信息
- 模板ID: {project.template_id}
- 模板名称: {template.name if template else "未知模板"}
"""
            
            write_file(output_path, md)
            logger.info(f"项目报告已生成: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成项目报告失败: {e}")
            return None, f"生成项目报告失败: {str(e)}"
    
    @staticmethod
    def generate_report(project: Project, type_key: str, output_path: str = None) -> tuple[Optional[str], str]:
        """
        根据类型生成不同格式的项目报告
        
        Args:
            project: 项目对象
            type_key: 报告类型
                - "overview_md": 项目概览报告（Markdown格式）
                - "detail_md": 详细报告（Markdown格式）
                - "statistics_json": 统计报告（JSON格式）
                - "progress_md": 进度报告（Markdown格式）
            output_path: 输出路径（可选）
        
        Returns:
            (输出路径, 错误信息)
        """
        try:
            if not project:
                return None, "项目不存在"
            
            project_path = Path(project.path)
            if not project_path.exists():
                return None, f"项目路径不存在: {project.path}"
            
            # 获取模板信息
            template_service = __import__('src.services.template_service', fromlist=['TemplateService']).TemplateService
            template = template_service.get_template(project.template_id)
            
            # 根据类型生成不同报告
            if type_key == "overview_md":
                return ReportService._generate_overview_report(project, template, output_path)
            elif type_key == "detail_md":
                return ReportService._generate_detail_report(project, template, output_path)
            elif type_key == "statistics_json":
                return ReportService._generate_statistics_report(project, template, output_path)
            elif type_key == "progress_md":
                return ReportService._generate_progress_report(project, template, output_path)
            else:
                return None, f"不支持的报告类型: {type_key}"
                
        except Exception as e:
            logger.exception(f"生成报告失败: {e}")
            return None, f"生成报告失败: {str(e)}"
    
    @staticmethod
    def _generate_overview_report(project: Project, template, output_path: str = None) -> tuple[Optional[str], str]:
        """生成项目概览报告（Markdown格式）"""
        try:
            # 收集项目目录信息
            project_path = Path(project.path)
            existing_dirs = []
            missing_dirs = []
            
            if template and template.structure:
                for item in template.structure:
                    dir_path = project_path / item["path"]
                    if dir_path.exists():
                        existing_dirs.append(item["path"])
                    else:
                        if item.get("required", False):
                            missing_dirs.append(item["path"])
            
            # 计算完成率
            total_required = len(existing_dirs) + len(missing_dirs)
            completion_rate = round((len(existing_dirs) / total_required * 100), 2) if total_required > 0 else 0
            
            if not output_path:
                report_dir = project_path / "19_交付物"
                report_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(report_dir / f"项目概览报告_{datetime.now().strftime('%Y%m%d')}.md")
            
            md = f"""# {project.name} - 项目概览报告

## 基本信息
| 项目 | 内容 |
|------|------|
| 项目编号 | {project.code} |
| 项目名称 | {project.name} |
| 业务线 | {project.business_line.value} ({BUSINESS_LINE_DESC.get(project.business_line, "")}) |
| 当前状态 | {project.status.value} |
| 项目负责人 | {project.manager or "-"} |
| 创建日期 | {project.created_at.strftime('%Y-%m-%d')} |
| 最后更新 | {project.updated_at.strftime('%Y-%m-%d')} |

## 项目描述
{project.description or "暂无描述"}

## 模板信息
- **模板名称**: {template.name if template else "未知模板"}
- **模板版本**: {template.version if template else "-"}
- **适用场景**: {template.scene or "-" if template else "-"}

## 目录结构完成情况
- **必填目录总数**: {total_required}
- **已创建**: {len(existing_dirs)}
- **缺失**: {len(missing_dirs)}
- **完成率**: {completion_rate}%

### 已创建目录
{chr(10).join(f"- {d}" for d in existing_dirs) if existing_dirs else "- 无"}

### 缺失的必填目录
{chr(10).join(f"- ⚠️ {d}" for d in missing_dirs) if missing_dirs else "- 全部已创建 ✅"}

## 快速链接
- [详细报告](./详细报告_{datetime.now().strftime('%Y%m%d')}.md)
- [统计报告](./统计报告_{datetime.now().strftime('%Y%m%d')}.json)

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*由 Python项目管理工具 自动生成*
"""
            
            write_file(output_path, md)
            logger.info(f"项目概览报告已生成: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成概览报告失败: {e}")
            return None, f"生成概览报告失败: {str(e)}"
    
    @staticmethod
    def _generate_detail_report(project: Project, template, output_path: str = None) -> tuple[Optional[str], str]:
        """生成详细报告（Markdown格式）"""
        try:
            project_path = Path(project.path)
            
            # 收集详细的目录和文件信息
            structure_details = []
            file_list = []
            
            if template and template.structure:
                for item in template.structure:
                    dir_path = project_path / item["path"]
                    item_info = {
                        "path": item["path"],
                        "required": item.get("required", False),
                        "description": item.get("description", ""),
                        "exists": dir_path.exists(),
                        "file_count": 0,
                        "files": []
                    }
                    
                    if dir_path.exists():
                        files = list(dir_path.iterdir()) if dir_path.is_dir() else []
                        item_info["file_count"] = len(files)
                        item_info["files"] = [f.name for f in files[:10]]  # 只显示前10个文件
                        file_list.extend([str(f.relative_to(project_path)) for f in files])
                    
                    structure_details.append(item_info)
            
            # 获取变更记录（如果存在）
            change_records = []
            change_dir = project_path / "05_变更管理"
            if change_dir.exists():
                for subdir in change_dir.iterdir():
                    if subdir.is_dir():
                        for f in subdir.glob("*.md"):
                            change_records.append(f.name)
            
            if not output_path:
                report_dir = project_path / "19_交付物"
                report_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(report_dir / f"详细报告_{datetime.now().strftime('%Y%m%d')}.md")
            
            md = f"""# {project.name} - 详细报告

## 1. 项目基本信息
| 属性 | 值 |
|------|-----|
| 项目编号 | {project.code} |
| 项目全称 | {project.full_name} |
| 业务线 | {project.business_line.value} |
| 业务线描述 | {BUSINESS_LINE_DESC.get(project.business_line, "")} |
| 模板ID | {project.template_id} |
| 模板名称 | {template.name if template else "未知"} |
| 项目状态 | {project.status.value} |
| 负责人 | {project.manager or "未指定"} |
| 当年序号 | {project.sequence} |
| 项目路径 | {project.path} |
| 创建时间 | {project.created_at.isoformat()} |
| 更新时间 | {project.updated_at.isoformat()} |

## 2. 项目描述
{project.description or "暂无项目描述"}

## 3. 目录结构详情

"""
            
            for detail in structure_details:
                status_icon = "✅" if detail["exists"] else "❌"
                required_mark = "【必填】" if detail["required"] else "【可选】"
                md += f"""### {status_icon} {detail['path']} {required_mark}
- **说明**: {detail['description'] or '-'}
- **状态**: {'已创建' if detail['exists'] else '未创建'}
- **包含文件数**: {detail['file_count']}
"""
                
                if detail["files"]:
                    md += "- **文件列表**:\n"
                    for fname in detail["files"]:
                        md += f"  - {fname}\n"
                md += "\n"
            
            md += f"""## 4. 变更记录概览
- **变更管理目录**: {'存在' if change_dir.exists() else '不存在'}
- **变更记录数**: {len(change_records)}

"""
            
            if change_records:
                md += "### 最近变更记录\n"
                for record in change_records[:20]:
                    md += f"- {record}\n"
                md += "\n"
            
            md += f"""## 5. 文件统计
- **总文件数**: {len(file_list)}
- **目录结构完整率**: {round(sum(1 for d in structure_details if d['exists']) / len(structure_details) * 100, 2) if structure_details else 0}%

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*由 Python项目管理工具 自动生成*
"""
            
            write_file(output_path, md)
            logger.info(f"详细报告已生成: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成详细报告失败: {e}")
            return None, f"生成详细报告失败: {str(e)}"
    
    @staticmethod
    def _generate_statistics_report(project: Project, template, output_path: str = None) -> tuple[Optional[str], str]:
        """生成统计报告（JSON格式）"""
        try:
            project_path = Path(project.path)
            
            # 收集统计数据
            stats = {
                "report_id": f"RPT-STAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "project": {
                    "id": project.project_id,
                    "code": project.code,
                    "name": project.name,
                    "business_line": project.business_line.value,
                    "status": project.status.value,
                    "manager": project.manager,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat()
                },
                "directory_stats": {
                    "total_defined": 0,
                    "total_exists": 0,
                    "total_missing_required": 0,
                    "completion_rate": 0.0,
                    "details": []
                },
                "file_stats": {
                    "total_files": 0,
                    "by_extension": {},
                    "by_directory": {}
                },
                "document_stats": {
                    "total_documents": 0,
                    "documents": []
                },
                "change_stats": {
                    "total_changes": 0,
                    "changes_by_type": {}
                },
                "template_info": {
                    "template_id": project.template_id,
                    "template_name": template.name if template else "未知",
                    "version": template.version if template else "-"
                }
            }
            
            # 目录统计
            if template and template.structure:
                stats["directory_stats"]["total_defined"] = len(template.structure)
                
                for item in template.structure:
                    dir_path = project_path / item["path"]
                    exists = dir_path.exists()
                    
                    if exists:
                        stats["directory_stats"]["total_exists"] += 1
                    elif item.get("required", False):
                        stats["directory_stats"]["total_missing_required"] += 1
                    
                    dir_detail = {
                        "path": item["path"],
                        "required": item.get("required", False),
                        "exists": exists,
                        "file_count": 0
                    }
                    
                    if exists and dir_path.is_dir():
                        files = list(dir_path.iterdir())
                        dir_detail["file_count"] = len(files)
                        
                        # 统计文件
                        for f in files:
                            if f.is_file():
                                stats["file_stats"]["total_files"] += 1
                                ext = f.suffix.lower() or "(无扩展名)"
                                stats["file_stats"]["by_extension"][ext] = stats["file_stats"]["by_extension"].get(ext, 0) + 1
                                
                                rel_path = str(f.relative_to(project_path))
                                parent_dir = str(f.parent.relative_to(project_path))
                                stats["file_stats"]["by_directory"][parent_dir] = stats["file_stats"]["by_directory"].get(parent_dir, 0) + 1
                    
                    stats["directory_stats"]["details"].append(dir_detail)
            
            # 计算完成率
            total = stats["directory_stats"]["total_defined"]
            if total > 0:
                stats["directory_stats"]["completion_rate"] = round(
                    (stats["directory_stats"]["total_exists"] / total) * 100, 2
                )
            
            # 文档统计
            doc_extensions = ['.md', '.txt', '.doc', '.docx', '.pdf']
            doc_dir = project_path / "01_项目文档"
            if doc_dir.exists():
                for f in doc_dir.rglob("*"):
                    if f.is_file() and f.suffix.lower() in doc_extensions:
                        stats["document_stats"]["total_documents"] += 1
                        stats["document_stats"]["documents"].append({
                            "name": f.name,
                            "path": str(f.relative_to(project_path)),
                            "size": f.stat().st_size,
                            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                        })
            
            # 变更统计
            change_dir = project_path / "05_变更管理"
            if change_dir.exists():
                for subdir in change_dir.iterdir():
                    if subdir.is_dir():
                        changes = list(subdir.glob("*"))
                        stats["change_stats"]["total_changes"] += len(changes)
                        stats["change_stats"]["changes_by_type"][subdir.name] = len(changes)
            
            if not output_path:
                report_dir = project_path / "19_交付物"
                report_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(report_dir / f"统计报告_{datetime.now().strftime('%Y%m%d')}.json")
            
            write_json(output_path, stats)
            logger.info(f"统计报告已生成: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成统计报告失败: {e}")
            return None, f"生成统计报告失败: {str(e)}"
    
    @staticmethod
    def _generate_progress_report(project: Project, template, output_path: str = None) -> tuple[Optional[str], str]:
        """生成进度报告（Markdown格式）"""
        try:
            project_path = Path(project.path)
            
            # 收集进度数据
            milestones = []
            current_phase = "未定义"
            phase_completion = {}
            
            if template and template.structure:
                # 根据目录判断当前阶段
                phases = {
                    "00_项目基础信息": ("项目立项", ["00_项目基础信息"]),
                    "01_项目文档": ("需求设计", ["01_项目文档", "02_需求设计"]),
                    "03_主程序": ("开发实施", ["03_主程序"]),
                    "06_测试相关": ("测试验证", ["06_测试相关", "04_调试记录", "06_测试与验收"]),
                    "19_交付物": ("交付验收", ["19_交付物", "07_交付文档"]),
                }
                
                for phase_name, (phase_label, dirs) in phases.items():
                    completed = sum(1 for d in dirs if (project_path / d).exists())
                    total = len(dirs)
                    rate = round((completed / total) * 100, 2) if total > 0 else 0
                    phase_completion[phase_label] = {
                        "completed": completed,
                        "total": total,
                        "rate": rate
                    }
                    
                    if rate == 100 and not milestones.__contains__(phase_label):
                        milestones.append({"phase": phase_label, "status": "已完成", "date": "-"})
                    elif 0 < rate < 100:
                        current_phase = phase_label
                
                # 设置当前阶段
                if not any(v["rate"] > 0 for v in phase_completion.values()):
                    current_phase = "项目启动"
            
            # 计算总体进度
            total_completed = sum(v["completed"] for v in phase_completion.values())
            total_all = sum(v["total"] for v in phase_completion.values())
            overall_progress = round((total_completed / total_all) * 100, 2) if total_all > 0 else 0
            
            # 估算剩余工作日（简单算法）
            estimated_days = max(0, int((100 - overall_progress) / 5))  # 假设每天5%进度
            
            if not output_path:
                report_dir = project_path / "19_交付物"
                report_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(report_dir / f"进度报告_{datetime.now().strftime('%Y%m%d')}.md")
            
            # 进度条可视化
            filled = int(overall_progress / 5)
            empty = 20 - filled
            progress_bar = "█" * filled + "░" * empty
            
            md = f"""# {project.name} - 项目进度报告

## 总体进度
### 进度: {overall_progress}%
`{progress_bar}` {overall_progress}%

**当前阶段**: {current_phase}

---

## 阶段进度详情

| 阶段 | 完成数 | 总数 | 完成率 | 状态 |
|------|--------|------|--------|------|
"""
            
            for phase_label, data in phase_completion.items():
                status = "✅ 已完成" if data["rate"] == 100 else ("🔄 进行中" if data["rate"] > 0 else "⏳ 未开始")
                md += f"| {phase_label} | {data['completed']} | {data['total']} | {data['rate']}% | {status} |\n"
            
            md += f"""
## 里程碑跟踪

| 里程碑 | 状态 | 完成日期 | 备注 |
|--------|------|----------|------|
"""
            
            for ms in milestones:
                ms_status = "✅" if ms["status"] == "已完成" else "⏳"
                md += f"| {ms['phase']} | {ms_status} {ms['status']} | {ms['date']} | |\n"
            
            # 补充未完成的里程碑
            for phase_label in phase_completion.keys():
                if phase_label not in [m["phase"] for m in milestones]:
                    md += f"| {phase_label} | ⏳ 待开始 | - | |\n"
            
            md += f"""
## 关键指标

| 指标 | 数值 |
|------|------|
| 总体完成率 | {overall_progress}% |
| 已完成阶段 | {sum(1 for v in phase_completion.values() if v['rate'] == 100)} / {len(phase_completion)} |
| 当前阶段 | {current_phase} |
| 预估剩余工作日 | ~{estimated_days} 天 |
| 报告日期 | {datetime.now().strftime('%Y-%m-%d')} |

## 建议与风险

### 下一步行动
"""
            
            if overall_progress < 25:
                md += "- 建议尽快完成项目基础信息和需求文档\n"
            elif overall_progress < 50:
                md += "- 建议推进开发实施阶段的任务\n"
            elif overall_progress < 75:
                md += "- 建议加强测试验证工作\n"
            elif overall_progress < 100:
                md += "- 建议准备交付验收材料\n"
            else:
                md += "- 项目接近完成，建议进行最终验收\n"
            
            md += f"""
### 注意事项
- 请定期更新此报告以反映最新进度
- 如有重大变更，请及时更新项目计划

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*由 Python项目管理工具 自动生成*
"""
            
            write_file(output_path, md)
            logger.info(f"进度报告已生成: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"生成进度报告失败: {e}")
            return None, f"生成进度报告失败: {str(e)}"
    
    @staticmethod
    def export_report(report_path: str, format: str = "pdf") -> tuple[Optional[str], str]:
        """导出报告为其他格式"""
        try:
            # TODO: 实现PDF/Word等格式导出
            logger.info(f"报告导出成功: {report_path} -> {format}")
            return report_path, ""
        except Exception as e:
            logger.exception(f"导出报告失败: {e}")
            return None, f"导出报告失败: {str(e)}"
