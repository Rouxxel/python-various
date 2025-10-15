package logic_class;

import players_class.Player;
import card_n_deck.Card;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.io.*;
import java.util.*;

public class GameSave {
    @JsonProperty("player1Name")
    private String player1Name;
    
    @JsonProperty("player2Name") 
    private String player2Name;
    
    @JsonProperty("player1Cards")
    private List<SavedCard> player1Cards;
    
    @JsonProperty("player2Cards")
    private List<SavedCard> player2Cards;
    
    @JsonProperty("gameRound")
    private int gameRound;
    
    @JsonProperty("saveDate")
    private String saveDate;
    
    // Default constructor for Jackson
    public GameSave() {
        this.player1Cards = new ArrayList<>();
        this.player2Cards = new ArrayList<>();
    }
    
    // Constructor
    public GameSave(Player player1, Player player2, int gameRound) {
        this.player1Name = player1.getName();
        this.player2Name = player2.getName();
        this.gameRound = gameRound;
        this.saveDate = new Date().toString();
        
        this.player1Cards = new ArrayList<>();
        for (Card card : player1.getHand()) {
            this.player1Cards.add(new SavedCard(card.get_card_face(), card.get_card_value()));
        }
        
        this.player2Cards = new ArrayList<>();
        for (Card card : player2.getHand()) {
            this.player2Cards.add(new SavedCard(card.get_card_face(), card.get_card_value()));
        }
    }
    
    // Save game to file
    public void saveToFile(String filename) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            mapper.writeValue(new File(filename), this);
            System.out.println("Game saved successfully to " + filename);
        } catch (IOException e) {
            System.err.println("Error saving game: " + e.getMessage());
        }
    }
    
    // Load game from file
    public static GameSave loadFromFile(String filename) {
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.readValue(new File(filename), GameSave.class);
        } catch (IOException e) {
            System.err.println("Error loading game: " + e.getMessage());
            return null;
        }
    }
    
    // Convert back to players
    public Player[] restorePlayers() {
        Player player1 = new Player(player1Name, 1, false);
        Player player2 = new Player(player2Name, 2, player2Name.equals("Computer"));
        
        for (SavedCard savedCard : player1Cards) {
            player1.addCard(new Card(savedCard.getFace(), savedCard.getValue()));
        }
        
        for (SavedCard savedCard : player2Cards) {
            player2.addCard(new Card(savedCard.getFace(), savedCard.getValue()));
        }
        
        return new Player[]{player1, player2};
    }
    
    // Getters and Setters
    public String getPlayer1Name() { return player1Name; }
    public void setPlayer1Name(String player1Name) { this.player1Name = player1Name; }
    
    public String getPlayer2Name() { return player2Name; }
    public void setPlayer2Name(String player2Name) { this.player2Name = player2Name; }
    
    public List<SavedCard> getPlayer1Cards() { return player1Cards; }
    public void setPlayer1Cards(List<SavedCard> player1Cards) { this.player1Cards = player1Cards; }
    
    public List<SavedCard> getPlayer2Cards() { return player2Cards; }
    public void setPlayer2Cards(List<SavedCard> player2Cards) { this.player2Cards = player2Cards; }
    
    public int getGameRound() { return gameRound; }
    public void setGameRound(int gameRound) { this.gameRound = gameRound; }
    
    public String getSaveDate() { return saveDate; }
    public void setSaveDate(String saveDate) { this.saveDate = saveDate; }
    
    // Print info
    public void printInfo() {
        System.out.println("=== Saved Game Info ===");
        System.out.println("Player 1: " + player1Name + " (" + player1Cards.size() + " cards)");
        System.out.println("Player 2: " + player2Name + " (" + player2Cards.size() + " cards)");
        System.out.println("Round: " + gameRound);
        System.out.println("Save Date: " + saveDate);
    }
    
    // Inner class for saved cards
    public static class SavedCard {
        @JsonProperty("face")
        private String face;
        
        @JsonProperty("value")
        private int value;
        
        public SavedCard() {} // Default constructor for Jackson
        
        public SavedCard(String face, int value) {
            this.face = face;
            this.value = value;
        }
        
        public String getFace() { return face; }
        public void setFace(String face) { this.face = face; }
        
        public int getValue() { return value; }
        public void setValue(int value) { this.value = value; }
    }
}