# -*- coding: utf-8 -*-
"""
统一交付物构建脚本 (build_delivery.py)

基于全局规范: 220_Python项目打包规范_DEV-V2.2.0
强制使用Python zipfile, 禁止PowerShell Compress-Archive

用法:
    python build_delivery.py --version V2.4.3              # 完整流程
    python build_delivery.py --version V2.4.3 --skip-build   # 跳过编译
    python build_delivery.py --version V2.4.3 --verify-only  # 仅验证已有zip

流程:
    [1] 编译检查(PyInstaller) → [2] 更新06_交付物/
    → [3] 校验交付物完整性   → [4] 打包zip(Python zipfile)
    → [5] 校验zip(7项CHK)    → [6] 输出报告
"""
import os
import sys
import shutil
import zipfile
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置区
# ============================================================
BASE_DIR = Path(r"d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具")
SRC_CODE = BASE_DIR / "03_主程序" / "01_主程序核心代码"
DELIVERY_DIR = BASE_DIR / "06_交付物"
PACK_DIR = BASE_DIR / "06_交付物打包"
RELEASE_NOTES_DIR = BASE_DIR / "02_发布说明"

PRODUCT_NAME = "Python自动化项目管理系统"
EXE_NAME = "Python项目管理工具.exe"

# 阈值常量 (基于V2.4.x实际数据)
THRESHOLDS = {
    "exe_min_mb": 50,
    "internal_min_files": 400,
    "config_count": 4,
    "delivery_min_files": 900,
    "zip_min_mb": 80,
    "zip_max_mb": 200,
    "zip_normal_min_mb": 150,
    "zip_normal_max_mb": 170,
    "total_min_files": 500,
    "total_max_files": 1500,
    "doc_min_count": 3,
}

# onefile 模式阈值 (V2.5.0+ 使用 --onefile 打包, 无 _internal 目录)
THRESHOLDS_ONEFILE = {
    "exe_min_mb": 50,
    "internal_min_files": 0,
    "config_count": 4,
    "delivery_min_files": 10,
    "zip_min_mb": 30,
    "zip_max_mb": 80,
    "zip_normal_min_mb": 50,
    "zip_normal_max_mb": 70,
    "total_min_files": 10,
    "total_max_files": 200,
    "doc_min_count": 2,
}

MB = 1024 * 1024

def detect_build_mode():
    """检测打包模式: onefile 或 onedir"""
    internal_src = SRC_CODE / "dist" / "_internal"
    if internal_src.exists():
        return "onedir", THRESHOLDS
    else:
        return "onefile", THRESHOLDS_ONEFILE

# ============================================================
# 颜色输出
# ============================================================
class C:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"

def ok(msg): print(f"{C.GREEN}✅{C.RESET} {msg}")
def fail(msg): print(f"{C.RED}❌{C.RESET} {msg}")
def warn(msg): print(f"{C.YELLOW}⚠️ {C.RESET} {msg}")
def info(msg): print(f"{C.BLUE}ℹ️{C.RESET}  {msg}")
def skip(msg): print(f"⏭️  {msg}")
def header(msg): print(f"\n{C.BOLD}{'='*60}{C.RESET}\n{C.BOLD}{msg}{C.RESET}\n{C.BOLD}{'='*60}{C.RESET}")

# ============================================================
# Step 1: 编译检查
# ============================================================
def step1_build_check(args):
    header("Step 1: 编译检查")
    exe_src = SRC_CODE / "dist" / EXE_NAME

    if args.verify_only:
        skip("verify-only模式, 跳过编译检查")
        return True

    if args.skip_build:
        if exe_src.exists():
            size_mb = exe_src.stat().st_size / MB
            if size_mb >= THRESHOLDS["exe_min_mb"]:
                ok(f"exe存在且大小正常: {size_mb:.2f} MB (>{THRESHOLDS['exe_min_mb']}MB)")
                return True
            else:
                fail(f"exe太小: {size_mb:.2f} MB (<{THRESHOLDS['exe_min_mb']}MB), 需要重新编译")
                return False
        else:
            fail(f"exe不存在: {exe_src}")
            return False

    # 执行PyInstaller编译
    spec_file = SRC_CODE / f"{EXE_NAME.replace('.exe', '')}.spec"
    if not spec_file.exists():
        fail(f"spec文件不存在: {spec_file}")
        return False

    info(f"执行 PyInstaller 编译...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", str(spec_file)],
        cwd=str(SRC_CODE),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        fail(f"PyInstaller编译失败:\n{result.stderr[-500:]}")
        return False

    if exe_src.exists():
        size_mb = exe_src.stat().st_size / MB
        ok(f"编译成功: {size_mb:.2f} MB")
        return True
    else:
        fail("编译完成但未找到exe")
        return False

# ============================================================
# Step 2: 更新交付物目录
# ============================================================
def step2_update_delivery(args):
    header("Step 2: 更新06_交付物/")
    copied = []

    # 2.1 复制exe
    exe_src = SRC_CODE / "dist" / EXE_NAME
    exe_dst = DELIVERY_DIR / "01_可执行文件" / EXE_NAME
    if exe_src.exists():
        if exe_dst.exists():
            exe_dst.unlink()
        shutil.copy2(str(exe_src), str(exe_dst))
        size_mb = exe_dst.stat().st_size / MB
        ok(f"exe: {size_mb:.2f} MB")
        copied.append(exe_dst)
    else:
        fail(f"源exe不存在: {exe_src}")
        return False, copied

    # 2.2 复制_internal (从dist/或保留已有)
    internal_src = SRC_CODE / "dist" / "_internal"
    internal_dst = DELIVERY_DIR / "01_可执行文件" / "_internal"
    if internal_src.exists():
        if internal_dst.exists():
            shutil.rmtree(internal_dst)
        shutil.copytree(str(internal_src), str(internal_dst))
        internal_count = sum(len(files) for _, _, files in os.walk(internal_dst))
        ok(f"_internal/: {internal_count} 文件 (从dist复制)")
        copied.append(internal_dst)
    elif internal_dst.exists():
        internal_count = sum(len(files) for _, _, files in os.walk(internal_dst))
        ok(f"_internal/: {internal_count} 文件 (保留已有)")
        info("  (注意: dist/无_internal, 使用交付物目录中的已有版本)")
    else:
        warn("_internal不存在于dist/和交付物目录 (onefile模式可能不需要)")
        # 非致命，继续

    # 2.3 复制config到01_可执行文件/config/
    config_dst = DELIVERY_DIR / "01_可执行文件" / "config"
    config_dst.mkdir(parents=True, exist_ok=True)
    config_files = ["app_config.json", "api_config.json", "database_config.json", "spec_version_config.json"]
    config_copied = 0
    for cf in config_files:
        src_f = SRC_CODE / "config" / cf
        dst_f = config_dst / cf
        if src_f.exists():
            shutil.copy2(str(src_f), str(dst_f))
            config_copied += 1
        else:
            warn(f"配置缺失: {cf}")
    if config_copied == THRESHOLDS["config_count"]:
        ok(f"config: {config_copied}/{THRESHOLDS['config_count']} 文件")
    else:
        warn(f"config: 仅{config_copied}/{THRESHOLDS['config_count']} 文件")

    # 2.4 复制数据库
    db_src = SRC_CODE / "data" / "project_manager.db"
    db_dst = DELIVERY_DIR / "data" / "project_manager.db"
    if db_src.exists():
        (DELIVERY_DIR / "data").mkdir(parents=True, exist_ok=True)
        if db_dst.exists():
            db_dst.unlink()
        shutil.copy2(str(db_src), str(db_dst))
        ok(f"db: {db_dst.stat().st_size / 1024:.2f} KB")
    else:
        warn("db源不存在(非致命)")

    # 2.5 复制发布说明文档 (显式匹配，避免中文文件名glob/fnmatch问题)
    docs_dst = DELIVERY_DIR / "02_发布说明"
    docs_dst.mkdir(parents=True, exist_ok=True)
    
    # 显式构建期望的文件名列表 (version 已含 V 前缀)
    expected_docs = [
        f"{args.version}_更新说明.md",
        f"01_交付清单_DEL.md",
    ]
    doc_count = 0
    
    if RELEASE_NOTES_DIR.exists():
        existing_files = set(os.listdir(str(RELEASE_NOTES_DIR)))
        info(f"  源目录文件列表: {list(existing_files)}")
        for doc_name in expected_docs:
            found = False
            for existing in existing_files:
                if existing == doc_name:
                    src_f = RELEASE_NOTES_DIR / existing
                    dst_f = docs_dst / existing
                    shutil.copy2(str(src_f), str(dst_f))
                    doc_count += 1
                    found = True
                    info(f"  已复制: {existing}")
                    break
            if not found:
                warn(f"  未找到: {doc_name}")
    if doc_count >= 2:
        ok(f"发布说明: {doc_count} 个文档")
    else:
        warn(f"发布说明: 仅{doc_count}个文档(可能版本号不匹配)")

    info(f"共复制关键文件/目录: {len(copied)} 项")
    return True, copied

# ============================================================
# Step 3: 交付物目录校验
# ============================================================
def step3_verify_delivery(build_mode="onedir"):
    header("Step 3: 交付物目录校验")
    checks_passed = 0
    checks_total = 6

    # CHK-D1: exe存在且大小
    exe_path = DELIVERY_DIR / "01_可执行文件" / EXE_NAME
    if exe_path.exists() and exe_path.stat().st_size > THRESHOLDS["exe_min_mb"] * MB:
        size_mb = exe_path.stat().st_size / MB
        ok(f"[D1] exe: {size_mb:.2f} MB ✓")
        checks_passed += 1
    else:
        fail(f"[D1] exe缺失或过小 ✗")

    # CHK-D2: _internal存在且有足够文件
    internal_dir = DELIVERY_DIR / "01_可执行文件" / "_internal"
    if internal_dir.exists():
        icount = sum(len(files) for _, _, files in os.walk(internal_dir))
        if icount >= THRESHOLDS["internal_min_files"]:
            ok(f"[D2] _internal: {icount} 文件 ✓")
            checks_passed += 1
        else:
            warn(f"[D2] _internal仅{icount}文件 (<{THRESHOLDS['internal_min_files']}) ⚠")
            checks_passed += 0.5
    else:
        warn("[D2] _internal目录不存在 (onefile模式可接受) ⚠")

    # CHK-D3: config文件数
    config_dir = DELIVERY_DIR / "01_可执行文件" / "config"
    if config_dir.exists():
        ccount = len([f for f in config_dir.iterdir() if f.suffix == '.json'])
        if ccount == THRESHOLDS["config_count"]:
            ok(f"[D3] config: {ccount}/4 ✓")
            checks_passed += 1
        else:
            warn(f"[D3] config: {ccount}/4 ⚠")
    else:
        fail("[D3] config目录不存在 ✗")

    # CHK-D4: db存在
    db_path = DELIVERY_DIR / "data" / "project_manager.db"
    if db_path.exists():
        ok(f"[D4] db: 存在 ✓")
        checks_passed += 1
    else:
        warn("[D4] db不存在 ⚠ (非致命)")

    # CHK-D5: 发布文档存在
    docs_dir = DELIVERY_DIR / "02_发布说明"
    if docs_dir.exists() and any(docs_dir.iterdir()):
        dcount = len(list(docs_dir.iterdir()))
        if dcount >= 2:
            ok(f"[D5] 文档: {dcount}个 ✓")
            checks_passed += 1
        else:
            warn(f"[D5] 文档: 仅{dcount}个 ⚠")
    else:
        warn("[D5] 文档目录空或不存在 ⚠")

    # CHK-D6: 总文件数
    total_files = sum(len(files) for _, _, files in os.walk(DELIVERY_DIR))
    if total_files >= THRESHOLDS["delivery_min_files"]:
        ok(f"[D6] 总文件数: {total_files} ✓")
        checks_passed += 1
    else:
        fail(f"[D6] 总文件数: {total_files} (<{THRESHOLDS['delivery_min_files']}) ✗")

    status = f"{checks_passed}/{checks_total}"
    # 动态阈值: onefile模式允许1个warn(无_internal)，onedir要求严格
    pass_threshold = 4 if build_mode == "onefile" else 5
    if checks_passed >= pass_threshold:
        ok(f"校验结果: {status} PASS (模式={build_mode}, 阈值>={pass_threshold})")
        return True
    else:
        fail(f"校验结果: {status} FAIL — 不满足最低要求(>{pass_threshold})!")
        return False

# ============================================================
# Step 4: 打包zip (强制Python zipfile)
# ============================================================
def step4_package(args):
    header("Step 4: 打包zip (Python zipfile.ZIP_DEFLATED)")
    date_str = datetime.now().strftime("%Y%m%d")
    zip_name = f"{PRODUCT_NAME}_{args.version}_{date_str}.zip"
    zip_path = PACK_DIR / zip_name

    if args.verify_only:
        if not zip_path.exists():
            fail(f"待验证的zip不存在: {zip_path}")
            return None
        skip(f"verify-only模式, 使用已有zip: {zip_name}")
        return zip_path

    if zip_path.exists():
        zip_path.unlink()
        info(f"已删除旧zip")

    file_count = 0
    try:
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(str(DELIVERY_DIR)):
                for fn in files:
                    fp = os.path.join(root, fn)
                    arcname = os.path.relpath(fp, str(DELIVERY_DIR))
                    zf.write(fp, arcname)
                    file_count += 1
    except Exception as e:
        fail(f"打包失败: {e}")
        return None

    zip_size = zip_path.stat().st_size / MB
    ok(f"打包完成: {zip_name}")
    info(f"  文件数: {file_count}")
    info(f"  大小: {zip_size:.2f} MB")
    return zip_path

# ============================================================
# Step 5: ZIP校验 (7项CHK)
# ============================================================
def step5_verify_zip(zip_path):
    header("Step 5: ZIP校验 (7项CHK)")
    if not zip_path or not zip_path.exists():
        fail("无有效zip路径")
        return False

    results = {"pass": [], "warn": [], "fail": []}

    with zipfile.ZipFile(str(zip_path), 'r') as zf:
        names = zf.namelist()

        # CHK-001: 总文件数
        total = len(names)
        if total < THRESHOLDS["total_min_files"]:
            results["fail"].append(f"[CHK-001] 文件数过少: {total} (<{THRESHOLDS['total_min_files']})")
        elif total > THRESHOLDS["total_max_files"]:
            results["fail"].append(f"[CHK-001] 文件数过多: {total} (>{THRESHOLDS['total_max_files']})")
        else:
            results["pass"].append(f"[CHK-001] 文件数: {total}")

        # CHK-002: ZIP大小
        zip_size = zip_path.stat().st_size / MB
        if zip_size < THRESHOLDS["zip_min_mb"]:
            results["fail"].append(f"[CHK-002] ZIP过小: {zip_size:.2f}MB (<{THRESHOLDS['zip_min_mb']}MB)")
        elif zip_size > THRESHOLDS["zip_max_mb"]:
            results["fail"].append(f"[CHK-002] ZIP过大: {zip_size:.2f}MB (>{THRESHOLDS['zip_max_mb']}MB)")
        elif THRESHOLDS["zip_normal_min_mb"] <= zip_size <= THRESHOLDS["zip_normal_max_mb"]:
            results["pass"].append(f"[CHK-002] ZIP大小: {zip_size:.2f}MB (正常范围)")
        else:
            results["warn"].append(f"[CHK-002] ZIP大小: {zip_size:.2f}MB (可接受)")

        # CHK-003: exe存在且大小
        exe_files = [n for n in names if n.endswith('.exe')]
        if not exe_files:
            results["fail"].append("[CHK-003] 缺少exe文件!")
        else:
            exe_info = zf.getinfo(exe_files[0])
            exe_mb = exe_info.file_size / MB
            if exe_mb < 10:
                results["fail"].append(f"[CHK-003] exe过小: {exe_mb:.2f}MB")
            else:
                results["pass"].append(f"[CHK-003] exe: {exe_mb:.2f}MB")

        # CHK-004: _internal文件数
        internal_count = len([n for n in names if '_internal/' in n])
        if internal_count == 0:
            results["warn"].append("[CHK-004] zip中无_internal (onefile模式可接受)")
        elif internal_count < THRESHOLDS["internal_min_files"]:
            results["warn"].append(f"[CHK-004] _internal: {internal_count}文件 (<{THRESHOLDS['internal_min_files']})")
        else:
            results["pass"].append(f"[CHK-004] _internal: {internal_count}文件")

        # CHK-005: 关键文档
        key_docs = ['README', '交付清单', '更新说明']
        found_docs = sum(1 for d in key_docs if any(d in n for n in names))
        if found_docs < THRESHOLDS["doc_min_count"]:
            results["warn"].append(f"[CHK-005] 文档: 仅找到{found_docs}/{len(key_docs)}类")
        else:
            results["pass"].append(f"[CHK-005] 文档: {found_docs}/{len(key_docs)}类")

        # CHK-006: 配置文件
        configs = ['app_config.json', 'api_config.json', 'database_config.json', 'spec_version_config.json']
        found_cfg = sum(1 for c in configs if any(c in n for n in names))
        if found_cfg < THRESHOLDS["config_count"]:
            results["fail"].append(f"[CHK-006] 配置: 仅{found_cfg}/{THRESHOLDS['config_count']}")
        else:
            results["pass"].append(f"[CHK-006] 配置: {found_cfg}/{THRESHOLDS['config_count']}")

        # CHK-007: 一级目录结构
        top_dirs = set()
        for n in names:
            parts = n.replace('\\', '/').split('/')
            if len(parts) >= 2:
                top_dirs.add(parts[0])
        expected = {'01_可执行文件'}
        missing = expected - top_dirs
        if missing:
            results["fail"].append(f"[CHK-007] 缺少顶级目录: {missing}")
        else:
            results["pass"].append(f"[CHK-007] 顶级目录完整 ({sorted(top_dirs)})")

    # 输出结果
    for r in results["pass"]: ok(r)
    for r in results["warn"]: warn(r)
    for r in results["fail"]: fail(r)

    status = "🔴 FAIL" if results["fail"] else ("🟠 WARN" if results["warn"] else "🟢 PASS")
    info(f">>> ZIP验证: {status} (P:{len(results['pass'])} W:{len(results['warn'])} F:{len(results['fail'])})")

    return len(results["fail"]) == 0

# ============================================================
# Step 6: 输出报告
# ============================================================
def step6_report(results):
    header("Step 6: 构建报告")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    all_pass = all(results.values())
    status_icon = "🟢" if all_pass else "🔴"
    status_text = "RELEASE APPROVED" if all_pass else "RELEASE BLOCKED"

    report = f"""
{'='*60}
{status_icon} DELIVERY BUILD REPORT - {results.get('version','?')}_{datetime.now().strftime('%Y%m%d')}
{'='*60}
  Step 1 [编译]:  {'✅ PASS' if results.get('s1') else ('⏭ SKIP' if results.get('s1_skip') else '❌ FAIL')}
  Step 2 [更新]:  {'✅ PASS' if results.get('s2') else '❌ FAIL'}
  Step 3 [校验]:  {'✅ PASS' if results.get('s3') else '❌ FAIL'}
  Step 4 [打包]:  {'✅ PASS' if results.get('s4') else '❌ FAIL'}
  Step 5 [验证]:  {'✅ PASS' if results.get('s5') else '❌ FAIL'}
{'='*60}
  >>> Final Status: {status_icon} {status_text}
{'='*60}
"""
    print(report)
    return all_pass

# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="统一交付物构建脚本 — 基于220_Python项目打包规范_V2.2.0",
        epilog="示例: python build_delivery.py --version V2.4.3 --skip-build"
    )
    parser.add_argument("--version", required=True, help="目标版本号 (如 V2.4.3)")
    parser.add_argument("--skip-build", action="store_true", help="跳过PyInstaller编译步骤")
    parser.add_argument("--verify-only", action="store_true", help="仅验证已有zip，不重新打包")
    args = parser.parse_args()

    print(f"\n{C.BOLD}{'#'*60}{C.RESET}")
    print(f"{C.BOLD}#  Python项目管理系统 — 交付物构建工具{C.RESET}")
    print(f"{C.BOLD}#  基于规范: 220_Python项目打包规范_V2.2.0{C.RESET}")
    print(f"{C.BOLD}#  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")
    print(f"{C.BOLD}{'#'*60}{C.RESET}")

    results = {"version": args.version}

    # 检测打包模式并动态调整阈值 (onefile vs onedir)
    global THRESHOLDS
    build_mode, mode_thresholds = detect_build_mode()
    THRESHOLDS = mode_thresholds
    info(f"检测到打包模式: {build_mode} (阈值已自动适配)")

    # Step 1
    r1 = step1_build_check(args)
    results["s1"] = r1
    results["s1_skip"] = args.skip_build or args.verify_only
    if not r1 and not (args.skip_build or args.verify_only):
        step6_report(results)
        sys.exit(1)

    # Step 2
    r2, _ = step2_update_delivery(args)
    results["s2"] = r2
    if not r2 and not args.verify_only:
        step6_report(results)
        sys.exit(1)

    # Step 3
    if not args.verify_only:
        r3 = step3_verify_delivery(build_mode)
        results["s3"] = r3
        if not r3:
            step6_report(results)
            sys.exit(1)

    # Step 4
    zip_path = step4_package(args)
    results["s4"] = zip_path is not None

    # Step 5
    if zip_path:
        r5 = step5_verify_zip(zip_path)
        results["s5"] = r5
    else:
        results["s5"] = False

    # Step 6
    success = step6_report(results)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
