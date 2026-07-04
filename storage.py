import json
from pathlib import Path

RECETAS_PATH = Path(__file__).parent / "recetas.json"


def cargar_recetas():
    if RECETAS_PATH.exists():
        return json.loads(RECETAS_PATH.read_text(encoding="utf-8"))
    return []


def guardar_receta(texto):
    texto = texto.strip()
    if not texto:
        return
    recetas = cargar_recetas()
    recetas.append(texto)
    RECETAS_PATH.write_text(json.dumps(recetas, ensure_ascii=False, indent=2), encoding="utf-8")
