# -*- coding: utf-8 -*-
"""
V1.1.1 模板功能完善测试脚本
测试内容：
1. 新增模板加载测试
2. 业务线模板关联测试
3. 模板编辑器功能测试
4. 模板导入导出测试
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dao.database import db
from src.core.constants import DEFAULT_TEMPLATES, BUSINESS_LINE_TEMPLATES, BusinessLine
from src.services.template_service import TemplateService
from src.models.template import Template
from src.dao.template_dao import TemplateDAO

def test_template_count():
    """测试模板数量"""
    print("\n" + "="*60)
    print("测试1: 模板数量验证")
    print("="*60)
    
    expected_count = len(DEFAULT_TEMPLATES)
    actual_templates = TemplateService.list_templates()
    actual_count = len(actual_templates)
    
    print(f"预期模板数量: {expected_count}")
    print(f"实际模板数量: {actual_count}")
    
    if actual_count >= expected_count:
        print("✓ 模板数量验证通过")
        return True
    else:
        print("✗ 模板数量不足")
        return False

def test_plc_templates():
    """测试PLC模板"""
    print("\n" + "="*60)
    print("测试2: PLC模板验证")
    print("="*60)
    
    plc_template_ids = ["TPL-PLC-STD-001", "TPL-PLC-AUTO-001", "TPL-PLC-HMI-001"]
    all_passed = True
    
    for template_id in plc_template_ids:
        template = TemplateService.get_template(template_id)
        if template:
            print(f"✓ {template_id}: {template.name}")
            print(f"  - 结构目录数: {len(template.structure)}")
            print(f"  - 文件模板数: {len(template.templates or [])}")
            print(f"  - 适用业务线: {template.business_lines}")
        else:
            print(f"✗ {template_id}: 未找到")
            all_passed = False
    
    return all_passed

def test_business_line_templates():
    """测试业务线模板关联"""
    print("\n" + "="*60)
    print("测试3: 业务线模板关联验证")
    print("="*60)
    
    all_passed = True
    
    for bl in BusinessLine:
        bl_value = bl.value
        recommended_ids = BUSINESS_LINE_TEMPLATES.get(bl_value, [])
        
        print(f"\n{bl_value} - {bl.name}:")
        print(f"  推荐模板ID: {recommended_ids}")
        
        for template_id in recommended_ids:
            template = TemplateService.get_template(template_id)
            if template:
                print(f"  ✓ {template_id}: {template.name}")
            else:
                print(f"  ✗ {template_id}: 未找到")
                all_passed = False
    
    return all_passed

def test_template_export_import():
    """测试模板导入导出"""
    print("\n" + "="*60)
    print("测试4: 模板导入导出验证")
    print("="*60)
    
    template_id = "TPL-PLC-STD-001"
    
    json_data, error = TemplateService.export_template(template_id)
    if error:
        print(f"✗ 导出失败: {error}")
        return False
    
    print(f"✓ 导出成功，数据长度: {len(json_data)} 字符")
    
    import json
    data = json.loads(json_data)
    data["id"] = "TPL-TEST-001"
    data["name"] = "测试模板"
    
    new_template, error = TemplateService.import_template(json.dumps(data, ensure_ascii=False))
    if error:
        print(f"✗ 导入失败: {error}")
        return False
    
    print(f"✓ 导入成功: {new_template.template_id} - {new_template.name}")
    
    success, error = TemplateService.delete_template(new_template.template_id)
    if error:
        print(f"✗ 清理失败: {error}")
        return False
    
    print("✓ 测试模板已清理")
    
    return True

def test_template_structure():
    """测试模板结构完整性"""
    print("\n" + "="*60)
    print("测试5: 模板结构完整性验证")
    print("="*60)
    
    templates = TemplateService.list_templates()
    all_passed = True
    
    for template in templates:
        issues = []
        
        if not template.structure:
            issues.append("缺少目录结构")
        
        if not template.templates:
            issues.append("缺少文件模板")
        
        if issues:
            print(f"✗ {template.template_id}: {', '.join(issues)}")
            all_passed = False
        else:
            print(f"✓ {template.template_id}: 结构完整")
    
    return all_passed

def test_template_editor_data():
    """测试模板编辑器数据格式"""
    print("\n" + "="*60)
    print("测试6: 模板编辑器数据格式验证")
    print("="*60)
    
    template = TemplateService.get_template("TPL-PLC-STD-001")
    if not template:
        print("✗ 未找到PLC标准版模板")
        return False
    
    print(f"模板ID: {template.template_id}")
    print(f"模板名称: {template.name}")
    print(f"版本: {template.version}")
    print(f"编译器: {template.compiler}")
    print(f"场景: {template.scene}")
    print(f"描述: {template.description}")
    print(f"内置: {template.is_builtin}")
    print(f"业务线: {template.business_lines}")
    
    print("\n目录结构示例:")
    for i, item in enumerate(template.structure[:3]):
        print(f"  {i+1}. {item.get('path')} ({'必填' if item.get('required') else '可选'})")
    
    print("\n文件模板示例:")
    for i, item in enumerate((template.templates or [])[:3]):
        print(f"  {i+1}. {item.get('path')} ({item.get('type')})")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("V1.1.1 模板功能完善测试")
    print("="*60)
    
    print("\n初始化内置模板...")
    TemplateService.initialize_builtin_templates()
    
    results = []
    
    results.append(("模板数量验证", test_template_count()))
    results.append(("PLC模板验证", test_plc_templates()))
    results.append(("业务线模板关联", test_business_line_templates()))
    results.append(("模板导入导出", test_template_export_import()))
    results.append(("模板结构完整性", test_template_structure()))
    results.append(("模板编辑器数据", test_template_editor_data()))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
