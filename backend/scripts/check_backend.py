#!/usr/bin/env python3
"""
后端整体语法检查脚本。

自动遍历 backend/app 下所有 .py 文件，执行 py_compile 检查。
不依赖数据库连接，不依赖外部 API。

用法：
    python scripts/check_backend.py
    python scripts/check_backend.py backend/app

退出码：
    0 - 全部通过
    1 - 有失败
"""

import py_compile
import os
import sys
import pathlib


def find_py_files(root_dir: str) -> list[str]:
    """递归查找所有 .py 文件，排除 __pycache__ 和 .pyc。"""
    root = pathlib.Path(root_dir)
    files = []
    for p in root.rglob("*.py"):
        if "__pycache__" in str(p):
            continue
        files.append(str(p))
    return sorted(files)


def check_file(path: str) -> tuple[bool, str | None]:
    """对单个文件执行 py_compile，返回 (是否成功, 错误信息)。"""
    try:
        py_compile.compile(path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)


def main() -> int:
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        script_dir = pathlib.Path(__file__).resolve().parent
        root_dir = str(script_dir.parent / "app")

    print(f"=== Backend Syntax Check ===")
    print(f"Root: {root_dir}")
    print()

    files = find_py_files(root_dir)
    if not files:
        print(f"WARNING: No .py files found under {root_dir}")
        return 0

    print(f"Total files: {len(files)}")
    print()

    passed = 0
    failed = 0
    failed_files: list[tuple[str, str]] = []

    for path in files:
        ok, err = check_file(path)
        rel = pathlib.Path(path).relative_to(pathlib.Path(root_dir).parent.parent)
        if ok:
            print(f"  PASS  {rel}")
            passed += 1
        else:
            print(f"  FAIL  {rel}")
            print(f"         {err}")
            failed += 1
            failed_files.append((path, err))

    print()
    print(f"=== Summary ===")
    print(f"  Passed: {passed}/{len(files)}")
    print(f"  Failed: {failed}/{len(files)}")

    if failed > 0:
        print()
        print("Failed files:")
        for path, err in failed_files:
            print(f"  - {path}")
        return 1

    print()
    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
