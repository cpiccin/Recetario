import tkinter as tk


class BuscarTab:
    def __init__(self, parent):
        self.parent = parent
        tk.Label(parent, text="Buscador en construcción", fg="gray").pack(expand=True)
