const sentences = [
  "はるのひかり",
  "そらはあおい",
  "やまをこえる",
  "まちをあるく",
  "わたしはうたう",
  "ゆめをみる"
];

let currentIndex = 0;
let experimentData = [];
let startTime = null;
let inputStarted = false;
let requiredChars = [];
let matchedIndexes = [];
let isInputComplete = false;
let charTimes = [];

const target = document.getElementById("target-sentence");
const input = document.getElementById("user-input");
const inputFeedback = document.getElementById("input-feedback");
const nextBtn = document.querySelector('#control-buttons button');

// 最小編集距離（MSD）を計算する関数
function calculateMSD(str1, str2) {
  const len1 = str1.length;
  const len2 = str2.length;
  const dp = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(0));
  
  for (let i = 0; i <= len1; i++) dp[i][0] = i;
  for (let j = 0; j <= len2; j++) dp[0][j] = j;
  
  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,     // 削除
          dp[i][j - 1] + 1,     // 挿入
          dp[i - 1][j - 1] + 1  // 置換
        );
      }
    }
  }
  
  return dp[len1][len2];
}

// 入力精度を計算（100 - (MSD / max(len1, len2)) * 100）
function calculateAccuracy(original, input) {
  const msd = calculateMSD(original, input);
  const maxLen = Math.max(original.length, input.length);
  if (maxLen === 0) return 100;
  return Math.max(0, 100 - (msd / maxLen) * 100);
}

// CER (Character Error Rate) を計算する関数
// 総入力文字数で割ることで、入力文字数に対する誤り率を計算
function calculateCER(original, input) {
  const msd = calculateMSD(original, input);
  const inputLength = input.length;  // 総入力文字数
  if (inputLength === 0) return 0;
  return msd / inputLength;
}

// 入力の正確性を視覚的に表示（部分列探索）
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
    const endTime = Date.now();
    const inputTime = (endTime - startTime) / 1000; // 秒
    const originalText = sentences[currentIndex];
    const accuracy = calculateAccuracy(originalText, inputText);
    const speed = originalText.length / inputTime; // 文字/秒
    
    const interCharMs = charTimes.map((t, i) => i ? t - charTimes[i-1] : 0);
    
    experimentData.push({
      sentenceIndex: currentIndex + 1,
      originalText: originalText,
      inputText: inputText,
      inputTime: inputTime,
      speed: speed,
      accuracy: accuracy,
      msd: calculateMSD(originalText, inputText),
      cer: calculateCER(originalText, inputText),
      charTimes: charTimes,
      interCharMs: interCharMs
    });
    // 「次の文へ」ボタンを表示
    nextBtn.style.display = 'inline-block';
    input.disabled = true;
  }
}

function showSentence(index) {
  target.textContent = sentences[index];
  input.value = "";
  input.disabled = false;
  inputStarted = false;
  startTime = null;
  requiredChars = sentences[index].split('');
  matchedIndexes = [];
  isInputComplete = false;
  inputFeedback.innerHTML = '';
  nextBtn.style.display = 'none';
  charTimes = [];
}

// 入力開始を検知
function onInputStart() {
  if (!inputStarted) {
    startTime = Date.now();
    inputStarted = true;
  }
}

function nextSentence() {
  currentIndex++;
  if (currentIndex < sentences.length) {
    showSentence(currentIndex);
  } else {
    // すべての文が終了したらアンケートを表示
    showSurvey();
  }
}

// アンケートを表示
function showSurvey() {
  target.textContent = "お疲れさまでした。以下のアンケートにお答えください。";
  
  const surveyHTML = `
    <div id="survey-container">
      <h3>アンケート</h3>
      <div class="survey-question">
        <label>1. 入力のしやすさはいかがでしたか？</label>
        <div class="rating">
          <input type="radio" name="ease" value="1" id="ease1"><label for="ease1">1 (とても難しい)</label>
          <input type="radio" name="ease" value="2" id="ease2"><label for="ease2">2 (難しい)</label>
          <input type="radio" name="ease" value="3" id="ease3"><label for="ease3">3 (普通)</label>
          <input type="radio" name="ease" value="4" id="ease4"><label for="ease4">4 (簡単)</label>
          <input type="radio" name="ease" value="5" id="ease5"><label for="ease5">5 (とても簡単)</label>
        </div>
      </div>
      
      <div class="survey-question">
        <label>2. 入力精度に満足していますか？</label>
        <div class="rating">
          <input type="radio" name="satisfaction" value="1" id="sat1"><label for="sat1">1 (とても不満)</label>
          <input type="radio" name="satisfaction" value="2" id="sat2"><label for="sat2">2 (不満)</label>
          <input type="radio" name="satisfaction" value="3" id="sat3"><label for="sat3">3 (普通)</label>
          <input type="radio" name="satisfaction" value="4" id="sat4"><label for="sat4">4 (満足)</label>
          <input type="radio" name="satisfaction" value="5" id="sat5"><label for="sat5">5 (とても満足)</label>
        </div>
      </div>
      
      <div class="survey-question">
        <label>3. 入力速度はいかがでしたか？</label>
        <div class="rating">
          <input type="radio" name="speed_feeling" value="1" id="speed1"><label for="speed1">1 (とても遅い)</label>
          <input type="radio" name="speed_feeling" value="2" id="speed2"><label for="speed2">2 (遅い)</label>
          <input type="radio" name="speed_feeling" value="3" id="speed3"><label for="speed3">3 (普通)</label>
          <input type="radio" name="speed_feeling" value="4" id="speed4"><label for="speed4">4 (速い)</label>
          <input type="radio" name="speed_feeling" value="5" id="speed5"><label for="speed5">5 (とても速い)</label>
        </div>
      </div>
      
      <div class="survey-question">
        <label>4. 全体的な使いやすさはいかがでしたか？</label>
        <div class="rating">
          <input type="radio" name="usability" value="1" id="use1"><label for="use1">1 (とても使いにくい)</label>
          <input type="radio" name="usability" value="2" id="use2"><label for="use2">2 (使いにくい)</label>
          <input type="radio" name="usability" value="3" id="use3"><label for="use3">3 (普通)</label>
          <input type="radio" name="usability" value="4" id="use4"><label for="use4">4 (使いやすい)</label>
          <input type="radio" name="usability" value="5" id="use5"><label for="use5">5 (とても使いやすい)</label>
        </div>
      </div>
      
      <div class="survey-question">
        <label>5. その他のご意見・ご感想があれば記入してください：</label>
        <textarea id="comments" rows="3" placeholder="任意でご記入ください"></textarea>
      </div>
      
      <button onclick="completeSurvey()" id="complete-btn">実験完了・データダウンロード</button>
    </div>
  `;
  
  input.style.display = 'none';
  document.getElementById('control-buttons').innerHTML = surveyHTML;
}

// アンケート完了とデータダウンロード
function completeSurvey() {
  const surveyData = {
    ease: document.querySelector('input[name="ease"]:checked')?.value || '',
    satisfaction: document.querySelector('input[name="satisfaction"]:checked')?.value || '',
    speed_feeling: document.querySelector('input[name="speed_feeling"]:checked')?.value || '',
    usability: document.querySelector('input[name="usability"]:checked')?.value || '',
    comments: document.getElementById('comments').value
  };
  
  const allInterCharMs = experimentData.flatMap(item => item.interCharMs.slice(1));
  const averageInterCharMs = allInterCharMs.length > 0 ? 
    allInterCharMs.reduce((sum, ms) => sum + ms, 0) / allInterCharMs.length : 0;
  
  // 実験データとアンケートデータを統合
  const completeData = {
    timestamp: new Date().toISOString(),
    experimentData: experimentData,
    surveyData: surveyData,
    summary: {
      totalSentences: sentences.length,
      averageSpeed: experimentData.reduce((sum, item) => sum + item.speed, 0) / experimentData.length,
      averageAccuracy: experimentData.reduce((sum, item) => sum + item.accuracy, 0) / experimentData.length,
      averageCER: experimentData.reduce((sum, item) => sum + item.cer, 0) / experimentData.length,
      totalTime: experimentData.reduce((sum, item) => sum + item.inputTime, 0),
      averageInterCharMs: averageInterCharMs
    }
  };
  
  // データをテキストファイルとしてダウンロード
  downloadData(completeData);
  
  // 完了メッセージを表示
  document.getElementById('survey-container').innerHTML = 
    '<h3>実験終了</h3><p>ご協力ありがとうございました。</p>';
}

// データダウンロード関数
function downloadData(data) {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `experiment_data_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// イベントリスナーを追加
input.addEventListener('input', (e) => {
  if (!isInputComplete) {
    onInputStart();
    updateInputFeedback(e.target.value);
  }
});

// 初期表示
showSentence(currentIndex);
