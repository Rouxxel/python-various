import random
import string

def random_password_generator(min_Length,letter=True,numbers=True,special_Characters=True):
    
    english_Alphabet = string.ascii_letters
    arabic_Numbers = string.digits
    special_Character = string.punctuation
    
    available_Characters = ""
    
    if letter:
        available_Characters = available_Characters + english_Alphabet
    if numbers:
        available_Characters = available_Characters + arabic_Numbers
    if special_Characters: 
        available_Characters = available_Characters + special_Character
            
    pwrd=""
    
    if available_Characters != "":
        while len(pwrd)<min_Length:
            new_char=random.choice(available_Characters)
            pwrd=pwrd+new_char
    else:
        print("Error: No characters selected for password generation")        
    
    return pwrd


password=random_password_generator(40,False,False,False)
print("Recommended password is: ",password)