document.addEventListener('DOMContentLoaded', () => {
  const PRACTICE_DURATION_SEC = 240; // 4分
  
  const timerDisplay = document.getElementById('timer');
  const startMeasurementBtn = document.getElementById('start-measurement-btn');
  
  let timeLeft = PRACTICE_DURATION_SEC;
  let timerInterval;

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
  }
  
  function startTimer() {
    // 最初に表示を更新
    timerDisplay.textContent = formatTime(timeLeft);

    timerInterval = setInterval(() => {
      timeLeft--;
      timerDisplay.textContent = formatTime(timeLeft);
      
      if (timeLeft <= 30) {
        timerDisplay.classList.add('warning');
      }
      
      if (timeLeft <= 0) {
        endPractice();
      }
    }, 1000);
  }
  
  function endPractice() {
    clearInterval(timerInterval);
    alert('練習終了。測定を開始します。');
    // 3秒後に測定ページへ遷移
    setTimeout(() => {
      window.location.href = 'measure.html';
    }, 3000);
  }

  // 「今すぐ測定へ」ボタンの処理
  startMeasurementBtn.addEventListener('click', () => {
    clearInterval(timerInterval); // 進行中のタイマーを停止
    window.location.href = 'measure.html';
  });

  // ページが読み込まれたらタイマーを開始
  startTimer();
});
