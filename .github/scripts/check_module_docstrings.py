#!/usr/bin/env python3
"""モジュール冒頭 docstring 検査。
目的:

責務:
- `__init__.py` を除く Python モジュールに冒頭 docstring があるか検査する。
- 必要時に module docstring を自動挿入する。
- CI とローカル実行で同じチェック入口を提供する。

含むもの:
- Python ファイル列挙
- AST による module docstring 判定
- 検査結果の標準出力

責務外:
- docstring 本文の品質審査
- README / docs 検証
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that Python modules have a top-level docstring."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to scan. Defaults to current directory.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Insert a default module docstring when missing.",
    )
    return parser.parse_args()


def iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        rel_parts = path.relative_to(root).parts
        parent_parts = rel_parts[:-1]
        if any(part in SKIP_DIRS for part in parent_parts):
            continue
        if any(part.startswith(".") for part in parent_parts):
            continue
        if path.name == "__init__.py":
            continue
        files.append(path)
    return sorted(files)


def has_module_docstring(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))
    return ast.get_docstring(module, clean=False) is not None


def build_default_docstring(path: Path) -> str:
    module_name = path.stem.replace("_", " ")
    return (
        f'"""{module_name} モジュール。\n\n'
        "責務:\n"
        "- このモジュールが提供する公開機能を扱う。\n"
        "- 入出力とデータ変換の境界を明確に保つ。\n\n"
        "責務外:\n"
        "- 呼び出し側の業務フロー判断\n"
        "- 外部依存の運用ポリシー決定\n"
        '"""\n\n'
    )


def insert_module_docstring(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1
    if len(lines) > insert_at and "coding" in lines[insert_at]:
        insert_at += 1

    doc = build_default_docstring(path)
    updated = "".join(lines[:insert_at]) + doc + "".join(lines[insert_at:])
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()

    missing: list[Path] = []
    fixed: list[Path] = []
    checked = 0
    for path in iter_python_files(root):
        checked += 1
        if not has_module_docstring(path):
            if args.fix:
                insert_module_docstring(path)
                if has_module_docstring(path):
                    fixed.append(path.relative_to(root))
                else:
                    missing.append(path.relative_to(root))
            else:
                missing.append(path.relative_to(root))

    if fixed:
        print("Inserted module header docstring:")
        for path in fixed:
            print(f"  - {path.as_posix()}")

    if missing:
        print("Missing module header docstring:")
        for path in missing:
            print(f"  - {path.as_posix()}")
        return 1

    print(f"Module header docstring check passed ({checked} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
