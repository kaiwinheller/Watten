import random
from Deck import Watten_Deck
from Karte import Karte # Assuming Karte.py exists and has Karte class

# Game Phases
PHASE_GAME_OVER = "GAME_OVER"
PHASE_NEW_ROUND = "NEW_ROUND"
PHASE_AWAITING_ABHEBEN_DECISION = "AWAITING_ABHEBEN_DECISION" # If Nehmer needs to decide
PHASE_AWAITING_SCHLAG_CHOICE = "AWAITING_SCHLAG_CHOICE"
PHASE_AWAITING_TRUMP_CHOICE = "AWAITING_TRUMP_CHOICE"
PHASE_AWAITING_UM_SCHOENERE_BITTEN_GEBER = "AWAITING_UM_SCHOENERE_BITTEN_GEBER" # If human Geber
PHASE_AWAITING_UM_SCHOENERE_BITTEN_NEHMER = "AWAITING_UM_SCHOENERE_BITTEN_NEHMER" # If human Nehmer
PHASE_AWAITING_AUSSCHAFFEN_OFFER = "AWAITING_AUSSCHAFFEN_OFFER" # Player can offer to raise points
PHASE_AWAITING_AUSSCHAFFEN_RESPONSE = "AWAITING_AUSSCHAFFEN_RESPONSE" # Player needs to respond to offer
PHASE_AWAITING_CARD_PLAY = "AWAITING_CARD_PLAY" # Generic: player whose turn it is needs to play
PHASE_TRICK_EVALUATION = "TRICK_EVALUATION"
PHASE_ROUND_EVALUATION = "ROUND_EVALUATION"


class Watten_Zwei_Spieler():
    def __init__(self, Spielerliste, initial_geber_idx=None): # Spielerliste should be [Human_Player, Bot_Player]
        self.Spielerliste = Spielerliste
        if initial_geber_idx is not None and initial_geber_idx in [0, 1]:
            self.Geber = initial_geber_idx
        else:
            self.Geber = random.randint(0, 1) # 0 or 1, index in Spielerliste
        
        self.Punkteliste = {'7': 7, '8': 8, '9': 9, '10': 10, 'Unter': 11, 'Ober': 12, 'König': 13, 'Sau': 14}
        self.Deck = Watten_Deck()
        
        self.stiche_bisher = {spieler: [] for spieler in self.Spielerliste}
        self.zuerst_gespielte_farbe = 'Farblos' # Farbe of the first card in a trick
        self.schlag = None # String, e.g. "König"
        self.farbe = None  # String, e.g. "Herz" (Trump)
        self.punkte_für_stich = 2 # Base points for a round, can be increased by ausschaffen
        self.spieler_ausschaffen_dict = {spieler: [] for spieler in self.Spielerliste} # Unused in current simplified logic
        self.erste_karte_wurde_abgehoben = False # Flag if Nehmer took the abgehoben card

        self.current_phase = PHASE_NEW_ROUND
        self.current_player_on_turn = None # Player object whose action is awaited
        self.trick_leader = None # Player object who leads the current trick
        self.abgehobene_karte_fuer_nehmer = None # Temp store for card from abheben
        self.round_winner_if_folded = None # If a player folds during ausschaffen

        self.prepare_new_round() # Initialize for the first round

    def get_human_player(self):
        return self.Spielerliste[0] if self.Spielerliste[0].is_human else (self.Spielerliste[1] if self.Spielerliste[1].is_human else None)

    def get_bot_player(self):
        return self.Spielerliste[0] if not self.Spielerliste[0].is_human else (self.Spielerliste[1] if not self.Spielerliste[1].is_human else None)
        
    def get_nehmer(self):
        return self.Spielerliste[self.Geber ^ 1]

    def get_geber(self):
        return self.Spielerliste[self.Geber]

    def prepare_new_round(self):
        """Resets state for a new round, deals cards, and sets initial phase."""
        if any(s.gewonnen() for s in self.Spielerliste):
            self.current_phase = PHASE_GAME_OVER
            self.current_player_on_turn = None
            return

        # Reset player hands, stich counts for the round, ausschaffen flags etc.
        for spieler in self.Spielerliste:
            spieler.karten_wegschmeißen()
            spieler.gewonnene_Stiche = 0
            spieler.darf_ausschaffen = True # Reset for new round
            spieler.ist_gespannt = spieler.Punktestand >= 13 # Update based on score
            spieler.hat_beim_abheben_geflunkert = False
            spieler.hat_bei_trumpf_oder_kritisch_geflunkert = False
            spieler.stich = None # Clear any card from previous trick
        
        self.Deck.reset() # Shuffle deck
        # Abheben is part of prepare_new_round before dealing
        self.abgehobene_karte_fuer_nehmer = self.Deck.abheben()
        self.erste_karte_wurde_abgehoben = False # Reset this flag

        # Nehmer decides on abgehobene_karte
        nehmer = self.get_nehmer()
        if nehmer.is_human:
            self.current_phase = PHASE_AWAITING_ABHEBEN_DECISION
            self.current_player_on_turn = nehmer
            # UI will prompt human, then call process_abheben_decision
        else: # Bot Nehmer
            self.process_abheben_decision(nehmer.nimmt_karte_beim_abheben(self.abgehobene_karte_fuer_nehmer))
            # ^ This will then call deal_cards_and_continue_setup() or similar

    def process_abheben_decision(self, nehmer_takes_card):
        """Called after Nehmer (human or bot) decides on the abgehobene Karte."""
        nehmer = self.get_nehmer()
        if nehmer_takes_card:
            nehmer.hand.append(self.abgehobene_karte_fuer_nehmer)
            self.erste_karte_wurde_abgehoben = True
            # Check for bluff if taken card is not critical (Maxl, Belli, Soacher)
            if not self.ist_kritische_karte(self.abgehobene_karte_fuer_nehmer):
                nehmer.hat_beim_abheben_geflunkert = True
        else:
            self.Deck.karte_nach_unten_legen(self.abgehobene_karte_fuer_nehmer)
        
        self.abgehobene_karte_fuer_nehmer = None # Clear it
        self._deal_cards_and_continue_setup()

    def _deal_cards_and_continue_setup(self):
        """Deals cards and moves to next phase (Maschine check, Schlagwahl)."""
        self.Deck.an_spieler_austeilen(self.Spielerliste) # Deals remaining cards
        
        # Check for Maschine (Maxl, Belli, Soacher in one hand)
        for spieler in self.Spielerliste:
            if self.check_for_maschine(spieler):
                spieler.erhält_punkte(3) # Maschine wins 3 points
                if spieler.gewonnen():
                    self.current_phase = PHASE_GAME_OVER
                else:
                    self.Geber ^= 1 # Switch Geber for next round
                    self.prepare_new_round() # Start new round
                return

        # TODO: Implement "Um schönere bitten" phase if desired.
        # For now, skipping to Schlag choice.

        self.current_phase = PHASE_AWAITING_SCHLAG_CHOICE
        self.current_player_on_turn = self.get_nehmer()
        if not self.current_player_on_turn.is_human: # If Nehmer is bot
            chosen_schlag = self.current_player_on_turn.wählt_schlag(self.erste_karte_wurde_abgehoben)
            self.set_schlag(chosen_schlag)
            # Then proceed to trump choice by Geber (which might also be bot)

    def set_schlag(self, schlag_wert):
        """Sets the Schlag and transitions to Trump choice."""
        self.schlag = schlag_wert
        self.current_phase = PHASE_AWAITING_TRUMP_CHOICE
        self.current_player_on_turn = self.get_geber()
        if not self.current_player_on_turn.is_human: # If Geber is bot
            chosen_trump = self.current_player_on_turn.wählt_farbe(self.erste_karte_wurde_abgehoben)
            self.set_trump(chosen_trump)

    def set_trump(self, trump_farbe):
        """Sets the Trump and transitions to the first trick (or Ausschaffen)."""
        self.farbe = trump_farbe
        self.trick_leader = self.get_nehmer() # Nehmer leads the first trick
        self.current_player_on_turn = self.trick_leader
        self.current_phase = PHASE_AWAITING_CARD_PLAY # Or potentially PHASE_AWAITING_AUSSCHAFFEN_OFFER
        
        # Reset points for this round value, accounting for "gespannt" players
        if any(s.ist_gespannt for s in self.Spielerliste):
            self.punkte_für_stich = 3
        else:
            self.punkte_für_stich = 2
        self.round_winner_if_folded = None # Reset any fold state

        # If first player (trick_leader) is a bot, it might play or ausschaffen
        if not self.current_player_on_turn.is_human:
            # Simplified: bot plays card. TODO: Bot ausschaffen logic
            self.process_bot_play_card()


    def process_play_card(self, player, card_object):
        """Processes a card played by a player. Assumes card_object is valid for player."""
        if player != self.current_player_on_turn or self.current_phase != PHASE_AWAITING_CARD_PLAY:
            raise ValueError("Not player's turn or wrong phase to play card.")

        player.stich = card_object
        player.hand.remove(card_object)

        # Determine who is next or if trick is complete
        if self.Spielerliste[0].stich and self.Spielerliste[1].stich: # Both played
            self.current_phase = PHASE_TRICK_EVALUATION
            self.current_player_on_turn = None # System evaluates
            # evaluate_trick will be called next by app.py
        else: # Waiting for other player
            self.current_player_on_turn = self.Gegner(player)
            if not self.current_player_on_turn.is_human: # If next player is bot
                self.process_bot_play_card()
            # else: UI waits for human input

    def process_bot_play_card(self):
        """Makes the bot play a card."""
        bot_player = self.current_player_on_turn
        if bot_player.is_human or self.current_phase != PHASE_AWAITING_CARD_PLAY:
             raise ValueError("Not Bot's turn or wrong phase.")

        # Bot needs context for its decision (schlag, farbe, opponent's card if any)
        gegner_stich = self.Gegner(bot_player).stich 
        
        # TODO: Determine if this is a "trumpf_oder_kritisch" situation for the bot
        # This is a complex part of Watten logic (e.g. "Gute ansagen")
        # For now, assume false or basic check
        bot_must_play_trumpf_kritisch = False 
        if gegner_stich: # If bot is responding
             # Simplified: if critical card led, bot should try to play critical if it has one
            if self.ist_kritische_karte(gegner_stich, self.schlag, self.farbe) or \
               (gegner_stich.farbe == self.farbe and self.schlag not in [k.wert for k in bot_player.hand if k.farbe == self.farbe]): # Opponent played trump, bot has no higher trump of same schlag
                 bot_must_play_trumpf_kritisch = True


        card_played_by_bot = bot_player.spielt_karte(
            schlag=self.schlag,
            farbe=self.farbe,
            stiche_bisher=self.stiche_bisher, # Bot might use its own stiche_bisher
            nehmer_hat_karte_beim_abheben_genommen=self.erste_karte_wurde_abgehoben,
            hat_gesetzt_dict=self.spieler_ausschaffen_dict, # Bot might use this
            gegner_stich=gegner_stich,
            trumpf_oder_kritisch=bot_must_play_trumpf_kritisch # Pass this context
        )
        if card_played_by_bot:
            self.process_play_card(bot_player, card_played_by_bot)
        else:
            # This should ideally not happen if bot has cards. Error or handle empty hand.
            print(f"ERROR: Bot {bot_player.name} could not play a card.")
            # Potentially force a card play or end round if bot hand is empty (should be caught by game logic)


    def evaluate_trick(self):
        """Evaluates the completed trick and sets up for the next one or round evaluation."""
        if not (self.Spielerliste[0].stich and self.Spielerliste[1].stich):
            raise ValueError("Trick not complete, cannot evaluate.")

        trick_winner = self._calculate_trick_winner(self.Spielerliste)
        trick_winner.erhält_stich()
        
        # Record cards played in this trick for history
        for spieler in self.Spielerliste:
            self.stiche_bisher[spieler].append(spieler.stich)
            # spieler.stich = None # Clear for next trick - NO, keep for UI display until next trick starts

        if self.check_round_over(trick_winner):
            self.current_phase = PHASE_ROUND_EVALUATION
            self.current_player_on_turn = None # System evaluates round
            # process_round_winner will be called next
        else:
            # Next trick starts
            self.trick_leader = trick_winner 
            self.current_player_on_turn = self.trick_leader
            self.zuerst_gespielte_farbe = 'Farblos' # Reset for new trick leader
            for spieler in self.Spielerliste: spieler.stich = None # Clear cards for next trick
            
            self.current_phase = PHASE_AWAITING_CARD_PLAY
            if not self.current_player_on_turn.is_human: # If bot leads next trick
                self.process_bot_play_card()


    def _calculate_trick_winner(self, spieler_mit_stichen):
        # This is a simplified version of punkte_vergleichen
        # Original logic: self.Punkteliste[Spieler.stich.wert] + self.ist_maxl(Spieler.stich) + ...
        # Need to ensure ist_maxl etc. use self.schlag, self.farbe correctly.
        
        punkte_spieler1 = self._get_card_value(self.Spielerliste[0].stich)
        punkte_spieler2 = self._get_card_value(self.Spielerliste[1].stich)

        print(f"Card Values for Trick: {self.Spielerliste[0].name}: {punkte_spieler1} ({self.Spielerliste[0].stich}), {self.Spielerliste[1].name}: {punkte_spieler2} ({self.Spielerliste[1].stich})")

        if punkte_spieler1 > punkte_spieler2:
            return self.Spielerliste[0]
        elif punkte_spieler2 > punkte_spieler1:
            return self.Spielerliste[1]
        else:
            # Tie-breaking: usually player who played the first card of the leading suit/trump wins.
            # Or if values are identical (e.g. two non-trump 7s of different suits),
            # the one who played the card that set the "zuerst_gespielte_farbe" wins.
            # This means the player who was self.trick_leader at the start of this trick.
            return self.trick_leader


    def _get_card_value(self, karte_obj):
        """Calculates the value of a card in the context of current schlag and farbe."""
        if not karte_obj: return 0
        
        base_value = self.Punkteliste.get(karte_obj.wert, 0)
        
        # Maxl (Herz König)
        if karte_obj.wert == 'König' and karte_obj.farbe == 'Herz': base_value += 1000
        # Belli (Schelle 7)
        elif karte_obj.wert == '7' and karte_obj.farbe == 'Schelle': base_value += 500
        # Soacher/Spitz (Eichel 7)
        elif karte_obj.wert == '7' and karte_obj.farbe == 'Eichel': base_value += 200
        
        # Hauptschlag (chosen schlag of chosen farbe)
        if karte_obj.wert == self.schlag and karte_obj.farbe == self.farbe:
            base_value += 150 # Higher than just schlag or just farbe
        # Schlag (chosen schlag of other farben)
        elif karte_obj.wert == self.schlag:
            base_value += 100
        # Trumpf (chosen farbe, not Hauptschlag)
        elif karte_obj.farbe == self.farbe:
            base_value += 50
        
        # If this card's farbe was the first played in the trick (and it's not trump)
        # This helps decide if non-trump cards of same value are compared.
        # The original `ist_erste_farbe` only added 20.
        # This needs to be carefully considered: if player A plays Herz 8 (zuerst_gespielte_farbe=Herz),
        # and player B plays Laub 8. Herz 8 wins.
        # If player A plays Herz 8, and player B plays Herz 9. Herz 9 wins.
        # The primary hierarchy (Maxl > Belli > Soacher > Hauptschlag > Schlag > Trumpf > Farbe anspielen > Höherer Wert)
        # should handle this. The base_value from Punkteliste handles rank.
        # The `ist_erste_farbe` might be for specific tie-breaking rules not fully captured here.
        # For now, rely on the hierarchy above and base rank.
        
        return base_value


    def check_round_over(self, last_trick_winner):
        """Checks if a player has won 3 stiche OR if a player folded."""
        if last_trick_winner: # A trick was actually played and won
            return last_trick_winner.gewonnene_Stiche == 3 or (self.round_winner_if_folded is not None)
        else: # No trick winner (e.g. round ended due to fold during ausschaffen)
            return self.round_winner_if_folded is not None

    def process_round_winner(self):
        """Processes the round winner, awards points (if not already awarded by fold), and prepares for next round or game over."""
        round_winner = None
        punkte_diese_runde = self.punkte_für_stich
        points_already_awarded_by_fold = False

        if self.round_winner_if_folded:
            round_winner = self.round_winner_if_folded
            # Points were already awarded by handle_ausschaffen_response or handle_ausschaffen_offer (if opponent gespannt)
            points_already_awarded_by_fold = True
        else:
            # Determine winner by stiche
            for spieler in self.Spielerliste:
                if spieler.gewonnene_Stiche == 3:
                    round_winner = spieler
                    break
        
        if not round_winner:
            # This should not happen if check_round_over was true
            raise Exception("Round ended but no winner determined.")

        # Bluff checking (simplified for now, needs more context from player actions)
        # hat_angezeigt = self.Gegner(round_winner).bluff_anzeigen(...)
        # if hat_angezeigt:
        #    if round_winner.hat_beim_abheben_geflunkert or round_winner.hat_bei_trumpf_oder_kritisch_geflunkert:
        #        round_winner = self.Gegner(round_winner) # Other player gets points
        #        punkte_diese_runde = 2 # Standard points for successful bluff call
        #    else:
        #        punkte_diese_runde += 1 # Penalty for wrongly accusing bluff
        
        if not points_already_awarded_by_fold and round_winner:
            round_winner.erhält_punkte(punkte_diese_runde)
        elif not round_winner: # Should not happen if logic is correct
             print("ERROR: process_round_winner called without a determined round_winner and not due to fold.")
             # Fallback or raise error
             return # Avoid crashing on round_winner.gewonnen() if round_winner is None

        if round_winner.gewonnen(): # Check if round_winner exists before accessing attributes
            self.current_phase = PHASE_GAME_OVER
            self.current_player_on_turn = None
        else:
            self.Geber ^= 1 # Switch Geber
            self.prepare_new_round() # Sets up for next round (deals, new phase etc)
        
        return round_winner, punkte_diese_runde # Return for informational purposes

    def handle_ausschaffen_offer(self, offering_player):
        """Player (human or bot) offers to 'ausschaffen' (raise points)."""
        if offering_player.ist_gespannt: # Cannot ausschaffen if already "gespannt"
            return {"message": f"{offering_player.name} is 'gespannt' and cannot 'ausschaffen'.", "proceed": False}
        
        opponent = self.Gegner(offering_player)
        if opponent.ist_gespannt: # If opponent is gespannt, ausschaffen wins current points automatically
            offering_player.erhält_punkte(self.punkte_für_stich)
            self.round_winner_if_folded = offering_player # Mark as winner due to this rule
            # check_round_over and process_round_winner will handle game end or next round
            return {"message": f"{opponent.name} is 'gespannt'. {offering_player.name} wins {self.punkte_für_stich} points.", "proceed": True, "folded": True}

        # Normal ausschaffen: opponent must decide
        self.current_phase = PHASE_AWAITING_AUSSCHAFFEN_RESPONSE
        self.current_player_on_turn = opponent # Opponent needs to respond
        
        # Disable further ausschaffen for the offering player for this specific raise sequence
        offering_player.darf_ausschaffen = False 
        
        if not opponent.is_human: # If opponent is bot, let it respond immediately
            bot_accepts = opponent.mitgehen(self.schlag, self.farbe, self.stiche_bisher, self.erste_karte_wurde_abgehoben, self.spieler_ausschaffen_dict)
            return self.handle_ausschaffen_response(opponent, bot_accepts)
        else:
            return {"message": f"{offering_player.name} offered to 'ausschaffen'. Waiting for {opponent.name}.", "proceed": True}


    def handle_ausschaffen_response(self, responding_player, accepts_offer):
        """Player (human or bot) responds to an 'ausschaffen' offer."""
        offering_player = self.Gegner(responding_player)

        if accepts_offer:
            self.punkte_für_stich += 1
            responding_player.darf_ausschaffen = True # Now this player can re-raise (if not gespannt)
            # Game continues, it's still the original trick_leader's turn to play a card (or offer ausschaffen again if it was responding_player)
            self.current_phase = PHASE_AWAITING_CARD_PLAY 
            self.current_player_on_turn = self.trick_leader # Return to whoever was supposed to play
            if not self.current_player_on_turn.is_human and not self.current_player_on_turn.stich: # If bot's turn and hasn't played
                self.process_bot_play_card()
            return {"message": f"{responding_player.name} accepted. Round points are now {self.punkte_für_stich}. It's {self.trick_leader.name}'s turn.", "proceed": True}
        else: # Folds
            offering_player.erhält_punkte(self.punkte_für_stich) # Offering player wins current points
            self.round_winner_if_folded = offering_player
            # check_round_over and process_round_winner will handle game end or next round
            self.current_phase = PHASE_ROUND_EVALUATION # Trigger round end processing
            self.current_player_on_turn = None
            return {"message": f"{responding_player.name} folded. {offering_player.name} wins {self.punkte_für_stich} points.", "proceed": True, "folded": True}


    # Helper methods from original, potentially adapted
    def ist_kritische_karte(self, karte, current_schlag = None, current_farbe = None):
        """Checks if a card is Maxl, Belli, or Soacher OR matches current Schlag/Farbe."""
        schlag_to_check = current_schlag if current_schlag else self.schlag
        farbe_to_check = current_farbe if current_farbe else self.farbe

        if karte.wert == 'König' and karte.farbe =='Herz': return True # Maxl
        if karte.wert == '7' and karte.farbe == 'Schelle': return True # Belli
        if karte.wert == '7' and karte.farbe == 'Eichel': return True # Soacher
        if schlag_to_check and karte.wert == schlag_to_check: return True
        if farbe_to_check and karte.farbe == farbe_to_check: return True
        return False
        
    def Gegner(self, Spieler):
        return self.Spielerliste[self.Spielerliste.index(Spieler) ^ 1]

    def check_for_maschine(self, spieler): # spieler is a Spieler object
        has_maxl = any(c.wert == 'König' and c.farbe == 'Herz' for c in spieler.hand)
        has_belli = any(c.wert == '7' and c.farbe == 'Schelle' for c in spieler.hand)
        has_soacher = any(c.wert == '7' and c.farbe == 'Eichel' for c in spieler.hand)
        return has_maxl and has_belli and has_soacher

    # --- Methods that might be less used now or are internal helpers ---
    def neue_karten_austeilen(self): # Called if "um schönere bitten" is successful
        # Hände von Spielern leeren
        for spieler in self.Spielerliste:
            spieler.karten_wegschmeißen()
        # Neue Karten austeilen
        self.Deck.an_spieler_austeilen(self.Spielerliste) # Deals 5 cards to each again
    
    # The hard_reset from original is mostly covered by prepare_new_round.
    # Specific parts of hard_reset like resetting schlag/farbe are done as part of phase transitions.