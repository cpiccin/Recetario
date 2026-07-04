import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from storage import BASE_DIR, cargar_recetas
from styles import (
    ACCENT,
    BG_PANEL,
    BORDER,
    FONT_BOLD,
    FONT_TITULO,
    agregar_hover_listbox,
    estilizar_listbox,
    habilitar_scroll_rueda,
)


class RecetasTab:
    def __init__(self, parent, on_editar):
        self.parent = parent
        self.on_editar = on_editar

        self.recetas = []
        self.imagenes_referencias = []
        self.receta_actual_indice = None

        list_frame = ttk.Frame(parent, style="Panel.TFrame")
        list_frame.pack(side="left", fill="y", padx=(0, 12), pady=0)

        inner_list = ttk.Frame(list_frame, style="Panel.TFrame")
        inner_list.pack(fill="both", expand=True, padx=12, pady=12)

        scrollbar = ttk.Scrollbar(inner_list)
        scrollbar.pack(side="right", fill="y")

        self.lista = tk.Listbox(inner_list, width=26, yscrollcommand=scrollbar.set)
        estilizar_listbox(self.lista)
        agregar_hover_listbox(self.lista)
        self.lista.pack(side="left", fill="both", expand=True)
        self.lista.bind("<<ListboxSelect>>", self.on_seleccionar)
        scrollbar.config(command=self.lista.yview)

        right_frame = ttk.Frame(parent, style="Panel.TFrame")
        right_frame.pack(side="left", fill="both", expand=True)

        toolbar = ttk.Frame(right_frame, style="Panel.TFrame")
        toolbar.pack(side="top", fill="x", padx=16, pady=(12, 0))
        self.editar_btn = ttk.Button(
            toolbar, text="Editar", command=self.on_editar_click, state="disabled"
        )
        self.editar_btn.pack(side="right")

        vista_area = ttk.Frame(right_frame, style="Panel.TFrame")
        vista_area.pack(fill="both", expand=True)

        self.vista_canvas = tk.Canvas(vista_area, borderwidth=0, highlightthickness=0, bg=BG_PANEL)
        self.vista_canvas.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=12)
        vista_scrollbar = ttk.Scrollbar(vista_area, orient="vertical", command=self.vista_canvas.yview)
        vista_scrollbar.pack(side="right", fill="y", padx=(0, 4), pady=12)
        self.vista_canvas.configure(yscrollcommand=vista_scrollbar.set)
        habilitar_scroll_rueda(self.vista_canvas)

        self.vista_inner = ttk.Frame(self.vista_canvas, style="Panel.TFrame")
        self.vista_canvas.create_window((0, 0), window=self.vista_inner, anchor="nw")
        self.vista_inner.bind(
            "<Configure>",
            lambda e: self.vista_canvas.configure(scrollregion=self.vista_canvas.bbox("all")),
        )

        self.refrescar_lista()

    def _cargar_lista(self):
        self.recetas = cargar_recetas()
        self.lista.delete(0, "end")
        for receta in self.recetas:
            self.lista.insert("end", receta.get("titulo", "(sin título)"))

    def _limpiar_vista(self):
        for widget in self.vista_inner.winfo_children():
            widget.destroy()
        self.imagenes_referencias.clear()

    def _mostrar_mensaje_vacio(self):
        ttk.Label(
            self.vista_inner,
            text="Elegí una receta de la lista para verla acá.",
            style="Muted.TLabel",
        ).pack(anchor="w", padx=(0, 16), pady=20)

    def refrescar_lista(self):
        self._cargar_lista()

        self.receta_actual_indice = None
        self.editar_btn.config(state="disabled")
        self._limpiar_vista()
        self._mostrar_mensaje_vacio()

    def seleccionar_indice(self, indice):
        self._cargar_lista()
        self.lista.selection_clear(0, "end")
        self.lista.selection_set(indice)
        self.lista.see(indice)
        self.receta_actual_indice = indice
        self.mostrar_vista(self.recetas[indice])
        self.editar_btn.config(state="normal")

    def on_seleccionar(self, event):
        seleccion = self.lista.curselection()
        if not seleccion:
            return
        indice = seleccion[0]
        self.receta_actual_indice = indice
        self.mostrar_vista(self.recetas[indice])
        self.editar_btn.config(state="normal")

    def _separador(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=14, padx=(0, 16))

    def _mostrar_imagen(self, parent, ruta, maximo=300, lado=None):
        try:
            imagen = Image.open(BASE_DIR / ruta)
            imagen.thumbnail((maximo, maximo))
            foto = ImageTk.PhotoImage(imagen)
            self.imagenes_referencias.append(foto)
            label = tk.Label(parent, image=foto, bg=BG_PANEL, borderwidth=0)
            if lado:
                label.pack(side=lado, padx=(0, 8), pady=(0, 8))
            else:
                label.pack(anchor="w", padx=(0, 16), pady=(10, 0))
        except (FileNotFoundError, OSError):
            ttk.Label(parent, text=f"(no se pudo cargar {ruta})", style="Muted.TLabel").pack(
                anchor="w", padx=(0, 16)
            )

    def mostrar_vista(self, receta):
        self._limpiar_vista()
        inner = self.vista_inner

        ttk.Label(inner, text=receta.get("titulo", ""), style="Panel.TLabel", font=FONT_TITULO).pack(
            anchor="w", padx=(0, 16)
        )

        ingredientes = receta.get("ingredientes") or []
        pasos = receta.get("pasos") or []
        imagenes = receta.get("imagenes") or []

        resumen = []
        if ingredientes:
            resumen.append(f"{len(ingredientes)} ingrediente{'s' if len(ingredientes) != 1 else ''}")
        if pasos:
            resumen.append(f"{len(pasos)} paso{'s' if len(pasos) != 1 else ''}")
        if resumen:
            ttk.Label(inner, text="  ·  ".join(resumen), style="Muted.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(2, 0)
            )

        if ingredientes:
            self._separador(inner)
            ttk.Label(inner, text="Ingredientes", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            for item in ingredientes:
                fila = ttk.Frame(inner, style="Panel.TFrame")
                fila.pack(fill="x", padx=(0, 16), pady=2)
                ttk.Label(fila, text="•", style="Panel.TLabel", foreground=ACCENT, font=FONT_BOLD).pack(
                    side="left"
                )
                cantidad = item.get("cantidad", "").strip()
                if cantidad:
                    ttk.Label(fila, text=cantidad, style="Panel.TLabel", font=FONT_BOLD, width=10).pack(
                        side="left", padx=(8, 0)
                    )
                ttk.Label(fila, text=item.get("nombre", ""), style="Panel.TLabel").pack(
                    side="left", padx=(0 if cantidad else 8, 0)
                )

        if pasos:
            self._separador(inner)
            ttk.Label(inner, text="Pasos", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            for numero, paso in enumerate(pasos, start=1):
                fila = ttk.Frame(inner, style="Panel.TFrame")
                fila.pack(fill="x", padx=(0, 16), pady=4)
                tk.Label(fila, text=str(numero), bg=ACCENT, fg="white", font=FONT_BOLD, width=2).pack(
                    side="left", anchor="n"
                )
                ttk.Label(fila, text=paso, style="Panel.TLabel", wraplength=460, justify="left").pack(
                    side="left", padx=(10, 0), fill="x", expand=True
                )

        if imagenes:
            self._separador(inner)
            ttk.Label(inner, text="Imágenes", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            self._mostrar_imagen(inner, imagenes[0], maximo=420)
            if len(imagenes) > 1:
                galeria = ttk.Frame(inner, style="Panel.TFrame")
                galeria.pack(fill="x", padx=(0, 16), pady=(10, 0))
                for ruta in imagenes[1:]:
                    self._mostrar_imagen(galeria, ruta, maximo=120, lado="left")

        tk.Frame(inner, bg=BG_PANEL, height=20).pack()

    def on_editar_click(self):
        if self.receta_actual_indice is None:
            return
        self.on_editar(self.recetas[self.receta_actual_indice], self.receta_actual_indice)
