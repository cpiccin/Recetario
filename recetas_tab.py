import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from storage import BASE_DIR, cargar_recetas
from styles import (
    ACCENT_DARK,
    FONT_SECCION,
    FONT_TITULO,
    TEXT,
    agregar_hover_listbox,
    estilizar_listbox,
    estilizar_texto,
)


class RecetasTab:
    def __init__(self, parent, on_editar):
        self.parent = parent
        self.on_editar = on_editar

        self.recetas = []
        self.imagenes_referencias = []
        self.receta_actual_indice = None

        list_frame = ttk.Frame(parent, style="Panel.TFrame")
        list_frame.pack(side="left", fill="y", padx=(0, 12), pady=0)

        inner_list = ttk.Frame(list_frame, style="Panel.TFrame")
        inner_list.pack(fill="both", expand=True, padx=12, pady=12)

        scrollbar = ttk.Scrollbar(inner_list)
        scrollbar.pack(side="right", fill="y")

        self.lista = tk.Listbox(inner_list, width=26, yscrollcommand=scrollbar.set)
        estilizar_listbox(self.lista)
        agregar_hover_listbox(self.lista)
        self.lista.pack(side="left", fill="both", expand=True)
        self.lista.bind("<<ListboxSelect>>", self.on_seleccionar)
        scrollbar.config(command=self.lista.yview)

        right_frame = ttk.Frame(parent, style="Panel.TFrame")
        right_frame.pack(side="left", fill="both", expand=True)

        inner_right = ttk.Frame(right_frame, style="Panel.TFrame")
        inner_right.pack(fill="both", expand=True, padx=16, pady=12)

        toolbar = ttk.Frame(inner_right, style="Panel.TFrame")
        toolbar.pack(side="top", fill="x")
        self.editar_btn = ttk.Button(
            toolbar, text="Editar", command=self.on_editar_click, state="disabled"
        )
        self.editar_btn.pack(side="right", pady=(0, 8))

        self.vista_texto = tk.Text(inner_right, wrap="word", width=1, height=1)
        estilizar_texto(self.vista_texto)
        self.vista_texto.pack(fill="both", expand=True)
        self.vista_texto.tag_configure("titulo", font=FONT_TITULO, foreground=TEXT, spacing3=12)
        self.vista_texto.tag_configure(
            "seccion", font=FONT_SECCION, foreground=ACCENT_DARK, spacing1=12, spacing3=4
        )
        self.vista_texto.tag_configure("cuerpo", foreground=TEXT, spacing1=2)
        self.vista_texto.config(state="disabled")

        self.refrescar_lista()

    def _cargar_lista(self):
        self.recetas = cargar_recetas()
        self.lista.delete(0, "end")
        for receta in self.recetas:
            self.lista.insert("end", receta.get("titulo", "(sin título)"))

    def refrescar_lista(self):
        self._cargar_lista()

        self.receta_actual_indice = None
        self.editar_btn.config(state="disabled")
        self.imagenes_referencias.clear()
        self.vista_texto.config(state="normal")
        self.vista_texto.delete("1.0", "end")
        self.vista_texto.config(state="disabled")

    def seleccionar_indice(self, indice):
        self._cargar_lista()
        self.lista.selection_clear(0, "end")
        self.lista.selection_set(indice)
        self.lista.see(indice)
        self.receta_actual_indice = indice
        self.mostrar_vista(self.recetas[indice])
        self.editar_btn.config(state="normal")

    def on_seleccionar(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        indice = seleccion[0]
        self.receta_actual_indice = indice
        self.mostrar_vista(self.recetas[indice])
        self.editar_btn.config(state="normal")

    def mostrar_vista(self, receta):
        self.imagenes_referencias.clear()

        self.vista_texto.config(state="normal")
        self.vista_texto.delete("1.0", "end")
        self.vista_texto.insert("end", receta.get("titulo", ""), "titulo")

        ingredientes = receta.get("ingredientes") or []
        if ingredientes:
            self.vista_texto.insert("end", "\nIngredientes\n", "seccion")
            for item in ingredientes:
                cantidad = item.get("cantidad", "").strip()
                nombre = item.get("nombre", "").strip()
                texto = f"{cantidad} {nombre}".strip() if cantidad else nombre
                self.vista_texto.insert("end", f"•  {texto}\n", "cuerpo")

        pasos = receta.get("pasos") or []
        if pasos:
            self.vista_texto.insert("end", "\nPasos\n", "seccion")
            for numero, paso in enumerate(pasos, start=1):
                self.vista_texto.insert("end", f"{numero}.  {paso}\n", "cuerpo")

        imagenes = receta.get("imagenes") or []
        if imagenes:
            self.vista_texto.insert("end", "\nImágenes\n", "seccion")
            for ruta in imagenes:
                try:
                    imagen = Image.open(BASE_DIR / ruta)
                    imagen.thumbnail((300, 300))
                    foto = ImageTk.PhotoImage(imagen)
                    self.imagenes_referencias.append(foto)
                    self.vista_texto.image_create("end", image=foto)
                    self.vista_texto.insert("end", "\n\n")
                except (FileNotFoundError, OSError):
                    self.vista_texto.insert("end", f"•  {ruta} (no se pudo cargar)\n", "cuerpo")

        self.vista_texto.config(state="disabled")

    def on_editar_click(self):
        if self.receta_actual_indice is None:
            return
        self.on_editar(self.recetas[self.receta_actual_indice], self.receta_actual_indice)
