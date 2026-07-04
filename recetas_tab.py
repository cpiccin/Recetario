import tkinter as tk
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageTk

from richtext import configurar_tags, insertar_html
from storage import BASE_DIR, cargar_recetas
from styles import (
    ACCENT,
    BG_PANEL,
    BORDER,
    FONT_BOLD,
    FONT_NORMAL,
    FONT_TITULO,
    TEXT,
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

    def _crear_texto_html(self, parent, html, ancho=60):
        texto = tk.Text(
            parent,
            wrap="word",
            width=ancho,
            height=1,
            font=FONT_NORMAL,
            bg=BG_PANEL,
            fg=TEXT,
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
        )
        configurar_tags(texto, FONT_NORMAL)
        insertar_html(texto, html)
        return texto

    def _ajustar_altura(self, texto):
        texto.update_idletasks()
        resultado = texto.count("1.0", "end", "displaylines")
        lineas = resultado[0] if isinstance(resultado, tuple) else (resultado or 1)
        texto.configure(height=max(lineas, 1), state="disabled")

    def _mostrar_imagen(self, parent, imagenes, indice, fila, col, tam=150):
        ruta = imagenes[indice]
        try:
            imagen = Image.open(BASE_DIR / ruta)
            imagen.thumbnail((tam, tam))
            foto = ImageTk.PhotoImage(imagen)
            self.imagenes_referencias.append(foto)
            label = tk.Label(parent, image=foto, bg=BG_PANEL, borderwidth=0, cursor="hand2")
            label.grid(row=fila, column=col, padx=(0, 8), pady=(0, 8), sticky="w")
            label.bind("<Button-1>", lambda e, i=indice: self._abrir_imagen_grande(imagenes, i))
        except (FileNotFoundError, OSError):
            ttk.Label(parent, text=f"(no se pudo cargar {ruta})", style="Muted.TLabel").grid(
                row=fila, column=col, sticky="w"
            )

    def _abrir_imagen_grande(self, imagenes, indice_inicial=0):
        estado = {"indice": indice_inicial}

        ventana = tk.Toplevel(self.parent)
        ventana.configure(bg="black")

        label = tk.Label(ventana, bg="black", cursor="hand2")
        label.pack(padx=10, pady=(10, 0))

        contador = tk.Label(ventana, bg="black", fg="white", font=FONT_NORMAL)
        contador.pack(pady=(4, 10))

        def mostrar(indice):
            estado["indice"] = indice % len(imagenes)
            ruta = imagenes[estado["indice"]]
            try:
                imagen = Image.open(BASE_DIR / ruta)
                imagen.thumbnail((900, 900))
                foto = ImageTk.PhotoImage(imagen)
            except (FileNotFoundError, OSError):
                label.config(image="", text=f"(no se pudo cargar {ruta})", fg="white")
                ventana.imagen_referencia = None
                return
            ventana.imagen_referencia = foto
            label.config(image=foto, text="")
            ventana.title(Path(ruta).name)
            contador.config(text=f"{estado['indice'] + 1} / {len(imagenes)}")

        def siguiente(event=None):
            mostrar(estado["indice"] + 1)

        def anterior(event=None):
            mostrar(estado["indice"] - 1)

        label.bind("<Button-1>", lambda e: ventana.destroy())
        ventana.bind("<Escape>", lambda e: ventana.destroy())
        ventana.bind("<Right>", siguiente)
        ventana.bind("<Left>", anterior)

        if len(imagenes) > 1:
            botones = tk.Frame(ventana, bg="black")
            botones.pack(pady=(0, 10))
            tk.Button(
                botones, text="‹ Anterior", command=anterior, bg="#333333", fg="white",
                activebackground=ACCENT, activeforeground="white", relief="flat", cursor="hand2",
            ).pack(side="left", padx=6)
            tk.Button(
                botones, text="Siguiente ›", command=siguiente, bg="#333333", fg="white",
                activebackground=ACCENT, activeforeground="white", relief="flat", cursor="hand2",
            ).pack(side="left", padx=6)

        mostrar(indice_inicial)
        ventana.focus_set()

    def mostrar_vista(self, receta):
        self._limpiar_vista()
        inner = self.vista_inner

        ttk.Label(inner, text=receta.get("titulo", ""), style="Panel.TLabel", font=FONT_TITULO).pack(
            anchor="w", padx=(0, 16)
        )

        ingredientes = receta.get("ingredientes") or []
        pasos = receta.get("pasos") or []
        notas = receta.get("notas", "").strip()
        imagenes = receta.get("imagenes") or []

        resumen = []
        if ingredientes:
            resumen.append(f"{len(ingredientes)} ingrediente{'s' if len(ingredientes) != 1 else ''}")
        if isinstance(pasos, list) and pasos:
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
                    ttk.Label(fila, text=cantidad, style="Panel.TLabel", font=FONT_BOLD).pack(
                        side="left", padx=(8, 0)
                    )
                nombre_widget = self._crear_texto_html(fila, item.get("nombre", ""), ancho=40)
                nombre_widget.pack(side="left", padx=(8, 0), fill="x", expand=True)
                self._ajustar_altura(nombre_widget)

        if pasos:
            self._separador(inner)
            ttk.Label(inner, text="Pasos", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            if isinstance(pasos, list):
                for numero, paso in enumerate(pasos, start=1):
                    fila = ttk.Frame(inner, style="Panel.TFrame")
                    fila.pack(fill="x", padx=(0, 16), pady=4)
                    tk.Label(fila, text=str(numero), bg=ACCENT, fg="white", font=FONT_BOLD, width=2).pack(
                        side="left", anchor="n"
                    )
                    paso_widget = self._crear_texto_html(fila, paso, ancho=55)
                    paso_widget.pack(side="left", padx=(10, 0), fill="x", expand=True)
                    self._ajustar_altura(paso_widget)
            else:
                pasos_widget = self._crear_texto_html(inner, pasos, ancho=64)
                pasos_widget.pack(anchor="w", fill="x", padx=(0, 16))
                self._ajustar_altura(pasos_widget)

        if notas:
            self._separador(inner)
            ttk.Label(inner, text="Notas", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            notas_widget = self._crear_texto_html(inner, notas, ancho=64)
            notas_widget.pack(anchor="w", fill="x", padx=(0, 16))
            self._ajustar_altura(notas_widget)

        if imagenes:
            self._separador(inner)
            ttk.Label(inner, text="Imágenes", style="Seccion.TLabel").pack(
                anchor="w", padx=(0, 16), pady=(0, 8)
            )
            galeria = ttk.Frame(inner, style="Panel.TFrame")
            galeria.pack(fill="x", padx=(0, 16))
            columnas = 4
            for indice in range(len(imagenes)):
                fila, col = divmod(indice, columnas)
                self._mostrar_imagen(galeria, imagenes, indice, fila, col)

        tk.Frame(inner, bg=BG_PANEL, height=20).pack()

    def on_editar_click(self):
        if self.receta_actual_indice is None:
            return
        self.on_editar(self.recetas[self.receta_actual_indice], self.receta_actual_indice)
