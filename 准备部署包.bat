@echo off
chcp 65001 >nul
echo.
echo 正在准备微信云开发部署包...
echo.

REM 创建临时目录
if not exist "deploy_package" mkdir deploy_package

REM 复制并重命名为 index.py
copy stock_monitor_tcb_simple.py deploy_package\index.py >nul

REM 创建 requirements.txt
echo requests>=2.31.0 > deploy_package\requirements.txt

echo 已创建以下文件:
echo   - deploy_package\index.py
echo   - deploy_package\requirements.txt
echo.

echo 请按以下步骤操作:
echo.
echo 1. 进入 deploy_package 文件夹
echo 2. 右键点击文件夹，选择"发送到" - "压缩(zipped)文件夹"
echo 3. 或者使用压缩软件将 deploy_package 文件夹压缩为 zip 文件
echo 4. 在微信云开发控制台上传这个 zip 文件
echo.

pause
