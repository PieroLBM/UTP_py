import csv
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple, Optional

# Configuración de rutas
ROOT = Path(__file__).resolve().parents[1]
IN_FILE = ROOT/"datos"/"raw"/"datos_sucios_250_v2.csv"
OUT_FILE = ROOT/"datos"/"proccesing"/"Temperaturas_Procesado.csv"

def limpiar_valor_numerico(valor_raw: str) -> Optional[float]:
    """
    Limpia y convierte un valor string a float.
    Returns None si el valor es inválido.
    """
    if not valor_raw:
        return None
    
    valor_raw = valor_raw.replace(",", ".")
    valor_low = valor_raw.lower().strip()
    
    # Verificar valores inválidos
    if valor_low in {"", "na", "n/a", "nan", "null", "none", "error"}:
        return None
    
    try:
        return float(valor_raw)
    except ValueError:
        return None

def limpiar_timestamp(ts_raw: str) -> Optional[str]:
    """
    Limpia y estandariza el formato de timestamp.
    Returns None si el formato no es reconocido.
    """
    if not ts_raw:
        return None
    
    ts_raw = ts_raw.strip()
    formatos = ["%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"]
    
    for fmt in formatos:
        try:
            dt = datetime.strptime(ts_raw, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    
    # Intentar con formato sin milisegundos
    if "T" in ts_raw and len(ts_raw) >= 19:
        try:
            dt = datetime.strptime(ts_raw[:19], "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
    
    return None

def convertir_voltaje_a_temperatura(voltaje: float) -> float:
    """
    Convierte voltaje a temperatura usando la fórmula T(°C) = 18*V - 64.
    """
    temperatura = 18 * voltaje - 64
    return round(temperatura, 2)

def generar_alerta(temperatura: float) -> Tuple[str, bool]:
    """
    Genera alerta si la temperatura es mayor a 40°C.
    Returns (mensaje_alerta, es_alerta)
    """
    if temperatura > 40:
        return "ALERTA", True
    return "OK", False

def procesar_fila(row: Dict) -> Optional[Dict]:
    """
    Procesa una fila individual de datos.
    Returns None si la fila debe ser descartada.
    """
    ts_raw = row.get("timestamp", "")
    val_raw = row.get("value", "")
    
    # Limpiar valor numérico
    voltaje = limpiar_valor_numerico(val_raw)
    if voltaje is None:
        return None
    
    # Limpiar timestamp
    ts_clean = limpiar_timestamp(ts_raw)
    if ts_clean is None:
        return None
    
    # Convertir a temperatura
    temperatura = convertir_voltaje_a_temperatura(voltaje)
    
    # Generar alerta
    alerta, es_alerta = generar_alerta(temperatura)
    
    return {
        "Timestamp": ts_clean,
        "voltaje": round(voltaje, 2),
        "Temp_C": temperatura,
        "Alertas": alerta,
        "es_alerta": es_alerta
    }

def procesar_archivo() -> Tuple[List[Dict], Dict]:
    """
    Procesa el archivo completo y retorna datos procesados y estadísticas.
    """
    datos_procesados = []
    estadisticas = {
        "total": 0,
        "keep": 0,
        "bad_ts": 0,
        "bad_val": 0,
        "alertas_count": 0
    }
    
    with open(IN_FILE, 'r', encoding="utf-8", newline="") as fin:
        reader = csv.DictReader(fin, delimiter=';')
        
        for row in reader:
            estadisticas["total"] += 1
            
            fila_procesada = procesar_fila(row)
            
            if fila_procesada is None:
                # Determinar por qué se descartó
                ts_raw = row.get("timestamp", "")
                val_raw = row.get("value", "")
                
                if limpiar_valor_numerico(val_raw) is None:
                    estadisticas["bad_val"] += 1
                elif limpiar_timestamp(ts_raw) is None:
                    estadisticas["bad_ts"] += 1
                continue
            
            # Contar alertas
            if fila_procesada["es_alerta"]:
                estadisticas["alertas_count"] += 1
            
            # Remover campo temporal antes de guardar
            fila_sin_es_alerta = {k: v for k, v in fila_procesada.items() if k != "es_alerta"}
            datos_procesados.append(fila_sin_es_alerta)
            estadisticas["keep"] += 1
    
    return datos_procesados, estadisticas

def guardar_datos_procesados(datos_procesados: List[Dict]):
    """
    Guarda los datos procesados en el archivo de salida.
    """
    with open(OUT_FILE, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=["Timestamp", "voltaje", "Temp_C", "Alertas"])
        writer.writeheader()
        for fila in datos_procesados:
            fila_para_escribir = {
                "Timestamp": fila["Timestamp"],
                "voltaje": f"{fila['voltaje']:.2f}", 
                "Temp_C": f"{fila['Temp_C']:.2f}",
                "Alertas": fila["Alertas"]
            }
            writer.writerow(fila_para_escribir)

def calcular_estadisticas(datos_procesados: List[Dict], estadisticas: Dict) -> Tuple[Dict, Dict]:
    """
    Calcula estadísticas de temperatura y calidad de datos.
    """
    # Extraer listas de voltajes y temperaturas
    voltajes = [fila["voltaje"] for fila in datos_procesados]  
    temperaturas = [fila["Temp_C"] for fila in datos_procesados]
    
    # Estadísticas de calidad de datos
    descartes_totales = estadisticas["bad_ts"] + estadisticas["bad_val"]
    pct_descartadas = (descartes_totales / estadisticas["total"] * 100.0) if estadisticas["total"] else 0.0
    
    kpis_calidad = {
        "filas_totales": estadisticas["total"],
        "filas_validas": estadisticas["keep"],
        "descartes_timestamp": estadisticas["bad_ts"],
        "descartes_valor": estadisticas["bad_val"],
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
            "alertas": estadisticas["alertas_count"],
            "alertas_pct": round(100.0 * estadisticas["alertas_count"] / len(temperaturas), 2),
        }
    
    return kpis_calidad, kpis_temperatura

def generar_informe(kpis_calidad: Dict, kpis_temperatura: Dict):
    """
    Genera y muestra el informe de resultados en pantalla.
    """
    print("\n" + "="*60)
    print("INFORME DE RESULTADOS - PROCESAMIENTO DE TEMPERATURAS")
    print("="*60)

    print(f"\n📊 ESTADÍSTICAS DE CALIDAD DE DATOS:")
    print(f"   • Filas totales procesadas: {kpis_calidad['filas_totales']}")
    print(f"   • Filas válidas conservadas: {kpis_calidad['filas_validas']}")
    print(f"   • Filas descartadas: {kpis_calidad['descartes_timestamp'] + kpis_calidad['descartes_valor']} ({kpis_calidad['%_descartadas']}%)")
    print(f"     - Por timestamp inválido: {kpis_calidad['descartes_timestamp']}")
    print(f"     - Por valor inválido: {kpis_calidad['descartes_valor']}")

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

def main():
    """
    Función principal que coordina todo el procesamiento.
    """
    print("=== PROCESAMIENTO DE DATOS DE TEMPERATURA ===")
    print("Iniciando procesamiento de datos...")
    
    # Procesar archivo
    datos_procesados, estadisticas = procesar_archivo()
    
    # Guardar datos
    guardar_datos_procesados(datos_procesados)
    
    # Calcular estadísticas
    kpis_calidad, kpis_temperatura = calcular_estadisticas(datos_procesados, estadisticas)
    
    # Generar informe
    generar_informe(kpis_calidad, kpis_temperatura)

# Ejecutar el programa
if __name__ == "__main__":
    main()