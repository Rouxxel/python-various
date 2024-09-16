import random
import sys

#TODO:remember to make dealt_cards private and
class Deck:
    def __init__(self): #, suits=None, ranks=None, dealt_cards=None ???
        self.__suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        self.__ranks = {"Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6,
                        "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, 
                        "Queen": 10, "King": 10}
        self.dealt_cards=[]
        
    def add_dealt_cards(self,given_card):
        self.dealt_cards.append(given_card)

    def generate_card(self):
        while True:
            #Select random suit and rank
            sel_suit = random.choice(self.__suits)
            sel_rank = random.choice(list(self.__ranks.keys()))

            #Create the card face
            card_face = sel_rank + " of " + sel_suit

            #Check if card has already been dealt
            if card_face not in self.dealt_cards:
                self.add_dealt_cards(card_face)
                def_value = self.__ranks[sel_rank]
                break  #Break out of the loop if it's a unique card

        final_card =[card_face, def_value]
        return final_card
    
    def display_dealt_cards(self):
        print("Dealt cards so far are: ")
        if not self.dealt_cards:
            print("No cards dealt so far")
            return
            
        for card in range (0,len(self.dealt_cards)):    
            if card == len(self.dealt_cards)-1:
                print(self.dealt_cards[card],".",end="")
            else:
                print(self.dealt_cards[card],",", end="")

class Dealer: #Dealer must hit over and over until at least 17
    def __init__(self,current_hand=[], name="John Doe",total_val=0):
        self.current_hand=current_hand
        self.name=name
        self.total_val=total_val
        
    def calculate_hand(self):
        try:
            self.total_val=sum(each_card[1] for each_card in self.current_hand)
            
            #OR USE
            
            #for i in range(0,len(self.current_hand)):
            #    self.total_val=self.total_val+self.current_hand[i][1]
        
            if any(each_card[0] == "Ace" for each_card in self.current_hand) and self.total_val>21:
                self.total_val=self.total_val-10
    
            return self.total_val
        
        except Exception as e:
            print(f"Error occurred during hand calculation: {e}")
            sys.exit(1)
    
    def hit(self, new_card):
        self.current_hand.append(new_card)
        self.calculate_hand()
        
    #TODO: add current info for player

class Player:
    def __init__(self,current_hand=[], name="Player",total_val=0,hit_count=0,double_down=False):
        self.current_hand=current_hand
        self.name=name
        self.total_val=total_val
        self.hit_count=hit_count
        self.double_down=double_down
        
    def calculate_hand(self):
        try:
        
            self.total_val=sum(each_card[1] for each_card in self.current_hand)
            #OR USE 
            #for i in range(0,len(self.current_hand)):
            #    self.total_val=self.total_val+self.current_hand[i][1]
                
            if any(each_card[0] == "Ace" for each_card in self.current_hand) and self.total_val>21:
                self.total_val=self.total_val-10
        
            return self.total_val
        
        except Exception as e:
            print(f"Error occurred during hand calculation: {e}")
            sys.exit(1)
    
    def hit(self, new_card):
        self.hit_count=self.hit_count+1
        self.current_hand.append(new_card)
        self.calculate_hand()
        
    def doubling_down(self, new_card):
        if(self.hit_count<3):
            self.hit_count=self.hit_count+1
            self.current_hand.append(new_card)
            self.calculate_hand()
        else:
            print("Player has already hit, impossible to double down")
            
    def stand(self):
        print(f"{self.name} stands with:")
        for i in range(0,len(self.current_hand)):
            print(f"-{self.current_hand[i][0]}")
        print(f"Total of: {self.total_val}")
    
    def surrender(self):
        print(f"{self.name} surrenders. Half of the bet is lost.")
        self.total_val=0
    
    #TODO: add current info for player

#************************************************************************************************
#************************************************************************************************
#************************************************************************************************

print("********************************")
print("Welcome to 21 Black Jack")
print("********************************\n")
quitgame=False

#Outer most infinite loop of the game
while True:
    
    #Mid infinite loop to play or not
    while True:
        print("Enter 'Start' to start a new game")
        print("Enter 'Quit' to quit")
        user_option=input("Entered option (Start or Quit): ").lower()
        print("")
        
        #"Switch case" statement
        if user_option=="start":
            current_deck=Deck()
            dealer=Dealer()
            player=Player()
            print("Shuffling the deck...")
            print("Handing cards...\n")
            
            player.hit(current_deck.generate_card())
            player.hit(current_deck.generate_card())
            dealer.hit(current_deck.generate_card())
            dealer.hit(current_deck.generate_card())      
            
            print("Your cards are: ")
            print(f"-{player.current_hand[0][0]}")
            print(f"-{player.current_hand[1][0]}")
            print(f"-Total of: {player.total_val}\n")
            
            print("Dealer's cards are: ")
            print(f"-{dealer.current_hand[0][0]}")
            print(f"-Secret card")
            print(f"-Total of: ???\n")
            
            #***************************************************************
            if player.total_val == 21:
                print("21 Black Jack!!!, You win\n")
                break
            
            #inner most infinite loop for player actions
            print("Do you want to: Hit, Double down, Stand or Surrender?")
            while True:
                user_action=input("Entered option (Player action): ").lower()
                
                if user_action=="hit":
                    player.hit(current_deck.generate_card())
                    print(f"-Player New card: {player.current_hand[-1][0]}")
                    print(f"Total of: {player.total_val}\n")
                    
                elif user_action=="double down" or user_action=="double" or user_action=="doubledown":
                    if player.hit_count<3:
                        player.doubling_down(current_deck.generate_card())          
                        print(f"-New card: {player.current_hand[-1][0]}, Be careful!")
                        print(f"Total of: {player.total_val}\n")
                    else:
                        print("Player has already hit once, impossible to double down\n")
                        continue
                    
                elif user_action=="stand":
                    player.stand()
                    print("")
                    break
                
                elif user_action=="surrender":
                    player.surrender()
                    print("You lose!, Sorry\n")
                    break
                else:
                    print("Invalid option, please try again")
                    continue     
                
                if player.total_val>21:
                    break   
            
            #****************************************************************        
            if player.total_val>21:
                print("You Bust, You lose")
                print(f"-Dealer score: {dealer.total_val}")
                print(f"-Player score: {player.total_val} (bust)\n")
                break
            
            if dealer.total_val>21:
                print("Dealer Bust, You win")
                print(f"-Dealer score: {dealer.total_val} (bust)")
                print(f"-Player score: {player.total_val}\n")
                break
            
            #****************************************************************
            print("Dealer's cards are: ")
            print(f"-{dealer.current_hand[0][0]}")
            print(f"-{dealer.current_hand[1][0]}")
            print(f"Total of: {dealer.total_val}\n")
            
            #inner most loop 2 for dealer to reach at least 17
            while dealer.total_val<17:
                dealer.hit(current_deck.generate_card())
                print(f"-Dealer New card: {dealer.current_hand[-1][0]}")
            print(f"New Total of: {dealer.total_val}\n")
            
            #****************************************************************s
            if dealer.total_val>21:
                print("Dealer Bust, You win")
                print(f"-Dealer score: {dealer.total_val} (bust)")
                print(f"-Player score: {player.total_val}\n")
                break  
            elif player.total_val>dealer.total_val:
                print("You win")
                print(f"-Dealer score: {dealer.total_val}")
                print(f"-Player score: {player.total_val}\n")
            elif player.total_val<dealer.total_val:
                print("Dealer wins")
                print(f"-Dealer score: {dealer.total_val}")
                print(f"-Player score: {player.total_val}\n")
            elif player.total_val==dealer.total_val:
                print("Draw, no one wins")
                print(f"-Dealer score: {dealer.total_val}")
                print(f"-Player score: {player.total_val}\n")
                                
        elif user_option=="quit":
            quitgame=True
            print("Have a nice Day!!!")
            break
        else:
            print("Invalid option, please try again")

    if quitgame:
        break
    
