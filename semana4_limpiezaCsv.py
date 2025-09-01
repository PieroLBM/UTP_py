import csv
from datetime import datetime
from pathlib import Path #importo el comando path (busca el lugar del codigo)


#path - ruta de acceso
ROOT = Path(__file__).resolve().parents[0] # sube desde src/ a la raiz del proyecto 
TXT = ROOT / "UTP_py" #carpeta donde estan los archivos
IN_FILE = TXT / "voltajes_250_sucio.csv" #archivo de entrada
OUT_FILE = TXT /"voltajes_250_limpio.csv" #archivo de salida
#apertura de archivos
with open(IN_FILE, "r", encoding="utf-8", newline='') as fin,\
    open(OUT_FILE, "w", encoding="utf-8", newline='') as fout:
    reader = csv.DictReader(fin, delimiter=";") #lee el archivo de entrada
    write  = csv.DictWriter(fout, fieldnames=["timestamp", "value"]) #escribe el archivo de salida
    writer.writeheader() #escribe la cabecera
#leer linea por linea y seleccionar en crudo raw
    total = kept = 0
    for row in reader:
        total += 1
        ts_raw = (row.get("timestamp") or "").strip() #si no hay timestamp, lo ignora
        val_raw = (row.get("value") or "").strip() #si no hay value, lo ignora
#limpiar datos
        val_raw = val_raw.replace(",", ".") #reemplaza las comas por puntos
        val_low = val_raw.lower() #convierte a minusculas
        if val_low in ("", "na", "n/a", "nan", "null", "none", "error"):
            continue #si el valor es alguno de estos, lo ignora
        try:
            val = float(val_raw) #convierte a float 
        except ValueError:
            continue    #si no es ni linea ni numero, lo ignora
        print(val)