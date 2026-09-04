# -*- coding: utf-8 -*-
"""将 _template_constants.py 中的 DEFAULT_TEMPLATES 转换为独立 YAML 文件"""
import sys
import os
import yaml

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ROOT = os.path.join(PROJECT_ROOT, "03_主程序", "01_主程序核心代码")
sys.path.insert(0, SRC_ROOT)

# 设置 PYTHONPATH 以确保 src 模块可导入
os.environ["PYTHONPATH"] = SRC_ROOT

# 切换工作目录以确保相对导入正常
os.chdir(SRC_ROOT)

from src.core._template_constants import DEFAULT_TEMPLATES

OUTPUT_DIR = os.path.join(SRC_ROOT, "config", "templates")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class LiteralDumper(yaml.Dumper):
    """自定义 YAML Dumper，多行字符串使用 | 块样式"""
    pass


def str_repr(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


LiteralDumper.add_representer(str, str_repr)


def main():
    for tmpl in DEFAULT_TEMPLATES:
        # 新增 schema_version 和 base_template_id 字段
        tmpl["schema_version"] = "1.0"
        tmpl["base_template_id"] = None

        template_id = tmpl["id"]
        filename = template_id + ".yaml"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                tmpl,
                f,
                Dumper=LiteralDumper,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        print("Generated: " + filename)

    print("Done! Output dir: " + OUTPUT_DIR)


if __name__ == "__main__":
    main()
