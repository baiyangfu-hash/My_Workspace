# -*- coding: utf-8 -*-
"""
数据验证工具
"""
import re
from typing import Optional

from src.core.constants import BusinessLine

def validate_project_name(name: str) -> tuple[bool, str]:
    """验证项目名称"""
    if not name or not name.strip():
        return False, "项目名称不能为空"
    
    if len(name) > 100:
        return False, "项目名称不能超过100个字符"
    
    # 检查是否包含非法字符
    invalid_chars = r'[\\/*?:"<>|]'
    if re.search(invalid_chars, name):
        return False, "项目名称不能包含特殊字符: \\ / * ? : \" < > |"
    
    return True, "验证通过"

def validate_business_line(business_line: str) -> tuple[bool, str]:
    """验证业务线类型"""
    valid_values = [e.value for e in BusinessLine]
    if business_line not in valid_values:
        return False, f"无效的业务线类型，有效值为: {', '.join(valid_values)}"
    return True, "验证通过"

def validate_template_id(template_id: str) -> tuple[bool, str]:
    """验证模板ID"""
    if not template_id:
        return False, "模板ID不能为空"
    
    if not re.match(r'^TPL-[A-Z0-9-]+$', template_id):
        return False, "模板ID格式不正确，应以TPL-开头"
    
    return True, "验证通过"

def validate_version(version: str) -> tuple[bool, str]:
    """验证版本号格式 (VX.Y.Z)"""
    if not re.match(r'^V\d+\.\d+\.\d+$', version):
        return False, "版本号格式不正确，应为: VX.Y.Z (如 V1.0.0)"
    return True, "验证通过"

def validate_version_number(version_number: str) -> tuple[bool, str]:
    """验证版本号格式 (X.Y.Z)"""
    if not version_number or not version_number.strip():
        return False, "版本号不能为空"
    
    if not re.match(r'^\d+\.\d+\.\d+$', version_number):
        return False, "版本号格式不正确，应为: X.Y.Z (如 1.0.0)"
    
    return True, "验证通过"

def validate_email(email: str) -> tuple[bool, str]:
    """验证邮箱格式"""
    if not email:
        return True, "验证通过"  # 邮箱是可选的
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "邮箱格式不正确"
    return True, "验证通过"

def validate_phone(phone: str) -> tuple[bool, str]:
    """验证手机号格式"""
    if not phone:
        return True, "验证通过"  # 手机号是可选的
    
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, phone):
        return False, "手机号格式不正确"
    return True, "验证通过"

def validate_library_name(name: str) -> tuple[bool, str]:
    """验证总库名称"""
    if not name or not name.strip():
        return False, "总库名称不能为空"
    
    if len(name) > 100:
        return False, "总库名称不能超过100个字符"
    
    # 检查是否包含非法字符
    invalid_chars = r'[\\/*?:"<>|]'
    if re.search(invalid_chars, name):
        return False, "总库名称不能包含特殊字符: \\ / * ? : \" < > |"
    
    return True, "验证通过"

def validate_category_name(name: str) -> tuple[bool, str]:
    """验证分类名称"""
    if not name or not name.strip():
        return False, "分类名称不能为空"
    
    if len(name) > 50:
        return False, "分类名称不能超过50个字符"
    
    # 检查是否包含非法字符
    invalid_chars = r'[\\/*?:"<>|]'
    if re.search(invalid_chars, name):
        return False, "分类名称不能包含特殊字符: \\ / * ? : \" < > |"
    
    return True, "验证通过"

def validate_change_title(title: str) -> tuple[bool, str]:
    """验证变更标题"""
    if not title or not title.strip():
        return False, "变更标题不能为空"
    
    if len(title) > 100:
        return False, "变更标题不能超过100个字符"
    
    # 检查是否包含非法字符
    invalid_chars = r'[\\/*?:"<>|]'
    if re.search(invalid_chars, title):
        return False, "变更标题不能包含特殊字符: \\ / * ? : \" < > |"
    
    return True, "验证通过"
