from tkinter import filedialog, messagebox, ttk

from storage import exportar_datos, importar_datos


class SesionTab:
    def __init__(self, parent, on_importado=None):
        self.parent = parent
        self.on_importado = on_importado

        panel = ttk.Frame(parent, style="Panel.TFrame")
        panel.pack(fill="both", expand=True)

        contenido = ttk.Frame(panel, style="Panel.TFrame")
        contenido.pack(fill="both", expand=True, padx=16, pady=16)

        ttk.Label(contenido, text="Tus datos", style="Seccion.TLabel").pack(anchor="w", pady=(0, 12))

        ttk.Label(
            contenido,
            text="Exportar",
            style="Panel.TLabel",
            font=("Verdana", 10, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            contenido,
            text=(
                "Guardá todas tus recetas y sus imágenes en un archivo .zip, para tener una copia "
                "de seguridad o pasarlas a otra computadora."
            ),
            style="Panel.TLabel",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(4, 8))
        ttk.Button(contenido, text="Exportar mis recetas...", command=self.on_exportar).pack(
            anchor="w", pady=(0, 24)
        )

        ttk.Label(
            contenido,
            text="Importar",
            style="Panel.TLabel",
            font=("Verdana", 10, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            contenido,
            text=(
                "Elegí un .zip exportado por esta app (con imágenes) o un .json con recetas ya "
                "guardadas. Se agregan a las que ya tenés, no se borra nada."
            ),
            style="Panel.TLabel",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(4, 8))
        ttk.Button(contenido, text="Importar recetas...", command=self.on_importar).pack(anchor="w")

    def on_exportar(self):
        ruta = filedialog.asksaveasfilename(
            title="Exportar recetas",
            defaultextension=".zip",
            filetypes=[("Copia de seguridad", "*.zip")],
            initialfile="recetario_backup.zip",
            parent=self.parent,
        )
        if not ruta:
            return
        try:
            exportar_datos(ruta)
        except Exception as error:
            messagebox.showerror("Exportar", f"No se pudo exportar:\n{error}", parent=self.parent)
            return
        messagebox.showinfo("Exportar", f"Copia guardada en:\n{ruta}", parent=self.parent)

    def on_importar(self):
        ruta = filedialog.askopenfilename(
            title="Importar recetas",
            filetypes=[("Recetas o copia de seguridad", "*.zip *.json")],
            parent=self.parent,
        )
        if not ruta:
            return
        try:
            cantidad = importar_datos(ruta)
        except Exception as error:
            messagebox.showerror("Importar", f"No se pudo importar:\n{error}", parent=self.parent)
            return

        if self.on_importado:
            self.on_importado()

        plural = "s" if cantidad != 1 else ""
        messagebox.showinfo(
            "Importar", f"Se importaron {cantidad} receta{plural}.", parent=self.parent
        )
