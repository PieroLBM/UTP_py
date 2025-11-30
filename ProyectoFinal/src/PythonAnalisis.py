import csv
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import math

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
IN_FILE = PROJECT_ROOT / "datos" / "raw" / "sensor_data.csv"
OUT_FILE = PROJECT_ROOT / "datos" / "processing" / "ultrasonic_processed.csv"

def verificar_estructura():
    print("Verificando estructura de carpetas...")
    
    carpetas_necesarias = [
        PROJECT_ROOT / "datos" / "raw",
        PROJECT_ROOT / "datos" / "processing"
    ]
    
    for carpeta in carpetas_necesarias:
        carpeta.mkdir(parents=True, exist_ok=True)
        print(f"   Carpeta verificada: {carpeta}")
    
    if not IN_FILE.exists():
        print(f"   Archivo no encontrado: {IN_FILE}")
        return False
    
    if IN_FILE.stat().st_size == 0:
        print(f"   Archivo existe pero está vacío: {IN_FILE}")
        return False
    
    print(f"   Archivo de entrada encontrado: {IN_FILE}")
    print(f"   Tamaño del archivo: {IN_FILE.stat().st_size} bytes")
    
    try:
        with open(IN_FILE, 'r', encoding='utf-8') as f:
            line_count = sum(1 for line in f)
        print(f"   Líneas totales en archivo: {line_count}")
    except:
        print("   No se pudo contar las líneas del archivo")
    
    return True

def limpiar_valor_numerico(valor_raw: str) -> Optional[float]:
    if not valor_raw:
        return None
    
    valor_raw = valor_raw.replace(",", ".")
    valor_low = valor_raw.lower().strip()
    
    if valor_low in {"", "na", "n/a", "nan", "null", "none", "error"}:
        return None
    
    try:
        return float(valor_raw)
    except ValueError:
        return None

def limpiar_timestamp(ts_raw: str) -> Optional[str]:
    if not ts_raw:
        return None
    
    ts_raw = ts_raw.strip()
    
    try:
        ts_int = int(ts_raw)
        dt = datetime.fromtimestamp(ts_int / 1000)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, OSError):
        pass
    
    return None

def procesar_archivo() -> Tuple[List[Dict], Dict]:
    datos_procesados = []
    estadisticas = {
        "total": 0,
        "keep": 0,
        "bad_ts": 0,
        "bad_val": 0,
        "alertas_count": 0
    }
    
    try:
        with open(IN_FILE, 'r', encoding="utf-8", newline="") as fin:
            contenido = fin.read()
            fin.seek(0)
            
            primera_linea = fin.readline().strip()
            fin.seek(0)
            
            if primera_linea.startswith("ts_ms") or primera_linea.startswith("timestamp"):
                reader = csv.DictReader(fin)
                print("   Usando archivo con encabezados")
            else:
                fieldnames = ["ts_ms", "Sensor_ID", "distancia", "dist_avg", "estado", 
                            "num_eventos", "dur_promedio", "porc_alerta", "escenario"]
                reader = csv.DictReader(fin, fieldnames=fieldnames)
                print("   Usando archivo sin encabezados")
            
            for row_num, row in enumerate(reader, 1):
                estadisticas["total"] += 1
                
                distancia_raw = row.get("dist_avg", "")
                distancia = limpiar_valor_numerico(distancia_raw)
                if distancia is None:
                    estadisticas["bad_val"] += 1
                    continue
                
                ts_raw = row.get("ts_ms", "")
                ts_clean = limpiar_timestamp(ts_raw)
                if ts_clean is None:
                    estadisticas["bad_ts"] += 1
                    continue
                
                estado_raw = row.get("estado", "")
                estado = "ALERT" if estado_raw.upper() in ["ALERTA", "ALERT", "1"] else "NORMAL"
                
                if estado == "ALERT":
                    estadisticas["alertas_count"] += 1
                
                datos_procesados.append({
                    "Timestamp": ts_clean,
                    "Distancia_cm": round(distancia, 2),
                    "Estado": estado
                })
                estadisticas["keep"] += 1
                
                if row_num % 100 == 0:
                    print(f"   Procesadas {row_num} filas...")
                
    except FileNotFoundError:
        print(f"Error: No se puede encontrar el archivo {IN_FILE}")
        return [], estadisticas
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        return [], estadisticas
    
    print(f"   Resumen de procesamiento:")
    print(f"      Filas totales: {estadisticas['total']}")
    print(f"      Filas válidas: {estadisticas['keep']}")
    print(f"      Errores timestamp: {estadisticas['bad_ts']}")
    print(f"      Errores valor: {estadisticas['bad_val']}")
    
    return datos_procesados, estadisticas

def guardar_datos_procesados(datos_procesados: List[Dict]):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUT_FILE, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=["ts_ms", "sensor_id", "valor(s)", "estado"])
        writer.writeheader()
        
        for fila in datos_procesados:
            processed_row = {
                "ts_ms": fila["Timestamp"],
                "sensor_id": "HC-SR04",
                "valor(s)": fila["Distancia_cm"],
                "estado": fila["Estado"]
            }
            writer.writerow(processed_row)

def calcular_estadisticas(datos_procesados: List[Dict], estadisticas: Dict) -> Tuple[Dict, Dict, Dict]:
    if not datos_procesados:
        print("   No hay datos para calcular estadísticas")
        return {}, {}, {}
        
    distancias = [fila["Distancia_cm"] for fila in datos_procesados]
    estados = [fila["Estado"] for fila in datos_procesados]
    
    descartes_totales = estadisticas["bad_ts"] + estadisticas["bad_val"]
    pct_descartadas = (descartes_totales / estadisticas["total"] * 100.0) if estadisticas["total"] else 0.0
    
    kpis_calidad = {
        "filas_totales": estadisticas["total"],
        "filas_validas": estadisticas["keep"],
        "descartes_timestamp": estadisticas["bad_ts"],
        "descartes_valor": estadisticas["bad_val"],
        "%_descartadas": round(pct_descartadas, 2),
    }
    
    kpis_basicos = {
        'n': len(distancias),
        'min': round(min(distancias), 2),
        "max": round(max(distancias), 2),
        "prom": round(mean(distancias), 2),
        "desviacion_std": round(stdev(distancias), 2) if len(distancias) > 1 else 0,
        "alertas": estadisticas["alertas_count"],
        "alertas_pct": round(100.0 * estadisticas["alertas_count"] / len(distancias), 2),
    }
    
    kpis_avanzados = calcular_kpis_avanzados(distancias)
    
    duraciones = []
    in_event = False
    event_start = None
    
    for fila in datos_procesados:
        current_time = datetime.strptime(fila["Timestamp"], "%Y-%m-%dT%H:%M:%S")
        
        if fila["Estado"] == "ALERT" and not in_event:
            in_event = True
            event_start = current_time
        elif fila["Estado"] == "NORMAL" and in_event and event_start:
            in_event = False
            duracion = (current_time - event_start).total_seconds()
            duraciones.append(duracion)
    
    kpis_avanzados["duracion_promedio_eventos"] = round(mean(duraciones), 2) if duraciones else 0
    kpis_avanzados["total_eventos"] = len(duraciones)
    
    return kpis_calidad, kpis_basicos, kpis_avanzados

def calcular_kpis_avanzados(distancias: List[float]) -> Dict:
    if not distancias:
        return {
            "rms": 0,
            "thd": 0,
            "frecuencia_pico": 0,
            "duracion_promedio_eventos": 0,
            "total_eventos": 0
        }
    
    rms = math.sqrt(sum(d**2 for d in distancias) / len(distancias))
    
    fundamental = mean(distancias)
    harmonic_distortion = math.sqrt(sum((d - fundamental)**2 for d in distancias) / len(distancias))
    thd = (harmonic_distortion / fundamental) * 100 if fundamental != 0 else 0
    
    histograma = {}
    for d in distancias:
        bin_val = round(d / 5) * 5
        histograma[bin_val] = histograma.get(bin_val, 0) + 1
    
    frecuencia_pico = max(histograma.items(), key=lambda x: x[1])[0] if histograma else 0
    
    return {
        "rms": round(rms, 2),
        "thd": round(thd, 2),
        "frecuencia_pico": frecuencia_pico
    }

def generar_graficos(datos_procesados: List[Dict]):
    if not datos_procesados:
        print("No hay datos para generar gráficos")
        return
    
    distancias = [fila["Distancia_cm"] for fila in datos_procesados]
    timestamps = [fila["Timestamp"] for fila in datos_procesados]
    estados = [fila["Estado"] for fila in datos_procesados]
    
    tiempos = [datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S") for ts in timestamps]
    
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.plot(tiempos, distancias, 'b-', alpha=0.7, linewidth=1, label='Distancia')
    
    alert_times = [tiempos[i] for i, estado in enumerate(estados) if estado == "ALERT"]
    alert_dists = [distancias[i] for i, estado in enumerate(estados) if estado == "ALERT"]
    if alert_times:
        plt.scatter(alert_times, alert_dists, color='red', s=10, alpha=0.6, label='Alerta')
    
    plt.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='Umbral (30cm)')
    plt.xlabel('Tiempo')
    plt.ylabel('Distancia (cm)')
    plt.title('Evolución Temporal - Distancia vs Tiempo')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 2)
    plt.hist(distancias, bins=20, alpha=0.7, edgecolor='black', color='skyblue')
    plt.axvline(x=30, color='r', linestyle='--', label='Umbral de alerta (30cm)')
    plt.xlabel('Distancia (cm)')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de Distancias')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 3)
    dist_normal = [distancias[i] for i, estado in enumerate(estados) if estado == "NORMAL"]
    dist_alerta = [distancias[i] for i, estado in enumerate(estados) if estado == "ALERT"]
    
    data = []
    labels = []
    
    if dist_normal:
        data.append(dist_normal)
        labels.append('Normal')
    if dist_alerta:
        data.append(dist_alerta) 
        labels.append('Alerta')
    
    if data:
        plt.boxplot(data, labels=labels)
        plt.ylabel('Distancia (cm)')
        plt.title('Boxplot - Comparación de Escenarios')
        plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 2, 4)
    estado_numerico = [1 if estado == "ALERT" else 0 for estado in estados]
    plt.plot(tiempos, estado_numerico, 'r-', linewidth=2)
    plt.xlabel('Tiempo')
    plt.ylabel('Estado (0=Normal, 1=Alerta)')
    plt.title('Estados del Sistema')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    grafico_path = PROJECT_ROOT / "datos" / "processing" / "graficos_ultrasonic.png"
    plt.savefig(grafico_path, dpi=150, bbox_inches='tight')
    print(f"Gráficos guardados en: {grafico_path}")
    plt.show()

def generar_informe(kpis_calidad: Dict, kpis_basicos: Dict, kpis_avanzados: Dict):
    print("\n" + "="*70)
    print("INFORME DE RESULTADOS - VIGILANTE ULTRASÓNICO")
    print("="*70)

    print(f"\nESTADÍSTICAS DE CALIDAD DE DATOS:")
    print(f"   Filas totales procesadas: {kpis_calidad['filas_totales']}")
    print(f"   Filas válidas conservadas: {kpis_calidad['filas_validas']}")
    print(f"   Filas descartadas: {kpis_calidad['descartes_timestamp'] + kpis_calidad['descartes_valor']} ({kpis_calidad['%_descartadas']}%)")

    print(f"\nESTADÍSTICAS BÁSICAS DE DISTANCIA:")
    print(f"   Muestras válidas (n): {kpis_basicos['n']}")
    print(f"   Distancia mínima: {kpis_basicos['min']} cm")
    print(f"   Distancia máxima: {kpis_basicos['max']} cm")
    print(f"   Distancia promedio: {kpis_basicos['prom']} cm")
    print(f"   Desviación estándar: {kpis_basicos['desviacion_std']} cm")
    print(f"   Alertas generadas: {kpis_basicos['alertas']}")
    print(f"   Porcentaje de alertas: {kpis_basicos['alertas_pct']}%")

    print(f"\nKPIs AVANZADOS DEL SISTEMA:")
    print(f"   Valor RMS: {kpis_avanzados['rms']} cm")
    print(f"   THD aproximado: {kpis_avanzados['thd']}%")
    print(f"   Frecuencia pico: {kpis_avanzados['frecuencia_pico']} cm")
    print(f"   Total de eventos: {kpis_avanzados['total_eventos']}")
    print(f"   Duración promedio eventos: {kpis_avanzados['duracion_promedio_eventos']} s")

    print(f"\nARCHIVOS:")
    print(f"   Entrada: {IN_FILE}")
    print(f"   Salida procesada: {OUT_FILE}")
    print(f"   Gráficos: {PROJECT_ROOT/'datos'/'processing'/'graficos_ultrasonic.png'}")

    print(f"\nPROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*70)

def main():
    print("PROCESAMIENTO DE DATOS - VIGILANTE ULTRASÓNICO")
    
    if not verificar_estructura():
        print("No se puede continuar - archivo de datos no disponible")
        return
    
    print("\nIniciando procesamiento de datos...")
    
    datos_procesados, estadisticas = procesar_archivo()
    
    if not datos_procesados:
        print("No se pudieron procesar datos")
        return
    
    guardar_datos_procesados(datos_procesados)
    print(f"Datos procesados guardados en: {OUT_FILE}")
    print(f"Registros procesados: {len(datos_procesados)}")
    
    kpis_calidad, kpis_basicos, kpis_avanzados = calcular_estadisticas(datos_procesados, estadisticas)
    
    print("\nGenerando gráficos...")
    generar_graficos(datos_procesados)
    
    generar_informe(kpis_calidad, kpis_basicos, kpis_avanzados)

if __name__ == "__main__":
    main()