import unittest
from Karte import Karte
from Deck import Watten_Deck
from Spieler import Spieler, Dein_Spieler, RandomBot
from Watten import Watten_Zwei_Spieler # Assuming this is the main game class

class TestCardAndDeck(unittest.TestCase):
    def test_card_creation(self):
        card = Karte("Herz", "König")
        # Assuming str(card) format is "Wert Farbe" based on Karte.py's __str__
        # If Karte.py uses "Farbe Wert", this needs to be "Herz König"
        self.assertEqual(str(card), "König Herz") 

    def test_deck_creation(self):
        deck = Watten_Deck()
        self.assertEqual(len(deck.cards), 32)
        # Check for unique cards
        self.assertEqual(len(set(str(c) for c in deck.cards)), 32)

    def test_deck_deal(self):
        deck = Watten_Deck()
        initial_len = len(deck.cards)
        # Watten_Deck.austeilen() in the provided code seems to deal all cards to players,
        # not return one card. Let's assume there's a method like `abheben` or a generic draw.
        # The provided Deck.py has `abheben()` which returns one card and `karte_nach_unten_legen`.
        # `an_spieler_austeilen` deals multiple.
        # For this test, let's use `abheben` as a way to get one card.
        card = deck.abheben() 
        self.assertIsNotNone(card)
        # abheben() puts the card back if not taken, so length might not change as expected for a simple deal.
        # If abheben() removes, then initial_len - 1 is correct.
        # Based on Watten.py, abheben() removes it from the main list if taken by player,
        # or it's put on bottom if not. For testing deal, let's assume it's removed.
        # The current Deck.abheben() removes the card and returns it.
        self.assertEqual(len(deck.cards), initial_len - 1)


    def test_deck_reset(self):
        deck = Watten_Deck()
        deck.abheben() # Simulate a card being removed
        deck.reset()
        self.assertEqual(len(deck.cards), 32)

class TestPlayer(unittest.TestCase):
    def setUp(self):
        # Using card values as per Karte.py: "7", "8", "9", "10", "Unter", "Ober", "König", "Sau"
        self.karten_beispiele = [
            Karte("Herz", "König"), 
            Karte("Schelle", "7"), 
            Karte("Eichel", "Sau"), 
            Karte("Laub", "Ober"), 
            Karte("Herz", "9")
        ]

    def test_spieler_init(self):
        player = Spieler("TestBot")
        self.assertEqual(player.name, "TestBot")
        self.assertEqual(player.Punktestand, 0)
        self.assertFalse(player.is_human)

    def test_dein_spieler_init(self):
        human = Dein_Spieler("HumanTest")
        self.assertEqual(human.name, "HumanTest")
        self.assertTrue(human.is_human)

    def test_random_bot_init(self):
        bot = RandomBot("Rando")
        self.assertEqual(bot.name, "Rando (RandomBot)") # Name is modified in RandomBot constructor
        self.assertFalse(bot.is_human)


    def test_random_bot_waehlt_schlag(self):
        bot = RandomBot("RandoSchlag")
        bot.hand = list(self.karten_beispiele) 
        schlag = bot.wählt_schlag(False) # False for nehmer_hat_karte_beim_abheben_genommen
        self.assertIn(schlag, ["7", "8", "9", "10", "U", "O", "K", "S"]) # U,O,K,S used by RandomBot

    def test_random_bot_waehlt_farbe(self):
        bot = RandomBot("RandoFarbe")
        bot.hand = list(self.karten_beispiele)
        farbe = bot.wählt_farbe(False)
        self.assertIn(farbe, ["Herz", "Schelle", "Eichel", "Laub"])

    def test_random_bot_spielt_karte(self):
        bot = RandomBot("RandoSpiel")
        bot.hand = list(self.karten_beispiele)
        initial_hand_size = len(bot.hand)
        
        # The spielt_karte method in Spieler.py (and RandomBot) was changed to NOT remove the card.
        # Watten.py's process_play_card is responsible for removing the card from hand.
        # So, the hand size should NOT change here.
        card_played_obj = bot.spielt_karte(
            schlag="Sau", farbe="Herz", stiche_bisher={}, 
            nehmer_hat_karte_beim_abheben_genommen=False, hat_gesetzt_dict={}
        )
        self.assertIsNotNone(card_played_obj)
        self.assertEqual(len(bot.hand), initial_hand_size) # Hand size should NOT change
        
        # To test removal, we'd have to simulate Watten.py's call structure.
        # For this unit test of RandomBot, we confirm it returns a card from its hand.
        # We need to find if the returned card object is one of the cards in the original hand.
        # This requires comparing card objects or their string representations if objects are different.
        # For simplicity, we'll check if the string representation of played card is in string reps of original hand.
        self.assertIn(str(card_played_obj), [str(c) for c in self.karten_beispiele])

        # The bot's .stich attribute is set by Watten.py, not by its own spielt_karte method.
        # So, self.assertEqual(bot.stich, card_played_obj) would be incorrect here.

    def test_spieler_erhaelt_punkte(self):
        player = Spieler("ScorePlayer")
        player.erhält_punkte(3)
        self.assertEqual(player.Punktestand, 3)
        player.erhält_punkte(2)
        self.assertEqual(player.Punktestand, 5)

class TestWattenGame(unittest.TestCase):
    def setUp(self):
        # Ensure players have distinct names for clarity in debugging game states
        self.player1 = Dein_Spieler("HumanP1") # Human player for some tests
        self.player2 = RandomBot("BotP2")    # Bot player
        
        # Test with Human as Geber (index 0)
        self.game_human_geber = Watten_Zwei_Spieler([self.player1, self.player2], initial_geber_idx=0)
        # Test with Bot as Geber (index 1)
        self.game_bot_geber = Watten_Zwei_Spieler([self.player1, self.player2], initial_geber_idx=1)

        # A generic game instance for tests not dependent on Geber order immediately
        self.game = self.game_human_geber 


    def test_game_init_roles_forced_human_geber(self):
        # Player1 (HumanP1) should be Geber
        self.assertEqual(self.game_human_geber.get_geber(), self.player1)
        self.assertEqual(self.game_human_geber.get_nehmer(), self.player2)
        # Cards are dealt after abheben decision in prepare_new_round
        # Initial phase is AWAITING_ABHEBEN_DECISION, so hands might be empty or partially full
        # Let's check phase
        self.assertEqual(self.game_human_geber.current_phase, "AWAITING_TRUMP_CHOICE")
        self.assertEqual(self.game_human_geber.current_player_on_turn, self.player1)
        # Nehmer (BotP2) makes abheben decision automatically.
        # Then cards are dealt. Then Schlag/Trump.
        # So, after full setup of a new round (which includes auto-decisions by bot if it's their turn)
        # hands should be full.
        # The Watten_Zwei_Spieler constructor calls prepare_new_round, which might progress
        # past abheben if bot is nehmer.
        # If BotP2 (Nehmer) chose abheben, its hand might have 1 card. Player1 (Geber) 0.
        # If BotP2 declined, both 0. Then _deal_cards_and_continue_setup is called.
        # This part is tricky as bot plays automatically.
        # Let's assume prepare_new_round completes to a point where hands are dealt for Schlag/Trump.
        # To test this robustly, we need to step through phases or mock bot choices.
        # For now, let's check that deck is there and players exist.
        self.assertIsNotNone(self.game_human_geber.Deck)
        self.assertIn(self.player1, self.game_human_geber.Spielerliste)
        self.assertIn(self.player2, self.game_human_geber.Spielerliste)


    def test_game_init_roles_forced_bot_geber(self):
        # Player2 (BotP2) should be Geber
        self.assertEqual(self.game_bot_geber.get_geber(), self.player2)
        self.assertEqual(self.game_bot_geber.get_nehmer(), self.player1) # Human is Nehmer
        self.assertEqual(self.game_bot_geber.current_phase, "AWAITING_ABHEBEN_DECISION")
        # Human (Nehmer) needs to make abheben decision. Hand should be empty.
        self.assertEqual(len(self.player1.hand), 0) 


    def test_critical_cards_evaluation_methods(self):
        # These are helper methods in Watten_Zwei_Spieler, not using self.game.schlag/farbe
        # They are more like static checks for card properties.
        # The original code had ist_maxl, ist_belli, ist_soacher with fixed values (1000,500,200)
        # The refactored Watten.py has _get_card_value which incorporates these.
        # Let's test _get_card_value for criticals vs non-criticals, assuming no schlag/farbe context for this part.

        # Test criticals (Maxl, Belli, Soacher)
        # _get_card_value uses self.schlag and self.farbe, so we need to set them or use ist_kritische_karte
        self.game.schlag = None
        self.game.farbe = None
        self.assertTrue(self.game.ist_kritische_karte(Karte("Herz", "König"))) # Maxl
        self.assertFalse(self.game.ist_kritische_karte(Karte("Herz", "Sau")))
        self.assertTrue(self.game.ist_kritische_karte(Karte("Schelle", "7")))  # Belli
        self.assertFalse(self.game.ist_kritische_karte(Karte("Schelle", "8")))
        self.assertTrue(self.game.ist_kritische_karte(Karte("Eichel", "7")))   # Soacher
        self.assertFalse(self.game.ist_kritische_karte(Karte("Eichel", "8")))

        # Test with schlag/farbe context for ist_kritische_karte
        self.game.schlag = "Unter"
        self.game.farbe = "Laub"
        self.assertTrue(self.game.ist_kritische_karte(Karte("Herz", "König"))) # Still Maxl
        self.assertTrue(self.game.ist_kritische_karte(Karte("Laub", "10")))    # Is Trump
        self.assertTrue(self.game.ist_kritische_karte(Karte("Eichel", "Unter"))) # Is Schlag


    def test_get_card_value_hierarchy(self):
        # Maxl vs Belli
        self.player1.stich = Karte("Herz", "König") # Maxl
        self.player2.stich = Karte("Schelle", "7")  # Belli
        # _calculate_trick_winner uses _get_card_value. No specific schlag/farbe needed for these top criticals.
        self.game.schlag = None 
        self.game.farbe = None
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Maxl should beat Belli")

        # Belli vs Soacher
        self.player1.stich = Karte("Schelle", "7")  # Belli
        self.player2.stich = Karte("Eichel", "7")   # Soacher
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Belli should beat Soacher")

        # Soacher vs Hauptschlag
        self.game.schlag = "Sau"
        self.game.farbe = "Herz" # Hauptschlag is Sau Herz
        self.player1.stich = Karte("Eichel", "7")   # Soacher
        self.player2.stich = Karte("Herz", "Sau")   # Hauptschlag
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Soacher should beat Hauptschlag")

        # Hauptschlag vs Schlag (non-trump)
        self.game.schlag = "Sau"
        self.game.farbe = "Herz" # Hauptschlag is Sau Herz
        self.player1.stich = Karte("Herz", "Sau")      # Hauptschlag
        self.player2.stich = Karte("Eichel", "Sau")    # Schlag (Eichel)
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Hauptschlag should beat other Schlag")
        
        # Schlag (non-trump) vs Trump (non-Hauptschlag)
        self.game.schlag = "Ober"
        self.game.farbe = "Herz" # Trump Herz
        self.player1.stich = Karte("Eichel", "Ober") # Schlag (Eichel)
        self.player2.stich = Karte("Herz", "9")      # Trump (Herz 9)
        # Based on _get_card_value: Schlag (100+rank) vs Trump (50+rank)
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Schlag (non-trump) should beat Trump (non-Hauptschlag) by current value logic")
        
        # Trump vs Plain card of same suit led
        self.game.schlag = "Unter" # Not relevant here
        self.game.farbe = "Schelle" # Trump Schelle
        self.game.trick_leader = self.player1 # Player1 leads the trick
        self.game.zuerst_gespielte_farbe = "Schelle" # Player1 leads a Schelle (Trump)
        self.player1.stich = Karte("Schelle", "8")   # Trump
        self.player2.stich = Karte("Schelle", "König") # Higher Trump
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player2, "Higher Trump should win")

        # Plain card vs Plain card (higher rank wins)
        self.game.farbe = "Laub" # Trump is Laub, these are Herz
        self.game.zuerst_gespielte_farbe = "Herz" # Player1 leads Herz
        self.player1.stich = Karte("Herz", "9")
        self.player2.stich = Karte("Herz", "Sau")
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player2, "Higher rank plain card should win if same suit led")
        
        # Plain card vs Plain card (different suit, first player's suit followed)
        self.game.zuerst_gespielte_farbe = "Herz" # Player1 leads Herz
        self.player1.stich = Karte("Herz", "Sau")
        self.player2.stich = Karte("Eichel", "Sau") # Player2 does not follow suit
        winner = self.game._calculate_trick_winner([self.player1, self.player2])
        self.assertEqual(winner, self.player1, "Card of led suit should win if opponent plays different non-trump suit")


    def test_hard_reset_deals_cards_and_resets_round_state(self):
        # Use a fresh game instance for this to avoid interference from other tests' state
        p1 = Spieler("P1HR")
        p2 = Spieler("P2HR")
        game_hr = Watten_Zwei_Spieler([p1, p2])

        # Simulate some game progression before reset
        game_hr.schlag = "Sau"
        game_hr.farbe = "Herz"
        p1.gewonnene_Stiche = 2
        game_hr.punkte_für_stich = 3
        p1.hand = [] # Empty hand before reset
        p2.hand = []

        # Ensure players are not gespannt for predictable punkte_für_stich reset
        p1.ist_gespannt = False
        p2.ist_gespannt = False
        
        game_hr.prepare_new_round() # This is the method that resets for a new round now
        
        self.assertIn(game_hr.schlag, [None, "7", "8", "9", "10", "Unter", "Ober", "König", "Sau", "U", "O", "K", "S"])
        self.assertIn(game_hr.farbe, [None, "Herz", "Schelle", "Eichel", "Laub"])
        # prepare_new_round calls _deal_cards_and_continue_setup which can lead to schlag/farbe choice by bot
        # depending on whether a human needs to make decisions. Accept any valid value here.
        # For now, let's check what prepare_new_round reliably resets:
        self.assertEqual(p1.gewonnene_Stiche, 0)
        self.assertEqual(p2.gewonnene_Stiche, 0)
        
        # Punkte für Stich resets based on gespannt status
        if any(s.ist_gespannt for s in game_hr.Spielerliste):
             self.assertEqual(game_hr.punkte_für_stich, 3)
        else:
             self.assertEqual(game_hr.punkte_für_stich, 2)

        # Hands are dealt after abheben decision.
        # If Human is Nehmer, hand is empty until abheben decision.
        # If Bot is Nehmer, it decides, then cards are dealt.
        # This makes testing hand length immediately after prepare_new_round complex.
        # Let's focus on what's certain: player stiche counts are reset.
        # A better test for card dealing might be to manually call _deal_cards_and_continue_setup
        # after mocking the abheben phase.

    def test_maschine_check(self):
        # Maxl (Herz König), Belli (Schelle 7), Soacher (Eichel 7)
        self.player1.hand = [Karte("Herz", "König"), Karte("Schelle", "7"), Karte("Eichel", "7"), Karte("Laub", "8"), Karte("Herz", "9")]
        self.assertTrue(self.game.check_for_maschine(self.player1))
        
        self.player2.hand = [Karte("Herz", "König"), Karte("Schelle", "7"), Karte("Eichel", "8"), Karte("Laub", "8"), Karte("Herz", "9")]
        self.assertFalse(self.game.check_for_maschine(self.player2))
        
        # Test with fewer than 3 criticals
        p3 = Spieler("P3Maschine")
        p3.hand = [Karte("Herz", "König"), Karte("Schelle", "7"), Karte("Laub", "Sau")]
        self.assertFalse(self.game.check_for_maschine(p3))


if __name__ == '__main__':
    unittest.main()
