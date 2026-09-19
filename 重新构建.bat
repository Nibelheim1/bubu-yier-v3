@echo off
chcp 65001 >nul
cd /d "%~dp0"
node scripts/build.mjs
if errorlevel 1 (
  echo 构建失败，请查看上方错误。
) else (
  echo 构建完成，发布文件在 dist 文件夹中。
)
pause
