import tkinter as tk
from tkinter import ttk

from storage import cargar_recetas
from styles import agregar_hover_listbox, estilizar_listbox


class BuscarTab:
    def __init__(self, parent, on_seleccionar):
        self.parent = parent
        self.on_seleccionar_callback = on_seleccionar
        self.resultados = []

        self.criterio = tk.StringVar(value="nombre")
        self.texto = tk.StringVar()

        panel = ttk.Frame(parent, style="Panel.TFrame")
        panel.pack(fill="both", expand=True)

        contenido = ttk.Frame(panel, style="Panel.TFrame")
        contenido.pack(fill="both", expand=True, padx=16, pady=16)

        ttk.Label(contenido, text="Buscar receta", style="Seccion.TLabel").pack(
            anchor="w", pady=(0, 10)
        )

        controles = ttk.Frame(contenido, style="Panel.TFrame")
        controles.pack(fill="x")

        ttk.Radiobutton(
            controles,
            text="Nombre de receta",
            variable=self.criterio,
            value="nombre",
            command=self.buscar,
        ).pack(side="left")
        ttk.Radiobutton(
            controles,
            text="Ingrediente",
            variable=self.criterio,
            value="ingrediente",
            command=self.buscar,
        ).pack(side="left", padx=(16, 0))

        entry = ttk.Entry(contenido, textvariable=self.texto, font=("Segoe UI", 11))
        entry.pack(fill="x", pady=(10, 12))
        entry.bind("<KeyRelease>", lambda e: self.buscar())

        self.lista = tk.Listbox(contenido)
        estilizar_listbox(self.lista)
        agregar_hover_listbox(self.lista)
        self.lista.pack(fill="both", expand=True)
        self.lista.bind("<<ListboxSelect>>", self.on_seleccionar)

        self.buscar()

    def buscar(self):
        recetas = cargar_recetas()
        texto = self.texto.get().strip().lower()
        criterio = self.criterio.get()

        self.resultados = []
        for indice, receta in enumerate(recetas):
            if criterio == "nombre":
                coincide = texto in receta.get("titulo", "").lower()
            else:
                coincide = any(
                    texto in ingrediente.get("nombre", "").lower()
                    for ingrediente in receta.get("ingredientes") or []
                )
            if coincide:
                self.resultados.append((indice, receta))

        self.lista.delete(0, "end")
        for _, receta in self.resultados:
            self.lista.insert("end", receta.get("titulo", "(sin título)"))

    def on_seleccionar(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        indice_original, _ = self.resultados[seleccion[0]]
        self.on_seleccionar_callback(indice_original)
