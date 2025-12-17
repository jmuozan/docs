// Language Management
let currentLanguage = localStorage.getItem('language') || 'en';

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    updatePageLanguage();
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('lang', lang);
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.history.replaceState({}, '', newUrl);
}

function updatePageLanguage() {
    if (typeof translations === 'undefined') return;

    const trans = translations[currentLanguage];
    if (!trans) return;

    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (trans[key]) {
            element.textContent = trans[key];
        }
    });
}

function initLanguage() {
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');

    if (langParam && translations[langParam]) {
        currentLanguage = langParam;
        localStorage.setItem('language', langParam);
    }

    document.querySelectorAll('.dropdown-menu a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('href').split('=')[1];
            setLanguage(lang);
        });
    });

    updatePageLanguage();
}

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(savedTheme + '-mode');
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const isDark = document.body.classList.contains('dark-mode');
    const newTheme = isDark ? 'light' : 'dark';

    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(newTheme + '-mode');
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// Pages to fetch content from
const pages = [
    { url: 'projects/index_p.html', type: 'project' },
    { url: 'writings/index_w.html', type: 'writing' },
    { url: 'news/index_n.html', type: 'news' },
    { url: 'readings/index_r.html', type: 'reading' },
    { url: 'about/index_a.html', type: 'about' }
];

// Function to fetch and parse grid items from a page
async function fetchGridItems(pageUrl, pageType) {
    try {
        const response = await fetch(pageUrl);
        if (!response.ok) return [];

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Get all grid items from the page
        const items = doc.querySelectorAll('.grid-item');
        const gridItems = [];

        items.forEach(item => {
            const date = item.dataset.date;
            const link = item.querySelector('a');
            const img = item.querySelector('img');
            const title = item.querySelector('h3');
            const description = item.querySelector('.description');

            if (date && link && img && title && description) {
                // Get the href from the link, combine with the page folder path
                const href = link.getAttribute('href');
                const folderPath = pageUrl.replace(/\/index_[a-z]\.html$/, '');
                // Check if href is an external URL (starts with http:// or https://)
                const fullUrl = href.startsWith('http://') || href.startsWith('https://')
                    ? href
                    : `${folderPath}/${href}`;

                // Get the image src and make it relative to the root if needed
                let imageSrc = img.getAttribute('src');
                // If the image path doesn't start with ../ or http, prepend the folder path
                if (!imageSrc.startsWith('../') && !imageSrc.startsWith('http')) {
                    imageSrc = `${folderPath}/${imageSrc}`;
                }

                gridItems.push({
                    date: date,
                    imageUrl: imageSrc,
                    imageAlt: img.alt,
                    title: title.textContent,
                    description: description.textContent,
                    type: pageType,
                    linkUrl: fullUrl
                });
            }
        });

        return gridItems;
    } catch (error) {
        console.error(`Error fetching ${pageUrl}:`, error);
        return [];
    }
}

// Function to create and append a grid item
function createGridItem(item) {
    const article = document.createElement('article');
    article.className = 'grid-item';
    article.dataset.date = item.date;
    article.dataset.type = item.type;

    article.innerHTML = `
        <a href="${item.linkUrl}">
            <img src="${item.imageUrl}" alt="${item.imageAlt}">
            <div class="grid-content">
                <h3>${item.title}</h3>
                <p class="description">${item.description}</p>
                <time class="date">${formatDate(item.date)}</time>
            </div>
        </a>
    `;

    return article;
}

// Function to sort and display all items
function sortAndDisplayItems(items) {
    const grid = document.getElementById('main-grid');
    if (!grid) return;

    // Sort items by date (newest first)
    items.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA;
    });

    // Clear grid and add sorted items
    grid.innerHTML = '';
    items.forEach(item => {
        const gridItem = createGridItem(item);
        grid.appendChild(gridItem);
    });
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Function to populate and sort grid on section pages
function sortSectionGrid() {
    const grid = document.querySelector('.grid');
    if (!grid) return;

    const items = Array.from(grid.querySelectorAll('.grid-item'));

    // Populate date text from data-date attribute
    items.forEach(item => {
        const date = item.dataset.date;
        const timeElement = item.querySelector('.date');
        if (date && timeElement) {
            timeElement.textContent = formatDate(date);
        }
    });

    // Sort items by date (newest first)
    items.sort((a, b) => {
        const dateA = new Date(a.dataset.date);
        const dateB = new Date(b.dataset.date);
        return dateB - dateA;
    });

    // Clear grid and append sorted items
    grid.innerHTML = '';
    items.forEach(item => grid.appendChild(item));
}

// Initialize language and theme on all pages
document.addEventListener('DOMContentLoaded', function() {
    initLanguage();
    initTheme();

    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleTheme();
        });
    }
});

// Check if we're on a section page and sort it
if (window.location.pathname.includes('/index_')) {
    document.addEventListener('DOMContentLoaded', function() {
        sortSectionGrid();
    });
}

// Load all items from all pages on page load (only on main index)
if (!window.location.pathname.includes('/index_')) {
    document.addEventListener('DOMContentLoaded', async function() {
        const allItems = [];

        // Fetch items from all pages
        for (const page of pages) {
            const items = await fetchGridItems(page.url, page.type);
            allItems.push(...items);
        }

        // Sort items by date (newest first)
        allItems.sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            return dateB - dateA;
        });

        // Only show the last 10 items on the main index
        const recentItems = allItems.slice(0, 10);

        // Display recent items
        sortAndDisplayItems(recentItems);
    });
}
