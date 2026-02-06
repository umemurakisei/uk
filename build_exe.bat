@echo off
setlocal

REM Build a Windows executable using PyInstaller.
REM Run in cmd.exe on Windows:
REM   build_exe.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --name image_to_video image_to_video_app.py

echo.
echo Build complete. Executable path:
echo   dist\image_to_video.exe
endlocal
