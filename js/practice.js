// 練習用文章（測定と同じものを使用）
const sentences = [
  "はるのひかり",
  "やまをこえる",
  "まちをあるく",
  "わたしはうたう",
  "ゆめをみる"
];

// 4分間タイマー関連
const PRACTICE_DURATION_SEC = 240; // 4分
let timeLeft = PRACTICE_DURATION_SEC;
let timerInterval;

// 測定関連変数（記録はしないが、動作に必要）
let currentIndex = 0;
let inputStarted = false;
let requiredChars = [];
let matchedIndexes = [];
let isInputComplete = false;
let charTimes = [];
let countdownTimer = null;
let isCountingDown = false;

// DOM要素
const target = document.getElementById("target-sentence");
const input = document.getElementById("user-input");
const inputFeedback = document.getElementById("input-feedback");
const nextBtn = document.getElementById('next-btn');
const skipBtn = document.getElementById('skip-btn');
const timerDisplay = document.getElementById('timer');
const startMeasurementBtn = document.getElementById('start-measurement-btn');

// タイマー関連関数
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function startTimer() {
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
  setTimeout(() => {
    window.location.href = 'measure.html';
  }, 3000);
}

// カウントダウン機能（測定と同じ）
function startCountdown() {
  if (isCountingDown) return;
  
  isCountingDown = true;
  const overlay = document.getElementById('countdown-overlay');
  const countdownNumber = document.getElementById('countdown-number');
  
  overlay.style.display = 'flex';
  let count = 3;
  countdownNumber.textContent = count;
  
  countdownTimer = setInterval(() => {
    count--;
    if (count > 0) {
      countdownNumber.textContent = count;
    } else {
      clearInterval(countdownTimer);
      overlay.style.display = 'none';
      startMeasurement();
    }
  }, 1000);
}

function startMeasurement() {
  inputStarted = true;
  isCountingDown = false;
  input.focus();
}

// 入力フィードバック表示（測定と同じ、記録なし）
function updateInputFeedback(inputText) {
  let feedbackHTML = '';
  let matchPos = 0;
  matchedIndexes = [];
  
  if (inputText.length > charTimes.length) {
    charTimes.push(Date.now());
  }
  
  for (let i = 0; i < inputText.length; i++) {
    if (
      matchPos < requiredChars.length &&
      inputText[i] === requiredChars[matchPos]
    ) {
      feedbackHTML += `<span class="correct-char">${inputText[i]}</span>`;
      matchedIndexes.push(i);
      matchPos++;
    } else {
      feedbackHTML += `<span class="incorrect-char">${inputText[i]}</span>`;
    }
  }
  inputFeedback.innerHTML = feedbackHTML;

  // すべての必要な文字が順番通りに現れた場合
  if (matchPos === requiredChars.length && !isInputComplete) {
    isInputComplete = true;
    nextBtn.style.display = 'inline-block';
    input.disabled = true;
  }
}

// 文章表示（測定と同じ）
function showSentence(index) {
  if (index >= sentences.length) {
    // 文章が終わったら最初に戻る
    currentIndex = 0;
    index = 0;
  }

  target.textContent = sentences[index];
  input.value = "";
  input.disabled = false;
  inputStarted = false;
  requiredChars = sentences[index].split('');
  matchedIndexes = [];
  isInputComplete = false;
  isCountingDown = false;
  inputFeedback.innerHTML = '';
  nextBtn.style.display = 'none';
  charTimes = [];
  
  // カウントダウンタイマーをクリア
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  
  // オーバーレイを非表示
  const overlay = document.getElementById('countdown-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

// 次の文へ進む
function nextSentence() {
  currentIndex++;
  showSentence(currentIndex);
}

// 文をスキップ
function skipSentence() {
  nextSentence();
}

// イベントリスナー
input.addEventListener('input', (e) => {
  if (!isInputComplete && inputStarted) {
    updateInputFeedback(e.target.value);
  }
});

input.addEventListener('focus', () => {
  if (!inputStarted && !isCountingDown) {
    input.blur();
    startCountdown();
  }
});

// 「今すぐ測定へ」ボタンの処理
startMeasurementBtn.addEventListener('click', () => {
  clearInterval(timerInterval);
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }
  window.location.href = 'measure.html';
});

// 初期化
document.addEventListener('DOMContentLoaded', () => {
  startTimer();
  showSentence(currentIndex);
});
