import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from storage import actualizar_receta, guardar_imagen, guardar_receta
from styles import ERROR, EXITO


class AgregarTab:
    def __init__(self, parent, on_guardado=None):
        self.parent = parent
        self.on_guardado = on_guardado
        self.editando_indice = None

        self.ingrediente_filas = []
        self.paso_filas = []
        self.imagen_filas = []

        panel = ttk.Frame(parent, style="Panel.TFrame")
        panel.pack(fill="both", expand=True)

        pie = ttk.Frame(panel, style="Panel.TFrame")
        pie.pack(side="bottom", fill="x", padx=16, pady=(0, 14))

        self.estado = tk.StringVar()
        self.estado_label = ttk.Label(pie, textvariable=self.estado, style="Panel.TLabel")
        self.estado_label.pack(side="left")

        self.guardar_btn = ttk.Button(pie, text="Guardar receta", command=self.on_guardar)
        self.guardar_btn.pack(side="right")

        cuerpo = ttk.Frame(panel, style="Panel.TFrame")
        cuerpo.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(cuerpo, borderwidth=0, highlightthickness=0, bg="#FFFFFF")
        canvas.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=16)
        form_scrollbar = ttk.Scrollbar(cuerpo, orient="vertical", command=canvas.yview)
        form_scrollbar.pack(side="right", fill="y", padx=(0, 4), pady=16)
        canvas.configure(yscrollcommand=form_scrollbar.set)

        self.form_inner = ttk.Frame(canvas, style="Panel.TFrame")
        canvas.create_window((0, 0), window=self.form_inner, anchor="nw")
        self.form_inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def seccion(texto, primera=False):
            ttk.Label(self.form_inner, text=texto, style="Seccion.TLabel").pack(
                anchor="w", pady=(0 if primera else 18, 6), padx=(0, 16)
            )

        seccion("Título *", primera=True)
        self.titulo_entry = ttk.Entry(self.form_inner, font=("Verdana", 12))
        self.titulo_entry.pack(fill="x", padx=(0, 16))

        seccion("Ingredientes")
        columnas = ttk.Frame(self.form_inner, style="Panel.TFrame")
        columnas.pack(fill="x", padx=(0, 16))
        ttk.Label(columnas, text="Cantidad", width=10, style="Muted.TLabel").pack(side="left")
        ttk.Label(columnas, text="Ingrediente", style="Muted.TLabel").pack(
            side="left", fill="x", expand=True
        )
        self.ingredientes_container = ttk.Frame(self.form_inner, style="Panel.TFrame")
        self.ingredientes_container.pack(fill="x", padx=(0, 16), pady=(4, 0))
        ttk.Button(
            self.form_inner,
            text="+ Agregar ingrediente",
            style="Secundario.TButton",
            command=self.agregar_ingrediente,
        ).pack(anchor="w", pady=(8, 0), padx=(0, 16))

        seccion("Pasos")
        self.pasos_container = ttk.Frame(self.form_inner, style="Panel.TFrame")
        self.pasos_container.pack(fill="x", padx=(0, 16))
        ttk.Button(
            self.form_inner,
            text="+ Agregar paso",
            style="Secundario.TButton",
            command=self.agregar_paso,
        ).pack(anchor="w", pady=(8, 0), padx=(0, 16))

        seccion("Imágenes")
        self.imagenes_container = ttk.Frame(self.form_inner, style="Panel.TFrame")
        self.imagenes_container.pack(fill="x", padx=(0, 16))
        ttk.Button(
            self.form_inner,
            text="+ Subir imagen",
            style="Secundario.TButton",
            command=self.agregar_imagen,
        ).pack(anchor="w", pady=(8, 20), padx=(0, 16))

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
        fila = ttk.Frame(self.ingredientes_container, style="Panel.TFrame")
        fila.pack(fill="x", pady=3)

        cantidad_entry = ttk.Entry(fila, width=10)
        cantidad_entry.insert(0, cantidad)
        cantidad_entry.pack(side="left")

        nombre_entry = ttk.Entry(fila)
        nombre_entry.insert(0, nombre)
        nombre_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

        def eliminar():
            self.ingrediente_filas.remove((fila, cantidad_entry, nombre_entry))
            fila.destroy()

        ttk.Button(fila, text="×", style="Quitar.TButton", width=2, command=eliminar).pack(
            side="left", padx=(6, 0)
        )
        self.ingrediente_filas.append((fila, cantidad_entry, nombre_entry))
        cantidad_entry.focus_set()

    def agregar_paso(self, texto=""):
        fila = ttk.Frame(self.pasos_container, style="Panel.TFrame")
        fila.pack(fill="x", pady=3)

        entry = ttk.Entry(fila)
        entry.insert(0, texto)
        entry.pack(side="left", fill="x", expand=True)

        def eliminar():
            self.paso_filas.remove((fila, entry))
            fila.destroy()

        ttk.Button(fila, text="×", style="Quitar.TButton", width=2, command=eliminar).pack(
            side="left", padx=(6, 0)
        )
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
        fila = ttk.Frame(self.imagenes_container, style="Panel.TFrame")
        fila.pack(fill="x", pady=3)
        ttk.Label(fila, text=Path(ruta_relativa).name, style="Panel.TLabel").pack(
            side="left", fill="x", expand=True
        )

        def eliminar():
            self.imagen_filas.remove((fila, ruta_relativa))
            fila.destroy()

        ttk.Button(fila, text="×", style="Quitar.TButton", width=2, command=eliminar).pack(
            side="left", padx=(6, 0)
        )
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
            self.estado_label.config(foreground=ERROR)
            self.estado.set("El título es obligatorio.")
            return

        self.estado_label.config(foreground=EXITO)
        self.estado.set("Receta guardada.")
        self.parent.after(2000, lambda: self.estado.set(""))

        if self.on_guardado:
            self.on_guardado()

        self._limpiar_formulario()
