package card_n_deck;

import java.util.List;
import java.util.Map;

public class CardData {
    private List<String> suits;
    private Map<String, Integer> ranks;

    //Getters and setters
    public List<String> getSuits() {
        return suits;
    }

    public void setSuits(List<String> suits) {
        this.suits = suits;
    }

    public Map<String, Integer> getRanks() {
        return ranks;
    }

    public void setRanks(Map<String, Integer> ranks) {
        this.ranks = ranks;
    }
}
