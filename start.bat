@echo off
chcp 65001 >nul
echo =========================================
echo   服装店库存管理系统 - 启动中
echo =========================================
echo 正在用项目虚拟环境启动...
echo 启动成功后请打开浏览器访问: http://127.0.0.1:5000
echo.

REM 切到项目目录
cd /d "%~dp0"

REM 使用项目 venv（基于 uv 3.12.15，已装 Flask）
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo [错误] 找不到项目虚拟环境 venv。
    echo 请先运行: "%~dp0.venv\Scripts\python.exe" -m venv .venv
    pause
    exit /b 1
)

REM 启动
"%PY%" app.py

echo =========================================
echo 程序已退出，按任意键关闭
echo =========================================
pause
