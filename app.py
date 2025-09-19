from flask import Flask, jsonify, request, send_from_directory
import sys
import os

# Add the directory containing Watten.py and other game files to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from Watten import Watten_Zwei_Spieler, PHASE_GAME_OVER # Import PHASE_GAME_OVER
from Spieler import Spieler, Dein_Spieler, RandomBot # Added RandomBot
from Deck import Watten_Deck # Keep if Watten.py needs it directly, though likely encapsulated
from Karte import Karte # Keep if Watten.py needs it directly

app = Flask(__name__, static_folder='static') 

@app.route('/')
def index():
    # Ensure index.html is served from the root where it's created
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    # Ensure static files are served from the 'static' directory
    return send_from_directory('static', path)

game_instance = None

@app.route('/game/new', methods=['POST'])
def new_game():
    global game_instance
    
    data = request.get_json()
    bot_type = data.get('bot_type', 'random') 
    force_human_role = data.get('force_human_role', None) # 'geber', 'nehmer', or None

    human_player = Dein_Spieler("Human")
    
    if bot_type == 'random':
        bot_player = RandomBot("RandomBot")
    elif bot_type == 'basic':
        bot_player = Spieler("BasicBot")
    else:
        print(f"Warning: Unknown bot_type '{bot_type}', defaulting to RandomBot.")
        bot_player = RandomBot(f"UnknownBot (as Random)")

    # Determine player order based on force_human_role
    if force_human_role == 'geber':
        # Human is Geber (index 0), Bot is Nehmer (index 1) for Watten_Zwei_Spieler if Geber is always index 0 in Spielerliste
        # Watten.py's self.Geber = 0 or 1 refers to index in self.Spielerliste.
        # If Human is Geber, game_instance.Geber should be 0.
        players = [human_player, bot_player]
        # We need to tell Watten_Zwei_Spieler who the Geber is, or ensure its random assignment is overridden.
        # For now, let Watten_Zwei_Spieler decide randomly, then we'll adjust if this isn't enough.
        # The constructor of Watten_Zwei_Spieler randomly assigns Geber.
        # A better approach would be to pass desired Geber index to Watten_Zwei_Spieler.
        # Let's modify Watten_Zwei_Spieler to accept an optional initial_geber_index.
        # For now, this change in app.py won't guarantee role until Watten.py is also changed.
        # As a simpler immediate step, we'll just create the instance and log.
        # The test script will have to retry if the role isn't what's desired.
        # NO - let's make the change to Watten.py too, it's critical for testing.
        # I will assume for now that I will modify Watten.py in the NEXT step to accept initial_geber_index.
        # For this app.py change, I'll prepare for it.
        initial_geber_idx = 0 if force_human_role == 'geber' else (1 if force_human_role == 'nehmer' else None)
        game_instance = Watten_Zwei_Spieler([human_player, bot_player], initial_geber_idx=initial_geber_idx)

    elif force_human_role == 'nehmer':
        players = [human_player, bot_player] # Human still at index 0 for consistency in app.py
        initial_geber_idx = 1 # Bot is Geber
        game_instance = Watten_Zwei_Spieler([human_player, bot_player], initial_geber_idx=initial_geber_idx)
    else: # No forcing, random assignment
        game_instance = Watten_Zwei_Spieler([human_player, bot_player]) # Original random assignment

    print(f"New game started with {bot_player.name}. Forced role: {force_human_role}. Actual Geber: {game_instance.get_geber().name}")
    print(f"Human hand: {[str(c) for c in human_player.hand]}") # May be empty until after abheben/dealing
    
    return jsonify(get_game_state_json(game_instance))

@app.route('/game/state', methods=['GET'])
def game_state_endpoint():
    # game_instance is global, directly accessible
    if not game_instance:
        return jsonify({"error": "No game in progress"}), 404
    return jsonify(get_game_state_json(game_instance))

def get_game_state_json(current_game): # Accepts current_game instance
    if not current_game:
        return {"error": "No game in progress", "game_over_message": "No game. Start a new one!"}

    human_player_instance = current_game.get_human_player()
    bot_player_instance = current_game.get_bot_player()

    if not human_player_instance or not bot_player_instance:
         return {"error": "Player instances not found", "game_over_message": "Error with players. Start new game!"}


    is_human_geber = (current_game.get_geber() == human_player_instance)
    is_human_turn = current_game.current_player_on_turn == human_player_instance

    # Determine current player and game phase from Watten.py
    current_turn_player_name = current_game.current_player_on_turn.name if current_game.current_player_on_turn else "N/A"
    game_phase_from_engine = current_game.current_phase
    
    # Build possible_actions based on current_game state
    possible_actions = []
    if current_game.current_player_on_turn == human_player_instance and current_game.current_phase != PHASE_GAME_OVER:
        if current_game.current_phase == "AWAITING_SCHLAG_CHOICE": # Watten.PHASE_AWAITING_SCHLAG_CHOICE
            possible_actions = [{"type": "CHOOSE_SCHLAG", "options": ["7", "8", "9", "10", "Unter", "Ober", "König", "Sau"]}]
        elif current_game.current_phase == "AWAITING_TRUMP_CHOICE": # Watten.PHASE_AWAITING_TRUMP_CHOICE
            possible_actions = [{"type": "CHOOSE_TRUMP", "options": ["Herz", "Schelle", "Eichel", "Laub"]}]
        elif current_game.current_phase == "AWAITING_CARD_PLAY": # Watten.PHASE_AWAITING_CARD_PLAY
            possible_actions = [{"type": "PLAY_CARD", "options": [str(c) for c in human_player_instance.hand]}]
            # Ausschaffen logic should be driven by Watten.py internal state (e.g. player.darf_ausschaffen)
            # And if it's a valid moment (e.g. start of trick, before card play)
            # For now, simplified: if it's your turn to play and you can offer
            if human_player_instance.darf_ausschaffen and not human_player_instance.ist_gespannt:
                 possible_actions.append({"type": "AUSSCHAFFEN"})
        elif current_game.current_phase == "AWAITING_AUSSCHAFFEN_RESPONSE":
            possible_actions.append({"type": "MITGEHEN"})
            possible_actions.append({"type": "NICHT_MITGEHEN"})
        elif current_game.current_phase == "AWAITING_ABHEBEN_DECISION":
             possible_actions.append({"type": "ABHEBEN_JA"})
             possible_actions.append({"type": "ABHEBEN_NEIN"})


    game_over_msg = None
    if current_game.current_phase == PHASE_GAME_OVER: # Watten.PHASE_GAME_OVER
        winner = max(current_game.Spielerliste, key=lambda s: s.Punktestand)
        game_over_msg = f"GAME OVER! {winner.name} wins with {winner.Punktestand} points!"
        current_turn_player_name = "N/A" # No turns if game over
        is_human_turn = False

    state = {
        "player_hand": [str(card) for card in human_player_instance.hand],
        "opponent_name": bot_player_instance.name, # Added opponent name
        "opponent_card_count": len(bot_player_instance.hand),
        "player_score": human_player_instance.Punktestand,
        "opponent_score": bot_player_instance.Punktestand,
        "player_tricks_round": human_player_instance.gewonnene_Stiche,
        "opponent_tricks_round": bot_player_instance.gewonnene_Stiche,
        "current_player_turn": current_turn_player_name,
        "human_is_geber": is_human_geber,
        "is_human_turn": is_human_turn,
        "human_player_name": human_player_instance.name,
        "geber_name": current_game.get_geber().name,
        "nehmer_name": current_game.get_nehmer().name,
        "schlag": current_game.schlag,
        "trump_suit": current_game.farbe,
        "round_points_value": current_game.punkte_für_stich,
        "player_is_gespannt": human_player_instance.ist_gespannt,
        "opponent_is_gespannt": bot_player_instance.ist_gespannt,
        "game_phase": game_phase_from_engine,
        "possible_actions": possible_actions,
        "stiche_bisher_player": [str(s) for s in current_game.stiche_bisher[human_player_instance]],
        "stiche_bisher_opponent": [str(s) for s in current_game.stiche_bisher[bot_player_instance]],
        "last_played_card_player": str(human_player_instance.stich) if human_player_instance.stich else "",
        "last_played_card_opponent": str(bot_player_instance.stich) if bot_player_instance.stich else "",
        "message": f"Phase: {game_phase_from_engine}. Turn: {current_turn_player_name}.",
        "game_over_message": game_over_msg
    }
    return state

@app.route('/game/action', methods=['POST'])
def game_action():
    global game_instance # Still using global game_instance for actions
    if not game_instance or game_instance.current_phase == PHASE_GAME_OVER:
        return jsonify({"error": "No active game or game is over"}), 400

    data = request.get_json()
    action_type = data.get('type')
    value = data.get('value')

    human_player = game_instance.get_human_player()
    response_message = f"Action {action_type} received."
    action_processed_successfully = False

    try:
        if game_instance.current_player_on_turn != human_player and \
           action_type not in ["ABHEBEN_JA", "ABHEBEN_NEIN", "MITGEHEN", "NICHT_MITGEHEN"]: # Some actions are responses not active turns
             # Recheck this condition. ABHEBEN is human's turn. MITGEHEN is human's turn.
             pass # Let specific handlers check turns more accurately.

        if action_type == "CHOOSE_SCHLAG":
            if game_instance.current_phase == "AWAITING_SCHLAG_CHOICE" and game_instance.current_player_on_turn == human_player:
                game_instance.set_schlag(value)
                response_message = f"Schlag chosen: {value}."
                action_processed_successfully = True
                if game_instance.current_player_on_turn == game_instance.get_bot_player(): # If bot's turn for trump
                    bot_trump_choice = game_instance.get_bot_player().wählt_farbe(game_instance.erste_karte_wurde_abgehoben)
                    game_instance.set_trump(bot_trump_choice)
                    response_message += f" Bot chose trump: {bot_trump_choice}."
            else: return jsonify({"error": "Not your turn or not correct phase for Schlag."}), 400
        
        elif action_type == "CHOOSE_TRUMP":
            if game_instance.current_phase == "AWAITING_TRUMP_CHOICE" and game_instance.current_player_on_turn == human_player:
                game_instance.set_trump(value)
                response_message = f"Trump chosen: {value}."
                action_processed_successfully = True
                # If bot is next to play, Watten.py's set_trump would call process_bot_play_card
            else: return jsonify({"error": "Not your turn or not correct phase for Trump."}), 400

        elif action_type == "PLAY_CARD":
            if game_instance.current_phase == "AWAITING_CARD_PLAY" and game_instance.current_player_on_turn == human_player:
                card_to_play = None
                for card_in_hand in human_player.hand:
                    if str(card_in_hand) == value:
                        card_to_play = card_in_hand
                        break
                if card_to_play:
                    # game_instance.process_play_card will handle removing card from hand
                    game_instance.process_play_card(human_player, card_to_play)
                    response_message = f"You played: {value}."
                    action_processed_successfully = True
                    # If trick is complete, app.py needs to call evaluate_trick
                    if game_instance.Spielerliste[0].stich and game_instance.Spielerliste[1].stich:
                        game_instance.evaluate_trick()
                        # If round is over, app.py needs to call process_round_winner
                        if game_instance.check_round_over(game_instance.trick_leader): # trick_leader is winner of last trick
                            game_instance.process_round_winner()
                else: return jsonify({"error": "Card not in hand."}), 400
            else: return jsonify({"error": "Not your turn or not correct phase for playing card."}), 400
        
        elif action_type == "AUSSCHAFFEN":
            if game_instance.current_phase == "AWAITING_CARD_PLAY" and game_instance.current_player_on_turn == human_player and human_player.darf_ausschaffen:
                result = game_instance.handle_ausschaffen_offer(human_player)
                response_message = result["message"]
                action_processed_successfully = True
                if result.get("folded") or result.get("proceed") == False: # Opponent folded or cannot ausschaffen
                    if game_instance.check_round_over(None): # Pass None as last_trick_winner if fold decided it
                         game_instance.process_round_winner()
            else: return jsonify({"error": "Cannot ausschaffen now."}), 400

        elif action_type == "MITGEHEN" or action_type == "NICHT_MITGEHEN":
            if game_instance.current_phase == "AWAITING_AUSSCHAFFEN_RESPONSE" and game_instance.current_player_on_turn == human_player:
                accepts = action_type == "MITGEHEN"
                result = game_instance.handle_ausschaffen_response(human_player, accepts)
                response_message = result["message"]
                action_processed_successfully = True
                if result.get("folded"): # Human folded or Bot folded
                    if game_instance.check_round_over(None):
                        game_instance.process_round_winner()
            else: return jsonify({"error": "Not correct phase to respond to ausschaffen."}), 400
        
        elif action_type == "ABHEBEN_JA" or action_type == "ABHEBEN_NEIN":
            if game_instance.current_phase == "AWAITING_ABHEBEN_DECISION" and game_instance.current_player_on_turn == human_player:
                takes_card = action_type == "ABHEBEN_JA"
                game_instance.process_abheben_decision(takes_card)
                response_message = f"Abheben decision processed: {'Took card.' if takes_card else 'Did not take card.'}"
                action_processed_successfully = True
                # process_abheben_decision should transition phase and handle bot turn if needed
            else: return jsonify({"error": "Not correct phase for abheben decision."}), 400

        else:
            return jsonify({"error": "Unknown action type"}), 400

    except Exception as e:
        print(f"Error during action {action_type}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    final_state = get_game_state_json(game_instance)
    # game_over_message is now part of final_state by get_game_state_json
    return jsonify({"message": response_message, "new_state": final_state})


if __name__ == '__main__':
    # Make sure static files are findable if app.py is not in the root
    # For simple cases where app.py is at root, Flask's default static_folder='static' works
    app.run(debug=True, port=5001)
