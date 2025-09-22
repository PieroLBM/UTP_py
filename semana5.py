import matplotlib.pyplot as plt
import numpy as np

# Generar datos para la función seno
x = np.linspace(0, 4*np.pi, 1000)  # Valores de x de 0 a 4π
y_seno = np.sin(x)                  # Función seno
y_seno_inversa = -np.sin(x)         # Función seno inversa

# Crear la gráfica
plt.figure(figsize=(10, 6))  # Tamaño de la figura

# Graficar ambas funciones
plt.plot(x, y_seno, 'b-', linewidth=2, label='Sen(x)')
plt.plot(x, y_seno_inversa, 'r--', linewidth=2, label='-Sen(x)')

# Configurar título y etiquetas
plt.title("Funciones Seno y su Inversa", fontsize=14, fontweight='bold')
plt.xlabel("Ángulo (radianes)", fontsize=12)
plt.ylabel("Valor de la función", fontsize=12)

# Agregar leyenda
plt.legend(loc='upper right')

# Agregar grid para mejor lectura
plt.grid(True, alpha=0.3)

# Configurar límites de los ejes
plt.xlim(0, 4*np.pi)
plt.ylim(-1.5, 1.5)

# Agregar líneas de referencia
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

# Mejorar el aspecto general
plt.tight_layout()

# Guardar la gráfica en un archivo
plt.savefig('funciones_seno.png', dpi=300, bbox_inches='tight')

# Mostrar la gráfica
plt.show()

# También podemos guardar los datos en un archivo de texto
datos = np.column_stack((x, y_seno, y_seno_inversa))
np.savetxt('datos_seno.txt', datos, 
           header='x\tSen(x)\t-Sen(x)', 
           delimiter='\t', 
           fmt='%.4f')

print("Gráfica guardada como 'funciones_seno.png'")
print("Datos guardados como 'datos_seno.txt'")