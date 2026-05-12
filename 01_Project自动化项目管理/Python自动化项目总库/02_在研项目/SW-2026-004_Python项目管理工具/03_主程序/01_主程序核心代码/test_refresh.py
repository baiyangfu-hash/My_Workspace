"""
刷新功能稳定性测试脚本
模拟连续多次调用模板列表接口，验证数据一致性
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.template_service import TemplateService
import time

def test_refresh_stability():
    """测试刷新功能的稳定性"""
    print("=" * 70)
    print("刷新功能稳定性测试")
    print("=" * 70)
    print()

    test_rounds = 5  # 模拟 5 次刷新
    results = []

    for i in range(1, test_rounds + 1):
        print(f"--- 第 {i}/{test_rounds} 次刷新 ---")

        start_time = time.time()
        templates = TemplateService.list_templates()
        duration = time.time() - start_time

        template_count = len(templates)
        template_ids = [t.template_id for t in templates]

        print(f"  获取到 {template_count} 个模板 (耗时 {duration:.3f}s)")
        print(f"  模板ID列表: {template_ids}")

        # 验证结果
        expected_count = 6
        if template_count == expected_count:
            status = "✅ 通过"
            # 验证是否包含所有预期的模板
            expected_ids = {
                'TPL-FULLLINE-AUTO-001',
                'TPL-SINGLE-PLC-S001',
                'TPL-SINGLE-PLC-M001',
                'TPL-SINGLE-ROBOT-001',
                'TPL-UPGRADE-STD-001',
                'TPL-UPPER-STD-001'
            }
            actual_ids = set(template_ids)
            if actual_ids == expected_ids:
                status = "✅ 通过（模板ID完全匹配）"
            else:
                missing = expected_ids - actual_ids
                extra = actual_ids - expected_ids
                status = f"⚠️ 数量正确但ID不匹配 (缺失: {missing}, 多余: {extra})"
        else:
            status = f"❌ 失败（预期 {expected_count} 个，实际 {template_count} 个）"

        print(f"  状态: {status}")
        print()

        results.append({
            'round': i,
            'count': template_count,
            'duration': duration,
            'status': status,
            'ids': template_ids
        })

        # 短暂延迟，模拟真实用户操作间隔
        if i < test_rounds:
            time.sleep(0.1)

    # 输出汇总
    print("=" * 70)
    print("测试汇总")
    print("=" * 70)

    all_pass = True
    for r in results:
        pass_mark = "✅" if "✅" in r['status'] else "❌"
        print(f"第 {r['round']:2d} 次: {r['count']:2d} 个模板 | {r['duration']:.3f}s | {pass_mark} {r['status']}")

        if "❌" in r['status']:
            all_pass = False

    print()
    if all_pass:
        print("🎉 所有刷新测试通过！核心 bug 已修复。")
        return 0
    else:
        print("⚠️ 部分测试失败，需要进一步排查。")
        return 1

if __name__ == '__main__':
    exit_code = test_refresh_stability()
    sys.exit(exit_code)
