package players_class;

import card_n_deck.Card;
import java.util.*;

public class Player {
    private String name;
    private int id;
    private List<Card> hand;
    private boolean isComputer;
    
    // Constructors
    public Player(String name, int id, boolean isComputer) {
        this.name = name;
        this.id = id;
        this.isComputer = isComputer;
        this.hand = new ArrayList<>();
    }
    
    public Player(String name, int id) {
        this(name, id, false);
    }
    
    // Getters and Setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    public List<Card> getHand() {
        return hand;
    }
    
    public void setHand(List<Card> hand) {
        this.hand = hand;
    }
    
    public boolean isComputer() {
        return isComputer;
    }
    
    public void setComputer(boolean isComputer) {
        this.isComputer = isComputer;
    }
    
    // Game methods
    public void addCard(Card card) {
        hand.add(card);
    }
    
    public void addCards(List<Card> cards) {
        hand.addAll(cards);
    }
    
    public Card playCard() {
        if (hand.isEmpty()) return null;
        return hand.remove(0);
    }
    
    public int getHandSize() {
        return hand.size();
    }
    
    public boolean hasCards() {
        return !hand.isEmpty();
    }
    
    // Print info
    public void printInfo() {
        System.out.println("Player: " + name + " (ID: " + id + ")");
        System.out.println("Type: " + (isComputer ? "Computer" : "Human"));
        System.out.println("Cards in hand: " + hand.size());
    }
    
    public void printHand() {
        System.out.println(name + "'s hand:");
        for (int i = 0; i < hand.size(); i++) {
            Card card = hand.get(i);
            System.out.println((i + 1) + ". " + card.get_card_face() + " (" + card.get_card_value() + ")");
        }
    }
}