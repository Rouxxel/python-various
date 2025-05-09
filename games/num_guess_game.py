#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Number Guessing Game
A simple game where the user tries to guess a randomly generated number.
"""

import random
import logging
import datetime

"""LOGGING SETUP"""
log_file = datetime.datetime.now().strftime("number_guess_log_%Y-%m-%d_%H-%M-%S.log")
logger = logging.getLogger("number_guess_game")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler (disabled)
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

def main():
    """
    Main function to run the number guessing game.
    """
    print("**********************************")
    print("Let's play a number guessing game")
    print("**********************************\n")
    logger.info("Game started")

    while True:
        break_game = False

        logger.info("Prompting user to input valid range")
        # Get valid range input
        while True:
            min_num = input("Please select a minimum number: ")
            max_num = input("Please select a maximum number: ")

            if min_num.isdigit() and max_num.isdigit():
                min_num = int(min_num)
                max_num = int(max_num)

                if min_num < max_num:
                    logger.debug(f"User selected range: {min_num} to {max_num}")
                    break
                else:
                    logger.warning("Invalid range: minimum is not less than maximum")
                    print("Minimum number must be less than maximum number.")
            else:
                logger.warning("Invalid input: non-integer values")
                print("One or both values are not valid integers.")

        random_num = random.randint(min_num, max_num)
        logger.info(f"Generated random number between {min_num} and {max_num}")

        # et valid guess input
        logger.info("Prompting user to guess the number")
        while True:
            guess = input("What number do you think it is?: ")
            if guess.isdigit():
                guess = int(guess)
                logger.debug(f"User guessed: {guess}")
                break
            else:
                logger.warning("Invalid guess input")
                print("Invalid input. Please enter a number.")

        if guess == random_num:
            logger.info(f"User guessed correctly: {guess}")
            print(f"🎉 Congratulations, your guess {guess} is correct!\n")
        else:
            logger.info(f"User guessed {guess}, but the number was {random_num}")
            print(f"❌ Sorry, the number was {random_num}\n")

        # Ask to play again
        logger.info("Prompting user to play again or quit")
        print("If you want to play again enter 1, if not enter 2\n")
        while True:
            user_option = input("Enter your choice: ")
            if user_option == "1":
                logger.debug("User chose to play again")
                print("New game:\n")
                break
            elif user_option == "2":
                logger.info("User chose to quit the game")
                print("Thanks for playing!")
                break_game = True
                break
            else:
                logger.warning(f"Invalid menu option selected: {user_option}")
                print(f"Invalid option: {user_option}")

        if break_game:
            logger.debug("Game ended by user")
            break

if __name__ == "__main__":
    main()
