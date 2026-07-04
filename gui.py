import tkinter as tk

from storage import cargar_recetas, guardar_receta


class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recetario")
        self.root.geometry("750x500")

        self.recetas = []

        list_frame = tk.Frame(root)
        list_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.lista = tk.Listbox(list_frame, width=25, yscrollcommand=scrollbar.set)
        self.lista.pack(side="left", fill="y", expand=True)
        self.lista.bind("<<ListboxSelect>>", self.on_seleccionar)
        scrollbar.config(command=self.lista.yview)

        right_frame = tk.Frame(root)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

        self.guardar_btn = tk.Button(right_frame, text="Guardar", command=self.on_guardar)
        self.guardar_btn.pack(side="bottom", pady=(5, 0))

        self.estado = tk.StringVar()
        self.estado_label = tk.Label(right_frame, textvariable=self.estado, fg="green")
        self.estado_label.pack(side="bottom")

        tk.Label(right_frame, text="Título *").pack(anchor="w")
        self.titulo_entry = tk.Entry(right_frame)
        self.titulo_entry.pack(fill="x")

        tk.Label(right_frame, text="Ingredientes").pack(anchor="w", pady=(8, 0))
        self.ingredientes_box = tk.Text(right_frame, wrap="word", width=1, height=5)
        self.ingredientes_box.pack(fill="x")

        tk.Label(right_frame, text="Instrucciones").pack(anchor="w", pady=(8, 0))
        self.instrucciones_box = tk.Text(right_frame, wrap="word", width=1, height=8)
        self.instrucciones_box.pack(fill="both", expand=True)

        tk.Label(right_frame, text="Imágenes (una ruta o URL por línea)").pack(anchor="w", pady=(8, 0))
        self.imagenes_box = tk.Text(right_frame, wrap="word", width=1, height=3)
        self.imagenes_box.pack(fill="x")

        self.refrescar_lista()

    def refrescar_lista(self):
        self.recetas = cargar_recetas()
        self.lista.delete(0, "end")
        for receta in self.recetas:
            self.lista.insert("end", receta.get("titulo", "(sin título)"))

    def on_seleccionar(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        receta = self.recetas[seleccion[0]]

        self.titulo_entry.delete(0, "end")
        self.titulo_entry.insert(0, receta.get("titulo", ""))

        self.ingredientes_box.delete("1.0", "end")
        self.ingredientes_box.insert("1.0", receta.get("ingredientes", ""))

        self.instrucciones_box.delete("1.0", "end")
        self.instrucciones_box.insert("1.0", receta.get("instrucciones", ""))

        self.imagenes_box.delete("1.0", "end")
        self.imagenes_box.insert("1.0", receta.get("imagenes", ""))

    def on_guardar(self):
        receta = {
            "titulo": self.titulo_entry.get().strip(),
            "ingredientes": self.ingredientes_box.get("1.0", "end").strip(),
            "instrucciones": self.instrucciones_box.get("1.0", "end").strip(),
            "imagenes": self.imagenes_box.get("1.0", "end").strip(),
        }

        if not guardar_receta(receta):
            self.estado_label.config(fg="red")
            self.estado.set("El título es obligatorio.")
            return

        self.titulo_entry.delete(0, "end")
        self.ingredientes_box.delete("1.0", "end")
        self.instrucciones_box.delete("1.0", "end")
        self.imagenes_box.delete("1.0", "end")

        self.estado_label.config(fg="green")
        self.estado.set("Receta guardada.")
        self.root.after(2000, lambda: self.estado.set(""))
        self.refrescar_lista()
