let allData = [];
let filteredData = [];
let currentPage = 1;
const itemsPerPage = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupEventListeners();
    startAutoRefresh();
    updateLastUpdateTime();
});

function setupEventListeners() {
    document.getElementById('searchInput').addEventListener('input', filterAndDisplay);
    document.getElementById('exchangeFilter').addEventListener('change', filterAndDisplay);
    document.getElementById('typeFilter').addEventListener('change', filterAndDisplay);
    document.getElementById('dateFilter').addEventListener('change', filterAndDisplay);
    document.getElementById('clearFilterBtn').addEventListener('click', clearFilters);
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
    document.getElementById('prevBtn').addEventListener('click', previousPage);
    document.getElementById('nextBtn').addEventListener('click', nextPage);
}

function loadData() {
    fetch('data/violations.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('数据加载失败');
            }
            return response.json();
        })
        .then(data => {
            allData = data.violations || [];
            filterAndDisplay();
            updateStatistics();
        })
        .catch(error => {
            console.error('加载数据错误:', error);
            displayNoData();
        });
}

function filterAndDisplay() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const exchangeFilter = document.getElementById('exchangeFilter').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const dateFilter = document.getElementById('dateFilter').value;

    filteredData = allData.filter(item => {
        const matchesSearch = !searchTerm || 
            item.company.toLowerCase().includes(searchTerm) ||
            item.content.toLowerCase().includes(searchTerm) ||
            item.exchange.toLowerCase().includes(searchTerm);

        const matchesExchange = !exchangeFilter || item.exchange === exchangeFilter;
        const matchesType = !typeFilter || item.type === typeFilter;

        let matchesDate = true;
        if (dateFilter) {
            const days = parseInt(dateFilter);
            const itemDate = new Date(item.date);
            const now = new Date();
            const daysDiff = (now - itemDate) / (1000 * 60 * 60 * 24);
            matchesDate = daysDiff <= days;
        }

        return matchesSearch && matchesExchange && matchesType && matchesDate;
    });

    filteredData.sort((a, b) => new Date(b.date) - new Date(a.date));

    currentPage = 1;
    displayData();
    updatePagination();
}

function displayData() {
    const dataList = document.getElementById('dataList');
    
    if (filteredData.length === 0) {
        displayNoData();
        return;
    }

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = filteredData.slice(start, end);

    dataList.innerHTML = pageData.map(item => createDataItem(item)).join('');
}

function createDataItem(item) {
    const typeClass = item.type === '违规' ? 'violation' : 
                      item.type === '通知' ? 'notification' : 'penalty';
    
    const dateObj = new Date(item.date);
    const formattedDate = formatDate(dateObj);

    return `
        <div class="data-item">
            <div class="item-header">
                <div>
                    <span class="item-exchange">${item.exchange}</span>
                    <span class="item-type ${typeClass}">${item.type}</span>
                </div>
                <div class="item-date">${formattedDate}</div>
            </div>
            <div class="item-company">企业: ${item.company}</div>
            <div class="item-content">
                <strong>违规内容:</strong> ${item.content}
            </div>
            ${item.penalty ? `<div class="item-penalty"><strong>处罚:</strong> ${item.penalty}</div>` : ''}
        </div>
    `;
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function displayNoData() {
    document.getElementById('dataList').innerHTML = '<div class="no-data">😔 未找到符合条件的记录</div>';
    hidePagination();
}

function updateStatistics() {
    const totalCount = allData.length;
    const violationCount = allData.filter(item => item.type === '违规').length;
    const exchanges = new Set(allData.map(item => item.exchange)).size;
    const notificationCount = allData.filter(item => item.type === '通知').length;

    document.getElementById('totalCount').textContent = totalCount;
    document.getElementById('violationCount').textContent = violationCount;
    document.getElementById('exchangeCount').textContent = exchanges;
    document.getElementById('notificationCount').textContent = notificationCount;
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('exchangeFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('dateFilter').value = '';
    filterAndDisplay();
}

function refreshData() {
    const btn = document.getElementById('refreshBtn');
    btn.disabled = true;
    btn.textContent = '⏳ 更新中...';

    setTimeout(() => {
        loadData();
        updateLastUpdateTime();
        btn.disabled = false;
        btn.textContent = '🔄 立即更新';
    }, 1000);
}

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN');
    document.getElementById('updateTime').textContent = `最后更新: ${timeString}`;
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        displayData();
        updatePagination();
        scrollToTop();
    }
}

function nextPage() {
    const maxPage = Math.ceil(filteredData.length / itemsPerPage);
    if (currentPage < maxPage) {
        currentPage++;
        displayData();
        updatePagination();
        scrollToTop();
    }
}

function updatePagination() {
    const maxPage = Math.ceil(filteredData.length / itemsPerPage);
    
    if (maxPage <= 1) {
        hidePagination();
        return;
    }

    showPagination();
    document.getElementById('pageInfo').textContent = `第 ${currentPage} / ${maxPage} 页`;
    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.getElementById('nextBtn').disabled = currentPage === maxPage;
}

function showPagination() {
    document.getElementById('pagination').style.display = 'flex';
}

function hidePagination() {
    document.getElementById('pagination').style.display = 'none';
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function startAutoRefresh() {
    setInterval(() => {
        loadData();
        updateLastUpdateTime();
    }, 3600000);
}