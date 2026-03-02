let quizData = {
    quizzes: [],
    passingScore: 70
};
let isQuizDataLoaded = false;

let currentQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = [];
let timer = null;
let timeRemaining = 0;

let multiplayerQuiz = null;
let multiplayerQuestionIndex = 0;
let multiplayerPlayers = [];
let multiplayerTimer = null;
let multiplayerTimeRemaining = 0;
let multiplayerTurnOrder = [0, 1];
let multiplayerTurnStep = 0;

let quizFilters = {
    search: '',
    category: 'all',
    difficulty: 'all',
    subcategory: 'all'
};

const TIMER_CIRCUMFERENCE = 283;
const DEFAULT_TIME_LIMIT = 60;
const THEME_STORAGE_KEY = 'quizflow-theme';
const DEFAULT_THEME = 'light';
const FAQS_FILE_PATH = '/static/json/faqs.json';
const TERMS_OF_USE_FILE_PATH = '/static/json/terms-of-use.json';
const LANDING_FAQ_PREVIEW_COUNT = 2;
const LANDING_TERMS_PREVIEW_COUNT = 2;
const QUIZZES_PER_PAGE = 15;
const QUIZ_URL_STATE_KEYS = Object.freeze({
    search: 'search',
    category: 'category',
    difficulty: 'difficulty',
    subcategory: 'subcategory',
    page: 'page'
});

const DIFFICULTY_LABELS = {
    easy: 'Kolay',
    medium: 'Orta',
    hard: 'Zor'
};

let quizPagination = {
    page: 1,
    perPage: QUIZZES_PER_PAGE
};
let areQuizFiltersInitialized = false;
let isQuizHistoryListenerInitialized = false;


function initTheme() {
    const preferredTheme = getPreferredTheme();
    applyTheme(preferredTheme);

    const themeToggleButtons = document.querySelectorAll('.theme-toggle');
    if (!themeToggleButtons.length) {
        return;
    }

    themeToggleButtons.forEach(button => {
        updateThemeToggle(button, preferredTheme);
    });

    themeToggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const currentTheme = document.body.classList.contains('theme-dark') ? 'dark' : 'light';
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
            themeToggleButtons.forEach(toggleButton => {
                updateThemeToggle(toggleButton, nextTheme);
            });
        });
    });
}

function initStickyHeader() {
    const header = document.querySelector('.header');
    if (!header) {
        return;
    }

    let isScrolled = false;

    const syncHeaderState = () => {
        const shouldBeScrolled = window.scrollY > 12;
        if (shouldBeScrolled === isScrolled) {
            return;
        }

        header.classList.toggle('is-scrolled', shouldBeScrolled);
        isScrolled = shouldBeScrolled;
    };

    syncHeaderState();
    window.addEventListener('scroll', syncHeaderState, { passive: true });
}

function initResponsiveNav() {
    const MOBILE_BREAKPOINT = 860;
    const header = document.querySelector('.header');
    if (!header) {
        return;
    }

    const headerContainer = header.querySelector('.header__container');
    const headerActions = header.querySelector('.header__actions');
    if (!headerContainer || !headerActions) {
        return;
    }

    if (!headerActions.id) {
        headerActions.id = 'headerActions';
    }

    let menuButton = headerContainer.querySelector('.header__menu-toggle');
    if (!menuButton) {
        menuButton = document.createElement('button');
        menuButton.type = 'button';
        menuButton.className = 'header__menu-toggle';
        menuButton.setAttribute('aria-controls', headerActions.id);
        menuButton.setAttribute('aria-expanded', 'false');
        menuButton.setAttribute('aria-label', 'Navigasyon menüsünü aç');
        menuButton.innerHTML = `
            <i class="ph ph-list"></i>
            <span>Menü</span>
        `;

        headerContainer.insertBefore(menuButton, headerActions);
    }

    let drawerOverlay = document.querySelector('.header__drawer-overlay');
    if (!drawerOverlay) {
        drawerOverlay = document.createElement('button');
        drawerOverlay.type = 'button';
        drawerOverlay.className = 'header__drawer-overlay';
        drawerOverlay.setAttribute('aria-label', 'Navigasyon menüsünü kapat');
        document.body.appendChild(drawerOverlay);
    }

    const setMenuState = isOpen => {
        const shouldOpen = Boolean(isOpen && window.innerWidth <= MOBILE_BREAKPOINT);

        header.classList.toggle('is-menu-open', shouldOpen);
        menuButton.classList.toggle('is-open', shouldOpen);
        document.body.classList.toggle('nav-drawer-open', shouldOpen);
        menuButton.setAttribute('aria-expanded', String(shouldOpen));
        const icon = menuButton.querySelector('i');
        const label = menuButton.querySelector('span');

        if (shouldOpen) {
            menuButton.setAttribute('aria-label', 'Navigasyon menüsünü kapat');
            if (icon) {
                icon.className = 'ph ph-x';
            }
            if (label) {
                label.textContent = 'Kapat';
            }
        } else {
            menuButton.setAttribute('aria-label', 'Navigasyon menüsünü aç');
            if (icon) {
                icon.className = 'ph ph-list';
            }
            if (label) {
                label.textContent = 'Menü';
            }
        }
    };

    setMenuState(false);

    menuButton.addEventListener('click', event => {
        event.stopPropagation();
        const isOpen = header.classList.contains('is-menu-open');
        setMenuState(!isOpen);
    });

    drawerOverlay.addEventListener('click', () => {
        setMenuState(false);
    });

    headerActions.addEventListener('click', event => {
        const targetAction = event.target.closest('a, button');
        if (!targetAction) {
            return;
        }

        if (targetAction.classList.contains('theme-toggle') || targetAction.id === 'themeToggle') {
            return;
        }

        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            setMenuState(false);
        }
    });

    document.addEventListener('click', event => {
        if (!header.classList.contains('is-menu-open')) {
            return;
        }

        if (!header.contains(event.target)) {
            setMenuState(false);
        }
    });

    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            setMenuState(false);
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > MOBILE_BREAKPOINT) {
            setMenuState(false);
        }
    });
}

function initFooterEnhancements() {
    const footers = document.querySelectorAll('.site-footer');
    if (!footers.length) {
        return;
    }

    footers.forEach(footer => {
        if (footer.dataset.enhanced === 'true') {
            return;
        }

        const brand = footer.querySelector('.site-footer__brand');
        const links = footer.querySelector('.site-footer__links');
        const meta = footer.querySelector('.site-footer__meta');

        if (!brand || !links || !meta) {
            return;
        }

        const topBlock = document.createElement('div');
        topBlock.className = 'site-footer__top';

        const socialBlock = document.createElement('div');
        socialBlock.className = 'site-footer__social';
        socialBlock.innerHTML = `
            <p class="site-footer__social-label">Sosyal Medya Adresleri</p>
            <div class="site-footer__social-links">
                <a class="site-footer__social-link" href="https://x.com" target="_blank" rel="noopener noreferrer" aria-label="X">
                    <i class="ph ph-x-logo"></i>
                </a>
                <a class="site-footer__social-link" href="https://t.me" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
                    <i class="ph ph-telegram-logo"></i>
                </a>
                <a class="site-footer__social-link" href="https://www.youtube.com" target="_blank" rel="noopener noreferrer" aria-label="YouTube">
                    <i class="ph ph-youtube-logo"></i>
                </a>
                <a class="site-footer__social-link" href="https://www.whatsapp.com" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">
                    <i class="ph ph-whatsapp-logo"></i>
                </a>
            </div>
        `;

        topBlock.append(brand, socialBlock);

        const bottomBlock = document.createElement('div');
        bottomBlock.className = 'site-footer__bottom';

        const topButton = document.createElement('button');
        topButton.type = 'button';
        topButton.className = 'site-footer__top-button';
        topButton.setAttribute('aria-label', 'Sayfanın başına dön');
        topButton.innerHTML = '<i class="ph ph-arrow-up"></i>';
        topButton.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        bottomBlock.append(links, topButton);

        footer.innerHTML = '';
        footer.append(topBlock, bottomBlock, meta);
        footer.dataset.enhanced = 'true';
    });
}

function getPreferredTheme() {
    try {
        const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
        if (savedTheme === 'dark' || savedTheme === 'light') {
            return savedTheme;
        }
    } catch (error) {
        console.warn('Tema tercihi okunamadı:', error);
    }

    return DEFAULT_THEME;
}

function applyTheme(theme) {
    const normalizedTheme = theme === 'dark' ? 'dark' : 'light';

    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(`theme-${normalizedTheme}`);
    document.documentElement.setAttribute('data-theme', normalizedTheme);
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    document.documentElement.classList.add(`theme-${normalizedTheme}`);

    try {
        window.localStorage.setItem(THEME_STORAGE_KEY, normalizedTheme);
    } catch (error) {
        console.warn('Tema tercihi kaydedilemedi:', error);
    }
}

function updateThemeToggle(button, theme) {
    const icon = button.querySelector('i');
    const label = button.querySelector('[data-theme-label]');

    if (!icon || !label) {
        return;
    }

    if (theme === 'dark') {
        icon.className = 'ph ph-sun';
        label.textContent = 'AÇIK';
        button.setAttribute('aria-label', 'Açık moda geç');
    } else {
        icon.className = 'ph ph-moon';
        label.textContent = 'KOYU';
        button.setAttribute('aria-label', 'Koyu moda geç');
    }
}

function getCurrentFilename() {
    const path = window.location.pathname;
    const pathMap = {
        '/': 'index.html',
        '/faq/': 'sss.html',
        '/terms/': 'kullanim-sartlari.html',
        '/quizzes/': 'quizzes.html',
        '/quiz/': 'quiz.html',
        '/result/': 'result.html',
        '/review/': 'review.html',
        '/multiplayer/': 'multiplayer.html',
    };
    return pathMap[path] || (path.substring(path.lastIndexOf('/') + 1) || 'index.html');
}

async function initInfoContent(filename) {
    const needsFaqContent = filename === 'index.html' || filename === 'sss.html';
    const needsTermsContent = filename === 'index.html' || filename === 'kullanim-sartlari.html';

    if (!needsFaqContent && !needsTermsContent) {
        return;
    }

    const loaders = [];

    if (needsFaqContent) {
        loaders.push(loadFaqContent(filename));
    }

    if (needsTermsContent) {
        loaders.push(loadTermsOfUseContent(filename));
    }

    await Promise.all(loaders);
}

async function loadFaqContent(filename) {
    const payload = await loadJsonPayload(FAQS_FILE_PATH);
    if (!payload || !Array.isArray(payload.faqs)) {
        return;
    }

    const faqItems = sanitizeFaqItems(payload.faqs);
    if (!faqItems.length) {
        return;
    }

    if (filename === 'index.html') {
        renderFaqItems('landingFaqList', faqItems.slice(0, LANDING_FAQ_PREVIEW_COUNT), true);
    }

    if (filename === 'sss.html') {
        renderFaqItems('faqList', faqItems, true);
    }
}

async function loadTermsOfUseContent(filename) {
    const payload = await loadJsonPayload(TERMS_OF_USE_FILE_PATH);
    if (!payload || !Array.isArray(payload.terms)) {
        return;
    }

    const termItems = sanitizeTermsItems(payload.terms);
    if (termItems.length) {
        if (filename === 'index.html') {
            renderTermsItems('landingTermsList', termItems.slice(0, LANDING_TERMS_PREVIEW_COUNT));
        }

        if (filename === 'kullanim-sartlari.html') {
            renderTermsItems('termsList', termItems);
        }
    }

    if (filename === 'kullanim-sartlari.html' && payload.note) {
        renderTermsNote('termsNote', payload.note);
    }
}

async function loadJsonPayload(filePath) {
    try {
        const response = await fetch(filePath, { cache: 'no-store' });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn(`${filePath} yüklenemedi:`, error);
        return null;
    }
}

function sanitizeFaqItems(items) {
    if (!Array.isArray(items)) {
        return [];
    }

    return items
        .map(item => ({
            question: typeof item.question === 'string' ? item.question.trim() : '',
            answer: typeof item.answer === 'string' ? item.answer.trim() : ''
        }))
        .filter(item => item.question && item.answer);
}

function sanitizeTermsItems(items) {
    if (!Array.isArray(items)) {
        return [];
    }

    return items
        .map(item => ({
            title: typeof item.title === 'string' ? item.title.trim() : '',
            description: typeof item.description === 'string' ? item.description.trim() : ''
        }))
        .filter(item => item.title && item.description);
}

function renderFaqItems(containerId, items, openFirstItem = false) {
    const container = document.getElementById(containerId);
    if (!container || !Array.isArray(items) || !items.length) {
        return;
    }

    container.innerHTML = items.map((item, index) => `
        <details class="faq-item"${openFirstItem && index === 0 ? ' open' : ''}>
            <summary>${escapeHtml(item.question)}</summary>
            <p>${escapeHtml(item.answer)}</p>
        </details>
    `).join('');
}


function setupFaqAccordion(container, openFirstItem = false) {
    if (!container) {
        return;
    }

    const faqItems = [...container.querySelectorAll('.faq-item')];
    if (!faqItems.length) {
        return;
    }

    if (openFirstItem) {
        faqItems.forEach((item, index) => {
            item.open = index === 0;
        });
    }

    faqItems.forEach(item => {
        item.addEventListener('toggle', () => {
            if (!item.open) {
                return;
            }

            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.open) {
                    otherItem.open = false;
                }
            });
        });
    });
}

function initFaqAccordions(filename) {
    if (filename === 'index.html') {
        setupFaqAccordion(document.getElementById('landingFaqList'), true);
    } else if (filename === 'sss.html') {
        setupFaqAccordion(document.getElementById('faqList'), true);
    }
}

function renderTermsItems(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container || !Array.isArray(items) || !items.length) {
        return;
    }

    container.innerHTML = items.map(item => `
        <article class="terms-item">
            <h4>${escapeHtml(item.title)}</h4>
            <p>${escapeHtml(item.description)}</p>
        </article>
    `).join('');
}

function renderTermsNote(elementId, noteData) {
    const noteElement = document.getElementById(elementId);
    if (!noteElement) {
        return;
    }

    if (typeof noteData === 'string') {
        const normalizedText = noteData.trim();
        if (!normalizedText) {
            return;
        }

        noteElement.textContent = normalizedText;
        return;
    }

    if (!noteData || typeof noteData !== 'object') {
        return;
    }

    const prefix = typeof noteData.prefix === 'string' ? noteData.prefix.trim() : '';
    const linkLabel = typeof noteData.linkLabel === 'string' ? noteData.linkLabel.trim() : '';
    const linkHref = typeof noteData.linkHref === 'string' ? noteData.linkHref.trim() : '';
    const suffix = typeof noteData.suffix === 'string' ? noteData.suffix.trim() : '';

    if (!prefix && !linkLabel && !suffix) {
        return;
    }

    if (!linkLabel || !linkHref) {
        noteElement.textContent = [prefix, suffix].filter(Boolean).join(' ').trim();
        return;
    }

    noteElement.innerHTML = `
        ${escapeHtml(prefix)}
        <a class="auth-link" href="${escapeHtml(linkHref)}">${escapeHtml(linkLabel)}</a>
        ${escapeHtml(suffix)}
    `.replace(/\s+/g, ' ').trim();
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function pageNeedsQuizData(filename) {
    return ['quizzes.html', 'quiz.html', 'review.html', 'multiplayer.html'].includes(filename);
}

async function loadQuizData() {
    if (isQuizDataLoaded) {
        return true;
    }

    if (typeof axios === 'undefined') {
        alert('Axios bulunamadı. Lütfen internet bağlantısını ve script ayarını kontrol edin.');
        return false;
    }

    try {
        const response = await axios.get('/static/json/data.json');
        const payload = response.data;

        if (!payload || !Array.isArray(payload.quizzes)) {
            throw new Error('data.json formatı geçersiz.');
        }

        quizData = {
            quizzes: payload.quizzes,
            passingScore: typeof payload.passingScore === 'number' ? payload.passingScore : 70
        };

        isQuizDataLoaded = true;
        return true;
    } catch (error) {
        console.error('Quiz verisi yüklenemedi:', error);
        alert('Quiz verisi yüklenemedi. Lütfen sayfayı yenileyin.');
        return false;
    }
}

function renderQuestionMedia(question, mediaId, imageId, captionId) {
    const media = document.getElementById(mediaId);
    const image = document.getElementById(imageId);
    const caption = document.getElementById(captionId);

    if (!media || !image) {
        return;
    }

    const imageSource = typeof question.image === 'string' ? question.image.trim() : '';
    if (!imageSource) {
        image.removeAttribute('src');
        image.alt = 'Soru görseli';
        media.hidden = true;
        if (caption) {
            caption.textContent = '';
            caption.hidden = true;
        }
        return;
    }

    image.src = imageSource;
    image.alt = question.imageAlt || 'Soru görseli';
    media.hidden = false;

    if (!caption) {
        return;
    }

    const captionText = typeof question.imageCaption === 'string' ? question.imageCaption.trim() : '';
    caption.textContent = captionText;
    caption.hidden = captionText.length === 0;
}

function getReviewQuestionMediaMarkup(question) {
    const imageSource = typeof question.image === 'string' ? question.image.trim() : '';
    if (!imageSource) {
        return '';
    }

    const imageAlt = question.imageAlt || 'Soru görseli';
    const captionText = typeof question.imageCaption === 'string' ? question.imageCaption.trim() : '';
    return `
        <figure class="question-media question-media--review">
            <img src="${imageSource}" alt="${imageAlt}" class="question-media__image" loading="lazy">
            ${captionText ? `<figcaption class="question-media__caption">${captionText}</figcaption>` : ''}
        </figure>
    `;
}

function initAuthUI() {
    const isLoggedIn = window.QUIZFLOW_IS_LOGGED_IN === true;

    document.querySelectorAll('.header__login-btn, .header__register-btn').forEach(btn => {
        btn.style.display = isLoggedIn ? 'none' : '';
    });

    document.querySelectorAll('.header__profile-btn, .header__logout-btn').forEach(btn => {
        btn.style.display = isLoggedIn ? '' : 'none';
    });
}

function updateCircularTimer(textId, progressId, remaining, total) {
    const timerText = document.getElementById(textId);
    const timerProgress = document.getElementById(progressId);

    if (!timerText || !timerProgress) {
        return;
    }

    const safeRemaining = Math.max(remaining, 0);
    timerText.textContent = safeRemaining;

    const progress = (safeRemaining / total) * TIMER_CIRCUMFERENCE;
    timerProgress.style.strokeDashoffset = TIMER_CIRCUMFERENCE - progress;

    timerProgress.classList.remove('warning', 'danger');
    if (safeRemaining <= 10) {
        timerProgress.classList.add('danger');
    } else if (safeRemaining <= 20) {
        timerProgress.classList.add('warning');
    }
}
