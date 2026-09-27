@echo off
setlocal
echo =======================================================
echo        Starting Financial Literacy Chatbot
echo =======================================================
echo.

cd /d "%~dp0"

:: Try py -3.11 launcher first
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Launching with Python 3.11 launcher (py -3.11)...
    py -3.11 -m streamlit run app.py
    if %ERRORLEVEL% equ 0 goto done
)

:: Direct path to Python 3.11
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo Launching with Python 3.11 directly...
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m streamlit run app.py
    if %ERRORLEVEL% equ 0 goto done
)

:: Fallback to python in PATH
echo Launching with default python...
python -m streamlit run app.py

:done
pause
