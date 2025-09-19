document.addEventListener('DOMContentLoaded', () => {
    const geb = (id) => document.getElementById(id);

    const elements = {
        newGameBtn: geb('new-game-btn'),
        botSelect: geb('bot-select'),
        gameMessage: geb('game-message'),
        gameOverMessage: geb('game-over-message'),
        roundPointsValue: geb('round-points-value'),
        geberName: geb('geber-name'),
        nehmerName: geb('nehmer-name'),
        currentTrumpSuit: geb('current-trump-suit'),
        currentSchlag: geb('current-schlag'),
        currentPlayerTurn: geb('current-player-turn'),
        turnIndicator: geb('turn-indicator'),
        gamePhase: geb('game-phase'),
        opponent: {
            panel: geb('opponent-panel'),
            name: geb('opponent-name'),
            role: geb('opponent-role'),
            score: geb('opponent-score'),
            scoreMeter: geb('opponent-score-meter'),
            tricks: geb('opponent-tricks-round'),
            cardCount: geb('opponent-card-count'),
            gespannStatus: geb('opponent-is-gespannt'),
            playedCard: geb('opponent-played-card'),
            history: geb('opponent-stiche-history'),
            hand: geb('opponent-hand'),
        },
        player: {
            panel: geb('player-panel'),
            name: geb('player-name'),
            role: geb('player-role'),
            score: geb('player-score'),
            scoreMeter: geb('player-score-meter'),
            tricks: geb('player-tricks-round'),
            cardCount: geb('player-card-count'),
            gespannStatus: geb('player-is-gespannt'),
            playedCard: geb('player-played-card'),
            history: geb('player-stiche-history'),
            hand: geb('player-hand'),
        },
        choicesArea: geb('choices-area'),
        actionsHint: geb('actions-hint'),
        logList: geb('log-list'),
        clearLogBtn: geb('clear-log-btn'),
    };

    const ACTION_LABELS = {
        CHOOSE_SCHLAG: 'Choose Schlag',
        CHOOSE_TRUMP: 'Choose Trump Suit',
        PLAY_CARD: 'Play Card',
        AUSSCHAFFEN: 'Raise (Ausschaffen)',
        MITGEHEN: 'Call (Mitgehen)',
        NICHT_MITGEHEN: 'Fold (Nicht Mitgehen)',
        ABHEBEN_JA: 'Take the Revealed Card',
        ABHEBEN_NEIN: 'Leave the Revealed Card',
    };

    const SUIT_SYMBOLS = {
        Herz: '♥',
        Schelle: '♦',
        Eichel: '♣',
        Laub: '♠',
    };

    const SUIT_NAMES = {
        Herz: 'Herz',
        Schelle: 'Schelle',
        Eichel: 'Eichel',
        Laub: 'Laub',
    };

    const VICTORY_POINTS = 15;
    const LOG_LIMIT = 40;

    let currentGameState = null;
    let autoRefreshHandle = null;
    let previousStateSnapshot = null;

    function setLoadingState(isLoading) {
        elements.newGameBtn.disabled = isLoading;
        elements.botSelect.disabled = isLoading;
        document.body.classList.toggle('is-loading', isLoading);
    }

    function setBotSelectAvailability(state) {
        const hasActiveRound = state && !state.game_over_message && (state.player_hand || []).length > 0;
        elements.botSelect.disabled = hasActiveRound;
        elements.newGameBtn.textContent = hasActiveRound ? 'Restart Match' : 'Start Match';
        if (!hasActiveRound && !document.body.classList.contains('is-loading')) {
            elements.newGameBtn.disabled = false;
        }
    }

    function setActionsHint(text) {
        if (elements.actionsHint) {
            elements.actionsHint.textContent = text;
        }
    }

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
            elements.gameMessage.textContent = `API Error: ${error.message}`;
            pushLog(`API error: ${error.message}`, 'system');
            throw error;
        }
    }

    async function startNewGame() {
        const selectedBotType = elements.botSelect.value;
        const selectedBotName = elements.botSelect.options[elements.botSelect.selectedIndex].text;
        setLoadingState(true);
        setActionsHint(`Starting new game vs ${selectedBotName}...`);
        pushLog(`Starting new match against ${selectedBotName}.`, 'system');
        try {
            const data = await fetchApi('/game/new', 'POST', { bot_type: selectedBotType });
            previousStateSnapshot = null;
            updateUI(data, { highlightStart: true });
        } catch (error) {
            // handled in fetchApi
        } finally {
            setLoadingState(false);
        }
    }

    async function sendGameAction(actionType, value = null) {
        if (!actionType) return;
        let actionLabel = ACTION_LABELS[actionType] || actionType;
        if (value) {
            actionLabel += `: ${value}`;
        }
        setActionsHint(`Sending ${actionLabel}...`);
        pushLog(`You selected ${actionLabel}.`, 'action');
        try {
            const payload = { type: actionType };
            if (value !== null) payload.value = value;
            const response = await fetchApi('/game/action', 'POST', payload);
            updateUI(response.new_state, { actionMessage: response.message });
        } catch (error) {
            // Error already surfaced via fetchApi
        }
    }

    function formatCardLabel(cardStr) {
        if (!cardStr) return '–';
        const parts = cardStr.split(' ');
        if (parts.length < 2) return cardStr;
        const value = parts[0];
        const suit = parts.slice(1).join(' ');
        const symbol = SUIT_SYMBOLS[suit] || '';
        return symbol ? `${symbol} ${value}` : `${value} ${suit}`;
    }

    function renderOpponentHand(cardCount) {
        elements.opponent.hand.innerHTML = '';
        if (!cardCount) {
            const empty = document.createElement('span');
            empty.className = 'empty-hand';
            empty.textContent = 'No cards remaining';
            elements.opponent.hand.appendChild(empty);
            return;
        }
        for (let i = 0; i < cardCount; i += 1) {
            const cardBack = document.createElement('div');
            cardBack.className = 'card-back';
            elements.opponent.hand.appendChild(cardBack);
        }
    }

    function renderHistory(targetElement, entries) {
        if (!targetElement) return;
        targetElement.textContent = entries && entries.length ? entries.join(' • ') : '–';
    }

    function updateScoreMeter(meterElement, scoreValue) {
        if (!meterElement) return;
        const fill = meterElement.querySelector('.meter-fill');
        const label = meterElement.querySelector('.meter-label');
        const normalizedScore = Number.isFinite(scoreValue) ? scoreValue : 0;
        const percent = Math.max(0, Math.min(100, (normalizedScore / VICTORY_POINTS) * 100));
        if (fill) fill.style.width = `${percent}%`;
        if (label) label.textContent = `${normalizedScore} / ${VICTORY_POINTS} pts`;
        meterElement.setAttribute('aria-valuenow', normalizedScore);
    }

    function updateStatePill(pillElement, isGespannt) {
        if (!pillElement) return;
        if (isGespannt) {
            pillElement.textContent = 'Gespannt';
            pillElement.classList.add('is-alert');
        } else {
            pillElement.textContent = 'Calm';
            pillElement.classList.remove('is-alert');
        }
    }

    function renderPlayerHand(hand, possibleActions, isHumanTurn) {
        const handContainer = elements.player.hand;
        handContainer.innerHTML = '';
        elements.player.cardCount.textContent = hand ? hand.length : 0;
        if (!hand || hand.length === 0) {
            const empty = document.createElement('span');
            empty.className = 'empty-hand';
            empty.textContent = 'No cards in hand';
            handContainer.appendChild(empty);
            return;
        }

        const playableOptions = (possibleActions || []).find((action) => action.type === 'PLAY_CARD');
        const allowedCards = playableOptions && playableOptions.options ? playableOptions.options : [];

        hand.forEach((cardStr) => {
            const cardButton = document.createElement('button');
            cardButton.type = 'button';
            cardButton.className = 'card';
            cardButton.dataset.cardValue = cardStr;

            const parts = cardStr.split(' ');
            const value = parts[0];
            const suit = parts.slice(1).join(' ');
            const symbol = SUIT_SYMBOLS[suit] || '';

            cardButton.innerHTML = `
                <span class="card-value">${value}</span>
                <span class="card-suit">${symbol ? `${symbol} ` : ''}${SUIT_NAMES[suit] || suit}</span>
            `;

            const cardIsAllowed = !allowedCards.length || allowedCards.includes(cardStr);
            const shouldEnable = isHumanTurn && cardIsAllowed;
            if (!shouldEnable) {
                cardButton.disabled = true;
                cardButton.classList.add('disabled');
            } else {
                cardButton.classList.add('is-playable');
                cardButton.addEventListener('click', () => sendGameAction('PLAY_CARD', cardStr));
            }

            handContainer.appendChild(cardButton);
        });
    }

    function renderActionChoices(possibleActions, state) {
        const container = elements.choicesArea;
        container.innerHTML = '';
        const isGameOver = !!state.game_over_message;
        const isHumanTurn = !!state.is_human_turn;

        if (isGameOver) {
            setActionsHint('Game over. Start a new match when ready.');
            return;
        }

        if (!possibleActions || possibleActions.length === 0) {
            if (state.current_player_turn && !isHumanTurn) {
                setActionsHint(`Waiting for ${state.current_player_turn}...`);
            } else {
                setActionsHint('No actions available right now.');
            }
            return;
        }

        setActionsHint(isHumanTurn ? 'Choose your next move.' : `Waiting for ${state.current_player_turn}...`);

        possibleActions.forEach((action) => {
            if (action.type === 'PLAY_CARD') {
                // PLAY_CARD is handled by the hand renderer
                return;
            }

            const group = document.createElement('div');
            group.className = 'action-group';
            const title = document.createElement('h3');
            title.textContent = ACTION_LABELS[action.type] || action.type;
            group.appendChild(title);

            const buttonWrap = document.createElement('div');
            buttonWrap.className = 'option-buttons';

            if (action.options && action.options.length) {
                action.options.forEach((optionValue) => {
                    const optionBtn = document.createElement('button');
                    optionBtn.type = 'button';
                    optionBtn.className = 'action-btn';
                    optionBtn.textContent = formatActionOptionLabel(action.type, optionValue);
                    optionBtn.addEventListener('click', () => sendGameAction(action.type, optionValue));
                    buttonWrap.appendChild(optionBtn);
                });
            } else {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'action-btn';
                button.textContent = ACTION_LABELS[action.type] || action.type;
                button.addEventListener('click', () => sendGameAction(action.type));
                buttonWrap.appendChild(button);
            }

            group.appendChild(buttonWrap);
            container.appendChild(group);
        });
    }

    function formatActionOptionLabel(actionType, optionValue) {
        if (actionType === 'CHOOSE_TRUMP') {
            const symbol = SUIT_SYMBOLS[optionValue] || '';
            return symbol ? `${symbol} ${SUIT_NAMES[optionValue] || optionValue}` : optionValue;
        }
        return optionValue;
    }

    function scheduleAutoRefresh(state) {
        if (autoRefreshHandle) {
            clearTimeout(autoRefreshHandle);
            autoRefreshHandle = null;
        }
        if (!state || state.game_over_message) return;
        if (state.is_human_turn) return;
        if (!state.current_player_turn || ['–', 'N/A'].includes(state.current_player_turn)) return;
        autoRefreshHandle = setTimeout(async () => {
            try {
                const latest = await fetchApi('/game/state');
                updateUI(latest);
            } catch (error) {
                // Already surfaced elsewhere
            }
        }, 900);
    }

    function pushLog(message, tag = 'info') {
        if (!elements.logList) return;
        const entry = document.createElement('li');
        entry.className = `log-entry ${tag}`;
        entry.dataset.tag = tag;
        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const text = document.createElement('span');
        text.textContent = message;
        entry.appendChild(timestamp);
        entry.appendChild(text);
        elements.logList.prepend(entry);
        while (elements.logList.children.length > LOG_LIMIT) {
            elements.logList.removeChild(elements.logList.lastChild);
        }
    }

    function logStateTransitions(previousState, nextState, options = {}) {
        if (!nextState) return;
        const { actionMessage, highlightStart } = options;

        if (highlightStart) {
            pushLog('New round initialized.', 'system');
        }

        if (actionMessage) {
            pushLog(actionMessage, 'action');
        }

        if (!previousState) {
            pushLog(`Phase: ${nextState.game_phase}.`, 'phase');
            pushLog(`Turn: ${nextState.current_player_turn || 'N/A'}.`, 'turn');
            return;
        }

        if (previousState.game_phase !== nextState.game_phase) {
            pushLog(`Phase changed to ${nextState.game_phase}.`, 'phase');
        }

        if (previousState.current_player_turn !== nextState.current_player_turn) {
            pushLog(`It is now ${nextState.current_player_turn || 'no one's'} turn.`, 'turn');
        }

        if (previousState.player_score !== nextState.player_score || previousState.opponent_score !== nextState.opponent_score) {
            pushLog(`Score update — You: ${nextState.player_score} | Opponent: ${nextState.opponent_score}.`, 'score');
        }

        const prevPlayerCard = previousState.last_played_card_player || '';
        const prevOpponentCard = previousState.last_played_card_opponent || '';
        const nextPlayerCard = nextState.last_played_card_player || '';
        const nextOpponentCard = nextState.last_played_card_opponent || '';

        if (prevPlayerCard !== nextPlayerCard && nextPlayerCard) {
            pushLog(`You played ${formatCardLabel(nextPlayerCard)}.`, 'action');
        }
        if (prevOpponentCard !== nextOpponentCard && nextOpponentCard) {
            pushLog(`${nextState.opponent_name} played ${formatCardLabel(nextOpponentCard)}.`, 'action');
        }

        if (nextState.game_over_message && previousState.game_over_message !== nextState.game_over_message) {
            pushLog(nextState.game_over_message, 'system');
        }
    }

    function updateTurnIndicator(state) {
        const isGameOver = !!state.game_over_message;
        const isHumanTurn = !!state.is_human_turn;
        let indicatorText = 'Waiting';
        if (isGameOver) {
            indicatorText = 'Finished';
        } else if (isHumanTurn) {
            indicatorText = 'Your move';
        } else if (state.current_player_turn) {
            indicatorText = `Waiting`;
        }
        elements.turnIndicator.textContent = indicatorText;
    }

    function updateBodyState(state) {
        const isGameOver = !!state.game_over_message;
        document.body.classList.toggle('game-over', isGameOver);
        const turnValue = isGameOver ? 'none' : (state.is_human_turn ? 'human' : 'opponent');
        document.body.setAttribute('data-turn', turnValue);
        elements.player.panel.classList.toggle('is-active', state.is_human_turn && !isGameOver);
        elements.opponent.panel.classList.toggle('is-active', !state.is_human_turn && !isGameOver);
    }

    function updateUI(state, options = {}) {
        if (!state || state.error) {
            elements.gameMessage.textContent = state ? state.error : 'Failed to update UI or no state received.';
            elements.gameOverMessage.textContent = '';
            return;
        }

        currentGameState = state;

        const displayMessage = options.actionMessage || state.message || 'State updated.';
        elements.gameMessage.textContent = displayMessage;
        elements.gameOverMessage.textContent = state.game_over_message || '';

        elements.currentTrumpSuit.textContent = state.trump_suit ? formatActionOptionLabel('CHOOSE_TRUMP', state.trump_suit) : '–';
        elements.currentSchlag.textContent = state.schlag || '–';
        elements.currentPlayerTurn.textContent = state.current_player_turn || '–';
        elements.gamePhase.textContent = state.game_phase || '–';
        elements.roundPointsValue.textContent = state.round_points_value !== undefined ? state.round_points_value : '–';
        elements.geberName.textContent = state.geber_name || '–';
        elements.nehmerName.textContent = state.nehmer_name || '–';

        elements.opponent.name.textContent = state.opponent_name || 'Opponent';
        elements.opponent.role.textContent = state.human_is_geber ? 'Nehmer' : 'Geber';
        elements.opponent.score.textContent = state.opponent_score ?? 0;
        elements.opponent.tricks.textContent = state.opponent_tricks_round ?? 0;
        elements.opponent.cardCount.textContent = state.opponent_card_count ?? 0;
        elements.opponent.playedCard.textContent = formatCardLabel(state.last_played_card_opponent);
        renderHistory(elements.opponent.history, state.stiche_bisher_opponent || []);
        renderOpponentHand(state.opponent_card_count || 0);
        updateScoreMeter(elements.opponent.scoreMeter, state.opponent_score ?? 0);
        updateStatePill(elements.opponent.gespannStatus, state.opponent_is_gespannt);

        const playerHand = state.player_hand || [];
        elements.player.name.textContent = state.human_player_name || 'You';
        elements.player.role.textContent = state.human_is_geber ? 'Geber' : 'Nehmer';
        elements.player.score.textContent = state.player_score ?? 0;
        elements.player.tricks.textContent = state.player_tricks_round ?? 0;
        elements.player.playedCard.textContent = formatCardLabel(state.last_played_card_player);
        renderHistory(elements.player.history, state.stiche_bisher_player || []);
        updateScoreMeter(elements.player.scoreMeter, state.player_score ?? 0);
        updateStatePill(elements.player.gespannStatus, state.player_is_gespannt);
        renderPlayerHand(playerHand, state.possible_actions || [], state.is_human_turn);

        renderActionChoices(state.possible_actions || [], state);
        updateTurnIndicator(state);
        updateBodyState(state);
        setBotSelectAvailability(state);
        logStateTransitions(previousStateSnapshot, state, options);
        previousStateSnapshot = JSON.parse(JSON.stringify(state));
        scheduleAutoRefresh(state);
    }

    elements.newGameBtn.addEventListener('click', startNewGame);
    elements.clearLogBtn.addEventListener('click', () => {
        if (elements.logList) {
            elements.logList.innerHTML = '';
        }
    });

    updateUI({
        message: "Welcome! Select a bot and click 'Start Match' to begin.",
        player_hand: [],
        possible_actions: [],
        game_phase: 'Not started',
        game_over_message: null,
        round_points_value: '–',
        geber_name: '–',
        nehmer_name: '–',
        trump_suit: '–',
        schlag: '–',
        current_player_turn: '–',
        opponent_name: 'Opponent',
        opponent_score: 0,
        opponent_tricks_round: 0,
        opponent_card_count: 0,
        opponent_is_gespannt: false,
        stiche_bisher_opponent: [],
        player_score: 0,
        player_tricks_round: 0,
        player_is_gespannt: false,
        stiche_bisher_player: [],
        human_is_geber: false,
        is_human_turn: false,
        human_player_name: 'You',
    });
});
