import csv
from datetime import datetime
from pathlib import Path
from statistics import mean

# Configuración de rutas
ROOT = Path(__file__).resolve().parents[1]
IN_FILE = ROOT/"datos"/"raw"/"datos_sucios_250_v2.csv"
OUT_FILE = ROOT/"datos"/"proccesing"/"Temperaturas_Procesado.csv"

print("=== PROCESAMIENTO DE DATOS DE TEMPERATURA ===")
print("Iniciando procesamiento de datos...")

with open(IN_FILE, 'r', encoding="utf-8", newline="") as fin, \
     open(OUT_FILE, "w", encoding="utf-8", newline="") as fout:
    
    reader = csv.DictReader(fin, delimiter=';')
    writer = csv.DictWriter(fout, fieldnames=["Timestamp", "voltaje", "Temp_C", "Alertas"])
    writer.writeheader()
    
    # Variables para estadísticas
    total = kept = 0
    bad_ts = bad_val = 0
    voltajes = []
    temperaturas = []
    alertas_count = 0
    
    print("Procesando filas...")
    
    for row in reader:
        total += 1
        ts_raw = (row.get("timestamp") or "").strip()
        val_raw = (row.get("value") or "").strip()
        
        # Limpiar y convertir valor numérico
        val_raw = val_raw.replace(",", ".")
        val_low = val_raw.lower()
        
        # Verificar valores inválidos
        if val_low in {"", "na", "n/a", "nan", "null", "none", "error"}:
            bad_val += 1
            continue
        
        try:
            val = float(val_raw)
        except ValueError:
            bad_val += 1
            continue
        
        # Limpieza de timestamp
        ts_clean = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"):
            try:
                dt = datetime.strptime(ts_raw, fmt)
                ts_clean = dt.strftime("%Y-%m-%dT%H:%M:%S")
                break
            except ValueError:
                pass
        
        # Intentar con formato sin milisegundos
        if ts_clean is None and "T" in ts_raw and len(ts_raw) >= 19:
            try:
                dt = datetime.strptime(ts_raw[:19], "%Y-%m-%dT%H:%M:%S")
                ts_clean = dt.strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
        
        if ts_clean is None:
            bad_ts += 1
            continue
        
        # Convertir voltaje a temperatura (T(°C) = 18*V - 64)
        temperatura = 18 * val - 64
        temperatura = round(temperatura, 2)  # 2 decimales
        
        # Generar alerta por temperatura > 40°C
        if temperatura > 40:
            alerta = "ALERTA"
            alertas_count += 1
        else:
            alerta = "OK"
        
        # Guardar datos para estadísticas
        voltajes.append(val)
        temperaturas.append(temperatura)
        kept += 1
        
        # Escribir fila procesada
        writer.writerow({
            "Timestamp": ts_clean,
            "voltaje": f"{val:.2f}",
            "Temp_C": f"{temperatura:.2f}",
            "Alertas": alerta
        })

# Estadísticas de calidad de datos
descartes_totales = bad_ts + bad_val
pct_descartadas = (descartes_totales / total * 100.0) if total else 0.0

kpis_calidad = {
    "filas_totales": total,
    "filas_validas": kept,
    "descartes_timestamp": bad_ts,
    "descartes_valor": bad_val,
    "%_descartadas": round(pct_descartadas, 2),
}

# Estadísticas de temperaturas
if len(temperaturas) == 0:
    kpis_temperatura = {
        "n": 0, "min": None, "max": None, "prom": None, 
        "alertas": 0, "alertas_pct": 0.0
    }
else:
    kpis_temperatura = {
        'n': len(temperaturas),
        'min': round(min(temperaturas), 2),
        "max": round(max(temperaturas), 2),
        "prom": round(mean(temperaturas), 2),
        "alertas": alertas_count,
        "alertas_pct": round(100.0 * alertas_count / len(temperaturas), 2),
    }

# INFORME DE VALORES OBTENIDOS
print("\n" + "="*60)
print("INFORME DE RESULTADOS - PROCESAMIENTO DE TEMPERATURAS")
print("="*60)

print(f"\n📊 ESTADÍSTICAS DE CALIDAD DE DATOS:")
print(f"   • Filas totales procesadas: {kpis_calidad['filas_totales']}")
print(f"   • Filas válidas conservadas: {kpis_calidad['filas_validas']}")
print(f"   • Filas descartadas: {descartes_totales} ({kpis_calidad['%_descartadas']}%)")
print(f"     - Por timestamp inválido: {bad_ts}")
print(f"     - Por valor inválido: {bad_val}")

print(f"\n🌡️  ESTADÍSTICAS DE TEMPERATURA:")
print(f"   • Muestras de temperatura: {kpis_temperatura['n']}")
print(f"   • Temperatura mínima: {kpis_temperatura['min']}°C")
print(f"   • Temperatura máxima: {kpis_temperatura['max']}°C")
print(f"   • Temperatura promedio: {kpis_temperatura['prom']}°C")
print(f"   • Alertas generadas (>40°C): {kpis_temperatura['alertas']}")
print(f"   • Porcentaje de alertas: {kpis_temperatura['alertas_pct']}%")

print(f"\n💾 ARCHIVOS:")
print(f"   • Entrada: {IN_FILE}")
print(f"   • Salida: {OUT_FILE}")

print(f"\n✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
print("="*60)