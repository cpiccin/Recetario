import tkinter as tk

from storage import cargar_recetas


class BuscarTab:
    def __init__(self, parent, on_seleccionar):
        self.parent = parent
        self.on_seleccionar_callback = on_seleccionar
        self.resultados = []

        self.criterio = tk.StringVar(value="nombre")
        self.texto = tk.StringVar()

        controles = tk.Frame(parent)
        controles.pack(fill="x", padx=10, pady=10)

        tk.Radiobutton(
            controles,
            text="Nombre de receta",
            variable=self.criterio,
            value="nombre",
            command=self.buscar,
        ).pack(side="left")
        tk.Radiobutton(
            controles,
            text="Ingrediente",
            variable=self.criterio,
            value="ingrediente",
            command=self.buscar,
        ).pack(side="left", padx=(10, 0))

        entry = tk.Entry(parent, textvariable=self.texto)
        entry.pack(fill="x", padx=10)
        entry.bind("<KeyRelease>", lambda e: self.buscar())

        self.lista = tk.Listbox(parent)
        self.lista.pack(fill="both", expand=True, padx=10, pady=10)
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
