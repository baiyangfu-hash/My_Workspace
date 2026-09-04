# -*- coding: utf-8 -*-
"""
Python项目管理工具 - 安装配置文件
"""

import os
from setuptools import setup, find_packages

# 读取版本信息
version_file = os.path.join(os.path.dirname(__file__), 'src', 'core', 'version.py')
version_dict = {}
with open(version_file, 'r', encoding='utf-8') as f:
    exec(f.read(), version_dict)

VERSION = version_dict.get('VERSION', '1.0.0')

# 读取README
readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = ''
if os.path.exists(readme_file):
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

# 读取依赖
requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = []
if os.path.exists(requirements_file):
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='python-project-manager',
    version=VERSION,
    author='技术团队',
    author_email='support@example.com',
    description='Python自动化项目总库管理系统',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/example/python-project-manager',
    
    # 包配置
    packages=find_packages(exclude=['tests', 'tests.*', 'build', 'dist']),
    include_package_data=True,
    
    # 依赖
    install_requires=requirements,
    
    # Python版本要求
    python_requires='>=3.7',
    
    # 入口点
    entry_points={
        'console_scripts': [
            'project-manager=main:main',
        ],
    },
    
    # 分类信息
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    # 关键词
    keywords='project management, automation, version control, change management',
    
    # 许可证
    license='MIT',
    
    # 项目URL
    project_urls={
        'Bug Reports': 'https://github.com/example/python-project-manager/issues',
        'Source': 'https://github.com/example/python-project-manager',
        'Documentation': 'https://github.com/example/python-project-manager/wiki',
    },
)