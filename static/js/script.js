document.addEventListener('DOMContentLoaded', () => {
    const geb = (id) => document.getElementById(id); // Helper
    // --- UI Elements ---
    const newGameBtn = geb('new-game-btn');
    const botSelectEl = geb('bot-select'); // Added bot selector
    const gameMessageEl = geb('game-message');
    const gameOverMessageEl = geb('game-over-message');
    const roundPointsValueEl = geb('round-points-value');
    const geberNameEl = geb('geber-name');
    const nehmerNameEl = geb('nehmer-name');
    const currentTrumpSuitEl = geb('current-trump-suit');
    const currentSchlagEl = geb('current-schlag');
    const currentPlayerTurnEl = geb('current-player-turn');
    const gamePhaseEl = geb('game-phase');

    const opponentScoreEl = geb('opponent-score');
    const opponentTricksEl = geb('opponent-tricks-round');
    const opponentCardCountEl = geb('opponent-card-count');
    const opponentIsGespanntEl = geb('opponent-is-gespannt');
    const opponentPlayedCardEl = geb('opponent-played-card');
    const opponentSticheHistoryEl = geb('opponent-stiche-history');
    const opponentNameEl = geb('opponent-role'); // To update bot name

    const playerScoreEl = geb('player-score');
    const playerTricksEl = geb('player-tricks-round');
    const playerIsGespanntEl = geb('player-is-gespannt');
    const playerHandEl = geb('player-hand');
    const playerPlayedCardEl = geb('player-played-card');
    const playerSticheHistoryEl = geb('player-stiche-history');
    const choicesAreaEl = geb('choices-area');

    let currentGameState = {}; // Store the latest state

    async function fetchApi(endpoint, method = 'GET', body = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);
        try {
            const response = await fetch(endpoint, options);
            const data = await response.json(); 
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! Status: ${response.status}`);
            }
            return data;
        } catch (error) {
            console.error(`API error calling ${endpoint}:`, error);
            gameMessageEl.textContent = `API Error: ${error.message}`;
            throw error;
        }
    }

    async function startNewGame() {
        const selectedBotType = botSelectEl.value;
        const selectedBotName = botSelectEl.options[botSelectEl.selectedIndex].text;
        gameMessageEl.textContent = `Starting new game against ${selectedBotName}...`;
        gameOverMessageEl.textContent = ''; 
        try {
            // Pass the selected bot_type in the POST request body
            const data = await fetchApi('/game/new', 'POST', { bot_type: selectedBotType });
            updateUI(data); 
        } catch (error) { /* Handled in fetchApi */ }
    }

    async function sendGameAction(actionType, value = null) {
        gameMessageEl.textContent = `Sending: ${actionType}...`;
        try {
            const payload = { type: actionType };
            if (value !== null) payload.value = value;
            const response = await fetchApi('/game/action', 'POST', payload);
            updateUI(response.new_state);
            gameMessageEl.textContent = response.message || "Action processed.";
            if (response.new_state && response.new_state.game_over_message) {
                gameOverMessageEl.textContent = response.new_state.game_over_message;
            }
        } catch (error) { /* Handled in fetchApi */ }
    }
    
    function renderPlayerHand(hand, possible_actions, game_phase) {
        playerHandEl.innerHTML = '';
        if (!hand) return;

        const can_play_card_action = possible_actions.find(a => a.type === "PLAY_CARD");
        const allowed_cards_to_play = can_play_card_action ? can_play_card_action.options : [];

        hand.forEach(cardStr => {
            const cardButton = document.createElement('button');
            cardButton.classList.add('card');
            cardButton.textContent = cardStr;
            cardButton.dataset.cardValue = cardStr;
            
            if (game_phase === "play_card" && can_play_card_action && allowed_cards_to_play.includes(cardStr)) {
                cardButton.disabled = false;
                cardButton.addEventListener('click', () => sendGameAction('PLAY_CARD', cardStr));
            } else {
                cardButton.disabled = true;
            }
            playerHandEl.appendChild(cardButton);
        });
    }

    function renderActionChoices(possibleActions, game_phase, is_game_over) {
        choicesAreaEl.innerHTML = '';
        if (is_game_over || !possibleActions) return;

        possibleActions.forEach(action => {
            if (action.type === "PLAY_CARD") return; 

            if (action.type === "CHOOSE_SCHLAG" || action.type === "CHOOSE_TRUMP") {
                action.options.forEach(optionValue => {
                    const button = document.createElement('button');
                    button.textContent = `${action.type.replace("CHOOSE_", "")}: ${optionValue}`;
                    // Enable based on game_phase and if it's the correct player's turn (implicitly handled by possible_actions from backend)
                    button.disabled = !(game_phase === "choose_schlag" && action.type === "CHOOSE_SCHLAG") && 
                                      !(game_phase === "choose_trump" && action.type === "CHOOSE_TRUMP");
                    button.addEventListener('click', () => sendGameAction(action.type, optionValue));
                    choicesAreaEl.appendChild(button);
                });
            } else if (action.type === "AUSSCHAFFEN" || action.type === "MITGEHEN" || action.type === "NICHT_MITGEHEN") {
                 const button = document.createElement('button');
                 button.textContent = action.type.replace("_", " "); 
                 // Enable if present in possible_actions. Backend should ensure these are only sent when valid.
                 button.disabled = false; 
                 button.addEventListener('click', () => sendGameAction(action.type));
                 choicesAreaEl.appendChild(button);
            }
        });
    }

    function updateUI(state) {
        if (!state || state.error) {
            gameMessageEl.textContent = state ? state.error : "Failed to update UI or no state received.";
            console.error("State error or no state:", state);
            // Don't disable new game button if there's an error, allow user to try again
            newGameBtn.disabled = false; 
            botSelectEl.disabled = false;
            return;
        }
        currentGameState = state; 

        gameMessageEl.textContent = state.message || "State updated.";
        if(state.game_over_message) {
            gameOverMessageEl.textContent = state.game_over_message;
        } else {
            gameOverMessageEl.textContent = '';
        }

        roundPointsValueEl.textContent = state.round_points_value !== undefined ? state.round_points_value : 'N/A';
        geberNameEl.textContent = state.geber_name || 'N/A';
        nehmerNameEl.textContent = state.nehmer_name || 'N/A';
        currentTrumpSuitEl.textContent = state.trump_suit || 'N/A';
        currentSchlagEl.textContent = state.schlag || 'N/A';
        currentPlayerTurnEl.textContent = state.current_player_turn || 'N/A';
        gamePhaseEl.textContent = state.game_phase || 'N/A';

        opponentNameEl.textContent = state.opponent_name || 'Bot'; // Update opponent name
        opponentScoreEl.textContent = state.opponent_score !== undefined ? state.opponent_score : '0';
        opponentTricksEl.textContent = state.opponent_tricks_round !== undefined ? state.opponent_tricks_round : '0';
        opponentCardCountEl.textContent = state.opponent_card_count !== undefined ? state.opponent_card_count : '0';
        opponentIsGespanntEl.textContent = state.opponent_is_gespannt ? 'Yes' : 'No';
        opponentPlayedCardEl.textContent = state.last_played_card_opponent || '';
        opponentSticheHistoryEl.textContent = (state.stiche_bisher_opponent || []).join('; ');

        playerScoreEl.textContent = state.player_score !== undefined ? state.player_score : '0';
        playerTricksEl.textContent = state.player_tricks_round !== undefined ? state.player_tricks_round : '0';
        playerIsGespanntEl.textContent = state.player_is_gespannt ? 'Yes' : 'No';
        playerPlayedCardEl.textContent = state.last_played_card_player || '';
        playerSticheHistoryEl.textContent = (state.stiche_bisher_player || []).join('; ');
        
        const is_game_over = !!state.game_over_message;

        renderPlayerHand(state.player_hand, state.possible_actions || [], state.game_phase);
        renderActionChoices(state.possible_actions || [], state.game_phase, is_game_over);
        
        // Enable/disable controls based on game state
        newGameBtn.disabled = !is_game_over && Object.keys(currentGameState).length > 0 && currentGameState.error == null;
        botSelectEl.disabled = !is_game_over && Object.keys(currentGameState).length > 0 && currentGameState.error == null;

        if (is_game_over) {
            newGameBtn.disabled = false;
            botSelectEl.disabled = false;
        }
    }

    newGameBtn.addEventListener('click', startNewGame);
    // Initialize UI for a fresh page load (no game started)
    updateUI({ 
        message: "Welcome! Select a bot and click 'New Game' to begin.",
        player_hand: [],
        possible_actions: [],
        game_phase: 'Startup',
        game_over_message: null, // Ensure no old game over message is shown
        // Initialize other fields to default/empty values
        round_points_value: "N/A", geber_name: "N/A", nehmer_name: "N/A",
        current_trump_suit: "N/A", current_schlag: "N/A", current_player_turn: "N/A",
        opponent_name: "Bot", opponent_score: 0, opponent_tricks_round: 0, opponent_card_count: 0, opponent_is_gespannt: false, last_played_card_opponent: "", stiche_bisher_opponent: [],
        player_score: 0, player_tricks_round: 0, player_is_gespannt: false, last_played_card_player: "", stiche_bisher_player: []
    });
    newGameBtn.disabled = false; // Ensure new game button is enabled at start
    botSelectEl.disabled = false; // Ensure bot select is enabled at start
});
