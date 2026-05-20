#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21 black jack game
Console game to play 21 black jack against the CPU only
Can be broken down in several files, maybe will be done in the future
"""

import random
import sys
import logging

"""LOGGING SETUP"""
logger = logging.getLogger("blackjack_game")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("blackjack_game_log.log")
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

"""CLASSES"""
class Deck:
    """
    A class representing a deck of cards used in the game of Blackjack.
    
    Attributes:
        __suits (list): A list of the four suits in a deck: "Spades", "Hearts", "Diamonds", "Clubs".
        __ranks (dict): A dictionary mapping card ranks to their corresponding values.
        dealt_cards (list): A list of cards that have been dealt already so they are not repeated.
    
    Methods:
        add_to_dealt_cards(given_card): Adds a given card (string) to the list of dealt cards.
        generate_card(): Generates a random card from the deck, ensuring no duplicate cards are dealt.
        display_dealt_cards(): Displays all the cards that have been dealt so far.
    """
    def __init__(self):
        self.__suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        self.__ranks = {"Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6,
                        "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, 
                        "Queen": 10, "King": 10}
        self.dealt_cards = []

    def add_to_dealt_cards(self, given_card):
        """Adds a given card to the list of dealt cards."""
        logger.debug(f"Adding {given_card} to dealt_cards list")
        self.dealt_cards.append(given_card)

    def generate_card(self):
        """
        Generates a random card from the deck.
        
        Ensures that the card has not been dealt already by checking
        self.dealt_cards.
        
        Returns:
            final_card (dict): A dict containing the card's face (rank and suit) as key and its 
            corresponding value as the value.
        """
        while True:
            #Select random suit and rank
            sel_suit = random.choice(self.__suits)
            sel_rank = random.choice(list(self.__ranks.keys()))

            #Create the card face
            card_face = sel_rank + " of " + sel_suit
            logger.debug(f"Created card face is {card_face}")

            #Check if card has already been dealt
            if card_face not in self.dealt_cards:
                logger.debug(f"Card has not been dealt yet")
                self.add_to_dealt_cards(card_face)
                def_value = self.__ranks[sel_rank]
                break  #Break out of the loop if it's a unique card
            else:
                logger.debug(f"Card has been dealt already, re-doing")
                continue

        #Create and return final card as dictionary
        final_card = {card_face: def_value}
        logger.info(f"Final card is {final_card}")
        return final_card

    def display_dealt_cards(self):
        """
        Displays all the cards that have been dealt so far.
        
        If no cards have been dealt, informs the user that no cards have been dealt yet.
        """
        logger.info("Displaying current session dealt cards")
        logger.info(f"{self.dealt_cards}")
        print("Dealt cards so far are: ")
        if not self.dealt_cards:
            print("No cards dealt so far")
            return
            
        for i, card_dict in enumerate(self.dealt_cards):    
            if i == len(self.dealt_cards) - 1:
                print(next(iter(card_dict)), ".", end="")
            else:
                print(next(iter(card_dict)), ",", end="")

class Dealer:
    """
    A class representing the dealer in the Blackjack game (CPU).
    
    Attributes:
        current_hand (list): A list of the cards held by the dealer.
        name (str): The name of the dealer.
        total_val (int): The total value of the dealer's hand.
    
    Methods:
        calculate_hand(): Calculates the total value of the dealer's hand.
        hit(new_card): Adds a new card to the dealer's hand and recalculates the hand value.
    """
    def __init__(self, current_hand=[], name="John Doe", total_val=0):
        self.current_hand = current_hand
        self.name = name
        self.total_val = total_val
        
    def calculate_hand(self):
        """
        Calculates the total value of the dealer's hand.
        
        If the hand contains an Ace and the total exceeds 21, it adjusts the value of Ace to be 1 instead of 11.
        
        Returns:
            total_val (int): The total value of the dealer's hand.
        """
        try:
            logger.debug(f"Calculating dealer's hand")
            self.total_val = sum(next(iter(each_card.values())) for each_card in self.current_hand)
            
            #Account for ace dynamic value
            if any("Ace" in next(iter(each_card)) for each_card in self.current_hand) and self.total_val > 21:
                self.total_val = self.total_val - 10
            logger.info(f"Dealer's hand total value: {self.total_val}")
            return self.total_val
        except Exception as e:
            logger.error(f"Error occurred calculating dealer's hand: {e}")
            sys.exit(1)
    
    def hit(self, new_card):
        """
        Adds a new card to the dealer's hand and recalculates the hand's total value.
        
        Args:
            new_card (list): The card to be added to the dealer's hand.
        """
        logger.debug(f"Adding {new_card} to Dealer's hand")
        self.current_hand.append(new_card)
        #Recalculate hand
        self.calculate_hand()

class Player:
    """
    A class representing the player in the Blackjack game.
    
    Attributes:
        current_hand (list): A list of the cards held by the player.
        name (str): The name of the player.
        total_val (int): The total value of the player's hand.
        hit_count (int): The number of times the player has hit.
        double_down (bool): Whether the player has chosen to double down.
    
    Methods:
        calculate_hand(): Calculates the total value of the player's hand.
        hit(new_card): Adds a new card to the player's hand and recalculates the hand value.
        doubling_down(new_card): Adds a new card to the player's hand as part of a double down move and recalculates the hand value.
        stand(): Ends the player's turn and displays their final hand.
        surrender(): The player surrenders and forfeits half their bet.
    """
    def __init__(self, current_hand=[], name="Player", total_val=0, hit_count=0, double_down=False):
        self.current_hand = current_hand
        self.name = name
        self.total_val = total_val
        self.hit_count = hit_count
        self.double_down = double_down
        
    def calculate_hand(self):
        """
        Calculates the total value of the player's hand.
        
        If the hand contains an Ace and the total exceeds 21, it adjusts the value of Ace to be 1 instead of 11.
        
        Returns:
            total_val (int): The total value of the player's hand.
        """
        try:
            logger.debug(f"Calculating {self.name}'s hand")
            self.total_val = sum(next(iter(each_card.values())) for each_card in self.current_hand)

            if any("Ace" in next(iter(each_card)) for each_card in self.current_hand) and self.total_val > 21:
                self.total_val = self.total_val - 10
            logger.info(f"{self.name}'s hand total value: {self.total_val}")
            return self.total_val
        except Exception as e:
            logger.error(f"Error occurred calculating {self.name}'s hand: {e}")
            sys.exit(1)
    
    def hit(self, new_card):
        """
        Adds a new card to the player's hand and recalculates the hand's total value.
        
        Args:
            new_card (list): The card to be added to the player's hand.
        """
        logger.debug(f"Adding {new_card} to {self.name}'s hand")
        self.hit_count += 1
        self.current_hand.append(new_card)
        logger.debug(f"Current player hand: {self.current_hand}")
        #Recalculate player's hand
        self.calculate_hand()
        
    def doubling_down(self, new_card):
        """
        Adds a new card to the player's hand as part of a double down move and recalculates the hand's total value.
        
        Args:
            new_card (list): The card to be added to the player's hand.
        """
        if self.hit_count < 3:
            logger.info(f"{self.name} doubling down")
            self.hit_count += 1
            self.current_hand.append(new_card)
            logger.debug(f"Current player hand: {self.current_hand}")
            #Recalculate player's hand
            self.calculate_hand()
        else:
            logger.warning(f"{self.name} has already hit, impossible to double down")
            print("Player has already hit, impossible to double down")
            
    def stand(self):
        """
        Ends the player's turn and displays their final hand.
        """
        logger.debug(f"{self.name} stands with {self.current_hand}")
        print(f"{self.name} stands with:")
        for card in self.current_hand:
            print(f"- {card[0]}")
        print(f"Total of: {self.total_val}")
    
    def surrender(self):
        """
        The player surrenders and forfeits half their bet.
        """
        logger.debug(f"{self.name} surrenders.")
        print(f"{self.name} surrenders. Half of the bet is lost.")
        self.total_val = 0

"""MAIN GAME LOOP"""
#TODO: Deal with the fact that cards are saved each iteration, it should not
def main():
    print("********************************")
    print("Welcome to 21 Black Jack")
    print("********************************\n")
    quit_game = False

    #Outer most infinite loop of the game
    while True:
        #Mid infinite loop to play or not
        while True:
            print("Enter 'Start' to start a new game")
            print("Enter 'Quit' to quit")
            user_option = input("Entered option (Start or Quit): ").lower()
            logger.debug(f"User selected option: {user_option}")
            print("")

            if user_option == "start":
                #Re-instantiate all classes each round
                current_deck = Deck()
                dealer = Dealer()
                player = Player()
                logger.debug(f"Instantiating deck, dealer and player")
                print("Shuffling the deck...")
                print("Handing cards...\n")
                
                #Deal cards to player and dealer
                logger.info(f"Dealing cards to player and dealer")
                player.hit(current_deck.generate_card())
                player.hit(current_deck.generate_card())
                dealer.hit(current_deck.generate_card())
                dealer.hit(current_deck.generate_card())    
                
                logger.debug(f"Showing player's cards to player")
                logger.debug(f"Player's card: {player.current_hand} and value of {player.total_val}")
                print("Your cards are: ")
                for card_dict in player.current_hand:
                    print(f"-{next(iter(card_dict))}")
                print(f"-Total of: {player.total_val}\n")
                
                logger.debug(f"Showing 1 of dealer's card to player")
                logger.debug(f"Dealer's card: {dealer.current_hand} and value of {dealer.total_val}")
                print("Dealer's cards are: ")
                print(f"-{next(iter(dealer.current_hand[0]))}") #Always only print first card face key
                print(f"-Secret card")
                print(f"-Total of: ???\n")
                
                #Check if from the get-go, user has 21
                if player.total_val == 21:
                    logger.info(f"Player got 21 blackjack")
                    logger.debug(f"Player's card {player.current_hand}")
                    print("21 Black Jack!!!")
                    
                    #TODO: Finish this logic when dealer and player both have 21 blackjack
                    # if player.total_val == dealer.total_val:
                    #     logger.info(f"Dealer also got 21 blackjack")
                    #     logger.debug(f"Dealer's card {dealer.current_hand}")

                    #     print("Wait, Dealer also has 21 Black Jack, draw")
                    #     print("Dealer's cards are: ")
                    #     print(f"-{dealer.current_hand[0][0]}")
                    #     print(f"-{dealer.current_hand[1][0]}\n")
                        
                    #     print(f"-Dealer score: {dealer.total_val}")
                    #     print(f"-Player score: {player.total_val}\n")
                    #     break
                    break  #Break to dealer's turn since already blackjack
                
                logger.info(f"Asking player actions to take")
                print("Do you want to: Hit, Double down, Stand or Surrender?")
                
                while True:
                    user_action = input("Entered option (Player action): ").lower()
                    logger.info(f"Player selected action: {user_action}")

                    if user_action == "hit":
                        player.hit(current_deck.generate_card())
                        logger.debug(f"Player hit with new card {next(iter(player.current_hand[-1]))}")
                        print(f"-Player New card: {next(iter(player.current_hand[-1]))}")
                        print(f"Total of: {player.total_val}\n")
                        
                    elif user_action in ["double down", "double", "doubledown", "Double Down", "Double down", "double Down"]:
                        if player.hit_count < 3:
                            player.doubling_down(current_deck.generate_card())
                            logger.debug(f"Player doubled down with new card {next(iter(player.current_hand[-1]))}")          
                            print(f"-New card: {next(iter(player.current_hand[-1]))}, Be careful!")
                            print(f"Total of: {player.total_val}\n")
                        else:
                            logger.warning(f"Player already hit, impossible to double down")
                            print("Player has already hit once, impossible to double down\n")
                            continue  #Continue until user gives a valid input
                        
                    elif user_action == "stand":
                        logger.info(f"Player decided to stand, proceeding with dealer")
                        player.stand()
                        break  #Break to dealer's turn
                    
                    elif user_action == "surrender":
                        logger.info(f"Player decided to surrender, bet is lost")
                        player.surrender()
                        print("You lose!, Sorry\n")
                        break  #Break and proceed to Dealer's win
                    else:
                        logger.warning(f"Player provided an invalid input")
                        print("Invalid option, please try again")
                        continue  #Continue until user gives a valid input
                    
                    if player.total_val > 21:
                        #Break inner most loop due to player bust
                        break   

                #Check if player busted
                if player.total_val > 21:
                    logger.info(f"Player bust with {player.total_val} over 21")
                    print("You Bust, You lose")
                    print(f"-Dealer score: {dealer.total_val}")
                    print(f"-Player score: {player.total_val} (bust)\n")
                    break  #Break with Dealer's win
                
                #Show Dealer's secret card
                print("Dealer's cards are: ")
                for card_dict in dealer.current_hand:
                    print(f"-{next(iter(card_dict))}")
                print(f"Total of: {dealer.total_val}\n")
                
                if dealer.total_val > 21:
                    logger.info(f"Dealer bust with {player.total_val} over 21")
                    print("Dealer Bust, You win")
                    print(f"-Dealer score: {dealer.total_val} (bust)")
                    print(f"-Player score: {player.total_val}\n")
                    break  #Break with Player's win
                
                #Dealer hit until bust or 21
                while dealer.total_val < 21:
                    dealer.hit(current_deck.generate_card())
                    print(f"-Dealer New card: {next(iter(dealer.current_hand[-1]))}")
                print(f"New Total of: {dealer.total_val}\n")

                if dealer.total_val > 21:
                    logger.info(f"Dealer bust with {player.total_val} over 21")
                    print("Dealer Bust, You win")
                    print(f"-Dealer score: {dealer.total_val} (bust)")
                    print(f"-Player score: {player.total_val}\n")
                    break  # Break with Player's win 
                elif player.total_val > dealer.total_val:
                    logger.info(f"Player win with {player.total_val} over 21")
                    print("You win")
                    print(f"-Dealer score: {dealer.total_val}")
                    print(f"-Player score: {player.total_val}\n")
                elif player.total_val < dealer.total_val:
                    logger.info(f"Dealer win with {dealer.total_val} over 21")
                    print("Dealer wins")
                    print(f"-Dealer score: {dealer.total_val}")
                    print(f"-Player score: {player.total_val}\n")
                elif player.total_val == dealer.total_val:
                    logger.info(f"No one wins, draw")
                    print("Draw, no one wins")
                    print(f"-Dealer score: {dealer.total_val}")
                    print(f"-Player score: {player.total_val}\n")

            elif user_option == "quit":
                quit_game = True
                logger.info(f"{player.name} decided to quit")
                print("Have a nice Day!!!")
                break
            
            else:
                logger.warning(f"User selected invalid option, re-iterating")
                print("Invalid option, please try again")

        if quit_game:
            break


#Call the main function to start the game
if __name__ == "__main__":
    main()
