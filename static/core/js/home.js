document.addEventListener('DOMContentLoaded', function() {
    const greetingElement = document.getElementById('greeting-text');
    const quoteElement = document.getElementById('daily-quote');

    // 1. 動態問候語：根據時間改變內容
    function updateGreeting() {
        const hour = new Date().getHours();
        let timeText = "";
        
        if (hour < 6) timeText = "夜深了";
        else if (hour < 11) timeText = "早安";
        else if (hour < 14) timeText = "午安";
        else if (hour < 18) timeText = "下午好";
        else timeText = "晚安";

        // 檢查畫面上的暱稱元素
        const nicknameElement = document.querySelector('.user-nickname');
        if (nicknameElement) {
            // 如果已登入，只保留時間問候，讓右上角的「你好，某某某」去處理稱呼
            greetingElement.textContent = `${timeText}，辛苦了`;
        } else {
            // 如果沒登入，維持原本的「時間，辛苦了」
            greetingElement.textContent = `${timeText}，辛苦了`;
        }
    }

    // 2. 隨機心靈小語
    const quotes = [
        "「每個小小的進步，都值得被大聲讚美。」",
        "「在這裡，你可以放心地做回最真實的自己。」",
        "「今天的你已經做得很好了，休息一下也沒關係的。」",
        "「溫柔地對待自己，就是最偉大的力量。」"
    ];

    function updateQuote() {
        const randomIndex = Math.floor(Math.random() * quotes.length);
        quoteElement.textContent = quotes[randomIndex];
    }

    updateGreeting();
    updateQuote();
});