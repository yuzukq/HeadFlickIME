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
let isInterrupted = false;  // 中断フラグを追加

const target = document.getElementById("target-sentence");
const input = document.getElementById("user-input");
const inputFeedback = document.getElementById("input-feedback");
const nextBtn = document.getElementById('next-btn');

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

// 中断ボタンの処理
function interruptSentence() {
  // カウントダウン中の場合は停止
  if (isCountingDown) {
    if (countdownTimer) {
      clearInterval(countdownTimer);
      countdownTimer = null;
    }
    isCountingDown = false;
    const overlay = document.getElementById('countdown-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
    nextSentence();
    return;
  }
  
  if (inputStarted && !isInputComplete) {
    isInterrupted = true;
    const endTime = Date.now();
    const inputTime = (endTime - startTime) / 1000; // 秒
    const originalText = sentences[currentIndex];
    const inputText = input.value;
    const accuracy = calculateAccuracy(originalText, inputText);
    const speed = inputText.length > 0 ? inputText.length / inputTime : 0; // CPS:文字/秒
    
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
      interCharMs: interCharMs,
      interrupted: true  // 中断フラグを追加
    });
    
    // 次の文へ進む
    nextSentence();
  }
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
    const speed = originalText.length / inputTime; // CPS:文字/秒
    
    const interCharMs = charTimes.map((t, i) => i ? t - charTimes[i-1] : 0);
    
    experimentData.push({
      sentenceIndex: currentIndex + 1,
      originalText: originalText,
      inputText: inputText, // 入力されたテキスト
      inputTime: inputTime, // 入力時間
      speed: speed,
      accuracy: accuracy, // 入力精度
      msd: calculateMSD(originalText, inputText), // 最小編集距離
      cer: calculateCER(originalText, inputText), // 文字エラー率
      charTimes: charTimes, 
      interCharMs: interCharMs, // 文字間インターバル
      interrupted: false  // 中断フラグを追加
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
  isInterrupted = false;  // 中断フラグをリセット
  isCountingDown = false; // カウントダウンフラグをリセット
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
      <p>各項目について、最も当てはまるものを選択してください。</p>

      <!-- SUS (システムユーザビリティスケール) -->
      <h4>システム全体の使いやすさ (SUS)</h4>
      <div class="survey-question">
        <label>1. この入力方法は、今後も頻繁に使いたいと思える。</label>
        <div class="rating">
          <input type="radio" name="sus1" value="1" id="sus1-1"><label for="sus1-1">1:全くそう思わない</label>
          <input type="radio" name="sus1" value="2" id="sus1-2"><label for="sus1-2">2</label>
          <input type="radio" name="sus1" value="3" id="sus1-3"><label for="sus1-3">3</label>
          <input type="radio" name="sus1" value="4" id="sus1-4"><label for="sus1-4">4</label>
          <input type="radio" name="sus1" value="5" id="sus1-5"><label for="sus1-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>2. この入力方法は、不必要に複雑だと感じた。</label>
        <div class="rating">
          <input type="radio" name="sus2" value="1" id="sus2-1"><label for="sus2-1">1:全くそう思わない</label>
          <input type="radio" name="sus2" value="2" id="sus2-2"><label for="sus2-2">2</label>
          <input type="radio" name="sus2" value="3" id="sus2-3"><label for="sus2-3">3</label>
          <input type="radio" name="sus2" value="4" id="sus2-4"><label for="sus2-4">4</label>
          <input type="radio" name="sus2" value="5" id="sus2-5"><label for="sus2-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>3. この入力方法は、とても使いやすいと思った。</label>
        <div class="rating">
          <input type="radio" name="sus3" value="1" id="sus3-1"><label for="sus3-1">1:全くそう思わない</label>
          <input type="radio" name="sus3" value="2" id="sus3-2"><label for="sus3-2">2</label>
          <input type="radio" name="sus3" value="3" id="sus3-3"><label for="sus3-3">3</label>
          <input type="radio" name="sus3" value="4" id="sus3-4"><label for="sus3-4">4</label>
          <input type="radio" name="sus3" value="5" id="sus3-5"><label for="sus3-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>4. この入力方法を使いこなすには、専門家の助けが必要だと感じた。</label>
        <div class="rating">
          <input type="radio" name="sus4" value="1" id="sus4-1"><label for="sus4-1">1:全くそう思わない</label>
          <input type="radio" name="sus4" value="2" id="sus4-2"><label for="sus4-2">2</label>
          <input type="radio" name="sus4" value="3" id="sus4-3"><label for="sus4-3">3</label>
          <input type="radio" name="sus4" value="4" id="sus4-4"><label for="sus4-4">4</label>
          <input type="radio" name="sus4" value="5" id="sus4-5"><label for="sus4-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>5. この入力方法の機能（子音選択、母音選択など）は、うまく統合されていると感じた。</label>
        <div class="rating">
          <input type="radio" name="sus5" value="1" id="sus5-1"><label for="sus5-1">1:全くそう思わない</label>
          <input type="radio" name="sus5" value="2" id="sus5-2"><label for="sus5-2">2</label>
          <input type="radio" name="sus5" value="3" id="sus5-3"><label for="sus5-3">3</label>
          <input type="radio" name="sus5" value="4" id="sus5-4"><label for="sus5-4">4</label>
          <input type="radio" name="sus5" value="5" id="sus5-5"><label for="sus5-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>6. この入力方法の操作には、一貫性のない部分が多すぎると感じた。</label>
        <div class="rating">
          <input type="radio" name="sus6" value="1" id="sus6-1"><label for="sus6-1">1:全くそう思わない</label>
          <input type="radio" name="sus6" value="2" id="sus6-2"><label for="sus6-2">2</label>
          <input type="radio" name="sus6" value="3" id="sus6-3"><label for="sus6-3">3</label>
          <input type="radio" name="sus6" value="4" id="sus6-4"><label for="sus6-4">4</label>
          <input type="radio" name="sus6" value="5" id="sus6-5"><label for="sus6-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>7. ほとんどの人は、この入力方法をすぐに習得できると思う。</label>
        <div class="rating">
          <input type="radio" name="sus7" value="1" id="sus7-1"><label for="sus7-1">1:全くそう思わない</label>
          <input type="radio" name="sus7" value="2" id="sus7-2"><label for="sus7-2">2</label>
          <input type="radio" name="sus7" value="3" id="sus7-3"><label for="sus7-3">3</label>
          <input type="radio" name="sus7" value="4" id="sus7-4"><label for="sus7-4">4</label>
          <input type="radio" name="sus7" value="5" id="sus7-5"><label for="sus7-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>8. この入力方法を使うのは、とても面倒だと感じた。</label>
        <div class="rating">
          <input type="radio" name="sus8" value="1" id="sus8-1"><label for="sus8-1">1:全くそう思わない</label>
          <input type="radio" name="sus8" value="2" id="sus8-2"><label for="sus8-2">2</label>
          <input type="radio" name="sus8" value="3" id="sus8-3"><label for="sus8-3">3</label>
          <input type="radio" name="sus8" value="4" id="sus8-4"><label for="sus8-4">4</label>
          <input type="radio" name="sus8" value="5" id="sus8-5"><label for="sus8-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>9. この入力方法を、自信を持って使うことができた。</label>
        <div class="rating">
          <input type="radio" name="sus9" value="1" id="sus9-1"><label for="sus9-1">1:全くそう思わない</label>
          <input type="radio" name="sus9" value="2" id="sus9-2"><label for="sus9-2">2</label>
          <input type="radio" name="sus9" value="3" id="sus9-3"><label for="sus9-3">3</label>
          <input type="radio" name="sus9" value="4" id="sus9-4"><label for="sus9-4">4</label>
          <input type="radio" name="sus9" value="5" id="sus9-5"><label for="sus9-5">5:強くそう思う</label>
        </div>
      </div>
      <div class="survey-question">
        <label>10. この入力方法を使い始める前に、多くのことを覚える必要があった。</label>
        <div class="rating">
          <input type="radio" name="sus10" value="1" id="sus10-1"><label for="sus10-1">1:全くそう思わない</label>
          <input type="radio" name="sus10" value="2" id="sus10-2"><label for="sus10-2">2</label>
          <input type="radio" name="sus10" value="3" id="sus10-3"><label for="sus10-3">3</label>
          <input type="radio" name="sus10" value="4" id="sus10-4"><label for="sus10-4">4</label>
          <input type="radio" name="sus10" value="5" id="sus10-5"><label for="sus10-5">5:強くそう思う</label>
        </div>
      </div>

      <!-- NASA-TLX -->
      <h4>作業中の負担感 (NASA-TLX)</h4>
      <div class="survey-question">
        <label>1. 知的要求: 文字を入力するために、どれくらい集中したり、考えたりする必要がありましたか？</label>
        <div class="rating">
          <input type="radio" name="tlx_mental" value="1" id="tlx_mental-1"><label for="tlx_mental-1">1:非常に少なかった</label>
          <input type="radio" name="tlx_mental" value="2" id="tlx_mental-2"><label for="tlx_mental-2">2</label>
          <input type="radio" name="tlx_mental" value="3" id="tlx_mental-3"><label for="tlx_mental-3">3</label>
          <input type="radio" name="tlx_mental" value="4" id="tlx_mental-4"><label for="tlx_mental-4">4</label>
          <input type="radio" name="tlx_mental" value="5" id="tlx_mental-5"><label for="tlx_mental-5">5:非常に多かった</label>
        </div>
      </div>
       <div class="survey-question">
        <label>2. 身体的要求: 文字を入力するために、頭を動かすなどの身体的な活動はどれくらい必要でしたか？</label>
        <div class="rating">
          <input type="radio" name="tlx_physical" value="1" id="tlx_physical-1"><label for="tlx_physical-1">1:非常に少なかった</label>
          <input type="radio" name="tlx_physical" value="2" id="tlx_physical-2"><label for="tlx_physical-2">2</label>
          <input type="radio" name="tlx_physical" value="3" id="tlx_physical-3"><label for="tlx_physical-3">3</label>
          <input type="radio" name="tlx_physical" value="4" id="tlx_physical-4"><label for="tlx_physical-4">4</label>
          <input type="radio" name="tlx_physical" value="5" id="tlx_physical-5"><label for="tlx_physical-5">5:非常に多かった</label>
        </div>
      </div>
      <div class="survey-question">
        <label>3. 時間的切迫感: 文字の入力中、時間に追われているようなプレッシャーをどれくらい感じましたか？</label>
        <div class="rating">
          <input type="radio" name="tlx_temporal" value="1" id="tlx_temporal-1"><label for="tlx_temporal-1">1:全く感じなかった</label>
          <input type="radio" name="tlx_temporal" value="2" id="tlx_temporal-2"><label for="tlx_temporal-2">2</label>
          <input type="radio" name="tlx_temporal" value="3" id="tlx_temporal-3"><label for="tlx_temporal-3">3</label>
          <input type="radio" name="tlx_temporal" value="4" id="tlx_temporal-4"><label for="tlx_temporal-4">4</label>
          <input type="radio" name="tlx_temporal" value="5" id="tlx_temporal-5"><label for="tlx_temporal-5">5:非常に感じた</label>
        </div>
      </div>
      <div class="survey-question">
        <label>4. 作業成績の自己評価: 今回の実験の目標（速く正確な入力）を、どれくらいうまく達成できたと思いますか？</label>
        <div class="rating">
          <input type="radio" name="tlx_performance" value="1" id="tlx_performance-1"><label for="tlx_performance-1">1:全くうまくできなかった</label>
          <input type="radio" name="tlx_performance" value="2" id="tlx_performance-2"><label for="tlx_performance-2">2</label>
          <input type="radio" name="tlx_performance" value="3" id="tlx_performance-3"><label for="tlx_performance-3">3</label>
          <input type="radio" name="tlx_performance" value="4" id="tlx_performance-4"><label for="tlx_performance-4">4</label>
          <input type="radio" name="tlx_performance" value="5" id="tlx_performance-5"><label for="tlx_performance-5">5:完璧にできた</label>
        </div>
      </div>
      <div class="survey-question">
        <label>5. 努力: 設定された目標を達成するために、どれくらい精神的・身体的な努力をする必要がありましたか？</label>
        <div class="rating">
          <input type="radio" name="tlx_effort" value="1" id="tlx_effort-1"><label for="tlx_effort-1">1:ほとんど必要なかった</label>
          <input type="radio" name="tlx_effort" value="2" id="tlx_effort-2"><label for="tlx_effort-2">2</label>
          <input type="radio" name="tlx_effort" value="3" id="tlx_effort-3"><label for="tlx_effort-3">3</label>
          <input type="radio" name="tlx_effort" value="4" id="tlx_effort-4"><label for="tlx_effort-4">4</label>
          <input type="radio" name="tlx_effort" value="5" id="tlx_effort-5"><label for="tlx_effort-5">5:非常に多くの努力が必要だった</label>
        </div>
      </div>
      <div class="survey-question">
        <label>6. フラストレーション: 入力作業中に、イライラしたり、不満に感じたりすることはどれくらいありましたか？</label>
        <div class="rating">
          <input type="radio" name="tlx_frustration" value="1" id="tlx_frustration-1"><label for="tlx_frustration-1">1:全くなかった</label>
          <input type="radio" name="tlx_frustration" value="2" id="tlx_frustration-2"><label for="tlx_frustration-2">2</label>
          <input type="radio" name="tlx_frustration" value="3" id="tlx_frustration-3"><label for="tlx_frustration-3">3</label>
          <input type="radio" name="tlx_frustration" value="4" id="tlx_frustration-4"><label for="tlx_frustration-4">4</label>
          <input type="radio" name="tlx_frustration" value="5" id="tlx_frustration-5"><label for="tlx_frustration-5">5:非常にあった</label>
        </div>
      </div>
      
      <button onclick="completeSurvey()" id="complete-btn">実験完了・データダウンロード</button>
    </div>
  `;
  
  input.style.display = 'none';
  document.getElementById('control-buttons').innerHTML = surveyHTML;
}

// アンケート完了とデータダウンロード
function completeSurvey() {
  const sus_answers = [];
  for (let i = 1; i <= 10; i++) {
    const answer = document.querySelector(`input[name="sus${i}"]:checked`)?.value;
    sus_answers.push(answer ? parseInt(answer, 10) : null);
  }

  let sus_score = null;
  if (sus_answers.every(a => a !== null)) {
      const score_q1 = sus_answers[0] - 1;
      const score_q2 = 5 - sus_answers[1];
      const score_q3 = sus_answers[2] - 1;
      const score_q4 = 5 - sus_answers[3];
      const score_q5 = sus_answers[4] - 1;
      const score_q6 = 5 - sus_answers[5];
      const score_q7 = sus_answers[6] - 1;
      const score_q8 = 5 - sus_answers[7];
      const score_q9 = sus_answers[8] - 1;
      const score_q10 = 5 - sus_answers[9];
      const total_score = score_q1 + score_q2 + score_q3 + score_q4 + score_q5 + score_q6 + score_q7 + score_q8 + score_q9 + score_q10;
      sus_score = total_score * 2.5;
  }
  
  const participantId = localStorage.getItem('participantId') || 'unknown';

  const surveyData = {
    sus: {
      q1: sus_answers[0], q2: sus_answers[1], q3: sus_answers[2], q4: sus_answers[3], q5: sus_answers[4],
      q6: sus_answers[5], q7: sus_answers[6], q8: sus_answers[7], q9: sus_answers[8], q10: sus_answers[9]
    },
    tlx: {
      mental: document.querySelector('input[name="tlx_mental"]:checked')?.value || '',
      physical: document.querySelector('input[name="tlx_physical"]:checked')?.value || '',
      temporal: document.querySelector('input[name="tlx_temporal"]:checked')?.value || '',
      performance: document.querySelector('input[name="tlx_performance"]:checked')?.value || '',
      effort: document.querySelector('input[name="tlx_effort"]:checked')?.value || '',
      frustration: document.querySelector('input[name="tlx_frustration"]:checked')?.value || ''
    }
  };
  
  const allInterCharMs = experimentData.flatMap(item => item.interCharMs.slice(1));
  const averageInterCharMs = allInterCharMs.length > 0 ? 
    allInterCharMs.reduce((sum, ms) => sum + ms, 0) / allInterCharMs.length : 0;
  
  // 実験データとアンケートデータを統合
  const completeData = {
    participantId: participantId,
    timestamp: new Date().toISOString(),
    experimentData: experimentData,
    surveyData: surveyData,
    surveySummary: {
      sus_score: sus_score
    },
    summary: {
      totalSentences: sentences.length,
      completedSentences: experimentData.filter(item => !item.interrupted).length,
      interruptedSentences: experimentData.filter(item => item.interrupted).length,
      averageSpeed: experimentData.filter(item => !item.interrupted).length > 0 ? 
        experimentData.filter(item => !item.interrupted).reduce((sum, item) => sum + item.speed, 0) / 
        experimentData.filter(item => !item.interrupted).length : 0,
      averageAccuracy: experimentData.filter(item => !item.interrupted).length > 0 ? 
        experimentData.filter(item => !item.interrupted).reduce((sum, item) => sum + item.accuracy, 0) / 
        experimentData.filter(item => !item.interrupted).length : 0,
      averageCER: experimentData.filter(item => !item.interrupted).length > 0 ? 
        experimentData.filter(item => !item.interrupted).reduce((sum, item) => sum + item.cer, 0) / 
        experimentData.filter(item => !item.interrupted).length : 0,
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

// カウントダウン機能
let countdownTimer = null;
let isCountingDown = false;

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
      // カウントダウン終了後に測定開始
      startMeasurement();
    }
  }, 1000);
}

function startMeasurement() {
  // 実際の測定開始処理
  startTime = Date.now();
  inputStarted = true;
  isCountingDown = false; // ここでfalseに設定
  input.focus();
}

// イベントリスナーを追加
input.addEventListener('input', (e) => {
  if (!isInputComplete && inputStarted) {
    updateInputFeedback(e.target.value);
  }
});

// フォーカスイベントでカウントダウンを開始
input.addEventListener('focus', () => {
  if (!inputStarted && !isCountingDown) {
    input.blur(); // 一度フォーカスを外す
    startCountdown();
  }
});

// 初期表示
showSentence(currentIndex);
