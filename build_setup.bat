@echo off
setlocal

rem Usage: build_setup.bat [version] [--skip-build]
rem   version      e.g. 0.01.202 (default: value in installer\CasaSerial.iss)
rem   --skip-build reuse the existing WIN\CasaSerial folder
rem Output: WIN\Setup\CasaSerial_Setup_<version>.exe  (all build output lives under WIN)

cd /d "%~dp0"

set "APP_VERSION="
set "SKIP_BUILD="
:parse
if "%~1"=="" goto parsed
if /I "%~1"=="--skip-build" (
  set "SKIP_BUILD=1"
) else (
  set "APP_VERSION=%~1"
)
shift
goto parse
:parsed

set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo Inno Setup 6 was not found. Install it from https://jrsoftware.org/isdl.php
  exit /b 1
)

if not defined SKIP_BUILD (
  call "%~dp0build_win.bat"
  if errorlevel 1 exit /b 1
)

if not exist "WIN\CasaSerial\CasaSerial.exe" (
  echo WIN\CasaSerial\CasaSerial.exe not found. Run build_win.bat first.
  exit /b 1
)

if defined APP_VERSION (
  "%ISCC%" /Qp "/DAppVersion=%APP_VERSION%" "installer\CasaSerial.iss"
) else (
  "%ISCC%" /Qp "installer\CasaSerial.iss"
)
if errorlevel 1 (
  echo Installer build failed.
  exit /b 1
)

echo.
echo Setup build complete: WIN\Setup
endlocal
