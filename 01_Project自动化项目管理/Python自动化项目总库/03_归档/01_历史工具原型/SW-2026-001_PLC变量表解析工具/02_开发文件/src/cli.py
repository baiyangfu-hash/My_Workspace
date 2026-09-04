#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC变量表解析工具 - 命令行接口

用途：
    解析接口文档(INT.md)并导出Excel变量表，供PLC技能自动化调用。

用法：
    plc-var-parser <INT.md文件路径> [-o <输出路径>]

退出码：
    0 = 成功
    1 = 解析失败
    2 = 导出失败
    3 = 参数错误

输出：
    成功时stdout输出JSON格式结果，便于调用方解析：
    {"status":"success","variables":14,"struct_fields":17,"output_path":"..."}
    失败时错误信息输出到stderr。
"""

import argparse
import json
import os
import sys
from typing import Optional

# 兼容两种运行场景：
# 1. 开发模式：从 02_开发文件/ 目录运行，src/ 不在 sys.path
# 2. 安装模式：plc-var-parser 命令通过 entry_points 调用，src/ 不在 sys.path
# 现有代码用绝对导入（from parser.xxx import），要求 src/ 在 sys.path
# 此处动态将 src/ 目录加入 sys.path，避免改动现有代码的 import 风格
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from parser.parser_factory import ParserFactory
from exporter.exporter import Exporter


# 退出码常量
EXIT_SUCCESS = 0
EXIT_PARSE_ERROR = 1
EXIT_EXPORT_ERROR = 2
EXIT_ARG_ERROR = 3


def build_arg_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="plc-var-parser",
        description="PLC变量表解析工具 - 解析接口文档(INT.md)并导出Excel变量表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  plc-var-parser FB_1011_INT.md\n"
            "  plc-var-parser FB_1011_INT.md -o output.xlsx\n"
            "\n"
            "默认输出路径：输入文件同目录/原文件名_变量表.xlsx\n"
            "退出码：0=成功 1=解析失败 2=导出失败 3=参数错误"
        ),
    )
    parser.add_argument(
        "intdoc",
        help="接口文档(INT.md)文件路径",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        default=None,
        help="输出Excel路径（默认：输入文件同目录/原文件名_变量表.xlsx）",
    )
    return parser


def compute_default_output_path(intdoc_path: str) -> str:
    """
    计算默认输出路径：输入文件同目录/原文件名_变量表.xlsx

    参数:
        intdoc_path: 接口文档路径

    返回:
        默认Excel输出路径
    """
    file_dir = os.path.dirname(os.path.abspath(intdoc_path))
    file_stem = os.path.splitext(os.path.basename(intdoc_path))[0]
    return os.path.join(file_dir, f"{file_stem}_变量表.xlsx")


def run(intdoc_path: str, output_path: Optional[str] = None) -> int:
    """
    执行解析+导出

    参数:
        intdoc_path: 接口文档路径
        output_path: 输出路径（None时使用默认路径）

    返回:
        退出码
    """
    # 校验输入文件存在
    if not os.path.isfile(intdoc_path):
        print(f"错误：接口文档不存在: {intdoc_path}", file=sys.stderr)
        return EXIT_ARG_ERROR

    # 计算输出路径
    if output_path is None:
        output_path = compute_default_output_path(intdoc_path)

    # 解析接口文档
    factory = ParserFactory()
    parser = factory.create_parser("intdoc", intdoc_path)
    if parser is None:
        print("错误：创建接口文档解析器失败", file=sys.stderr)
        return EXIT_PARSE_ERROR

    try:
        variables = parser.parse()
        struct_fields = parser.get_struct_fields()
    except Exception as e:
        print(f"错误：解析接口文档失败: {e}", file=sys.stderr)
        return EXIT_PARSE_ERROR

    # 校验解析结果
    if not variables:
        print(
            "错误：解析完成但未提取到变量，请确认文件是接口文档(INT.md)格式",
            file=sys.stderr,
        )
        return EXIT_PARSE_ERROR

    # 导出Excel
    exporter = Exporter()
    try:
        success = exporter.export_to_excel(
            variables, output_path, struct_fields=struct_fields
        )
    except Exception as e:
        print(f"错误：导出Excel异常: {e}", file=sys.stderr)
        return EXIT_EXPORT_ERROR

    if not success:
        print(f"错误：导出Excel失败: {output_path}", file=sys.stderr)
        return EXIT_EXPORT_ERROR

    # 输出JSON结果到stdout（便于PLC技能解析）
    result = {
        "status": "success",
        "variables": len(variables),
        "struct_fields": len(struct_fields),
        "output_path": os.path.abspath(output_path),
    }
    print(json.dumps(result, ensure_ascii=False))
    return EXIT_SUCCESS


def main() -> int:
    """CLI主入口"""
    parser = build_arg_parser()
    args = parser.parse_args()
    return run(args.intdoc, args.output)


if __name__ == "__main__":
    sys.exit(main())
