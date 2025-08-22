// Enhanced Search JavaScript

// Search functionality
function performSearch() {
    const query = document.getElementById('projectSearch').value.trim();
    if (query.length < 2) {
        hideSearchResults();
        return;
    }

    // Show loading state
    const searchBtn = document.querySelector('.search-container .btn-link');
    const originalIcon = searchBtn.innerHTML;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    const lang = document.documentElement.lang || 'ar';
    fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${lang}`)
        .then(response => response.json())
        .then(projects => {
            displaySearchResults(projects, query);
            searchBtn.innerHTML = originalIcon;
        })
        .catch(error => {
            console.error('Search error:', error);
            searchBtn.innerHTML = originalIcon;
            hideSearchResults();
        });
}

function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performSearch();
    }
}

function displaySearchResults(projects, query) {
    const searchInput = document.getElementById('projectSearch');
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'search-results';
    resultsContainer.id = 'searchResults';
    
    // Remove existing results
    const existingResults = document.getElementById('searchResults');
    if (existingResults) {
        existingResults.remove();
    }

    if (projects.length === 0) {
        resultsContainer.innerHTML = `
            <div class="list-group">
                <div class="list-group-item text-center py-3">
                    <i class="fas fa-search text-muted mb-2" style="font-size: 2rem;"></i>
                    <p class="mb-0 text-muted">{% if lang == 'ar' %}لا توجد نتائج لـ "${query}"{% else %}No results found for "${query}"{% endif %}</p>
                </div>
            </div>
        `;
    } else {
        const lang = document.documentElement.lang || 'ar';
        resultsContainer.innerHTML = `
            <div class="list-group">
                ${projects.map(project => `
                    <a href="/project/${project.id}" class="list-group-item list-group-item-action">
                        <div class="search-result-item">
                            ${project.image_url ? `
                                <img src="${project.image_url}" alt="${project.title}" class="rounded">
                            ` : `
                                <div class="bg-light rounded d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                                    <i class="fas fa-code text-muted"></i>
                                </div>
                            `}
                            <div class="search-result-content">
                                <h6 class="search-result-title">${project.title}</h6>
                                <p class="search-result-description">${project.description}</p>
                            </div>
                        </div>
                    </a>
                `).join('')}
            </div>
        `;
    }

    // Position results below search input
    const searchContainer = document.querySelector('.search-container');
    searchContainer.appendChild(resultsContainer);
    
    // Close results when clicking outside
    document.addEventListener('click', function closeResults(e) {
        if (!searchContainer.contains(e.target)) {
            hideSearchResults();
            document.removeEventListener('click', closeResults);
        }
    });
}

function hideSearchResults() {
    const results = document.getElementById('searchResults');
    if (results) {
        results.remove();
    }
}

// Real-time search (optional enhancement)
function initRealTimeSearch() {
    const searchInput = document.getElementById('projectSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.trim().length >= 2) {
                    performSearch();
                } else {
                    hideSearchResults();
                }
            }, 300);
        });
    }
}

// Initialize search functionality
document.addEventListener('DOMContentLoaded', function() {
    initRealTimeSearch();
});

// Export search functions
window.Search = {
    performSearch,
    handleSearchKeyPress,
    hideSearchResults
};
