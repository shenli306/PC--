document.addEventListener('DOMContentLoaded', function() {
    // 搜索和排序功能
    function initializeTableFilters() {
        document.querySelectorAll('.hardware-table').forEach(table => {
            const searchInput = table.closest('.brand-section').querySelector('.search-input');
            const sortSelect = table.closest('.brand-section').querySelector('.sort-select');
            
            if (searchInput && sortSelect) {
                const filterAndSort = () => {
                    const rows = Array.from(table.querySelectorAll('tbody tr'));
                    const searchTerm = searchInput.value.toLowerCase();
                    const sortValue = sortSelect.value;

                    // 过滤
                    rows.forEach(row => {
                        const text = row.querySelector('.model-cell').textContent.toLowerCase();
                        row.style.display = text.includes(searchTerm) ? '' : 'none';
                    });

                    // 排序
                    if (sortValue !== 'default') {
                        const visibleRows = rows.filter(row => row.style.display !== 'none');
                        sortRows(visibleRows, sortValue);
                        const tbody = table.querySelector('tbody');
                        visibleRows.forEach(row => tbody.appendChild(row));
                    }
                };

                searchInput.addEventListener('input', filterAndSort);
                sortSelect.addEventListener('change', filterAndSort);
            }
        });
    }

    // 初始化所有功能
    initializeTableFilters();
}); 