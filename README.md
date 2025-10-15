# Programming Projects Collection

This repository contains a diverse collection of programming projects including Python games, visual animations, and Java applications. Each project demonstrates different programming concepts and technologies.

## 🐍 Python Projects

### Terminal Games
1. **21 Blackjack**
   - A simple implementation of the Blackjack card game. The goal is to get as close to 21 points as possible without going over. The player competes against the dealer.

2. **Rock, Paper, Scissors**
   - A classic game of Rock, Paper, Scissors, where the player competes against the computer. The game continues until the player decides to quit.

3. **Number Guessing Game**
   - In this game, the computer selects a random number, and the player has to guess the number. The player is given hints whether their guess is too high or too low.

### Visual Animations & Shapes
4. **2D Beating Heart** (`shapes/2d_beating_heart.py`)
   - Animated beating heart using ASCII characters with responsive scaling based on window size

5. **2D Beating Strawberry** (`shapes/2d_beating_strawberry.py`)
   - Animated strawberry with seeds and leaves, featuring responsive pixel scaling and beating animation

6. **3D Jellyfish** (`shapes/3d_jellyfish.py`)
   - 3D animated jellyfish visualization

7. **Geometric Figures**
   - Collection of methods to print different geometric shapes (pyramids, squares, rectangles) made of asterisks (`*`):
     - Full pyramids
     - Inverted pyramids
     - Left, right, and center-aligned pyramids
     - Squares and rectangles (filled and hollow)

### Utilities
8. **Password Generator**
   - A utility to generate random passwords with varying lengths and complexities based on user preferences, including lowercase, uppercase letters, numbers, and special characters.

## ☕ Java Projects

### WAR Card Game (`java_card_game/`)
A complete implementation of the WAR card game featuring:

- **Dual Interface**: Both console and GUI versions
- **Game Modes**: Human vs Computer, Human vs Human
- **Save/Load System**: JSON-based game state persistence
- **Complete OOP Design**: Proper class structure with all required components
- **Professional GUI**: Swing-based graphical interface

**Key Features:**
- ✅ Complete WAR game rules implementation
- ✅ War scenario handling (face-down + face-up cards)
- ✅ Save/load functionality with JSON persistence
- ✅ Interactive console and GUI interfaces
- ✅ Robust error handling and input validation

**How to Run:**
```bash
cd java_card_game
./build.sh          # Build the project
./build.sh console  # Run console version
./build.sh gui      # Run GUI version
```

## 🚀 Getting Started

### Python Projects
```bash
# Run any Python game/animation
python3 game_name.py
# or
python3 shapes/animation_name.py
```

### Java Projects
```bash
cd java_card_game
./build.sh
```

## 📁 Project Structure
```
├── README.md
├── python_games/           # Python terminal games
├── shapes/                 # Python visual animations
├── java_card_game/         # Java WAR card game
│   ├── src/               # Java source code
│   ├── lib/               # External libraries
│   ├── build.sh           # Build and run script
│   └── README.md          # Detailed project documentation
└── utilities/             # Various utility programs
```

## 🎯 Learning Objectives

These projects demonstrate:
- **Object-Oriented Programming** (Python & Java)
- **GUI Development** (Tkinter, Swing)
- **Game Logic Implementation**
- **File I/O and Data Persistence**
- **Animation and Graphics Programming**
- **User Interface Design**
- **Error Handling and Validation**

Each project includes comprehensive documentation and follows best practices for code organization and design patterns.
