@echo off
echo ========================================
echo B站直播点歌机启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [提示] 请确保LX Music已经启动
echo [提示] 如果未启动，请先手动启动LX Music
echo.
timeout /t 3 >nul

echo [启动] 正在启动点歌机...
python main.py

pause