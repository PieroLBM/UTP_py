import numpy as np
import matplotlib.pyplot as plt

# Datos corregidos
d = [i for i in range(200)]  # Lista de tiempo (eje x)
A = [12, 20]  # Amplitudes
f = [0.23, 0.35]  # Frecuencias
theta_i = [0.26, 1.45]  # Fases iniciales 

# Generar las señales sinusoidales
x1 = A[0] * np.sin(2 * np.pi * f[0] * np.array(d) * 0.1 + theta_i[0])  # Usar 'd' en lugar de 'dt'
x2 = A[1] * np.sin(2 * np.pi * f[1] * np.array(d) * 0.1 + theta_i[1])  # Usar 'd' en lugar de 'dt'

# Señal acoplada (suma de las dos señales)
xaco = np.array(x1) + np.array(x2)

# Crear figura con 4 subplots (3 señales + la suma)
plt.figure(figsize=(12, 10))

# Primer gráfico: Señal 1
plt.subplot(4, 1, 1)
plt.plot(d, x1, 'b-', linewidth=2, label='Señal 1')
plt.ylabel('Amplitud')
plt.title('Señal 1: A=12, f=0.23, θ=0.26')
plt.grid(True, alpha=0.3)
plt.legend()

# Segundo gráfico: Señal 2
plt.subplot(4, 1, 2)
plt.plot(d, x2, 'r-', linewidth=2, label='Señal 2')
plt.ylabel('Amplitud')
plt.title('Señal 2: A=20, f=0.35, θ=1.45')
plt.grid(True, alpha=0.3)
plt.legend()

# Tercer gráfico: Señal acoplada (suma)
plt.subplot(4, 1, 3)
plt.plot(d, xaco, 'g-', linewidth=2, label='Señal Acoplada')
plt.ylabel('Amplitud')
plt.title('Señal Acoplada (Suma de Señal 1 + Señal 2)')
plt.grid(True, alpha=0.3)
plt.legend()

# Cuarto gráfico: Las tres señales superpuestas
plt.subplot(4, 1, 4)
plt.plot(d, x1, 'b-', alpha=0.7, label='Señal 1')
plt.plot(d, x2, 'r-', alpha=0.7, label='Señal 2')
plt.plot(d, xaco, 'g-', linewidth=2, label='Señal Acoplada')
plt.xlabel('Tiempo')
plt.ylabel('Amplitud')
plt.title('Todas las señales superpuestas')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()

# También mostrar las señales por separado
print("\n--- Gráficos individuales ---")
plt.figure(figsize=(12, 4))
plt.plot(d, x1, 'b-', label='Señal 1')
plt.plot(d, x2, 'r-', label='Señal 2')
plt.plot(d, xaco, 'g-', label='Señal Acoplada', color = "#ffe100d2")
plt.xlabel('Tiempo')
plt.ylabel('Amplitud')
plt.title('Todas las señales en un mismo gráfico')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()