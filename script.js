// Pages to fetch content from
const pages = [
    { url: 'projects.html', type: 'project' },
    { url: 'writings.html', type: 'writing' },
    { url: 'news.html', type: 'news' },
    { url: 'readings.html', type: 'reading' },
    { url: 'about.html', type: 'about' }
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
            const img = item.querySelector('img');
            const title = item.querySelector('h3');
            const description = item.querySelector('.description');
            const id = item.id || '';

            if (date && img && title && description) {
                gridItems.push({
                    date: date,
                    imageUrl: img.src,
                    imageAlt: img.alt,
                    title: title.textContent,
                    description: description.textContent,
                    type: pageType,
                    linkUrl: `${pageUrl}${id ? '#' + id : ''}`
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

// Load all items from all pages on page load
document.addEventListener('DOMContentLoaded', async function() {
    const allItems = [];

    // Fetch items from all pages
    for (const page of pages) {
        const items = await fetchGridItems(page.url, page.type);
        allItems.push(...items);
    }

    // Sort and display all items
    sortAndDisplayItems(allItems);
});
