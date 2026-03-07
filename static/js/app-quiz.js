function getQuizById(quizId) {
    return quizData.quizzes.find(quiz => quiz.id === quizId);
}

let currentAttemptResult = null;

function getDifficultyLabel(difficulty) {
    return DIFFICULTY_LABELS[difficulty] || DIFFICULTY_LABELS.medium;
}

function renderCategoryList() {
    const categoryList = document.getElementById('categoryList');
    if (!categoryList) {
        return;
    }

    const categories = ['all', ...getAvailableCategories()];
    categoryList.innerHTML = categories
        .map(category => {
            const label = category === 'all' ? 'Tüm Kategoriler' : category;
            const isActive = quizFilters.category === category;
            return `
                <button
                    type="button"
                    class="category-pill category-pill--interactive ${isActive ? 'is-active' : ''}"
                    data-category-value="${category}">
                    ${label}
                </button>
            `;
        })
        .join('');
}

function normalizeFilterValue(value) {
    return typeof value === 'string'
        ? value.toLocaleLowerCase('tr-TR').trim()
        : '';
}

function getQuizSubcategory(quiz) {
    if (!quiz || typeof quiz.subcategory !== 'string') {
        return '';
    }

    return quiz.subcategory.trim();
}

function sanitizeQuizPage(value) {
    const parsedValue = Number.parseInt(value, 10);
    if (Number.isNaN(parsedValue) || parsedValue < 1) {
        return 1;
    }

    return parsedValue;
}

function readQuizStateFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);

    quizFilters.search = (urlParams.get(QUIZ_URL_STATE_KEYS.search) || '').trim();
    quizFilters.category = urlParams.get(QUIZ_URL_STATE_KEYS.category) || 'all';
    quizFilters.difficulty = urlParams.get(QUIZ_URL_STATE_KEYS.difficulty) || 'all';
    quizFilters.subcategory = urlParams.get(QUIZ_URL_STATE_KEYS.subcategory) || 'all';
    quizPagination.page = sanitizeQuizPage(urlParams.get(QUIZ_URL_STATE_KEYS.page));
}

function syncQuizStateToUrl() {
    if (getCurrentFilename() !== 'quizzes.html') {
        return;
    }

    const urlParams = new URLSearchParams();
    urlParams.set(QUIZ_URL_STATE_KEYS.search, quizFilters.search);
    urlParams.set(QUIZ_URL_STATE_KEYS.category, quizFilters.category);
    urlParams.set(QUIZ_URL_STATE_KEYS.difficulty, quizFilters.difficulty);
    urlParams.set(QUIZ_URL_STATE_KEYS.subcategory, quizFilters.subcategory);
    urlParams.set(QUIZ_URL_STATE_KEYS.page, String(quizPagination.page));

    const nextUrl = `${window.location.pathname}?${urlParams.toString()}${window.location.hash || ''}`;
    const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash || ''}`;

    if (nextUrl !== currentUrl) {
        window.history.replaceState({}, '', nextUrl);
    }
}

function getAvailableCategories() {
    return [...new Set(quizData.quizzes.map(quiz => quiz.category).filter(Boolean))]
        .sort((first, second) => first.localeCompare(second, 'tr-TR'));
}

function getAvailableSubcategories(selectedCategory) {
    return [...new Set(
        quizData.quizzes
            .filter(quiz => selectedCategory === 'all' || quiz.category === selectedCategory)
            .map(quiz => getQuizSubcategory(quiz))
            .filter(Boolean)
    )].sort((first, second) => first.localeCompare(second, 'tr-TR'));
}

function renderCategoryFilterOptions() {
    const categorySelect = document.getElementById('categoryFilterSelect');
    if (!categorySelect) {
        return;
    }

    const categories = getAvailableCategories();
    categorySelect.innerHTML = [
        '<option value="all">Tüm kategoriler</option>',
        ...categories.map(category => `<option value="${category}">${category}</option>`)
    ].join('');
}

function renderSubcategoryFilterOptions() {
    const subcategorySelect = document.getElementById('subcategoryFilterSelect');
    const subcategoryField = document.getElementById('subcategoryFilterField');

    if (!subcategorySelect) {
        return;
    }

    const subcategories = getAvailableSubcategories(quizFilters.category);

    if (subcategories.length === 0) {
        quizFilters.subcategory = 'all';
        subcategorySelect.innerHTML = '<option value="all">Tüm alt kategoriler</option>';
        if (subcategoryField) {
            subcategoryField.hidden = true;
        }
        return;
    }

    if (quizFilters.subcategory !== 'all' && !subcategories.includes(quizFilters.subcategory)) {
        quizFilters.subcategory = 'all';
    }

    subcategorySelect.innerHTML = [
        '<option value="all">Tüm alt kategoriler</option>',
        ...subcategories.map(subcategory => `<option value="${subcategory}">${subcategory}</option>`)
    ].join('');

    if (subcategoryField) {
        subcategoryField.hidden = false;
    }
}

function syncQuizFilterControls() {
    const searchInput = document.getElementById('quizSearchInput');
    const categorySelect = document.getElementById('categoryFilterSelect');
    const difficultySelect = document.getElementById('difficultyFilterSelect');
    const subcategorySelect = document.getElementById('subcategoryFilterSelect');

    if (!searchInput || !categorySelect || !difficultySelect || !subcategorySelect) {
        return;
    }

    const availableCategories = getAvailableCategories();
    if (quizFilters.category !== 'all' && !availableCategories.includes(quizFilters.category)) {
        quizFilters.category = 'all';
    }

    if (!['all', 'easy', 'medium', 'hard'].includes(quizFilters.difficulty)) {
        quizFilters.difficulty = 'all';
    }

    searchInput.value = quizFilters.search;

    renderCategoryFilterOptions();
    categorySelect.value = quizFilters.category;
    difficultySelect.value = quizFilters.difficulty;

    renderSubcategoryFilterOptions();
    subcategorySelect.value = quizFilters.subcategory;
}

function getFilteredQuizzes() {
    const searchTerm = normalizeFilterValue(quizFilters.search);

    return quizData.quizzes.filter(quiz => {
        const quizSubcategory = getQuizSubcategory(quiz);
        const searchCorpus = normalizeFilterValue([
            quiz.title,
            quiz.description,
            quiz.category,
            quizSubcategory,
            getDifficultyLabel(quiz.difficulty)
        ].join(' '));

        const matchesSearch = !searchTerm || searchCorpus.includes(searchTerm);
        const matchesCategory = quizFilters.category === 'all' || quiz.category === quizFilters.category;
        const matchesDifficulty = quizFilters.difficulty === 'all' || quiz.difficulty === quizFilters.difficulty;
        const matchesSubcategory = quizFilters.subcategory === 'all' || quizSubcategory === quizFilters.subcategory;

        return matchesSearch && matchesCategory && matchesDifficulty && matchesSubcategory;
    });
}

function updateQuizResultCount(filteredCount, totalCount, currentPage, totalPages) {
    const resultCount = document.getElementById('quizResultCount');
    if (!resultCount) {
        return;
    }

    if (totalCount === 0) {
        resultCount.textContent = 'Henuz quiz eklenmemis.';
        return;
    }

    resultCount.textContent = `${filteredCount} / ${totalCount} quiz gosteriliyor | Sayfa ${currentPage}/${totalPages}`;
}

function getQuizPaginationMeta(filteredCount) {
    const totalPages = Math.max(1, Math.ceil(filteredCount / quizPagination.perPage));
    quizPagination.page = Math.min(Math.max(quizPagination.page, 1), totalPages);

    return {
        totalPages,
        currentPage: quizPagination.page,
        startIndex: (quizPagination.page - 1) * quizPagination.perPage,
        endIndex: quizPagination.page * quizPagination.perPage
    };
}

function getVisiblePaginationPages(totalPages, currentPage) {
    const visiblePages = new Set([
        1,
        totalPages,
        currentPage - 1,
        currentPage,
        currentPage + 1
    ]);

    return [...visiblePages]
        .filter(pageNumber => pageNumber >= 1 && pageNumber <= totalPages)
        .sort((first, second) => first - second);
}

function renderQuizPagination(filteredCount, paginationMeta) {
    const pagination = document.getElementById('quizPagination');
    if (!pagination) {
        return;
    }

    const { totalPages, currentPage } = paginationMeta;

    if (filteredCount === 0 || totalPages <= 1) {
        pagination.innerHTML = '';
        pagination.hidden = true;
        return;
    }

    const visiblePages = getVisiblePaginationPages(totalPages, currentPage);
    const controls = [];

    controls.push(`
        <button
            type="button"
            class="quizzes__pagination-btn quizzes__pagination-btn--nav"
            data-page="${currentPage - 1}"
            ${currentPage === 1 ? 'disabled' : ''}>
            <i class="ph ph-caret-left"></i>
            Onceki
        </button>
    `);

    let previousPage = 0;
    visiblePages.forEach(pageNumber => {
        if (previousPage && pageNumber - previousPage > 1) {
            controls.push('<span class="quizzes__pagination-gap" aria-hidden="true">...</span>');
        }

        controls.push(`
            <button
                type="button"
                class="quizzes__pagination-btn ${pageNumber === currentPage ? 'is-active' : ''}"
                data-page="${pageNumber}"
                ${pageNumber === currentPage ? 'aria-current="page"' : ''}>
                ${pageNumber}
            </button>
        `);
        previousPage = pageNumber;
    });

    controls.push(`
        <button
            type="button"
            class="quizzes__pagination-btn quizzes__pagination-btn--nav"
            data-page="${currentPage + 1}"
            ${currentPage === totalPages ? 'disabled' : ''}>
            Sonraki
            <i class="ph ph-caret-right"></i>
        </button>
    `);

    controls.push(`<p class="quizzes__pagination-info">Sayfa ${currentPage} / ${totalPages}</p>`);

    pagination.innerHTML = controls.join('');
    pagination.hidden = false;
}

function getQuizCardMarkup(quiz) {
    const quizSubcategory = getQuizSubcategory(quiz);

    return `
        <div class="quiz-card" data-testid="quiz-card-${quiz.id}">
            <img src="${quiz.thumbnail}" alt="${quiz.title}" class="quiz-card__image">
            <div class="quiz-card__content">
                <h3 class="quiz-card__title">${quiz.title}</h3>
                <p class="quiz-card__description">${quiz.description}</p>
                <div class="quiz-card__meta">
                    <span class="quiz-card__badge">
                        <i class="ph ph-question"></i>
                        ${quiz.questions.length} Soru
                    </span>
                    <span class="quiz-card__badge">
                        <i class="ph ph-tag"></i>
                        ${quiz.category}
                    </span>
                    ${quizSubcategory ? `
                    <span class="quiz-card__badge">
                        <i class="ph ph-folders"></i>
                        ${quizSubcategory}
                    </span>
                    ` : ''}
                    <span class="quiz-card__badge quiz-card__badge--difficulty ${quiz.difficulty}">
                        <i class="ph ph-chart-line"></i>
                        ${getDifficultyLabel(quiz.difficulty)}
                    </span>
                </div>
                <div class="quiz-card__actions">
                    <button class="btn btn--primary" data-testid="start-quiz-${quiz.id}" onclick="startQuiz('${quiz.id}')">
                        Quizi Baslat
                        <i class="ph ph-caret-right"></i>
                    </button>
                    <button class="btn btn--secondary" data-testid="start-multiplayer-${quiz.id}" onclick="startMultiplayerFromQuiz('${quiz.id}')">
                        2 Oyunculu
                        <i class="ph ph-users-three"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function renderQuizGrid(quizzes) {
    const grid = document.getElementById('quizGrid');
    if (!grid) {
        return;
    }

    if (quizzes.length === 0) {
        grid.innerHTML = `
            <article class="quiz-grid__empty" data-testid="quiz-grid-empty">
                <i class="ph ph-magnifying-glass-minus"></i>
                <h3>Sonuç bulunamadı</h3>
                <p>Arama veya filtreleri degistirip tekrar dene.</p>
            </article>
        `;
        return;
    }

    grid.innerHTML = quizzes.map(quiz => getQuizCardMarkup(quiz)).join('');
}

function applyQuizFilters() {
    const filteredQuizzes = getFilteredQuizzes();
    const paginationMeta = getQuizPaginationMeta(filteredQuizzes.length);
    const paginatedQuizzes = filteredQuizzes.slice(paginationMeta.startIndex, paginationMeta.endIndex);

    renderCategoryList();
    renderQuizGrid(paginatedQuizzes);
    renderQuizPagination(filteredQuizzes.length, paginationMeta);
    updateQuizResultCount(
        filteredQuizzes.length,
        quizData.quizzes.length,
        paginationMeta.currentPage,
        paginationMeta.totalPages
    );
    syncQuizStateToUrl();
}

function setupQuizFilters() {
    const searchInput = document.getElementById('quizSearchInput');
    const categorySelect = document.getElementById('categoryFilterSelect');
    const difficultySelect = document.getElementById('difficultyFilterSelect');
    const subcategorySelect = document.getElementById('subcategoryFilterSelect');
    const clearFiltersButton = document.getElementById('clearFiltersButton');
    const categoryList = document.getElementById('categoryList');
    const pagination = document.getElementById('quizPagination');

    if (!searchInput || !categorySelect || !difficultySelect || !subcategorySelect || !clearFiltersButton) {
        return;
    }

    syncQuizFilterControls();

    if (areQuizFiltersInitialized) {
        return;
    }

    searchInput.addEventListener('input', event => {
        quizFilters.search = event.target.value;
        quizPagination.page = 1;
        applyQuizFilters();
    });

    categorySelect.addEventListener('change', event => {
        quizFilters.category = event.target.value;
        quizFilters.subcategory = 'all';
        quizPagination.page = 1;
        syncQuizFilterControls();
        applyQuizFilters();
    });

    difficultySelect.addEventListener('change', event => {
        quizFilters.difficulty = event.target.value;
        quizPagination.page = 1;
        applyQuizFilters();
    });

    subcategorySelect.addEventListener('change', event => {
        quizFilters.subcategory = event.target.value;
        quizPagination.page = 1;
        applyQuizFilters();
    });

    clearFiltersButton.addEventListener('click', () => {
        quizFilters = {
            search: '',
            category: 'all',
            difficulty: 'all',
            subcategory: 'all'
        };
        quizPagination.page = 1;
        syncQuizFilterControls();
        applyQuizFilters();
    });

    if (categoryList) {
        categoryList.addEventListener('click', event => {
            const categoryButton = event.target.closest('[data-category-value]');
            if (!categoryButton) {
                return;
            }

            quizFilters.category = categoryButton.getAttribute('data-category-value') || 'all';
            quizFilters.subcategory = 'all';
            quizPagination.page = 1;
            syncQuizFilterControls();
            applyQuizFilters();
        });
    }

    if (pagination) {
        pagination.addEventListener('click', event => {
            const pageButton = event.target.closest('[data-page]');
            if (!pageButton || pageButton.hasAttribute('disabled')) {
                return;
            }

            const nextPage = sanitizeQuizPage(pageButton.getAttribute('data-page'));
            if (nextPage === quizPagination.page) {
                return;
            }

            quizPagination.page = nextPage;
            applyQuizFilters();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    if (!isQuizHistoryListenerInitialized) {
        window.addEventListener('popstate', () => {
            if (getCurrentFilename() !== 'quizzes.html') {
                return;
            }

            readQuizStateFromUrl();
            syncQuizFilterControls();
            applyQuizFilters();
        });
        isQuizHistoryListenerInitialized = true;
    }

    areQuizFiltersInitialized = true;
}

// Quizleri yükle ve göster
function loadQuizzes() {
    const grid = document.getElementById('quizGrid');
    if (!grid) {
        return;
    }

    readQuizStateFromUrl();
    setupQuizFilters();
    applyQuizFilters();
}

function startQuiz(quizId) {
    if (!isUserLoggedIn()) {
        showLoginRequiredModal();
        return;
    }
    window.location.href = `/quiz/?id=${quizId}`;
}

function isUserLoggedIn() {
    return window.QUIZFLOW_IS_LOGGED_IN === true;
}

function showLoginRequiredModal() {
    let modal = document.getElementById('loginRequiredModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'login-modal';
        modal.id = 'loginRequiredModal';
        modal.innerHTML = `
            <div class="login-modal__overlay" onclick="closeLoginModal()"></div>
            <div class="login-modal__content">
                <div class="login-modal__icon">
                    <i class="ph ph-warning-circle"></i>
                </div>
                <h2 class="login-modal__title">Giriş Yapmanız Gerekiyor</h2>
                <p class="login-modal__text">
                    Bir sınava girebilmek için önce hesabınıza giriş yapmanız gerekmektedir. Lütfen giriş yapın veya yeni bir hesap oluşturun.
                </p>
                <div class="login-modal__actions">
                    <button class="btn btn--primary" onclick="window.location.href='/auth/login/'">
                        <i class="ph ph-sign-in"></i>
                        Giriş Yap
                    </button>
                    <button class="btn btn--secondary" onclick="window.location.href='/auth/register/'">
                        <i class="ph ph-user-plus"></i>
                        Kayıt Ol
                    </button>
                    <button class="btn btn--secondary" onclick="closeLoginModal()">
                        <i class="ph ph-x"></i>
                        Kapat
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    modal.hidden = false;
}

function closeLoginModal() {
    const modal = document.getElementById('loginRequiredModal');
    if (modal) {
        modal.hidden = true;
    }
}

function startMultiplayerFromQuiz(quizId) {
    if (!isUserLoggedIn()) {
        showLoginRequiredModal();
        return;
    }
    window.location.href = `/multiplayer/?id=${quizId}`;
}

function initQuiz() {
    if (!isUserLoggedIn()) {
        showLoginRequiredModal();
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const quizId = urlParams.get('id');

    if (!quizId) {
        window.location.href = '/404/';
        return;
    }

    currentQuiz = getQuizById(quizId);

    if (!currentQuiz) {
        window.location.href = '/404/';
        return;
    }

    currentQuestionIndex = 0;
    userAnswers = new Array(currentQuiz.questions.length).fill(null);

    const quizTitle = document.getElementById('quizTitle');
    if (quizTitle) {
        quizTitle.textContent = currentQuiz.title;
    }

    displayQuestion();
    startTimer();
}

function getQuestionOptionType(question) {
    if (!question || typeof question.questionType !== 'string') {
        return 'text';
    }

    if (question.questionType === 'text_question_image_answers' ||
        question.questionType === 'image_question_image_answers') {
        return 'image';
    }

    return 'text';
}

function getOptionContentMarkup(option, optionType) {
    const optionText = option && typeof option.text === 'string' ? option.text : '';
    const optionImage = option && typeof option.image === 'string' ? option.image.trim() : '';
    const optionImageAlt = option && typeof option.imageAlt === 'string' && option.imageAlt.trim()
        ? option.imageAlt
        : (optionText || 'Cevap görseli');

    if (optionType === 'image' && optionImage) {
        return `
            <span class="option__content option__content--image">
                <img src="${optionImage}" alt="${optionImageAlt}" class="option__image" loading="lazy">
                ${optionText ? `<span class="option__text option__text--support">${optionText}</span>` : ''}
            </span>
        `;
    }

    return `<span class="option__text">${optionText}</span>`;
}

function getReviewAnswerContentMarkup(labelClassName, labelText, answerText, answerImage, answerImageAlt) {
    const hasImage = typeof answerImage === 'string' && answerImage.trim().length > 0;
    const hasText = typeof answerText === 'string' && answerText.trim().length > 0;

    return `
        <span class="review-item__label ${labelClassName}">${labelText}</span>
        ${hasImage ? `<img src="${answerImage}" alt="${answerImageAlt || answerText || 'Cevap görseli'}" class="review-item__answer-image" loading="lazy">` : ''}
        ${hasText ? `<span class="review-item__answer-text">${answerText}</span>` : ''}
    `;
}

function displayQuestion() {
    if (!currentQuiz) {
        return;
    }

    const question = currentQuiz.questions[currentQuestionIndex];

    document.getElementById('questionText').textContent = question.question;
    document.getElementById('progressText').textContent = `Soru ${currentQuestionIndex + 1} / ${currentQuiz.questions.length}`;

    const progressPercent = ((currentQuestionIndex + 1) / currentQuiz.questions.length) * 100;
    document.getElementById('progressBar').style.width = `${progressPercent}%`;

    renderQuestionMedia(question, 'questionMedia', 'questionImage', 'questionImageCaption');

    const optionsContainer = document.getElementById('optionsContainer');
    const optionType = getQuestionOptionType(question);
    optionsContainer.innerHTML = question.options.map((option, index) => `
        <button class="option ${optionType === 'image' ? 'option--image' : ''} ${userAnswers[currentQuestionIndex] === index ? 'selected' : ''}"
                data-testid="option-${index}"
                onclick="selectOption(${index})">
            ${getOptionContentMarkup(option, optionType)}
        </button>
    `).join('');

    const nextButton = document.getElementById('nextButton');
    nextButton.disabled = userAnswers[currentQuestionIndex] === null;

    if (currentQuestionIndex < currentQuiz.questions.length - 1) {
        nextButton.innerHTML = 'Sonraki Soru <i class="ph ph-caret-right"></i>';
    } else {
        nextButton.innerHTML = 'Quizi Bitir <i class="ph ph-check"></i>';
    }
}

function selectOption(optionIndex) {
    if (!currentQuiz) {
        return;
    }

    userAnswers[currentQuestionIndex] = optionIndex;

    document.querySelectorAll('#optionsContainer .option').forEach((opt, idx) => {
        if (idx === optionIndex) {
            opt.classList.add('selected');
        } else {
            opt.classList.remove('selected');
        }
    });

    document.getElementById('nextButton').disabled = false;
}

function nextQuestion() {
    if (!currentQuiz) {
        return;
    }

    if (currentQuestionIndex < currentQuiz.questions.length - 1) {
        currentQuestionIndex++;
        displayQuestion();
    } else {
        finishQuiz();
    }
}

function finishQuiz() {
    if (!currentQuiz) {
        return;
    }

    clearInterval(timer);
    submitQuizAttempt();
}

async function submitQuizAttempt() {
    if (!currentQuiz) {
        return;
    }

    try {
        const elapsedSeconds = Math.max((currentQuiz.timeLimit || DEFAULT_TIME_LIMIT) - timeRemaining, 0);
        const response = await fetch('/api/attempts/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                quiz_id: currentQuiz.id,
                answers: userAnswers,
                elapsed_seconds: elapsedSeconds,
            }),
        });
        const payload = await response.json();

        if (!response.ok || !payload.success) {
            throw new Error(payload.error || 'Quiz sonucu kaydedilemedi.');
        }

        currentAttemptResult = payload.attempt;
        window.location.href = `/result/?attempt=${payload.attempt.id}`;
    } catch (error) {
        console.error('Quiz denemesi kaydedilemedi:', error);
        alert('Quiz sonucu kaydedilemedi. Lütfen tekrar deneyin.');
    }
}

function startTimer() {
    if (!currentQuiz) {
        return;
    }

    clearInterval(timer);
    const totalTime = currentQuiz.timeLimit || DEFAULT_TIME_LIMIT;
    timeRemaining = totalTime;
    updateTimerDisplay();

    timer = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();

        if (timeRemaining <= 0) {
            clearInterval(timer);
            alert('Süre doldu!');
            finishQuiz();
        }
    }, 1000);
}

function updateTimerDisplay() {
    if (!currentQuiz) {
        return;
    }

    const totalTime = currentQuiz.timeLimit || DEFAULT_TIME_LIMIT;
    updateCircularTimer('timerText', 'timerProgress', timeRemaining, totalTime);
}


function confirmQuit() {
    if (confirm('Quizden çıkmak istediğine emin misin? İlerlemen kaydedilmeyecek.')) {
        clearInterval(timer);
        window.location.href = '/quizzes/';
    }
}

function displayResults() {
    loadAttemptResult().then(resultData => {
        if (!resultData) {
            window.location.href = '/quizzes/';
            return;
        }

        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const scorePercentage = document.getElementById('scorePercentage');
        const scoreCircle = document.getElementById('scoreCircle');
        const correctCount = document.getElementById('correctCount');
        const totalCount = document.getElementById('totalCount');
        const passStatus = document.getElementById('passStatus');

        resultIcon.classList.remove('pass', 'fail');
        scoreCircle.classList.remove('pass', 'fail');
        passStatus.classList.remove('pass', 'fail');

        if (resultData.passed) {
            resultIcon.classList.add('pass');
            resultIcon.innerHTML = '<i class="ph ph-trophy"></i>';
            resultTitle.textContent = 'Tebrikler, Geçtin!';
            scoreCircle.classList.add('pass');
            passStatus.textContent = 'GEÇTİ';
            passStatus.classList.add('pass');
        } else {
            resultIcon.classList.add('fail');
            resultIcon.innerHTML = '<i class="ph ph-x-circle"></i>';
            resultTitle.textContent = 'Quiz Tamamlandı';
            scoreCircle.classList.add('fail');
            passStatus.textContent = 'KALDI';
            passStatus.classList.add('fail');
        }

        scorePercentage.textContent = `${resultData.percentage}%`;
        correctCount.textContent = resultData.correctCount;
        totalCount.textContent = resultData.totalQuestions;
    });
}

function reviewAnswers() {
    const attemptId = getAttemptIdFromUrl();
    if (!attemptId) {
        window.location.href = '/quizzes/';
        return;
    }
    window.location.href = `/review/?attempt=${attemptId}`;
}

function playAgain() {
    loadAttemptResult().then(resultData => {
        if (!resultData) {
            window.location.href = '/quizzes/';
            return;
        }

        window.location.href = `/quiz/?id=${resultData.quizId}`;
    });
}

function goHome() {
    window.location.href = '/';
}

function displayReview() {
    loadAttemptResult().then(resultData => {
        if (!resultData) {
            window.location.href = '/quizzes/';
            return;
        }

        const reviewSubtitle = document.getElementById('reviewSubtitle');
        reviewSubtitle.textContent =
            `${resultData.quizTitle} - ${resultData.correctCount}/${resultData.totalQuestions} doğru (%${resultData.percentage})`;

        const reviewList = document.getElementById('reviewList');
        reviewList.innerHTML = resultData.answers.map((answer, index) => {
            const imageMarkup = answer.image ? `
                <figure class="question-media question-media--review">
                    <img src="${answer.image}" alt="${answer.imageAlt || 'Soru görseli'}" class="question-media__image" loading="lazy">
                    ${answer.imageCaption ? `<figcaption class="question-media__caption">${answer.imageCaption}</figcaption>` : ''}
                </figure>
            ` : '';

            return `
                <div class="review-item ${answer.isCorrect ? 'correct' : 'incorrect'}" data-testid="review-item-${index}">
                    <div class="review-item__header">
                        <span class="review-item__number">Soru ${index + 1}</span>
                        <span class="review-item__status ${answer.isCorrect ? 'correct' : 'incorrect'}" data-testid="review-status-${index}">
                            <i class="ph ${answer.isCorrect ? 'ph-check-circle' : 'ph-x-circle'}"></i>
                            ${answer.isCorrect ? 'Doğru' : 'Yanlış'}
                        </span>
                    </div>
                    <p class="review-item__question">${answer.questionText}</p>
                    ${imageMarkup}
                    <div class="review-item__answers">
                        ${!answer.isCorrect && answer.selectedAnswerIndex !== null ? `
                            <div class="review-item__answer user-wrong">
                                ${getReviewAnswerContentMarkup(
                                    'incorrect',
                                    'Senin Cevabın:',
                                    answer.selectedAnswerText,
                                    answer.selectedAnswerImage,
                                    answer.selectedAnswerImageAlt
                                )}
                            </div>
                        ` : ''}
                        <div class="review-item__answer correct-answer">
                            ${getReviewAnswerContentMarkup(
                                'correct',
                                'Doğru Cevap:',
                                answer.correctAnswerText,
                                answer.correctAnswerImage,
                                answer.correctAnswerImageAlt
                            )}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    });
}

function getAttemptIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const attemptId = Number.parseInt(urlParams.get('attempt'), 10);
    return Number.isNaN(attemptId) ? null : attemptId;
}

async function loadAttemptResult() {
    if (currentAttemptResult) {
        return currentAttemptResult;
    }

    const attemptId = getAttemptIdFromUrl();
    if (!attemptId) {
        return null;
    }

    try {
        const response = await fetch(`/api/attempts/${attemptId}/`);
        const payload = await response.json();
        if (!response.ok || !payload.success) {
            throw new Error(payload.error || 'Deneme sonucu yüklenemedi.');
        }
        currentAttemptResult = payload.attempt;
        return currentAttemptResult;
    } catch (error) {
        console.error('Deneme sonucu yüklenemedi:', error);
        return null;
    }
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
