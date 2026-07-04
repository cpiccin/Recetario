import tkinter as tk

from storage import cargar_recetas, guardar_receta


class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recetario")
        self.root.geometry("750x500")

        self.recetas = []
        self.ingrediente_filas = []
        self.paso_filas = []

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

        tk.Label(self.form_inner, text="Imágenes (una ruta o URL por línea)").pack(anchor="w", pady=(8, 0))
        self.imagenes_box = tk.Text(self.form_inner, wrap="word", width=1, height=3)
        self.imagenes_box.pack(fill="x")

    def _agregar_fila(self, container, filas):
        fila = tk.Frame(container)
        fila.pack(fill="x", pady=2)

        entry = tk.Entry(fila)
        entry.pack(side="left", fill="x", expand=True)

        def eliminar():
            filas.remove((fila, entry))
            fila.destroy()

        tk.Button(fila, text="×", command=eliminar, width=2).pack(side="left", padx=(4, 0))
        filas.append((fila, entry))
        entry.focus_set()

    def agregar_ingrediente(self):
        self._agregar_fila(self.ingredientes_container, self.ingrediente_filas)

    def agregar_paso(self):
        self._agregar_fila(self.pasos_container, self.paso_filas)

    def _limpiar_filas(self, container, filas):
        for fila, _ in filas:
            fila.destroy()
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
        self.imagenes_box.delete("1.0", "end")
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
                self.vista_texto.insert("end", f"• {item}\n", "cuerpo")

        pasos = receta.get("pasos") or []
        if pasos:
            self.vista_texto.insert("end", "\nPasos\n", "seccion")
            for numero, paso in enumerate(pasos, start=1):
                self.vista_texto.insert("end", f"{numero}. {paso}\n", "cuerpo")

        imagenes = receta.get("imagenes", "").strip()
        if imagenes:
            self.vista_texto.insert("end", "\nImágenes\n", "seccion")
            self.vista_texto.insert("end", imagenes, "cuerpo")

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
            "ingredientes": [e.get().strip() for _, e in self.ingrediente_filas if e.get().strip()],
            "pasos": [e.get().strip() for _, e in self.paso_filas if e.get().strip()],
            "imagenes": self.imagenes_box.get("1.0", "end").strip(),
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
