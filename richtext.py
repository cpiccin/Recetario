import re
import tkinter as tk

from styles import ACCENT

_TAG_A_TK = {"b": "negrita", "i": "cursiva", "u": "subrayado"}
_TK_A_TAG = {v: k for k, v in _TAG_A_TK.items()}
_PREFIJO_ENLACE = "enlace::"
_PATRON_ETIQUETA = re.compile(r'<(/?)([biu])>|<a href="([^"]*)">|(</a>)')


def _escapar(texto):
    return (
        texto.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _desescapar(texto):
    return (
        texto.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
    )


def configurar_tags(text_widget, font_normal=("Verdana", 10)):
    familia, tamano = font_normal[0], font_normal[1]
    text_widget.tag_configure("negrita", font=(familia, tamano, "bold"))
    text_widget.tag_configure("cursiva", font=(familia, tamano, "italic"))
    text_widget.tag_configure("subrayado", font=(familia, tamano), underline=True)
    text_widget.tag_configure("enlace", foreground=ACCENT, underline=True)


def insertar_html(text_widget, html):
    activos = []
    enlace_actual = None
    pos = 0

    def _tags_actuales():
        tags = [_TAG_A_TK[letra] for letra in activos]
        if enlace_actual is not None:
            tags.append("enlace")
            tags.append(_PREFIJO_ENLACE + enlace_actual)
        return tuple(tags)

    for match in _PATRON_ETIQUETA.finditer(html):
        fragmento = html[pos : match.start()]
        if fragmento:
            text_widget.insert("end", _desescapar(fragmento), _tags_actuales())

        cierre_biu, letra, href, cierre_enlace = match.groups()
        if letra:
            if cierre_biu:
                if letra in activos:
                    activos.remove(letra)
            elif letra not in activos:
                activos.append(letra)
        elif href is not None:
            enlace_actual = _desescapar(href)
        elif cierre_enlace:
            enlace_actual = None
        pos = match.end()

    resto = html[pos:]
    if resto:
        text_widget.insert("end", _desescapar(resto), _tags_actuales())


def texto_a_html(text_widget):
    partes = []
    for clave, valor, _indice in text_widget.dump("1.0", "end-1c", tag=True, text=True):
        if clave == "tagon":
            if valor in _TK_A_TAG:
                partes.append(f"<{_TK_A_TAG[valor]}>")
            elif valor.startswith(_PREFIJO_ENLACE):
                titulo = valor[len(_PREFIJO_ENLACE) :]
                partes.append(f'<a href="{_escapar(titulo)}">')
        elif clave == "tagoff":
            if valor in _TK_A_TAG:
                partes.append(f"</{_TK_A_TAG[valor]}>")
            elif valor.startswith(_PREFIJO_ENLACE):
                partes.append("</a>")
        elif clave == "text":
            partes.append(_escapar(valor))
    return "".join(partes)


def quitar_etiquetas(html):
    return _desescapar(_PATRON_ETIQUETA.sub("", html))


def aplicar_enlace(text_widget, inicio, fin, titulo):
    text_widget.tag_add("enlace", inicio, fin)
    text_widget.tag_add(_PREFIJO_ENLACE + titulo, inicio, fin)


def titulo_de_tag_enlace(tag):
    if tag.startswith(_PREFIJO_ENLACE):
        return tag[len(_PREFIJO_ENLACE) :]
    return None


def alternar_formato(text_widget, tag):
    try:
        inicio = text_widget.index("sel.first")
        fin = text_widget.index("sel.last")
    except tk.TclError:
        return False
    if tag in text_widget.tag_names(inicio):
        text_widget.tag_remove(tag, inicio, fin)
    else:
        text_widget.tag_add(tag, inicio, fin)
    return True
