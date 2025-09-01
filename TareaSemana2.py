nombre = input("Cual es tu nombre? ")
equipo = input("Cual es el nombre de tu equipo? ")
muestra1 = float(input("Numero de muestra 1: "))
muestra2 = float(input("Numero de muestra 2: "))
series = input("Numero de series: ")
UMBRAL_ALTO = "ALTO (>= 5.00 V)"
UMBRAL_MEDIO = "MEDIO (< 5.00  V)"
UMBRAL_BAJO = "BAJO (<= 2.50 V)"  
PROMEDIO = (muestra1 + muestra2)/2
try:
    m1 = float(muestra1)
    m2 = float(muestra2)
    s = int(series)
    if PROMEDIO >= 5.00:
        print("=== REPORTE DE SENSOR ===")
        print(f"Alumno: {nombre} | Equipo: {equipo}")
        print(f"Lecturas (V): {muestra1}, {muestra2} | Promedio: {PROMEDIO:.2f} V")
        print(f"Estado: {UMBRAL_ALTO}")
    elif 2.50 < PROMEDIO < 5.00:
                print("=== REPORTE DE SENSOR ===")
                print(f"Alumno: {nombre} | Equipo: {equipo}")
                print(f"Lecturas (V): {muestra1}, {muestra2} | Promedio: {PROMEDIO:.2f} V")
                print(f"Estado: {UMBRAL_MEDIO}")
    else:
        print("=== REPORTE DE SENSOR ===")
        print(f"Alumno: {nombre} | Equipo: {equipo}")
        print(f"Lecturas (V): {muestra1}, {muestra2} | Promedio: {PROMEDIO:.2f} V")
        print(f"Estado: {UMBRAL_BAJO}")
    
    if PROMEDIO >= 5.00:
        print(f"Muestra 2: {m2:.2f} V - {UMBRAL_ALTO}")
    elif 2.50 < m2 < 5.00:
        print(f"Muestra 2: {m2:.2f} V - {UMBRAL_MEDIO}")
    else:
        print(f"Muestra 2: {m2:.2f} V - {UMBRAL_BAJO}")

except ValueError:
    print("Error: Por favor ingrese valores numéricos válidos para las muestras y un entero para las series.")