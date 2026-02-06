@echo off
setlocal

REM Python を使わずに image_to_video.exe を実行するための補助スクリプト
REM 使い方:
REM   run_exe_no_python.bat --image input.jpg --output output.mp4 --duration 120

set "APP_EXE=%~dp0dist\image_to_video.exe"
set "FFMPEG_DIR=%~dp0tools\ffmpeg\bin"
set "FFMPEG_EXE=%FFMPEG_DIR%\ffmpeg.exe"
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "FFMPEG_ZIP=%TEMP%\ffmpeg-release-essentials.zip"
set "WORK_DIR=%TEMP%\ffmpeg_extract_%RANDOM%"

if not exist "%APP_EXE%" (
  echo [ERROR] %APP_EXE% が見つかりません。
  echo [HINT] 配布された image_to_video.exe を dist フォルダに配置してください。
  exit /b 1
)

where ffmpeg >nul 2>nul
if %ERRORLEVEL% EQU 0 goto RUN_APP

if exist "%FFMPEG_EXE%" (
  set "PATH=%FFMPEG_DIR%;%PATH%"
  goto RUN_APP
)

echo [INFO] ffmpeg が見つからないため、ローカルにダウンロードします...
if not exist "%~dp0tools\ffmpeg" mkdir "%~dp0tools\ffmpeg"

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%'"
if not exist "%FFMPEG_ZIP%" (
  echo [ERROR] ffmpeg のダウンロードに失敗しました。
  exit /b 1
)

if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
mkdir "%WORK_DIR%"

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%WORK_DIR%' -Force"
if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] ffmpeg の展開に失敗しました。
  exit /b 1
)

for /d %%D in ("%WORK_DIR%\*") do (
  if exist "%%~fD\bin\ffmpeg.exe" (
    xcopy /e /i /y "%%~fD\*" "%~dp0tools\ffmpeg\" >nul
  )
)

if not exist "%FFMPEG_EXE%" (
  echo [ERROR] ffmpeg の配置に失敗しました。
  exit /b 1
)

set "PATH=%FFMPEG_DIR%;%PATH%"

echo [INFO] ffmpeg を %~dp0tools\ffmpeg に準備しました。

:RUN_APP
echo [INFO] image_to_video.exe を実行します...
"%APP_EXE%" %*

endlocal
