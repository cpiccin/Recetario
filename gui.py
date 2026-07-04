import tkinter as tk

from storage import guardar_receta


class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recetario")
        self.root.geometry("500x400")

        self.guardar_btn = tk.Button(root, text="Guardar", command=self.on_guardar)
        self.guardar_btn.pack(side="bottom", pady=(0, 10))

        self.estado = tk.StringVar()
        self.estado_label = tk.Label(root, textvariable=self.estado, fg="green")
        self.estado_label.pack(side="bottom")

        self.texto_box = tk.Text(root, wrap="word", width=1, height=1)
        self.texto_box.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    def on_guardar(self):
        guardar_receta(self.texto_box.get("1.0", "end"))
        self.texto_box.delete("1.0", "end")
        self.estado.set("Receta guardada.")
        self.root.after(2000, lambda: self.estado.set(""))
