# -*- coding: utf-8 -*-
"""
SW-2026-005 PLC项目管理工具 - 配置管理模块

提供应用级别的常量定义、路径管理和配置加载功能。
支持从JSON配置文件加载自定义配置，并提供默认值回退机制。
"""

# ============================================================
# 应用基本信息
# ============================================================
APP_NAME = "SW-2026-005 PLC项目管理工具"
VERSION = "1.0.0"
AUTHOR = "Trae AI"
DESCRIPTION = "面向IEC 61131-3标准的PLC项目管理工具，集成文档管理、ST代码编辑、变量检查与HMI映射"

# ============================================================
# 技术栈版本要求
# ============================================================
PYTHON_MIN_VERSION = (3, 8)
PYQT_MIN_VERSION = (5, 15)

# ============================================================
# 默认路径配置
# ============================================================
DEFAULT_PROJECT_ROOT = "./Projects"
DEFAULT_BACKUP_DIR = "./backups"
DEFAULT_TEMPLATE_DIR = "src/templates"
DEFAULT_LOG_DIR = "logs"
DEFAULT_DATA_DIR = "data"

# ============================================================
# 数据库配置
# ============================================================
DATABASE_CONFIG = {
    "db_type": "sqlite",
    "db_name": "plc_project_manager.db",
    "echo": False,
}

# ============================================================
# 编辑器配置
# ============================================================
EDITOR_CONFIG = {
    "font_family": "Consolas",
    "font_size": 12,
    "tab_width": 4,
    "show_line_numbers": True,
    "auto_indent": True,
    "word_wrap": False,
    "st_syntax_highlighting": True,
}

# ============================================================
# PLC相关配置
# ============================================================
PLC_CONFIG = {
    "supported_brands": ["Siemens", "Beckhoff", "Omron", "Mitsubishi", "Codesys"],
    "default_brand": "Codesys",
    "iec_standards": ["IEC 61131-3"],
    "supported_languages": ["ST", "LD", "FBD", "SFC", "IL"],
}

# ============================================================
# HMI相关配置
# ============================================================
HMI_CONFIG = {
    "supported_brands": ["Siemens", "Beckhoff", "Proface", "Weinview", "Mitsubishi"],
    "default_brand": "Weinview",
}

# ============================================================
# 文档模板配置
# ============================================================
DOCUMENT_TEMPLATES = {
    "REQ": {"name": "需求规格说明书", "file": "req_template.md"},
    "DSN": {"name": "详细设计文档", "file": "dsn_template.md"},
    "IFC": {"name": "接口文档", "file": "ifc_template.md"},
    "UM": {"name": "用户操作手册", "file": "um_template.md"},
    "CHG": {"name": "变更记录", "file": "chg_template.md"},
    "ALM": {"name": "报警码定义", "file": "alm_template.md"},
    "VAR": {"name": "变量清单", "file": "var_template.md"},
    "IO": {"name": "IO分配表", "file": "io_template.md"},
    "ARC": {"name": "架构设计文档", "file": "arc_template.md"},
}

# ============================================================
# 规范检查配置（SpecCheckerService使用）
# ============================================================
SPEC_CHECK_CONFIG = {
    # 并发控制配置
    "concurrency": {
        "max_workers": 4,                    # 最大线程数（根据CPU核心数调整）
        "timeout_per_file": 30,              # 单文件检查超时时间（秒）
        "enable_parallel": True,             # 是否启用并行检查
    },
    # 文件扫描配置
    "file_scanning": {
        "supported_extensions": [".st", ".TcPOU", ".st7"],  # 支持的文件扩展名
        "exclude_patterns": [                # 排除的文件模式
            "_test",
            "test_",
            "example",
            ".bak",
            ".tmp",
        ],
        "max_file_size": 1024 * 1024,       # 最大文件大小限制（1MB）
        "recursive_scan": True,              # 是否递归扫描子目录
    },
    # 缓存机制配置
    "caching": {
        "enabled": True,                     # 是否启用结果缓存
        "cache_max_size": 1000,              # 缓存最大条目数
        "cache_ttl_seconds": 300,            # 缓存有效期（秒，5分钟）
    },
    # 项目规则覆盖配置
    "project_rules": {
        "rules_file_name": ".rules.json",    # 项目级规则配置文件名
        "auto_load_on_check": True,          # 检查时自动加载项目规则
        "fallback_to_default": True,         # 找不到规则时使用默认配置
    },
}

# ============================================================
# 诊断服务配置（DiagnosticService使用）
# ============================================================
DIAGNOSTIC_CONFIG = {
    # 完整诊断流程编排
    "full_diagnostic_flow": {
        "steps_order": [                     # 诊断步骤执行顺序
            "spec_check",                    # 第1步：规范检查
            "lsp_diagnostic",               # 第2步：LSP兼容性诊断
            "health_analysis",              # 第3步：健康度分析
        ],
        "continue_on_error": True,           # 某步失败是否继续执行后续步骤
        "timeout_total": 120,                # 整体超时时间（秒，2分钟）
    },
    # LSP诊断配置
    "lsp_diagnostic": {
        "enabled": True,                     # 是否启用LSP诊断
        "scan_plc_output_dir": True,         # 扫描.plc-out输出目录
        "detect_stub_misuse": True,          # 检测builtin stub误用
        "analyze_call_chain": True,          # 分析OB→FB调用链
        "check_missing_impl": True,          # 检查缺失的FB/FC实现
    },
    # 健康度分析配置
    "health_analysis": {
        "enabled": True,                     # 是否启用健康度分析
        "dimensions_weights": {              # 各维度权重配置
            "compliance": 0.40,             # 规范符合度权重
            "issues": 0.30,                 # 问题严重程度权重
            "library": 0.15,                # 库引用状态权重
            "structure": 0.15,              # 结构合规性权重
        },
        "generate_suggestions": True,        # 是否生成改进建议
        "min_score_for_suggestions": 80,     # 低于此分数才生成建议
    },
    # 错误处理和日志配置
    "error_handling": {
        "log_detailed_errors": True,         # 记录详细错误信息
        "collect_stack_trace": True,         # 收集堆栈跟踪
        "notify_on_critical_error": True,    # 关键错误时发送通知
    },
}

# ============================================================
# 测试配置（测试框架使用）
# ============================================================
TEST_CONFIG = {
    # 测试发现与加载
    "test_discovery": {
        "test_file_pattern": "*_test.scltest",   # 测试文件匹配模式
        "test_dir_name": "Test",                  # 测试目录名称
        "auto_discover_tests": True,              # 自动发现测试用例
        "max_test_files": 100,                    # 最大测试文件数限制
    },
    # 测试执行配置
    "execution": {
        "default_timeout": 60,                 # 默认单用例超时时间（秒）
        "stop_on_first_failure": False,         # 首次失败是否停止
        "max_retries": 2,                       # 失败重试次数
        "parallel_execution": False,            # 是否并行执行测试
    },
    # 测试报告配置
    "reporting": {
        "generate_html_report": True,           # 生成HTML格式报告
        "generate_json_report": True,           # 生成JSON格式报告
        "include_code_coverage": False,         # 包含代码覆盖率数据
        "report_output_dir": "./test_reports",  # 报告输出目录
        "retain_old_reports": 5,                # 保留的历史报告数量
    },
    # 断言和验证配置
    "assertions": {
        "strict_mode": True,                    # 严格模式（所有断言必须通过）
        "custom_assertion_timeout": 10,         # 自定义断言超时（秒）
        "allow_soft_assertions": False,         # 允许软断言（不阻断执行）
    },
}
