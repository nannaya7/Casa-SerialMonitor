@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=python"
set "PYTHONW_EXE=pythonw"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"
if exist ".venv\Scripts\pythonw.exe" set "PYTHONW_EXE=.venv\Scripts\pythonw.exe"

if /I "%~1"=="--check" goto check
if /I "%~1"=="--console" goto console

rem Launch with pythonw so no terminal window is shown.
start "" "%PYTHONW_EXE%" main.py
goto done

:console
rem Debug mode: show console and error messages.
"%PYTHON_EXE%" main.py
if errorlevel 1 goto error
goto done

:check
echo Python command: "%PYTHON_EXE%"
echo Pythonw command: "%PYTHONW_EXE%"
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
