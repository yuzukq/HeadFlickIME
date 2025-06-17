const sentences = [
  "さんま",
  "あひる",
  "くるま",
  "たちよみ",
  "こーひー",
  "たいふう",
  "いのしし",
  "ほうせんか",
  "かつかれー",
  "めんちかつ",
  "しきおりおり",
  "せんもんてん",
  "まほうつかい",
];

let currentIndex = 0;
const target = document.getElementById("target-sentence");
const input = document.getElementById("user-input");

function showSentence(index) {
  target.textContent = sentences[index];
  input.value = "";
  input.focus();
}

function nextSentence() {
  currentIndex++;
  if (currentIndex < sentences.length) {
    showSentence(currentIndex);
  } else {
    target.textContent = "すべての文が終了しました。";
    input.disabled = true;
  }
}

// 初期表示
showSentence(currentIndex);
