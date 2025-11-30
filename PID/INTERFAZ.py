import sys
import serial
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- CONFIGURACIÓN SERIAL ---
PORT = 'COM3'     # Cambia según tu puerto
BAUD = 115200

# --- LÍMITES DEL GRÁFICO Y TABLA ---
MAX_POINTS = 200
MAX_ROWS = 30

# --- CONFIG GRÁFICO ---
AUTO_Y_SCALING = True
Y_MIN_INIT = 0
Y_MAX_INIT = 60

class MotorMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Motor - PID (Setpoint, RPM y Error)")
        self.setGeometry(100, 100, 900, 600)

        # Datos iniciales
        self.sp_data = []
        self.pv_data = []
        self.time_data = []

        # Escalado inicial del eje Y
        self.y_min = Y_MIN_INIT
        self.y_max = Y_MAX_INIT

        # Configurar interfaz
        self.initUI()

        # Iniciar lectura serial
        self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.serial_thread.start()

        # Temporizador de refresco
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)

    def initUI(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.label_status = QLabel("Conectando al puerto serial...")
        layout.addWidget(self.label_status)

        # --- FIGURA DE MATPLOTLIB ---
        self.fig = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Setpoint vs RPM del Motor")
        self.ax.set_ylabel("Velocidad (RPM)")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.grid(True)

        # --- TABLA DE DATOS ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Setpoint (RPM)", "RPM medida", "Error"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def read_serial(self):
        try:
            self.ser = serial.Serial(PORT, BAUD, timeout=1)
            self.label_status.setText(f"✅ Conectado a {PORT}")
            start_time = time.time()

            while True:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        try:
                            sp = float(parts[0])
                            pv = float(parts[1])
                            error = sp - pv
                            t = time.time() - start_time

                            self.sp_data.append(sp)
                            self.pv_data.append(pv)
                            self.time_data.append(t)

                            if len(self.time_data) > MAX_POINTS:
                                self.sp_data.pop(0)
                                self.pv_data.pop(0)
                                self.time_data.pop(0)

                            self.update_table(sp, pv, error)
                        except ValueError:
                            pass
        except serial.SerialException:
            self.label_status.setText("❌ Error: no se pudo abrir el puerto serial.")

    def update_table(self, sp, pv, error):
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(f"{sp:.2f}"))
        self.table.setItem(0, 1, QTableWidgetItem(f"{pv:.2f}"))
        self.table.setItem(0, 2, QTableWidgetItem(f"{error:.2f}"))

        if self.table.rowCount() > MAX_ROWS:
            self.table.removeRow(self.table.rowCount() - 1)

        for col in range(3):
            self.table.item(0, col).setTextAlignment(Qt.AlignCenter)

    def update_display(self):
        if len(self.time_data) > 1:
            self.ax.clear()
            self.ax.plot(self.time_data, self.sp_data, label="Setpoint", color='blue', linewidth=1.5)
            self.ax.plot(self.time_data, self.pv_data, label="RPM medida", color='red', linewidth=1)

            self.ax.legend()
            self.ax.set_ylabel("Velocidad (RPM)")
            self.ax.set_xlabel("Tiempo (s)")
            self.ax.set_title("Setpoint vs RPM del Motor")
            self.ax.grid(True)

            # --- ESCALADO INTELIGENTE DEL EJE Y ---
            if AUTO_Y_SCALING:
                ymin = min(self.pv_data + self.sp_data)
                ymax = max(self.pv_data + self.sp_data)
                margin = (ymax - ymin) * 0.2 if ymax != ymin else 1
                target_min = ymin - margin
                target_max = ymax + margin

                # Si el rango aumenta → ajusta rápido
                if target_max > self.y_max:
                    self.y_max = 0.8 * self.y_max + 0.2 * target_max
                if target_min < self.y_min:
                    self.y_min = 0.8 * self.y_min + 0.2 * target_min

                # Si el rango disminuye → ajusta lento (histéresis)
                if target_max < self.y_max:
                    self.y_max = 0.95 * self.y_max + 0.05 * target_max
                if target_min > self.y_min:
                    self.y_min = 0.95 * self.y_min + 0.05 * target_min

                # Evita que se haga demasiado pequeño el rango
                if (self.y_max - self.y_min) < 10:
                    mid = (self.y_max + self.y_min) / 2
                    self.y_min = mid - 5
                    self.y_max = mid + 5

                self.ax.set_ylim(self.y_min, self.y_max)
            else:
                self.ax.set_ylim(Y_MIN_INIT, Y_MAX_INIT)

            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MotorMonitor()
    window.show()
    sys.exit(app.exec_())
