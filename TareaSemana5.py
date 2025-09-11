from pathlib import Path
ROOT = Path(__file__).resolve().parents[0]
TXT = ROOT / "archivos"/ "mediciones_basico.txt"
print(ROOT)
with open(TXT, 'r', encoding='utf-8') as f:
    contenido = f.read()
    print(contenido)