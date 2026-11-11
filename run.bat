@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

if /I "%~1"=="--check" goto check

"%PYTHON_EXE%" main.py
if errorlevel 1 goto error
goto done

:check
echo Python command: "%PYTHON_EXE%"
goto done

:error
echo.
echo Failed to run the application.
echo If dependencies are missing, run:
echo pip install -r requirements.txt
echo.
pause

:done

endlocal
