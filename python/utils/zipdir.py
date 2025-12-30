#!/usr/bin/env python3
"""
把某个目录下所有一级子目录分别打包成 .zip
用法：
    python zip_subdirs.py  /path/to/root  [-o /output/dir]
"""
import argparse
import os
import zipfile
from pathlib import Path

def zip_subdirs(root_dir: Path, out_dir: Path):
    """把 root_dir 下的每个一级子目录打成同名 zip"""
    out_dir.mkdir(parents=True, exist_ok=True)

    for sub in root_dir.iterdir():
        if not sub.is_dir():
            continue

        zip_path = out_dir / f"{sub.name}.zip"
        # 如果已存在同名文件，先删除以免追加
        if zip_path.exists():
            zip_path.unlink()

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in sub.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(sub)   # 保持子目录内部结构
                    zf.write(file, arcname)

        print(f"打包完成：{zip_path}")

def main():
    parser = argparse.ArgumentParser(description="把目录下所有一级子目录分别打成 zip")
    parser.add_argument("root", type=Path, help="要处理的根目录")
    parser.add_argument("-o", "--out", type=Path, default=Path.cwd(),
                        help="输出 zip 的目录（默认当前工作目录）")
    args = parser.parse_args()

    if not args.root.exists():
        parser.error(f"目录不存在：{args.root}")

    zip_subdirs(args.root.expanduser().resolve(),
                args.out.expanduser().resolve())

if __name__ == "__main__":
    main()