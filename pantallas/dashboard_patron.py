import tkinter as tk

from constantes import *
from .base import FrameBase
from .lazy import FrameMenuAdmin


PANEL = "#FFFFFF"
BORDE = "#D1D5DB"
MUTED = "#6B7280"
VERDE = "#0F766E"
AZUL = "#2563EB"
MORADO = "#7C3AED"
NARANJA = "#F59E0B"


class FrameDashboardPatron(FrameBase):
    def configurar(self):
        contenedor = tk.Frame(self, bg=BG)
        contenedor.pack(fill="both", expand=True, padx=16, pady=12)

        self.crear_header(contenedor)

        grid = tk.Frame(contenedor, bg=BG)
        grid.pack(fill="both", expand=True, pady=(10, 0))

        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="dash")
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)

        self.crear_tarjeta_eventos(grid).grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.crear_tarjeta_socioeconomico(grid).grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.crear_tarjeta_propinas(grid).grid(row=0, column=2, sticky="nsew", padx=6, pady=6)
        self.crear_tarjeta_opiniones(grid).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.crear_tarjeta_resumen(grid).grid(row=1, column=2, sticky="nsew", padx=6, pady=6)

    def crear_header(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x")

        marca = tk.Frame(frame, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
        marca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        logo = tk.Canvas(marca, width=56, height=56, bg=PANEL, highlightthickness=0)
        logo.pack(side="left", padx=12, pady=10)
        logo.create_oval(8, 8, 48, 48, fill=VERDE, outline="")
        logo.create_text(28, 28, text="S", fill="white", font=("Arial", 20, "bold"))
        tk.Label(marca, text="Sistema Salon", font=("Arial", 18, "bold"), bg=PANEL, fg=TXT).pack(anchor="w", pady=(12, 0))
        tk.Label(marca, text="Dashboard general del patron", font=("Arial", 10), bg=PANEL, fg=MUTED).pack(anchor="w")

        acciones = tk.Frame(frame, bg=BG)
        acciones.pack(side="right")
        tk.Button(acciones, text="Volver al menu", command=lambda: self.volver(FrameMenuAdmin),
                  bg="#777", fg="white", activebackground="#777", activeforeground="white",
                  relief="flat", width=18, height=2, cursor="hand2").pack()

    def tarjeta(self, parent, titulo, subtitulo=None):
        frame = tk.Frame(parent, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
        tk.Label(frame, text=titulo, font=("Arial", 12, "bold"), bg=PANEL, fg=TXT).pack(anchor="w", padx=12, pady=(10, 0))
        if subtitulo:
            tk.Label(frame, text=subtitulo, font=("Arial", 9), bg=PANEL, fg=MUTED).pack(anchor="w", padx=12, pady=(2, 6))
        return frame

    def crear_tarjeta_eventos(self, parent):
        frame = self.tarjeta(parent, "Eventos realizados", "Ultimos 6 meses")
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_linea_placeholder(canvas, AZUL)
        tk.Label(frame, text="Aun no hay datos para mostrar", font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_socioeconomico(self, parent):
        frame = self.tarjeta(parent, "Nivel socioeconomico", "Promedio mensual estimado")
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_barras_placeholder(canvas, MORADO)
        tk.Label(frame, text="Aun no hay datos para mostrar", font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_propinas(self, parent):
        frame = self.tarjeta(parent, "Propinas aproximadas", "Tendencia acumulada")
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_linea_placeholder(canvas, VERDE)
        tk.Label(frame, text="Aun no hay datos para mostrar", font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_opiniones(self, parent):
        frame = self.tarjeta(parent, "Opiniones y tendencias", "Salon y patron, sin senalar personas")
        cuerpo = tk.Frame(frame, bg=PANEL)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=8)

        columnas = [("Tendencias positivas", VERDE), ("Alertas generales", NARANJA)]
        for titulo, color in columnas:
            col = tk.Frame(cuerpo, bg="#F9FAFB", highlightbackground="#E5E7EB", highlightthickness=1)
            col.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(col, text=titulo, font=("Arial", 10, "bold"), bg="#F9FAFB", fg=color).pack(anchor="w", padx=10, pady=(8, 4))
            tk.Label(col, text="Aun no hay datos para mostrar", font=("Arial", 9), bg="#F9FAFB", fg=MUTED,
                     wraplength=260, justify="left").pack(anchor="w", padx=10, pady=(0, 8))
        return frame

    def crear_tarjeta_resumen(self, parent):
        frame = self.tarjeta(parent, "Resumen del salon", "Indicadores pendientes")
        indicadores = [
            ("Eventos analizados", "--"),
            ("Promedio socioeconomico", "--"),
            ("Propina promedio", "--"),
            ("Opinion general", "--"),
        ]
        for etiqueta, valor in indicadores:
            fila = tk.Frame(frame, bg=PANEL)
            fila.pack(fill="x", padx=12, pady=5)
            tk.Label(fila, text=etiqueta, font=("Arial", 9), bg=PANEL, fg=MUTED).pack(side="left")
            tk.Label(fila, text=valor, font=("Arial", 11, "bold"), bg=PANEL, fg=TXT).pack(side="right")
        tk.Label(frame, text="Aun no hay datos para mostrar", font=("Arial", 9), bg=PANEL, fg=MUTED).pack(anchor="w", padx=12, pady=(12, 0))
        return frame

    def dibujar_linea_placeholder(self, canvas, color):
        canvas.update_idletasks()
        w = max(canvas.winfo_width(), 260)
        h = max(canvas.winfo_height(), 120)
        puntos = [(18, h - 28), (58, h - 52), (102, h - 44), (148, h - 74), (198, h - 60), (244, h - 90)]
        canvas.create_line(16, h - 20, w - 16, h - 20, fill="#E5E7EB")
        canvas.create_line(16, 18, 16, h - 20, fill="#E5E7EB")
        for i in range(len(puntos) - 1):
            canvas.create_line(*puntos[i], *puntos[i + 1], fill=color, width=3)
        for x, y in puntos:
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="")

    def dibujar_barras_placeholder(self, canvas, color):
        canvas.update_idletasks()
        h = max(canvas.winfo_height(), 120)
        alturas = [42, 66, 54, 78, 60, 88]
        x = 24
        for altura in alturas:
            canvas.create_rectangle(x, h - 22 - altura, x + 22, h - 22, fill=color, outline="")
            x += 38
        canvas.create_line(16, h - 20, 270, h - 20, fill="#E5E7EB")
