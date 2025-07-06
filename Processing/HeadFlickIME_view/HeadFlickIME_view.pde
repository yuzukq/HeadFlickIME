import processing.serial.*;
import java.awt.Robot;
import java.awt.event.KeyEvent;
import java.awt.Toolkit;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.Clipboard;

Serial myPort;
Robot robot;
Clipboard clipboard; // 文字入力用

String[][] consonantTable = {
  {"あ", "か", "さ"},
  {"た", "な", "は"},
  {"ま", "や", "ら"},
  {"*", "わ", "*"}
};

int row = 1;
int col = 1;
boolean inSecondLayer = false;
String currentConsonant = "";

// 第二レイヤー用の母音表示配列（動的に更新）
String[][] vowelDisplay = {
  {"", "", ""},
  {"", "", ""},
  {"", "", ""}
};

// 子音に応じた母音表示を更新する関数
void updateVowelDisplay(String consonant) {
  String[] kana = new String[5];
  if (consonant.equals("a")) {
    kana = new String[]{"あ", "い", "う", "え", "お"};
  } else if (consonant.equals("k")) {
    kana = new String[]{"か", "き", "く", "け", "こ"};
  } else if (consonant.equals("s")) {
    kana = new String[]{"さ", "し", "す", "せ", "そ"};
  } else if (consonant.equals("t")) {
    kana = new String[]{"た", "ち", "つ", "て", "と"};
  } else if (consonant.equals("n")) {
    kana = new String[]{"な", "に", "ぬ", "ね", "の"};
  } else if (consonant.equals("h")) {
    kana = new String[]{"は", "ひ", "ふ", "へ", "ほ"};
  } else if (consonant.equals("m")) {
    kana = new String[]{"ま", "み", "む", "め", "も"};
  } else if (consonant.equals("y")) {
    kana = new String[]{"や", "「", "ゆ", "」", "よ"};
  } else if (consonant.equals("r")) {
    kana = new String[]{"ら", "り", "る", "れ", "ろ"};
  } else if (consonant.equals("w")) {
    kana = new String[]{"わ", "!", "ん", "ー", "を"};
  }

  // 十字キー配置で母音を配置
  vowelDisplay[0][1] = kana[2]; // う
  vowelDisplay[1][0] = kana[1]; // い
  vowelDisplay[1][1] = kana[0]; // あ
  vowelDisplay[1][2] = kana[3]; // え
  vowelDisplay[2][1] = kana[4]; // お
}

void setup() {
  size(990, 820); 
  int windowX = displayWidth - width;
  int windowY = 120;
  surface.setLocation(windowX, windowY);

  myPort = new Serial(this, "COM3", 115200);
  myPort.bufferUntil('\n');
  
  PFont jpFont = createFont("MS Gothic", 96, true);
  textFont(jpFont);

  inSecondLayer = false;

  try {
    robot = new Robot();
    clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
  } catch (Exception e) {
    e.printStackTrace();
  }

  java.awt.Frame frame = 
    (java.awt.Frame)((processing.awt.PSurfaceAWT.SmoothCanvas)surface.getNative()).getFrame();
  frame.setAlwaysOnTop(true);
  frame.setFocusableWindowState(false);

  textAlign(CENTER, CENTER);
  textSize(96); 
}

void draw() {
  background(255);
  int offsetX = 70;  // 横(左)の余白
  int offsetY = 60;   // 縦(上)の余白

  if (!inSecondLayer) { // 第一レイヤーなら子音群を表示
    for (int r = 0; r < 4; r++) {
      for (int c = 0; c < 3; c++) {
        if (r == row && c == col) {
          fill(0, 100, 255); // 現在のポインターの位置をハイライト
        } else {
          fill(200);
        }
        rect(c * 300 + offsetX, r * 180 + offsetY, 240, 150);
        fill(0);
        text(consonantTable[r][c], c * 300 + offsetX + 120, r * 180 + offsetY + 75);
      }
    }
  } else { // 第二レイヤーなら母音群を表示
    for (int r = 0; r < 3; r++) {
      for (int c = 0; c < 3; c++) {
        if (r == row && c == col) {
          fill(0, 100, 255);
        } else {
          fill(200);
        }
        rect(c * 300 + offsetX, r * 180 + offsetY, 240, 150);
        fill(0);
        text(vowelDisplay[r][c], c * 300 + offsetX + 120, r * 180 + offsetY + 75);
      }
    }
  }
}

// シリアル通信で更新されたら
void serialEvent(Serial myPort) {
  try {
    byte[] inBytes = myPort.readBytesUntil('\n');
    if (inBytes == null) return;

    String input = new String(inBytes, "UTF-8");
    input = trim(input);
    println("受信データ: " + input); // Arduinoからのデータを表示

    if (input.startsWith("ROW:")) { // シリアル通信で受信したデータがROW:から始まる場合
      String[] parts = input.split("[,;]");
      row = int(parts[0].split(":")[1]);
      col = int(parts[1].split(":")[1]);
    } else if (input.startsWith("第一レイヤーで選択した子音:")) { // シリアル通信で受信したデータが第一レイヤーで選択した子音:から始まる場合
      currentConsonant = input.split(":")[1].trim(); // 第一レイヤーで選択した子音を格納
      inSecondLayer = true;
      // 第二レイヤーでは中央から開始
      row = 1;
      col = 1;
      // 子音に応じた母音表示を動的に更新
      updateVowelDisplay(currentConsonant);
    } else if (input.startsWith("VOWEL:") && inSecondLayer) {
      String vowel = input.split(":")[1];
      String result = decodeKana(currentConsonant, vowel); // 子音と母音の組み合わせに基づいて日本語文字を返す
      if (!result.equals("")) {
        typeString(result);
      }
      inSecondLayer = false;
      currentConsonant = "";
    }
  } catch (Exception e) {
    println("serialEventエラー: " + e);
  }
}

String decodeKana(String consonantKana, String vowelCode) {
  // 子音と母音の組み合わせに基づいて日本語文字を返す
  if (consonantKana.equals("a")) {
    if (vowelCode.equals("a")) return "あ";
    if (vowelCode.equals("i")) return "い";
    if (vowelCode.equals("u")) return "う";
    if (vowelCode.equals("e")) return "え";
    if (vowelCode.equals("o")) return "お";
  }
  if (consonantKana.equals("k")) {
    if (vowelCode.equals("a")) return "か";
    if (vowelCode.equals("i")) return "き";
    if (vowelCode.equals("u")) return "く";
    if (vowelCode.equals("e")) return "け";
    if (vowelCode.equals("o")) return "こ";
  }
  if (consonantKana.equals("s")) {
    if (vowelCode.equals("a")) return "さ";
    if (vowelCode.equals("i")) return "し";
    if (vowelCode.equals("u")) return "す";
    if (vowelCode.equals("e")) return "せ";
    if (vowelCode.equals("o")) return "そ";
  }
  if (consonantKana.equals("t")) {
    if (vowelCode.equals("a")) return "た";
    if (vowelCode.equals("i")) return "ち";
    if (vowelCode.equals("u")) return "つ";
    if (vowelCode.equals("e")) return "て";
    if (vowelCode.equals("o")) return "と";
  }
  if (consonantKana.equals("n")) {
    if (vowelCode.equals("a")) return "な";
    if (vowelCode.equals("i")) return "に";
    if (vowelCode.equals("u")) return "ぬ";
    if (vowelCode.equals("e")) return "ね";
    if (vowelCode.equals("o")) return "の";
  }
  if (consonantKana.equals("h")) {
    if (vowelCode.equals("a")) return "は";
    if (vowelCode.equals("i")) return "ひ";
    if (vowelCode.equals("u")) return "ふ";
    if (vowelCode.equals("e")) return "へ";
    if (vowelCode.equals("o")) return "ほ";
  }
  if (consonantKana.equals("m")) {
    if (vowelCode.equals("a")) return "ま";
    if (vowelCode.equals("i")) return "み";
    if (vowelCode.equals("u")) return "む";
    if (vowelCode.equals("e")) return "め";
    if (vowelCode.equals("o")) return "も";
  }
  if (consonantKana.equals("y")) {
    if (vowelCode.equals("a")) return "や";
    if (vowelCode.equals("i")) return "「";
    if (vowelCode.equals("u")) return "ゆ";
    if (vowelCode.equals("e")) return "」";
    if (vowelCode.equals("o")) return "よ";
  }
  if (consonantKana.equals("r")) {
    if (vowelCode.equals("a")) return "ら";
    if (vowelCode.equals("i")) return "り";
    if (vowelCode.equals("u")) return "る";
    if (vowelCode.equals("e")) return "れ";
    if (vowelCode.equals("o")) return "ろ";
  }
  if (consonantKana.equals("w")) {
    if (vowelCode.equals("a")) return "わ";
    if (vowelCode.equals("i")) return "!";
    if (vowelCode.equals("u")) return "ん";
    if (vowelCode.equals("e")) return "ー";
    if (vowelCode.equals("o")) return "を";
  }
  return "";
}

void typeString(String str) {
  for (char c : str.toCharArray()) {
    typeChar(c);
  }
}

void typeChar(char c) {
  try {
    // 文字をクリップボードにコピー
    StringSelection selection = new StringSelection(String.valueOf(c));
    clipboard.setContents(selection, null);
    delay(100);  // クリップボード操作の待ち時間

    // クリップボードから貼り付け（Ctrl+V）
    robot.keyPress(KeyEvent.VK_CONTROL);
    robot.keyPress(KeyEvent.VK_V);
    robot.keyRelease(KeyEvent.VK_V);
    robot.keyRelease(KeyEvent.VK_CONTROL);
    delay(100);  

  } catch (Exception e) {
    println("キー入力エラー: " + e);
  }
}
