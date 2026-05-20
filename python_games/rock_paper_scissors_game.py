#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rock, Paper, Scissors Game
Simple console game where a player competes against the computer.
"""

import random
import logging
import datetime

"""LOGGING SET UP"""
log_file = datetime.datetime.now().strftime("game_log_%Y-%m-%d_%H-%M-%S.log")
logger = logging.getLogger("rps_game")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

#File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

"""VARIABLES"""
options = ["rock", "paper", "scissors"]

"""METHODS"""
def determine_winner(player_answer, cpu_answer, user_wins, cpu_wins):
    """
    Determine the winner of a rock-paper-scissors round.
    Returns updated user_wins and cpu_wins.
    """
    if player_answer == cpu_answer:
        
        logger.debug(f"Draw: Both chose {player_answer}")
        print("It's a draw!\n")
    elif (player_answer == "rock" and cpu_answer == "scissors") or \
        (player_answer == "paper" and cpu_answer == "rock") or \
        (player_answer == "scissors" and cpu_answer == "paper"):
        
        logger.info(f"Player wins: {player_answer} beats {cpu_answer}")
        print("You won!")
        user_wins = user_wins + 1
    else:
        logger.info(f"CPU wins: {cpu_answer} beats {player_answer}")
        print("You lost!")
        cpu_wins = cpu_wins + 1

    print(f"Player: {user_wins}  CPU: {cpu_wins}\n")
    return user_wins, cpu_wins

def cpu_random_choice():
    """
    Generate the CPU's random choice.
    """
    cpu_pick = random.choice(options)
    logger.debug(f"CPU pick is {cpu_pick}")
    return cpu_pick

def validate_user_input(user_input, user_wins, cpu_wins):
    """
    Validate the user's input.
    Returns: 'quit', 'invalid', or 'ok'
    """
    if user_input == "q":
        
        print("\nFinal scores: Player", user_wins, "vs CPU", cpu_wins)
        print("Have a nice day, goodbye!")
        return "quit"
    elif user_input not in options:
        
        logger.warning(f"User input {user_input} is not valid option")
        logger.warning(f"Valid options are {options}")
        print("Please select a valid option\n")
        return "invalid"
    logger.info("User chose a valid option, proceeding")
    return "ok"

def main():
    """
    Main method to execute program
    """
    user_wins = 0
    cpu_wins = 0

    print("**********************************")
    print("Let's play a rock, paper, scissors game")
    print("**********************************\n")
    print("Select between 'Rock', 'Paper', 'Scissors' or 'Q' to quit\n")
    logger.info("Game started")

    while True:
        user_input = input("Your move: ").lower()
        status = validate_user_input(user_input, user_wins, cpu_wins)

        if status == "quit":
            logger.debug("Game quit by user. Final score "
                        f"- Player: {user_wins}, CPU: {cpu_wins}")
            break
        elif status == "invalid":
            continue

        cpu_pick = cpu_random_choice()

        print("You picked:", user_input)
        print("Opponent picked:", cpu_pick)
        logger.info(f"Player: {user_input} | CPU: {cpu_pick}")

        user_wins, cpu_wins = determine_winner(user_input, cpu_pick, user_wins, cpu_wins)

if __name__ == "__main__":
    main()
