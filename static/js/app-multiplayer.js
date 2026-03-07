function initMultiplayer() {
    if (!window.QUIZFLOW_IS_LOGGED_IN) {
        window.location.href = '/auth/login/?next=/multiplayer/';
        return;
    }

    const setupForm = document.getElementById('multiplayerSetupForm');
    const quizSelect = document.getElementById('multiplayerQuizSelect');

    if (!setupForm || !quizSelect) {
        return;
    }

    quizSelect.innerHTML = `
        <option value="" selected disabled>Quiz seçin</option>
        ${quizData.quizzes.map(quiz => `<option value="${quiz.id}">${quiz.title}</option>`).join('')}
    `;

    const urlParams = new URLSearchParams(window.location.search);
    const presetQuizId = urlParams.get('id');
    if (presetQuizId && getQuizById(presetQuizId)) {
        quizSelect.value = presetQuizId;
    }

    setupForm.addEventListener('submit', startMultiplayerQuiz);
    setMultiplayerView('setup');
}

function startMultiplayerQuiz(event) {
    event.preventDefault();

    const quizId = document.getElementById('multiplayerQuizSelect').value;
    const playerOneName = document.getElementById('playerOneName').value.trim();
    const playerTwoName = document.getElementById('playerTwoName').value.trim();

    if (!quizId || !playerOneName || !playerTwoName) {
        alert('Lütfen quiz ve iki oyuncu adını girin.');
        return;
    }

    if (playerOneName.toLowerCase() === playerTwoName.toLowerCase()) {
        alert('Oyuncu adları farklı olmalı.');
        return;
    }

    multiplayerQuiz = getQuizById(quizId);
    if (!multiplayerQuiz) {
        alert('Seçilen quiz bulunamadı.');
        return;
    }

    multiplayerQuestionIndex = 0;
    multiplayerPlayers = [
        {
            name: playerOneName,
            answers: new Array(multiplayerQuiz.questions.length).fill(null)
        },
        {
            name: playerTwoName,
            answers: new Array(multiplayerQuiz.questions.length).fill(null)
        }
    ];

    multiplayerTimeRemaining = multiplayerQuiz.timeLimit || DEFAULT_TIME_LIMIT;
    resetMultiplayerTurnForCurrentQuestion();

    document.getElementById('multiplayerQuizTitle').textContent = multiplayerQuiz.title;
    document.getElementById('playerOneLabel').textContent = playerOneName;
    document.getElementById('playerTwoLabel').textContent = playerTwoName;

    setMultiplayerView('game');
    displayMultiplayerQuestion();
    startMultiplayerTimer();
}

function setMultiplayerView(view) {
    const setup = document.getElementById('multiplayerSetup');
    const game = document.getElementById('multiplayerGame');
    const result = document.getElementById('multiplayerResult');

    if (setup) {
        setup.hidden = view !== 'setup';
    }
    if (game) {
        game.hidden = view !== 'game';
    }
    if (result) {
        result.hidden = view !== 'result';
    }
}

function displayMultiplayerQuestion() {
    if (!multiplayerQuiz || multiplayerPlayers.length !== 2) {
        return;
    }

    const question = multiplayerQuiz.questions[multiplayerQuestionIndex];
    const totalQuestions = multiplayerQuiz.questions.length;

    document.getElementById('multiplayerProgressText').textContent =
        `Soru ${multiplayerQuestionIndex + 1} / ${totalQuestions}`;
    document.getElementById('multiplayerQuestionText').textContent = question.question;
    document.getElementById('multiplayerProgressBar').style.width =
        `${((multiplayerQuestionIndex + 1) / totalQuestions) * 100}%`;

    renderQuestionMedia(question, 'multiplayerQuestionMedia', 'multiplayerQuestionImage', 'multiplayerQuestionImageCaption');

    updateMultiplayerTurnInfo();
    renderMultiplayerActivePlayerOptions(question);
    updateMultiplayerScoreboard();
    updateMultiplayerNextButton();
}

function selectMultiplayerOption(playerIndex, optionIndex) {
    if (!multiplayerQuiz || !multiplayerPlayers[playerIndex]) {
        return;
    }

    const activePlayerIndex = getActiveMultiplayerPlayerIndex();
    if (playerIndex !== activePlayerIndex || haveBothPlayersAnsweredCurrentQuestion()) {
        return;
    }

    multiplayerPlayers[activePlayerIndex].answers[multiplayerQuestionIndex] = optionIndex;
    if (multiplayerTurnStep === 0) {
        multiplayerTurnStep = 1;
    }

    displayMultiplayerQuestion();
}

function updateMultiplayerNextButton() {
    if (!multiplayerQuiz) {
        return;
    }

    const nextButton = document.getElementById('multiplayerNextButton');
    if (!nextButton) {
        return;
    }

    nextButton.disabled = !haveBothPlayersAnsweredCurrentQuestion();
    if (multiplayerQuestionIndex < multiplayerQuiz.questions.length - 1) {
        nextButton.innerHTML = 'Sonraki Soru <i class="ph ph-caret-right"></i>';
    } else {
        nextButton.innerHTML = 'Maçı Bitir <i class="ph ph-check"></i>';
    }
}

function haveBothPlayersAnsweredCurrentQuestion() {
    return multiplayerPlayers.length === 2 &&
        multiplayerPlayers[0].answers[multiplayerQuestionIndex] !== null &&
        multiplayerPlayers[1].answers[multiplayerQuestionIndex] !== null;
}

function nextMultiplayerQuestion() {
    if (!multiplayerQuiz) {
        return;
    }

    if (!haveBothPlayersAnsweredCurrentQuestion()) {
        alert('Sonraki soruya geçmek için iki oyuncu da cevap vermeli.');
        return;
    }

    if (multiplayerQuestionIndex < multiplayerQuiz.questions.length - 1) {
        multiplayerQuestionIndex++;
        resetMultiplayerTurnForCurrentQuestion();
        displayMultiplayerQuestion();
    } else {
        finishMultiplayerQuiz('completed');
    }
}

function resetMultiplayerTurnForCurrentQuestion() {
    const firstPlayer = Math.random() < 0.5 ? 0 : 1;
    multiplayerTurnOrder = [firstPlayer, firstPlayer === 0 ? 1 : 0];
    multiplayerTurnStep = 0;
}

function getActiveMultiplayerPlayerIndex() {
    const step = Math.min(multiplayerTurnStep, multiplayerTurnOrder.length - 1);
    return multiplayerTurnOrder[step];
}

function updateMultiplayerTurnInfo() {
    if (multiplayerPlayers.length !== 2) {
        return;
    }

    const turnInfo = document.getElementById('multiplayerTurnInfo');
    const activePlayerTitle = document.getElementById('multiplayerActivePlayerTitle');
    if (!turnInfo || !activePlayerTitle) {
        return;
    }

    const firstPlayerIndex = multiplayerTurnOrder[0];
    const secondPlayerIndex = multiplayerTurnOrder[1];
    const firstPlayerName = multiplayerPlayers[firstPlayerIndex].name;
    const secondPlayerName = multiplayerPlayers[secondPlayerIndex].name;

    if (haveBothPlayersAnsweredCurrentQuestion()) {
        turnInfo.textContent = 'Bu soruda iki oyuncu da cevap verdi. Sonraki soruya geçebilirsiniz.';
        activePlayerTitle.textContent = `${secondPlayerName} cevabı`;
        return;
    }

    if (multiplayerTurnStep === 0) {
        turnInfo.textContent = `Bu soruda ilk cevap hakkı: ${firstPlayerName}`;
        activePlayerTitle.textContent = `${firstPlayerName} cevabı`;
    } else {
        turnInfo.textContent = `${firstPlayerName} cevap verdi. Şimdi sıra: ${secondPlayerName}`;
        activePlayerTitle.textContent = `${secondPlayerName} cevabı`;
    }
}

function renderMultiplayerActivePlayerOptions(question) {
    const container = document.getElementById('multiplayerActivePlayerOptions');
    if (!container || !question) {
        return;
    }

    const activePlayerIndex = getActiveMultiplayerPlayerIndex();
    const selectedAnswer = multiplayerPlayers[activePlayerIndex].answers[multiplayerQuestionIndex];
    const isLocked = haveBothPlayersAnsweredCurrentQuestion();

    const optionType = getQuestionOptionType(question);
    container.innerHTML = question.options.map((option, optionIndex) => `
        <button class="option ${optionType === 'image' ? 'option--image' : ''} ${selectedAnswer === optionIndex ? 'selected' : ''}"
                onclick="selectMultiplayerOption(${activePlayerIndex}, ${optionIndex})"
                ${isLocked ? 'disabled' : ''}>
            ${getOptionContentMarkup(option, optionType)}
        </button>
    `).join('');
}

function startMultiplayerTimer() {
    clearInterval(multiplayerTimer);
    updateMultiplayerTimerDisplay();

    multiplayerTimer = setInterval(() => {
        multiplayerTimeRemaining--;
        updateMultiplayerTimerDisplay();

        if (multiplayerTimeRemaining <= 0) {
            clearInterval(multiplayerTimer);
            finishMultiplayerQuiz('time_up');
        }
    }, 1000);
}

function updateMultiplayerTimerDisplay() {
    if (!multiplayerQuiz) {
        return;
    }

    const totalTime = multiplayerQuiz.timeLimit || DEFAULT_TIME_LIMIT;
    updateCircularTimer('multiplayerTimerText', 'multiplayerTimerProgress', multiplayerTimeRemaining, totalTime);
}

function calculateMultiplayerScore(playerIndex) {
    if (!multiplayerQuiz || !multiplayerPlayers[playerIndex]) {
        return 0;
    }

    return multiplayerPlayers[playerIndex].answers.reduce((score, answer, questionIndex) => {
        if (answer === multiplayerQuiz.questions[questionIndex].correctAnswer) {
            return score + 1;
        }
        return score;
    }, 0);
}

function updateMultiplayerScoreboard() {
    if (!multiplayerQuiz || multiplayerPlayers.length !== 2) {
        return;
    }

    document.getElementById('playerOneScore').textContent = calculateMultiplayerScore(0);
    document.getElementById('playerTwoScore').textContent = calculateMultiplayerScore(1);
}

function finishMultiplayerQuiz(reason) {
    if (!multiplayerQuiz || multiplayerPlayers.length !== 2) {
        return;
    }

    clearInterval(multiplayerTimer);

    const totalQuestions = multiplayerQuiz.questions.length;
    const playerOneScore = calculateMultiplayerScore(0);
    const playerTwoScore = calculateMultiplayerScore(1);

    let winnerText = 'Maç Berabere!';
    let winnerName = 'draw';
    if (playerOneScore > playerTwoScore) {
        winnerText = `${multiplayerPlayers[0].name} kazandı!`;
        winnerName = multiplayerPlayers[0].name;
    } else if (playerTwoScore > playerOneScore) {
        winnerText = `${multiplayerPlayers[1].name} kazandı!`;
        winnerName = multiplayerPlayers[1].name;
    }

    const subtitle = reason === 'time_up'
        ? 'Süre bitti. Sonuçlar mevcut cevaplara göre hesaplandı.'
        : 'Tüm sorular tamamlandı.';

    document.getElementById('multiplayerWinnerTitle').textContent = winnerText;
    document.getElementById('multiplayerResultSubtitle').textContent = subtitle;

    document.getElementById('multiplayerPlayerOneResultName').textContent = multiplayerPlayers[0].name;
    document.getElementById('multiplayerPlayerTwoResultName').textContent = multiplayerPlayers[1].name;
    document.getElementById('multiplayerPlayerOneResultScore').textContent = `${playerOneScore}/${totalQuestions}`;
    document.getElementById('multiplayerPlayerTwoResultScore').textContent = `${playerTwoScore}/${totalQuestions}`;

    setMultiplayerView('result');

    saveMultiplayerSession({
        quiz_id: multiplayerQuiz.id,
        quiz_title: multiplayerQuiz.title,
        player_one_name: multiplayerPlayers[0].name,
        player_two_name: multiplayerPlayers[1].name,
        player_one_score: playerOneScore,
        player_two_score: playerTwoScore,
        total_questions: totalQuestions,
        winner: winnerName,
        status: reason,
    });
}

function getCsrfToken() {
    const name = 'csrftoken';
    for (const cookie of document.cookie.split(';')) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) {
            return decodeURIComponent(value);
        }
    }
    return '';
}

async function saveMultiplayerSession(payload) {
    if (!window.QUIZFLOW_IS_LOGGED_IN) {
        return;
    }

    try {
        await fetch('/api/multiplayer/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(payload),
        });
    } catch (error) {
        console.warn('Maç kaydedilemedi:', error);
    }
}

function confirmMultiplayerQuit() {
    if (confirm('Oyunu bitirip çıkmak istediğine emin misin?')) {
        clearInterval(multiplayerTimer);
        window.location.href = '/quizzes/';
    }
}

function restartMultiplayer() {
    if (multiplayerQuiz) {
        window.location.href = `/multiplayer/?id=${multiplayerQuiz.id}`;
    } else {
        window.location.href = '/multiplayer/';
    }
}

function backToQuizSelection() {
    clearInterval(multiplayerTimer);
    window.location.href = '/quizzes/';
}
