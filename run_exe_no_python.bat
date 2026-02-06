@echo off
setlocal

REM Python を使わずに image_to_video.exe を実行するための補助スクリプト
REM 使い方:
REM   run_exe_no_python.bat --image input.jpg --output output.mp4 --duration 120

set "APP_EXE=%~dp0dist\image_to_video.exe"

if not exist "%APP_EXE%" (
  echo [ERROR] %APP_EXE% が見つかりません。
  echo [HINT] 配布された image_to_video.exe を dist フォルダに配置してください。
  exit /b 1
)

echo [INFO] image_to_video.exe を実行します...
"%APP_EXE%" %*

endlocal
