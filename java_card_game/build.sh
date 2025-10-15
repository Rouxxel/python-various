#!/bin/bash

# WAR Card Game - Build and Run Script
# Backend Programming Final Exam Project
# Prof. Dr. Rand Kouatly, EU University Europe, Summer 2025

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SRC_DIR="src"
LIB_DIR="lib"
BIN_DIR="bin"

# Create bin directory if it doesn't exist
mkdir -p $BIN_DIR

echo -e "${BLUE}🃏 WAR Card Game - Build Script 🃏${NC}"
echo "=================================="

# Function to check if Java is installed
check_java() {
    if ! command -v java &> /dev/null; then
        echo -e "${RED}❌ Java is not installed or not in PATH${NC}"
        echo "Please install Java 8 or higher and try again."
        exit 1
    fi
    
    if ! command -v javac &> /dev/null; then
        echo -e "${RED}❌ Java compiler (javac) is not installed or not in PATH${NC}"
        echo "Please install JDK and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Java installation found${NC}"
    java -version
    echo ""
}

# Function to check dependencies
check_dependencies() {
    echo -e "${YELLOW}📦 Checking dependencies...${NC}"
    
    if [ ! -d "$LIB_DIR" ]; then
        echo -e "${YELLOW}⚠️  Creating lib directory...${NC}"
        mkdir -p $LIB_DIR
    fi
    
    # Check for Jackson JSON library
    if [ ! -f "$LIB_DIR/jackson-core-2.15.2.jar" ] || [ ! -f "$LIB_DIR/jackson-databind-2.15.2.jar" ] || [ ! -f "$LIB_DIR/jackson-annotations-2.15.2.jar" ]; then
        echo -e "${YELLOW}⚠️  Jackson JSON library not found. Downloading...${NC}"
        
        # Download Jackson libraries
        curl -L -o "$LIB_DIR/jackson-core-2.15.2.jar" "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.15.2/jackson-core-2.15.2.jar" 2>/dev/null
        curl -L -o "$LIB_DIR/jackson-databind-2.15.2.jar" "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.15.2/jackson-databind-2.15.2.jar" 2>/dev/null
        curl -L -o "$LIB_DIR/jackson-annotations-2.15.2.jar" "https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.15.2/jackson-annotations-2.15.2.jar" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Jackson libraries downloaded successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not download Jackson libraries automatically.${NC}"
            echo "Please download Jackson JSON libraries manually to the lib/ directory:"
            echo "- jackson-core-2.15.2.jar"
            echo "- jackson-databind-2.15.2.jar" 
            echo "- jackson-annotations-2.15.2.jar"
            echo ""
            echo "The game will still compile and run, but save/load functionality may not work."
        fi
    else
        echo -e "${GREEN}✅ Jackson JSON libraries found${NC}"
    fi
    echo ""
}

# Function to compile the project
compile_project() {
    echo -e "${YELLOW}🔨 Compiling Java source files...${NC}"
    
    # Set classpath
    CLASSPATH="$LIB_DIR/*:$SRC_DIR"
    
    # Find all Java files
    JAVA_FILES=$(find $SRC_DIR -name "*.java")
    
    if [ -z "$JAVA_FILES" ]; then
        echo -e "${RED}❌ No Java source files found in $SRC_DIR${NC}"
        exit 1
    fi
    
    # Compile all Java files
    javac -cp "$CLASSPATH" -d $BIN_DIR $JAVA_FILES
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Compilation successful${NC}"
        echo ""
    else
        echo -e "${RED}❌ Compilation failed${NC}"
        exit 1
    fi
}

# Function to run console version
run_console() {
    echo -e "${BLUE}🎮 Starting WAR Card Game (Console Version)...${NC}"
    echo ""
    java -cp "$LIB_DIR/*:$BIN_DIR" card_game.Main
}

# Function to run GUI version
run_gui() {
    echo -e "${BLUE}🎮 Starting WAR Card Game (GUI Version)...${NC}"
    echo ""
    java -cp "$LIB_DIR/*:$BIN_DIR" card_game.WarGameGUI
}

# Function to clean build files
clean_project() {
    echo -e "${YELLOW}🧹 Cleaning build files...${NC}"
    rm -rf $BIN_DIR
    find $SRC_DIR -name "*.class" -delete
    echo -e "${GREEN}✅ Clean complete${NC}"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  (no args)    Build and show menu"
    echo "  console      Build and run console version"
    echo "  gui          Build and run GUI version"
    echo "  clean        Clean build files"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Build and show interactive menu"
    echo "  $0 console   # Build and run console version directly"
    echo "  $0 gui       # Build and run GUI version directly"
    echo "  $0 clean     # Clean all build files"
}

# Function to show interactive menu
show_menu() {
    echo -e "${BLUE}🎯 Choose how to run the game:${NC}"
    echo "1. Console Version (Text-based interface)"
    echo "2. GUI Version (Graphical interface)"
    echo "3. Clean build files"
    echo "4. Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            run_console
            ;;
        2)
            run_gui
            ;;
        3)
            clean_project
            ;;
        4)
            echo -e "${GREEN}Goodbye! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            show_menu
            ;;
    esac
}

# Main script logic
case "$1" in
    "console")
        check_java
        check_dependencies
        compile_project
        run_console
        ;;
    "gui")
        check_java
        check_dependencies
        compile_project
        run_gui
        ;;
    "clean")
        clean_project
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        check_java
        check_dependencies
        compile_project
        show_menu
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_help
        exit 1
