import json
import shutil
import sys
import zipfile
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

RECETAS_PATH = BASE_DIR / "recetas.json"
IMG_DIR = BASE_DIR / "img"


def cargar_recetas():
    if RECETAS_PATH.exists():
        return json.loads(RECETAS_PATH.read_text(encoding="utf-8"))
    return []


def _guardar_recetas(recetas):
    RECETAS_PATH.write_text(json.dumps(recetas, ensure_ascii=False, indent=2), encoding="utf-8")


def guardar_receta(receta):
    if not receta.get("titulo", "").strip():
        return False
    recetas = cargar_recetas()
    recetas.append(receta)
    _guardar_recetas(recetas)
    return True


def actualizar_receta(indice, receta):
    if not receta.get("titulo", "").strip():
        return False
    recetas = cargar_recetas()
    if indice < 0 or indice >= len(recetas):
        return False
    recetas[indice] = receta
    _guardar_recetas(recetas)
    return True


def eliminar_receta(indice):
    recetas = cargar_recetas()
    if indice < 0 or indice >= len(recetas):
        return False
    del recetas[indice]
    _guardar_recetas(recetas)
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


def exportar_datos(ruta_destino):
    with zipfile.ZipFile(ruta_destino, "w", zipfile.ZIP_DEFLATED) as zf:
        if RECETAS_PATH.exists():
            zf.write(RECETAS_PATH, arcname="recetas.json")
        if IMG_DIR.exists():
            for archivo in IMG_DIR.rglob("*"):
                if archivo.is_file():
                    zf.write(archivo, arcname=f"img/{archivo.name}")


def _nombre_disponible(nombre_archivo):
    destino = IMG_DIR / nombre_archivo
    if not destino.exists():
        return nombre_archivo, destino
    stem, sufijo = Path(nombre_archivo).stem, Path(nombre_archivo).suffix
    contador = 1
    while destino.exists():
        nombre_archivo = f"{stem}_{contador}{sufijo}"
        destino = IMG_DIR / nombre_archivo
        contador += 1
    return nombre_archivo, destino


def _importar_desde_zip(ruta_zip):
    with zipfile.ZipFile(ruta_zip) as zf:
        try:
            nuevas = json.loads(zf.read("recetas.json").decode("utf-8"))
        except KeyError:
            raise ValueError("El .zip no contiene un recetas.json.")
        if not isinstance(nuevas, list):
            raise ValueError("El archivo no tiene el formato esperado (una lista de recetas).")

        IMG_DIR.mkdir(exist_ok=True)
        mapa_rutas = {}
        for nombre_en_zip in zf.namelist():
            if nombre_en_zip.startswith("img/") and not nombre_en_zip.endswith("/"):
                nombre_final, destino = _nombre_disponible(Path(nombre_en_zip).name)
                with zf.open(nombre_en_zip) as origen_f, open(destino, "wb") as destino_f:
                    shutil.copyfileobj(origen_f, destino_f)
                mapa_rutas[Path(nombre_en_zip).name] = f"img/{nombre_final}"

    for receta in nuevas:
        receta["imagenes"] = [
            mapa_rutas.get(Path(ruta).name, ruta) for ruta in (receta.get("imagenes") or [])
        ]
    return nuevas


def _importar_desde_json(ruta_json):
    nuevas = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    if not isinstance(nuevas, list):
        raise ValueError("El archivo no tiene el formato esperado (una lista de recetas).")
    return nuevas


def importar_datos(ruta_origen):
    ruta_origen = Path(ruta_origen)
    if ruta_origen.suffix.lower() == ".zip":
        nuevas = _importar_desde_zip(ruta_origen)
    else:
        nuevas = _importar_desde_json(ruta_origen)

    recetas = cargar_recetas()
    recetas.extend(nuevas)
    _guardar_recetas(recetas)
    return len(nuevas)
