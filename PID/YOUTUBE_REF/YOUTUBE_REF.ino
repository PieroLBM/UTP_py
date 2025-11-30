int PWM_salida = 6;   // salida PWM al driver del motor
float pv;             // variable de proceso (velocidad medida)
float sp = 19.41;     // setpoint fijo en rpm

int pinA = 3;         // entrada del encoder (canal A)
volatile int contador = 0;
unsigned long previousMillis = 0;
long interval = 50;   // tiempo de muestreo (ms)

// Variables PID
float cv;     // salida de control
float cv1;
float error;
float error1;
float error2;

// Constantes PID (ajustables)
float Kp = 0.2;
float Ki = 0.3;
float Kd = 0.0005;
float Tm = 0.1; // periodo de muestreo en segundos

// Filtro paso bajo (variable de estado)
float pv_filtrado = 0.0;
float alpha = 0.9;   // factor de suavizado (0.9 = muy suave, 0.5 = más rápido)

void setup() {
  pinMode(pinA, INPUT);
  pinMode(PWM_salida, OUTPUT);
  Serial.begin(115200);

  // interrupción en pin 3 (INT1)
  attachInterrupt(1, interrupcion, RISING);
}

void loop() {
  unsigned long currentMillis = millis();

  if ((currentMillis - previousMillis) >= interval) {
    previousMillis = currentMillis;

    // Calcular velocidad instantánea (PV sin filtrar)
    float pv_raw = 10 * contador * (60.0 / 649.0); // rpm del eje principal
    contador = 0;

    // --- Filtro paso bajo para reducir ruido ---
    // pv_filtrado = alpha * pv_filtrado_anterior + (1 - alpha) * pv_nueva
    pv_filtrado = alpha * pv_filtrado + (1.0 - alpha) * pv_raw;
    pv = pv_filtrado;
    // -------------------------------------------

    // Calcular error
    error = sp - pv;

    // Ecuación en diferencias del PID
    cv = cv1 + (Kp + Kd / Tm) * error 
            + (-Kp + Ki * Tm - 2 * Kd / Tm) * error1 
            + (Kd / Tm) * error2;

    // Actualizar variables del PID
    cv1 = cv;
    error2 = error1;
    error1 = error;

    // Saturar salida PID (0–100%)
    if (cv > 100.0) cv = 100.0;
    if (cv < 0.0) cv = 0.0;

    // Aplicar señal PWM al motor
    analogWrite(PWM_salida, cv * (255.0 / 100.0));

    // Enviar datos al Serial Plotter (SP, PV filtrado)
    Serial.print(sp);
    Serial.print(",");
    Serial.println(pv);
  }
}

// Interrupción del encoder (canal A)
void interrupcion() {
  contador++;
}
