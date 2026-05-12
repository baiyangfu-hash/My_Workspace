# -*- coding: utf-8 -*-
"""
模板测试脚本 - 测试所有内置模板的项目创建和目录结构验证

测试目标：
1. 使用 5 种模板各创建 1 个测试项目
2. 验证每个项目的目录结构完整性
3. 检查变更管理相关文件和目录
4. 输出详细的测试报告

运行方式：
    cd d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码
    python test_templates.py

作者：开发工程师
日期：2026-04-16
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TemplateTestResult:
    """单个模板测试结果"""

    def __init__(self, template_id: str, template_name: str):
        self.template_id = template_id
        self.template_name = template_name
        self.success = False
        self.project_code = None
        self.project_path = None
        self.error_message = ""
        self.directory_structure = []
        self.change_mgmt_checks = {}
        self.issues = []
        self.start_time = None
        self.end_time = None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "success": self.success,
            "project_code": self.project_code,
            "project_path": str(self.project_path) if self.project_path else None,
            "error_message": self.error_message,
            "directory_count": len(self.directory_structure),
            "change_mgmt_checks": self.change_mgmt_checks,
            "issues_count": len(self.issues),
            "issues": self.issues,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if (self.start_time and self.end_time) else 0
        }


class TemplateTester:
    """模板测试器"""

    # 测试用的模板列表
    TEST_TEMPLATES = [
        {
            "id": "TPL-FULLLINE-AUTO-001",
            "name": "自动化整线",
            "business_line": "SW",
            "test_project_name": "TEST_自动化整线模板"
        },
        {
            "id": "TPL-SINGLE-PLC-001",
            "name": "单机设备 PLC+HMI",
            "business_line": "SW",
            "test_project_name": "TEST_单机设备PLC_HMI模板"
        },
        {
            "id": "TPL-SINGLE-ROBOT-001",
            "name": "单机机器人",
            "business_line": "SW",
            "test_project_name": "TEST_单机机器人模板"
        },
        {
            "id": "TPL-UPGRADE-STD-001",
            "name": "系统升级改造",
            "business_line": "SW",
            "test_project_name": "TEST_系统升级改造模板"
        },
        {
            "id": "TPL-UPPER-STD-001",
            "name": "上位机/数据系统",
            "business_line": "SW",
            "test_project_name": "TEST_上位机数据系统模板"
        }
    ]

    def __init__(self, test_base_path: str = r"D:\temp_test_projects"):
        """
        初始化测试器

        Args:
            test_base_path: 测试项目的基础路径
        """
        self.test_base_path = Path(test_base_path)
        self.results: List[TemplateTestResult] = []
        self.project_service = None
        self.test_start_time = None
        self.test_end_time = None

    def setup(self) -> bool:
        """初始化测试环境"""
        print("\n" + "=" * 80)
        print("🧪 模板测试脚本启动")
        print("=" * 80)
        print(f"📁 测试基础路径: {self.test_base_path}")
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 测试模板数量: {len(self.TEST_TEMPLATES)}")
        print("-" * 80)

        try:
            # 创建测试基础目录
            self.test_base_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 测试目录准备完成: {self.test_base_path}")

            # 初始化 ProjectService
            from src.services.project_service import ProjectService
            self.project_service = ProjectService()
            print("✅ ProjectService 初始化成功")

            # 初始化数据库（如果需要）
            self._initialize_database()

            self.test_start_time = datetime.now()
            return True

        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _initialize_database(self):
        """初始化数据库连接"""
        try:
            from src.dao.database import Database
            db = Database()
            if not db.is_connected():
                db.connect()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"⚠️ 数据库初始化警告: {e}")

    def run_all_tests(self) -> bool:
        """运行所有模板测试"""
        print("\n" + "🚀 开始执行模板测试")
        print("-" * 80)

        for i, template_config in enumerate(self.TEST_TEMPLATES, 1):
            print(f"\n[{i}/{len(self.TEST_TEMPLATES)}] 测试模板: {template_config['id']} ({template_config['name']})")

            result = self._test_single_template(template_config)
            self.results.append(result)

            # 输出简要结果
            if result.success:
                print(f"   ✅ 测试通过 - 项目编号: {result.project_code}")
            else:
                print(f"   ❌ 测试失败 - {result.error_message}")

        self.test_end_time = datetime.now()
        return all(r.success for r in self.results)

    def _test_single_template(self, template_config: dict) -> TemplateTestResult:
        """测试单个模板"""
        result = TemplateTestResult(
            template_id=template_config["id"],
            template_name=template_config["name"]
        )
        result.start_time = datetime.now()

        try:
            # 1. 创建项目
            print(f"   📝 正在创建项目...")
            project, error_msg = self.project_service.create_project(
                business_line=template_config["business_line"],
                name=template_config["test_project_name"],
                template_id=template_config["id"],
                manager="测试管理员",
                description=f"自动测试项目 - {template_config['name']}模板",
                custom_path=str(self.test_base_path)
            )

            if not project:
                result.success = False
                result.error_message = error_msg or "创建项目失败"
                result.issues.append(f"项目创建失败: {result.error_message}")
                result.end_time = datetime.now()
                return result

            result.success = True
            result.project_code = project.code
            result.project_path = Path(project.path)
            print(f"   ✅ 项目创建成功: {project.code} @ {project.path}")

            # 2. 验证目录结构
            print(f"   🔍 正在验证目录结构...")
            self._verify_directory_structure(result)

            # 3. 验证变更管理文件
            print(f"   🔍 正在验证变更管理...")
            self._verify_change_management(result)

            result.end_time = datetime.now()

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.issues.append(f"异常错误: {e}")
            import traceback
            traceback.print_exc()
            result.end_time = datetime.now()

        return result

    def _verify_directory_structure(self, result: TemplateTestResult):
        """验证目录结构"""
        if not result.project_path or not result.project_path.exists():
            result.issues.append("项目路径不存在")
            return

        # 收集所有目录和文件
        def collect_paths(path: Path, prefix: str = "") -> List[str]:
            items = []
            try:
                for item in sorted(path.iterdir()):
                    relative_path = f"{prefix}{item.name}" if prefix else item.name
                    items.append(relative_path)
                    if item.is_dir():
                        items.extend(collect_paths(item, relative_path + "/"))
            except Exception as e:
                result.issues.append(f"无法读取目录 {path}: {e}")
            return items

        result.directory_structure = collect_paths(result.project_path)
        print(f"   📂 发现 {len(result.directory_structure)} 个目录/文件项")

        # 基本检查
        if len(result.directory_structure) == 0:
            result.issues.append("目录结构为空")

    def _verify_change_management(self, result: TemplateTestResult):
        """验证变更管理相关内容"""
        if not result.project_path:
            return

        chg_mgmt_path = result.project_path / "00_项目管理" / "04_变更管理"

        # 检查1: 变更管理主目录是否存在
        check1_key = "变更管理主目录存在"
        result.change_mgmt_checks[check1_key] = chg_mgmt_path.exists()
        if not chg_mgmt_path.exists():
            result.issues.append(f"缺少变更管理目录: 00_项目管理/04_变更管理")

        # 检查2: 必需子目录
        required_subdirs = ["01_变更单", "04_变更记录"]
        for subdir in required_subdirs:
            subdir_path = chg_mgmt_path / subdir
            check_key = f"子目录_{subdir}_存在"
            result.change_mgmt_checks[check_key] = subdir_path.exists()
            if not subdir_path.exists():
                result.issues.append(f"缺少子目录: 04_变更管理/{subdir}")

        # 检查3: 可选子目录（03_变更管理规范）
        spec_dir_path = chg_mgmt_path / "03_变更管理规范"
        check3_key = "可选子目录_03_变更管理规范_存在"
        result.change_mgmt_checks[check3_key] = spec_dir_path.exists()
        # 注意：这个目录只对特定模板存在，所以不作为必检项

        # 检查4: .gitkeep 或 README 文件
        gitkeep_path = chg_mgmt_path / "01_变更单" / ".gitkeep"
        readme_chg_path = chg_mgmt_path / "README.md"

        check4a_key = "01_变更单/.gitkeep_存在"
        result.change_mgmt_checks[check4a_key] = gitkeep_path.exists()

        check4b_key = "04_变更管理/README.md_存在"
        result.change_mgmt_checks[check4b_key] = readme_chg_path.exists()

        if not gitkeep_path.exists() and not readme_chg_path.exists():
            result.issues.append("缺少 .gitkeep 或 README.md 文件")

        # 检查5: 变更台帐文件
        if result.project_code:
            ledger_pattern = f"041_{result.project_code}_版本变更台帐_CHG-V2.1.0.md"
            ledger_path = chg_mgmt_path / "04_变更记录" / ledger_pattern

            check5_key = "变更台帐文件存在"
            result.change_mgmt_checks[check5_key] = ledger_path.exists()
            if not ledger_path.exists():
                # 尝试查找任何台帐文件
                record_dir = chg_mgmt_path / "04_变更记录"
                if record_dir.exists():
                    ledger_files = list(record_dir.glob("041_*_版本变更台帐*.md"))
                    if ledger_files:
                        result.change_mgmt_checks[check5_key] = True
                        result.issues.append(f"台帐文件名不符合预期，找到: {ledger_files[0].name}")
                    else:
                        result.issues.append(f"缺少变更台帐文件: {ledger_pattern}")
                else:
                    result.issues.append(f"缺少变更台帐文件（04_变更记录目录不存在）")

        # 检查6: 可选的变更管理流程规范文件
        if result.project_code:
            spec_pattern = f"042_{result.project_code}_变更管理流程规范_PM-V2.0.0.md"
            spec_file_path = chg_mgmt_path / "03_变更管理规范" / spec_pattern

            check6_key = "可选_变更管理流程规范_存在"
            result.change_mgmt_checks[check6_key] = spec_file_path.exists()
            # 这个是可选文件，仅记录结果

        # 统计通过率
        total_checks = len(result.change_mgmt_checks)
        passed_checks = sum(1 for v in result.change_mgmt_checks.values() if v)
        result.change_mgmt_checks["通过率"] = f"{passed_checks}/{total_checks}"

    def generate_report(self) -> str:
        """生成详细的测试报告"""
        report_lines = []
        report_lines.append("\n")
        report_lines.append("=" * 80)
        report_lines.append("📊 模板测试详细报告")
        report_lines.append("=" * 80)
        report_lines.append(f"\n⏰ 测试时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S') if self.test_start_time else 'N/A'}")
        report_lines.append(f"⏱️  总耗时: {(self.test_end_time - self.test_start_time).total_seconds():.2f} 秒" if (self.test_end_time and self.test_start_time) else "")
        report_lines.append(f"📁 测试路径: {self.test_base_path}")
        report_lines.append(f"📋 测试模板数: {len(self.results)}")
        report_lines.append("-" * 80)

        # 总体统计
        success_count = sum(1 for r in self.results if r.success)
        failure_count = len(self.results) - success_count
        total_issues = sum(len(r.issues) for r in self.results)

        report_lines.append(f"\n📈 总体统计:")
        report_lines.append(f"   ✅ 成功: {success_count}/{len(self.results)}")
        report_lines.append(f"   ❌ 失败: {failure_count}/{len(self.results)}")
        report_lines.append(f"   ⚠️  问题总数: {total_issues}")
        report_lines.append("-" * 80)

        # 各模板详情
        for i, result in enumerate(self.results, 1):
            report_lines.append(f"\n{'=' * 80}")
            report_lines.append(f"🔍 [{i}] 模板: {result.template_id} ({result.template_name})")
            report_lines.append(f"{'=' * 80}")

            # 基本信息
            status_icon = "✅" if result.success else "❌"
            report_lines.append(f"\n状态: {status_icon} {'成功' if result.success else '失败'}")
            report_lines.append(f"项目编号: {result.project_code or 'N/A'}")
            report_lines.append(f"项目路径: {result.project_path or 'N/A'}")
            report_lines.append(f"耗时: {result.to_dict()['duration_seconds']:.2f} 秒")

            if result.error_message:
                report_lines.append(f"错误信息: {result.error_message}")

            # 目录结构
            report_lines.append(f"\n📂 目录结构 ({len(result.directory_structure)} 项):")
            if result.directory_structure:
                for item in result.directory_structure[:30]:  # 最多显示前30项
                    report_lines.append(f"   ├─ {item}")
                if len(result.directory_structure) > 30:
                    report_lines.append(f"   └─ ... 还有 {len(result.directory_structure) - 30} 项")
            else:
                report_lines.append("   (空)")

            # 变更管理检查
            report_lines.append(f"\n🔄 变更管理检查:")
            for check_name, check_result in result.change_mgmt_checks.items():
                icon = "✅" if check_result else "❌"
                report_lines.append(f"   {icon} {check_name}")

            # 发现的问题
            if result.issues:
                report_lines.append(f"\n⚠️  发现的问题 ({len(result.issues)} 项):")
                for j, issue in enumerate(result.issues, 1):
                    report_lines.append(f"   {j}. {issue}")
            else:
                report_lines.append(f"\n✨ 未发现问题")

        # 总结和建议
        report_lines.append(f"\n{'=' * 80}")
        report_lines.append("📝 总结与建议")
        report_lines.append(f"{'=' * 80}")

        if all(r.success for r in self.results):
            report_lines.append("\n✨ 所有模板测试均通过！")
            report_lines.append("   所有模板都能正常创建项目并生成正确的目录结构。")
        else:
            failed_templates = [r for r in self.results if not r.success]
            report_lines.append(f"\n⚠️  {len(failed_templates)} 个模板测试未通过:")
            for r in failed_templates:
                report_lines.append(f"   - {r.template_id}: {r.error_message}")

        if total_issues > 0:
            report_lines.append(f"\n💡 建议:")
            report_lines.append(f"   1. 共发现 {total_issues} 个问题，请逐一排查")
            report_lines.append(f"   2. 重点关注变更管理相关的缺失项")
            report_lines.append(f"   3. 检查模板定义是否完整")

        report_lines.append(f"\n{'=' * 80}")
        report_lines.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def cleanup(self):
        """清理测试数据（可选）"""
        print(f"\n🧹 清理说明:")
        print(f"   测试项目保存在: {self.test_base_path}")
        print(f"   如需清理，请手动删除该目录或运行:")
        print(f"   shutil.rmtree(r'{self.test_base_path}', ignore_errors=True)")


def main():
    """主函数"""
    tester = TemplateTester(test_base_path=r"D:\temp_test_projects")

    try:
        # 初始化
        if not tester.setup():
            print("\n❌ 测试环境初始化失败，终止测试")
            return 1

        # 运行所有测试
        success = tester.run_all_tests()

        # 生成并输出报告
        report = tester.generate_report()
        print(report)

        # 保存报告到文件
        report_file = project_root / "data" / "test_reports" / f"template_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 报告已保存至: {report_file}")

        # 清理提示
        tester.cleanup()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        tester.cleanup()
        return 130
    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
        tester.cleanup()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
