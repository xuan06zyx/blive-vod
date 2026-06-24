# -*- coding: utf-8 -*-
"""
打包脚本 - 将 blive-vod 打包为单文件夹 exe
使用 PyInstaller，无需目标机器安装 Python
"""
import subprocess
import sys
import os
import shutil

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
        # 单文件夹模式（启动更快，兼容性好）
        "--onedir",
        # 控制台程序
        "--console",
        # 程序名
        "--name", "blive-vod",
        # 输出目录
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        # 指定 spec 文件目录
        "--specpath", os.path.dirname(os.path.abspath(__file__)),
        # 隐式导入（asyncio相关）
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
        # 添加数据文件
        "--add-data", f"{os.path.join(PROJECT_ROOT, '.A歌曲黑名单.txt')};.",
        # 主脚本
        main_script,
    ]

    print("[打包] 开始打包...")
    print(f"[打包] 项目目录: {PROJECT_ROOT}")
    print(f"[打包] 输出目录: {DIST_DIR}")
    subprocess.check_call(args)

    # 复制额外文件到输出目录
    output_dir = os.path.join(DIST_DIR, "blive-vod")
    extra_files = [".A歌曲黑名单.txt"]
    for f in extra_files:
        src = os.path.join(PROJECT_ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, output_dir)
            print(f"[打包] 复制: {f}")

    # 创建启动脚本
    bat_content = """@echo off
echo ========================================
echo B站直播弹幕点歌机
echo ========================================
echo.
echo [提示] 请确保LX Music已经启动
echo [提示] 如果未启动，请先手动启动LX Music
echo.
timeout /t 3 >nul
echo [启动] 正在启动点歌机...
blive-vod.exe
pause
"""
    bat_path = os.path.join(output_dir, "启动点歌机.bat")
    with open(bat_path, "w", encoding="gbk") as f:
        f.write(bat_content)
    print(f"[打包] 创建启动脚本: 启动点歌机.bat")

    print("\n" + "=" * 50)
    print("[完成] 打包成功！")
    print(f"[输出] {output_dir}")
    print("[说明] 将整个 blive-vod 文件夹复制到目标电脑即可运行")
    print("[说明] 运行方式：双击 启动点歌机.bat 或直接运行 blive-vod.exe")
    print("=" * 50)


if __name__ == "__main__":
    build()
