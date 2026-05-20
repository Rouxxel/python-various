#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Random Password Generator
Generates a password with configurable character sets.
"""

import random
import string
import logging
import datetime

"""LOGGING SETUP"""
log_file = datetime.datetime.now().strftime("password_log_%Y-%m-%d_%H-%M-%S.log")
logger = logging.getLogger("password_generator")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

"""VARIABLES"""
english_alphabet = string.ascii_letters
arabic_numbers = string.digits
special_characters = string.punctuation
non_english_characters = 'áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜçÇøØñÑ'

"""FUNCTIONS"""
def available_characters(use_letters=True, 
                        use_numbers=True, 
                        use_special_chars=True,
                        use_non_english_chars=False):
    """
    Returns a string containing the set of characters to be used for password generation
    based on the specified criteria.

    Parameters:
        use_letters (bool): Include English alphabet letters (uppercase and lowercase) if True.
        use_numbers (bool): Include Arabic numerals (0–9) if True.
        use_special_chars (bool): Include special characters (e.g., !@#$%) if True.
        use_non_english_chars (bool): Include characters from non-English languages (e.g., accented characters) if True.

    Returns:
        str: A string of available characters to be used for generating a password.
    """
    characters = ""
    if use_letters:
        characters = characters + english_alphabet
    if use_numbers:
        characters = characters + arabic_numbers
    if use_special_chars:
        characters = characters + special_characters
    if use_non_english_chars:
        characters = characters + non_english_characters

    logger.debug(f"Permitted characters are: letters= {use_letters}, numbers= "
                 f"{use_numbers}, special_chars= {use_special_chars}, "
                 f"non_english_chars= {use_non_english_chars}")

    if not characters:
        logger.error("No character sets selected for password generation.")
        return None
    return characters

def generate_password(given_characters,
                    min_length=2):
    """
    Generates a random password from the provided character set.

    Parameters:
        given_characters (str): A string containing all characters eligible for password generation.
        min_length (int): The desired minimum length of the generated password (must be > 0).

    Returns:
        str or None: The generated password as a string, or None if inputs are invalid.
    """
    #Deal with parameters validity
    if not isinstance(given_characters, str):
        logger.error(f"given_characters is not expected type, stopping")
        return None
    if (min_length <= 0) or (not isinstance(min_length, int)):
        logger.error(f"min_length is not an int greater than 0, stopping")
        return None
    
    #Generate password
    logger.info(f"Generating password with length of {min_length} characters")
    password = ''.join(random.choice(given_characters) for _ in range(min_length))
    logger.debug(f"Generated password: {password}")
    
    #Return password
    return password

def get_user_input():
    """
    Prompts the user for input to customize password generation options.
    
    Returns:
        tuple: (length, use_letters, use_numbers, use_special_chars, use_non_english_chars)
    """
    #Get the password length from the user
    while True:
        try:
            length = int(input("Enter the desired password length: "))
            if length > 0:
                logger.debug(f"User selected a length of {length} characters")
                break
            else:
                logger.warning(f"Selected length is equal or less than 0")
                print("Length must be a positive integer greater than 0!")
        except ValueError:
            logger.error(f"Length value error, not an int")
            print("Please enter a valid number for the length.")

    #Ask if the user wants to include letters
    while True:
        use_letters_input = input("Include letters in the password? (yes/no): ").lower()
        if use_letters_input in ['yes', 'no']:
            use_letters = use_letters_input == 'yes'
            if use_letters:
                logger.debug(f"User selected to use letter characters")
            else:
                logger.debug(f"User selected not to use letter characters")
            break
        else:
            logger.warning(f"User selected invalid input outside 'yes' or 'no'")
            print("Invalid input! Please enter 'yes' or 'no'.")
            continue

    #Ask if the user wants to include numbers
    while True:
        use_numbers_input = input("Include numbers in the password? (yes/no): ").lower()
        if use_numbers_input in ['yes', 'no']:
            use_numbers = use_numbers_input == 'yes'
            if use_numbers:
                logger.debug(f"User selected to use number characters")
            else:
                logger.debug(f"User selected not to use number characters")
            break
        else:
            logger.warning(f"User selected invalid input outside 'yes' or 'no'")
            print("Invalid input! Please enter 'yes' or 'no'.")
            continue

    #Ask if the user wants to include special characters
    while True:
        use_special_chars_input = input("Include special characters in the password? (yes/no): ").lower()
        if use_special_chars_input in ['yes', 'no']:
            use_special_chars = use_special_chars_input == 'yes'
            if use_special_chars:
                logger.debug(f"User selected to use special characters")
            else:
                logger.debug(f"User selected not to use special characters")
            break
        else:
            logger.warning(f"User selected invalid input outside 'yes' or 'no'")
            print("Invalid input! Please enter 'yes' or 'no'.")
            continue

    #Ask if the user wants to include characters from non-English languages
    while True:
        use_non_english_chars_input = input("Include characters from non-English languages (e.g., accented characters)? (yes/no): ").lower()
        if use_non_english_chars_input in ['yes', 'no']:
            use_non_english_chars = use_non_english_chars_input == 'yes'
            if use_non_english_chars:
                logger.debug(f"User selected to use non-English characters")
            else:
                logger.debug(f"User selected not to use non-English characters")
            break
        else:
            logger.warning(f"User selected invalid input outside 'yes' or 'no'")
            print("Invalid input! Please enter 'yes' or 'no'.")
            continue

    return length, use_letters, use_numbers, use_special_chars, use_non_english_chars

def main():
    """
    Main method to execute the program.
    """
    print("Welcome to the Random Password Generator")

    # Get user input for password configuration
    length, use_letters, use_numbers, use_special_chars, use_non_english_chars = get_user_input()

    # Get the set of characters to use for password generation
    characters = available_characters(use_letters, use_numbers, use_special_chars, use_non_english_chars)

    # Generate the password
    password = generate_password(characters, length)

    # Display the result
    if isinstance(password, str):
        print(f"Generated password: {password}")
        logger.info("Password successfully generated and displayed to user.")
    else:
        print("Password generation failed. Please check your inputs.")
        logger.warning("Password generation returned None.")

if __name__ == "__main__":
    main()
