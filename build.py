#!/usr/bin/env python3
# 打包为独立可执行文件。各平台需在本机执行一次打包，得到对应系统的可执行文件。
# 用法: pip install -r requirements-build.txt && python build.py

import subprocess
import sys
import os
import platform

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # CI 环境使用英文名避免 Windows 编码问题，本地打包用中文名
    is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    app_name = "TG-Converter" if is_ci else "TG账号格式转换"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 单文件
        "--name", app_name,
        "--clean",
        "--noconfirm",
        # opentele 依赖 PyQt/PySide，需整体收集
        "--collect-all", "opentele",
    ]
    # --windowed: macOS/Windows 隐藏控制台，Linux CI 没有桌面环境则跳过
    if platform.system() != "Linux" or os.environ.get("DISPLAY"):
        cmd.append("--windowed")

    cmd.append("converter.py")
    subprocess.run(cmd, check=True)
    print("Done. Output is in dist/ directory.")

if __name__ == "__main__":
    main()
