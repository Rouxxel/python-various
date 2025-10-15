package card_n_deck;

import java.util.*;
import java.io.File;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Deck {
    private List<Card> cards;

    public Deck() {
        cards = new ArrayList<>();
        loadDeckFromConfig();
    }

    private void loadDeckFromConfig() {
        try {
            ObjectMapper mapper = new ObjectMapper();
            CardData data = mapper.readValue(new File("src/card_n_deck/card_config_info.json"), CardData.class);

            for (String suit : data.getSuits()) {
                for (Map.Entry<String, Integer> rank : data.getRanks().entrySet()) {
                    String cardFace = rank.getKey() + " of " + suit;
                    cards.add(new Card(cardFace, rank.getValue()));
                }
            }
            shuffle();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void shuffle() {
        Collections.shuffle(cards);
    }

    public Card drawCard() {
        if (cards.isEmpty()) return null;
        return cards.remove(0);
    }

    public int size() {
        return cards.size();
    }

    public void printDeck() {
        for (Card c : cards) {
            System.out.println(c.get_card_face() + " (" + c.get_card_value() + ")");
        }
    }
}
