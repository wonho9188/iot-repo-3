#include <DHT.h>

#define DHTPIN 2         // DHT 데이터 핀을 디지털 2번에 연결
#define DHTTYPE DHT11    // 센서 타입: DHT11 또는 DHT22

#define BLUE_LED_PIN 4
#define YELLOW_LED_PIN1 5
#define RED_LED_PIN 6
#define YELLOW_LED_PIN2 7

#define TEMP_BUZZER_PIN 8
#define HUM_BUZZER_PIN 9

DHT dht(DHTPIN, DHTTYPE);

const int NOTE_C = 261;  // 도
const int NOTE_E = 329;  // 미
const int NOTE_G = 392;  // 솔

// 기준 온도 및 습도 (원하는 값으로 조절하세요)
const float MIN_TEMP = 20.0;
const float MAX_TEMP = 25.0;
const float MIN_HUM = 40.0;
const float MAX_HUM = 60.0;

bool tempAlarmActive = false;
bool humAlarmActive = false;
unsigned long buzzerStartTime = 0;
int buzzerStep = 0;
const int buzzerDelay = 300;

// 비동기 처리용 변수
unsigned long lastSensorCheck = 0;
const unsigned long sensorInterval = 2000;

unsigned long lastTempMelodyTime = 0;
unsigned long tempMelodyStartTime = 0;
int tempMelodyStep = 0;
bool isTempMelodyPlaying = false;

unsigned long lastHumMelodyTime = 0;
unsigned long humMelodyStartTime = 0;
int humMelodyStep = 0;
bool isHumMelodyPlaying = false;

const unsigned long melodyInterval = 10000;  // 5초마다 반복
const unsigned long melodyDuration = 1000;  // 1초간 재생

// 알람 상태 구분
enum AlarmType { NONE, COOLING, HEATING, DEHUMID, HUMIDIFY };
AlarmType tempAlarmType = NONE;
AlarmType humAlarmType = NONE;

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN1, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN2, OUTPUT);

  pinMode(TEMP_BUZZER_PIN, OUTPUT);
  pinMode(HUM_BUZZER_PIN, OUTPUT);
}


void loop() {
  unsigned long currentTime = millis();

  // 센서 측정 주기
  if (currentTime - lastSensorCheck >= sensorInterval) {
    lastSensorCheck = currentTime;

    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (isnan(temp) || isnan(hum)) {
      Serial.println("센서 에러!");
      return;
    }

    Serial.print("온도: ");
    Serial.print(temp);
    Serial.print(" °C, 습도: ");
    Serial.print(hum);
    Serial.print(" %");

    // 온도 제어
    if (temp > MAX_TEMP) {
      digitalWrite(BLUE_LED_PIN, HIGH);
      digitalWrite(RED_LED_PIN, LOW);
      tempAlarmActive = true;
      tempAlarmType = COOLING;
      buzzerStartTime = currentTime;
      buzzerStep = 0;
      Serial.print(" | 냉각 ON ");
      Serial.print(" | [경고] 온도가 너무 높습니다. ");
    } else if (temp < MIN_TEMP) {
      digitalWrite(BLUE_LED_PIN, LOW);
      digitalWrite(RED_LED_PIN, HIGH);
      tempAlarmActive = true;
      tempAlarmType = HEATING;
      buzzerStartTime = currentTime;
      buzzerStep = 0;
      Serial.print(" | 온열 ON ");
      Serial.print(" | [경고] 온도가 너무 낮습니다. ");
    } else {
      digitalWrite(BLUE_LED_PIN, LOW);
      digitalWrite(RED_LED_PIN, LOW);
      tempAlarmActive = false;
      tempAlarmType = NONE;
      noTone(TEMP_BUZZER_PIN);
      Serial.print(" | 온도 OFF ");
    }

    // 습도 제어
    if (hum > MAX_HUM) {
      digitalWrite(YELLOW_LED_PIN1, HIGH);
      digitalWrite(YELLOW_LED_PIN2, LOW);
      humAlarmActive = true;
      humAlarmType = DEHUMID;
      buzzerStartTime = currentTime;
      buzzerStep = 0;
      Serial.print(" | 제습기 ON ");
      Serial.print(" | [경고] 습도가 너무 높습니다. ");
    } else if (hum < MIN_HUM) {
      digitalWrite(YELLOW_LED_PIN1, LOW);
      digitalWrite(YELLOW_LED_PIN2, HIGH);
      humAlarmActive = true;
      humAlarmType = HUMIDIFY;
      buzzerStartTime = currentTime;
      buzzerStep = 0;
      Serial.print(" | 가습기 ON ");
      Serial.print(" | [경고] 습도가 너무 낮습니다. ");
    } else {
      digitalWrite(YELLOW_LED_PIN1, LOW);
      digitalWrite(YELLOW_LED_PIN2, LOW);
      humAlarmActive = false;
      humAlarmType = NONE;
      noTone(HUM_BUZZER_PIN);
      Serial.print(" | 습도 OFF ");
    }

    Serial.println();
  }

  unsigned long now = millis();

  // 온도 멜로디 제어
  if (tempAlarmType != NONE) {
    if (!isTempMelodyPlaying && now - lastTempMelodyTime >= melodyInterval) {
      tempMelodyStartTime = now;
      isTempMelodyPlaying = true;
      tempMelodyStep = 0;
      lastTempMelodyTime = now;
    }

    if (isTempMelodyPlaying) {
      if (now - tempMelodyStartTime < melodyDuration) {
        switch (tempAlarmType) {
          case COOLING: playTone(TEMP_BUZZER_PIN, tempMelodyStep, NOTE_G, NOTE_E, NOTE_C); break;
          case HEATING: playTone(TEMP_BUZZER_PIN, tempMelodyStep, NOTE_C, NOTE_E, NOTE_G); break;
        }
        if (now - tempMelodyStartTime > 300 * (tempMelodyStep + 1)) tempMelodyStep++;
      } else {
        noTone(TEMP_BUZZER_PIN);
        isTempMelodyPlaying = false;
      }
    }
  } else {
    noTone(TEMP_BUZZER_PIN);
    isTempMelodyPlaying = false;
  }

  // 온도 멜로디 제어
  if (humAlarmType != NONE) {
    if (!isHumMelodyPlaying && now - lastHumMelodyTime >= melodyInterval) {
      humMelodyStartTime = now;
      isHumMelodyPlaying = true;
      humMelodyStep = 0;
      lastHumMelodyTime = now;
    }

    if (isHumMelodyPlaying) {
      if (now - humMelodyStartTime < melodyDuration) {
        switch (humAlarmType) {
          case DEHUMID: 
            playTone(HUM_BUZZER_PIN, humMelodyStep, NOTE_G, NOTE_E, NOTE_C); 
            break;
          case HUMIDIFY: 
            playTone(HUM_BUZZER_PIN, humMelodyStep, NOTE_C, NOTE_E, NOTE_G); 
            break;
        }
        if (now - humMelodyStartTime > 300 * (humMelodyStep + 1)) humMelodyStep++;
      } else {
        noTone(HUM_BUZZER_PIN);
        isHumMelodyPlaying = false;
      }
    }
  } else {
    noTone(HUM_BUZZER_PIN);
    isHumMelodyPlaying = false;
  }
}

// 부저 멜로디 함수
void playTone(int pin, int step, int note1, int note2, int note3) {
  switch (step) {
    case 0: tone(pin, note1); break;
    case 1: tone(pin, note2); break;
    case 2: tone(pin, note3); break;
    default: noTone(pin); break;
  }
}
