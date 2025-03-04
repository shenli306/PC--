document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");

    const expand = () => {
        searchBtn.classList.toggle("close");
        input.classList.toggle("square");
        if (searchBtn.classList.contains("close")) {
            input.focus();
        }
    };

    searchBtn.addEventListener("click", expand);
});

function checkSearch(event) {
    event.preventDefault(); // 阻止表单默认提交
    
    const searchInput = document.getElementById('search-input');
    const searchValue = searchInput.value.trim().toLowerCase();
    
    // 检查是否输入了"zyd"
    if (searchValue === 'zyd') {
        window.location.href = '/zero/'; // 确保使用正确的URL路径
        return false;
    }
    
    // 这里可以添加正常搜索功能的代码
    // ... 
    
    return false; // 防止表单提交
}
