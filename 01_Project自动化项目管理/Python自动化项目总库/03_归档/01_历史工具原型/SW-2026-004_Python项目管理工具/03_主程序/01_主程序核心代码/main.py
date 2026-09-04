# -*- coding: utf-8 -*-
"""
应用程序入口
"""
import sys
import os
import argparse
from pathlib import Path

def get_base_path():
    """获取基础路径（兼容PyInstaller打包）"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

def setup_paths():
    """设置Python路径"""
    base_path = get_base_path()
    src_path = base_path / "src"
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(base_path))

setup_paths()

from src.core.config import Config
Config.load_config()
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def run_gui():
    """启动GUI界面"""
    from PyQt5.QtWidgets import QApplication
    from src.ui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger.info("GUI应用启动成功")
    sys.exit(app.exec_())

def run_api():
    """启动API服务"""
    from src.api.app import create_app
    
    app = create_app()
    host = Config.get("api.host", "127.0.0.1")
    port = Config.get("api.port", 5000)
    debug = Config.get("api.debug", False)
    
    logger.info(f"API服务启动，监听 {host}:{port}")
    app.run(host=host, port=port, debug=debug)

def run_cli():
    """启动CLI模式"""
    import click
    
    @click.group()
    def cli():
        """Python项目管理工具"""
        pass
    
    @cli.command()
    def gui():
        """启动GUI界面"""
        run_gui()
    
    @cli.command()
    def api():
        """启动API服务"""
        run_api()
    
    @cli.command()
    @click.option("--business-line", required=True, help="业务线")
    @click.option("--name", required=True, help="项目名称")
    @click.option("--template-id", required=True, help="模板ID")
    @click.option("--path", help="自定义路径")
    @click.option("--manager", help="项目负责人")
    def create_project(business_line, name, template_id, path, manager):
        """创建新项目"""
        from src.services.project_service import ProjectService
        project, error = ProjectService.create_project(
            business_line=business_line,
            name=name,
            template_id=template_id,
            manager=manager,
            custom_path=path
        )
        
        if error:
            click.echo(f"创建失败: {error}", err=True)
            sys.exit(1)
        
        click.echo(f"项目创建成功: {project.code} {project.name}")
        click.echo(f"路径: {project.path}")
    
    @cli.command()
    @click.argument("project_id")
    @click.option("--type", default="all", help="检查类型")
    def check_project(project_id, type):
        """检查项目规范"""
        from src.services.project_service import ProjectService
        from src.services.check_service import CheckService
        from src.services.report_service import ReportService
        
        project = ProjectService.get_project(project_id)
        if not project:
            click.echo(f"项目不存在: {project_id}", err=True)
            sys.exit(1)
        
        click.echo(f"正在检查项目: {project.code} {project.name}")
        check_types = None if type == "all" else [type]
        
        result, error = CheckService.check_project(project, check_types)
        if error:
            click.echo(f"检查失败: {error}", err=True)
            sys.exit(1)
        
        report_path, report_error = ReportService.generate_check_report(project, result)
        
        click.echo(f"\n检查完成:")
        click.echo(f"总检查项: {result.total}")
        click.echo(f"通过: {result.passed} ({round((result.passed/result.total*100), 2)}%)")
        click.echo(f"警告: {result.warnings}")
        click.echo(f"错误: {result.errors}")
        
        if report_path:
            click.echo(f"\n报告已生成: {report_path}")
    
    @cli.command()
    def info():
        """显示工具信息"""
        from src.core.version import VERSION
        from src.core.config import Config
        
        click.echo("Python项目管理工具")
        click.echo(f"版本: {VERSION}")
        click.echo("功能:")
        click.echo("  - 项目创建与管理")
        click.echo("  - 项目规范检查")
        click.echo("  - 模板管理")
        click.echo("  - 配置管理")
        click.echo("  - API服务")
        click.echo("  - GUI界面")
        click.echo("  - 规范同步管理 (新增)")
        click.echo("")
        click.echo("规范同步命令:")
        click.echo("  check-spec       检查规范更新")
        click.echo("  sync-spec        同步规范到最新版本")
        click.echo("  spec-info        显示规范信息")
    
    @cli.command()
    def version():
        """显示版本信息"""
        from src.core.version import VERSION
        click.echo(f"Python项目管理工具 v{VERSION}")
    
    @cli.command()
    @click.option("--auto-sync", is_flag=True, help="自动同步修订更新")
    def check_spec(auto_sync):
        """检查规范更新"""
        from src.core.spec_manager import SpecManager
        
        manager = SpecManager()
        click.echo("正在检查规范更新...")
        
        results = manager.check_updates()
        
        # 显示检查结果
        click.echo("\n" + "="*60)
        click.echo("规范更新检查报告")
        click.echo("="*60)
        click.echo(f"检查时间: {results['检查时间']}")
        click.echo("")
        
        # 可更新规范
        if results["可更新规范"]:
            click.echo(f"【可更新规范】({len(results['可更新规范'])}个)")
            for spec in results["可更新规范"]:
                click.echo(f"  • {spec['规范名称']}: {spec['当前版本']} → {spec['最新版本']} ({spec['更新类型']})")
            click.echo("")
        
        # 已最新规范
        if results["已最新规范"]:
            click.echo(f"【已最新规范】({len(results['已最新规范'])}个)")
            for spec in results["已最新规范"]:
                click.echo(f"  ✓ {spec['规范名称']}: {spec['当前版本']}")
            click.echo("")
        
        # 未找到规范
        if results["未找到规范"]:
            click.echo(f"【未找到规范】({len(results['未找到规范'])}个)")
            for spec in results["未找到规范"]:
                click.echo(f"  x {spec['规范名称']}: {spec['预期路径']}")
            click.echo("")
        
        click.echo("="*60)
        
        # 询问是否同步
        if results["可更新规范"]:
            if auto_sync:
                click.echo("\n正在自动同步修订更新...")
                sync_results = manager.sync_all_specs(auto_sync=True)
                
                success_count = len(sync_results.get("同步成功", []))
                skip_count = len(sync_results.get("跳过", []))
                
                click.echo(f"同步完成: 成功 {success_count} 个, 跳过 {skip_count} 个")
                
                for spec in sync_results.get("同步成功", []):
                    click.echo(f"  ✓ {spec['规范名称']}: {spec['原版本']} → {spec['新版本']}")
                
                for spec in sync_results.get("跳过", []):
                    click.echo(f"  ⊘ {spec['规范名称']}: {spec['原因']}")
            else:
                click.echo("\n提示: 使用 --auto-sync 参数可自动同步修订更新")
                click.echo("      或使用 'python main.py sync-spec' 命令同步所有规范")
    
    @cli.command()
    @click.option("--spec-name", help="指定规范名称，不指定则同步所有")
    @click.option("--no-backup", is_flag=True, help="不备份旧版本")
    def sync_spec(spec_name, no_backup):
        """同步规范到最新版本"""
        from src.core.spec_manager import SpecManager
        
        manager = SpecManager()
        backup = not no_backup
        
        if spec_name:
            # 同步单个规范
            click.echo(f"正在同步规范: {spec_name}...")
            result = manager.sync_spec(spec_name, backup=backup)
            
            if result["成功"]:
                if "消息" in result:
                    click.echo(result["消息"])
                else:
                    click.echo(f"✓ 同步成功: {result['规范名称']}")
                    click.echo(f"  版本: {result['原版本']} → {result['新版本']}")
                    if result.get("备份路径"):
                        click.echo(f"  备份: {result['备份路径']}")
            else:
                click.echo(f"✗ 同步失败: {result.get('错误', '未知错误')}", err=True)
                sys.exit(1)
        else:
            # 同步所有规范
            click.echo("正在同步所有可更新的规范...")
            results = manager.sync_all_specs(auto_sync=False)
            
            success_count = len(results.get("同步成功", []))
            fail_count = len(results.get("同步失败", []))
            skip_count = len(results.get("跳过", []))
            
            click.echo(f"\n同步完成:")
            click.echo(f"  成功: {success_count} 个")
            click.echo(f"  失败: {fail_count} 个")
            click.echo(f"  跳过: {skip_count} 个")
            
            if results["同步成功"]:
                click.echo("\n同步成功的规范:")
                for spec in results["同步成功"]:
                    click.echo(f"  ✓ {spec['规范名称']}: {spec['原版本']} → {spec['新版本']}")
            
            if results["同步失败"]:
                click.echo("\n同步失败的规范:")
                for spec in results["同步失败"]:
                    click.echo(f"  ✗ {spec['规范名称']}: {spec['错误']}")
            
            if results["跳过"]:
                click.echo("\n跳过的规范:")
                for spec in results["跳过"]:
                    click.echo(f"  ⊘ {spec['规范名称']}: {spec['原因']}")
    
    @cli.command()
    def spec_info():
        """显示规范信息"""
        from src.core.spec_manager import SpecManager
        
        manager = SpecManager()
        spec_list = manager.config.get("规范清单", {})
        
        click.echo("="*60)
        click.echo("项目引用的全局规范清单")
        click.echo("="*60)
        click.echo("")
        
        for spec_name, spec_info in spec_list.items():
            click.echo(f"【{spec_name}】")
            click.echo(f"  规范ID: {spec_info.get('规范ID', 'N/A')}")
            click.echo(f"  当前版本: {spec_info.get('当前版本', 'N/A')}")
            click.echo(f"  最新版本: {spec_info.get('最新版本', '未检查')}")
            click.echo(f"  状态: {spec_info.get('更新状态', '未检查')}")
            click.echo(f"  重要性: {spec_info.get('重要性', '中')}")
            click.echo(f"  描述: {spec_info.get('描述', 'N/A')}")
            click.echo("")
        
        click.echo("="*60)
        click.echo(f"总计: {len(spec_list)} 个规范")
        click.echo("="*60)
    
    cli()

def main():
    """主函数"""
    if getattr(sys, 'frozen', False):
        run_gui()
        return
    
    parser = argparse.ArgumentParser(description="Python项目管理工具")
    parser.add_argument("--mode", choices=["gui", "api", "cli"], default="gui", help="运行模式")
    
    if len(sys.argv) > 1 and sys.argv[1] not in ["--mode", "-m"]:
        run_cli()
    else:
        args = parser.parse_args()
        
        if args.mode == "gui":
            run_gui()
        elif args.mode == "api":
            run_api()
        elif args.mode == "cli":
            run_cli()

if __name__ == "__main__":
    main()
