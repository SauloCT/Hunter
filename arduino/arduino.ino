#include <ArduinoJson.h>
#include <Mouse.h>
#include <Keyboard.h>  // para emular eventos de teclado

// Variáveis para rastrear posição do mouse
int currentX = 0;
int currentY = 0;
const int newW = 1920, newH = 1080;
const int oldW = 1366, oldH = 768;

// Interpolação linear para smoothMove
float lerpF(float a, float b, float t) {
  return a + t * (b - a);
}

// Move o mouse suavemente em pequenos passos
void smoothMove(int steps, int delayMs, int targetX, int targetY) {
  int x_new = (targetX * newW) / oldW;
  int y_new = (targetY * newH) / oldH;
  for (int i = 1; i <= steps; i++) {
    float t = i / float(steps);
    int x = lerpF(currentX, x_new, t);
    int y = lerpF(currentY, y_new, t);
    Mouse.move(x - currentX, y - currentY);
    currentX = x;
    currentY = y;
    delay(delayMs);
  }
}

// Processa JSON recebido e executa ação correspondente
void receiveJson(DynamicJsonDocument &doc) {
  int a = doc["a"];
  int x = doc.containsKey("x") ? doc["x"] : 0;
  int y = doc.containsKey("y") ? doc["y"] : 0;

  switch (a) {
    case 0:
      Serial.println("CASE 0: smoothMove");
      smoothMove(50, 10, x, y);
      break;
    case 1:
      Serial.println("CASE 1: click left");
      smoothMove(50, 10, x, y);
      Mouse.click(MOUSE_LEFT);
      break;
    case 2:
      Serial.println("CASE 2: click right");
      smoothMove(50, 10, x, y);
      Mouse.click(MOUSE_RIGHT);
      break;
    case 3:
      Serial.println("CASE 3: drag");
      Mouse.press(MOUSE_LEFT);
      smoothMove(50, 10, x, y);
      Mouse.release(MOUSE_LEFT);
      break;
    case 4:
      Serial.println("CASE 4: click middle");
      Mouse.click(MOUSE_MIDDLE);
      break;
    case 5:
      Serial.println("CASE 5: update pos");
      currentX = x;
      currentY = y;
      break;
    case 6: {
      // Emula pressionamento de tecla única
      const char* keyStr = doc["k"];
      if (keyStr && strlen(keyStr) > 0) {
        char key = keyStr[0];
        Serial.print("CASE 6: key ");
        Serial.println(key);
        Keyboard.press(key);
        delay(10);
        Keyboard.release(key);
      }
      break;
    }
    case 99:
      // Handshake: responde ao Python
      Serial.println("{\"ack\":\"arduino\"}");
      break;
    default:
      Serial.print("CASE ?? a=");
      Serial.println(a);
      break;
  }
}

void setup() {
  // Inicializa Serial USB para comandos JSON
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Ready");  // Indica que o Arduino está pronto

  // Inicializa HID mouse e teclado
  Mouse.begin();
  Keyboard.begin();
}

void loop() {
  if (Serial.available()) {
    // Lê até newline (caractere '\n')
    String s = Serial.readStringUntil('\n');
    Serial.print("RX: ");
    Serial.println(s);
    DynamicJsonDocument doc(256);
    if (deserializeJson(doc, s) == DeserializationError::Ok) {
      receiveJson(doc);
    } else {
      Serial.println("! JSON Error");
    }
  }
}
