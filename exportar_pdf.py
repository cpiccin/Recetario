import re

from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from richtext import quitar_etiquetas
from storage import BASE_DIR

_PATRON_ENLACE = re.compile(r'<a href="([^"]*)">(.*?)</a>', re.DOTALL)


def _html_a_reportlab(html):
    def _reemplazo(match):
        titulo, texto = match.groups()
        return f"{texto} <i>(receta: {titulo})</i>"

    return _PATRON_ENLACE.sub(_reemplazo, html or "")


def _parrafo_seguro(texto, estilo):
    try:
        return Paragraph(texto, estilo)
    except Exception:
        return Paragraph(quitar_etiquetas(texto), estilo)


def _estilos():
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle("TituloReceta", parent=base["Title"], alignment=0, spaceAfter=10),
        "seccion": ParagraphStyle("Seccion", parent=base["Heading2"], spaceBefore=14, spaceAfter=6),
        "cuerpo": ParagraphStyle("Cuerpo", parent=base["BodyText"], spaceAfter=4),
    }


def _imagen_ajustada(ruta_absoluta, maximo_cm=14):
    try:
        with PILImage.open(ruta_absoluta) as imagen:
            ancho_px, alto_px = imagen.size
    except (FileNotFoundError, OSError):
        return None

    maximo = maximo_cm * cm
    escala = min(maximo / ancho_px, maximo / alto_px, 1)
    return RLImage(str(ruta_absoluta), width=ancho_px * escala, height=alto_px * escala)


def exportar_recetas_pdf(recetas, ruta_destino):
    estilos = _estilos()
    documento = SimpleDocTemplate(
        str(ruta_destino), pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
    )
    elementos = []

    for indice, receta in enumerate(recetas):
        if indice > 0:
            elementos.append(PageBreak())

        elementos.append(_parrafo_seguro(receta.get("titulo", ""), estilos["titulo"]))

        ingredientes = receta.get("ingredientes") or []
        if ingredientes:
            elementos.append(Paragraph("Ingredientes", estilos["seccion"]))
            items = []
            for item in ingredientes:
                cantidad = item.get("cantidad", "").strip()
                nombre = _html_a_reportlab(item.get("nombre", ""))
                texto = f"{cantidad} {nombre}".strip() if cantidad else nombre
                items.append(ListItem(_parrafo_seguro(texto, estilos["cuerpo"])))
            elementos.append(ListFlowable(items, bulletType="bullet"))

        pasos = receta.get("pasos") or []
        if pasos:
            elementos.append(Paragraph("Pasos", estilos["seccion"]))
            if isinstance(pasos, list):
                items = [
                    ListItem(_parrafo_seguro(_html_a_reportlab(p), estilos["cuerpo"])) for p in pasos
                ]
                elementos.append(ListFlowable(items, bulletType="1"))
            else:
                elementos.append(_parrafo_seguro(_html_a_reportlab(pasos), estilos["cuerpo"]))

        notas = (receta.get("notas") or "").strip()
        if notas:
            elementos.append(Paragraph("Notas", estilos["seccion"]))
            elementos.append(_parrafo_seguro(_html_a_reportlab(notas), estilos["cuerpo"]))

        imagenes = receta.get("imagenes") or []
        if imagenes:
            elementos.append(Paragraph("Imágenes", estilos["seccion"]))
            for ruta in imagenes:
                imagen_rl = _imagen_ajustada(BASE_DIR / ruta)
                if imagen_rl is not None:
                    elementos.append(imagen_rl)
                    elementos.append(Spacer(1, 8))

    documento.build(elementos)
