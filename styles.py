from tkinter import ttk

BG = "#FBF7F2"
BG_PANEL = "#FFFFFF"
TEXT = "#3A2E2A"
TEXT_MUTED = "#8A7A73"
ACCENT = "#D96C4F"
ACCENT_DARK = "#B8543A"
ACCENT_LIGHT = "#F3D9CE"
BORDER = "#E7DDD5"
ERROR = "#C0392B"
EXITO = "#4C8C5C"

FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_TITULO = (FONT_FAMILY, 20, "bold")
FONT_SECCION = (FONT_FAMILY, 12, "bold")
FONT_PEQUENA = (FONT_FAMILY, 9)


def aplicar_estilo(root):
    root.configure(bg=BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=BG_PANEL)

    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_NORMAL)
    style.configure("Panel.TLabel", background=BG_PANEL, foreground=TEXT, font=FONT_NORMAL)
    style.configure("Titulo.TLabel", background=BG, foreground=TEXT, font=FONT_TITULO)
    style.configure("Seccion.TLabel", background=BG_PANEL, foreground=ACCENT_DARK, font=FONT_SECCION)
    style.configure("Muted.TLabel", background=BG_PANEL, foreground=TEXT_MUTED, font=FONT_PEQUENA)

    style.configure(
        "TButton",
        background=ACCENT,
        foreground="white",
        font=FONT_BOLD,
        padding=(14, 8),
        borderwidth=0,
        focuscolor=ACCENT,
    )
    style.map(
        "TButton",
        background=[("active", ACCENT_DARK), ("disabled", BORDER)],
        foreground=[("disabled", TEXT_MUTED)],
    )

    style.configure(
        "Secundario.TButton",
        background=BG_PANEL,
        foreground=ACCENT_DARK,
        font=FONT_NORMAL,
        padding=(10, 5),
        borderwidth=1,
        relief="solid",
    )
    style.map(
        "Secundario.TButton",
        background=[("active", ACCENT_LIGHT)],
        bordercolor=[("!disabled", ACCENT_LIGHT)],
    )

    style.configure(
        "Quitar.TButton",
        background=BG_PANEL,
        foreground=TEXT_MUTED,
        font=FONT_BOLD,
        padding=(4, 0),
        borderwidth=0,
    )
    style.map("Quitar.TButton", foreground=[("active", ERROR)])

    style.configure(
        "TEntry",
        fieldbackground="white",
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=6,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    style.configure("TRadiobutton", background=BG, foreground=TEXT, font=FONT_NORMAL)
    style.map("TRadiobutton", background=[("active", BG)], foreground=[("active", ACCENT_DARK)])

    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(10, 10, 10, 0))
    style.configure(
        "TNotebook.Tab",
        background=BG,
        foreground=TEXT_MUTED,
        font=FONT_BOLD,
        padding=(18, 10),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG_PANEL)],
        foreground=[("selected", ACCENT_DARK)],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=BORDER,
        troughcolor=BG,
        arrowsize=12,
        borderwidth=0,
        relief="flat",
    )
    style.map("Vertical.TScrollbar", background=[("active", ACCENT_LIGHT)])

    return style


def estilizar_listbox(listbox):
    listbox.configure(
        bg=BG_PANEL,
        fg=TEXT,
        font=FONT_NORMAL,
        selectbackground=ACCENT,
        selectforeground="white",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        activestyle="none",
    )


def agregar_hover_listbox(listbox):
    estado = {"indice": None}

    def limpiar(indice):
        if indice is not None:
            listbox.itemconfig(indice, background=BG_PANEL, foreground=TEXT)

    def on_motion(event):
        if listbox.size() == 0:
            return
        indice = listbox.nearest(event.y)
        if indice != estado["indice"]:
            limpiar(estado["indice"])
            listbox.itemconfig(indice, background=ACCENT_LIGHT, foreground=ACCENT_DARK)
            estado["indice"] = indice

    def on_leave(event):
        limpiar(estado["indice"])
        estado["indice"] = None

    listbox.bind("<Motion>", on_motion)
    listbox.bind("<Leave>", on_leave)


def estilizar_texto(texto):
    texto.configure(
        bg=BG_PANEL,
        fg=TEXT,
        font=FONT_NORMAL,
        borderwidth=0,
        highlightthickness=0,
        padx=4,
        pady=4,
    )
