class Player():
    def __init__(self, name, num_cards, cards=[]):
        """
        For each player, track the following:
            - name, str: Player's given name.
            - num_cards, int: How many cards they're holding.
            - cards_held, set(str): Set of cards they logically must be holding, inferred either
                through direct showing, or by a combination of passing and showing to other players.
            - impossible_cards, set(str): Set of cards they cannot be holding, inferred whenever
                they pass on a suggestion.
            - possible_cards_list, list(set(str)): A "history" of suggestions that this player
                showed a card on, where impossible cards are removed from the history as they are
                inferred. Every subset has at most three cards (from a different player's suggestion)
                and if a subset is winnowed to only one card X, the player must be holding X.
        """
        if cards and num_cards != len(cards):
            raise ValueError(f"Number of cards ({num_cards}) does not match cards list: {cards}")
        self.name = name
        self.num_cards = num_cards
        self.cards_held = set(cards)
        self.impossible_cards = set()
        self.possible_cards_list = list()
        return
    
    def reveal_to_other(self, suggested_cards):
        """ When a player reveals one of their cards to another player. """
        self._add_suggested_cards(suggested_cards)
        return
    
    def reveal_to_me(self, card, suggested_cards):
        """ When a player reveals one of their cards to the user. """
        self.cards_held.add(card)
        self._add_suggested_cards(suggested_cards)
        return
    
    def reveal_none(self, suggested_cards):
        """ When a player says they have none of the suggested cards. """
        for card in suggested_cards:
            self.impossible_cards.add(card)
            self._remove_card_from_possible(card)
        self._check_for_held_cards()
        return
    
    def _add_suggested_cards(self, suggested_cards):
        """
        Add suggested cards to the possible cards list (as long as we don't know that the player
        cannot possibly hold them).
        """
        subset = set()
        for card in suggested_cards:
            if card not in self.impossible_cards:
                subset.add(card)
        self.possible_cards_list.append(subset)
        return
    
    def _remove_card_from_possible(self, card):
        """ Remove card from each subset in the possible cards list, if it exists. """
        for subset in self.possible_cards_list:
            subset.discard(card) # TODO: Are we sure this removes in place?
        # new_possible_cards_list = []
        # for subset in self.possible_cards_list:
        #     if card in subset:
        #         subset.discard(card)
        #     new_possible_cards_list.append(subset)
        # self.possible_cards_list = new_possible_cards_list
        return
    
    def _check_for_held_cards(self):
        """
        If any subset in the possible cards list is of length one, that card is definitely held.
        """
        for subset in self.possible_cards_list:
            if len(subset) == 1:
                self.cards_held.add(list(subset)[0])
        return
    
    def summarize(self):
        """
        Display what we know about the player:
            - Which cards they're certainly holding
            - Which cards they might be holding based on previous shows
            - Which cards they cannot be holding based on previous passes
        """
        print(f"{self.name.upper()} ({len(self.cards_held)}/{self.num_cards} known):")
        print(f"  is certainly holding ({len(self.cards_held)}): {self.cards_held}")
        unknown_cards = self.num_cards - len(self.cards_held)
        if unknown_cards:
            might_have = set()
            for subset in self.possible_cards_list:
                for card in subset:
                    if card not in self.cards_held:
                        might_have.add(card)
            caveat = f" (at most {unknown_cards})" if unknown_cards < len(might_have) else ""
            print(f"  might have{caveat}: {might_have}")
        print(f"  cannot be holding ({len(self.impossible_cards)}): {self.impossible_cards}")