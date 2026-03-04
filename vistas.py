# vistas.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkcalendar import Calendar
import datetime
from constantes import *
from modelos import Evento, Mesa, Organizacion
from gestores import GestorArchivos

class Aplicacion(tk.Tk):
    """Clase principal de la aplicación."""
    def __init__(self):
        super().__init__()
        self.title("Sistema Salón")
        self.geometry("1100x700")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._frame = None
        self.usuario_actual = None
        self.rol_actual = None
        self.origen_actual = None
        self.calendario_cache = {}
        self.calendario_offset = 0
        
        # Iniciar con la pantalla de login
        self.cambiar_frame(FrameLogin)

    def cambiar_frame(self, frame_class, **kwargs):
        """Destruye el frame actual y crea uno nuevo de la clase especificada."""
        if self._frame is not None:
            self._frame.destroy()
        self._frame = frame_class(self, **kwargs)
        self._frame.pack(fill="both", expand=True)


class FrameBase(tk.Frame):
    """Clase base para todos los frames de la aplicación."""
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG, **kwargs)
        self.master = master
        self.configurar()

    def configurar(self):
        """Método a sobrescribir por las subclases."""
        pass

    def volver(self, frame_class, **kwargs):
        """Vuelve al frame especificado."""
        self.master.cambiar_frame(frame_class, **kwargs)


class FrameLogin(FrameBase):
    def configurar(self):
        tk.Label(self, text="Sistema Salón", font=("Arial", 22, "bold"), bg=BG, fg=TXT).pack(pady=20)

        tk.Button(self, text="Patrón / Admin", bg=BTN, fg="white", width=25, height=2,
                  command=lambda: self.volver(FrameMenuAdmin)).pack(pady=8)
        tk.Button(self, text="Capitán", bg=BTN2, fg="white", width=25, height=2,
                  command=lambda: self.volver(FrameMenuCapitan)).pack(pady=8)
        tk.Button(self, text="Mesero", bg="#FF9800", fg="white", width=25, height=2,
                  command=lambda: self.volver(FrameMenuMesero)).pack(pady=8)

        tk.Button(self, text="Salir", bg="#f44336", fg="white", width=25, height=2,
                  command=self.master.destroy).pack(pady=15)


class FrameMenuAdmin(FrameBase):
    def configurar(self):
        tk.Label(self, text="Menú Patrón", font=("Arial", 20, "bold"), bg=BG).pack(pady=20)
        tk.Button(self, text="Demostración", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameCroquis, modo="demo")).pack(pady=5)
        tk.Button(self, text="Reservación (Anfitrión)", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameSeleccionFecha)).pack(pady=5)
        tk.Button(self, text="Calendario", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameCalendario)).pack(pady=5)
        tk.Button(self, text="Volver", bg="#777", fg="white", width=30, height=2,
                  command=lambda: self.volver(FrameLogin)).pack(pady=10)


class FrameMenuCapitan(FrameBase):
    def configurar(self):
        tk.Label(self, text="Menú Capitán", font=("Arial", 20, "bold"), bg=BG).pack(pady=20)
        tk.Button(self, text="Cargar evento", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameListaEventos, modo="cargar")).pack(pady=5)
        tk.Button(self, text="Cargar organización", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameListaOrganizaciones)).pack(pady=5)
        tk.Button(self, text="Comparar evento", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameCompararEventos)).pack(pady=5)
        tk.Button(self, text="Volver", bg="#777", fg="white", width=30, height=2,
                  command=lambda: self.volver(FrameLogin)).pack(pady=10)


class FrameMenuMesero(FrameBase):
    def configurar(self):
        tk.Label(self, text="Menú Mesero", font=("Arial", 20, "bold"), bg=BG).pack(pady=20)
        tk.Button(self, text="Ver organización", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameListaOrganizaciones, modo_mesero=True)).pack(pady=5)
        tk.Button(self, text="Comentarios", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameComentariosMesero)).pack(pady=5)
        tk.Button(self, text="Estadísticas", bg=BTN, width=30, height=2,
                  command=lambda: self.volver(FrameEstadisticas)).pack(pady=5)
        tk.Button(self, text="Volver", bg="#777", fg="white", width=30, height=2,
                  command=lambda: self.volver(FrameLogin)).pack(pady=10)


class FrameSeleccionFecha(FrameBase):
    """Frame para seleccionar fecha de una nueva reservación."""
    def __init__(self, master, **kwargs):
        self.calendarios_actuales = []
        self.fechas_ocupadas = set()
        super().__init__(master, **kwargs)

    def configurar(self):
        tk.Label(self, text="Fecha del evento", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Cargar fechas ocupadas
        eventos = GestorArchivos.cargar_eventos()
        self.fechas_ocupadas = {e.fecha for e in eventos}
        
        self.hoy = datetime.date.today()
        self.manana = self.hoy + datetime.timedelta(days=1)
        
        # Frame principal
        frame_principal = tk.Frame(self, bg=BG)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para controles de navegación
        frame_navegacion = tk.Frame(frame_principal, bg=BG)
        frame_navegacion.pack(pady=5, fill="x")
        
        # Frame para los calendarios
        self.frame_cals = tk.Frame(frame_principal, bg=BG)
        self.frame_cals.pack(fill="both", expand=True, pady=10)
        
        # Preconfigurar grid
        for i in range(3):
            self.frame_cals.grid_columnconfigure(i, weight=1, uniform="cal_col")
        for i in range(2):
            self.frame_cals.grid_rowconfigure(i, weight=1, uniform="cal_row")
        
        # Botones de navegación
        self.btn_prev = tk.Button(frame_navegacion, text="◀ Anterior", 
                                 command=lambda: self.actualizar_calendarios("prev"))
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 10, "bold"), bg=BG)
        self.lbl_info.pack(side="left", padx=20, expand=True)
        
        self.btn_next = tk.Button(frame_navegacion, text="Siguiente ▶", 
                                 command=lambda: self.actualizar_calendarios("next"))
        self.btn_next.pack(side="left", padx=10)
        
        self.btn_reset = tk.Button(frame_navegacion, text="Ir a hoy", 
                                  command=lambda: self.actualizar_calendarios("reset"))
        self.btn_reset.pack(side="left", padx=10)
        
        # Cargar calendarios iniciales
        self.actualizar_calendarios("reset")
        
        # Frame para botones de acción
        frame_botones = tk.Frame(frame_principal, bg=BG)
        frame_botones.pack(pady=20, fill="x")
        
        tk.Button(frame_botones, text="Aceptar fecha seleccionada", 
                  command=self.validar_fecha, bg=BTN, fg="white", 
                  width=25, height=2, font=("Arial", 10, "bold")).pack(padx=10)
        
        tk.Button(frame_botones, text="Volver al menú", 
                  command=lambda: self.volver(FrameMenuAdmin), bg="#777", fg="white", 
                  width=25, height=2).pack(padx=10)
        
        # Instrucciones
        tk.Label(self, text="Instrucciones: 1) Selecciona una fecha haciendo clic en un día\n2) Haz clic en 'Aceptar fecha' o doble clic en la fecha",
                 font=("Arial", 10), fg="#555", bg=BG).pack(pady=5)

    def crear_calendario(self, año, mes):
        """Crea un calendario optimizado."""
        clave = f"{año}-{mes}"
        
        # Verificar cache
        if clave in self.master.calendario_cache:
            cal = self.master.calendario_cache[clave]
            return cal
        
        # Crear nuevo calendario
        cal = Calendar(
            self.frame_cals,
            selectmode="day",
            date_pattern="mm/dd/yy",
            mindate=self.manana,
            year=año,
            month=mes,
            showweeknumbers=False,
            showothermonthdays=False,
            firstweekday='sunday',
            font=("Arial", 8),
            background='white',
            foreground='black',
            selectbackground=BTN,
            selectforeground='white',
            bordercolor='#ddd',
            headersbackground='#f8f8f8',
            headersforeground='#333',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='white',
            weekendforeground='black',
            othermonthbackground='white',
            othermonthforeground='#ccc',
            cursor="hand2"
        )
        
        # Marcar fechas ocupadas
        for fecha_str in self.fechas_ocupadas:
            try:
                fecha_dt = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                if fecha_dt.year == año and fecha_dt.month == mes:
                    cal.calevent_create(fecha_dt, "Ocupado", "ocupado")
                    cal.tag_config("ocupado", background="#f44336", foreground="white")
            except:
                continue
        
        # Guardar en cache
        self.master.calendario_cache[clave] = cal
        
        return cal

    def actualizar_calendarios(self, direccion):
        """Actualiza los calendarios mostrados."""
        # Actualizar offset
        if direccion == "prev":
            self.master.calendario_offset -= MESES_POR_PAGINA
        elif direccion == "next":
            self.master.calendario_offset += MESES_POR_PAGINA
        else:  # reset
            self.master.calendario_offset = 0
        
        if self.master.calendario_offset < 0:
            self.master.calendario_offset = 0
        
        # Limpiar grid
        for widget in self.frame_cals.winfo_children():
            widget.grid_forget()
        
        # Calcular fecha base
        fecha_base = self.manana
        if self.master.calendario_offset > 0:
            meses_extra = self.master.calendario_offset
            año_extra = meses_extra // 12
            mes_extra = meses_extra % 12
            
            nuevo_mes = self.manana.month + mes_extra
            nuevo_año = self.manana.year + año_extra
            
            if nuevo_mes > 12:
                nuevo_mes -= 12
                nuevo_año += 1
            
            fecha_base = datetime.date(nuevo_año, nuevo_mes, 1)
        
        # Actualizar info
        fecha_fin = fecha_base
        for i in range(MESES_POR_PAGINA - 1):
            mes_fin = fecha_fin.month + 1
            año_fin = fecha_fin.year
            if mes_fin > 12:
                mes_fin = 1
                año_fin += 1
            fecha_fin = datetime.date(año_fin, mes_fin, 1)
        
        self.lbl_info.config(text=f"Mostrando: {fecha_base.strftime('%b %Y')} - {fecha_fin.strftime('%b %Y')}")
        
        # Actualizar botones
        self.btn_prev.config(state="normal" if self.master.calendario_offset > 0 else "disabled")
        
        # Crear calendarios
        self.calendarios_actuales = []
        
        def cargar_progresivo():
            for i in range(MESES_POR_PAGINA):
                mes = fecha_base.month + i
                año = fecha_base.year
                
                while mes > 12:
                    mes -= 12
                    año += 1
                
                cal = self.crear_calendario(año, mes)
                row = i // 3
                col = i % 3
                cal.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                self.calendarios_actuales.append(cal)
                cal.bind("<<CalendarSelected>>", self.on_date_selected)
                self.frame_cals.update_idletasks()
        
        self.after(10, cargar_progresivo)

    def on_date_selected(self, event):
        """Maneja la selección de fecha."""
        widget = event.widget
        fecha_str = widget.get_date()
        if fecha_str:
            if fecha_str in self.fechas_ocupadas:
                messagebox.showerror("No disponible", "Ese día ya está reservado")
            else:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                    if fecha_obj >= self.manana:
                        self.volver(FrameCroquis, modo="anfitrion", fecha=fecha_str)
                    else:
                        messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha futura")
                except ValueError:
                    pass

    def validar_fecha(self):
        """Valida la fecha seleccionada."""
        for cal in self.calendarios_actuales:
            fecha_str = cal.get_date()
            if fecha_str:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                    
                    if fecha_obj < self.manana:
                        messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha futura")
                        return
                    
                    if fecha_str in self.fechas_ocupadas:
                        messagebox.showerror("No disponible", "Ese día ya está reservado")
                        return
                    
                    self.volver(FrameCroquis, modo="anfitrion", fecha=fecha_str)
                    return
                    
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido")
                    return
        
        messagebox.showwarning("Error", "Por favor, selecciona una fecha")


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
        self.mesas_ids = {}
        super().__init__(master, **kwargs)

    def configurar(self):
        # ===== CONTENEDORES PRINCIPALES =====
        frame_main = tk.Frame(self, bg=BG)
        frame_main.pack(expand=True)

        frame_sup = tk.Frame(frame_main, bg=BG)
        frame_sup.pack(pady=5)

        frame_centro = tk.Frame(frame_main, bg=BG)
        frame_centro.pack()

        frame_left = tk.Frame(frame_centro, bg=BG)
        frame_left.pack(side="left", padx=20)

        self.frame_right = tk.Frame(frame_centro, bg=BG)
        self.frame_right.pack(side="left", padx=20)

        # ===== PARTE SUPERIOR =====
        if self.modo in ["demo", "anfitrion"]:
            tk.Label(frame_sup, text="Total invitados:", bg=BG).grid(row=0, column=0)
            self.entry_total = tk.Entry(frame_sup, width=6)
            self.entry_total.grid(row=0, column=1)

            self.lbl_faltan = tk.Label(frame_sup, text="Personas sin acomodar: 0", bg=BG)
            self.lbl_faltan.grid(row=1, column=0, columnspan=3)

            tk.Button(frame_sup, text="Calcular", command=self.calcular).grid(row=0, column=2)

        # ===== CANVAS =====
        self.canvas = tk.Canvas(frame_left, width=COLUMNAS*CELL, height=(FILAS+1)*CELL, bg="white")
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

        # ===== BOTONES =====
        frame_botones = tk.Frame(frame_main, bg=BG)
        frame_botones.pack(pady=10)
        self.configurar_botones(frame_botones)

    def dibujar_elementos_fijos(self):
        """Dibuja la mesa principal y la pista."""
        # Mesa principal (siempre visible)
        self.mp = self.canvas.create_rectangle(2*CELL, 0, 4*CELL, int(CELL*0.7), fill="brown")
        self.texto_mp = self.canvas.create_text(3*CELL, int(CELL*0.35), 
                                                text=f"Principal\n{self.mesa_principal_valor}", 
                                                fill="white")
        
        if self.modo in ["demo", "anfitrion"]:
            self.canvas.tag_bind(self.mp, "<Button-1>", self.editar_principal)

        # Pista - ocupa filas 1-2 (siempre visible)
        self.canvas.create_rectangle(2*CELL, 1*CELL, 4*CELL, 3*CELL, fill="black")
        self.canvas.create_text(3*CELL, 2*CELL, text="PISTA", fill="white")

    def crear_mesa(self, col, fila):
        """Crea una mesa en la posición especificada (visible por defecto)."""
        x1 = (col-1)*CELL
        y1 = fila*CELL
        x2 = x1+CELL
        y2 = y1+CELL
        
        # Crear la mesa visible por defecto
        mesa = self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="lightgray", state="normal")
        texto = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="0", state="normal")
        
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
                if 3 <= col <= 4 and 1 <= fila <= 2:
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
            (3,3), (4,3),                                 # Centro fila 3
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
            self.lbl_faltan.config(text=f"Personas sin acomodar: {faltan}")

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
        tk.Label(self.frame_right, text="ASIGNAR COLORES A MESEROS", 
                font=("Arial", 12, "bold"), bg=BG, fg=BTN2).pack(pady=10)

        colores = ["red", "blue", "green", "yellow", "orange", "pink", "purple", 
                   "cyan", "magenta", "brown", "gray", "lime", "gold", "navy", 
                   "teal", "salmon", "khaki", "coral"]

        if self.organizacion:
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

        tk.Label(self.frame_right, text="Colores:", font=("Arial", 11, "bold"), bg=BG).pack(pady=5)
        frame_colores = tk.Frame(self.frame_right, bg=BG)
        frame_colores.pack()

        for i, color in enumerate(colores):
            btn = tk.Button(frame_colores, text=color, bg=color, width=10,
                           command=lambda col=color: self.seleccionar_color(col))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)

        self.lbl_contador = tk.Label(self.frame_right, 
                                     text=f"Meseros asignados: {len(self.conteo_meseros)}",
                                     font=("Arial", 12, "bold"), bg=BG, fg=BTN)
        self.lbl_contador.pack(pady=10)

        tk.Label(self.frame_right, 
                text="Instrucciones:\n1. Selecciona un color\n2. Haz clic en las mesas\n   para asignarlas",
                font=("Arial", 10), bg=BG, justify="left").pack(pady=10)

        self.bind_eventos_pintar()

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
        tk.Label(self.frame_right, text="ASIGNAR NOMBRES A MESAS", 
                font=("Arial", 12, "bold"), bg=BG, fg=BTN).pack(pady=10)

        frame_pal = tk.Frame(self.frame_right, bg=BG)
        frame_pal.pack()

        colores = {"Verde": "green", "Rojo": "red", "Azul": "blue", 
                  "Amarillo": "yellow", "Rosa": "pink"}
        
        tk.Label(frame_pal, text="Colores para identificar mesas:", 
                font=("Arial", 10), bg=BG).pack()
        
        for nombre, color in colores.items():
            tk.Button(frame_pal, text=nombre, bg=color, width=12,
                     command=lambda col=color: self.seleccionar_color(col)).pack(pady=2)

        tk.Label(frame_pal, text="Leyenda de nombres", font=("Arial", 11, "bold"), bg=BG).pack(pady=5)
        self.frame_leyenda = tk.Frame(frame_pal, bg=BG)
        self.frame_leyenda.pack()

        tk.Label(self.frame_right, 
                text="Instrucciones:\n1. Selecciona un color\n2. Click derecho en mesa\n   para asignar nombre",
                font=("Arial", 10), bg=BG, justify="left").pack(pady=10)

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
                
                tk.Label(frame_color, text=f"{color}: {personas} personas", 
                        font=("Arial", 10), bg=BG).pack(side="left")

    def configurar_panel_demo(self):
        """Configura el panel para modo demostración."""
        tk.Label(self.frame_right, text="MODO DEMOSTRACIÓN",
                font=("Arial", 14, "bold"), bg=BG, fg=BTN).pack(pady=10)
        
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
                    font=("Arial", 10), bg=BG).pack(pady=2)

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
            tk.Button(frame_botones, text="Guardar organización", 
                     command=self.guardar_organizacion, bg=BTN, fg="white",
                     width=20, height=2).pack(side="left", padx=10)
            tk.Button(frame_botones, text="Volver", 
                     command=lambda: self.volver(FrameMenuCapitan), bg="#777", fg="white",
                     width=20, height=2).pack(side="left", padx=10)

        elif self.modo == "anfitrion":
            tk.Button(frame_botones, text="Guardar evento", 
                     command=self.guardar_evento, bg=BTN, fg="white",
                     width=20, height=2).pack(side="left", padx=10)
            tk.Button(frame_botones, text="Volver", 
                     command=lambda: self.volver(FrameMenuAdmin), bg="#777", fg="white",
                     width=20, height=2).pack(side="left", padx=10)

        elif self.modo == "mesero":
            tk.Button(frame_botones, text="Volver", 
                     command=lambda: self.volver(FrameMenuMesero), bg="#777", fg="white",
                     width=20, height=2).pack(side="left", padx=10)

        elif self.modo == "demo":
            tk.Button(frame_botones, text="Volver al Menú Patrón",
                     command=lambda: self.volver(FrameMenuAdmin),
                     bg=BTN2, fg="white", width=20, height=2).pack(side="left", padx=10)

        else:  # visualizacion
            if self.master.origen_actual == "comentarios":
                tk.Button(frame_botones, text="Volver a Comentarios",
                         command=lambda: self.volver(FrameComentariosMesero),
                         bg=BTN2, fg="white", width=20, height=2).pack(side="left", padx=10)
            else:
                tk.Button(frame_botones, text="Volver al Calendario",
                         command=lambda: self.volver(FrameCalendario),
                         bg=BTN2, fg="white", width=20, height=2).pack(side="left", padx=10)

    def seleccionar_color(self, color):
        """Selecciona el color actual."""
        self.color_actual = color

    def actualizar_leyenda(self):
        """Actualiza la leyenda de colores en modo anfitrión."""
        if hasattr(self, 'frame_leyenda'):
            for widget in self.frame_leyenda.winfo_children():
                widget.destroy()
            for color, nombre in self.asociaciones_colores.items():
                frame_item = tk.Frame(self.frame_leyenda, bg=BG)
                frame_item.pack(fill="x", pady=2)
                
                canvas_color = tk.Canvas(frame_item, width=20, height=20, bg=color, highlightthickness=1)
                canvas_color.pack(side="left", padx=5)
                
                tk.Label(frame_item, text=nombre, font=("Arial", 10), bg=BG).pack(side="left")

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
            {str(k): v for k, v in self.mesas_colores.items()}
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

class FrameCalendario(FrameBase):
    """Frame que muestra el calendario de eventos."""
    def __init__(self, master, **kwargs):
        self.calendarios_actuales = []
        self.eventos_por_fecha = {}
        super().__init__(master, **kwargs)

    def configurar(self):
        self.master.origen_actual = "calendario"
        
        tk.Label(self, text="Calendario de Eventos", font=("Arial", 14, "bold"), bg=BG).pack(pady=5)
        
        # Cargar eventos
        eventos = GestorArchivos.cargar_eventos()
        self.eventos_por_fecha = {e.fecha: e for e in eventos}
        
        self.hoy = datetime.date.today()
        
        # Frame principal
        frame_principal = tk.Frame(self, bg=BG)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para navegación
        frame_navegacion = tk.Frame(frame_principal, bg=BG)
        frame_navegacion.pack(pady=5, fill="x")
        
        # Botones de navegación
        self.btn_prev = tk.Button(frame_navegacion, text="◀ Anterior", 
                                 command=lambda: self.actualizar_calendarios("prev"))
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 10, "bold"), bg=BG)
        self.lbl_info.pack(side="left", padx=20, expand=True)
        
        self.btn_next = tk.Button(frame_navegacion, text="Siguiente ▶", 
                                 command=lambda: self.actualizar_calendarios("next"))
        self.btn_next.pack(side="left", padx=10)
        
        self.btn_reset = tk.Button(frame_navegacion, text="Ir a hoy", 
                                  command=lambda: self.actualizar_calendarios("reset"))
        self.btn_reset.pack(side="left", padx=10)
        
        # Frame para calendarios
        self.frame_cals = tk.Frame(frame_principal, bg=BG)
        self.frame_cals.pack(fill="both", expand=True, pady=10)
        
        # Preconfigurar grid
        for i in range(3):
            self.frame_cals.grid_columnconfigure(i, weight=1, uniform="cal_col")
        for i in range(2):
            self.frame_cals.grid_rowconfigure(i, weight=1, uniform="cal_row")
        
        # Cargar calendarios iniciales
        self.actualizar_calendarios("reset")
        
        # Frame para botones
        frame_botones = tk.Frame(frame_principal, bg=BG)
        frame_botones.pack(pady=20, fill="x")
        
        tk.Button(frame_botones, text="Volver al menú", 
                  command=lambda: self.volver(FrameMenuAdmin), bg="#777", fg="white", 
                  width=25, height=2).pack(pady=10)
        
        # Leyenda
        self.mostrar_leyenda(frame_principal)

    def crear_calendario(self, año, mes):
        """Crea un calendario con eventos marcados."""
        cal = Calendar(
            self.frame_cals,
            selectmode="day",
            date_pattern="mm/dd/yy",
            year=año,
            month=mes,
            showweeknumbers=False,
            showothermonthdays=False,
            firstweekday='sunday',
            font=("Arial", 9),
            background='white',
            foreground='black',
            selectbackground=BTN,
            selectforeground='white',
            bordercolor='#ddd',
            headersbackground='#f8f8f8',
            headersforeground='#333',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='white',
            weekendforeground='black',
            othermonthbackground='white',
            othermonthforeground='#ccc',
            cursor="hand2"
        )
        
        # Marcar hoy
        if self.hoy.year == año and self.hoy.month == mes:
            cal.calevent_create(self.hoy, "Hoy", "hoy")
            cal.tag_config("hoy", background="#2196F3", foreground="white")
        
        # Marcar días pasados
        if (año < self.hoy.year) or (año == self.hoy.year and mes < self.hoy.month):
            for day in range(1, 32):
                try:
                    fecha_cal = datetime.date(año, mes, day)
                    if fecha_cal < self.hoy:
                        cal.calevent_create(fecha_cal, "Día pasado", "pasado")
                        cal.tag_config("pasado", background="#f0f0f0", foreground="#888")
                except ValueError:
                    continue
        elif año == self.hoy.year and mes == self.hoy.month:
            for day in range(1, self.hoy.day):
                try:
                    fecha_cal = datetime.date(año, mes, day)
                    cal.calevent_create(fecha_cal, "Día pasado", "pasado")
                    cal.tag_config("pasado", background="#f0f0f0", foreground="#888")
                except ValueError:
                    continue
        
        # Marcar eventos
        for fecha_str, evento in self.eventos_por_fecha.items():
            try:
                fecha_dt = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_dt = datetime.datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_dt and fecha_dt.year == año and fecha_dt.month == mes:
                    total_personas = evento.total_invitados()
                    
                    if fecha_dt < self.hoy:
                        cal.calevent_create(fecha_dt, f"Evento pasado: {total_personas} personas", "evento_pasado")
                        cal.tag_config("evento_pasado", background="#2196F3", foreground="white")
                    elif fecha_dt == self.hoy:
                        cal.calevent_create(fecha_dt, f"Evento HOY: {total_personas} personas", "evento_hoy")
                        cal.tag_config("evento_hoy", background="#FF9800", foreground="white")
                    else:
                        cal.calevent_create(fecha_dt, f"Evento futuro: {total_personas} personas", "evento_futuro")
                        cal.tag_config("evento_futuro", background="#4CAF50", foreground="white")
            except:
                continue
        
        return cal

    def actualizar_calendarios(self, direccion):
        """Actualiza los calendarios mostrados."""
        if direccion == "prev":
            self.master.calendario_offset -= MESES_POR_PAGINA
        elif direccion == "next":
            self.master.calendario_offset += MESES_POR_PAGINA
        else:
            self.master.calendario_offset = 0
        
        if self.master.calendario_offset < 0:
            self.master.calendario_offset = 0
        
        # Limpiar frame
        for widget in self.frame_cals.winfo_children():
            widget.destroy()
        
        # Calcular meses a mostrar (siempre 6 meses, empezando en enero)
        año_actual = self.hoy.year
        mes_base = 1
        
        if self.master.calendario_offset > 0:
            total_meses = self.master.calendario_offset
            años_extra = total_meses // 12
            meses_extra = total_meses % 12
            
            mes_base += meses_extra
            año_actual += años_extra
            
            if mes_base > 12:
                mes_base -= 12
                año_actual += 1
        
        # Determinar rango de meses
        meses_a_mostrar = []
        for i in range(6):
            mes = mes_base + i
            año = año_actual
            while mes > 12:
                mes -= 12
                año += 1
            meses_a_mostrar.append((año, mes))
        
        # Actualizar label
        nombres_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        primer_año, primer_mes = meses_a_mostrar[0]
        ultimo_año, ultimo_mes = meses_a_mostrar[-1]
        
        if primer_año == ultimo_año:
            self.lbl_info.config(text=f"Mostrando: {nombres_meses[primer_mes-1]} - {nombres_meses[ultimo_mes-1]} {primer_año}")
        else:
            self.lbl_info.config(text=f"Mostrando: {nombres_meses[primer_mes-1]} {primer_año} - {nombres_meses[ultimo_mes-1]} {ultimo_año}")
        
        # Actualizar botones
        self.btn_prev.config(state="normal" if self.master.calendario_offset > 0 else "disabled")
        
        # Crear calendarios
        self.calendarios_actuales = []
        for i, (año, mes) in enumerate(meses_a_mostrar):
            cal = self.crear_calendario(año, mes)
            row = i // 3
            col = i % 3
            cal.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.calendarios_actuales.append(cal)
            cal.bind("<<CalendarSelected>>", self.on_date_selected)

    def on_date_selected(self, event):
        """Maneja la selección de fecha."""
        widget = event.widget
        fecha_str = widget.get_date()
        
        if not fecha_str:
            return
        
        try:
            fecha_dt = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
        except ValueError:
            messagebox.showerror("Error", f"No se pudo interpretar la fecha: {fecha_str}")
            return
        
        # Buscar evento
        evento_encontrado = None
        for fecha_guardada, evento in self.eventos_por_fecha.items():
            try:
                fecha_guardada_dt = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_guardada_dt = datetime.datetime.strptime(fecha_guardada, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_guardada_dt and fecha_guardada_dt == fecha_dt:
                    evento_encontrado = evento
                    break
            except:
                continue
        
        if evento_encontrado:
            self.mostrar_info_evento(evento_encontrado, fecha_dt)
        else:
            if fecha_dt < self.hoy:
                messagebox.showinfo("Información", f"No hubo evento reservado el {fecha_str}")
            else:
                messagebox.showinfo("Información", f"No hay evento reservado para el {fecha_str}")

    def mostrar_info_evento(self, evento, fecha_dt):
        """Muestra información detallada del evento."""
        info_ventana = tk.Toplevel(self)
        info_ventana.title(f"Evento del {evento.fecha}")
        info_ventana.geometry("600x550")
        info_ventana.resizable(False, False)
        info_ventana.configure(bg=BG)
        
        frame_info = tk.Frame(info_ventana, bg=BG)
        frame_info.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(frame_info, text=f"EVENTO - {evento.fecha}", 
                font=("Arial", 16, "bold"), bg=BG, fg=TXT).pack(pady=10)
        
        # Información básica
        frame_datos = tk.Frame(frame_info, bg=BG)
        frame_datos.pack(fill="x", pady=10)
        
        tk.Label(frame_datos, text=f"Mesa Principal: {evento.principal} personas", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        total_mesas = len(evento.mesas)
        tk.Label(frame_datos, text=f"Total de mesas: {total_mesas}", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        total_invitados = evento.total_invitados()
        tk.Label(frame_datos, text=f"Total de invitados: {total_invitados}", 
                font=("Arial", 12, "bold"), bg=BG, anchor="w").pack(fill="x", pady=5)
        
        # Mostrar nombres de mesas
        if evento.mesas:
            frame_mesas = tk.Frame(frame_info, bg=BG)
            frame_mesas.pack(fill="x", pady=10)
            
            tk.Label(frame_mesas, text="Mesas asignadas:", 
                    font=("Arial", 11, "bold"), bg=BG).pack(anchor="w")
            
            for i, mesa in enumerate(evento.mesas[:5]):
                if mesa.nombre:
                    tk.Label(frame_mesas, text=f"  • {mesa.nombre}: {mesa.personas} personas", 
                            font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
            
            if len(evento.mesas) > 5:
                tk.Label(frame_mesas, text=f"  ... y {len(evento.mesas) - 5} mesas más", 
                        font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
        
        # Estado del evento
        frame_estado = tk.Frame(frame_info, bg=BG)
        frame_estado.pack(fill="x", pady=15)
        
        if fecha_dt < self.hoy:
            estado_texto = "EVENTO REALIZADO ✓"
            estado_color = "#757575"
        elif fecha_dt == self.hoy:
            estado_texto = "EVENTO HOY ⚠"
            estado_color = "#FF9800"
        else:
            estado_texto = "EVENTO PROGRAMADO"
            estado_color = "#2196F3"
        
        tk.Label(frame_estado, text=estado_texto, 
                font=("Arial", 14, "bold"), bg=estado_color, fg="white",
                width=30, height=2).pack(pady=10)
        
        # Botones
        frame_botones = tk.Frame(frame_info, bg=BG)
        frame_botones.pack(pady=20)
        
        if evento.mesas:
            tk.Button(frame_botones, text="Ver Croquis del Evento", 
                     command=lambda: self.ver_croquis(evento, info_ventana), 
                     bg=BTN, fg="white", width=25).pack(pady=5)
        
        # Verificar si hay organización
        organizacion = GestorArchivos.buscar_organizacion_por_fecha(evento.fecha)
        if organizacion:
            tk.Button(frame_botones, text="Ver Organización Asignada", 
                     command=lambda: self.ver_organizacion(evento, organizacion, info_ventana), 
                     bg=BTN2, fg="white", width=25).pack(pady=5)
        
        tk.Button(frame_botones, text="Cerrar", 
                 command=info_ventana.destroy, 
                 bg="#777", fg="white", width=25).pack(pady=5)

    def ver_croquis(self, evento, ventana_actual):
        """Muestra el croquis del evento."""
        ventana_actual.destroy()
        self.master.cambiar_frame(FrameCroquis, modo="visualizacion", evento=evento)

    def ver_organizacion(self, evento, organizacion, ventana_actual):
        """Muestra la organización del evento."""
        ventana_actual.destroy()
        self.master.cambiar_frame(FrameCroquis, modo="visualizacion", evento=evento, organizacion=organizacion)

    def mostrar_leyenda(self, parent):
        """Muestra la leyenda de colores."""
        frame_leyenda = tk.Frame(parent, bg=BG)
        frame_leyenda.pack(pady=10)
        
        tk.Label(frame_leyenda, text="Leyenda:", font=("Arial", 10, "bold"), bg=BG).pack(side="left", padx=5)
        
        colores_leyenda = [
            ("Hoy", "#2196F3"),
            ("Día pasado sin evento", "#f0f0f0"),
            ("Evento pasado", "#2196F3"),
            ("Evento hoy", "#FF9800"),
            ("Evento futuro", "#4CAF50")
        ]
        
        for texto, color in colores_leyenda:
            frame_color = tk.Frame(frame_leyenda, bg=BG)
            frame_color.pack(side="left", padx=10)
            
            tk.Label(frame_color, text="⬤", fg=color, font=("Arial", 14), bg=BG).pack(side="left")
            tk.Label(frame_color, text=texto, font=("Arial", 9), bg=BG).pack(side="left", padx=2)


class FrameListaEventos(FrameBase):
    """Frame para listar eventos no organizados."""
    def __init__(self, master, modo="cargar", **kwargs):
        self.modo = modo
        super().__init__(master, **kwargs)

    def configurar(self):
        tk.Label(self, text="Eventos sin organizar", font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        eventos = GestorArchivos.cargar_eventos()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        
        # Filtrar eventos no organizados
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        if not eventos_no_org:
            tk.Label(self, text="No hay eventos pendientes de organizar", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=50, height=15, 
                                  yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, evento in enumerate(eventos_no_org):
            total = evento.total_invitados()
            self.listbox.insert(tk.END, f"{i} - {evento.fecha} - {total} invitados")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir evento", command=self.abrir_evento,
                 bg=BTN, fg="white", width=20).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                 bg="#777", fg="white", width=20).pack(side="left", padx=10)

    def abrir_evento(self):
        """Abre el evento seleccionado."""
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Selección", "Por favor, selecciona un evento")
            return
        
        # Obtener el índice real del evento
        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        
        eventos = GestorArchivos.cargar_eventos()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        evento = eventos_no_org[int(indice_texto)]
        self.master.cambiar_frame(FrameCroquis, modo="capitan", evento=evento)


class FrameListaOrganizaciones(FrameBase):
    """Frame para listar organizaciones guardadas."""
    def __init__(self, master, modo_mesero=False, **kwargs):
        self.modo_mesero = modo_mesero
        super().__init__(master, **kwargs)

    def configurar(self):
        titulo = "Organizaciones disponibles para meseros" if self.modo_mesero else "Organizaciones guardadas"
        tk.Label(self, text=titulo, font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        organizaciones = GestorArchivos.cargar_organizaciones()
        
        if not organizaciones:
            tk.Label(self, text="No hay organizaciones guardadas", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
            tk.Button(self, text="Volver", command=lambda: self.volver(btn_volver),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=50, height=15, 
                                  yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, org in enumerate(organizaciones):
            num_meseros = len(org.meseros)
            self.listbox.insert(tk.END, f"{i} - {org.fecha} - {num_meseros} meseros")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir organización", command=self.abrir_organizacion,
                 bg=BTN, fg="white", width=20).pack(side="left", padx=10)
        
        btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(btn_volver),
                 bg="#777", fg="white", width=20).pack(side="left", padx=10)

    def abrir_organizacion(self):
        """Abre la organización seleccionada."""
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Selección", "Por favor, selecciona una organización")
            return
        
        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        
        organizaciones = GestorArchivos.cargar_organizaciones()
        org = organizaciones[int(indice_texto)]
        
        # Buscar el evento correspondiente
        evento = GestorArchivos.buscar_evento_por_fecha(org.fecha)
        
        if not evento:
            messagebox.showerror("Error", "No se encontró el evento asociado")
            return
        
        modo = "mesero" if self.modo_mesero else "capitan"
        self.master.cambiar_frame(FrameCroquis, modo=modo, evento=evento, organizacion=org)


class FrameCompararEventos(FrameBase):
    """Frame para comparar dos eventos."""
    def configurar(self):
        tk.Label(self, text="Comparar eventos", font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        if len(eventos_con_fecha) < 2:
            tk.Label(self, text="Se necesitan al menos 2 eventos para comparar", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Frame de selección
        frame_sel = tk.Frame(self, bg=BG)
        frame_sel.pack(pady=10)
        
        tk.Label(frame_sel, text="Evento actual", bg=BG, font=("Arial", 11, "bold")).grid(row=0, column=0, padx=20)
        tk.Label(frame_sel, text="Evento siguiente", bg=BG, font=("Arial", 11, "bold")).grid(row=0, column=1, padx=20)
        
        # Listboxes
        self.lb1 = tk.Listbox(frame_sel, width=30, height=10, exportselection=False)
        self.lb2 = tk.Listbox(frame_sel, width=30, height=10, exportselection=False)
        self.lb1.grid(row=1, column=0, padx=10)
        self.lb2.grid(row=1, column=1, padx=10)
        
        for i, e in enumerate(eventos_con_fecha):
            self.lb1.insert(tk.END, f"{i} - {e.fecha}")
        
        # Frame de información
        frame_info = tk.Frame(self, bg=BG)
        frame_info.pack(pady=10)
        
        self.lbl_info1 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info1.pack()
        self.lbl_info2 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info2.pack()
        self.lbl_info3 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info3.pack()
        
        # Frame para canvas
        self.frame_canvas = tk.Frame(self, bg=BG)
        self.frame_canvas.pack(pady=10, fill="both", expand=True)
        
        # Bind eventos
        self.lb1.bind("<<ListboxSelect>>", self.on_select_actual)
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=10)
        
        tk.Button(frame_botones, text="Comparar", command=self.comparar,
                 bg=BTN, fg="white", width=15).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                 bg="#777", fg="white", width=15).pack(side="left", padx=10)

    def on_select_actual(self, event):
        """Maneja la selección del evento actual."""
        self.lb2.delete(0, tk.END)
        sel = self.lb1.curselection()
        if not sel:
            return
        
        idx = sel[0]
        texto = self.lb1.get(idx)
        indice = int(texto.split(" - ")[0])
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        try:
            fecha_actual = datetime.datetime.strptime(eventos_con_fecha[indice].fecha, "%m/%d/%y")
            
            for i, e in enumerate(eventos_con_fecha):
                fecha_e = datetime.datetime.strptime(e.fecha, "%m/%d/%y")
                if fecha_e > fecha_actual:
                    self.lb2.insert(tk.END, f"{i} - {e.fecha}")
        except:
            pass

    def comparar(self):
        """Compara los dos eventos seleccionados."""
        sel1 = self.lb1.curselection()
        sel2 = self.lb2.curselection()
        
        if not sel1 or not sel2:
            messagebox.showwarning("Error", "Selecciona dos eventos")
            return
        
        texto1 = self.lb1.get(sel1[0])
        texto2 = self.lb2.get(sel2[0])
        i1 = int(texto1.split(" - ")[0])
        i2 = int(texto2.split(" - ")[0])
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        ev1 = eventos_con_fecha[i1]
        ev2 = eventos_con_fecha[i2]
        
        # Limpiar canvas
        for widget in self.frame_canvas.winfo_children():
            widget.destroy()
        
        # Dibujar croquis
        self.dibujar_croquis_comparacion(ev1, ev2)
        
        # Calcular diferencias
        total1 = ev1.total_invitados()
        total2 = ev2.total_invitados()
        diff = total2 - total1
        
        org = GestorArchivos.buscar_organizacion_por_fecha(ev1.fecha)
        total_meseros = len(org.meseros) if org else 0
        
        if diff > 0:
            self.lbl_info1.config(text=f"Sillas que FALTAN: {diff}")
        else:
            self.lbl_info1.config(text=f"Sillas que SOBRAN: {abs(diff)}")
        
        self.lbl_info2.config(text=f"Meseros del evento actual: {total_meseros}")
        
        if diff < 0 and total_meseros > 0:
            sillas_por_mesero = abs(diff) // total_meseros
            self.lbl_info3.config(text=f"Sillas por mesero: {sillas_por_mesero}")
        else:
            self.lbl_info3.config(text="")

    def dibujar_croquis_comparacion(self, ev1, ev2):
        """Dibuja dos croquis para comparar."""
        def dibujar_uno(frame, evento, titulo):
            canvas = tk.Canvas(frame, width=COLUMNAS*CELL//2, height=(FILAS+1)*CELL//2, bg="white")
            canvas.pack(side="left", padx=10)
            
            scale = 0.5
            
            def sx(x): return int(x*scale)
            def sy(y): return int(y*scale)
            
            # Título
            canvas.create_text(150, sy(15), text=titulo, font=("Arial", 10, "bold"))
            
            # Mesa principal
            canvas.create_rectangle(sx(2*CELL), sy(20), sx(4*CELL), sy(20+CELL*0.7), fill="brown")
            canvas.create_text(sx(3*CELL), sy(20+0.35*CELL),
                              text=f"P:{evento.principal}", fill="white")
            
            # Pista
            canvas.create_rectangle(sx(2*CELL), sy(1*CELL+20), sx(4*CELL), sy(4*CELL+20), fill="black")
            canvas.create_text(sx(3*CELL), sy(2.5*CELL+20), text="PISTA", fill="white")
            
            # Mesas
            for mesa in evento.mesas:
                x1 = sx((mesa.col-1)*CELL)
                y1 = sy(mesa.fila*CELL+20)
                x2 = sx((mesa.col)*CELL)
                y2 = sy((mesa.fila+1)*CELL+20)
                
                canvas.create_oval(x1+sx(5), y1+sy(5), x2-sx(5), y2-sy(5), fill="lightgray")
                canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(mesa.personas))
        
        frame_comp = tk.Frame(self.frame_canvas, bg=BG)
        frame_comp.pack()
        
        dibujar_uno(frame_comp, ev1, "Evento Actual")
        dibujar_uno(frame_comp, ev2, "Evento Siguiente")


class FrameComentariosMesero(FrameBase):
    """Frame para que los meseros agreguen comentarios."""
    def configurar(self):
        self.master.origen_actual = "comentarios"
        
        tk.Label(self, text="Comentarios del evento", font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        # Cargar eventos pasados y de hoy
        eventos = GestorArchivos.cargar_eventos()
        hoy = datetime.date.today()
        self.eventos_comentables = []
        
        for e in eventos:
            try:
                fecha_str = e.fecha
                if not fecha_str:
                    continue
                
                fecha_dt = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_dt = datetime.datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_dt and fecha_dt <= hoy:
                    self.eventos_comentables.append((fecha_dt, e))
            except:
                continue
        
        self.eventos_comentables.sort(key=lambda x: x[0], reverse=True)
        
        if not self.eventos_comentables:
            tk.Label(self, text="No hay eventos pasados o del día de hoy para comentar.",
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuMesero),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Variable para el evento seleccionado
        self.evento_seleccionado = tk.StringVar()
        
        # Frame para selección con scroll
        self.crear_selector_eventos()
        
        # Frame para el formulario
        self.frame_formulario = tk.Frame(self, bg=BG, relief="groove", bd=2)
        self.crear_formulario()
        
        # Botón volver
        tk.Button(self, text="Volver al menú", command=lambda: self.volver(FrameMenuMesero),
                 bg="#777", fg="white", width=20, height=2).pack(pady=10)

    def crear_selector_eventos(self):
        """Crea el selector de eventos con scroll."""
        frame_seleccion = tk.Frame(self, bg=BG)
        frame_seleccion.pack(pady=10, fill="x", padx=20)
        
        tk.Label(frame_seleccion, text="Selecciona el evento:", 
                font=("Arial", 11, "bold"), bg=BG).pack(anchor="w")
        
        # Frame con scroll
        frame_scroll = tk.Frame(self, bg=BG)
        frame_scroll.pack(pady=5, fill="both", expand=True, padx=20)
        
        canvas_scroll = tk.Canvas(frame_scroll, height=150, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_scroll.yview)
        self.scrollable_frame = tk.Frame(canvas_scroll, bg=BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar eventos
        for fecha_dt, evento in self.eventos_comentables:
            fecha_str = fecha_dt.strftime("%d/%m/%Y")
            total_personas = evento.total_invitados()
            estado = "HOY" if fecha_dt == datetime.date.today() else "PASADO"
            
            frame_opcion = tk.Frame(self.scrollable_frame, bg=BG)
            frame_opcion.pack(fill="x", pady=2)
            
            rb = tk.Radiobutton(frame_opcion, 
                               text=f"{fecha_str} - {estado} - {total_personas} invitados",
                               variable=self.evento_seleccionado, 
                               value=evento.fecha,
                               font=("Arial", 10), bg=BG,
                               command=self.habilitar_formulario)
            rb.pack(side="left")
            
            btn_ver = tk.Button(frame_opcion, text="Ver croquis",
                               command=lambda ev=evento: self.ver_croquis(ev),
                               bg=BTN2, fg="white", font=("Arial", 8))
            btn_ver.pack(side="right", padx=5)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def crear_formulario(self):
        """Crea el formulario de comentarios."""
        tk.Label(self.frame_formulario, text="Formulario de comentarios", 
                font=("Arial", 12, "bold"), bg=BG).pack(pady=5)
        
        frame_campos = tk.Frame(self.frame_formulario, bg=BG)
        frame_campos.pack(pady=10, padx=20)
        
        # Campos
        labels = ["¿Cuánto ganaste? ($):", "¿Cómo sentiste el evento?:", 
                 "Observaciones:", "¿Hubo desperfectos o quejas?:"]
        
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame_campos, text=label, font=("Arial", 10), bg=BG).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(frame_campos, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[f"field_{i}"] = entry
        
        # Calificación
        tk.Label(frame_campos, text="Calificación (1-5):", font=("Arial", 10), bg=BG).grid(row=4, column=0, sticky="w", pady=5)
        self.calificacion_var = tk.StringVar(value="5")
        calificacion_combo = tk.Spinbox(frame_campos, from_=1, to=5, textvariable=self.calificacion_var, width=5)
        calificacion_combo.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # Etiqueta de edición
        self.lbl_editando = tk.Label(self.frame_formulario, text="", font=("Arial", 9, "italic"), 
                                    fg=BTN2, bg=BG)
        self.lbl_editando.pack(pady=2)
        
        # Botones del formulario
        frame_botones = tk.Frame(self.frame_formulario, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Guardar comentario", 
                 command=self.guardar, bg=BTN, fg="white", 
                 width=20, height=2, font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        tk.Button(frame_botones, text="Ver comentarios guardados", 
                 command=self.mostrar_comentarios_guardados, bg=BTN2, fg="white", 
                 width=25).pack(side="left", padx=10)

    def habilitar_formulario(self):
        """Habilita el formulario cuando se selecciona un evento."""
        self.frame_formulario.pack(pady=20, fill="x", padx=20)
        fecha = self.evento_seleccionado.get()
        if fecha:
            self.cargar_comentarios_existentes()

    def cargar_comentarios_existentes(self):
        """Carga comentarios existentes para el evento seleccionado."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            return
        
        comentarios = GestorArchivos.cargar_comentarios()
        encontrado = False
        
        for c in comentarios:
            if c.get("fecha") == fecha:
                self.entries["field_0"].delete(0, tk.END)
                self.entries["field_0"].insert(0, c.get("ganancia", ""))
                
                self.entries["field_1"].delete(0, tk.END)
                self.entries["field_1"].insert(0, c.get("sentir", ""))
                
                self.entries["field_2"].delete(0, tk.END)
                self.entries["field_2"].insert(0, c.get("observaciones", ""))
                
                self.entries["field_3"].delete(0, tk.END)
                self.entries["field_3"].insert(0, c.get("reporte", ""))
                
                self.calificacion_var.set(c.get("calificacion", "5"))
                
                self.lbl_editando.config(text="✎ Editando comentario existente")
                encontrado = True
                break
        
        if not encontrado:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.calificacion_var.set("5")
            self.lbl_editando.config(text="+ Nuevo comentario")

    def guardar(self):
        """Guarda el comentario."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            messagebox.showwarning("Error", "Por favor, selecciona un evento")
            return
        
        if not self.entries["field_0"].get().strip():
            messagebox.showwarning("Error", "Por favor, ingresa cuánto ganaste")
            return
        
        if not self.entries["field_1"].get().strip():
            messagebox.showwarning("Error", "Por favor, describe cómo sentiste el evento")
            return
        
        data = {
            "fecha": fecha,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ganancia": self.entries["field_0"].get(),
            "sentir": self.entries["field_1"].get(),
            "observaciones": self.entries["field_2"].get(),
            "reporte": self.entries["field_3"].get(),
            "calificacion": self.calificacion_var.get()
        }
        
        GestorArchivos.guardar_comentario(data)
        
        messagebox.showinfo("Gracias", f"Comentario guardado para el evento del {fecha}")
        
        respuesta = messagebox.askyesno("Continuar", "¿Quieres agregar otro comentario?")
        if respuesta:
            self.evento_seleccionado.set("")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.calificacion_var.set("5")
            self.lbl_editando.config(text="")
            self.frame_formulario.pack_forget()
        else:
            self.volver(FrameMenuMesero)

    def mostrar_comentarios_guardados(self):
        """Muestra los comentarios guardados para el evento seleccionado."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            messagebox.showinfo("Info", "Selecciona un evento para ver sus comentarios")
            return
        
        comentarios = GestorArchivos.cargar_comentarios()
        comentarios_evento = [c for c in comentarios if c.get("fecha") == fecha]
        
        if not comentarios_evento:
            messagebox.showinfo("Info", "No hay comentarios guardados para este evento")
            return
        
        ventana_comentarios = tk.Toplevel(self)
        ventana_comentarios.title(f"Comentarios - {fecha}")
        ventana_comentarios.geometry("500x400")
        ventana_comentarios.configure(bg=BG)
        
        frame_ver = tk.Frame(ventana_comentarios, bg=BG)
        frame_ver.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame_ver, text=f"Comentarios del evento {fecha}", 
                font=("Arial", 14, "bold"), bg=BG).pack(pady=10)
        
        for c in comentarios_evento:
            frame_com = tk.Frame(frame_ver, bg=BG, relief="groove", bd=1)
            frame_com.pack(fill="x", pady=5)
            
            tk.Label(frame_com, text=f"Ganancia: ${c.get('ganancia', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Cómo sintió: {c.get('sentir', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Observaciones: {c.get('observaciones', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Reporte: {c.get('reporte', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Calificación: {c.get('calificacion', 'N/A')}/5", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Registrado: {c.get('timestamp', 'N/A')}", 
                    font=("Arial", 8, "italic"), fg="gray", bg=BG).pack(anchor="e", padx=5)
        
        tk.Button(frame_ver, text="Cerrar", command=ventana_comentarios.destroy,
                 bg="#777", fg="white", width=15).pack(pady=10)

    def ver_croquis(self, evento):
        """Muestra el croquis del evento."""
        self.master.origen_actual = "comentarios"
        self.master.cambiar_frame(FrameCroquis, modo="visualizacion", evento=evento)


class FrameEstadisticas(FrameBase):
    """Frame para mostrar estadísticas."""
    def configurar(self):
        tk.Label(self, text="Estadísticas de desempeño", font=("Arial", 16, "bold"), bg=BG).pack(pady=20)
        
        # Aquí iría la lógica de estadísticas
        tk.Label(self, text="Próximamente: Estadísticas detalladas", 
                font=("Arial", 12), bg=BG).pack(pady=10)
        
        # Botón para exportar comentarios
        tk.Button(self, text="Exportar comentarios a Excel", 
                 command=self.exportar_comentarios, bg=BTN, fg="white",
                 width=25, height=2).pack(pady=10)
        
        tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuMesero),
                 bg="#777", fg="white", width=20, height=2).pack(pady=20)

    def exportar_comentarios(self):
        """Exporta los comentarios a CSV."""
        archivos = GestorArchivos.exportar_comentarios_a_excel()
        if archivos:
            mensaje = "Archivos generados:\n" + "\n".join(archivos)
            messagebox.showinfo("Exportación exitosa", mensaje)
        else:
            messagebox.showinfo("Sin datos", "No hay comentarios para exportar")