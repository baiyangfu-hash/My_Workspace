# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

TEST_DIR = Path(r"d:\BaiduSyncdisk\My_Workspace\_test_plc_eplan_20260415")

def main():
    print("=" * 70)
    print("TPL-SINGLE-PLC-001 V2.1.0 (Eplan+机械) 自测验证")
    print("=" * 70)

    from src.core.config import Config
    Config.load_config()

    from src.dao.database import db

    from src.services.template_service import TemplateService
    TemplateService.initialize_builtin_templates()
    print("\n[初始化] 模板已更新")

    from src.services.project_service import ProjectService

    TEST_DIR.mkdir(parents=True, exist_ok=True)
    project, error = ProjectService.create_project(
        business_line="DJ",
        name="Eplan+机械结构测试项目",
        template_id="TPL-SINGLE-PLC-001",
        manager="测试",
        description="V2.1.0 Eplan+机械子目录验证",
        custom_path=str(TEST_DIR)
    )

    if error or not project:
        print(f"❌ 创建失败: {error}")
        return False

    print(f"\n✅ 项目创建成功: {project.code}")
    print(f"   路径: {project.path}")

    proj = Path(project.path)
    top_dirs = sorted([d.name for d in proj.iterdir() if d.is_dir()])
    
    print(f"\n{'='*50}")
    print(f"一级目录 ({len(top_dirs)}个):")
    for d in top_dirs:
        print(f"  📁 {d}")

    checks = {
        "一级目录=8": len(top_dirs) == 8,
        "含00_项目管理": "00_项目管理" in top_dirs,
        "含01_需求与设计": "01_需求与设计" in top_dirs,
        "含02~07": all(f"{i:02d}_" in "".join(top_dirs) for i in range(2, 8)),
    }

    design_dir = proj / "01_需求与设计"
    if design_dir.exists():
        sub_dirs = sorted([d.name for d in design_dir.iterdir() if d.is_dir()])
        print(f"\n{'='*50}")
        print(f"01_需求与设计 子目录 ({len(sub_dirs)}个):")
        for d in sub_dirs:
            print(f"  📂 {d}")

        checks["11_Eplan电气存在"] = "11_Eplan电气" in sub_dirs
        checks["12_机械结构存在"] = "12_机械结构" in sub_dirs
        checks["13_软件方案存在"] = "13_软件方案" in sub_dirs

        eplan_dir = design_dir / "11_Eplan电气"
        if eplan_dir.exists():
            eplan_subs = [d.name for d in eplan_dir.iterdir() if d.is_dir()]
            checks["Export_PDF存在"] = "Export_PDF" in eplan_subs
            checks["Source存在"] = "Source" in eplan_subs

        mech_dir = design_dir / "12_机械结构"
        if mech_dir.exists():
            mech_subs = [d.name for d in mech_dir.iterdir() if d.is_dir()]
            checks["3D_Models存在"] = "3D_Models" in mech_subs
            checks["2D_Drawings存在"] = "2D_Drawings" in mech_subs

    total_phys = sum(1 for _ in proj.rglob("*") if _.is_file())
    checks[f"总文件数>30"] = total_phys > 30

    print(f"\n{'='*50}")
    print("验证结果:")
    all_pass = True
    for k, v in checks.items():
        icon = "✅" if v else "❌"
        print(f"  {icon} {k}")
        if not v:
            all_pass = False

    import shutil
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    print(f"\n[清理] 测试目录已删除")

    if all_pass:
        print(f"\n🎉 全部通过! TPL-SINGLE-PLC-001 V2.1.0 验证成功!")
    else:
        print(f"\n⚠️ 部分检查未通过!")

    return all_pass

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
