package logic_class;

import card_n_deck.*;
import players_class.Player;
import java.util.*;

public class WarGame {
    private Player player1;
    private Player player2;
    private int roundNumber;
    private boolean gameOver;
    private Player winner;
    private Scanner scanner;
    
    // Constructor
    public WarGame() {
        this.roundNumber = 0;
        this.gameOver = false;
        this.scanner = new Scanner(System.in);
    }
    
    public WarGame(Player player1, Player player2, int roundNumber) {
        this.player1 = player1;
        this.player2 = player2;
        this.roundNumber = roundNumber;
        this.gameOver = false;
        this.scanner = new Scanner(System.in);
    }
    
    // Initialize new game
    public void initializeGame(String player1Name, boolean vsComputer) {
        // Create players
        this.player1 = new Player(player1Name, 1, false);
        this.player2 = new Player(vsComputer ? "Computer" : "Player 2", 2, vsComputer);
        
        // Create and shuffle deck
        Deck deck = new Deck();
        
        // Deal cards evenly
        dealCards(deck);
        
        System.out.println("Game initialized!");
        System.out.println(player1.getName() + " has " + player1.getHandSize() + " cards");
        System.out.println(player2.getName() + " has " + player2.getHandSize() + " cards");
    }
    
    private void dealCards(Deck deck) {
        boolean dealToPlayer1 = true;
        while (deck.size() > 0) {
            Card card = deck.drawCard();
            if (card != null) {
                if (dealToPlayer1) {
                    player1.addCard(card);
                } else {
                    player2.addCard(card);
                }
                dealToPlayer1 = !dealToPlayer1;
            }
        }
    }
    
    // Play one round
    public void playRound() {
        if (gameOver) return;
        
        roundNumber++;
        System.out.println("\n=== Round " + roundNumber + " ===");
        
        // Check if players have cards
        if (!player1.hasCards()) {
            endGame(player2);
            return;
        }
        if (!player2.hasCards()) {
            endGame(player1);
            return;
        }
        
        // Play cards
        Card card1 = player1.playCard();
        Card card2 = player2.playCard();
        
        System.out.println(player1.getName() + " plays: " + card1.get_card_face() + " (" + card1.get_card_value() + ")");
        System.out.println(player2.getName() + " plays: " + card2.get_card_face() + " (" + card2.get_card_value() + ")");
        
        List<Card> cardsOnTable = new ArrayList<>();
        cardsOnTable.add(card1);
        cardsOnTable.add(card2);
        
        // Compare cards
        if (card1.get_card_value() > card2.get_card_value()) {
            System.out.println(player1.getName() + " wins the round!");
            player1.addCards(cardsOnTable);
        } else if (card2.get_card_value() > card1.get_card_value()) {
            System.out.println(player2.getName() + " wins the round!");
            player2.addCards(cardsOnTable);
        } else {
            System.out.println("WAR! Cards are equal!");
            handleWar(cardsOnTable);
        }
        
        // Show current status
        System.out.println(player1.getName() + ": " + player1.getHandSize() + " cards");
        System.out.println(player2.getName() + ": " + player2.getHandSize() + " cards");
    }
    
    private void handleWar(List<Card> cardsOnTable) {
        System.out.println("Starting WAR sequence...");
        
        // Each player puts down 2 face-down cards and 1 face-up
        for (int i = 0; i < 2; i++) {
            if (player1.hasCards()) {
                Card faceDown1 = player1.playCard();
                cardsOnTable.add(faceDown1);
                System.out.println(player1.getName() + " places a face-down card");
            }
            if (player2.hasCards()) {
                Card faceDown2 = player2.playCard();
                cardsOnTable.add(faceDown2);
                System.out.println(player2.getName() + " places a face-down card");
            }
        }
        
        // Check if players still have cards for face-up battle
        if (!player1.hasCards()) {
            System.out.println(player1.getName() + " runs out of cards during war!");
            endGame(player2);
            return;
        }
        if (!player2.hasCards()) {
            System.out.println(player2.getName() + " runs out of cards during war!");
            endGame(player1);
            return;
        }
        
        // Face-up cards
        Card warCard1 = player1.playCard();
        Card warCard2 = player2.playCard();
        cardsOnTable.add(warCard1);
        cardsOnTable.add(warCard2);
        
        System.out.println(player1.getName() + " war card: " + warCard1.get_card_face() + " (" + warCard1.get_card_value() + ")");
        System.out.println(player2.getName() + " war card: " + warCard2.get_card_face() + " (" + warCard2.get_card_value() + ")");
        
        // Compare war cards
        if (warCard1.get_card_value() > warCard2.get_card_value()) {
            System.out.println(player1.getName() + " wins the WAR!");
            player1.addCards(cardsOnTable);
        } else if (warCard2.get_card_value() > warCard1.get_card_value()) {
            System.out.println(player2.getName() + " wins the WAR!");
            player2.addCards(cardsOnTable);
        } else {
            System.out.println("Another WAR!");
            handleWar(cardsOnTable); // Recursive war
        }
    }
    
    private void endGame(Player winner) {
        this.gameOver = true;
        this.winner = winner;
        System.out.println("\n🎉 GAME OVER! 🎉");
        System.out.println(winner.getName() + " wins the game!");
        System.out.println("Total rounds played: " + roundNumber);
    }
    
    // Save game
    public void saveGame(String filename) {
        GameSave save = new GameSave(player1, player2, roundNumber);
        save.saveToFile(filename);
    }
    
    // Load game
    public boolean loadGame(String filename) {
        GameSave save = GameSave.loadFromFile(filename);
        if (save != null) {
            Player[] players = save.restorePlayers();
            this.player1 = players[0];
            this.player2 = players[1];
            this.roundNumber = save.getGameRound();
            this.gameOver = false;
            System.out.println("Game loaded successfully!");
            save.printInfo();
            return true;
        }
        return false;
    }
    
    // Getters
    public Player getPlayer1() { return player1; }
    public Player getPlayer2() { return player2; }
    public int getRoundNumber() { return roundNumber; }
    public boolean isGameOver() { return gameOver; }
    public Player getWinner() { return winner; }
    
    // Print game info
    public void printGameInfo() {
        System.out.println("\n=== Game Status ===");
        if (player1 != null) player1.printInfo();
        if (player2 != null) player2.printInfo();
        System.out.println("Round: " + roundNumber);
        System.out.println("Game Over: " + gameOver);
        if (winner != null) System.out.println("Winner: " + winner.getName());
    }
}