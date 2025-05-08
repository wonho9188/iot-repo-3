#include <DHT.h>

#define DHTPIN 2         // DHT 데이터 핀을 디지털 2번에 연결
#define DHTTYPE DHT11    // 센서 타입: DHT11 또는 DHT22

#define BLUE_LED_PIN 4
#define YELLOW_LED_PIN1 5
#define RED_LED_PIN 6
#define YELLOW_LED_PIN2 7

DHT dht(DHTPIN, DHTTYPE);

// 기준 온도 및 습도 (원하는 값으로 조절하세요)
const float MIN_TEMP = 20.0;
const float MAX_TEMP = 25.0;
const float MIN_HUM = 40.0;
const float MAX_HUM = 60.0;

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN1, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN2, OUTPUT);
}

void loop() {
  float temp = dht.readTemperature(); // 섭씨
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("센서에서 값을 읽을 수 없습니다.");
    return;
  }

  Serial.print("온도: ");
  Serial.print(temp);
  Serial.print(" °C, 습도: ");
  Serial.print(hum);
  Serial.print(" %");


  // 조건: 온도 또는 습도가 기준보다 높으면 파란 LED ON
  if (temp > MAX_TEMP) 
  {
    digitalWrite(BLUE_LED_PIN, HIGH);
    digitalWrite(RED_LED_PIN, LOW);
    Serial.print(" | 냉각 장치 ON ");
  } 
  else if (temp < MIN_TEMP)
  {
    digitalWrite(BLUE_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, HIGH);
    Serial.print(" | 온열 장치 ON ");
  }
  else 
  {
    digitalWrite(BLUE_LED_PIN, LOW);
    digitalWrite(RED_LED_PIN, LOW);
    Serial.print(" | 온도 조절 OFF ");
  }

  // 조건: 온도 또는 습도가 기준보다 높으면 파란 LED ON
  if (hum > MAX_HUM) 
  {
    digitalWrite(YELLOW_LED_PIN1, HIGH);
    digitalWrite(YELLOW_LED_PIN2, LOW);
    Serial.print(" | 제습기 ON ");
  } 
  else if (hum < MIN_HUM)
  {
    digitalWrite(YELLOW_LED_PIN1, LOW);
    digitalWrite(YELLOW_LED_PIN2, HIGH);
    Serial.print(" | 가습기 ON ");
  }
  else 
  {
    digitalWrite(YELLOW_LED_PIN1, LOW);
    digitalWrite(YELLOW_LED_PIN2, LOW);
    Serial.print(" | 습도 조절 OFF ");
  }

  Serial.println("");
  delay(2000);  // 2초마다 측정
}
