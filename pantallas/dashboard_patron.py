import datetime
import re
import tkinter as tk

from constantes import *
from datos import GestorArchivos
from .base import FrameBase
from .lazy import FrameMenuAdmin


PANEL = "#FFFFFF"
BORDE = "#D1D5DB"
MUTED = "#6B7280"
VERDE = "#0F766E"
AZUL = "#2563EB"
MORADO = "#7C3AED"
NARANJA = "#F59E0B"
ROJO = "#DC2626"


MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def parse_fecha_evento(valor):
    for formato in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(str(valor), formato).date()
        except ValueError:
            continue
    return None


def numero_desde_texto(valor):
    texto = re.sub(r"[^\d,.\-]", "", str(valor or ""))
    if "," in texto and "." in texto:
        texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        texto = texto.replace(",", ".") if len(partes[-1]) == 2 else texto.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", texto)
    if not match:
        return 0.0
    try:
        return float(match.group(0))
    except ValueError:
        return 0.0


def moneda(valor):
    return f"${valor:,.2f}"


class FrameDashboardPatron(FrameBase):
    def configurar(self):
        self.hoy = datetime.date.today()
        self.salones = GestorArchivos.cargar_salones()
        self.salon = self.salones[0] if self.salones else None
        self.eventos = GestorArchivos.cargar_eventos()
        self.comentarios = self.cargar_comentarios()
        self.resultados_analizador = GestorArchivos.cargar_resultados_analizador()
        self.resumen_reposicion = GestorArchivos.resumen_reposicion_inventario()
        self.meses = self.ultimos_seis_meses()
        self.metricas = self.calcular_metricas()

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

    def ultimos_seis_meses(self):
        meses = []
        base = datetime.date(self.hoy.year, self.hoy.month, 1)
        for i in range(5, -1, -1):
            mes_total = base.month - 1 - i
            anio = base.year + mes_total // 12
            mes = mes_total % 12 + 1
            meses.append((anio, mes))
        return meses

    def cargar_comentarios(self):
        comentarios = []
        try:
            comentarios.extend([dict(c, fuente="general") for c in GestorArchivos.cargar_comentarios()])
        except Exception:
            pass
        try:
            comentarios.extend([dict(c.to_dict(), fuente="mesero") for c in GestorArchivos.cargar_comentarios_mesero()])
        except Exception:
            pass
        try:
            comentarios.extend([dict(c.to_dict(), fuente="evento") for c in GestorArchivos.cargar_comentarios_evento()])
        except Exception:
            pass
        return comentarios

    def calcular_metricas(self):
        eventos_mes = {mes: 0 for mes in self.meses}
        invitados_mes = {mes: 0 for mes in self.meses}
        propinas_mes = {mes: 0.0 for mes in self.meses}
        comentarios_mes = {mes: [] for mes in self.meses}

        fechas_eventos = {}
        for evento in self.eventos:
            fecha = parse_fecha_evento(evento.fecha)
            if not fecha:
                continue
            clave = (fecha.year, fecha.month)
            fechas_eventos[evento.fecha] = fecha
            if clave in eventos_mes:
                eventos_mes[clave] += 1
                invitados_mes[clave] += evento.total_invitados()

        for comentario in self.comentarios:
            fecha = fechas_eventos.get(comentario.get("fecha")) or parse_fecha_evento(comentario.get("fecha"))
            if not fecha:
                continue
            clave = (fecha.year, fecha.month)
            if clave not in propinas_mes:
                continue
            propina = numero_desde_texto(comentario.get("ganancia") or comentario.get("ganancia_total"))
            propinas_mes[clave] += propina
            comentarios_mes[clave].append(comentario)

        calificaciones = []
        buenos = neutrales = malos = 0
        textos = []
        for comentario in self.comentarios:
            calificacion = numero_desde_texto(comentario.get("calificacion") or comentario.get("calificacion_promedio"))
            if calificacion > 0:
                calificaciones.append(calificacion)
                if calificacion >= 4:
                    buenos += 1
                elif calificacion >= 3:
                    neutrales += 1
                else:
                    malos += 1
            for campo in ("sentir", "observaciones", "reporte", "satisfaccion_general"):
                texto = str(comentario.get(campo, "")).strip()
                if texto and texto.lower() not in {"n/a", "na", "ninguno"}:
                    textos.append(texto)

        total_propinas = sum(propinas_mes.values())
        total_comentarios = len(self.comentarios)
        calificacion_promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

        return {
            "eventos_mes": eventos_mes,
            "invitados_mes": invitados_mes,
            "propinas_mes": propinas_mes,
            "comentarios_mes": comentarios_mes,
            "total_eventos": len(self.eventos),
            "eventos_6m": sum(eventos_mes.values()),
            "total_propinas": total_propinas,
            "total_comentarios": total_comentarios,
            "calificacion_promedio": calificacion_promedio,
            "buenos": buenos,
            "neutrales": neutrales,
            "malos": malos,
            "textos": textos[:6],
        }

    def crear_header(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x")

        marca = tk.Frame(frame, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
        marca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        logo = tk.Canvas(marca, width=56, height=56, bg=PANEL, highlightthickness=0)
        logo.pack(side="left", padx=12, pady=10)
        nombre = self.salon.nombre if self.salon else "Sistema Salon"
        inicial = (nombre[:1] or "S").upper()
        logo.create_oval(8, 8, 48, 48, fill=VERDE, outline="")
        logo.create_text(28, 28, text=inicial, fill="white", font=("Arial", 20, "bold"))

        datos = tk.Frame(marca, bg=PANEL)
        datos.pack(side="left", fill="x", expand=True)
        tk.Label(datos, text=nombre, font=("Arial", 18, "bold"), bg=PANEL, fg=TXT).pack(anchor="w", pady=(10, 0))
        subtitulo = "Dashboard general del patron"
        if self.salon and (self.salon.zona or self.salon.telefono):
            subtitulo = " | ".join([v for v in [self.salon.zona, self.salon.telefono, self.salon.correo] if v])
        tk.Label(datos, text=subtitulo, font=("Arial", 10), bg=PANEL, fg=MUTED).pack(anchor="w")
        if self.salon and (self.salon.precio_base or self.salon.precio_por_persona):
            tk.Label(datos, text=f"Precio aprox: base {moneda(self.salon.precio_base)} + {moneda(self.salon.precio_por_persona)} por persona",
                     font=("Arial", 9), bg=PANEL, fg=MUTED).pack(anchor="w")

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

    def etiquetas_meses(self):
        return [MESES[mes - 1] for _, mes in self.meses]

    def crear_tarjeta_eventos(self, parent):
        frame = self.tarjeta(parent, "Eventos realizados", "Ultimos 6 meses")
        valores = [self.metricas["eventos_mes"][mes] for mes in self.meses]
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_linea(canvas, valores, AZUL)
        tk.Label(frame, text=f"{self.metricas['eventos_6m']} evento(s) en 6 meses | {self.metricas['total_eventos']} historicos",
                 font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_socioeconomico(self, parent):
        frame = self.tarjeta(parent, "Nivel socioeconomico", "Estimado por propinas registradas")
        valores = [self.estimar_socio(self.metricas["propinas_mes"][mes], self.metricas["comentarios_mes"][mes]) for mes in self.meses]
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_barras(canvas, valores, MORADO)
        texto = "Sin datos suficientes"
        if max(valores or [0]) > 0:
            texto = "Escala 1 bajo, 2 medio, 3 alto"
        tk.Label(frame, text=texto, font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_propinas(self, parent):
        frame = self.tarjeta(parent, "Propinas aproximadas", "Tendencia acumulada")
        valores = [self.metricas["propinas_mes"][mes] for mes in self.meses]
        canvas = tk.Canvas(frame, height=145, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        self.dibujar_linea(canvas, valores, VERDE)
        tk.Label(frame, text=f"Total registrado: {moneda(self.metricas['total_propinas'])}" if self.metricas["total_propinas"] else "Sin propinas registradas",
                 font=("Arial", 9), bg=PANEL, fg=MUTED).pack(pady=(0, 10))
        return frame

    def crear_tarjeta_opiniones(self, parent):
        frame = self.tarjeta(parent, "Opiniones y analizador", "Salon y patron, sin senalar personas")
        cuerpo = tk.Frame(frame, bg=PANEL)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=8)

        izquierda = tk.Frame(cuerpo, bg="#F9FAFB", highlightbackground="#E5E7EB", highlightthickness=1)
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 5))
        derecha = tk.Frame(cuerpo, bg="#F9FAFB", highlightbackground="#E5E7EB", highlightthickness=1)
        derecha.pack(side="left", fill="both", expand=True, padx=(5, 0))

        tk.Label(izquierda, text="Comentarios capturados", font=("Arial", 10, "bold"), bg="#F9FAFB", fg=VERDE).pack(anchor="w", padx=10, pady=(8, 4))
        self.fila_texto(izquierda, f"Buenos: {self.metricas['buenos']} | Neutrales: {self.metricas['neutrales']} | Malos: {self.metricas['malos']}")
        if self.metricas["calificacion_promedio"]:
            self.fila_texto(izquierda, f"Calificacion promedio: {self.metricas['calificacion_promedio']:.1f}/5")
        for texto in self.metricas["textos"][:3]:
            self.fila_texto(izquierda, f"- {texto}")
        if not self.metricas["textos"]:
            self.fila_texto(izquierda, "Sin comentarios registrados.")

        tk.Label(derecha, text="Resultados del analizador", font=("Arial", 10, "bold"), bg="#F9FAFB", fg=NARANJA).pack(anchor="w", padx=10, pady=(8, 4))
        if self.resultados_analizador:
            for resultado in self.resultados_analizador[-4:]:
                resumen = resultado.resumen or resultado.sentimiento or "Resultado sin resumen"
                self.fila_texto(derecha, f"- {resultado.entidad_tipo}: {resumen}")
        else:
            self.fila_texto(derecha, "Aun no hay resultados del analizador.")
            self.fila_texto(derecha, "Cuando lo conectes, se mostraran tendencias agregadas aqui.")
        return frame

    def crear_tarjeta_resumen(self, parent):
        frame = self.tarjeta(parent, "Resumen del salon", "Indicadores operativos")
        indicadores = [
            ("Eventos historicos", str(self.metricas["total_eventos"])),
            ("Comentarios", str(self.metricas["total_comentarios"])),
            ("Propina total", moneda(self.metricas["total_propinas"]) if self.metricas["total_propinas"] else "--"),
            ("Reposicion prom.", moneda(self.resumen_reposicion["promedio"]) if self.resumen_reposicion["total_comparaciones"] else "--"),
            ("Comparaciones inv.", str(self.resumen_reposicion["total_comparaciones"])),
            ("Analizador", str(len(self.resultados_analizador))),
        ]
        for etiqueta, valor in indicadores:
            fila = tk.Frame(frame, bg=PANEL)
            fila.pack(fill="x", padx=12, pady=5)
            tk.Label(fila, text=etiqueta, font=("Arial", 9), bg=PANEL, fg=MUTED).pack(side="left")
            tk.Label(fila, text=valor, font=("Arial", 11, "bold"), bg=PANEL, fg=TXT).pack(side="right")
        return frame

    def fila_texto(self, parent, texto):
        tk.Label(parent, text=texto, font=("Arial", 9), bg="#F9FAFB", fg="#555",
                 wraplength=380, justify="left").pack(anchor="w", padx=10, pady=2)

    def estimar_socio(self, total_propinas, comentarios):
        if not comentarios:
            return 0
        promedio = total_propinas / len(comentarios)
        if promedio >= 800:
            return 3
        if promedio >= 400:
            return 2
        if promedio > 0:
            return 1
        return 0

    def dibujar_linea(self, canvas, valores, color):
        canvas.update_idletasks()
        w = max(canvas.winfo_width(), 260)
        h = max(canvas.winfo_height(), 120)
        canvas.create_line(18, h - 24, w - 12, h - 24, fill="#E5E7EB")
        canvas.create_line(18, 16, 18, h - 24, fill="#E5E7EB")
        if not valores or max(valores) <= 0:
            canvas.create_text(w // 2, h // 2, text="Sin datos", fill=MUTED, font=("Arial", 10, "bold"))
            return
        maximo = max(valores)
        espacio = (w - 50) / max(len(valores) - 1, 1)
        puntos = []
        for i, valor in enumerate(valores):
            x = 26 + i * espacio
            y = h - 28 - ((valor / maximo) * (h - 54))
            puntos.append((x, y))
        for i in range(len(puntos) - 1):
            canvas.create_line(*puntos[i], *puntos[i + 1], fill=color, width=3)
        for (x, y), etiqueta, valor in zip(puntos, self.etiquetas_meses(), valores):
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="")
            canvas.create_text(x, h - 12, text=etiqueta, fill=MUTED, font=("Arial", 8))
            canvas.create_text(x, y - 12, text=str(int(valor)), fill=TXT, font=("Arial", 8, "bold"))

    def dibujar_barras(self, canvas, valores, color):
        canvas.update_idletasks()
        w = max(canvas.winfo_width(), 260)
        h = max(canvas.winfo_height(), 120)
        canvas.create_line(18, h - 24, w - 12, h - 24, fill="#E5E7EB")
        if not valores or max(valores) <= 0:
            canvas.create_text(w // 2, h // 2, text="Sin datos", fill=MUTED, font=("Arial", 10, "bold"))
            return
        espacio = (w - 46) / len(valores)
        for i, (valor, etiqueta) in enumerate(zip(valores, self.etiquetas_meses())):
            x1 = 26 + i * espacio
            x2 = x1 + min(28, espacio * 0.55)
            altura = (valor / 3) * (h - 52)
            canvas.create_rectangle(x1, h - 24 - altura, x2, h - 24, fill=color, outline="")
            canvas.create_text((x1 + x2) / 2, h - 12, text=etiqueta, fill=MUTED, font=("Arial", 8))
            canvas.create_text((x1 + x2) / 2, h - 30 - altura, text=str(int(valor)), fill=TXT, font=("Arial", 8, "bold"))
