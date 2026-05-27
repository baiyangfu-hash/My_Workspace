# -*- coding: utf-8 -*-
"""
打包脚本

使用方法:
    python build.py [--clean] [--debug] [--onedir]
    
参数:
    --clean: 清理构建目录后重新打包
    --debug: 打包调试版本（带控制台窗口）
    --onedir: 打包为目录模式（默认单文件）
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    spec_file = 'build.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                except:
                    pass

def copy_extra_files(dist_path: Path):
    """复制额外文件到输出目录"""
    print("\n复制配置文件和插件...")
    
    config_src = Path('config')
    if config_src.exists():
        config_dst = dist_path / 'config'
        config_dst.mkdir(parents=True, exist_ok=True)
        for f in config_src.glob('*'):
            if f.is_file():
                shutil.copy2(f, config_dst / f.name)
                print(f"  复制: {f.name}")
    
    plugins_src = Path('src/plugins')
    if plugins_src.exists():
        plugins_dst = dist_path / 'src' / 'plugins'
        plugins_dst.mkdir(parents=True, exist_ok=True)
        for f in plugins_src.rglob('*'):
            if f.is_file():
                rel_path = f.relative_to(plugins_src)
                dst_file = plugins_dst / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst_file)
        print(f"  复制插件目录完成")
    
    data_dir = dist_path / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"  创建数据目录: data/")

def build_exe(debug=False, onedir=False):
    """打包可执行文件"""
    print("="*50)
    print("Python项目管理工具 - 打包脚本")
    print("="*50)
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir' if onedir else '--onefile',
        '--windowed' if not debug else '--console',
        '--name', 'Python项目管理工具',
        '--hidden-import', 'PyQt5',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'flask',
        '--hidden-import', 'sqlalchemy',
        '--hidden-import', 'sqlalchemy.dialects.sqlite',
        '--hidden-import', 'sqlalchemy.orm',
        '--hidden-import', 'sqlalchemy.ext.declarative',
        '--hidden-import', 'click',
        '--hidden-import', 'markdown',
        '--hidden-import', 'dateutil',
        '--hidden-import', 'src',
        '--hidden-import', 'src.core',
        '--hidden-import', 'src.models',
        '--hidden-import', 'src.dao',
        '--hidden-import', 'src.services',
        '--hidden-import', 'src.ui',
        '--hidden-import', 'src.utils',
        '--hidden-import', 'src.api',
        '--hidden-import', 'src.plugins',
        '--hidden-import', 'src.plugins.code_check',
        '--hidden-import', 'src.plugins.document_generator',
        '--exclude-module', 'tkinter',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PIL',
        '--exclude-module', 'cv2',
        '--exclude-module', 'IPython',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'notebook',
    ]
    
    config_dir = Path('config')
    if config_dir.exists():
        cmd.extend(['--add-data', f'config;config'])
    
    plugins_dir = Path('src/plugins')
    if plugins_dir.exists():
        cmd.extend(['--add-data', f'src/plugins;src/plugins'])
    
    cmd.append('main.py')
    
    print(f"执行命令: {' '.join(cmd)}")
    print("-"*50)
    
    result = subprocess.run(cmd, cwd=os.getcwd())
    
    if result.returncode == 0:
        print("-"*50)
        print("打包成功!")
        
        dist_dir = Path('dist')
        
        if onedir:
            output_path = dist_dir / 'Python项目管理工具'
            print(f"输出目录: {output_path}")
            copy_extra_files(output_path)
            
            exe_file = output_path / 'Python项目管理工具.exe'
            if exe_file.exists():
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"\nEXE大小: {size_mb:.2f} MB")
                
                total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
                total_mb = total_size / (1024 * 1024)
                print(f"总大小: {total_mb:.2f} MB")
        else:
            output_path = dist_dir / 'Python项目管理工具.exe'
            print(f"输出文件: {output_path}")
            
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"文件大小: {size_mb:.2f} MB")
                
                if size_mb > 50:
                    print("\n提示: 文件大小超过50MB，建议使用 --onedir 参数打包为目录模式")
        
        print("\n" + "="*50)
        print("打包完成！")
        print("="*50)
    else:
        print("-"*50)
        print("打包失败!")
        sys.exit(1)

def main():
    """主函数"""
    debug = '--debug' in sys.argv
    clean = '--clean' in sys.argv
    onedir = '--onedir' in sys.argv
    
    if clean:
        clean_build()
    
    build_exe(debug=debug, onedir=onedir)

if __name__ == '__main__':
    main()
