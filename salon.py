import tkinter as tk
from tkinter import simpledialog, messagebox
from tkcalendar import Calendar
import json, os, datetime

CELL = 90
FILAS = 5
COLUMNAS = 6
ARCHIVO = "eventos.json"
ARCHIVO_ORG = "organizacion.json"
ARCHIVO_COMENTARIOS = "comentarios.json"
MESES_POR_PAGINA = 6
ARCHIVO_COMENTARIOS_MESERO = "comentarios_mesero.json"
ARCHIVO_COMENTARIOS_EVENTO = "comentarios_evento.json"

mesa_principal_valor = 2
valores_mesas = {}
total_invitados = 0
color_actual = "lightgray"
asociaciones_colores = {}
mesas_colores = {}
calendario_cache = {}  # Cache para calendarios ya creados
calendario_offset = 0
volver_a_comentarios = False  # Para saber si volver a comentarios o calendario
origen_actual = None  # Puede ser "calendario", "comentarios", "capitan", etc.
usuario_actual = None
rol_actual = None

# ======== ESTÉTICA ========
BG = "#f2f2f2"
BTN = "#4CAF50"
BTN2 = "#2196F3"
TXT = "#333"

# ---------------- ARCHIVOS ----------------
def cargar_eventos():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO,"r",encoding="utf8") as f:
        return json.load(f)

def guardar_evento(data):
    eventos = cargar_eventos()
    eventos.append(data)
    with open(ARCHIVO,"w",encoding="utf8") as f:
        json.dump(eventos,f,indent=4)

def cargar_org():
    if not os.path.exists(ARCHIVO_ORG):
        return []
    with open(ARCHIVO_ORG,"r",encoding="utf8") as f:
        return json.load(f)

def guardar_organizacion(data):
    lista = cargar_org()
    nueva = []
    reemplazo = False

    for o in lista:
        if o["fecha"] == data["fecha"]:
            nueva.append(data)   # reemplaza la existente
            reemplazo = True
        else:
            nueva.append(o)

    if not reemplazo:
        nueva.append(data)  # si no existía, se agrega

    with open(ARCHIVO_ORG,"w",encoding="utf8") as f:
        json.dump(nueva,f,indent=4)


def limpiar():
    for w in ventana.winfo_children():
        w.destroy()

def cargar_comentarios():
    if not os.path.exists(ARCHIVO_COMENTARIOS):
        return []
    with open(ARCHIVO_COMENTARIOS,"r",encoding="utf8") as f:
        return json.load(f)

def guardar_comentario(data):
    lista = cargar_comentarios()
    
    # Buscar si ya existe un comentario para esta fecha
    encontrado = False
    for i, c in enumerate(lista):
        if c.get("fecha") == data.get("fecha"):
            lista[i] = data  # Reemplazar
            encontrado = True
            break
    
    if not encontrado:
        lista.append(data)  # Agregar nuevo
    
    with open(ARCHIVO_COMENTARIOS, "w", encoding="utf8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

# ---------------- LOGIN ----------------
def login():
    limpiar()
    ventana.configure(bg=BG)
    frame=tk.Frame(ventana,bg=BG)
    frame.pack(expand=True)

    tk.Label(frame,text="Sistema Salón",font=("Arial",22,"bold"),bg=BG,fg=TXT).pack(pady=20)

    tk.Button(frame,text="Patrón / Admin",bg=BTN,fg="white",width=25,height=2,
              command=menu_admin).pack(pady=8)
    tk.Button(frame,text="Capitán",bg=BTN2,fg="white",width=25,height=2,
              command=menu_capitan).pack(pady=8)
    tk.Button(frame,text="Mesero",bg="#FF9800",fg="white",width=25,height=2,
              command=menu_mesero).pack(pady=8)

    tk.Button(frame,text="Salir",bg="#f44336",fg="white",width=25,height=2,
              command=ventana.destroy).pack(pady=15)

# ---------------- MENÚ ADMIN ----------------
def menu_admin():
    limpiar()
    ventana.configure(bg=BG)
    frame=tk.Frame(ventana,bg=BG)
    frame.pack(expand=True)

    tk.Label(frame,text="Menú Patrón",font=("Arial",20,"bold"),bg=BG).pack(pady=20)
    tk.Button(frame,text="Demostración",bg=BTN,width=30,height=2,command=vista_demo).pack(pady=5)
    tk.Button(frame,text="Reservación (Anfitrión)",bg=BTN,width=30,height=2,command=vista_reservacion).pack(pady=5)
    tk.Button(frame,text="Calendario",bg=BTN,width=30,height=2,command=vista_calendario).pack(pady=5)
    tk.Button(frame,text="Volver",bg="#777",fg="white",width=30,height=2,command=login).pack(pady=10)

# ---------------- MENÚ CAPITÁN ----------------
def menu_capitan():
    limpiar()
    ventana.configure(bg=BG)
    frame=tk.Frame(ventana,bg=BG)
    frame.pack(expand=True)

    tk.Label(frame,text="Menú Capitán",font=("Arial",20,"bold"),bg=BG).pack(pady=20)
    tk.Button(frame,text="Cargar evento",bg=BTN,width=30,height=2,command=vista_capitan).pack(pady=5)
    tk.Button(frame,text="Cargar organización",bg=BTN,width=30,height=2,command=vista_cargar_org).pack(pady=5)
    tk.Button(frame,text="Comparar evento",bg=BTN,width=30,height=2,command=vista_comparar).pack(pady=5)
    tk.Button(frame,text="Volver",bg="#777",fg="white",width=30,height=2,command=login).pack(pady=10)

# ---------------- MENÚ MESERO ----------------
def menu_mesero():
    limpiar()
    ventana.configure(bg=BG)
    frame=tk.Frame(ventana,bg=BG)
    frame.pack(expand=True)

    tk.Label(frame,text="Menú Mesero",font=("Arial",20,"bold"),bg=BG).pack(pady=20)
    tk.Button(frame,text="Ver organización",bg=BTN,width=30,height=2,command=vista_mesero_org).pack(pady=5)
    tk.Button(frame,text="Comentarios",bg=BTN,width=30,height=2,command=vista_mesero_comentarios).pack(pady=5)
    tk.Button(frame,text="Estadísticas",bg=BTN,width=30,height=2,command=vista_mesero_stats).pack(pady=5)
    tk.Button(frame,text="Volver",bg="#777",fg="white",width=30,height=2,command=login).pack(pady=10)

# ---------------- DEMO ----------------
def vista_demo():
    vista_croquis(modo="demo")

# ---------------- RESERVACIÓN ----------------
def vista_reservacion():
    limpiar()
    
    global calendario_offset
    global calendario_cache
    
    tk.Label(ventana, text="Fecha del evento", font=("Arial", 14, "bold")).pack(pady=5)
    
    # Cargar datos primero (rápido)
    eventos = cargar_eventos()
    fechas_ocupadas = {e["fecha"] for e in eventos if "fecha" in e}
    
    hoy = datetime.date.today()
    manana = hoy + datetime.timedelta(days=1)
    
    # Frame principal con estructura fija
    frame_principal = tk.Frame(ventana)
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Frame para controles de navegación
    frame_navegacion = tk.Frame(frame_principal)
    frame_navegacion.pack(pady=5, fill="x")
    
    # Variables para manejo de calendarios
    calendarios_actuales = []
    frame_cals = tk.Frame(frame_principal)
    frame_cals.pack(fill="both", expand=True, pady=10)
    
    # Preconfigurar grid para distribución uniforme
    for i in range(3):  # columnas
        frame_cals.grid_columnconfigure(i, weight=1, uniform="cal_col")
    for i in range(2):  # filas
        frame_cals.grid_rowconfigure(i, weight=1, uniform="cal_row")
    
    # Botones de navegación con estado inicial
    def update_nav_buttons():
        btn_prev.config(state="normal" if calendario_offset > 0 else "disabled")
        # Siempre permitir siguiente
        btn_next.config(state="normal")
    
    btn_prev = tk.Button(frame_navegacion, text="◀ Anterior", 
                        command=lambda: actualizar_calendarios("prev"))
    btn_prev.pack(side="left", padx=10)
    
    lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 10, "bold"))
    lbl_info.pack(side="left", padx=20, expand=True)
    
    btn_next = tk.Button(frame_navegacion, text="Siguiente ▶", 
                        command=lambda: actualizar_calendarios("next"))
    btn_next.pack(side="left", padx=10)
    
    btn_reset = tk.Button(frame_navegacion, text="Ir a hoy", 
                         command=lambda: actualizar_calendarios("reset"))
    btn_reset.pack(side="left", padx=10)
    
    # Función para crear un calendario optimizado
    def crear_calendario_optimizado(año, mes, fecha_base):
        clave = f"{año}-{mes}"
        
        # Verificar cache
        if clave in calendario_cache:
            cal = calendario_cache[clave]
            # Reconfigurar para nueva posición
            cal.grid(row=0, column=0)  # Posición temporal
            return cal
        
        # Crear nuevo calendario optimizado
        cal = Calendar(
            frame_cals,
            selectmode="day",
            date_pattern="mm/dd/yy",
            mindate=manana,
            year=año,
            month=mes,
            showweeknumbers=False,
            showothermonthdays=False,  # No mostrar días de otros meses
            firstweekday='sunday',
            font=("Arial", 8),  # Fuente más pequeña
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
            othermonthwebackground='white',
            othermonthweforeground='#ccc',
            cursor="hand2"
        )
        
        # Marcar fechas ocupadas
        for fecha_str in fechas_ocupadas:
            try:
                fecha_dt = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                if fecha_dt.year == año and fecha_dt.month == mes:
                    cal.calevent_create(fecha_dt, "Ocupado", "ocupado")
                    cal.tag_config("ocupado", background="#f44336", foreground="white")
            except:
                continue
        
        # Guardar en cache
        calendario_cache[clave] = cal
        
        return cal
    
    # Función principal para actualizar calendarios
    def actualizar_calendarios(direccion):
        nonlocal calendarios_actuales
        
        # Actualizar offset
        global calendario_offset
        if direccion == "prev":
            calendario_offset -= MESES_POR_PAGINA
        elif direccion == "next":
            calendario_offset += MESES_POR_PAGINA
        else:  # reset
            calendario_offset = 0
        
        # Limitar offset mínimo
        if calendario_offset < 0:
            calendario_offset = 0
        
        # Limpiar solo la configuración de grid, no destruir widgets
        for widget in frame_cals.winfo_children():
            widget.grid_forget()
        
        # Calcular nueva fecha base
        fecha_base = manana
        if calendario_offset > 0:
            meses_extra = calendario_offset
            año_extra = meses_extra // 12
            mes_extra = meses_extra % 12
            
            nuevo_mes = manana.month + mes_extra
            nuevo_año = manana.year + año_extra
            
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
        
        lbl_info.config(text=f"Mostrando: {fecha_base.strftime('%b %Y')} - {fecha_fin.strftime('%b %Y')}")
        
        # Crear/recuperar calendarios
        calendarios_actuales = []
        
        # Usar after para no bloquear la interfaz
        def cargar_calendarios_progresivo():
            for i in range(MESES_POR_PAGINA):
                mes = fecha_base.month + i
                año = fecha_base.year
                
                # Ajustar si pasamos de diciembre
                while mes > 12:
                    mes -= 12
                    año += 1
                
                # Crear o recuperar calendario
                cal = crear_calendario_optimizado(año, mes, fecha_base)
                
                # Posicionar en grid
                row = i // 3
                col = i % 3
                cal.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                calendarios_actuales.append(cal)
                
                # Actualizar interfaz progresivamente
                frame_cals.update_idletasks()
            
            # Actualizar botones de navegación
            update_nav_buttons()
            
            # Conectar eventos después de cargar
            conectar_eventos_calendarios()
        
        # Iniciar carga
        ventana.after(10, cargar_calendarios_progresivo)
    
    # Conectar eventos a calendarios
    def conectar_eventos_calendarios():
        def on_date_selected(event):
            widget = event.widget
            fecha_str = widget.get_date()
            if fecha_str:
                if fecha_str in fechas_ocupadas:
                    messagebox.showerror("No disponible", "Ese día ya está reservado")
                else:
                    try:
                        fecha_obj = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                        if fecha_obj >= manana:
                            vista_croquis(modo="anfitrion", fecha=fecha_str)
                        else:
                            messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha futura")
                    except ValueError:
                        pass
        
        for cal in calendarios_actuales:
            cal.bind("<<CalendarSelected>>", on_date_selected)
    
    # Cargar calendarios iniciales
    actualizar_calendarios("reset")
    
    # Función para validar fecha seleccionada
    def validar_fecha():
        fecha_seleccionada = None
        
        for cal in calendarios_actuales:
            fecha_str = cal.get_date()
            if fecha_str:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                    
                    if fecha_obj < manana:
                        messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha futura")
                        return
                    
                    if fecha_str in fechas_ocupadas:
                        messagebox.showerror("No disponible", "Ese día ya está reservado")
                        return
                    
                    vista_croquis(modo="anfitrion", fecha=fecha_str)
                    return
                    
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido")
                    return
        
        messagebox.showwarning("Error", "Por favor, selecciona una fecha")
    
    # Frame para botones de acción
    frame_botones = tk.Frame(frame_principal)
    frame_botones.pack(pady=20, fill="x")
    
    tk.Button(frame_botones, text="Aceptar fecha seleccionada", 
              command=validar_fecha, bg=BTN, fg="white", 
              width=25, height=2, font=("Arial", 10, "bold")).pack(padx=10)
    
    tk.Button(frame_botones, text="Volver al menú", 
              command=menu_admin, bg="#777", fg="white", 
              width=25, height=2).pack(padx=10)
    
    # Añadir indicador de carga rápida
    tk.Label(frame_principal, 
             text="Calendarios carga rápida",
             font=("Arial", 9), 
             fg="#4CAF50").pack(pady=5)
    
    # También permitir doble clic en el calendario para selección rápida
    def on_date_selected(event):
        widget = event.widget
        fecha_str = widget.get_date()
        if fecha_str:
            # Verificar inmediatamente si está disponible
            if fecha_str in fechas_ocupadas:
                messagebox.showerror("No disponible", "Ese día ya está reservado")
            else:
                try:
                    fecha_obj = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
                    if fecha_obj >= manana:
                        vista_croquis(modo="anfitrion", fecha=fecha_str)
                    else:
                        messagebox.showwarning("Fecha inválida", "Debes seleccionar una fecha futura")
                except ValueError:
                    pass
    
    # Conectar evento de doble clic a todos los calendarios
    for cal in calendarios_actuales:
        cal.bind("<<CalendarSelected>>", on_date_selected)
    
    # Añadir instrucciones
    tk.Label(ventana, 
             text="Instrucciones: 1) Selecciona una fecha haciendo clic en un día\n2) Haz clic en 'Aceptar fecha' o doble clic en la fecha",
             font=("Arial", 10), 
             fg="#555").pack(pady=5)
    
# ---------------- CALENDARIO ----------------
def vista_calendario():
    global calendario_offset
    global origen_actual
    origen_actual = "calendario"  # Establecer origen
    limpiar()
    
    tk.Label(ventana, text="Calendario de Eventos", font=("Arial", 14, "bold")).pack(pady=5)
    
    # Cargar eventos
    eventos = cargar_eventos()
    eventos_por_fecha = {e["fecha"]: e for e in eventos if "fecha" in e}
    
    hoy = datetime.date.today()
    print(f"Hoy es: {hoy}")
    print(f"Eventos cargados: {len(eventos)}")
    print(f"Eventos por fecha: {list(eventos_por_fecha.keys())}")
    
    # Frame principal
    frame_principal = tk.Frame(ventana)
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Frame para controles de navegación
    frame_navegacion = tk.Frame(frame_principal)
    frame_navegacion.pack(pady=5, fill="x")
    
    # Variable para calendarios actuales
    calendarios_actuales = []
    
    # Botones de navegación
    def update_nav_buttons():
        btn_prev.config(state="normal" if calendario_offset > 0 else "disabled")
        btn_next.config(state="normal")
    
    btn_prev = tk.Button(frame_navegacion, text="◀ Anterior", 
                        command=lambda: actualizar_calendarios("prev"))
    btn_prev.pack(side="left", padx=10)
    
    lbl_info = tk.Label(frame_navegacion, text="", font=("Arial", 10, "bold"))
    lbl_info.pack(side="left", padx=20, expand=True)
    
    btn_next = tk.Button(frame_navegacion, text="Siguiente ▶", 
                        command=lambda: actualizar_calendarios("next"))
    btn_next.pack(side="left", padx=10)
    
    btn_reset = tk.Button(frame_navegacion, text="Ir a hoy", 
                         command=lambda: actualizar_calendarios("reset"))
    btn_reset.pack(side="left", padx=10)
    
    # Frame para los calendarios
    frame_cals = tk.Frame(frame_principal)
    frame_cals.pack(fill="both", expand=True, pady=10)
    
    # Preconfigurar grid
    for i in range(3):
        frame_cals.grid_columnconfigure(i, weight=1, uniform="cal_col")
    for i in range(2):
        frame_cals.grid_rowconfigure(i, weight=1, uniform="cal_row")
    
    # Función para crear calendario optimizado - VERSIÓN CORREGIDA
    def crear_calendario_optimizado_cal(año, mes):
        cal = Calendar(
            frame_cals,
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
            othermonthwebackground='white',
            othermonthweforeground='#ccc',
            cursor="hand2"
        )
        
        # Marcar el día de hoy SIEMPRE
        if hoy.year == año and hoy.month == mes:
            print(f"Marcando hoy ({hoy}) en calendario {mes}/{año}")
            cal.calevent_create(hoy, "Hoy", "hoy")
            cal.tag_config("hoy", background="#2196F3", foreground="white")
        
        # Primero: Marcar TODOS los días pasados como gris
        # (luego sobrescribiremos los que tienen evento)
        if (año < hoy.year) or (año == hoy.year and mes < hoy.month):
            # Mes completo en el pasado
            for day in range(1, 32):
                try:
                    fecha_cal = datetime.date(año, mes, day)
                    if fecha_cal.month == mes and fecha_cal < hoy:
                        # Solo marcar si no es hoy (aunque en este caso no debería serlo)
                        if fecha_cal != hoy:
                            cal.calevent_create(fecha_cal, "Día pasado", "pasado")
                            cal.tag_config("pasado", background="#f0f0f0", foreground="#888")
                except ValueError:
                    continue
        elif año == hoy.year and mes == hoy.month:
            # Mes actual - solo días anteriores a hoy
            for day in range(1, hoy.day):
                try:
                    fecha_cal = datetime.date(año, mes, day)
                    if fecha_cal.month == mes:
                        cal.calevent_create(fecha_cal, "Día pasado", "pasado")
                        cal.tag_config("pasado", background="#f0f0f0", foreground="#888")
                except ValueError:
                    continue
        
        # Segundo: Marcar eventos existentes (esto sobrescribirá el gris donde haya eventos)
        for fecha_str, evento in eventos_por_fecha.items():
            try:
                # Intentar diferentes formatos de fecha
                fecha_dt = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_dt = datetime.datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_dt is None:
                    continue  # No se pudo parsear la fecha
                    
                if fecha_dt.year == año and fecha_dt.month == mes:
                    # Calcular total de personas
                    total_personas = evento.get('principal', 0) + sum(m.get('personas', 0) for m in evento.get('mesas', []))
                    
                    print(f"Marcando evento en {fecha_dt}: {total_personas} personas")
                    
                    # Determinar color según fecha
                    if fecha_dt < hoy:
                        # Evento pasado - AZUL (sobrescribe el gris)
                        cal.calevent_create(fecha_dt, f"Evento pasado: {total_personas} personas", "evento_pasado")
                        cal.tag_config("evento_pasado", background="#2196F3", foreground="white")
                    elif fecha_dt == hoy:
                        # Evento hoy - NARANJA
                        cal.calevent_create(fecha_cal, f"Evento HOY: {total_personas} personas", "evento_hoy")
                        cal.tag_config("evento_hoy", background="#FF9800", foreground="white")
                    else:
                        # Evento futuro - VERDE
                        cal.calevent_create(fecha_dt, f"Evento futuro: {total_personas} personas", "evento_futuro")
                        cal.tag_config("evento_futuro", background="#4CAF50", foreground="white")
                        
            except Exception as e:
                print(f"Error procesando evento {fecha_str}: {e}")
                continue
        
        return cal
    
    # Función principal para actualizar calendarios
    def actualizar_calendarios(direccion):
        nonlocal calendarios_actuales
        
        # Actualizar offset
        global calendario_offset
        if direccion == "prev":
            calendario_offset -= MESES_POR_PAGINA
        elif direccion == "next":
            calendario_offset += MESES_POR_PAGINA
        else:  # reset
            calendario_offset = 0
        
        # Limitar offset mínimo
        if calendario_offset < 0:
            calendario_offset = 0
        
        print(f"Offset actual: {calendario_offset}")
        
        # Limpiar frame
        for widget in frame_cals.winfo_children():
            widget.destroy()
        calendarios_actuales = []
        
        # Calcular fecha base - Empezar en enero del año actual
        año_actual = hoy.year
        mes_base = 1  # Enero
        
        # Ajustar según offset
        if calendario_offset > 0:
            total_meses = calendario_offset
            años_extra = total_meses // 12
            meses_extra = total_meses % 12
            
            mes_base += meses_extra
            año_actual += años_extra
            
            if mes_base > 12:
                mes_base -= 12
                año_actual += 1
        
        print(f"Mostrando calendarios desde mes {mes_base} del año {año_actual}")
        
        # Determinar rango de meses (siempre 6 meses)
        meses_a_mostrar = []
        
        if mes_base <= 6:
            # Primera mitad del año (Enero-Junio)
            for i in range(6):
                mes = mes_base + i
                año = año_actual
                if mes > 12:
                    mes -= 12
                    año += 1
                meses_a_mostrar.append((año, mes))
        else:
            # Segunda mitad del año (Julio-Diciembre)
            for i in range(6):
                mes = mes_base + i
                año = año_actual
                if mes > 12:
                    mes -= 12
                    año += 1
                meses_a_mostrar.append((año, mes))
        
        # Actualizar label
        nombres_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        primer_año, primer_mes = meses_a_mostrar[0]
        ultimo_año, ultimo_mes = meses_a_mostrar[-1]
        
        if primer_año == ultimo_año:
            lbl_info.config(text=f"Mostrando: {nombres_meses[primer_mes-1]} - {nombres_meses[ultimo_mes-1]} {primer_año}")
        else:
            lbl_info.config(text=f"Mostrando: {nombres_meses[primer_mes-1]} {primer_año} - {nombres_meses[ultimo_mes-1]} {ultimo_año}")
        
        # Crear calendarios
        def cargar_calendarios_progresivo():
            for i, (año_mes, mes_num) in enumerate(meses_a_mostrar):
                # Crear calendario
                cal = crear_calendario_optimizado_cal(año_mes, mes_num)
                
                # Posicionar
                row = i // 3
                col = i % 3
                cal.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                calendarios_actuales.append(cal)
                
                # Actualizar UI
                frame_cals.update_idletasks()
            
            # Actualizar botones y conectar eventos
            update_nav_buttons()
            conectar_eventos_calendarios()
        
        # Iniciar carga
        ventana.after(10, cargar_calendarios_progresivo)
    
    # Conectar eventos
    def conectar_eventos_calendarios():
        def on_date_selected(event):
            widget = event.widget
            fecha_str = widget.get_date()
            
            if not fecha_str:
                return
            
            print(f"Fecha seleccionada desde calendario: {fecha_str}")
            
            # Parsear fecha del calendario (formato mm/dd/yy)
            try:
                fecha_dt = datetime.datetime.strptime(fecha_str, "%m/%d/%y").date()
            except ValueError:
                messagebox.showerror("Error", f"No se pudo interpretar la fecha: {fecha_str}")
                return
            
            # Buscar evento (probar diferentes formatos)
            evento_encontrado = None
            
            for fecha_guardada, evento in eventos_por_fecha.items():
                # Intentar parsear la fecha guardada
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
            
            if evento_encontrado:
                print(f"Evento encontrado para {fecha_dt}: {evento_encontrado}")
                mostrar_info_evento(evento_encontrado, fecha_dt)
            else:
                if fecha_dt < hoy:
                    messagebox.showinfo("Información", f"No hubo evento reservado el {fecha_str}")
                else:
                    messagebox.showinfo("Información", f"No hay evento reservado para el {fecha_str}")
        
        for cal in calendarios_actuales:
            cal.bind("<<CalendarSelected>>", on_date_selected)
    
    # Función para mostrar información del evento - CORREGIDA
    def mostrar_info_evento(evento, fecha_dt):
        # Crear ventana emergente
        info_ventana = tk.Toplevel(ventana)
        info_ventana.title(f"Evento del {evento['fecha']}")
        info_ventana.geometry("600x550")
        info_ventana.resizable(False, False)
        info_ventana.configure(bg=BG)
        
        # Hacer que info_ventana sea accesible para las funciones internas
        def cerrar_ventana():
            info_ventana.destroy()
        
        # Función para ver croquis
        def ver_croquis():
            print(f"Ver croquis llamado para evento: {evento['fecha']}")
            cerrar_ventana()
            global origen_actual
            origen_actual = "calendario"  # Asegurar que el origen es calendario
            mostrar_evento(evento, modo="visualizacion")
        
        # Función para ver organización
        def ver_organizacion():
            orgs = cargar_org()
            org_evento = None
            for o in orgs:
                # Comparar fechas
                try:
                    fecha_o_str = o.get("fecha", "")
                    fecha_o = None
                    for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                        try:
                            fecha_o = datetime.datetime.strptime(fecha_o_str, formato).date()
                            break
                        except ValueError:
                            continue
                    
                    if fecha_o and fecha_o == fecha_dt:
                        org_evento = o
                        break
                except Exception as e:
                    print(f"Error comparando organización: {e}")
                    continue
            
            if org_evento:
                cerrar_ventana()
                mostrar_evento(evento, org_evento, modo="visualizacion")
        
        # Frame principal
        frame_info = tk.Frame(info_ventana, bg=BG)
        frame_info.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(frame_info, text=f"EVENTO - {evento['fecha']}", 
                font=("Arial", 16, "bold"), bg=BG, fg=TXT).pack(pady=10)
        
        # Información básica
        frame_datos = tk.Frame(frame_info, bg=BG)
        frame_datos.pack(fill="x", pady=10)
        
        # Mesa principal
        tk.Label(frame_datos, text=f"Mesa Principal: {evento.get('principal', 0)} personas", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        # Total de mesas
        total_mesas = len(evento.get('mesas', []))
        tk.Label(frame_datos, text=f"Total de mesas: {total_mesas}", 
                font=("Arial", 12), bg=BG, anchor="w").pack(fill="x", pady=2)
        
        # Total de invitados
        total_invitados = evento.get('principal', 0) + sum(m.get('personas', 0) for m in evento.get('mesas', []))
        tk.Label(frame_datos, text=f"Total de invitados: {total_invitados}", 
                font=("Arial", 12, "bold"), bg=BG, anchor="w").pack(fill="x", pady=5)
        
        # Mostrar nombres de mesas si existen
        if 'mesas' in evento and evento['mesas']:
            frame_mesas = tk.Frame(frame_info, bg=BG)
            frame_mesas.pack(fill="x", pady=10)
            
            tk.Label(frame_mesas, text="Mesas asignadas:", 
                    font=("Arial", 11, "bold"), bg=BG).pack(anchor="w")
            
            # Mostrar hasta 5 mesas
            for i, mesa in enumerate(evento['mesas'][:5]):
                if mesa.get('nombre'):
                    tk.Label(frame_mesas, text=f"  • {mesa['nombre']}: {mesa['personas']} personas", 
                            font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
            
            if len(evento['mesas']) > 5:
                tk.Label(frame_mesas, text=f"  ... y {len(evento['mesas']) - 5} mesas más", 
                        font=("Arial", 10), bg=BG, anchor="w").pack(fill="x")
        
        # Estado del evento
        frame_estado = tk.Frame(frame_info, bg=BG)
        frame_estado.pack(fill="x", pady=15)
        
        if fecha_dt < hoy:
            estado_texto = "EVENTO REALIZADO ✓"
            estado_color = "#757575"
        elif fecha_dt == hoy:
            estado_texto = "EVENTO HOY ⚠"
            estado_color = "#FF9800"
        else:
            estado_texto = "EVENTO PROGRAMADO"
            estado_color = "#2196F3"
        
        tk.Label(frame_estado, text=estado_texto, 
                font=("Arial", 14, "bold"), bg=estado_color, fg="white",
                width=30, height=2).pack(pady=10)
        
        # Botones - REVISADO Y SIMPLIFICADO
        frame_botones = tk.Frame(frame_info, bg=BG)
        frame_botones.pack(pady=20)
        
        # Botón para ver croquis - SIEMPRE disponible si hay mesas
        print(f"Verificando mesas en evento: {evento.get('mesas', [])}")
        if 'mesas' in evento and len(evento['mesas']) > 0:
            print(f"Mostrando botón de croquis - {len(evento['mesas'])} mesas encontradas")
            tk.Button(frame_botones, text="Ver Croquis del Evento", 
                     command=ver_croquis, 
                     bg=BTN, fg="white", width=25).pack(pady=5)
        else:
            print("NO mostrando botón de croquis - no hay mesas o evento no tiene clave 'mesas'")
        
        # Botón para ver organización si existe
        orgs = cargar_org()
        org_evento = None
        for o in orgs:
            # Comparar fechas
            try:
                fecha_o_str = o.get("fecha", "")
                fecha_o = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_o = datetime.datetime.strptime(fecha_o_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_o and fecha_o == fecha_dt:
                    org_evento = o
                    break
            except Exception as e:
                print(f"Error comparando organización: {e}")
                continue
        
        if org_evento:
            tk.Button(frame_botones, text="Ver Organización Asignada", 
                     command=ver_organizacion, 
                     bg=BTN2, fg="white", width=25).pack(pady=5)
        
        tk.Button(frame_botones, text="Cerrar", 
                 command=cerrar_ventana, 
                 bg="#777", fg="white", width=25).pack(pady=5)
    
    # Cargar calendarios iniciales
    actualizar_calendarios("reset")
    
    # Frame para botones
    frame_botones = tk.Frame(frame_principal)
    frame_botones.pack(pady=20, fill="x")
    
    tk.Button(frame_botones, text="Volver al menú", 
              command=menu_admin, bg="#777", fg="white", 
              width=25, height=2).pack(pady=10)
    
    # Leyenda de colores
    frame_leyenda = tk.Frame(frame_principal, bg=BG)
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
    
    # Nota sobre días pasados
    tk.Label(frame_principal, 
             text="Nota: Los días pasados sin evento aparecen en gris claro",
             font=("Arial", 9, "italic"), 
             fg="#777", bg=BG).pack(pady=5)
    
    # Instrucciones
    tk.Label(frame_principal, 
             text="Instrucciones: Haz clic en cualquier día marcado para ver detalles del evento",
             font=("Arial", 9), 
             fg="#555", bg=BG).pack(pady=5)

# ---------------- CAPITÁN ----------------
def vista_capitan():
    limpiar()
    eventos=cargar_eventos()
    orgs=cargar_org()
    fechas_organizadas = {o["fecha"] for o in orgs}

    listbox=tk.Listbox(ventana,width=40)
    listbox.pack()

    for i,e in enumerate(eventos):
        if e["fecha"] not in fechas_organizadas:
            listbox.insert(tk.END,f"{i} - {e['fecha']}")

    def abrir():
        idx=listbox.curselection()
        if not idx: return
        real_index=int(listbox.get(idx[0]).split(" - ")[0])
        mostrar_evento(eventos[real_index])

    tk.Button(ventana,text="Abrir",command=abrir).pack()
    tk.Button(ventana,text="Volver",command=menu_capitan).pack()

def mostrar_evento(evento, org_existente=None, modo="capitan"):
    limpiar()
    global color_actual, origen_actual
    color_actual = "lightgray"
    conteo_meseros = {}
    mesas_colores.clear()

    if org_existente and "meseros" in org_existente:
        conteo_meseros = org_existente["meseros"].copy()

    # ===== CONTENEDORES =====
    frame_main = tk.Frame(ventana)
    frame_main.pack(expand=True)

    frame_centro = tk.Frame(frame_main)
    frame_centro.pack(pady=10)

    frame_left = tk.Frame(frame_centro)
    frame_left.pack(side="left", padx=30)

    frame_right = tk.Frame(frame_centro)
    frame_right.pack(side="left", padx=30)

    # ===== CANVAS =====
    canvas = tk.Canvas(frame_left, width=COLUMNAS*CELL, height=(FILAS+1)*CELL, bg="white")
    canvas.pack()

    canvas.create_rectangle(2*CELL, 0, 4*CELL, CELL*0.7, fill="brown")
    canvas.create_text(3*CELL, 0.35*CELL, text=f"Principal\n{evento['principal']}", fill="white")

    canvas.create_rectangle(2*CELL, 1*CELL, 4*CELL, 3*CELL, fill="black")
    canvas.create_text(3*CELL, 2*CELL, text="PISTA", fill="white")

    mapa = {(m["col"], m["fila"]): m for m in evento["mesas"]}
    mesas_ids = {}

    def pintar(event, id_mesa, personas, c, f):
        # Solo permitir pintar en modo capitan
        if modo != "capitan":
            return

        viejo_color = mesas_colores.get((c, f))

        if viejo_color == color_actual:
            return

        if viejo_color:
            conteo_meseros[viejo_color] -= personas
            if conteo_meseros[viejo_color] <= 0:
                del conteo_meseros[viejo_color]

        canvas.itemconfig(id_mesa, fill=color_actual)
        conteo_meseros[color_actual] = conteo_meseros.get(color_actual, 0) + personas
        mesas_colores[(c, f)] = color_actual
        lbl_contador.config(text=f"Meseros asignados: {len(conteo_meseros)}")

    for fila in range(1, FILAS+1):
        for col in range(1, COLUMNAS+1):
            if 3 <= col <= 4 and 1 <= fila <= 2:
                continue
            if (col, fila) in mapa:
                m = mapa[(col, fila)]
                x1 = (col-1)*CELL
                y1 = fila*CELL
                x2 = x1+CELL
                y2 = y1+CELL
                mesa = canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="lightgray")
                mesas_ids[(col, fila)] = mesa

                txt = str(m["personas"])
                if m["nombre"]:
                    txt += f"\n{m['nombre']}"
                canvas.create_text((x1+x2)//2, (y1+y2)//2, text=txt)

                if modo == "capitan":
                    canvas.tag_bind(
                        mesa,
                        "<Button-1>",
                        lambda e, idm=mesa, p=m["personas"], c=col, f=fila: pintar(e, idm, p, c, f)
                    )

    # ===== PALETA ===== (solo para modo capitan)
    if modo == "capitan":
        colores = ["red", "blue", "green", "yellow", "orange", "pink", "purple", "cyan", "magenta",
                   "brown", "gray", "lime", "gold", "navy", "teal", "salmon", "khaki", "coral"]

        if org_existente and "colores" in org_existente:
            for clave, color in org_existente["colores"].items():
                c, f = eval(clave)
                if (c, f) in mesas_ids:
                    canvas.itemconfig(mesas_ids[(c, f)], fill=color)
                    mesas_colores[(c, f)] = color

        for c in colores:
            tk.Button(frame_right, text=c, bg=c, width=12,
                      command=lambda col=c: seleccionar_color(col)).pack(pady=2)

        lbl_contador = tk.Label(frame_right, text=f"Meseros asignados: {len(conteo_meseros)}",
                                font=("Arial", 12, "bold"))
        lbl_contador.pack(pady=10)
    else:
        # Para modos visualizacion y mesero, mostrar información del evento
        tk.Label(frame_right, text=f"Evento: {evento['fecha']}",
                 font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(frame_right, text=f"Mesa Principal: {evento['principal']} personas",
                 font=("Arial", 11)).pack(pady=5)
        tk.Label(frame_right, text=f"Total Mesas: {len(evento['mesas'])}",
                 font=("Arial", 11)).pack(pady=5)
        total_personas = evento['principal'] + sum(m['personas'] for m in evento['mesas'])
        tk.Label(frame_right, text=f"Total Invitados: {total_personas}",
                 font=("Arial", 12, "bold")).pack(pady=10)

    def guardar_org():
        data = {
            "fecha": evento["fecha"],
            "meseros": conteo_meseros,
            "colores": {str(k): v for k, v in mesas_colores.items()}
        }
        guardar_organizacion(data)
        messagebox.showinfo("Guardado", "Organización guardada")

    # ===== BOTONES =====
    frame_botones = tk.Frame(frame_main)
    frame_botones.pack(pady=10)

    if modo == "capitan":
        tk.Button(frame_botones, text="Guardar organización", command=guardar_org).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=menu_capitan).pack(side="left", padx=10)
    elif modo == "mesero":
        tk.Button(frame_botones, text="Volver", command=menu_mesero).pack(side="left", padx=10)
    else:  # modo "visualizacion"
        # Determinar a dónde volver según el origen
        if origen_actual == "comentarios":
            tk.Button(frame_botones, text="Volver a Comentarios",
                     command=vista_mesero_comentarios,
                     bg=BTN2, fg="white").pack(side="left", padx=10)
        else:
            # Por defecto, volver al calendario (para Patrón/Admin)
            tk.Button(frame_botones, text="Volver al Calendario",
                     command=vista_calendario).pack(side="left", padx=10)


def seleccionar_color(c):
    global color_actual
    color_actual=c

# ---------------- COMPARAR ----------------
def vista_comparar():
    limpiar()
    eventos=cargar_eventos()
    eventos_con_fecha=[e for e in eventos if "fecha" in e]

    tk.Label(ventana,text="Comparar eventos",font=("Arial",16)).pack()

    frame_sel=tk.Frame(ventana); frame_sel.pack()
    tk.Label(frame_sel,text="Evento actual").grid(row=0,column=0)
    tk.Label(frame_sel,text="Evento siguiente").grid(row=0,column=1)

    lb1=tk.Listbox(frame_sel,width=30,exportselection=False)
    lb2=tk.Listbox(frame_sel,width=30,exportselection=False)
    lb1.grid(row=1,column=0,padx=5)
    lb2.grid(row=1,column=1,padx=5)

    for i,e in enumerate(eventos_con_fecha):
        lb1.insert(tk.END,f"{i} - {e['fecha']}")

    frame_info = tk.Frame(ventana)
    frame_info.place(relx=0.75, rely=0.05)  # arriba a la derecha
    
    lbl_info1 = tk.Label(frame_info, text="", font=("Arial",11,"bold"), anchor="w")
    lbl_info1.pack(anchor="w")
    lbl_info2 = tk.Label(frame_info, text="", font=("Arial",11,"bold"), anchor="w")
    lbl_info2.pack(anchor="w")
    lbl_info3 = tk.Label(frame_info, text="", font=("Arial",11,"bold"), anchor="w")
    lbl_info3.pack(anchor="w")


    frame_canvas=tk.Frame(ventana)
    frame_canvas.pack()

    def on_select_actual(event):
        lb2.delete(0,tk.END)
        sel=lb1.curselection()
        if not sel: return
        idx=sel[0]
        fecha_actual=datetime.datetime.strptime(eventos_con_fecha[idx]["fecha"],"%m/%d/%y")
        for i,e in enumerate(eventos_con_fecha):
            fecha_e=datetime.datetime.strptime(e["fecha"],"%m/%d/%y")
            if fecha_e>fecha_actual:
                lb2.insert(tk.END,f"{i} - {e['fecha']}")

    lb1.bind("<<ListboxSelect>>",on_select_actual)

    def comparar():
        sel1=lb1.curselection()
        sel2=lb2.curselection()
        if not sel1 or not sel2:
            messagebox.showwarning("Error","Selecciona dos eventos")
            return

        i1=int(lb1.get(sel1[0]).split(" - ")[0])
        i2=int(lb2.get(sel2[0]).split(" - ")[0])

        ev1=eventos_con_fecha[i1]
        ev2=eventos_con_fecha[i2]

        for w in frame_canvas.winfo_children():
            w.destroy()

        dibujar_croquis(frame_canvas, ev1, scale=0.7)
        dibujar_croquis(frame_canvas, ev2, scale=0.7)

        total1 = ev1["principal"] + sum(m["personas"] for m in ev1["mesas"])
        total2 = ev2["principal"] + sum(m["personas"] for m in ev2["mesas"])
        diff = total2 - total1

        orgs = cargar_org()
        org_evento = None
        for o in orgs:
            if o["fecha"] == ev1["fecha"]:
                org_evento = o
                break

        total_meseros = len(org_evento["meseros"]) if org_evento else 0

        if diff > 0:
            lbl_info1.config(text=f"Sillas que FALTAN: {diff}")
        else:
            lbl_info1.config(text=f"Sillas que SOBRAN: {abs(diff)}")

        lbl_info2.config(text=f"Meseros del evento actual: {total_meseros}")

        if diff < 0 and total_meseros > 0:
            sillas_por_mesero = abs(diff) // total_meseros
            lbl_info3.config(text=f"Sillas por mesero: {sillas_por_mesero}")
        else:
            lbl_info3.config(text="")

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)
    tk.Button(frame_botones,text="Comparar",command=comparar,width=20).pack(side="left",padx=10)
    tk.Button(frame_botones,text="Volver",command=menu_capitan,width=20).pack(side="left",padx=10)

def vista_cargar_org():
    limpiar()
    orgs=cargar_org()
    eventos=cargar_eventos()

    listbox=tk.Listbox(ventana,width=40)
    listbox.pack()

    for i,o in enumerate(orgs):
        listbox.insert(tk.END,f"{i} - {o['fecha']}")

    def abrir():
        idx=listbox.curselection()
        if not idx: return
        fecha=orgs[idx[0]]["fecha"]

        evento=None
        for e in eventos:
            if e["fecha"]==fecha:
                evento=e
                break

        if not evento:
            messagebox.showerror("Error","Evento no encontrado")
            return

        mostrar_evento(evento,orgs[idx[0]])

    tk.Button(ventana,text="Abrir",command=abrir).pack()
    tk.Button(ventana,text="Volver",command=menu_capitan).pack()

def vista_mesero_org():
    limpiar()
    orgs=cargar_org()

    tk.Label(ventana,text="Organizaciones disponibles",font=("Arial",16)).pack(pady=10)

    if not orgs:
        tk.Label(ventana,
                 text="No hay organizaciones aún,\nespere al capitán.",
                 font=("Arial",12),
                 fg="red").pack(pady=30)
        tk.Button(ventana,text="Volver",command=menu_mesero).pack(pady=10)
        return

    listbox=tk.Listbox(ventana,width=40)
    listbox.pack()

    for i,o in enumerate(orgs):
        listbox.insert(tk.END,f"{i} - {o['fecha']}")

    eventos=cargar_eventos()

    def abrir():
        idx=listbox.curselection()
        if not idx: return
        fecha=orgs[idx[0]]["fecha"]

        evento=None
        for e in eventos:
            if e["fecha"]==fecha:
                evento=e
                break

        if evento:
            mostrar_evento(evento,orgs[idx[0]],modo="mesero")
        else:
            messagebox.showerror("Error","Evento no encontrado")

    tk.Button(ventana,text="Abrir",command=abrir).pack(pady=5)
    tk.Button(ventana,text="Volver",command=menu_mesero).pack(pady=10)

def vista_mesero_comentarios():
    global origen_actual
    origen_actual = "comentarios"  # Establecer origen
    limpiar()
    tk.Label(ventana, text="Comentarios del evento", font=("Arial", 16)).pack(pady=10)
    
    # Cargar eventos pasados y el de hoy
    eventos = cargar_eventos()
    hoy = datetime.date.today()
    eventos_comentables = []
    
    for e in eventos:
        try:
            fecha_str = e.get("fecha", "")
            if not fecha_str:
                continue
                
            # Intentar parsear la fecha
            fecha_dt = None
            for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                try:
                    fecha_dt = datetime.datetime.strptime(fecha_str, formato).date()
                    break
                except ValueError:
                    continue
            
            # Solo eventos pasados o de hoy
            if fecha_dt and fecha_dt <= hoy:
                eventos_comentables.append((fecha_dt, e))
        except Exception as e:
            print(f"Error procesando evento: {e}")
            continue
    
    # Ordenar por fecha (más reciente primero)
    eventos_comentables.sort(key=lambda x: x[0], reverse=True)
    
    if not eventos_comentables:
        tk.Label(ventana,
                text="No hay eventos pasados o del día de hoy para comentar.",
                font=("Arial", 12),
                fg="red").pack(pady=30)
        tk.Button(ventana, text="Volver", command=menu_mesero, 
                 bg="#777", fg="white", width=20).pack(pady=10)
        return
    
    # Variable para controlar la ventana anterior (para volver a comentarios)
    global ventana_anterior_comentarios
    ventana_anterior_comentarios = "comentarios"
    
    # Frame para selección de evento
    frame_seleccion = tk.Frame(ventana)
    frame_seleccion.pack(pady=10, fill="x", padx=20)
    
    tk.Label(frame_seleccion, text="Selecciona el evento:", 
            font=("Arial", 11, "bold")).pack(anchor="w")
    
    # Variable para guardar el evento seleccionado
    evento_seleccionado = tk.StringVar()
    
    # Frame para los radiobuttons con scroll
    frame_scroll = tk.Frame(ventana)
    frame_scroll.pack(pady=5, fill="both", expand=True, padx=20)
    
    canvas_scroll = tk.Canvas(frame_scroll, height=150, bg=BG)
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_scroll.yview)
    scrollable_frame = tk.Frame(canvas_scroll, bg=BG)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
    )
    
    canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    
    # Frame para el formulario de comentarios (inicialmente deshabilitado)
    frame_formulario = tk.Frame(ventana, bg=BG, relief="groove", bd=2)
    
    # Mostrar eventos en radiobuttons
    for i, (fecha_dt, evento) in enumerate(eventos_comentables):
        fecha_str = fecha_dt.strftime("%d/%m/%Y")
        fecha_original = evento.get("fecha", "")  # Formato original para guardar
        total_personas = evento.get('principal', 0) + sum(m.get('personas', 0) for m in evento.get('mesas', []))
        
        estado = "HOY" if fecha_dt == hoy else "PASADO"
        
        frame_opcion = tk.Frame(scrollable_frame, bg=BG)
        frame_opcion.pack(fill="x", pady=2)
        
        rb = tk.Radiobutton(frame_opcion, text=f"{fecha_str} - {estado} - {total_personas} invitados",
                           variable=evento_seleccionado, value=fecha_original, 
                           font=("Arial", 10), bg=BG,
                           command=lambda: habilitar_formulario())
        rb.pack(side="left")
        
        # Botón para ver croquis del evento
        btn_ver = tk.Button(frame_opcion, text="Ver croquis", 
                          command=lambda ev=evento: ver_croquis_desde_comentarios(ev),
                          bg=BTN2, fg="white", font=("Arial", 8))
        btn_ver.pack(side="right", padx=5)
    
    canvas_scroll.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Función para ver croquis y volver a comentarios
    def ver_croquis_desde_comentarios(evento):
        global origen_actual
        origen_actual = "comentarios"  # Mantener el origen
        mostrar_evento(evento, modo="visualizacion")
    
    # Función para habilitar el formulario cuando se selecciona un evento
    def habilitar_formulario():
        frame_formulario.pack(pady=20, fill="x", padx=20)
        fecha = evento_seleccionado.get()
        if fecha:
            cargar_comentarios_existentes()
    
    # Título del formulario
    tk.Label(frame_formulario, text="Formulario de comentarios", 
            font=("Arial", 12, "bold"), bg=BG).pack(pady=5)
    
    # Campos del formulario
    frame_campos = tk.Frame(frame_formulario, bg=BG)
    frame_campos.pack(pady=10, padx=20)
    
    # Ganancia
    tk.Label(frame_campos, text="¿Cuánto ganaste? ($)", 
            font=("Arial", 10), bg=BG).grid(row=0, column=0, sticky="w", pady=5)
    entry_ganancia = tk.Entry(frame_campos, width=30)
    entry_ganancia.grid(row=0, column=1, padx=10, pady=5)
    
    # Cómo sentiste el evento
    tk.Label(frame_campos, text="¿Cómo sentiste el evento?", 
            font=("Arial", 10), bg=BG).grid(row=1, column=0, sticky="w", pady=5)
    entry_sentir = tk.Entry(frame_campos, width=30)
    entry_sentir.grid(row=1, column=1, padx=10, pady=5)
    
    # Observaciones
    tk.Label(frame_campos, text="Observaciones", 
            font=("Arial", 10), bg=BG).grid(row=2, column=0, sticky="w", pady=5)
    entry_obs = tk.Entry(frame_campos, width=30)
    entry_obs.grid(row=2, column=1, padx=10, pady=5)
    
    # Reporte de desperfectos/quejas
    tk.Label(frame_campos, text="¿Hubo desperfectos o quejas?", 
            font=("Arial", 10), bg=BG).grid(row=3, column=0, sticky="w", pady=5)
    entry_reporte = tk.Entry(frame_campos, width=30)
    entry_reporte.grid(row=3, column=1, padx=10, pady=5)
    
    # Calificación
    tk.Label(frame_campos, text="Calificación (1-5):", 
            font=("Arial", 10), bg=BG).grid(row=4, column=0, sticky="w", pady=5)
    calificacion_var = tk.StringVar()
    calificacion_combo = tk.Spinbox(frame_campos, from_=1, to=5, textvariable=calificacion_var, width=5)
    calificacion_combo.grid(row=4, column=1, sticky="w", padx=10, pady=5)
    calificacion_var.set("5")
    
    # Etiqueta para indicar si es edición
    lbl_editando = tk.Label(frame_formulario, text="", font=("Arial", 9, "italic"), 
                           fg=BTN2, bg=BG)
    lbl_editando.pack(pady=2)
    
    # Cargar comentarios existentes si hay evento seleccionado
    def cargar_comentarios_existentes():
        fecha = evento_seleccionado.get()
        if not fecha:
            return
        
        comentarios = cargar_comentarios()
        encontrado = False
        
        for c in comentarios:
            if c.get("fecha") == fecha:
                entry_ganancia.delete(0, tk.END)
                entry_ganancia.insert(0, c.get("ganancia", ""))
                
                entry_sentir.delete(0, tk.END)
                entry_sentir.insert(0, c.get("sentir", ""))
                
                entry_obs.delete(0, tk.END)
                entry_obs.insert(0, c.get("observaciones", ""))
                
                entry_reporte.delete(0, tk.END)
                entry_reporte.insert(0, c.get("reporte", ""))
                
                calificacion_var.set(c.get("calificacion", "5"))
                
                lbl_editando.config(text="✎ Editando comentario existente")
                encontrado = True
                break
        
        if not encontrado:
            # Limpiar campos para nuevo comentario
            entry_ganancia.delete(0, tk.END)
            entry_sentir.delete(0, tk.END)
            entry_obs.delete(0, tk.END)
            entry_reporte.delete(0, tk.END)
            calificacion_var.set("5")
            lbl_editando.config(text="+ Nuevo comentario")
    
    # Función para guardar comentarios
    def guardar():
        fecha = evento_seleccionado.get()
        if not fecha:
            messagebox.showwarning("Error", "Por favor, selecciona un evento")
            return
        
        # Validar campos obligatorios
        if not entry_ganancia.get().strip():
            messagebox.showwarning("Error", "Por favor, ingresa cuánto ganaste")
            return
        
        if not entry_sentir.get().strip():
            messagebox.showwarning("Error", "Por favor, describe cómo sentiste el evento")
            return
        
        # Crear el comentario con la fecha del evento
        data = {
            "fecha": fecha,  # Enlazar con la fecha del evento
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ganancia": entry_ganancia.get(),
            "sentir": entry_sentir.get(),
            "observaciones": entry_obs.get(),
            "reporte": entry_reporte.get(),
            "calificacion": calificacion_var.get()
        }
        
        # Guardar o actualizar comentario (usando la función guardar_comentario)
        guardar_comentario(data)
        
        # Verificar si fue edición o nuevo
        comentarios = cargar_comentarios()
        es_edicion = False
        for c in comentarios:
            if c.get("fecha") == fecha and c.get("timestamp") == data.get("timestamp"):
                es_edicion = True
                break
        
        if es_edicion:
            messagebox.showinfo("Actualizado", f"Comentario actualizado para el evento del {fecha}")
        else:
            messagebox.showinfo("Gracias", f"Comentario guardado para el evento del {fecha}")
        
        # Preguntar si quiere agregar otro comentario
        respuesta = messagebox.askyesno("Continuar", "¿Quieres agregar otro comentario?")
        if respuesta:
            # Limpiar selección y formulario
            evento_seleccionado.set("")
            entry_ganancia.delete(0, tk.END)
            entry_sentir.delete(0, tk.END)
            entry_obs.delete(0, tk.END)
            entry_reporte.delete(0, tk.END)
            calificacion_var.set("5")
            lbl_editando.config(text="")
            frame_formulario.pack_forget()  # Ocultar formulario
        else:
            menu_mesero()
    
    # Frame para botones
    frame_botones = tk.Frame(frame_formulario)
    frame_botones.pack(pady=20)
    
    tk.Button(frame_botones, text="Guardar comentario", 
              command=guardar, bg=BTN, fg="white", 
              width=20, height=2, font=("Arial", 10, "bold")).pack(side="left", padx=10)
    
    # Mostrar comentarios existentes para la fecha seleccionada
    def mostrar_comentarios_guardados():
        fecha = evento_seleccionado.get()
        if not fecha:
            messagebox.showinfo("Info", "Selecciona un evento para ver sus comentarios")
            return
        
        comentarios = cargar_comentarios()
        comentarios_evento = [c for c in comentarios if c.get("fecha") == fecha]
        
        if not comentarios_evento:
            messagebox.showinfo("Info", "No hay comentarios guardados para este evento")
            return
        
        # Crear ventana para mostrar comentarios
        ventana_comentarios = tk.Toplevel(ventana)
        ventana_comentarios.title(f"Comentarios - {fecha}")
        ventana_comentarios.geometry("500x400")
        ventana_comentarios.configure(bg=BG)
        
        frame_ver = tk.Frame(ventana_comentarios, bg=BG)
        frame_ver.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame_ver, text=f"Comentarios del evento {fecha}", 
                font=("Arial", 14, "bold"), bg=BG).pack(pady=10)
        
        # Mostrar cada comentario
        for i, c in enumerate(comentarios_evento):
            frame_com = tk.Frame(frame_ver, bg=BG, relief="groove", bd=1)
            frame_com.pack(fill="x", pady=5)
            
            tk.Label(frame_com, text=f"Fecha: {c.get('fecha', 'N/A')}", 
                    font=("Arial", 10, "bold"), bg=BG).pack(anchor="w", padx=5)
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
    
    tk.Button(frame_formulario, text="Ver comentarios guardados", 
              command=mostrar_comentarios_guardados, bg=BTN2, fg="white", 
              width=25).pack(pady=10)
    
    # Frame para botones principales
    frame_botones_principales = tk.Frame(ventana)
    frame_botones_principales.pack(pady=10)
    
    tk.Button(frame_botones_principales, text="Volver al menú", 
              command=menu_mesero, bg="#777", fg="white", 
              width=20, height=2).pack(pady=10)
    
    # Instrucciones
    tk.Label(ventana, 
             text="Instrucciones: 1) Selecciona un evento de la lista\n2) Completa el formulario\n3) Guarda tu comentario",
             font=("Arial", 9), 
             fg="#555", bg=BG).pack(pady=5)

def vista_mesero_stats():
    limpiar()
    tk.Label(ventana,text="Estadísticas de desempeño",font=("Arial",16)).pack(pady=20)
    tk.Label(ventana,text="Aquí tu desempeño",font=("Arial",12)).pack(pady=10)
    tk.Button(ventana,text="Volver",command=menu_mesero).pack(pady=20)


# ---------------- CROQUIS BASE ----------------
def vista_croquis(modo="demo",fecha=None):
    limpiar()
    global total_invitados, mesa_principal_valor, color_actual
    color_actual="lightgray"

    # ===== CONTENEDORES PRINCIPALES =====
    frame_main = tk.Frame(ventana)
    frame_main.pack(expand=True)

    frame_sup = tk.Frame(frame_main)
    frame_sup.pack(pady=5)

    frame_centro = tk.Frame(frame_main)
    frame_centro.pack()

    frame_left = tk.Frame(frame_centro)
    frame_left.pack(side="left", padx=20)

    frame_right = tk.Frame(frame_centro)
    frame_right.pack(side="left", padx=20)

    # ===== PARTE SUPERIOR =====
    tk.Label(frame_sup,text="Total invitados:").grid(row=0,column=0)
    entry=tk.Entry(frame_sup,width=6)
    entry.grid(row=0,column=1)

    lbl=tk.Label(frame_sup,text="Personas sin acomodar: 0")
    lbl.grid(row=1,column=0,columnspan=3)

    tk.Button(frame_sup,text="Calcular",command=lambda:calcular()).grid(row=0,column=2)

    # ===== CANVAS =====
    canvas=tk.Canvas(frame_left,width=COLUMNAS*CELL,height=(FILAS+1)*CELL,bg="white")
    canvas.pack()

    mp=canvas.create_rectangle(2*CELL,0,4*CELL,CELL*0.7,fill="brown")
    texto_mp=canvas.create_text(3*CELL,0.35*CELL,text="Principal\n2",fill="white")

    def editar_principal(event):
        global mesa_principal_valor
        v=simpledialog.askinteger("Principal","Personas (2-8):",minvalue=2,maxvalue=8)
        if v:
            mesa_principal_valor=v
            canvas.itemconfig(texto_mp,text=f"Principal\n{v}")
            actualizar()

    canvas.tag_bind(mp,"<Button-1>",editar_principal)

    canvas.create_rectangle(2*CELL,1*CELL,4*CELL,3*CELL,fill="black")
    canvas.create_text(3*CELL,2*CELL,text="PISTA",fill="white")

    valores_mesas.clear()
    asociaciones_colores.clear()

    def crear_mesa(col,fila):
        x1=(col-1)*CELL; y1=fila*CELL
        x2=x1+CELL; y2=y1+CELL
        mesa=canvas.create_oval(x1+10,y1+10,x2-10,y2-10,fill="lightgray")
        texto=canvas.create_text((x1+x2)//2,(y1+y2)//2,text="0")
        valores_mesas[(col,fila)]={"mesa":mesa,"texto":texto,"valor":0,"nombre":None,"color":"lightgray"}

        def editar(event,c=col,f=fila):
            v=simpledialog.askinteger("Mesa","Personas (0-12):",minvalue=0,maxvalue=12)
            if v!=None:
                valores_mesas[(c,f)]["valor"]=v
                canvas.itemconfig(texto,text=str(v))
                actualizar()

        canvas.tag_bind(mesa,"<Button-1>",editar)

        if modo=="anfitrion":
            def poner_nombre(event,c=col,f=fila):
                nombre=simpledialog.askstring("Nombre","Nombre mesa:")
                if nombre:
                    valores_mesas[(c,f)]["nombre"]=nombre
                    valores_mesas[(c,f)]["color"]=color_actual
                    canvas.itemconfig(valores_mesas[(c,f)]["mesa"],fill=color_actual)
                    asociaciones_colores[color_actual]=nombre
                    actualizar_leyenda()
            canvas.tag_bind(mesa,"<Button-3>",poner_nombre)

    for fila in range(1,FILAS+1):
        for col in range(1,COLUMNAS+1):
            if 3<=col<=4 and 1<=fila<=3: continue
            crear_mesa(col,fila)

    prioridad=[]
    for f in range(1,5): prioridad.append((2,f))
    for f in range(1,5): prioridad.append((5,f))
    prioridad += [(3,3),(4,3),(3,4),(4,4),(3,5),(4,5),(2,5),(5,5)]

    def calcular():
        global total_invitados
        total_invitados=int(entry.get())
        restantes=total_invitados-mesa_principal_valor
        for info in valores_mesas.values():
            info["valor"]=0
            canvas.itemconfig(info["texto"],text="0")
        for (c,f) in prioridad:
            if restantes<=0: break
            asignar=min(10,restantes)
            valores_mesas[(c,f)]["valor"]=asignar
            canvas.itemconfig(valores_mesas[(c,f)]["texto"],text=str(asignar))
            restantes-=asignar
        actualizar()

    def actualizar():
        usados=mesa_principal_valor+sum(i["valor"] for i in valores_mesas.values())
        faltan=total_invitados-usados
        lbl.config(text=f"Personas sin acomodar: {faltan}")

    # ===== LADO DERECHO =====
    if modo=="anfitrion":
        frame_pal=tk.Frame(frame_right)
        frame_pal.pack()

        colores={"Verde":"green","Rojo":"red","Azul":"blue","Amarillo":"yellow","Rosa":"pink"}
        for n,c in colores.items():
            tk.Button(frame_pal,text=n,bg=c,width=12,command=lambda col=c:seleccionar_color(col)).pack(pady=2)

        tk.Label(frame_pal,text="Leyenda").pack()
        frame_leyenda=tk.Frame(frame_pal)
        frame_leyenda.pack()

        def actualizar_leyenda():
            for w in frame_leyenda.winfo_children(): w.destroy()
            for c,n in asociaciones_colores.items():
                tk.Label(frame_leyenda,text=n,bg=c,width=12).pack()

        def hacer_evento():
            mesas_guardar=[]
            for (c,f),info in valores_mesas.items():
                if info["valor"]>=2:
                    mesas_guardar.append({"col":c,"fila":f,"personas":info["valor"],"nombre":info["nombre"],"color":info["color"]})
            data={"fecha":fecha,"principal":mesa_principal_valor,"mesas":mesas_guardar}
            guardar_evento(data)
            messagebox.showinfo("Evento","Evento guardado")

        tk.Button(frame_sup,text="Guardar evento",command=hacer_evento).grid(row=2,column=0,columnspan=3)

    tk.Button(frame_main,text="Volver",command=menu_admin).pack(pady=10)

def cargar_comentarios_mesero():
    """Carga los comentarios hechos por meseros"""
    if not os.path.exists(ARCHIVO_COMENTARIOS_MESERO):
        return []
    with open(ARCHIVO_COMENTARIOS_MESERO, "r", encoding="utf8") as f:
        return json.load(f)

def guardar_comentario_mesero(data):
    """Guarda o actualiza un comentario de mesero"""
    lista = cargar_comentarios_mesero()
    
    # Buscar si ya existe un comentario de este mesero para esta fecha
    encontrado = False
    for i, c in enumerate(lista):
        if c.get("fecha") == data.get("fecha") and c.get("usuario") == data.get("usuario"):
            lista[i] = data  # Reemplazar
            encontrado = True
            break
    
    if not encontrado:
        lista.append(data)  # Agregar nuevo
    
    with open(ARCHIVO_COMENTARIOS_MESERO, "w", encoding="utf8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def cargar_comentarios_evento():
    """Carga los comentarios generales del evento"""
    if not os.path.exists(ARCHIVO_COMENTARIOS_EVENTO):
        return []
    with open(ARCHIVO_COMENTARIOS_EVENTO, "r", encoding="utf8") as f:
        return json.load(f)

def guardar_comentario_evento(data):
    """Guarda o actualiza un comentario general del evento"""
    lista = cargar_comentarios_evento()
    
    # Buscar si ya existe un comentario para esta fecha
    encontrado = False
    for i, c in enumerate(lista):
        if c.get("fecha") == data.get("fecha"):
            lista[i] = data  # Reemplazar
            encontrado = True
            break
    
    if not encontrado:
        lista.append(data)  # Agregar nuevo
    
    with open(ARCHIVO_COMENTARIOS_EVENTO, "w", encoding="utf8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def exportar_comentarios_a_excel():
    """Exporta todos los comentarios a formato Excel (CSV) para estadísticas"""
    import csv
    from datetime import datetime
    
    # Exportar comentarios de meseros
    comentarios_mesero = cargar_comentarios_mesero()
    if comentarios_mesero:
        nombre_archivo_mesero = f"comentarios_meseros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nombre_archivo_mesero, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Cabeceras
            writer.writerow(['Fecha Evento', 'Usuario', 'Rol', 'Ganancia', 'Satisfaccion', 
                           'Observaciones', 'Reportes', 'Calificacion', 'Timestamp'])
            # Datos
            for c in comentarios_mesero:
                writer.writerow([
                    c.get('fecha', ''),
                    c.get('usuario', ''),
                    c.get('rol', ''),
                    c.get('ganancia', ''),
                    c.get('sentir', ''),
                    c.get('observaciones', ''),
                    c.get('reporte', ''),
                    c.get('calificacion', ''),
                    c.get('timestamp', '')
                ])
        print(f"Archivo exportado: {nombre_archivo_mesero}")
    
    # Exportar comentarios de eventos
    comentarios_evento = cargar_comentarios_evento()
    if comentarios_evento:
        nombre_archivo_evento = f"comentarios_eventos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nombre_archivo_evento, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Cabeceras
            writer.writerow(['Fecha Evento', 'Ganancia Total', 'Satisfaccion General', 
                           'Observaciones', 'Reportes', 'Calificacion Promedio', 'Numero Meseros', 'Timestamp'])
            # Datos
            for c in comentarios_evento:
                writer.writerow([
                    c.get('fecha', ''),
                    c.get('ganancia_total', ''),
                    c.get('satisfaccion_general', ''),
                    c.get('observaciones', ''),
                    c.get('reportes', ''),
                    c.get('calificacion_promedio', ''),
                    c.get('num_meseros', ''),
                    c.get('timestamp', '')
                ])
        print(f"Archivo exportado: {nombre_archivo_evento}")
    
    return nombre_archivo_mesero if comentarios_mesero else None, nombre_archivo_evento if comentarios_evento else None

def dibujar_croquis(frame,evento,scale=1.0):
    w = int(COLUMNAS*CELL*scale)
    h = int((FILAS+1)*CELL*scale)

    canvas=tk.Canvas(frame,width=w,height=h,bg="white")
    canvas.pack(side="left",padx=10)

    def sx(x): return int(x*scale)
    def sy(y): return int(y*scale)

    total=evento["principal"]+sum(m["personas"] for m in evento["mesas"])
    canvas.create_text(w//2,sy(15),text=f"Total invitados: {total}",font=("Arial",int(12*scale),"bold"))

    canvas.create_rectangle(sx(2*CELL),sy(20),sx(4*CELL),sy(20+CELL*0.7),fill="brown")
    canvas.create_text(sx(3*CELL),sy(20+0.35*CELL),
                       text=f"Principal\n{evento['principal']}",fill="white")

    canvas.create_rectangle(sx(2*CELL),sy(1*CELL+20),sx(4*CELL),sy(3*CELL+20),fill="black")
    canvas.create_text(sx(3*CELL),sy(2*CELL+20),text="PISTA",fill="white")

    mapa={(m["col"],m["fila"]):m for m in evento["mesas"]}

    for fila in range(1,FILAS+1):
        for col in range(1,COLUMNAS+1):
            if 3<=col<=4 and 1<=fila<=3: continue
            if (col,fila) in mapa:
                m=mapa[(col,fila)]
                x1 = sx((col-1)*CELL)
                y1 = sy(fila*CELL+20)
                x2 = sx((col)*CELL)
                y2 = sy((fila+1)*CELL+20)

                canvas.create_oval(x1+sx(10),y1+sy(10),x2-sx(10),y2-sy(10),fill="lightgray")
                canvas.create_text((x1+x2)//2,(y1+y2)//2,text=str(m["personas"]))

    return canvas


# ---------------- MAIN ----------------
ventana=tk.Tk()
ventana.title("Sistema Salón")
ventana.geometry("1100x700")
ventana.resizable(False,False)
login()
ventana.mainloop()
