#include <Arduino.h>
// 핀 정의
#define A_1A 5
#define A_1B 6

// 모터 상태 변수
int motorSpeed = 0;

void setup() {
  pinMode(A_1A, OUTPUT);
  pinMode(A_1B, OUTPUT);
  Serial.begin(9600);
  Serial.println("L9110 단방향 모터 제어");
  Serial.println("명령어: 0-255 사이의 숫자 입력 (속도)");
  Serial.println("0 입력 시 모터 정지");
  
  // 초기 상태: 모터 정지
  digitalWrite(A_1A, LOW);
  digitalWrite(A_1B, LOW);
}

void loop() {
  // 시리얼 입력 확인
  if (Serial.available() > 0) {
    // 숫자 값만 읽기
    int newSpeed = Serial.parseInt();
    
    // 범위 제한 (0-255)
    newSpeed = constrain(newSpeed, 0, 255);
    
    // 새 속도 값 설정
    motorSpeed = newSpeed;
    
    // 상태 출력
    if (motorSpeed == 0) {
      Serial.println("모터 정지");
      // 모터 정지
      digitalWrite(A_1A, LOW);
      digitalWrite(A_1B, LOW);
    } else {
      Serial.print("모터 속도: ");
      Serial.println(motorSpeed);
      
      // 단방향 모터 제어 (정방향만)
      analogWrite(A_1A, motorSpeed);
      digitalWrite(A_1B, LOW);
    }
    
    // 입력 버퍼 비우기
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}