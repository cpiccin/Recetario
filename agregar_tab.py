import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from storage import actualizar_receta, guardar_imagen, guardar_receta


class AgregarTab:
    def __init__(self, parent, on_guardado=None):
        self.parent = parent
        self.on_guardado = on_guardado
        self.editando_indice = None

        self.ingrediente_filas = []
        self.paso_filas = []
        self.imagen_filas = []

        self.guardar_btn = tk.Button(parent, text="Guardar", command=self.on_guardar)
        self.guardar_btn.pack(side="bottom", pady=(5, 10))

        self.estado = tk.StringVar()
        self.estado_label = tk.Label(parent, textvariable=self.estado, fg="green")
        self.estado_label.pack(side="bottom")

        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        form_scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        form_scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=form_scrollbar.set)

        self.form_inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.form_inner, anchor="nw")
        self.form_inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        tk.Label(self.form_inner, text="Título *").pack(anchor="w")
        self.titulo_entry = tk.Entry(self.form_inner)
        self.titulo_entry.pack(fill="x")

        tk.Label(self.form_inner, text="Ingredientes").pack(anchor="w", pady=(8, 0))
        columnas = tk.Frame(self.form_inner)
        columnas.pack(fill="x")
        tk.Label(columnas, text="Cantidad", width=10, anchor="w").pack(side="left")
        tk.Label(columnas, text="Ingrediente", anchor="w").pack(side="left", fill="x", expand=True)
        self.ingredientes_container = tk.Frame(self.form_inner)
        self.ingredientes_container.pack(fill="x")
        tk.Button(
            self.form_inner, text="+ Agregar ingrediente", command=self.agregar_ingrediente
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(self.form_inner, text="Pasos").pack(anchor="w", pady=(8, 0))
        self.pasos_container = tk.Frame(self.form_inner)
        self.pasos_container.pack(fill="x")
        tk.Button(self.form_inner, text="+ Agregar paso", command=self.agregar_paso).pack(
            anchor="w", pady=(2, 0)
        )

        tk.Label(self.form_inner, text="Imágenes").pack(anchor="w", pady=(8, 0))
        self.imagenes_container = tk.Frame(self.form_inner)
        self.imagenes_container.pack(fill="x")
        tk.Button(self.form_inner, text="+ Subir imagen", command=self.agregar_imagen).pack(
            anchor="w", pady=(2, 0)
        )

        self.agregar_ingrediente()
        self.agregar_paso()

    def cargar_receta(self, receta, indice):
        self.editando_indice = indice

        self.titulo_entry.delete(0, "end")
        self.titulo_entry.insert(0, receta.get("titulo", ""))

        self._limpiar_filas(self.ingredientes_container, self.ingrediente_filas)
        self._limpiar_filas(self.pasos_container, self.paso_filas)
        self._limpiar_filas(self.imagenes_container, self.imagen_filas)

        ingredientes = receta.get("ingredientes") or []
        for item in ingredientes:
            self.agregar_ingrediente(item.get("cantidad", ""), item.get("nombre", ""))
        if not ingredientes:
            self.agregar_ingrediente()

        pasos = receta.get("pasos") or []
        for paso in pasos:
            self.agregar_paso(paso)
        if not pasos:
            self.agregar_paso()

        for ruta in receta.get("imagenes") or []:
            self._crear_fila_imagen(ruta)

    def agregar_ingrediente(self, cantidad="", nombre=""):
        fila = tk.Frame(self.ingredientes_container)
        fila.pack(fill="x", pady=2)

        cantidad_entry = tk.Entry(fila, width=10)
        cantidad_entry.insert(0, cantidad)
        cantidad_entry.pack(side="left")

        nombre_entry = tk.Entry(fila)
        nombre_entry.insert(0, nombre)
        nombre_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        def eliminar():
            self.ingrediente_filas.remove((fila, cantidad_entry, nombre_entry))
            fila.destroy()

        tk.Button(fila, text="×", command=eliminar, width=2).pack(side="left", padx=(4, 0))
        self.ingrediente_filas.append((fila, cantidad_entry, nombre_entry))
        cantidad_entry.focus_set()

    def agregar_paso(self, texto=""):
        fila = tk.Frame(self.pasos_container)
        fila.pack(fill="x", pady=2)

        entry = tk.Entry(fila)
        entry.insert(0, texto)
        entry.pack(side="left", fill="x", expand=True)

        def eliminar():
            self.paso_filas.remove((fila, entry))
            fila.destroy()

        tk.Button(fila, text="×", command=eliminar, width=2).pack(side="left", padx=(4, 0))
        self.paso_filas.append((fila, entry))
        entry.focus_set()

    def agregar_imagen(self):
        ruta_origen = filedialog.askopenfilename(
            title="Elegí una imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")],
        )
        if not ruta_origen:
            return

        self._crear_fila_imagen(guardar_imagen(ruta_origen))

    def _crear_fila_imagen(self, ruta_relativa):
        fila = tk.Frame(self.imagenes_container)
        fila.pack(fill="x", pady=2)
        tk.Label(fila, text=Path(ruta_relativa).name, anchor="w").pack(
            side="left", fill="x", expand=True
        )

        def eliminar():
            self.imagen_filas.remove((fila, ruta_relativa))
            fila.destroy()

        tk.Button(fila, text="×", command=eliminar, width=2).pack(side="left", padx=(4, 0))
        self.imagen_filas.append((fila, ruta_relativa))

    def _limpiar_filas(self, container, filas):
        for fila_info in filas:
            fila_info[0].destroy()
        filas.clear()

    def _limpiar_formulario(self):
        self.editando_indice = None
        self.titulo_entry.delete(0, "end")
        self._limpiar_filas(self.ingredientes_container, self.ingrediente_filas)
        self._limpiar_filas(self.pasos_container, self.paso_filas)
        self._limpiar_filas(self.imagenes_container, self.imagen_filas)
        self.agregar_ingrediente()
        self.agregar_paso()

    def on_guardar(self):
        receta = {
            "titulo": self.titulo_entry.get().strip(),
            "ingredientes": [
                {"cantidad": cantidad.get().strip(), "nombre": nombre.get().strip()}
                for _, cantidad, nombre in self.ingrediente_filas
                if nombre.get().strip()
            ],
            "pasos": [e.get().strip() for _, e in self.paso_filas if e.get().strip()],
            "imagenes": [ruta for _, ruta in self.imagen_filas],
        }

        if self.editando_indice is not None:
            ok = actualizar_receta(self.editando_indice, receta)
        else:
            ok = guardar_receta(receta)

        if not ok:
            self.estado_label.config(fg="red")
            self.estado.set("El título es obligatorio.")
            return

        self.estado_label.config(fg="green")
        self.estado.set("Receta guardada.")
        self.parent.after(2000, lambda: self.estado.set(""))

        if self.on_guardado:
            self.on_guardado()

        self._limpiar_formulario()
