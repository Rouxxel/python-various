@echo off
REM Quick Start Script for WAR Card Game (Windows)
REM This script compiles and runs without external dependencies

echo WAR Card Game - Quick Start
echo ============================

REM Check Java
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java is not installed. Please install Java and try again.
    pause
    exit /b 1
)

echo SUCCESS: Java found
echo.

echo Compiling Java files...

REM Compile all Java source files (without external libs for now)
javac -d . src\card_n_deck\*.java src\players_class\*.java src\logic_class\*.java src\card_game\*.java

if errorlevel 1 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

echo SUCCESS: Compilation successful
echo.

echo Choose version to run:
echo 1. Console Version
echo 2. GUI Version
echo.
set /p choice="Enter choice (1-2): "

if "%choice%"=="1" (
    echo Starting Console Version...
    echo.
    java card_game.Main
) else if "%choice%"=="2" (
    echo Starting GUI Version...
    echo.
    java card_game.WarGameGUI
) else (
    echo Invalid choice
)

echo.
echo Note: Save/Load functionality requires Jackson JSON libraries.
echo Use .\build.bat for full functionality.
pause