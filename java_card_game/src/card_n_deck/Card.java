package card_n_deck;

public class Card {
    private String card_face;
    private int card_value;

    public Card(String card_face, int card_value){
        this.card_face = card_face;
        this.card_value = card_value;
    }

    //setters and getters
    public String get_card_face(){
        return this.card_face;
    }
    public void set_card_face(String new_card_face){
        this.card_face = new_card_face;
    }

    public int get_card_value(){
        return this.card_value;
    }
    public void set_card_value(int new_card_value){
        this.card_value = new_card_value;
    }

    // Print info method
    public void printInfo() {
        System.out.println("Card: " + card_face + " (Value: " + card_value + ")");
    }
    
    // toString method for better display
    @Override
    public String toString() {
        return card_face + " (" + card_value + ")";
    }
    
    // equals method for comparison
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Card card = (Card) obj;
        return card_value == card.card_value && card_face.equals(card.card_face);
    }
}
