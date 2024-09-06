import random
import string

def random_password_generator(min_Length,numbers=True,special_Characters=True):
    
    english_Alphabet = string.ascii_letters
    arabic_Numbers = string.digits
    special_Character = string.punctuation
    
    available_Characters = english_Alphabet
    if numbers:
        available_Characters = available_Characters + arabic_Numbers
    if special_Characters: 
        available_Characters = available_Characters + special_Character
            
    pwrd=""
    
    while len(pwrd)<min_Length:
        new_char=random.choice(available_Characters)
        pwrd=pwrd+new_char
            
    
    return pwrd


password=random_password_generator(40,False,False)
print("Recommended password is: ",password)