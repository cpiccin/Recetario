import re
import tkinter as tk

_TAG_A_TK = {"b": "negrita", "i": "cursiva", "u": "subrayado"}
_TK_A_TAG = {v: k for k, v in _TAG_A_TK.items()}
_PATRON_ETIQUETA = re.compile(r"<(/?)([biu])>")


def _escapar(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _desescapar(texto):
    return texto.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def configurar_tags(text_widget, font_normal=("Verdana", 10)):
    familia, tamano = font_normal[0], font_normal[1]
    text_widget.tag_configure("negrita", font=(familia, tamano, "bold"))
    text_widget.tag_configure("cursiva", font=(familia, tamano, "italic"))
    text_widget.tag_configure("subrayado", font=(familia, tamano), underline=True)


def insertar_html(text_widget, html):
    activos = []
    pos = 0
    for match in _PATRON_ETIQUETA.finditer(html):
        fragmento = html[pos : match.start()]
        if fragmento:
            tags = tuple(_TAG_A_TK[letra] for letra in activos)
            text_widget.insert("end", _desescapar(fragmento), tags)
        cierre, letra = match.groups()
        if cierre:
            if letra in activos:
                activos.remove(letra)
        elif letra not in activos:
            activos.append(letra)
        pos = match.end()

    resto = html[pos:]
    if resto:
        tags = tuple(_TAG_A_TK[letra] for letra in activos)
        text_widget.insert("end", _desescapar(resto), tags)


def texto_a_html(text_widget):
    partes = []
    for clave, valor, _indice in text_widget.dump("1.0", "end-1c", tag=True, text=True):
        if clave == "tagon" and valor in _TK_A_TAG:
            partes.append(f"<{_TK_A_TAG[valor]}>")
        elif clave == "tagoff" and valor in _TK_A_TAG:
            partes.append(f"</{_TK_A_TAG[valor]}>")
        elif clave == "text":
            partes.append(_escapar(valor))
    return "".join(partes)


def quitar_etiquetas(html):
    return _desescapar(_PATRON_ETIQUETA.sub("", html))


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
