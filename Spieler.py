import random

class Spieler(): # This will serve as the BasicBot or a base for other bots
    def __init__(self, Name):
        self.name = Name
        self.Punktestand = 0
        self.gewonnene_Stiche = 0
        self.hand = [] # List of Card objects
        self.stich = None # Card object, current card played in a trick
        self.darf_ausschaffen = True
        self.ist_gespannt = False
        self.hat_beim_abheben_geflunkert = False
        self.hat_bei_trumpf_oder_kritisch_geflunkert = False
        self.is_human = False # Differentiate bot from human

    def karten_wegschmeißen(self):
        self.hand = []

    def erhält_punkte(self, punkte):
        self.Punktestand += punkte

    def erhält_stich(self):
        self.gewonnene_Stiche += 1

    def gewonnen(self):
        return self.Punktestand >= 15

    def __str__(self):
        return self.name
    
    def wählt_schlag(self, nehmer_hat_karte_beim_abheben_genommen):
        # Wählt Wert von dem er am meisten Karten auf der Hand hat aber als String
        # For "Sau" (Ace), the value is "S", not "A" or "Ass" as per Karte.py values
        # Ensure Karte.py values are ["7", "8", "9", "10", "Unter", "Ober", "König", "Sau"]
        # The provided code uses "U", "O", "K", "S". Assuming these are correct.
        counts = {}
        for card_obj in self.hand:
            counts[card_obj.wert] = counts.get(card_obj.wert, 0) + 1
        
        # Prioritize pairs or more
        for wert_option in ["7", "8", "9", "10", "U", "O", "K", "S"]: # U,O,K,S from original
             if counts.get(wert_option, 0) >=2:
                 return wert_option
        
        # Fallback: if no pairs, return the value of the first card in hand (if any)
        if self.hand:
            return self.hand[0].wert
        return None # Should not happen if hand is not empty

    def wählt_farbe(self, nehmer_hat_karte_beim_abheben_genommen):
        # Wählt Farbe von der er am meisten Karten auf der Hand hat
        counts = {}
        for card_obj in self.hand:
            counts[card_obj.farbe] = counts.get(card_obj.farbe, 0) + 1

        # Prioritize pairs or more
        for farbe_option in ["Eichel", "Laub", "Herz", "Schelle"]:
            if counts.get(farbe_option, 0) >= 2:
                return farbe_option
        
        # Fallback: if no pairs, return the farbe of the first card in hand (if any)
        if self.hand:
            return self.hand[0].farbe
        return None # Should not happen if hand is not empty


    def spielt_karte(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict, gegner_stich = None, trumpf_oder_kritisch = False):
        # Basic bot logic: play the first valid card, or just the first card.
        # This needs to be enhanced for actual gameplay.
        # For now, it must return a Card object and remove it from hand.
        if not self.hand:
            return None 

        # Simple logic: if trumpf_oder_kritisch, try to play one. Otherwise, play any.
        # This doesn't consider "zuerst_gespielte_farbe" or if it must follow suit.
        # This is a very basic placeholder for bot logic.
        
        if trumpf_oder_kritisch:
            playable_critical_cards = []
            for karte_in_hand in self.hand: # Corrected variable name from i to karte_in_hand for clarity
                is_schlag_card = karte_in_hand.wert == schlag # Renamed for clarity
                is_trumpf_card = karte_in_hand.farbe == farbe # Renamed for clarity
                is_maxl = (karte_in_hand.wert == "K" and karte_in_hand.farbe == "Herz")
                is_belli = (karte_in_hand.wert == "7" and karte_in_hand.farbe == "Schelle")
                is_soacher = (karte_in_hand.wert == "7" and karte_in_hand.farbe == "Eichel")
                
                if is_schlag_card or is_trumpf_card or is_maxl or is_belli or is_soacher:
                    playable_critical_cards.append(karte_in_hand)
            
            if playable_critical_cards:
                # Basic bot: chooses the first available critical card.
                return playable_critical_cards[0] # DO NOT REMOVE/POP
            else:
                # No critical card, play the first available card.
                return self.hand[0] if self.hand else None # DO NOT REMOVE/POP
        else:
            # Not a trumpf_oder_kritisch situation, play the first available card.
            # TODO: Implement logic for following suit (zuerst_gespielte_farbe) if gegner_stich is provided.
            return self.hand[0] if self.hand else None # DO NOT REMOVE/POP


    def nimmt_karte_beim_abheben(self, karte): # karte is a Card object
        # Critical cards: Maxl (Herz König), Weli (Eichel 7), Belle (Schelle 7)
        if (karte.wert == "K" and karte.farbe == "Herz") or \
           (karte.wert == "7" and karte.farbe == "Eichel") or \
           (karte.wert == "7" and karte.farbe == "Schelle"):
            return True
        else:
            return False

    def um_schönere_bitten(self, nehmer_hat_karte_beim_abheben_genommen):
        # Bot logic: for now, never asks for nicer cards
        return False

    def ausschaffen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        # Bot logic: For now, only if Maxl (Herz König) is in hand and not gespannt.
        if any(k.wert == "K" and k.farbe == "Herz" for k in self.hand) and not self.ist_gespannt:
            return True
        else:
            return False

    def mitgehen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        # Bot logic: For now, always accepts "mitgehen" if offered.
        return True

    def bluff_anzeigen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        # Bot logic: For now, never accuses of bluffing.
        return False

class RandomBot(Spieler):
    def __init__(self, Name):
        super().__init__(Name)
        self.name = Name + " (RandomBot)" # Distinguish from base Spieler if used

    def wählt_schlag(self, nehmer_hat_karte_beim_abheben_genommen):
        # Possible ranks (using the "U", "O", "K", "S" convention from base Spieler)
        possible_ranks = ["7", "8", "9", "10", "U", "O", "K", "S"]
        # Option 1: Choose from ranks present in hand
        # ranks_in_hand = list(set(card.wert for card in self.hand))
        # if ranks_in_hand:
        #     return random.choice(ranks_in_hand)
        # Option 2: Choose from all possible ranks (even if not in hand, as per some rules)
        return random.choice(possible_ranks)

    def wählt_farbe(self, nehmer_hat_karte_beim_abheben_genommen):
        possible_suits = ["Herz", "Schelle", "Eichel", "Laub"]
        # Option 1: Choose from suits present in hand
        # suits_in_hand = list(set(card.farbe for card in self.hand))
        # if suits_in_hand:
        #    return random.choice(suits_in_hand)
        # Option 2: Choose from all possible suits
        return random.choice(possible_suits)

    def spielt_karte(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict, gegner_stich=None, trumpf_oder_kritisch=False):
        if not self.hand:
            return None

        if trumpf_oder_kritisch:
            critical_cards = []
            non_critical_cards = []
            for card_in_hand in self.hand:
                is_schlag_card = card_in_hand.wert == schlag
                is_trumpf_card = card_in_hand.farbe == farbe
                is_maxl = (card_in_hand.wert == "K" and card_in_hand.farbe == "Herz")
                is_belli = (card_in_hand.wert == "7" and card_in_hand.farbe == "Schelle")
                is_soacher = (card_in_hand.wert == "7" and card_in_hand.farbe == "Eichel")
                
                if is_schlag_card or is_trumpf_card or is_maxl or is_belli or is_soacher:
                    critical_cards.append(card_in_hand)
                else:
                    non_critical_cards.append(card_in_hand)
            
            if critical_cards: # Must play a critical card if available
                chosen_card = random.choice(critical_cards)
                # self.hand.remove(chosen_card) # DO NOT REMOVE HERE
                return chosen_card
            elif non_critical_cards: # No critical cards, play any other card
                chosen_card = random.choice(non_critical_cards)
                # self.hand.remove(chosen_card) # DO NOT REMOVE HERE
                return chosen_card
            # If hand is empty somehow (should be caught by `if not self.hand: return None` earlier)
            # or if logic error leads to no cards being selected. Fallback to random if hand not empty.
            return self.hand[random.randrange(len(self.hand))] if self.hand else None # DO NOT REMOVE/POP


        # Default: play any random card if not trumpf_oder_kritisch
        # Ensure hand is not empty before trying to access.
        if not self.hand: return None # Added check
        chosen_card_index = random.randrange(len(self.hand))
        chosen_card = self.hand[chosen_card_index] # DO NOT REMOVE/POP HERE
        return chosen_card

    def ausschaffen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        if self.ist_gespannt:
            return False # Cannot ausschaffen if gespannt
        return random.random() < 0.3 # 30% chance to ausschaffen

    def mitgehen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        return random.choice([True, False])

    def bluff_anzeigen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        return random.choice([True, False]) # 50% chance to call bluff

    def um_schönere_bitten(self, nehmer_hat_karte_beim_abheben_genommen):
        return random.choice([True, False]) # 50% chance

    def nimmt_karte_beim_abheben(self, karte): # karte is a Card object
        # Critical cards: Maxl (Herz König), Weli (Eichel 7), Belle (Schelle 7)
        is_critical = (karte.wert == "K" and karte.farbe == "Herz") or \
                      (karte.wert == "7" and karte.farbe == "Eichel") or \
                      (karte.wert == "7" and karte.farbe == "Schelle")
        if is_critical:
            return True
        # RandomBot currently does not bluff by taking non-criticals.
        return False


class Dein_Spieler(Spieler):
    def __init__(self, Name):
        super().__init__(Name)
        self.is_human = True

    # For human player, these methods indicate that the game is waiting for UI input.
    # They don't contain decision logic themselves.
    # The actual choice is made via API and processed by Watten.py/app.py.

    def wählt_schlag(self, nehmer_hat_karte_beim_abheben_genommen): 
        # UI will provide this choice. This method might not be called.
        # Or if called, it signals Watten.py that it's human's turn.
        print(f"{self.name} (Human) needs to choose Schlag via UI.")
        return None # Indicates decision is external

    def wählt_farbe(self, nehmer_hat_karte_beim_abheben_genommen):
        print(f"{self.name} (Human) needs to choose Trump via UI.")
        return None # Indicates decision is external

    def spielt_karte(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict, gegner_stich = None, trumpf_oder_kritisch = False):
        # The card is chosen in UI and passed to game logic in app.py.
        # This method, if called, just signifies it's human's turn.
        # The actual card object is set on self.stich by the game logic.
        print(f"{self.name} (Human) needs to play a card via UI.")
        return None # Card is handled externally

    def nimmt_karte_beim_abheben(self, karte):
        # Decision will be made via UI if this scenario arises for human.
        # For now, assume it's a yes/no choice passed via API.
        print(f"{self.name} (Human) needs to decide on taking card {str(karte)} beim Abheben via UI.")
        return None # Decision is external, passed to a specific handler in Watten.py

    def um_schönere_bitten(self, nehmer_hat_karte_beim_abheben_genommen):
        print(f"{self.name} (Human) needs to decide on 'um schönere bitten' via UI.")
        return None # Decision is external

    def ausschaffen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        print(f"{self.name} (Human) needs to decide on 'ausschaffen' via UI.")
        return None # Decision is external

    def mitgehen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        print(f"{self.name} (Human) needs to decide on 'mitgehen' via UI.")
        return None # Decision is external

    def bluff_anzeigen(self, schlag, farbe, stiche_bisher, nehmer_hat_karte_beim_abheben_genommen, hat_gesetzt_dict):
        print(f"{self.name} (Human) needs to decide on 'bluff anzeigen' via UI.")
        return None # Decision is external