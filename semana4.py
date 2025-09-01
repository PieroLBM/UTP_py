#from pathlib import Path #importo el comando path (busca el lugar del codigo)
#ROOT = Path(__file__).resolve().parents[0] # sube desde src/ a la raiz del proyecto 
#TXT = ROOT / "UTP_Py" / "mediciones_basico.txt"

valores = []
#with open("mediciones_basico.txt", "r", encoding="utf-8") as file:
    #contenido = file.read()
    #print(contenido)                                

with open("mediciones_basico.txt", "r", encoding="utf-8") as file:
    for linea in file:
        s=linea.strip()
        if not s or s.startswith("#"): #si la linea esta vacia o empieza con #, la ignora
            continue
        if not s or s.startswith("!"): #si la linea no empieza con !, la ignora
            continue
        s = s.replace(",", ".") #reemplaza las comas por puntos
        try:
            valores.append(s)
        except ValueError:
            print(f"Valor no numerico: {s}") #si no es ni linea ni numero, lo ignora
            pass
print(valores)