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

## 🌐 Templates

### REST API Template (`templates/rest_api_template/`)
A production-ready FastAPI template for building scalable REST APIs featuring:

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Rate Limiting**: Built-in request rate limiting with SlowAPI
- **Comprehensive Logging**: File and console logging with configurable levels
- **Security Features**: Non-root Docker user, input validation, encryption utilities
- **Configuration Management**: JSON-based configuration system
- **Health Checks**: Built-in health check endpoints and Docker health monitoring
- **Development Ready**: Hot reload support and development scripts

**Quick Start:**
```bash
cd templates/rest_api_template
./start.sh          # Linux/Mac
# or
start.bat           # Windows
# or
docker-compose up --build
```

### GraphQL API Template (`templates/graphql_template/`)
A production-ready GraphQL API template built with FastAPI and Strawberry GraphQL featuring:

- **Strawberry GraphQL**: Modern, type-safe GraphQL library for Python
- **FastAPI Integration**: Seamless integration with FastAPI framework
- **GraphiQL Interface**: Interactive GraphQL query interface for development
- **Type Safety**: Full type safety with Python type hints and Strawberry
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Rate Limiting**: Built-in request rate limiting for GraphQL endpoints
- **Schema Introspection**: Auto-generated documentation from Python types
- **Comprehensive Logging**: File and console logging with GraphQL query tracking
- **Security Features**: Input validation, rate limiting, non-root Docker user

**Quick Start:**
```bash
cd templates/graphql_template
./start.sh          # Linux/Mac
# or
start.bat           # Windows
# or
docker-compose up --build
```

**GraphQL Endpoints:**
- GraphQL API: http://localhost:8000/graphql
- GraphiQL Interface: http://localhost:8000/graphql
- Health Check: http://localhost:8000/health

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
├── templates/             # Project templates
│   ├── rest_api_template/ # FastAPI REST API template
│   │   ├── src/          # API source code
│   │   ├── DOCKERFILE    # Docker configuration
│   │   ├── docker-compose.yml
│   │   ├── start.sh      # Development startup script
│   │   └── README.md     # Template documentation
│   └── graphql_template/  # FastAPI + Strawberry GraphQL template
│       ├── src/          # GraphQL API source code
│       │   ├── graphql_schema/ # Schema definitions
│       │   ├── resolvers/     # Query/Mutation resolvers
│       │   ├── types/         # GraphQL types
│       │   └── utils/         # Utility modules
│       ├── DOCKERFILE    # Docker configuration
│       ├── docker-compose.yml
│       ├── start.sh      # Development startup script
│       └── README.md     # Template documentation
└── utilities/             # Various utility programs
```

## 🎯 Learning Objectives

These projects demonstrate:
- **Object-Oriented Programming** (Python & Java)
- **GUI Development** (Tkinter, Swing)
- **Web API Development** (FastAPI, REST APIs)
- **Containerization** (Docker, Docker Compose)
- **Game Logic Implementation**
- **File I/O and Data Persistence**
- **Animation and Graphics Programming**
- **User Interface Design**
- **Error Handling and Validation**
- **Production Deployment** (Multi-stage Docker builds)
- **Security Best Practices** (Rate limiting, input validation)

Each project includes comprehensive documentation and follows best practices for code organization and design patterns.
