@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo 请先安装 Node.js 18 或以上版本，再双击此文件。
  pause
  exit /b 1
)
echo.
echo 布布一二 V2 本地试玩
 echo 浏览器访问：http://localhost:4173
 echo 关闭此窗口会停止本地服务器。
 echo 无需 npm install，无需 API Key。
 echo.
node scripts/serve.mjs
pause
