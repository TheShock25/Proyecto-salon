import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

COLOR_PISO = "#F8FAFC"
COLOR_BORDE = "#CBD5E1"
COLOR_MESA = "#E5E7EB"
COLOR_PRINCIPAL = "#8B5E34"
COLOR_PISTA = "#111827"
COLOR_PANEL = "#FFFFFF"


def crear_boton(parent, text, command, bg=BTN, width=20):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        activebackground=bg,
        activeforeground="white",
        relief="flat",
        width=width,
        height=2,
        font=("Arial", 10, "bold"),
        cursor="hand2",
    )


class FrameCroquis(FrameBase):
    """Frame que dibuja el croquis del salón."""
    def __init__(self, master, modo="demo", fecha=None, evento=None, organizacion=None, **kwargs):
        self.modo = modo
        self.fecha = fecha
        # Solo asignar evento si realmente se proporcionó uno
        self.evento = evento if evento is not None else None
        self.organizacion = organizacion
        self.color_actual = "lightgray"
        self.total_invitados = 0
        self.mesa_principal_valor = 2
        self.valores_mesas = {}
        self.asociaciones_colores = {}
        self.mesas_colores = {}
        self.conteo_meseros = {}
        self.nombres_meseros = {}
        self.mesas_ids = {}
        super().__init__(master, **kwargs)

    def configurar(self):
        # ===== CONTENEDORES PRINCIPALES =====
        frame_main = tk.Frame(self, bg=BG)
        frame_main.pack(fill="both", expand=True, padx=18, pady=12)

        titulo = "Croquis de reservacion"
        if self.modo == "demo":
            titulo = "Demostracion de croquis"
        elif self.modo == "capitan":
            titulo = "Organizacion del evento"
        elif self.modo == "mesero":
            titulo = "Croquis para servicio"
        elif self.modo == "visualizacion":
            titulo = "Detalle del evento"

        tk.Label(frame_main, text=titulo, font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(0, 2))
        if self.fecha:
            tk.Label(frame_main, text=f"Fecha: {self.fecha}", font=("Arial", 10), bg=BG, fg="#555").pack(pady=(0, 8))

        frame_sup = tk.Frame(frame_main, bg=BG)
        frame_sup.pack(pady=6)

        frame_botones = tk.Frame(frame_main, bg=BG)
        frame_botones.pack(pady=(2, 8))
        self.configurar_botones(frame_botones)

        frame_centro = tk.Frame(frame_main, bg=BG)
        frame_centro.pack(fill="both", expand=True)

        frame_left = tk.Frame(frame_centro, bg=BG)
        frame_left.pack(side="left", padx=20)

        self.frame_right = tk.Frame(frame_centro, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1)
        self.frame_right.pack(side="left", padx=20)

        # ===== PARTE SUPERIOR =====
        if self.modo in ["demo", "anfitrion"]:
            tk.Label(frame_sup, text="Total invitados", bg=BG, fg=TXT, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 8))
            self.entry_total = tk.Entry(frame_sup, width=8, font=("Arial", 11), justify="center")
            self.entry_total.grid(row=0, column=1, padx=(0, 8))

            self.lbl_faltan = tk.Label(frame_sup, text="Personas sin acomodar: 0", bg=BG, fg="#555", font=("Arial", 10, "bold"))
            self.lbl_faltan.grid(row=1, column=0, columnspan=3, pady=(4, 0))

            crear_boton(frame_sup, text="Calcular", command=self.calcular, bg=BTN2, width=12).grid(row=0, column=2)

        # ===== CANVAS =====
        self.canvas = tk.Canvas(
            frame_left,
            width=COLUMNAS*CELL,
            height=(FILAS+1)*CELL,
            bg=COLOR_PISO,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
        )
        self.canvas.pack()

        # Dibujar elementos fijos
        self.dibujar_elementos_fijos()

        # Crear mesas (visibles por defecto)
        self.crear_todas_mesas()

        # Si hay evento cargado (desde calendario, capitán o mesero), mostrar SOLO mesas con personas
        if self.evento is not None and len(self.evento.mesas) > 0:
            self.cargar_evento_existente()
        # Si es modo anfitrión sin evento, mostrar todas las mesas (ya están visibles por defecto)
        elif self.modo == "anfitrion" and self.evento is None:
            # Ya están visibles, no hacer nada
            pass

        # ===== LADO DERECHO =====
        self.configurar_panel_derecho()

    def dibujar_elementos_fijos(self):
        """Dibuja la mesa principal y la pista."""
        # Mesa principal (siempre visible)
        self.mp = self.canvas.create_rectangle(2*CELL, 0, 4*CELL, int(CELL*0.7), fill=COLOR_PRINCIPAL, outline="#6B3F1D", width=2)
        self.texto_mp = self.canvas.create_text(3*CELL, int(CELL*0.35), 
                                                text=f"Principal\n{self.mesa_principal_valor}", 
                                                fill="white", font=("Arial", 10, "bold"))
        
        if self.modo in ["demo", "anfitrion"]:
            self.canvas.tag_bind(self.mp, "<Button-1>", self.editar_principal)

        # Pista - ocupa columnas 3 y 4, filas 1 a 3.
        self.canvas.create_rectangle(2*CELL, 1*CELL, 4*CELL, 4*CELL, fill=COLOR_PISTA, outline="#030712", width=2)
        self.canvas.create_text(3*CELL, int(2.5*CELL), text="PISTA", fill="white", font=("Arial", 12, "bold"))

    def crear_mesa(self, col, fila):
        """Crea una mesa en la posición especificada (visible por defecto)."""
        x1 = (col-1)*CELL
        y1 = fila*CELL
        x2 = x1+CELL
        y2 = y1+CELL
        
        # Crear la mesa visible por defecto
        mesa = self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=COLOR_MESA, outline="#94A3B8", width=2, state="normal")
        texto = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="0", state="normal", font=("Arial", 11, "bold"), fill=TXT)
        
        self.valores_mesas[(col, fila)] = {
            "mesa": mesa,
            "texto": texto,
            "valor": 0,
            "nombre": None,
            "color": "lightgray"
        }
        self.mesas_ids[(col, fila)] = mesa

        if self.modo in ["demo", "anfitrion"]:
            def editar(event, c=col, f=fila):
                v = simpledialog.askinteger("Mesa", "Personas (0-12):", minvalue=0, maxvalue=12)
                if v is not None:
                    self.valores_mesas[(c, f)]["valor"] = v
                    self.canvas.itemconfig(texto, text=str(v))
                    self.actualizar_contador()

            self.canvas.tag_bind(mesa, "<Button-1>", editar)

        if self.modo == "anfitrion":
            def poner_nombre(event, c=col, f=fila):
                nombre = simpledialog.askstring("Nombre", "Nombre mesa:")
                if nombre:
                    self.valores_mesas[(c, f)]["nombre"] = nombre
                    self.valores_mesas[(c, f)]["color"] = self.color_actual
                    self.canvas.itemconfig(self.valores_mesas[(c, f)]["mesa"], fill=self.color_actual)
                    self.asociaciones_colores[self.color_actual] = nombre
                    self.actualizar_leyenda()
            self.canvas.tag_bind(mesa, "<Button-3>", poner_nombre)

        return mesa, texto

    def crear_todas_mesas(self):
        """Crea todas las mesas en el canvas (visibles por defecto)."""
        for fila in range(1, FILAS+1):
            for col in range(1, COLUMNAS+1):
                if 3 <= col <= 4 and 1 <= fila <= 3:
                    continue
                self.crear_mesa(col, fila)

    def editar_principal(self, event):
        """Edita el valor de la mesa principal."""
        v = simpledialog.askinteger("Principal", "Personas (2-8):", minvalue=2, maxvalue=8)
        if v:
            self.mesa_principal_valor = v
            self.canvas.itemconfig(self.texto_mp, text=f"Principal\n{v}")
            self.actualizar_contador()

    def calcular(self):
        """Calcula la distribución automática de invitados con el orden correcto."""
        try:
            self.total_invitados = int(self.entry_total.get())
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")
            return

        restantes = self.total_invitados - self.mesa_principal_valor
        
        if restantes < 0:
            messagebox.showwarning("Advertencia", "El total de invitados es menor que la mesa principal")
            restantes = 0

        # ORDEN DE PRIORIDAD CORREGIDO:
        prioridad = [
            (2,1), (2,2), (2,3), (5,1), (5,2), (5,3),  # Alrededor pista
            (3,4), (4,4), (2,4), (5,4),                   # Fila 4
            (1,1), (6,1),                                  # Extremos fila 1
            (1,2), (6,2),                                  # Extremos fila 2
            (1,3), (6,3),                                  # Extremos fila 3
            (1,4), (6,4),                                  # Extremos fila 4
            (3,5), (4,5), (2,5), (5,5), (1,5), (6,5)      # Fila 5
        ]

        # Resetear valores de todas las mesas a 0
        for info in self.valores_mesas.values():
            info["valor"] = 0
            info["nombre"] = None
            info["color"] = "lightgray"
            self.canvas.itemconfig(info["texto"], text="0")
            self.canvas.itemconfig(info["mesa"], fill=COLOR_MESA)
            # No ocultamos las mesas, solo reseteamos sus valores

        # Asignar personas a las mesas según prioridad
        for (col, fila) in prioridad:
            if restantes <= 0:
                break
            if (col, fila) in self.valores_mesas:
                asignar = min(10, restantes)
                info = self.valores_mesas[(col, fila)]
                info["valor"] = asignar
                self.canvas.itemconfig(info["texto"], text=str(asignar))
                restantes -= asignar

        self.actualizar_contador()

    def actualizar_contador(self):
        """Actualiza el contador de personas sin acomodar."""
        if hasattr(self, 'lbl_faltan'):
            usados = self.mesa_principal_valor + sum(i["valor"] for i in self.valores_mesas.values())
            faltan = self.total_invitados - usados
            color = "#15803D" if faltan == 0 else "#B45309"
            if faltan < 0:
                color = "#DC2626"
            self.lbl_faltan.config(text=f"Personas sin acomodar: {faltan}", fg=color)

    def configurar_panel_derecho(self):
        """Configura el panel derecho según el modo."""
        if self.modo == "capitan":
            self.configurar_panel_capitan()
        elif self.modo == "anfitrion":
            self.configurar_panel_anfitrion()
        elif self.modo == "mesero":
            self.configurar_panel_mesero()
        elif self.modo == "demo":
            self.configurar_panel_demo()
        elif self.modo == "visualizacion":
            self.configurar_panel_visualizacion()

    def configurar_panel_capitan(self):
        """Configura el panel para el capitán - SOLO COLORES."""
        self.frame_right.configure(padx=14, pady=14)
        tk.Label(self.frame_right, text="Asignar meseros",
                font=("Arial", 14, "bold"), bg=COLOR_PANEL, fg=TXT).pack(pady=(0, 4))
        tk.Label(self.frame_right, text="Selecciona un color, ponle nombre y marca sus mesas.",
                font=("Arial", 9), bg=COLOR_PANEL, fg="#555", wraplength=240, justify="center").pack(pady=(0, 10))

        colores = ["red", "blue", "green", "yellow", "orange", "pink", "purple", 
                   "cyan", "magenta", "brown", "gray", "lime", "gold", "navy", 
                   "teal", "salmon", "khaki", "coral"]

        if self.organizacion:
            self.nombres_meseros = dict(getattr(self.organizacion, "nombres_meseros", {}))
            for clave, color in self.organizacion.colores.items():
                try:
                    c, f = eval(clave)
                    if (c, f) in self.valores_mesas and self.valores_mesas[(c, f)]["valor"] > 0:
                        mesa_id = self.valores_mesas[(c, f)]["mesa"]
                        self.canvas.itemconfig(mesa_id, fill=color)
                        self.mesas_colores[(c, f)] = color
                        personas = self.valores_mesas[(c, f)]["valor"]
                        self.conteo_meseros[color] = self.conteo_meseros.get(color, 0) + personas
                except:
                    pass

        tk.Label(self.frame_right, text="Colores de meseros", font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=TXT).pack(anchor="w", pady=(4, 5))
        frame_colores = tk.Frame(self.frame_right, bg=COLOR_PANEL)
        frame_colores.pack()

        self.botones_colores = {}
        for i, color in enumerate(colores):
            btn = tk.Button(frame_colores, text=self.texto_color_mesero(color), bg=color, fg="white",
                           activebackground=color, activeforeground="white", relief="flat",
                           width=12, cursor="hand2",
                           command=lambda col=color: self.seleccionar_color(col))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.botones_colores[color] = btn

        self.lbl_color_actual = tk.Label(self.frame_right,
                                         text=f"Color seleccionado: {self.texto_color_mesero(self.color_actual)}",
                                         font=("Arial", 10, "bold"), bg=COLOR_PANEL, fg=TXT)
        self.lbl_color_actual.pack(pady=(10, 4))

        tk.Button(self.frame_right, text="Asignar nombre al color",
                  command=self.asignar_nombre_color, bg=BTN2, fg="white",
                  activebackground=BTN2, activeforeground="white", relief="flat",
                  width=24, height=2, cursor="hand2").pack(pady=4)

        self.lbl_contador = tk.Label(self.frame_right, 
                                     text=f"Meseros asignados: {len(self.conteo_meseros)}",
                                     font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=BTN)
        self.lbl_contador.pack(pady=10)

        tk.Label(self.frame_right, 
                text="1. Selecciona color\n2. Opcional: asigna nombre\n3. Haz clic en mesas con invitados",
                font=("Arial", 9), bg=COLOR_PANEL, fg="#555", justify="left").pack(pady=10, anchor="w")

        self.bind_eventos_pintar()

    def texto_color_mesero(self, color):
        nombre = self.nombres_meseros.get(color)
        return f"{nombre}\n({color})" if nombre else color

    def asignar_nombre_color(self):
        nombre_actual = self.nombres_meseros.get(self.color_actual, "")
        nombre = simpledialog.askstring("Mesero", f"Nombre para el color {self.color_actual}:", initialvalue=nombre_actual)
        if nombre is not None:
            nombre = nombre.strip()
            if nombre:
                self.nombres_meseros[self.color_actual] = nombre
            elif self.color_actual in self.nombres_meseros:
                del self.nombres_meseros[self.color_actual]
            if hasattr(self, "lbl_color_actual"):
                self.lbl_color_actual.config(text=f"Color seleccionado: {self.texto_color_mesero(self.color_actual)}")
            if hasattr(self, "botones_colores") and self.color_actual in self.botones_colores:
                self.botones_colores[self.color_actual].config(text=self.texto_color_mesero(self.color_actual))

    def bind_eventos_pintar(self):
        """Bind eventos para pintar mesas en modo capitán."""
        def pintar(event, id_mesa, personas, c, f):
            if self.modo != "capitan":
                return

            viejo_color = self.mesas_colores.get((c, f))

            if viejo_color == self.color_actual:
                return

            if viejo_color:
                self.conteo_meseros[viejo_color] -= personas
                if self.conteo_meseros[viejo_color] <= 0:
                    del self.conteo_meseros[viejo_color]

            self.canvas.itemconfig(id_mesa, fill=self.color_actual)
            self.conteo_meseros[self.color_actual] = self.conteo_meseros.get(self.color_actual, 0) + personas
            self.mesas_colores[(c, f)] = self.color_actual
            self.lbl_contador.config(text=f"Meseros asignados: {len(self.conteo_meseros)}")

        # Limpiar binds anteriores
        for (c, f), info in self.valores_mesas.items():
            self.canvas.tag_unbind(info["mesa"], "<Button-1>")

        # Bindear SOLO a mesas con personas (para que no puedan pintar mesas vacías)
        for (c, f), info in self.valores_mesas.items():
            if info["valor"] > 0:
                self.canvas.tag_bind(
                    info["mesa"],
                    "<Button-1>",
                    lambda e, idm=info["mesa"], p=info["valor"], col=c, fil=f: pintar(e, idm, p, col, fil)
                )

    def configurar_panel_anfitrion(self):
        """Configura el panel para el anfitrión."""
        self.frame_right.configure(padx=14, pady=14)
        tk.Label(self.frame_right, text="Personalizar mesas",
                font=("Arial", 14, "bold"), bg=COLOR_PANEL, fg=TXT).pack(pady=(0, 4))
        tk.Label(self.frame_right, text="Elige un color y da clic derecho en una mesa para nombrarla.",
                font=("Arial", 9), bg=COLOR_PANEL, fg="#555", wraplength=230, justify="center").pack(pady=(0, 12))

        frame_pal = tk.Frame(self.frame_right, bg=COLOR_PANEL)
        frame_pal.pack(fill="x")

        colores = {
            "Familia": "#22C55E",
            "Amigos": "#3B82F6",
            "Especial": "#EC4899",
            "Ninos": "#F59E0B",
            "Reserva": "#A855F7",
        }
        
        tk.Label(frame_pal, text="Grupos", 
                font=("Arial", 10, "bold"), bg=COLOR_PANEL, fg=TXT).pack(anchor="w")
        
        for nombre, color in colores.items():
            tk.Button(frame_pal, text=nombre, bg=color, fg="white", activebackground=color,
                     activeforeground="white", relief="flat", width=20, cursor="hand2",
                     command=lambda col=color: self.seleccionar_color(col)).pack(pady=3, fill="x")

        tk.Label(frame_pal, text="Mesas nombradas", font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=TXT).pack(anchor="w", pady=(14, 4))
        self.frame_leyenda = tk.Frame(frame_pal, bg=COLOR_PANEL)
        self.frame_leyenda.pack(fill="x")

        tk.Label(self.frame_right, 
                text="Click izquierdo: cambiar personas\nClick derecho: poner nombre",
                font=("Arial", 9), bg=COLOR_PANEL, fg="#555", justify="left").pack(pady=(14, 0), anchor="w")

    def configurar_panel_mesero(self):
        """Configura el panel para el mesero - SOLO VISUALIZACIÓN."""
        tk.Label(self.frame_right, text="VISTA DE ORGANIZACIÓN", 
                font=("Arial", 12, "bold"), bg=BG, fg="#FF9800").pack(pady=10)

        if self.evento:
            tk.Label(self.frame_right, text=f"Fecha: {self.evento.fecha}",
                    font=("Arial", 11), bg=BG).pack(pady=5)
            tk.Label(self.frame_right, text=f"Total invitados: {self.evento.total_invitados()}",
                    font=("Arial", 11, "bold"), bg=BG).pack(pady=5)

        if self.organizacion:
            tk.Label(self.frame_right, text="Distribución de meseros:", 
                    font=("Arial", 11, "bold"), bg=BG).pack(pady=10)
            
            for color, personas in self.organizacion.meseros.items():
                frame_color = tk.Frame(self.frame_right, bg=BG)
                frame_color.pack(fill="x", pady=2)
                
                canvas_color = tk.Canvas(frame_color, width=20, height=20, bg=color, highlightthickness=1)
                canvas_color.pack(side="left", padx=5)
                
                nombre = getattr(self.organizacion, "nombres_meseros", {}).get(color, color)
                tk.Label(frame_color, text=f"{nombre} ({color}): {personas} personas",
                        font=("Arial", 10), bg=BG).pack(side="left")

    def configurar_panel_demo(self):
        """Configura el panel para modo demostración."""
        self.frame_right.configure(padx=14, pady=14)
        tk.Label(self.frame_right, text="MODO DEMOSTRACIÓN",
                font=("Arial", 14, "bold"), bg=COLOR_PANEL, fg=BTN).pack(pady=(0, 10))
        
        instrucciones = [
            "Prueba la distribución automática:",
            "1. Ingresa total de invitados",
            "2. Ajusta mesa principal si deseas",
            "3. Haz clic en 'Calcular'",
            "",
            "ORDEN DE PRIORIDAD:",
            "1⃣ Alrededor pista (col2/5, filas1-3)",
            "2⃣ Centro fila 3 (col3-4)",
            "3⃣ Fila 4: centro → laterales",
            "4⃣ Extremos fila 1 (col1/6)",
            "5⃣ Extremos fila 2",
            "6⃣ Extremos fila 3",
            "7⃣ Extremos fila 4",
            "8⃣ Fila 5: centro → laterales"
        ]
        
        for texto in instrucciones:
            tk.Label(self.frame_right, text=texto, 
                    font=("Arial", 10), bg=COLOR_PANEL, fg=TXT).pack(pady=2, anchor="w")

    def configurar_panel_visualizacion(self):
        """Configura el panel para visualización de eventos."""
        if self.evento:
            tk.Label(self.frame_right, text=f"EVENTO: {self.evento.fecha}",
                    font=("Arial", 14, "bold"), bg=BG, fg=BTN2).pack(pady=10)
            
            tk.Label(self.frame_right, text=f"Mesa Principal: {self.evento.principal} personas",
                    font=("Arial", 11), bg=BG).pack(pady=5)
            tk.Label(self.frame_right, text=f"Total Mesas: {len(self.evento.mesas)}",
                    font=("Arial", 11), bg=BG).pack(pady=5)
            tk.Label(self.frame_right, text=f"Total Invitados: {self.evento.total_invitados()}",
                    font=("Arial", 12, "bold"), bg=BG).pack(pady=10)

            if self.organizacion:
                tk.Label(self.frame_right, text="Organización:", 
                        font=("Arial", 11, "bold"), bg=BG).pack(pady=5)
                tk.Label(self.frame_right, text=f"Meseros: {len(self.organizacion.meseros)}",
                        font=("Arial", 11), bg=BG).pack()

    def configurar_botones(self, frame_botones):
        """Configura los botones según el modo."""
        if self.modo == "capitan":
            crear_boton(frame_botones, text="Guardar organizacion",
                     command=self.guardar_organizacion, bg=BTN).pack(side="left", padx=10)
            crear_boton(frame_botones, text="Volver",
                     command=lambda: self.volver(FrameMenuCapitan), bg="#777").pack(side="left", padx=10)

        elif self.modo == "anfitrion":
            crear_boton(frame_botones, text="Guardar evento",
                     command=self.guardar_evento, bg=BTN).pack(side="left", padx=10)
            crear_boton(frame_botones, text="Volver",
                     command=lambda: self.volver(FrameMenuAdmin), bg="#777").pack(side="left", padx=10)

        elif self.modo == "mesero":
            crear_boton(frame_botones, text="Volver",
                     command=lambda: self.volver(FrameMenuMesero), bg="#777").pack(side="left", padx=10)

        elif self.modo == "demo":
            crear_boton(frame_botones, text="Volver al Menu Patron",
                     command=lambda: self.volver(FrameMenuAdmin),
                     bg=BTN2).pack(side="left", padx=10)

        else:  # visualizacion
            if self.master.origen_actual == "comentarios":
                crear_boton(frame_botones, text="Volver a Comentarios",
                         command=lambda: self.volver(FrameComentariosMesero),
                         bg=BTN2).pack(side="left", padx=10)
            else:
                crear_boton(frame_botones, text="Volver al Calendario",
                         command=lambda: self.volver(FrameCalendario),
                         bg=BTN2).pack(side="left", padx=10)

    def seleccionar_color(self, color):
        """Selecciona el color actual."""
        self.color_actual = color
        if hasattr(self, "lbl_color_actual"):
            self.lbl_color_actual.config(text=f"Color seleccionado: {self.texto_color_mesero(color)}")

    def actualizar_leyenda(self):
        """Actualiza la leyenda de colores en modo anfitrión."""
        if hasattr(self, 'frame_leyenda'):
            for widget in self.frame_leyenda.winfo_children():
                widget.destroy()
            for color, nombre in self.asociaciones_colores.items():
                frame_item = tk.Frame(self.frame_leyenda, bg=COLOR_PANEL)
                frame_item.pack(fill="x", pady=2)
                
                canvas_color = tk.Canvas(frame_item, width=20, height=20, bg=color, highlightthickness=1)
                canvas_color.pack(side="left", padx=5)
                
                tk.Label(frame_item, text=nombre, font=("Arial", 10), bg=COLOR_PANEL, fg=TXT).pack(side="left")

    def guardar_evento(self):
        """Guarda el evento actual - SOLO mesas con personas."""
        if not hasattr(self, 'entry_total') or not self.entry_total.get():
            messagebox.showerror("Error", "Debes ingresar el total de invitados")
            return

        try:
            total = int(self.entry_total.get())
            usados = self.mesa_principal_valor + sum(i["valor"] for i in self.valores_mesas.values())
            
            if usados < total:
                messagebox.showerror("Error", f"Faltan {total - usados} personas por acomodar")
                return
            if usados > total:
                messagebox.showerror("Error", f"Sobran {usados - total} personas")
                return
        except:
            messagebox.showerror("Error", "Debes calcular primero")
            return

        # Crear lista de mesas (SOLO las que tienen al menos 2 personas)
        mesas_guardar = []
        for (c, f), info in self.valores_mesas.items():
            if info["valor"] >= 2:
                mesas_guardar.append(Mesa(c, f, info["valor"], info["nombre"], info["color"]))
        
        # Validar que haya al menos una mesa
        if not mesas_guardar:
            messagebox.showwarning("Advertencia", "No hay mesas con suficientes personas (mínimo 2)")
            return
        
        evento = Evento(self.fecha, self.mesa_principal_valor, mesas_guardar)
        GestorArchivos.guardar_evento(evento)
        messagebox.showinfo("Evento", f"Evento guardado exitosamente con {len(mesas_guardar)} mesas")
        self.volver(FrameMenuAdmin)

    def guardar_organizacion(self):
        """Guarda la organización actual."""
        if not self.evento:
            messagebox.showerror("Error", "No hay evento asociado")
            return

        organizacion = Organizacion(
            self.evento.fecha,
            self.conteo_meseros,
            {str(k): v for k, v in self.mesas_colores.items()},
            self.nombres_meseros
        )
        GestorArchivos.guardar_organizacion(organizacion)
        messagebox.showinfo("Guardado", "Organización guardada exitosamente")
        self.volver(FrameMenuCapitan)

    def cargar_evento_existente(self):
        """Carga los datos de un evento existente en el canvas.
        SOLO para cuando se ve un evento guardado (calendario, capitán, mesero)."""
        if not self.evento:
            return

        # Cargar mesa principal
        self.mesa_principal_valor = self.evento.principal
        self.canvas.itemconfig(self.texto_mp, text=f"Principal\n{self.evento.principal}")

        # Si estamos en modo anfitrion o demo, también cargar el total
        if self.modo in ["anfitrion", "demo"] and hasattr(self, 'entry_total'):
            self.total_invitados = self.evento.total_invitados()
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, str(self.total_invitados))

        # Primero, ocultar TODAS las mesas
        for info in self.valores_mesas.values():
            info["valor"] = 0
            info["nombre"] = None
            info["color"] = "lightgray"
            self.canvas.itemconfig(info["mesa"], state="hidden")
            self.canvas.itemconfig(info["texto"], state="hidden")

        # Luego, mostrar SOLO las mesas que tienen personas en el evento
        for mesa in self.evento.mesas:
            if (mesa.col, mesa.fila) in self.valores_mesas:
                info = self.valores_mesas[(mesa.col, mesa.fila)]
                info["valor"] = mesa.personas
                info["nombre"] = mesa.nombre
                info["color"] = mesa.color
                
                # Mostrar la mesa
                self.canvas.itemconfig(info["mesa"], state="normal", 
                                      fill=mesa.color if mesa.color != "lightgray" else "lightgray")
                self.canvas.itemconfig(info["texto"], state="normal", text=str(mesa.personas))
                
                if mesa.nombre:
                    self.asociaciones_colores[mesa.color] = mesa.nombre

        self.actualizar_contador()
        if hasattr(self, 'actualizar_leyenda'):
            self.actualizar_leyenda()
