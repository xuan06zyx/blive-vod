# -*- coding: utf-8 -*-
"""
打包脚本 - 将 blive-vod 打包为单个 exe 文件
使用 PyInstaller onefile 模式，无需目标机器安装 Python
"""
import subprocess
import sys
import os

# 项目根目录（package-exe 的上级目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")

def install_pyinstaller():
    """确保 PyInstaller 已安装"""
    try:
        import PyInstaller
        print(f"[打包] PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("[打包] 正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[打包] PyInstaller 安装完成")


def build():
    """执行打包"""
    install_pyinstaller()

    main_script = os.path.join(PROJECT_ROOT, "main.py")

    # PyInstaller 参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        # 单文件模式（只生成一个 exe）
        "--onefile",
        # 控制台程序
        "--console",
        # 程序名
        "--name", "blive-vod",
        # 输出目录
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        # 指定 spec 文件目录
        "--specpath", os.path.dirname(os.path.abspath(__file__)),
        # 隐式导入
        "--hidden-import", "aiohttp",
        "--hidden-import", "asyncio",
        "--hidden-import", "http.cookies",
        "--hidden-import", "blivedm",
        "--hidden-import", "blivedm.clients",
        "--hidden-import", "blivedm.clients.web",
        "--hidden-import", "blivedm.clients.ws_base",
        "--hidden-import", "blivedm.models",
        "--hidden-import", "blivedm.models.web",
        "--hidden-import", "blivedm.handlers",
        "--hidden-import", "blivedm.utils",
        # 主脚本
        main_script,
    ]

    print("[打包] 开始打包（onefile 模式）...")
    print(f"[打包] 项目目录: {PROJECT_ROOT}")
    print(f"[打包] 输出目录: {DIST_DIR}")
    subprocess.check_call(args)

    print("\n" + "=" * 50)
    print("[完成] 打包成功！")
    print(f"[输出] {os.path.join(DIST_DIR, 'blive-vod.exe')}")
    print("[说明] 只需复制 blive-vod.exe 到目标电脑即可运行")
    print("[说明] 首次启动自动生成 config.json 和歌曲黑名单文件")
    print("[说明] 首次启动约需 2-3 秒（解压运行时）")
    print("=" * 50)


if __name__ == "__main__":
    build()
