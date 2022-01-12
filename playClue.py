from player import Player
from game import Game
import os


class GamePlay():
    def __init__(self, trialGame):
        rooms = ["Hall", "Ballroom", "Conservatory", "Library", "Billiard-Room", 
                      "Lounge", "Kitchen", "Study", "Dining-Room"]
        weapons = ["Candlestick", "Knife", "Rope", "Revolver", "Lead-Pipe", "Wrench"]
        people = ["White", "Green", "Plum", "Scarlet", "Peacock", "Mustard"]

        if trialGame:
            print("Initializing a trial game...")
            starting_dict = {
                "Helena": 5,
                "Chloe": 5,
                "Rowan": 4,
            }
            me = Player("Gabe", 4, ["Dining-Room", "Hall", "Library", "Knife"])
            game = Game("trialGame", starting_dict, me)
            game.check_status()
            self.gameInstance = game
            return

        print('There has been a murder in the Clue Mansion! It is up to you to figure out "WhoDunIt..."\n')
        print(f"There are six suspects: {sorted(people)}")
        print(f"          six weapons: {sorted(weapons)}")
        print(f"      and nine rooms: {sorted(rooms)}\n")
        print("When inputting cards, please be sure to spell them as listed above.\n")
        
        my_name = self._get_input("What is your name? ")
        my_cards = self._get_input("What cards do you have? Please use commas to separate each card: ", people + weapons + rooms)
        other_players = self._get_input("Starting from your left, who are you playing with? ")
        
        starting_dict = {}
        for player in other_players:
            starting_dict[player] = int(self._get_input(f"How many cards does {player} have? "))
            
        gameID = self._get_input("Please enter a unique alphanumeric game ID: (Ex: game011122)\n")
        
        me = Player(my_name, len(my_cards), my_cards)
        game = Game(gameID, starting_dict, me)
        self.gameInstance = game
        return

    def _clear_console(self):
        return os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    def _get_input(self, prompt, acceptable_inputs=None, require_answer=False):
        while True:
            stdin = input(prompt)
            spelling_error = "Oops! Did you misspell something?"
            if "," in stdin:
                result = list(filter(lambda x: x != "", stdin.replace(" ", "").split(",")))
                if acceptable_inputs and any([word not in acceptable_inputs for word in result]):
                    print(spelling_error)
                    continue
                else:
                    break
            else:
                result = stdin.strip()
                if (result != "" and acceptable_inputs and result not in acceptable_inputs) or (result == "" and require_answer):
                    print(spelling_error)
                    continue
                else:
                    break
        return result if result != "" else None

    def turn(self, helpful=False):
        players_names = [player.name for player in self.gameInstance.players]
        player_name = self._get_input("Whose turn is it? ", players_names)
        my_turn = player_name == self.gameInstance.me.name
        
        pronoun = "you" if my_turn else "they"
        prompt = " (Please remember to separate with commas)" if helpful else ""
        suggested_cards = self._get_input(f"What did {pronoun} suggest?{prompt} ", self.gameInstance.all_cards)
        prompt = " (Press enter if no one)" if helpful else ""
        passing_player_names = self._get_input(f"Who had nothing?{prompt} ", players_names)
        showing_player_name = self._get_input(f"Who finally showed something?{prompt} ", players_names)
        
        if my_turn:
            card = self._get_input("What did they show you? ", self.gameInstance.all_cards, require_answer=True)
            self.gameInstance.turn(player_name, suggested_cards, passing_player_names, showing_player_name, card=card)
        else:
            self.gameInstance.turn(player_name, suggested_cards, passing_player_names, showing_player_name)

        self._clear_console()
        self.gameInstance.check_status()
        return

if __name__=="__main__":
    gameplay = GamePlay(trialGame=True)
    gameplay.turn(helpful=True)
    while True:
        gameplay.turn(helpful=False)