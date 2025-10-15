package card_game;

import logic_class.WarGame;
import players_class.Player;
import java.util.Scanner;

public class Main {
    private static Scanner scanner = new Scanner(System.in);
    private static WarGame game = new WarGame();
    
    public static void main(String[] args) {
        System.out.println("🃏 Welcome to WAR Card Game! 🃏");
        System.out.println("================================");
        
        showMainMenu();
    }
    
    private static void showMainMenu() {
        while (true) {
            System.out.println("\n=== MAIN MENU ===");
            System.out.println("1. New Game");
            System.out.println("2. Load Game");
            System.out.println("3. Game Rules");
            System.out.println("4. Exit");
            System.out.print("Choose an option (1-4): ");
            
            int choice = getIntInput();
            
            switch (choice) {
                case 1:
                    startNewGame();
                    break;
                case 2:
                    loadGame();
                    break;
                case 3:
                    showGameRules();
                    break;
                case 4:
                    System.out.println("Thanks for playing! Goodbye! 👋");
                    System.exit(0);
                    break;
                default:
                    System.out.println("Invalid option. Please try again.");
            }
        }
    }
    
    private static void startNewGame() {
        System.out.println("\n=== NEW GAME SETUP ===");
        System.out.print("Enter your name: ");
        String playerName = scanner.nextLine();
        
        System.out.println("Choose game mode:");
        System.out.println("1. vs Computer");
        System.out.println("2. vs Another Player");
        System.out.print("Choose (1-2): ");
        
        int mode = getIntInput();
        boolean vsComputer = (mode == 1);
        
        game.initializeGame(playerName, vsComputer);
        playGame();
    }
    
    private static void playGame() {
        while (!game.isGameOver()) {
            System.out.println("\n=== GAME OPTIONS ===");
            System.out.println("1. Play Next Round");
            System.out.println("2. Save Game");
            System.out.println("3. View Game Status");
            System.out.println("4. Return to Main Menu");
            System.out.print("Choose an option (1-4): ");
            
            int choice = getIntInput();
            
            switch (choice) {
                case 1:
                    game.playRound();
                    if (game.isGameOver()) {
                        System.out.println("\nWould you like to start a new game? (y/n): ");
                        String response = scanner.nextLine();
                        if (response.toLowerCase().startsWith("y")) {
                            game = new WarGame(); // Reset game
                            startNewGame();
                        } else {
                            return;
                        }
                    }
                    break;
                case 2:
                    saveGame();
                    break;
                case 3:
                    game.printGameInfo();
                    break;
                case 4:
                    return;
                default:
                    System.out.println("Invalid option. Please try again.");
            }
        }
    }
    
    private static void saveGame() {
        System.out.print("Enter filename to save (without extension): ");
        String filename = scanner.nextLine() + ".json";
        game.saveGame(filename);
    }
    
    private static void loadGame() {
        System.out.print("Enter filename to load (without extension): ");
        String filename = scanner.nextLine() + ".json";
        
        if (game.loadGame(filename)) {
            playGame();
        } else {
            System.out.println("Failed to load game. File might not exist or be corrupted.");
        }
    }
    
    private static void showGameRules() {
        System.out.println("\n🃏 WAR CARD GAME RULES 🃏");
        System.out.println("========================");
        System.out.println("OBJECTIVE: Win all the cards!");
        System.out.println();
        System.out.println("HOW TO PLAY:");
        System.out.println("1. The deck is divided evenly between players");
        System.out.println("2. Each round, both players reveal their top card");
        System.out.println("3. The player with the higher card wins both cards");
        System.out.println("4. Aces are high (value 14), suits are ignored");
        System.out.println();
        System.out.println("WAR RULES:");
        System.out.println("• If cards are equal, there's a WAR!");
        System.out.println("• Each player places 2 cards face-down, then 1 face-up");
        System.out.println("• The higher face-up card wins all cards on the table");
        System.out.println("• If face-up cards are equal, repeat the war process");
        System.out.println("• If a player runs out of cards during war, they lose");
        System.out.println();
        System.out.println("WINNING:");
        System.out.println("• The game continues until one player has all 52 cards");
        System.out.println();
        System.out.println("CARD VALUES (High to Low):");
        System.out.println("Ace(14) > King(13) > Queen(12) > Jack(11) > 10 > 9 > ... > 2");
        
        System.out.println("\nPress Enter to return to main menu...");
        scanner.nextLine();
    }
    
    private static int getIntInput() {
        while (true) {
            try {
                String input = scanner.nextLine();
                return Integer.parseInt(input);
            } catch (NumberFormatException e) {
                System.out.print("Please enter a valid number: ");
            }
        }
    }
}
