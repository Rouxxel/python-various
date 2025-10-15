package card_n_deck;

import java.io.File;
import com.fasterxml.jackson.databind.ObjectMapper;

public class Card_config_loader {
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        // Use the correct file name
        CardData cardData = mapper.readValue(new File("src/card_n_deck/card_config_info.json"), CardData.class);

        System.out.println("Suits: " + cardData.getSuits());
        System.out.println("Rank of Ace: " + cardData.getRanks().get("Ace"));
    }
}
