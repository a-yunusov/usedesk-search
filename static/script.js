const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const resultsContainer = document.getElementById('resultsContainer');
const resultsTableBody = document.getElementById('resultsTableBody');
const paginationContainer = document.getElementById('paginationContainer');
const paginationList = document.getElementById('paginationList');
const resultsInfo = document.getElementById('resultsInfo');
const errorContainer = document.getElementById('errorContainer');
const loadingContainer = document.getElementById('loadingContainer');

const USEDESK_BASE_URL = 'https://secure.usedesk.ru/tickets';

searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const query = searchInput.value.trim();
    
    if (!query) {
        showError('Пожалуйста, введите поисковый запрос');
        return;
    }
    
    performSearch(query, 1);
});

function performSearch(query, page) {
    showLoading();
    hideResults();
    hideError();
    
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query,
            page: page
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сервера');
        }
        return response.json();
    })
    .then(data => {
        handleSearchResults(data, query);
    })
    .catch(error => {
        console.error('Ошибка при поиске:', error);
        showError('Произошла ошибка при поиске тикетов. Пожалуйста, попробуйте еще раз.');
    })
    .finally(() => {
        hideLoading();
    });
}

function handleSearchResults(data, query) {
    if (data.error) {
        showError(data.error);
        return;
    }
    
    if (data.tickets && data.tickets.length > 0) {
        displayResults(data.tickets, data.total, data.page, data.total_pages, query);
    } else {
        showError('По вашему запросу не найдено тикетов');
    }
}

function displayResults(tickets, total, currentPage, totalPages, query) {
    resultsTableBody.innerHTML = '';
    
    tickets.forEach(ticket => {
        const row = document.createElement('tr');
        
        const ticketUrl = `${USEDESK_BASE_URL}/${ticket.id}`;
        
        row.innerHTML = `
            <td>
                <a href="${ticketUrl}" target="_blank" class="ticket-link">
                    ${ticket.id}
                </a>
            </td>
            <td>${escapeHtml(ticket.subject)}</td>
            <td>${escapeHtml(ticket.assignee_name)}</td>
            <td><span class="status-${ticket.status_class}">${ticket.status_text}</span></td>
            <td>${ticket.created_at_formatted}</td>
            <td>${escapeHtml(ticket.client_info)}</td>
        `;
        
        resultsTableBody.appendChild(row);
    });
    
    displayPagination(currentPage, totalPages, query);
    displayResultsInfo(total, currentPage, totalPages);
    showResults();
}

function displayPagination(currentPage, totalPages, query) {
    paginationList.innerHTML = '';
    
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    }
    
    paginationContainer.style.display = 'block';
    
    if (currentPage > 1) {
        const prevItem = createPaginationItem('←', () => {
            performSearch(query, currentPage - 1);
        });
        paginationList.appendChild(prevItem);
    }
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageItem = createPaginationItem(i, () => {
                performSearch(query, i);
            }, i === currentPage);
            paginationList.appendChild(pageItem);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsis = document.createElement('li');
            ellipsis.className = 'page-item disabled';
            ellipsis.innerHTML = '<span class="page-link">...</span>';
            paginationList.appendChild(ellipsis);
        }
    }
    
    if (currentPage < totalPages) {
        const nextItem = createPaginationItem('→', () => {
            performSearch(query, currentPage + 1);
        });
        paginationList.appendChild(nextItem);
    }
}

function createPaginationItem(text, onClick, active = false) {
    const li = document.createElement('li');
    li.className = `page-item ${active ? 'active' : ''}`;
    
    const link = document.createElement('a');
    link.className = 'page-link';
    link.href = '#';
    link.textContent = text;
    link.addEventListener('click', (e) => {
        e.preventDefault();
        onClick();
    });
    
    li.appendChild(link);
    return li;
}

function displayResultsInfo(total, currentPage, totalPages) {
    const start = (currentPage - 1) * 10 + 1;
    const end = Math.min(currentPage * 10, total);
    
    let text;
    if (total === 1) {
        // Для единственного числа
        text = `Найден <strong>${total}</strong> тикет`;
    } else {
        // Для множественного числа
        text = `Найдено <strong>${total}</strong> тикет${getPlural(total, ['', 'а', 'ов'])}`;
    }
    
    resultsInfo.innerHTML = `
        ${text} | 
        Страница: <strong>${currentPage}</strong> из <strong>${totalPages}</strong>
    `;
}

function getPlural(num, forms) {
    const cases = [2, 0, 1, 1, 1, 2];
    return forms[(num % 100 > 4 && num % 100 < 20) ? 2 : cases[(num % 10 < 5) ? num % 10 : 5]];
}

function getStatusClass(status) {
    if (status === 1) return 'open';
    if (status === 2) return 'closed';
    if (status === 3) return 'pending';
    return 'unknown';
}

function escapeHtml(text) {
    if (!text) return '';
    return text.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function showError(message) {
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
    resultsContainer.style.display = 'none';
}

function hideError() {
    errorContainer.style.display = 'none';
}

function showResults() {
    resultsContainer.style.display = 'block';
}

function hideResults() {
    resultsContainer.style.display = 'none';
}

function showLoading() {
    loadingContainer.style.display = 'block';
}

function hideLoading() {
    loadingContainer.style.display = 'none';
}