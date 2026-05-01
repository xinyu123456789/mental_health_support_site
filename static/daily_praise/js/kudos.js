document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('kudosForm');
    const submitBtn = document.getElementById('submitBtn');
    const feedbackMessage = document.getElementById('feedbackMessage');

    form.addEventListener('submit', function(e) {
        // 阻止表單預設的重整提交行為[cite: 4]
        e.preventDefault(); 
        
        const content = document.getElementById('praiseContent').value.trim();
        
        if (!content) return;

        // 準備發送資料，改變按鈕狀態防止重複點擊[cite: 4]
        submitBtn.disabled = true;
        submitBtn.innerText = '儲存中...';

        // 從 HTML 表單中取得 Django 的 CSRF token[cite: 4]
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // 關鍵修正：動態取得由 Django 生成的完整 API 網址
        const apiUrl = form.getAttribute('data-api-url');
        const successUrl = form.getAttribute('data-success-url');

        // 使用 Fetch API 發送 POST 請求至 Django 後端[cite: 4]
        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Django 要求的 Header[cite: 4]
            },
            body: JSON.stringify({
                praise_content: content 
            })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('儲存失敗');
        })
        .then(data => {
            window.location.href = successUrl;
        })
        .catch(error => {
            showFeedback(error.message, 'error'); 
            // 發生錯誤時才需要恢復按鈕狀態
            submitBtn.disabled = false;
            submitBtn.innerText = '好好紀錄下來';
        })
    });

    // 顯示提示訊息的輔助函式[cite: 4]
    function showFeedback(message, type) {
        feedbackMessage.innerText = message;
        feedbackMessage.className = type === 'success' ? 'msg-success' : 'msg-error';
        feedbackMessage.style.display = 'block';
        
        // 3秒後自動隱藏[cite: 4]
        setTimeout(() => {
            feedbackMessage.style.display = 'none';
        }, 3000);
    }
});