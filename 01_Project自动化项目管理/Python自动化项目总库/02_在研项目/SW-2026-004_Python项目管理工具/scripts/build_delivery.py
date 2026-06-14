"""Wrapper: 交付物构建脚本入口

在 `scripts/` 下提供统一入口，内部调用 `src.../scripts/build_delivery.py` 的实现。
用法:
    python build_delivery.py --version V2.6.0 [--skip-build|--verify-only]
"""
import sys

def main(argv=None):
    argv = argv or sys.argv[1:]

    # delegate to core implementation
    from src.scripts.build_delivery import main as core_main

    # core_main expects to be called as a script; pass through argv
    return core_main(argv)

if __name__ == '__main__':
    raise SystemExit(main())
