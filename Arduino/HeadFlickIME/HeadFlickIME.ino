#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif


// 加速度センサー
MPU6050 mpu;
bool dmpReady = false;
uint8_t devStatus;
uint16_t packetSize;
uint8_t fifoBuffer[64];
Quaternion q;
VectorFloat gravity;
float ypr[3]; // yaw, pitch, roll

// 移動平均用変数
const int windowSize = 3;
float yawBuffer[windowSize] = {0};
float rollBuffer[windowSize] = {0};
int bufferIndex = 0;

// 移動平均フィルタ関数
float movingAverage(float buffer[], float newValue) {
    buffer[bufferIndex] = newValue;
    float sum = 0;
    for (int i = 0; i < windowSize; i++) {
        sum += buffer[i];
    }
    return sum / windowSize;
}


// フォトリフレクタ関連
const uint8_t sensorPin = A0; // まばたき検知用フォトリフレクタのピン
int lidInitialVal; 
const double BLINK_THRESHOLD = 0.985; // 瞼閉じの閾値
bool lid = false;
bool inSecondLayer = false;
unsigned int blinkStartTime = 0;
const unsigned int BLINK_HOLD_TIME = 250; // 瞼閉じの保持時間

// ポインター位置
uint8_t row = 1;
uint8_t col = 1;

// 子音テーブル
char consonantTable[4][3] = {
    {'a', 'k', 's'},
    {'t', 'n', 'h'},
    {'m', 'y', 'r'},
    {' ', 'w', ' '}
};

// 方向判定用の閾値
const float ROLL_THRESHOLD_TOP = 10.0;    // 上方向の閾値
const float ROLL_THRESHOLD_BOTTOM = -9.0; // 下方向の閾値
const float ROLL_THRESHOLD_BOTTOMOST = -16.0; // 最下段の閾値
const float YAW_THRESHOLD_LEFT = -20.0;   // 左方向の閾値
const float YAW_THRESHOLD_RIGHT = 19.0;   // 右方向の閾値



// 渡された角度に基づくポインタ位置の更新する関数
void updatePointerPosition(float roll, float yaw) {
    // 行（上下）の判定
    if (roll > ROLL_THRESHOLD_TOP) {
        row = 0;  // 上段
    } else if (roll < ROLL_THRESHOLD_BOTTOM) {
        if (roll < ROLL_THRESHOLD_BOTTOMOST) {
            row = 3;  // 最下段
        } else {
            row = 2;  // 下段
        }
    } else {
        row = 1;  // 中段
    }

    // 列（左右）の判定
    if (row == 3) {
        col = 1;  // 最下段は中央列のみ
    } else {
        // その他の行では通常の左右判定
        if (yaw < YAW_THRESHOLD_LEFT) {
            col = 0;  // 左列
        } else if (yaw > YAW_THRESHOLD_RIGHT) {
            col = 2;  // 右列
        } else {
            col = 1;  // 中央列
        }
    }

    // Processing側にポインター位置を送信
    Serial.print(F("ROW:"));
    Serial.print(row);
    Serial.print(F(",COL:"));
    Serial.println(col);
}

void setup() {
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(400000);
    #endif

    inSecondLayer = false;

    Serial.begin(115200);
    while (!Serial);

    mpu.initialize();
    Serial.println(mpu.testConnection() ? F("MPU6050接続成功") : F("MPU6050接続失敗"));

    devStatus = mpu.dmpInitialize(); // 加速度センサーの初期化
    mpu.setXGyroOffset(63); // ジャイロオフセットの設定
    mpu.setYGyroOffset(2);
    mpu.setZGyroOffset(-22);
    mpu.setXAccelOffset(-289);
    mpu.setYAccelOffset(1497);
    mpu.setZAccelOffset(1145);
    
    if (devStatus == 0) {
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.setDMPEnabled(true);
        dmpReady = true;
        packetSize = mpu.dmpGetFIFOPacketSize();
    }

    Serial.println(F("基準点を設定します．正面を見てください"));
    delay(1000);
    Serial.println(F("3"));
    delay(1000);
    Serial.println(F("2"));
    delay(1000);
    Serial.println(F("1"));
    delay(1000);

    lidInitialVal = analogRead(sensorPin); // 瞼が開いている時のフォトリフレクタの基準値を取得
}

void loop() {
    if (dmpReady && mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        
        // 角度を度に変換
        float yawRaw = ypr[0] * 180 / M_PI;
        float rollRaw = ypr[2] * 180 / M_PI;

        float yaw = movingAverage(yawBuffer, yawRaw);
        float roll = movingAverage(rollBuffer, rollRaw);
        bufferIndex = (bufferIndex + 1) % windowSize;

        

        // フォトリフレクタでのまばたき検出
        int sensorValue = analogRead(sensorPin);   
        double rate = (double)sensorValue / lidInitialVal;
        if (inSecondLayer == false) { // 前回セカンドレイヤでない
            // 方向に基づくポインター位置の更新
            updatePointerPosition(roll, yaw);
            if (lid == false && rate <= BLINK_THRESHOLD) { // 前回閉じでない∧現在閉じているか
                blinkStartTime = millis();
                lid = true;
            } else if (lid == true && rate <= BLINK_THRESHOLD) {  // 前回瞼を閉じていて∧現在閉じているか
                if (millis() - blinkStartTime > BLINK_HOLD_TIME) { // 前回の閉じから閾値以上経過していたら
                    inSecondLayer = true;
                    Serial.print(F("第一レイヤーで選択した子音: "));
                    Serial.println(consonantTable[row][col]); // この時点でProcesingに子音が決定したことを送信
                    Serial.println(F("==== 第二レイヤーへ遷移 ===="));
                }
            } else if (lid == true && rate > BLINK_THRESHOLD) { // 正面注視中
                lid = false;
            }
        }

        // 第二レイヤーで母音入力
        if (inSecondLayer) {
            char vowel = '\0';
            if (roll > ROLL_THRESHOLD_TOP) {
                vowel = 'u';
                row = 0; col = 1;  // 上
            }
            else if (roll < ROLL_THRESHOLD_BOTTOM) {
                vowel = 'o';
                row = 2; col = 1;  // 下
            }
            else if (yaw > YAW_THRESHOLD_RIGHT) {
                vowel = 'e';
                row = 1; col = 2;  // 右
            }
            else if (yaw < YAW_THRESHOLD_LEFT) {
                vowel = 'i';
                row = 1; col = 0;  // 左
            }
            else {
                vowel = 'a';  // 正面で 'a'
                row = 1; col = 1;  // 中央
            }

            // ポインター位置の更新を送信
            Serial.print(F("ROW:"));
            Serial.print(row);
            Serial.print(F(",COL:"));
            Serial.println(col);

            // 目が開いたことを検出
            if (rate > BLINK_THRESHOLD && lid) {
                lid = false;
                if (vowel != '\0') {
                    Serial.print(F("VOWEL:"));
                    Serial.println(vowel);
                    inSecondLayer = false;
                    delay(200);  // 誤検出防止の待ち時間
                }
            }
        }
    }
    delay(100);
}
