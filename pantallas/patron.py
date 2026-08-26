import datetime
import re
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


def numero_desde_texto(valor):
    texto = re.sub(r"[^\d,.\-]", "", str(valor or ""))
    if "," in texto and "." in texto:
        texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        if len(partes[-1]) == 2:
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", texto)
    if not match:
        return 0.0
    try:
        return float(match.group(0))
    except ValueError:
        return 0.0


def formato_moneda(valor):
    return f"${valor:,.2f}"


SERVICIOS_FIJOS_CROQUIS = {
    "cocina": ("COC", "izquierda", 3, False),
    "barra": ("BAR", "izquierda", 4, False),
    "pantalla": ("PAN", "derecha", 1, False),
    "mesa_pastel": ("PAS", "derecha", 2, False),
    "dulces": ("DUL", "derecha", 3, False),
    "area_fotos": ("FOT", "derecha", 5, True),
}


def mesas_visibles_evento(evento):
    return list(evento.mesas)


def crear_area_scroll(parent, bg=BG, padx=0, pady=0):
    contenedor = tk.Frame(parent, bg=bg)
    contenedor.pack(fill="both", expand=True, padx=padx, pady=pady)

    canvas = tk.Canvas(contenedor, bg=bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    contenido = tk.Frame(canvas, bg=bg)

    ventana = canvas.create_window((0, 0), window=contenido, anchor="nw")

    def actualizar_scroll(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajustar_ancho(event):
        canvas.itemconfigure(ventana, width=event.width)

    def activar_rueda(_event):
        canvas.bind_all("<MouseWheel>", mover_rueda)

    def desactivar_rueda(_event):
        canvas.unbind_all("<MouseWheel>")

    def mover_rueda(event):
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            canvas.unbind_all("<MouseWheel>")

    contenido.bind("<Configure>", actualizar_scroll)
    canvas.bind("<Configure>", ajustar_ancho)
    canvas.bind("<Enter>", activar_rueda)
    canvas.bind("<Leave>", desactivar_rueda)
    canvas.bind("<Destroy>", desactivar_rueda)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return contenido


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
        
        boton_accion(frame_botones, text="Historial en lista",
                  command=self.mostrar_historial_eventos, bg="#7C3AED", width=20).pack(side="left", padx=8)

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

    def fecha_evento_dt(self, evento):
        for formato in ["%m/%d/%yy", "%m/%d/%y", "%m/%d/%Y"]:
            try:
                return datetime.datetime.strptime(evento.fecha, formato).date()
            except ValueError:
                continue
        return None

    def mostrar_historial_eventos(self):
        eventos = []
        for evento in GestorArchivos.cargar_eventos():
            fecha_dt = self.fecha_evento_dt(evento)
            if fecha_dt:
                eventos.append((fecha_dt, evento))
        eventos.sort(key=lambda item: item[0], reverse=True)

        ventana = tk.Toplevel(self)
        ventana.title("Historial de eventos")
        ventana.geometry("760x560")
        ventana.configure(bg=BG)

        contenedor = tk.Frame(ventana, bg=BG)
        contenedor.pack(fill="both", expand=True, padx=16, pady=12)

        tk.Label(contenedor, text="Historial de eventos", font=("Arial", 16, "bold"), bg=BG, fg=TXT).pack(anchor="w")
        tk.Label(contenedor, text="Lista rapida para consultar eventos pasados, actuales y futuros.",
                 font=("Arial", 10), bg=BG, fg="#555").pack(anchor="w", pady=(0, 8))

        frame_lista = tk.Frame(contenedor, bg=BG)
        frame_lista.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        lista = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, font=("Arial", 10), height=18)
        lista.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=lista.yview)

        for fecha_dt, evento in eventos:
            if fecha_dt < self.hoy:
                estado = "REALIZADO"
            elif fecha_dt == self.hoy:
                estado = "HOY"
            else:
                estado = "PROGRAMADO"
            total_mesas = len(mesas_visibles_evento(evento))
            lista.insert(tk.END, f"{fecha_dt.strftime('%d/%m/%Y')} - {estado} - {evento.total_invitados()} invitados - {total_mesas} mesas")

        if not eventos:
            lista.insert(tk.END, "No hay eventos guardados.")

        acciones = tk.Frame(contenedor, bg=BG)
        acciones.pack(fill="x", pady=10)

        def abrir_seleccion():
            seleccion = lista.curselection()
            if not seleccion or not eventos:
                messagebox.showinfo("Historial", "Selecciona un evento.")
                return
            fecha_dt, evento = eventos[seleccion[0]]
            self.mostrar_info_evento(evento, fecha_dt)

        tk.Button(acciones, text="Abrir detalle", command=abrir_seleccion,
                  bg=BTN, fg="white", width=18, height=2).pack(side="left", padx=(0, 8))
        tk.Button(acciones, text="Cerrar", command=ventana.destroy,
                  bg="#777", fg="white", width=18, height=2).pack(side="left")

    def mostrar_info_evento(self, evento, fecha_dt):
        """Muestra información detallada del evento."""
        info_ventana = tk.Toplevel(self)
        info_ventana.title(f"Evento del {evento.fecha}")
        info_ventana.geometry("700x680")
        info_ventana.minsize(620, 520)
        info_ventana.resizable(True, True)
        info_ventana.configure(bg=BG)
        
        frame_info = crear_area_scroll(info_ventana, BG, padx=20, pady=20)
        
        # Título
        tk.Label(frame_info, text=f"EVENTO - {evento.fecha}", 
                font=("Arial", 16, "bold"), bg=BG, fg=TXT).pack(pady=10)
        
        # Información básica
        frame_datos = tk.Frame(frame_info, bg=BG)
        frame_datos.pack(fill="x", pady=10)
        
        tk.Label(frame_datos, text=f"Mesa Principal: {evento.principal} personas", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        mesas_visibles = mesas_visibles_evento(evento)
        total_mesas = len(mesas_visibles)
        tk.Label(frame_datos, text=f"Total de mesas: {total_mesas}", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        total_invitados = evento.total_invitados()
        tk.Label(frame_datos, text=f"Total de invitados: {total_invitados}", 
                font=("Arial", 12, "bold"), bg=BG, anchor="w").pack(fill="x", pady=5)

        servicios = getattr(evento, "servicios", {})
        frame_servicios = tk.Frame(frame_info, bg=BG)
        frame_servicios.pack(fill="x", pady=(4, 10))
        tk.Label(frame_servicios, text="Servicios rentados:",
                 font=("Arial", 11, "bold"), bg=BG, fg=TXT).pack(anchor="w")
        for clave, texto in [
            ("pantalla", "Pantalla"),
            ("mesa_pastel", "Mesa de pastel"),
            ("dulces", "Mesa de dulces"),
            ("cocina", "Cocina / comida del salon"),
            ("barra", "Barra"),
            ("area_fotos", "Area de fotos"),
            ("animador", "Animador / extra"),
        ]:
            estado = "Si" if servicios.get(clave, False) else "No"
            tk.Label(frame_servicios, text=f"  {texto}: {estado}",
                     font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
        
        # Mostrar nombres de mesas
        if mesas_visibles:
            frame_mesas = tk.Frame(frame_info, bg=BG)
            frame_mesas.pack(fill="x", pady=10)
            
            tk.Label(frame_mesas, text="Mesas asignadas:", 
                    font=("Arial", 11, "bold"), bg=BG).pack(anchor="w")
            
            for i, mesa in enumerate(mesas_visibles[:5]):
                if mesa.nombre:
                    tk.Label(frame_mesas, text=f"  • {mesa.nombre}: {mesa.personas} personas", 
                            font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
            
            if len(mesas_visibles) > 5:
                tk.Label(frame_mesas, text=f"  ... y {len(mesas_visibles) - 5} mesas más", 
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

        frame_dashboard = tk.Frame(frame_info, bg=BG)
        frame_dashboard.pack(pady=(0, 10))
        if fecha_dt < self.hoy:
            tk.Button(frame_dashboard, text="Informacion completa",
                     command=lambda: self.mostrar_informacion_completa(evento, fecha_dt),
                     bg="#7C3AED", fg="white", width=28, height=2).pack()
        else:
            tk.Button(frame_dashboard, text="Informacion completa",
                     state="disabled", disabledforeground="#777",
                     width=28, height=2).pack(side="left", padx=5)
            if fecha_dt > self.hoy:
                tk.Button(frame_dashboard, text="Eliminar evento",
                         command=lambda: self.eliminar_evento_calendario(evento, info_ventana),
                         bg="#DC2626", fg="white", width=20, height=2).pack(side="left", padx=5)

        self.mostrar_resumen_analisis(frame_info, evento)
        
        # Botones
        frame_botones = tk.Frame(frame_info, bg=BG)
        frame_botones.pack(pady=20)
        
        if mesas_visibles:
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

    def eliminar_evento_calendario(self, evento, ventana_actual):
        confirmar = messagebox.askyesno(
            "Eliminar evento",
            f"Esta accion eliminara el evento del {evento.fecha} y su organizacion asociada si existe.\n\nDeseas continuar?"
        )
        if not confirmar:
            return

        eliminado = GestorArchivos.eliminar_evento(evento.fecha)
        if not eliminado:
            messagebox.showwarning("Eliminar evento", "No se encontro el evento para eliminar.")
            return

        ventana_actual.destroy()
        eventos = GestorArchivos.cargar_eventos()
        self.eventos_por_fecha = {e.fecha: e for e in eventos}
        self.actualizar_calendarios("reset")
        messagebox.showinfo("Eliminar evento", "Evento eliminado correctamente.")

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

        tk.Label(frame, text="El resumen usa comentarios y propinas registradas; el nivel socioeconomico queda como estimacion hasta capturarlo directamente.",
                 font=("Arial", 8), bg="white", fg="#777", wraplength=520, justify="left").pack(anchor="w", padx=10, pady=(4, 8))

    def obtener_resumen_analisis_evento(self, evento):
        analisis = self.analizar_evento(evento)
        return [
            ("Comentarios del evento", analisis["resumen_comentarios"]),
            ("Propinas de meseros", analisis["resumen_propinas"]),
            ("Categoria socioeconomica", analisis["nivel_socioeconomico"]),
        ]

    def comentarios_del_evento(self, evento):
        comentarios = []
        try:
            comentarios.extend([
                dict(c, fuente="general")
                for c in GestorArchivos.cargar_comentarios()
                if c.get("fecha") == evento.fecha
            ])
        except Exception:
            pass

        try:
            comentarios.extend([
                dict(c.to_dict(), fuente="mesero")
                for c in GestorArchivos.cargar_comentarios_mesero()
                if c.fecha == evento.fecha
            ])
        except Exception:
            pass

        try:
            comentarios.extend([
                dict(c.to_dict(), fuente="evento")
                for c in GestorArchivos.cargar_comentarios_evento()
                if c.fecha == evento.fecha
            ])
        except Exception:
            pass

        return comentarios

    def analizar_evento(self, evento):
        comentarios = self.comentarios_del_evento(evento)
        organizacion = GestorArchivos.buscar_organizacion_por_fecha(evento.fecha)
        num_meseros = len(organizacion.meseros) if organizacion else 0

        calificaciones = []
        ganancias = []
        destacados = []
        buenos = neutrales = malos = 0

        for comentario in comentarios:
            calificacion = numero_desde_texto(comentario.get("calificacion") or comentario.get("calificacion_promedio"))
            if calificacion > 0:
                calificaciones.append(calificacion)
                if calificacion >= 4:
                    buenos += 1
                elif calificacion >= 3:
                    neutrales += 1
                else:
                    malos += 1

            ganancia = numero_desde_texto(comentario.get("ganancia") or comentario.get("ganancia_total"))
            if ganancia > 0:
                ganancias.append(ganancia)

            for campo in ("sentir", "observaciones", "reporte", "satisfaccion_general"):
                texto = str(comentario.get(campo, "")).strip()
                if texto and texto.lower() not in {"n/a", "na", "ninguno"}:
                    destacados.append(texto)

        total_propinas = sum(ganancias)
        promedio_propina = total_propinas / len(ganancias) if ganancias else 0
        propina_por_mesero = total_propinas / num_meseros if num_meseros else 0
        calificacion_promedio = sum(calificaciones) / len(calificaciones) if calificaciones else 0

        if comentarios:
            resumen_comentarios = f"{len(comentarios)} comentario(s), calificacion promedio {calificacion_promedio:.1f}/5" if calificacion_promedio else f"{len(comentarios)} comentario(s) sin calificacion"
        else:
            resumen_comentarios = "Sin comentarios registrados"

        resumen_propinas = formato_moneda(total_propinas) if total_propinas else "Sin propinas registradas"

        return {
            "comentarios": comentarios,
            "destacados": destacados[:5],
            "buenos": buenos,
            "neutrales": neutrales,
            "malos": malos,
            "calificacion_promedio": calificacion_promedio,
            "total_propinas": total_propinas,
            "promedio_propina": promedio_propina,
            "propina_por_mesero": propina_por_mesero,
            "num_meseros": num_meseros,
            "organizacion": organizacion,
            "resumen_comentarios": resumen_comentarios,
            "resumen_propinas": resumen_propinas,
            "nivel_socioeconomico": self.estimar_nivel_socioeconomico(promedio_propina),
        }

    def estimar_nivel_socioeconomico(self, promedio_propina):
        if promedio_propina >= 800:
            return "Alto, estimado por propinas registradas"
        if promedio_propina >= 400:
            return "Medio alto, estimado por propinas registradas"
        if promedio_propina > 0:
            return "Medio / por confirmar con mas datos"
        return "Sin datos suficientes"

    def mostrar_informacion_completa(self, evento, fecha_dt):
        analisis = self.analizar_evento(evento)

        ventana = tk.Toplevel(self)
        ventana.title(f"Informacion completa - {evento.fecha}")
        ventana.geometry("1060x680")
        ventana.minsize(860, 560)
        ventana.resizable(True, True)
        ventana.configure(bg=BG)

        contenedor = tk.Frame(ventana, bg=BG)
        contenedor.pack(fill="both", expand=True, padx=16, pady=12)

        header = tk.Frame(contenedor, bg=BG)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text=f"Informacion completa del evento - {evento.fecha}",
                 font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(side="left")
        tk.Button(header, text="Cerrar", command=ventana.destroy,
                  bg="#777", fg="white", relief="flat", width=14, height=2).pack(side="right")

        cuerpo = crear_area_scroll(contenedor, BG)
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)

        izquierda = tk.Frame(cuerpo, bg=BG)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        derecha = tk.Frame(cuerpo, bg=BG)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        croquis = self.tarjeta_dashboard(izquierda, "Croquis del evento")
        self.dibujar_croquis_resumen(croquis, evento, analisis["organizacion"])

        resumen = self.tarjeta_dashboard(izquierda, "Resumen basico")
        self.fila_dashboard(resumen, "Fecha", evento.fecha)
        self.fila_dashboard(resumen, "Estado", "Realizado" if fecha_dt < self.hoy else "Programado")
        self.fila_dashboard(resumen, "Mesas", str(len(mesas_visibles_evento(evento))))
        self.fila_dashboard(resumen, "Personas", str(evento.total_invitados()))
        self.fila_dashboard(resumen, "Mesa principal", f"{evento.principal} personas")
        self.fila_dashboard(resumen, "Servicios", self.texto_servicios_evento(evento))

        comentarios = self.tarjeta_dashboard(derecha, "Comentarios destacados")
        if analisis["destacados"]:
            for texto in analisis["destacados"]:
                tk.Label(comentarios, text=f"- {texto}", font=("Arial", 9), bg="white", fg="#555",
                         wraplength=500, justify="left").pack(anchor="w", padx=12, pady=2)
        else:
            tk.Label(comentarios, text="Sin comentarios registrados para este evento.",
                     font=("Arial", 9), bg="white", fg="#777").pack(anchor="w", padx=12, pady=(4, 10))

        estadisticas = self.tarjeta_dashboard(derecha, "Estadisticas por comentarios")
        calificacion = analisis["calificacion_promedio"]
        self.fila_dashboard(estadisticas, "Calificacion promedio", f"{calificacion:.1f}/5" if calificacion else "Sin datos")
        self.fila_dashboard(estadisticas, "Comentarios buenos", str(analisis["buenos"]))
        self.fila_dashboard(estadisticas, "Comentarios neutrales", str(analisis["neutrales"]))
        self.fila_dashboard(estadisticas, "Comentarios malos", str(analisis["malos"]))

        socio = self.tarjeta_dashboard(derecha, "Nivel socioeconomico")
        self.fila_dashboard(socio, "Estimacion", analisis["nivel_socioeconomico"])
        tk.Label(socio, text="Nota: por ahora se estima con propinas registradas; despues se puede agregar una captura directa del tipo de cliente.",
                 font=("Arial", 8), bg="white", fg="#777", wraplength=500, justify="left").pack(anchor="w", padx=12, pady=(2, 8))

        propinas = self.tarjeta_dashboard(derecha, "Propinas aproximadas")
        self.fila_dashboard(propinas, "Total registrado", formato_moneda(analisis["total_propinas"]) if analisis["total_propinas"] else "Sin datos")
        self.fila_dashboard(propinas, "Promedio reportado", formato_moneda(analisis["promedio_propina"]) if analisis["promedio_propina"] else "Sin datos")
        self.fila_dashboard(propinas, "Meseros organizados", str(analisis["num_meseros"]) if analisis["num_meseros"] else "Sin organizacion")
        self.fila_dashboard(propinas, "Estimado por mesero", formato_moneda(analisis["propina_por_mesero"]) if analisis["propina_por_mesero"] else "Sin datos")

        self.mostrar_resumen_meseros(izquierda, analisis)

    def tarjeta_dashboard(self, parent, titulo):
        frame = tk.Frame(parent, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
        frame.pack(fill="x", pady=6)
        tk.Label(frame, text=titulo, font=("Arial", 12, "bold"), bg="white", fg=TXT).pack(anchor="w", padx=12, pady=(9, 4))
        return frame

    def fila_dashboard(self, parent, etiqueta, valor):
        fila = tk.Frame(parent, bg="white")
        fila.pack(fill="x", padx=12, pady=2)
        tk.Label(fila, text=f"{etiqueta}:", font=("Arial", 9, "bold"), bg="white", fg=TXT, width=20, anchor="w").pack(side="left")
        tk.Label(fila, text=valor, font=("Arial", 9), bg="white", fg="#555", anchor="w",
                 wraplength=320, justify="left").pack(side="left", fill="x", expand=True)

    def texto_servicios_evento(self, evento):
        servicios = getattr(evento, "servicios", {})
        etiquetas = {
            "pantalla": "pantalla",
            "mesa_pastel": "mesa pastel",
            "dulces": "dulces",
            "cocina": "cocina",
            "barra": "barra",
            "area_fotos": "fotos",
            "animador": "animador/extra",
        }
        activos = [texto for clave, texto in etiquetas.items() if servicios.get(clave, clave == "area_fotos")]
        return ", ".join(activos) if activos else "Sin servicios extra"

    def dibujar_croquis_resumen(self, parent, evento, organizacion=None):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=12, pady=(0, 10))
        cell = 52
        canvas = tk.Canvas(frame, width=(COLUMNAS + 2) * cell, height=(FILAS + 1) * cell,
                           bg="#F8FAFC", highlightthickness=1, highlightbackground="#CBD5E1")
        canvas.pack(side="left")

        canvas.create_rectangle(3 * cell, 4, 5 * cell, int(cell * 0.75),
                                fill="#8B5E34", outline="#6B3F1D", width=2)
        canvas.create_text(4 * cell, int(cell * 0.38),
                           text=f"Principal\n{evento.principal}", fill="white",
                           font=("Arial", 8, "bold"))
        canvas.create_rectangle(3 * cell, 1 * cell, 5 * cell, 3 * cell,
                                fill="#111827", outline="#030712", width=2)
        canvas.create_text(4 * cell, int(2 * cell), text="PISTA",
                           fill="white", font=("Arial", 10, "bold"))
        self.dibujar_servicios_resumen(canvas, evento, cell)

        colores_org = self.colores_organizacion(organizacion)
        for mesa in evento.mesas:
            x1 = mesa.col * cell
            y1 = mesa.fila * cell
            x2 = (mesa.col + 1) * cell
            y2 = (mesa.fila + 1) * cell
            color = colores_org.get((mesa.col, mesa.fila), mesa.color)
            if color == "lightgray":
                color = "#E5E7EB"
            canvas.create_oval(x1 + 7, y1 + 7, x2 - 7, y2 - 7,
                               fill=color, outline="#94A3B8", width=2)
            texto = str(mesa.personas)
            if mesa.nombre:
                nombre = str(mesa.nombre)
                if len(nombre) > 8:
                    nombre = nombre[:7] + "."
                texto = f"{mesa.personas}\n{nombre}"
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                               text=texto, fill=TXT, font=("Arial", 8, "bold"))

    def dibujar_servicios_resumen(self, canvas, evento, cell):
        servicios = getattr(evento, "servicios", {})
        for clave, (texto, lado, fila, siempre) in SERVICIOS_FIJOS_CROQUIS.items():
            if lado == "izquierda":
                x1 = 6
                x2 = cell - 6
            else:
                x1 = (COLUMNAS + 1) * cell + 6
                x2 = (COLUMNAS + 2) * cell - 6
            y1 = fila * cell + 8
            y2 = (fila + 1) * cell - 8
            activo = True if siempre else bool(servicios.get(clave, False))
            fill = "#10B981" if activo else "#CBD5E1"
            outline = "#047857" if activo else "#94A3B8"
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                               text=texto, fill="white" if activo else "#475569",
                               font=("Arial", 6, "bold"))

    def colores_organizacion(self, organizacion):
        colores = {}
        if not organizacion:
            return colores
        for clave, color in organizacion.colores.items():
            numeros = re.findall(r"\d+", str(clave))
            if len(numeros) >= 2:
                colores[(int(numeros[0]), int(numeros[1]))] = color
        return colores

    def mostrar_resumen_meseros(self, parent, analisis):
        organizacion = analisis["organizacion"]
        frame = self.tarjeta_dashboard(parent, "Meseros y zonas")
        if not organizacion:
            tk.Label(frame, text="No hay organizacion guardada para este evento.",
                     font=("Arial", 9), bg="white", fg="#777").pack(anchor="w", padx=12, pady=(0, 10))
            return

        estimado = analisis["propina_por_mesero"]
        for color, personas in organizacion.meseros.items():
            nombre = getattr(organizacion, "nombres_meseros", {}).get(color, color)
            fila = tk.Frame(frame, bg="white")
            fila.pack(fill="x", padx=12, pady=2)
            muestra = tk.Canvas(fila, width=18, height=18, bg="white", highlightthickness=0)
            muestra.pack(side="left", padx=(0, 6))
            muestra.create_rectangle(2, 2, 16, 16, fill=color, outline="#555")
            texto = f"{nombre}: {personas} personas asignadas"
            if estimado:
                texto += f" | propina estimada {formato_moneda(estimado)}"
            tk.Label(fila, text=texto, font=("Arial", 9), bg="white", fg="#555",
                     anchor="w").pack(side="left", fill="x", expand=True)

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
