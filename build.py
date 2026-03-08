#!/usr/bin/env python3
# 打包为独立可执行文件。各平台需在本机执行一次打包，得到对应系统的可执行文件。
# 用法: pip install -r requirements-build.txt && python build.py

import subprocess
import sys
import os

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 单文件
        "--windowed",          # GUI 不弹控制台
        "--name", "TG账号格式转换",
        "--clean",
        "--noconfirm",
        # opentele 依赖 PyQt/PySide，需整体收集
        "--collect-all", "opentele",
        "converter.py",
    ]
    subprocess.run(cmd, check=True)
    print("完成。可执行文件在 dist/ 目录下。")

if __name__ == "__main__":
    main()
