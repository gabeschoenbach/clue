from player import Player
import pandas as pd
from copy import deepcopy
import os

class Game(): 
    def __init__(self, gameID, starting_dict, my_player):
        """
        For each game of Clue, track the following:
            - gameID, str: A unique ID for the file to which we'll save gameplay.
            - turn_number, int: A counter for the number of turns that have been played.
            - rooms, set: The set of rooms to gradually winnow down to one (all_rooms stays constant).
            - weapons, set: The set of weapons to gradually winnow down to one (all_weapons stays constant).
            - people, set: The set of people to gradually winnow down to one (all_people stays constant).
            - all_cards, set: The set of all Clue cards (people, weapons, rooms).
            - players, list(Player): A list of every Player in the game.
            - me, Player: The Player who is using this program.
        
        To instantiate this class, you need:
            - gameID, str: To set the unique ID
            - starting_dict, dict(str -> int): Each player's name and the number of cards they have,
                except for yourself.
            - my_player, Player: Your own player instance, with the cards you have in your hand.
        """
        self.gameID = gameID
        self.turn_number = 0
        self.rooms = set(["Hall", "Ballroom", "Conservatory", "Library", "Billiard-Room", 
                      "Lounge", "Kitchen", "Study", "Dining-Room"])
        self.all_rooms = deepcopy(self.rooms)
        self.weapons = set(["Candlestick", "Knife", "Rope", "Revolver", "Lead-Pipe", "Wrench"])
        self.all_weapons = deepcopy(self.weapons)
        self.people = set(["White", "Green", "Plum", "Scarlet", "Peacock", "Mustard"])
        self.all_people = deepcopy(self.people)
        self.all_cards = self.rooms.union(self.weapons).union(self.people)

        
        self.players = [Player(name, num) for (name, num) in starting_dict.items()]
        self.me = my_player
        for player in self.players:
            for my_card in my_player.cards_held:
                player.impossible_cards.add(my_card)
        self.players.append(my_player)
        if sum([player.num_cards for player in self.players]) != len(self.rooms) + \
                len(self.weapons) + len(self.people) - 3:
            raise ArithmeticError(f"The numbers of cards for each player seems incorrect.")
            
        self._eliminate_guesses()
        self._initialize_turns_file()
        return

    def _initialize_turns_file(self):
        """ Create a file to track each turn in the game. """
        game_dir = f"games/{self.gameID}"
        os.makedirs(game_dir, exist_ok=True)
        player_names = ",".join([player.name for player in self.players])
        with open(f"{game_dir}/{self.gameID}_turns.csv", "w") as f:
            f.write("guessing_player,person,room,weapon," + player_names + "\n")
        f.close()
        return

    def _update_turns_file(self, 
                           player_name, 
                           suggested_cards, 
                           passing_player_names, 
                           showing_player_name, 
                           card):
        """ Write to file the outcome of a given turn. """
        my_turn = player_name == self.me.name
        person, room, weapon = self._check_suggested_cards(suggested_cards)
        player_string = ""
        for player in self.players:
            if passing_player_names and player.name in passing_player_names:
                player_string += "PASS,"
            elif not my_turn and player.name == showing_player_name:
                player_string += "SHOW,"
            elif my_turn and player.name == showing_player_name:
                player_string += f"{card},"
            else:
                player_string += ","
        player_string = player_string[:-1] + "\n"
        with open(f"games/{self.gameID}/{self.gameID}_turns.csv", "a") as f:
            f.write(f"{player_name},{person},{room},{weapon},{player_string}")
        f.close()
        return
        
    def _get_intersection(self, suggested_cards, card_type):
        """ Return the intersection of the suggested cards with the given card type. """
        return list(set(suggested_cards).intersection(getattr(self, f"all_{card_type}")))

    def _check_suggested_cards(self, suggested_cards):
        """
        Given a list of suggested cards, check the following:
            - There are only three cards.
            - There is exactly one of each card_type: person, room, weapon.
        Then return the person, room, weapon
        """
        guessed_people = self._get_intersection(suggested_cards, "people")
        guessed_rooms = self._get_intersection(suggested_cards, "rooms")
        guessed_weapons = self._get_intersection(suggested_cards, "weapons")
        assert all([len(guesses) == 1 for guesses in [guessed_people, guessed_rooms, guessed_weapons]])
        return guessed_people[0], guessed_rooms[0], guessed_weapons[0]
        

    def turn(self, 
             player_name, 
             suggested_cards, 
             passing_player_names=None, 
             showing_player_name=None, 
             card=None):
        """
        Carry out a turn in Clue. For each passing player (if any), have them reveal no cards. For
        the player who shows a card (if there is one), have them reveal a card, specifying the card
        if it's revealed to the user. Finally, do some bookkeeping/update the turns file and increment
        the turn number.
        """
        my_turn = player_name == self.me.name
        if passing_player_names:
            if type(passing_player_names) is not list:
                passing_player_names = [passing_player_names]
            for passing_player_name in passing_player_names:
                player = [p for p in self.players if p.name == passing_player_name][0]
                player.reveal_none(suggested_cards)
        if showing_player_name and my_turn:
            showing_player = [player for player in self.players if player.name == showing_player_name][0]
            showing_player.reveal_to_me(card, suggested_cards)
        elif showing_player_name:
            showing_player = [player for player in self.players if player.name == showing_player_name][0]
            showing_player.reveal_to_other(suggested_cards)
        self._realign_players()
        self._eliminate_guesses()
        self._update_turns_file(player_name, 
                                suggested_cards, 
                                passing_player_names, 
                                showing_player_name, 
                                card)
        self.turn_number += 1
        return
    
    def check_status(self):
        """ Display what we know about the game and each player. """
        print(120*"~")
        print(f"GAME: {self.gameID} | TURN: {self.turn_number}")
        print(30*"-")
        for player in self.players:
            player.summarize()
        print(30*"-")
        for (card_type, total_cards) in [("people", 6), ("rooms", 9), ("weapons", 6)]:
            print(f"Possible {card_type.upper()} ({len(getattr(self, card_type))}/{total_cards}):")
            print(f"  {getattr(self, card_type)}")
        print(120*"~")
        return
    
    def _realign_players(self):
        """
        For every card X that we know a player is holding, check that no other player is holding that
        card (otherwise we made a logical error somewhere), and then add X to every other player's
        impossible cards set.
        """
        for player in self.players:
            other_players = [p for p in self.players if p is not player]
            for card in player.cards_held:
                assert all([card not in other_player.cards_held for other_player in other_players])
                for other_player in other_players:
                    other_player.impossible_cards.add(card)
                    other_player._remove_card_from_possible(card)
                    other_player._check_for_held_cards()
        return
    
    def _eliminate_guesses(self):
        """
        Update the people, rooms, and weapons sets. For every card we know is held by a player,
        remove it from its corresponding set. Moreover, if there is any card that _every_ player
        cannot be holding, then it must be the card we are looking for, so update its corresponding
        set to be the singleton set!
        """
        for player in self.players:
            for card_type in ["people", "rooms", "weapons"]:
                for card in player.cards_held:
                    if card in getattr(self, card_type):
                        getattr(self, card_type).remove(card)
        possible_people = self.people
        possible_rooms = self.rooms
        possible_weapons = self.weapons
        for card in possible_people:
            if all([card in player.impossible_cards for player in self.players]):
                self.people = set([card])
        for card in possible_rooms:
            if all([card in player.impossible_cards for player in self.players]):
                self.rooms = set([card])
        for card in possible_weapons:
            if all([card in player.impossible_cards for player in self.players]):
                self.weapons = set([card])
        return