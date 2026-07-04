import tkinter as tk
from tkinter import ttk

from agregar_tab import AgregarTab
from buscar_tab import BuscarTab
from recetas_tab import RecetasTab
from styles import aplicar_estilo


def main():
    root = tk.Tk()
    root.title("Recetario")
    root.geometry("1100x780")
    root.minsize(650, 450)

    aplicar_estilo(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=12, pady=12)

    recetas_frame = ttk.Frame(notebook)
    agregar_frame = ttk.Frame(notebook)
    buscar_frame = ttk.Frame(notebook)

    notebook.add(recetas_frame, text="Recetas")
    notebook.add(agregar_frame, text="Agregar/Editar")
    notebook.add(buscar_frame, text="Buscar")

    def ir_a_editar(receta, indice):
        agregar_tab.cargar_receta(receta, indice)
        notebook.select(agregar_frame)

    def on_receta_guardada():
        recetas_tab.refrescar_lista()

    def ir_a_receta(indice):
        recetas_tab.seleccionar_indice(indice)
        notebook.select(recetas_frame)

    recetas_tab = RecetasTab(recetas_frame, on_editar=ir_a_editar)
    agregar_tab = AgregarTab(agregar_frame, on_guardado=on_receta_guardada)
    BuscarTab(buscar_frame, on_seleccionar=ir_a_receta)

    root.mainloop()


if __name__ == "__main__":
    main()
