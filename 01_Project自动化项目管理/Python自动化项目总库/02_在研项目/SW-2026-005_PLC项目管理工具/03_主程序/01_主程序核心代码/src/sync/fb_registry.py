# -*- coding: utf-8 -*-
"""
FB Registry - 功能块映射表统一注册中心

将原先分散在 chg_generator / ifc_generator 中的三重复制映射表
合并为单一数据源，所有模块通过 import 使用。

映射维度:
- title_en: 英文标题 (CHG文档使用)
- title_cn: 中文标题 (IFC文档使用)
- file_prefix: 文件名前缀 (CHG/IFC共用)
- struct_key: DB结构体名 (IFC文档使用)
"""
from __future__ import annotations

from typing import Dict, Optional


_FB_REGISTRY: Dict[str, dict] = {
    "conveyor": {
        "title_en": "FB_1002_SingleLayerConveyor_BufferFraming",
        "title_cn": "FB_1002 四层输送机系统",
        "file_prefix": "FB1002-SingleLayerConveyor",
        "struct_key": "stconveyor",
    },
    "pickplace": {
        "title_en": "FB_1003_PickPlace_BufferFraming",
        "title_cn": "FB_1003 取放料机构",
        "file_prefix": "FB1003-PickPlace",
        "struct_key": "stpickplace",
    },
    "feeder": {
        "title_en": "FB_1004_GlueMachineFeeder_BufferFraming",
        "title_cn": "FB_1004 打胶机送料机构",
        "file_prefix": "FB1004-GlueMachineFeeder",
        "struct_key": "stfeeder",
    },
    "alarm": {
        "title_en": "FB_2001_CommonAlarm_AllStation",
        "title_cn": "FB_2001 公共报警管理",
        "file_prefix": "FB2001-CommonAlarm",
        "struct_key": "stglobal",
    },
    "common": {
        "title_en": "FB_2001_CommonAlarm_AllStation",
        "title_cn": "FB_2001 公共报警管理",
        "file_prefix": "FB2001-CommonAlarm",
        "struct_key": "stglobal",
    },
    "2001": {
        "title_en": "FB_2001_CommonAlarm_AllStation",
        "title_cn": "FB_2001 公共报警管理",
        "file_prefix": "FB2001-CommonAlarm",
        "struct_key": "stglobal",
    },
    "external": {
        "title_en": "FB_ExternalDeviceInteraction",
        "title_cn": "FB_ExternalDeviceInteraction 外部设备交互",
        "file_prefix": "FB3001-ExternalDeviceInteraction",
        "struct_key": "stexternal",
    },
    "3001": {
        "title_en": "FB_ExternalDeviceInteraction",
        "title_cn": "FB_ExternalDeviceInteraction 外部设备交互",
        "file_prefix": "FB3001-ExternalDeviceInteraction",
        "struct_key": "stexternal",
    },
    "ob1": {
        "title_en": "OB1",
        "title_cn": "OB1 主组织块全局变量接口",
        "file_prefix": "OB1",
        "struct_key": "__ALL__",
    },
}


def resolve_title_en(fb_name: str) -> str:
    fb_lower = fb_name.lower()
    for key, entry in _FB_REGISTRY.items():
        if key in fb_lower:
            return entry["title_en"]
    return fb_name


def resolve_title_cn(fb_name: str) -> str:
    fb_lower = fb_name.lower()
    for key, entry in _FB_REGISTRY.items():
        if key in fb_lower:
            return entry["title_cn"]
    return fb_name


def resolve_file_prefix(fb_name: str) -> str:
    fb_lower = fb_name.lower()
    for key, entry in _FB_REGISTRY.items():
        if key in fb_lower:
            return entry["file_prefix"]
    return fb_name.replace("_", "-")


def resolve_struct_key(fb_name: str) -> Optional[str]:
    fb_lower = fb_name.lower()
    for key, entry in _FB_REGISTRY.items():
        if key in fb_lower:
            return entry["struct_key"]
    return None


def get_registry() -> Dict[str, dict]:
    return dict(_FB_REGISTRY)
