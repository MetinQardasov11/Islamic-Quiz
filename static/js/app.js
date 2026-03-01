document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    initStickyHeader();
    initResponsiveNav();
    initFooterEnhancements();
    initAuthUI();

    const filename = getCurrentFilename();
    await initInfoContent(filename);
    initFaqAccordions(filename);

    if (pageNeedsQuizData(filename)) {
        const loaded = await loadQuizData();
        if (!loaded) {
            return;
        }
    }

    if (filename === 'quizzes.html') {
        loadQuizzes();
    } else if (filename === 'quiz.html') {
        initQuiz();
    } else if (filename === 'result.html') {
        displayResults();
    } else if (filename === 'review.html') {
        displayReview();
    } else if (filename === 'multiplayer.html') {
        initMultiplayer();
    }
});

window.addEventListener('beforeunload', () => {
    clearInterval(timer);
    clearInterval(multiplayerTimer);
});
