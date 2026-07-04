import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from storage import cargar_recetas, guardar_imagen, guardar_receta


class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recetario")
        self.root.geometry("750x500")

        self.recetas = []
        self.ingrediente_filas = []
        self.paso_filas = []
        self.imagen_filas = []

        list_frame = tk.Frame(root)
        list_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

        self.nueva_btn = tk.Button(list_frame, text="+ Nueva receta", command=self.mostrar_formulario)
        self.nueva_btn.pack(side="top", fill="x", pady=(0, 5))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.lista = tk.Listbox(list_frame, width=25, yscrollcommand=scrollbar.set)
        self.lista.pack(side="left", fill="y", expand=True)
        self.lista.bind("<<ListboxSelect>>", self.on_seleccionar)
        scrollbar.config(command=self.lista.yview)

        self.right_container = tk.Frame(root)
        self.right_container.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

        self._build_formulario()
        self._build_vista()

        self.refrescar_lista()
        self.mostrar_formulario()

    def _build_formulario(self):
        self.form_frame = tk.Frame(self.right_container)

        self.guardar_btn = tk.Button(self.form_frame, text="Guardar", command=self.on_guardar)
        self.guardar_btn.pack(side="bottom", pady=(5, 0))

        self.estado = tk.StringVar()
        self.estado_label = tk.Label(self.form_frame, textvariable=self.estado, fg="green")
        self.estado_label.pack(side="bottom")

        canvas = tk.Canvas(self.form_frame, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        form_scrollbar = tk.Scrollbar(self.form_frame, orient="vertical", command=canvas.yview)
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

    def agregar_ingrediente(self):
        fila = tk.Frame(self.ingredientes_container)
        fila.pack(fill="x", pady=2)

        cantidad_entry = tk.Entry(fila, width=10)
        cantidad_entry.pack(side="left")

        nombre_entry = tk.Entry(fila)
        nombre_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        def eliminar():
            self.ingrediente_filas.remove((fila, cantidad_entry, nombre_entry))
            fila.destroy()

        tk.Button(fila, text="×", command=eliminar, width=2).pack(side="left", padx=(4, 0))
        self.ingrediente_filas.append((fila, cantidad_entry, nombre_entry))
        cantidad_entry.focus_set()

    def agregar_paso(self):
        fila = tk.Frame(self.pasos_container)
        fila.pack(fill="x", pady=2)

        entry = tk.Entry(fila)
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

        ruta_relativa = guardar_imagen(ruta_origen)

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

    def _build_vista(self):
        self.view_frame = tk.Frame(self.right_container)

        self.vista_texto = tk.Text(
            self.view_frame, wrap="word", width=1, height=1, borderwidth=0, highlightthickness=0
        )
        self.vista_texto.pack(fill="both", expand=True)
        self.vista_texto.tag_configure("titulo", font=("Segoe UI", 18, "bold"), spacing3=12)
        self.vista_texto.tag_configure("seccion", font=("Segoe UI", 11, "bold"), spacing1=10, spacing3=4)
        self.vista_texto.tag_configure("cuerpo", font=("Segoe UI", 10), spacing1=2)
        self.vista_texto.config(state="disabled")

    def mostrar_formulario(self):
        self.lista.selection_clear(0, "end")
        self.view_frame.pack_forget()
        self.form_frame.pack(fill="both", expand=True)

        self.titulo_entry.delete(0, "end")
        self._limpiar_filas(self.ingredientes_container, self.ingrediente_filas)
        self._limpiar_filas(self.pasos_container, self.paso_filas)
        self._limpiar_filas(self.imagenes_container, self.imagen_filas)
        self.agregar_ingrediente()
        self.agregar_paso()

    def mostrar_vista(self, receta):
        self.form_frame.pack_forget()
        self.view_frame.pack(fill="both", expand=True)

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
                self.vista_texto.insert("end", f"• {texto}\n", "cuerpo")

        pasos = receta.get("pasos") or []
        if pasos:
            self.vista_texto.insert("end", "\nPasos\n", "seccion")
            for numero, paso in enumerate(pasos, start=1):
                self.vista_texto.insert("end", f"{numero}. {paso}\n", "cuerpo")

        imagenes = receta.get("imagenes") or []
        if imagenes:
            self.vista_texto.insert("end", "\nImágenes\n", "seccion")
            for ruta in imagenes:
                self.vista_texto.insert("end", f"• {ruta}\n", "cuerpo")

        self.vista_texto.config(state="disabled")

    def refrescar_lista(self):
        self.recetas = cargar_recetas()
        self.lista.delete(0, "end")
        for receta in self.recetas:
            self.lista.insert("end", receta.get("titulo", "(sin título)"))

    def on_seleccionar(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        self.mostrar_vista(self.recetas[seleccion[0]])

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

        if not guardar_receta(receta):
            self.estado_label.config(fg="red")
            self.estado.set("El título es obligatorio.")
            return

        self.estado_label.config(fg="green")
        self.estado.set("Receta guardada.")
        self.root.after(2000, lambda: self.estado.set(""))
        self.refrescar_lista()
        self.mostrar_formulario()
