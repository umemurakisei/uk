@echo off
setlocal

REM かんたん実行スクリプト（Python不要）
REM 引数なしでも対話形式で実行できます。
REM 例:
REM   run_exe_no_python.bat
REM   run_exe_no_python.bat --image input.jpg

set "APP_EXE=%~dp0dist\image_to_video.exe"
set "LOCAL_FFMPEG_DIR=%~dp0tools\ffmpeg\bin"
set "LOCAL_FFMPEG_EXE=%LOCAL_FFMPEG_DIR%\ffmpeg.exe"

if not exist "%APP_EXE%" (
  echo [ERROR] %APP_EXE% が見つかりません。
  echo [HINT] dist フォルダに image_to_video.exe を配置してください。
  exit /b 1
)

where ffmpeg >nul 2>nul
if %ERRORLEVEL% EQU 0 goto RUN

if exist "%LOCAL_FFMPEG_EXE%" (
  set "PATH=%LOCAL_FFMPEG_DIR%;%PATH%"
  goto RUN
)

echo [ERROR] ffmpeg が見つかりません。
echo [HINT] どちらかの方法で準備してください:
echo        1) ffmpeg をインストールして PATH に追加する
echo        2) %~dp0tools\ffmpeg\bin\ffmpeg.exe を配置する
exit /b 1

:RUN
if "%~1"=="" goto INTERACTIVE

"%APP_EXE%" %*
exit /b %ERRORLEVEL%

:INTERACTIVE
echo.
echo ==== Image to Video かんたんモード ====
set /p IMAGE_PATH=画像ファイルのパスを入力してください: 
if "%IMAGE_PATH%"=="" (
  echo [ERROR] 画像ファイルのパスは必須です。
  exit /b 1
)

set /p DURATION=動画の長さ（秒、Enterで10秒）: 
if "%DURATION%"=="" set "DURATION=10"

"%APP_EXE%" --image "%IMAGE_PATH%" --duration %DURATION%
exit /b %ERRORLEVEL%
