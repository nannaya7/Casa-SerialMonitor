@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

set "APP_NAME=CasaSerial"
set "DIST_DIR=WIN"
set "WORK_DIR=WIN\build"
set "SPEC_DIR=WIN\spec"
set "ROOT_DIR=%CD%"
set "ICON_FILE=%ROOT_DIR%\image\CasaSerial.ico"
set "ICON_DATA=%ROOT_DIR%\image\CASA_Serial_APP_ICON.png"
set "BUTTON_DATA=%ROOT_DIR%\image\buttons"
set "FONT_DATA=%ROOT_DIR%\Fonts"
set "UI_DATA=%ROOT_DIR%\UI"

if /I "%~1"=="--check" goto check

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"
if not exist "%SPEC_DIR%" mkdir "%SPEC_DIR%"

"%PYTHON_EXE%" -m PyInstaller ^
  --noconfirm ^
  --windowed ^
  --clean ^
  --name "%APP_NAME%" ^
  --icon "%ICON_FILE%" ^
  --add-data "%ICON_DATA%;image" ^
  --add-data "%BUTTON_DATA%;image\buttons" ^
  --add-data "%FONT_DATA%;Fonts" ^
  --add-data "%UI_DATA%;UI" ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  main.py
if errorlevel 1 goto error

echo.
echo Build complete: %DIST_DIR%\%APP_NAME%\%APP_NAME%.exe
goto done

:check
echo Python command: "%PYTHON_EXE%"
echo Build output: "%DIST_DIR%\%APP_NAME%\%APP_NAME%.exe"
echo Icon file: "%ICON_FILE%"
echo Runtime icon data: "%ICON_DATA%"
echo Runtime button data: "%BUTTON_DATA%"
echo Runtime font data: "%FONT_DATA%"
echo Runtime UI data: "%UI_DATA%"
echo Work path: "%WORK_DIR%"
echo Spec path: "%SPEC_DIR%"
goto done

:error
echo.
echo Windows build failed.
echo If PyInstaller is missing, run:
echo "%PYTHON_EXE%" -m pip install pyinstaller
echo.
exit /b 1

:done
endlocal
