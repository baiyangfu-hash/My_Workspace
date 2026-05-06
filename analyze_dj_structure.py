"""
项目目录结构分析工具 - 统计空壳目录和有内容目录的比例

用途：
    分析指定项目目录的结构，识别空壳目录（仅包含README.md或.gitignore的目录）
    和有实际内容的目录，并生成统计报告。

参数：
    本脚本硬编码了分析目标路径，需要修改 base 变量指向目标目录：
    base = Path(r"目标项目路径")

输出格式：
    1. 统计摘要：总目录数、空壳目录数、有内容目录数、空壳率
    2. 空壳目录列表：按字母排序的空壳目录完整路径
    3. 有内容目录列表：包含前3个示例文件的有内容目录路径

使用方法：
    python analyze_dj_structure.py
"""

import os
from pathlib import Path

base = Path(r"d:\BaiduSyncdisk\My_Workspace\项目文件夹\DJ-2026-014_三段式玻璃输送线控制系统")

all_dirs = []
empty_dirs = []
content_dirs = []

for root, dirs, files in os.walk(base):
    for d in dirs:
        dir_path = Path(root) / d
        all_dirs.append(dir_path)
        
        # 统计非README文件
        non_readme_files = []
        for r, _, fs in os.walk(dir_path):
            for f in fs:
                if f != 'README.md' and f != '.gitignore':
                    non_readme_files.append(f)
        
        if len(non_readme_files) == 0:
            empty_dirs.append(dir_path)
        else:
            content_dirs.append(dir_path)

print("=" * 80)
print("DJ-2026-014 项目目录结构分析报告")
print("=" * 80)
print(f"\n[统计摘要]")
print(f"   总目录数: {len(all_dirs)}")
print(f"   空壳目录(仅README): {len(empty_dirs)}")
print(f"   有内容目录: {len(content_dirs)}")
print(f"   空壳率: {len(empty_dirs)/len(all_dirs)*100:.1f}%")

print(f"\n\n[空壳目录列表] (共{len(empty_dirs)}个):")
print("-" * 80)
for i, d in enumerate(sorted(empty_dirs), 1):
    rel_path = str(d).replace(str(base), '')
    print(f"{i:2d}. {rel_path}")

print(f"\n\n[有内容目录列表] (共{len(content_dirs)}个):")
print("-" * 80)
for i, d in enumerate(sorted(content_dirs), 1):
    rel_path = str(d).replace(str(base), '')
    # 列出前3个文件作为示例
    sample_files = []
    for r, _, fs in os.walk(d):
        for f in fs[:3]:
            if f != 'README.md':
                sample_files.append(f)
        break
    print(f"{i:2d}. {rel_path} (示例: {', '.join(sample_files[:3])})")
