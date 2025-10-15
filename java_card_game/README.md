# WAR Card Game - Java Implementation
## 🎯 Project Overview

This is a complete implementation of the WAR card game in Java with both console and GUI interfaces. The game supports human vs computer and human vs human gameplay, with save/load functionality to continue games later.

## 🃏 Game Rules

**Objective:** Win all 52 cards!

**How to Play:**
1. The deck is divided evenly between two players (26 cards each)
2. Each round, both players reveal their top card simultaneously
3. The player with the higher card wins both cards and adds them to their deck
4. Aces are high (value 14), suits are ignored

**WAR Rules:**
- If both cards have equal value, a "WAR" occurs
- Each player places 2 cards face-down, then 1 card face-up
- The player with the higher face-up card wins all cards on the table
- If face-up cards are equal, the war continues with more cards
- If a player runs out of cards during a war, they lose immediately

**Winning:** The game continues until one player has all 52 cards

## 🏗️ Project Structure

```
java_card_game/
├── src/
│   ├── card_game/           # Main application package
│   │   ├── Main.java        # Console version entry point
│   │   └── WarGameGUI.java  # GUI version entry point
│   ├── card_n_deck/         # Card and deck management
│   │   ├── Card.java        # Card class with face and value
│   │   ├── Deck.java        # Deck class with shuffle/deal functionality
│   │   ├── CardData.java    # JSON data structure for cards
│   │   ├── Card_config_loader.java  # Configuration loader
│   │   └── card_config_info.json   # Card definitions
│   ├── players_class/       # Player management
│   │   └── Player.java      # Player class (human/computer)
│   ├── logic_class/         # Game logic and save system
│   │   ├── WarGame.java     # Main game logic
│   │   └── GameSave.java    # Save/load functionality
│   └── resources/           # Game resources
└── lib/                     # External libraries (Jackson JSON)
```

## 🔧 Technical Implementation

### Object-Oriented Design
- **Card Class:** Represents individual playing cards with face and value
- **Player Class:** Manages player information, hand, and game actions
- **Deck Class:** Handles card deck creation, shuffling, and dealing
- **WarGame Class:** Contains all game logic and rules implementation
- **GameSave Class:** Manages game state persistence

### Key Features
✅ **Complete OOP Design** - All classes have constructors, getters/setters, and print methods  
✅ **Two Game Modes** - Human vs Computer, Human vs Human  
✅ **Save/Load System** - JSON-based game state persistence  
✅ **Dual Interface** - Both console and GUI versions  
✅ **War Logic** - Complete implementation of war scenarios  
✅ **Input Validation** - Robust error handling  
✅ **Game Statistics** - Round counting and game progress tracking

## 🚀 How to Run

### Prerequisites
- Java 8 or higher
- Jackson JSON library (included in lib/ folder)

### Console Version

**Windows:**
```cmd
cd java_card_game
javac -cp "lib/*;src" src/card_game/*.java src/card_n_deck/*.java src/players_class/*.java src/logic_class/*.java
java -cp "lib/*;src" card_game.Main
```

**Linux/Mac:**
```bash
cd java_card_game
javac -cp "lib/*:src" src/card_game/*.java src/card_n_deck/*.java src/players_class/*.java src/logic_class/*.java
java -cp "lib/*:src" card_game.Main
```

### GUI Version

**Windows:**
```cmd
cd java_card_game
javac -cp "lib/*;src" src/card_game/*.java src/card_n_deck/*.java src/players_class/*.java src/logic_class/*.java
java -cp "lib/*;src" card_game.WarGameGUI
```

**Linux/Mac:**
```bash
cd java_card_game
javac -cp "lib/*:src" src/card_game/*.java src/card_n_deck/*.java src/players_class/*.java src/logic_class/*.java
java -cp "lib/*:src" card_game.WarGameGUI
```

### Using the Build Script

**Linux/Mac:**
```bash
cd java_card_game
chmod +x build.sh
./build.sh
```

**Windows:**
```cmd
cd java_card_game
.\build.bat
```

**Build Script Options:**
- `./build.sh` or `build.bat` - Interactive menu
- `./build.sh console` or `build.bat console` - Run console version directly
- `./build.sh gui` or `build.bat gui` - Run GUI version directly
- `./build.sh clean` or `build.bat clean` - Clean build files

## 🎮 Gameplay Features

### Console Interface
- Interactive menu system
- Step-by-step round progression
- Game rules display
- Save/load with custom filenames
- Real-time game statistics

### GUI Interface
- User-friendly graphical interface
- Visual game status display
- File dialog for save/load operations
- Game log with complete history
- Intuitive button controls

### Save System
- JSON-based save files
- Preserves complete game state
- Player names and card hands
- Current round number
- Save date/time tracking

## 📋 Class Details

### Card Class
```java
- String card_face (e.g., "Ace of Spades")
- int card_value (2-14, Ace=14)
- Constructors, getters/setters
- printInfo(), toString(), equals() methods
```

### Player Class
```java
- String name, int id, boolean isComputer
- List<Card> hand
- Methods: addCard(), playCard(), hasCards()
- printInfo(), printHand() methods
```

### WarGame Class
```java
- Complete war game logic
- Round management
- War scenario handling
- Game state tracking
- Save/load integration
```

### GameSave Class
```java
- JSON serialization/deserialization
- Game state preservation
- Player hand restoration
- File I/O operations
```

## 🎯 Requirements Compliance

✅ **Package Structure:** Multiple packages (card_game, card_n_deck, players_class, logic_class)  
✅ **OOP Design:** All classes follow OOP principles  
✅ **Required Classes:** Card, Player (User), Save classes implemented  
✅ **Class Components:** All classes have constructors, getters/setters, print methods  
✅ **Save Functionality:** Complete save/load system with JSON persistence  
✅ **GUI Interface:** Swing-based graphical user interface  
✅ **Game Logic:** Complete WAR game implementation with all rules

## 🔄 Game Flow

1. **Start:** Choose console or GUI version
2. **Setup:** Enter player name, select game mode
3. **Play:** Click/select "Play Round" to battle
4. **War:** Automatic handling of equal card scenarios
5. **Save:** Save game progress at any time
6. **Load:** Resume saved games
7. **Win:** Game ends when one player has all cards

## 📁 Save File Format

Save files are stored in JSON format with complete game state:
```json
{
  "player1Name": "Alice",
  "player2Name": "Computer", 
  "player1Cards": [...],
  "player2Cards": [...],
  "gameRound": 15,
  "saveDate": "..."
}
```

This implementation provides a complete, professional-grade card game with all requested features and follows best practices for Java development.