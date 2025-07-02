@echo off
echo Building KeepAwake executable...
echo.

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

echo Starting PyInstaller build...
C:\Users\beingbigz\AppData\Local\Programs\Python\Python313\python.exe -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=KeepAwake ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=tkinter ^
    "keep awake.py"

echo.
if exist "dist\KeepAwake.exe" (
    echo Build successful! 
    echo Executable created: dist\KeepAwake.exe
    dir "dist\KeepAwake.exe"
) else (
    echo Build failed - executable not found
)

pause
