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
                const fullUrl = `${folderPath}/${href}`;

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

// Check if we're on a section page and sort it
if (window.location.pathname.includes('/index_')) {
    document.addEventListener('DOMContentLoaded', function() {
        sortSectionGrid();
    });
}

// Load all items from all pages on page load
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
