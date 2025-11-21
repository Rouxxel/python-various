@echo off
REM WAR Card Game - Build and Run Script (Windows)
REM Backend Programming Final Exam Project
REM Prof. Dr. Rand Kouatly, EU University Europe, Summer 2025

setlocal enabledelayedexpansion

REM Project directories
set "SRC_DIR=src"
set "LIB_DIR=lib"
set "BIN_DIR=bin"

REM Create bin directory if it doesn't exist
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

echo.
echo WAR Card Game - Build Script
echo ============================

REM Check if Java is installed
echo Checking Java installation...
java -version >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 8 or higher and try again.
    pause
    exit /b 1
)

javac -version >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Java compiler ^(javac^) is not installed or not in PATH
    echo Please install JDK and try again.
    pause
    exit /b 1
)

echo SUCCESS: Java installation found
echo.

REM Check dependencies
echo Checking dependencies...

if not exist "%LIB_DIR%" mkdir "%LIB_DIR%"

REM Check for Jackson JSON library
if not exist "%LIB_DIR%\jackson-core-2.17.1.jar" (
    echo WARNING: Jackson JSON library not found in lib directory.
    echo Please ensure Jackson JSON libraries are in the lib\ directory:
    echo - jackson-core-2.17.1.jar
    echo - jackson-databind-2.17.1.jar
    echo - jackson-annotations-2.17.1.jar
    echo.
    echo The game will still compile and run, but save/load functionality may not work.
    echo.
) else (
    echo SUCCESS: Jackson JSON libraries found
)

echo.

REM Compile the project
echo Compiling Java source files...

REM Set classpath (Windows uses semicolon)
set "CLASSPATH=%LIB_DIR%\*;%SRC_DIR%"

REM Compile all Java files
javac -cp "%CLASSPATH%" -d "%BIN_DIR%" "%SRC_DIR%\card_game\*.java" "%SRC_DIR%\card_n_deck\*.java" "%SRC_DIR%\players_class\*.java" "%SRC_DIR%\logic_class\*.java"

if errorlevel 1 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

echo SUCCESS: Compilation successful
echo.

REM Handle command line arguments
if "%1"=="console" goto run_console
if "%1"=="gui" goto run_gui
if "%1"=="clean" goto clean_project
if "%1"=="help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--help" goto show_help

REM Show interactive menu
:show_menu
echo Choose how to run the game:
echo 1. Console Version (Text-based interface)
echo 2. GUI Version (Graphical interface)
echo 3. Clean build files
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto run_console
if "%choice%"=="2" goto run_gui
if "%choice%"=="3" goto clean_project
if "%choice%"=="4" goto exit_script

echo Invalid choice. Please try again.
goto show_menu

:run_console
echo Starting WAR Card Game (Console Version)...
echo.
java -cp "%LIB_DIR%\*;%BIN_DIR%" card_game.Main
goto end

:run_gui
echo Starting WAR Card Game (GUI Version)...
echo.
java -cp "%LIB_DIR%\*;%BIN_DIR%" card_game.WarGameGUI
goto end

:clean_project
echo Cleaning build files...
if exist "%BIN_DIR%" rmdir /s /q "%BIN_DIR%"
for /r "%SRC_DIR%" %%f in (*.class) do del "%%f" 2>nul
echo Clean complete
goto end

:show_help
echo Usage: %0 [OPTION]
echo.
echo Options:
echo   (no args)    Build and show menu
echo   console      Build and run console version
echo   gui          Build and run GUI version
echo   clean        Clean build files
echo   help         Show this help message
echo.
echo Examples:
echo   %0           # Build and show interactive menu
echo   %0 console   # Build and run console version directly
echo   %0 gui       # Build and run GUI version directly
echo   %0 clean     # Clean all build files
goto end

:exit_script
echo Goodbye!
goto end

:end
pause