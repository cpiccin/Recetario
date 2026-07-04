import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
RECETAS_PATH = BASE_DIR / "recetas.json"
IMG_DIR = BASE_DIR / "img"


def cargar_recetas():
    if RECETAS_PATH.exists():
        return json.loads(RECETAS_PATH.read_text(encoding="utf-8"))
    return []


def guardar_receta(receta):
    if not receta.get("titulo", "").strip():
        return False
    recetas = cargar_recetas()
    recetas.append(receta)
    RECETAS_PATH.write_text(json.dumps(recetas, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def guardar_imagen(ruta_origen):
    IMG_DIR.mkdir(exist_ok=True)
    origen = Path(ruta_origen)

    destino = IMG_DIR / origen.name
    contador = 1
    while destino.exists():
        destino = IMG_DIR / f"{origen.stem}_{contador}{origen.suffix}"
        contador += 1

    shutil.copy2(origen, destino)
    return str(destino.relative_to(BASE_DIR)).replace("\\", "/")
