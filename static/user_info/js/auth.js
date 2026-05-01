document.addEventListener('DOMContentLoaded', function() {
    // 尋找畫面上所有的密碼輸入框
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(function(input) {
        // 為每個密碼框建立一個外層容器，方便我們把按鈕塞進去
        const wrapper = document.createElement('div');
        wrapper.className = 'password-wrapper';
        wrapper.style.position = 'relative'; // 設定相對定位

        // 把原本的 input 用 wrapper 包起來
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // 建立「顯示/隱藏」的切換按鈕
        const toggleBtn = document.createElement('span');
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = '👁️'; // 可以替換成更漂亮的 SVG 或 FontAwesome 圖示
        
        // 設定按鈕樣式（將它絕對定位在輸入框右側）
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '15px';
        toggleBtn.style.top = '50%';
        toggleBtn.style.transform = 'translateY(-50%)';
        toggleBtn.style.cursor = 'pointer';
        toggleBtn.style.userSelect = 'none';
        toggleBtn.style.opacity = '0.6';

        // 點擊事件：切換密碼顯示狀態
        toggleBtn.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                toggleBtn.style.opacity = '1'; // 顯示時變亮
            } else {
                input.type = 'password';
                toggleBtn.style.opacity = '0.6'; // 隱藏時變暗
            }
        });

        // 把按鈕加到密碼框旁邊
        wrapper.appendChild(toggleBtn);
    });
});