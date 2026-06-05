import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def sumar_meses(fecha, meses):
    mes_total = fecha.month - 1 + meses
    anio = fecha.year + mes_total // 12
    mes = mes_total % 12 + 1
    return datetime.date(anio, mes, 1)


def formatear_rango_meses(meses):
    primer_anio, primer_mes = meses[0]
    ultimo_anio, ultimo_mes = meses[-1]
    inicio = f"{MESES_ES[primer_mes - 1]} {primer_anio}"
    fin = f"{MESES_ES[ultimo_mes - 1]} {ultimo_anio}"
    return inicio if inicio == fin else f"{inicio} - {fin}"


def inicio_semestre(fecha):
    mes = 1 if fecha.month <= 6 else 7
    return datetime.date(fecha.year, mes, 1)


def fijar_navegacion_calendario(cal):
    """Desactiva la navegacion interna para que solo manden los botones globales."""
    for attr in ("_l_month", "_r_month", "_l_year", "_r_year"):
        boton = getattr(cal, attr, None)
        if boton is not None:
            boton.state(["disabled"])


def boton_accion(parent, text, command, bg=BTN, width=24):
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


class FrameSeleccionFecha(FrameBase):
    """Frame para seleccionar fecha de una nueva reservación."""
    def __init__(self, master, **kwargs):
        self.calendarios_actuales = []
        self.fechas_ocupadas = set()
        super().__init__(master, **kwargs)

    def configurar(self):
        tk.Label(self, text="Disponibilidad para reservar", font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(16, 2))
        tk.Label(self, text="Selecciona una fecha libre para apartar el salon.", font=("Arial", 10), bg=BG, fg="#555").pack()
        
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
        self.btn_prev = boton_accion(frame_navegacion, text="< Anterior",
                                 command=lambda: self.actualizar_calendarios("prev"), bg="#6B7280", width=14)
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 12, "bold"), bg=BG, fg=TXT)
        self.lbl_info.pack(side="left", padx=20, expand=True)
        
        self.btn_next = boton_accion(frame_navegacion, text="Siguiente >",
                                 command=lambda: self.actualizar_calendarios("next"), bg=BTN2, width=14)
        self.btn_next.pack(side="left", padx=10)
        
        self.btn_reset = boton_accion(frame_navegacion, text="Ir a hoy",
                                  command=lambda: self.actualizar_calendarios("reset"), bg="#374151", width=12)
        self.btn_reset.pack(side="left", padx=10)
        
        # Acciones visibles antes de los calendarios para que no queden fuera de pantalla.
        frame_botones = tk.Frame(frame_principal, bg=BG)
        frame_botones.pack(pady=8, fill="x")
        
        boton_accion(frame_botones, text="Aceptar fecha seleccionada",
                  command=self.validar_fecha, bg=BTN, width=28).pack(side="left", padx=8)
        
        boton_accion(frame_botones, text="Volver al menu",
                  command=lambda: self.volver(FrameMenuAdmin), bg="#777", width=20).pack(side="left", padx=8)
        
        # Cargar calendarios iniciales
        self.actualizar_calendarios("reset")
        
        # Instrucciones
        tk.Label(self, text="Verde: disponible. Rojo: ocupado. Los controles de mes estan fijos para evitar duplicados.",
                 font=("Arial", 10), fg="#555", bg=BG).pack(pady=5)

    def crear_calendario(self, año, mes):
        """Crea un calendario optimizado."""
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
            bordercolor='#D1D5DB',
            headersbackground='#F3F4F6',
            headersforeground='#333',
            normalbackground='#ECFDF5',
            normalforeground='black',
            weekendbackground='#ECFDF5',
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
        
        fijar_navegacion_calendario(cal)
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
        
        # Limpiar frame
        for widget in self.frame_cals.winfo_children():
            widget.destroy()
        
        fecha_base = sumar_meses(datetime.date(self.manana.year, self.manana.month, 1), self.master.calendario_offset)
        meses_a_mostrar = []
        for i in range(MESES_POR_PAGINA):
            fecha_mes = sumar_meses(fecha_base, i)
            meses_a_mostrar.append((fecha_mes.year, fecha_mes.month))
        
        self.lbl_info.config(text=formatear_rango_meses(meses_a_mostrar))
        
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
            cal.bind("<<CalendarMonthChanged>>", lambda event, anio=año, mes_cal=mes: self.bloquear_cambio_mes(event, anio, mes_cal))

    def bloquear_cambio_mes(self, event, año, mes):
        """Mantiene cada calendario en su mes asignado aunque reciba navegacion interna."""
        widget = event.widget
        mes_actual, año_actual = widget.get_displayed_month()
        if mes_actual != mes or año_actual != año:
            widget.see(datetime.date(año, mes, 1))
            fijar_navegacion_calendario(widget)

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

class FrameCalendario(FrameBase):
    """Frame que muestra el calendario de eventos."""
    def __init__(self, master, **kwargs):
        self.calendarios_actuales = []
        self.eventos_por_fecha = {}
        super().__init__(master, **kwargs)

    def configurar(self):
        self.master.origen_actual = "calendario"
        
        tk.Label(self, text="Calendario de eventos", font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(16, 2))
        tk.Label(self, text="Revisa disponibilidad, eventos programados y eventos ya realizados.", font=("Arial", 10), bg=BG, fg="#555").pack()
        
        # Cargar eventos
        eventos = GestorArchivos.cargar_eventos()
        self.eventos_por_fecha = {e.fecha: e for e in eventos}
        
        self.hoy = datetime.date.today()
        self.semestre_actual = inicio_semestre(self.hoy)
        self.limite_historial = datetime.date(self.hoy.year - 2, 1, 1)
        
        # Frame principal
        frame_principal = tk.Frame(self, bg=BG)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para navegación
        frame_navegacion = tk.Frame(frame_principal, bg=BG)
        frame_navegacion.pack(pady=5, fill="x")
        
        # Botones de navegación
        self.btn_prev = boton_accion(frame_navegacion, text="< Anterior",
                                 command=lambda: self.actualizar_calendarios("prev"), bg="#6B7280", width=14)
        self.btn_prev.pack(side="left", padx=10)
        
        self.lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 12, "bold"), bg=BG, fg=TXT)
        self.lbl_info.pack(side="left", padx=20, expand=True)
        
        self.btn_next = boton_accion(frame_navegacion, text="Siguiente >",
                                 command=lambda: self.actualizar_calendarios("next"), bg=BTN2, width=14)
        self.btn_next.pack(side="left", padx=10)
        
        self.btn_reset = boton_accion(frame_navegacion, text="Ir a hoy",
                                  command=lambda: self.actualizar_calendarios("reset"), bg="#374151", width=12)
        self.btn_reset.pack(side="left", padx=10)
        
        frame_botones = tk.Frame(frame_principal, bg=BG)
        frame_botones.pack(pady=8, fill="x")
        
        boton_accion(frame_botones, text="Volver al menu",
                  command=lambda: self.volver(FrameMenuAdmin), bg="#777", width=20).pack(side="left", padx=8)
        
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
            bordercolor='#D1D5DB',
            headersbackground='#F3F4F6',
            headersforeground='#333',
            normalbackground='#ECFDF5',
            normalforeground='black',
            weekendbackground='#ECFDF5',
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
        
        fijar_navegacion_calendario(cal)
        return cal

    def actualizar_calendarios(self, direccion):
        """Actualiza los calendarios mostrados."""
        if direccion == "prev":
            self.master.calendario_offset -= MESES_POR_PAGINA
        elif direccion == "next":
            self.master.calendario_offset += MESES_POR_PAGINA
        else:
            self.master.calendario_offset = 0
        
        # Limpiar frame
        for widget in self.frame_cals.winfo_children():
            widget.destroy()
        
        fecha_base = sumar_meses(self.semestre_actual, self.master.calendario_offset)
        while fecha_base < self.limite_historial:
            self.master.calendario_offset += MESES_POR_PAGINA
            fecha_base = sumar_meses(self.semestre_actual, self.master.calendario_offset)

        meses_a_mostrar = []
        for i in range(MESES_POR_PAGINA):
            fecha_mes = sumar_meses(fecha_base, i)
            meses_a_mostrar.append((fecha_mes.year, fecha_mes.month))

        self.lbl_info.config(text=formatear_rango_meses(meses_a_mostrar))
        
        # Actualizar botones
        semestre_anterior = sumar_meses(fecha_base, -MESES_POR_PAGINA)
        self.btn_prev.config(state="normal" if semestre_anterior >= self.limite_historial else "disabled")
        self.btn_next.config(state="normal")
        
        # Crear calendarios
        self.calendarios_actuales = []
        for i, (año, mes) in enumerate(meses_a_mostrar):
            cal = self.crear_calendario(año, mes)
            row = i // 3
            col = i % 3
            cal.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.calendarios_actuales.append(cal)
            cal.bind("<<CalendarSelected>>", self.on_date_selected)
            cal.bind("<<CalendarMonthChanged>>", lambda event, anio=año, mes_cal=mes: self.bloquear_cambio_mes(event, anio, mes_cal))

    def bloquear_cambio_mes(self, event, año, mes):
        """Mantiene cada calendario en su mes asignado aunque reciba navegacion interna."""
        widget = event.widget
        mes_actual, año_actual = widget.get_displayed_month()
        if mes_actual != mes or año_actual != año:
            widget.see(datetime.date(año, mes, 1))
            fijar_navegacion_calendario(widget)

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
        info_ventana.geometry("640x680")
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

        self.mostrar_resumen_analisis(frame_info, evento)
        
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

    def mostrar_resumen_analisis(self, parent, evento):
        frame = tk.Frame(parent, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
        frame.pack(fill="x", pady=8)

        tk.Label(frame, text="Analisis del evento", font=("Arial", 12, "bold"), bg="white", fg=TXT).pack(anchor="w", padx=10, pady=(8, 2))

        resumen = self.obtener_resumen_analisis_evento(evento)
        for titulo, valor in resumen:
            fila = tk.Frame(frame, bg="white")
            fila.pack(fill="x", padx=10, pady=2)
            tk.Label(fila, text=f"{titulo}:", font=("Arial", 10, "bold"), bg="white", fg=TXT, width=24, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, font=("Arial", 10), bg="white", fg="#666", anchor="w").pack(side="left", fill="x", expand=True)

        tk.Label(frame, text="Pendiente: conectar comentarios, propinas y analisis socioeconomico cuando esos datos existan.",
                 font=("Arial", 8), bg="white", fg="#777", wraplength=520, justify="left").pack(anchor="w", padx=10, pady=(4, 8))

    def obtener_resumen_analisis_evento(self, evento):
        return [
            ("Comentarios del evento", "Aun no hay datos para mostrar"),
            ("Propinas de meseros", "Aun no hay datos para mostrar"),
            ("Categoria socioeconomica", "Aun no hay datos para mostrar"),
        ]

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
