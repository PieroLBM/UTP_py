import matplotlib.pyplot as plt
import csv
import math
import statistics

class DataAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self.timestamps = []
        self.distances = []
        self.states = []
        
    def load_data(self):
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.timestamps.append(int(row['ts_ms']))
                self.distances.append(float(row['distance']))
                self.states.append(row['state'])
    
    def calculate_kpis(self):
        # KPIs básicos
        n = len(self.distances)
        min_dist = min(self.distances)
        max_dist = max(self.distances)
        mean_dist = statistics.mean(self.distances)
        
        # % en ALERTA
        alert_count = self.states.count('ALERT')
        percent_alert = (alert_count / n) * 100
        
        # Duración de eventos
        event_durations = []
        in_event = False
        event_start = 0
        
        for i, state in enumerate(self.states):
            if state == 'ALERT' and not in_event:
                in_event = True
                event_start = self.timestamps[i]
            elif state == 'NORMAL' and in_event:
                in_event = False
                duration = self.timestamps[i] - event_start
                event_durations.append(duration)
        
        avg_event_duration = statistics.mean(event_durations) if event_durations else 0
        
        # RMS y THD (simulados para distancia)
        rms = math.sqrt(sum(d**2 for d in self.distances) / n)
        
        # Calcular THD aproximado
        fundamental = statistics.mean(self.distances)
        harmonic_distortion = math.sqrt(sum((d - fundamental)**2 for d in self.distances) / n)
        thd = (harmonic_distortion / fundamental) * 100 if fundamental != 0 else 0
        
        print("=== KPIs DEL SISTEMA ===")
        print(f"Total de muestras (n): {n}")
        print(f"Distancia mínima: {min_dist:.2f} cm")
        print(f"Distancia máxima: {max_dist:.2f} cm")
        print(f"Distancia media: {mean_dist:.2f} cm")
        print(f"% en ALERTA: {percent_alert:.2f}%")
        print(f"Número de eventos: {len(event_durations)}")
        print(f"Duración media de eventos: {avg_event_duration:.2f} ms")
        print(f"Valor RMS: {rms:.2f}")
        print(f"THD aproximado: {thd:.2f}%")
        
        return {
            'n': n,
            'min': min_dist,
            'max': max_dist,
            'mean': mean_dist,
            'percent_alert': percent_alert,
            'event_count': len(event_durations),
            'avg_duration': avg_event_duration,
            'rms': rms,
            'thd': thd
        }
    
    def plot_temporal_line(self):
        plt.figure(figsize=(12, 6))
        
        # Convertir timestamps a tiempo relativo en segundos
        start_time = self.timestamps[0]
        relative_times = [(ts - start_time) / 1000 for ts in self.timestamps]
        
        plt.plot(relative_times, self.distances, 'b-', alpha=0.7, label='Distancia')
        
        # Resaltar zonas de alerta
        alert_x = [relative_times[i] for i, state in enumerate(self.states) if state == 'ALERT']
        alert_y = [self.distances[i] for i, state in enumerate(self.states) if state == 'ALERT']
        plt.scatter(alert_x, alert_y, color='red', s=20, label='Alerta', alpha=0.6)
        
        plt.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='Umbral (30cm)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Distancia (cm)')
        plt.title('Evolución Temporal - Distancia vs Tiempo')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_histogram(self):
        plt.figure(figsize=(10, 6))
        
        plt.hist(self.distances, bins=20, alpha=0.7, edgecolor='black')
        plt.axvline(x=30, color='r', linestyle='--', label='Umbral de alerta')
        plt.xlabel('Distancia (cm)')
        plt.ylabel('Frecuencia')
        plt.title('Histograma de Distancias')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_boxplot(self):
        plt.figure(figsize=(8, 6))
        
        # Separar datos por escenario
        normal_distances = [self.distances[i] for i, state in enumerate(self.states) if state == 'NORMAL']
        alert_distances = [self.distances[i] for i, state in enumerate(self.states) if state == 'ALERT']
        
        data = [normal_distances, alert_distances]
        labels = ['Escenario Normal', 'Escenario Alerta']
        
        plt.boxplot(data, labels=labels)
        plt.ylabel('Distancia (cm)')
        plt.title('Boxplot - Comparación de Escenarios')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def generate_all_plots(self):
        self.load_data()
        kpis = self.calculate_kpis()
        
        print("\nGenerando gráficos...")
        self.plot_temporal_line()
        self.plot_histogram()
        self.plot_boxplot()
        
        return kpis

# Ejecutar análisis
if __name__ == "__main__":
    analyzer = DataAnalyzer('sensor_data.csv')
    analyzer.generate_all_plots()