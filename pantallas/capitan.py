import datetime
import re
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, OfertaTrabajo, Organizacion
from .base import FrameBase
from .lazy import *
from .patron import crear_area_scroll, formato_moneda, numero_desde_texto


def fecha_evento_a_date(fecha):
    for formato in ("%m/%d/%y", "%m/%d/%yy"):
        try:
            return datetime.datetime.strptime(fecha, formato).date()
        except ValueError:
            continue
    return datetime.date.today()


def meseros_sugeridos_evento(evento):
    mesas = len([mesa for mesa in evento.mesas if mesa.personas > 0])
    return max(1, (mesas + 1) // 2) if mesas else 0


def servicios_evento_texto(evento):
    servicios = getattr(evento, "servicios", {})
    etiquetas = {
        "pantalla": "pantalla",
        "mesa_pastel": "pastel",
        "dulces": "dulces",
        "cocina": "cocina",
        "barra": "barra",
        "area_fotos": "fotos",
        "animador": "animador/extra",
    }
    activos = [texto for clave, texto in etiquetas.items() if servicios.get(clave, clave == "area_fotos")]
    return ", ".join(activos) if activos else "sin servicios extra"


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


class DashboardCapitanMixin:
    def abrir_dashboard_capitan(self, evento):
        fecha_dt = fecha_evento_a_date(evento.fecha)
        analisis = self.analizar_evento_capitan(evento)

        ventana = tk.Toplevel(self)
        ventana.title(f"Dashboard solo lectura - {evento.fecha}")
        ventana.geometry("1060x680")
        ventana.minsize(860, 560)
        ventana.resizable(True, True)
        ventana.configure(bg=BG)

        contenedor = tk.Frame(ventana, bg=BG)
        contenedor.pack(fill="both", expand=True, padx=16, pady=12)

        header = tk.Frame(contenedor, bg=BG)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text=f"Dashboard del evento - {evento.fecha}",
                 font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(side="left")
        tk.Button(header, text="Cerrar", command=ventana.destroy,
                  bg="#777", fg="white", relief="flat", width=14, height=2).pack(side="right")

        tk.Label(contenedor, text="Vista solo lectura para capitan: puedes consultar desempeno, croquis y comentarios, pero no agregar ni modificar datos aqui.",
                 font=("Arial", 10, "bold"), bg="#FEF3C7", fg="#92400E",
                 wraplength=980, justify="left").pack(fill="x", pady=(0, 10))

        cuerpo = crear_area_scroll(contenedor, BG)
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)

        izquierda = tk.Frame(cuerpo, bg=BG)
        izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        derecha = tk.Frame(cuerpo, bg=BG)
        derecha.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        croquis = self.tarjeta_capitan(izquierda, "Croquis del evento")
        self.dibujar_croquis_capitan(croquis, evento, analisis["organizacion"])

        resumen = self.tarjeta_capitan(izquierda, "Resumen basico")
        self.fila_capitan(resumen, "Fecha", evento.fecha)
        self.fila_capitan(resumen, "Estado", "Realizado" if fecha_dt < datetime.date.today() else "Programado")
        self.fila_capitan(resumen, "Mesas", str(len(mesas_visibles_evento(evento))))
        self.fila_capitan(resumen, "Personas", str(evento.total_invitados()))
        self.fila_capitan(resumen, "Servicios", servicios_evento_texto(evento))
        self.fila_capitan(resumen, "Meseros sugeridos", str(analisis["meseros_sugeridos"]))
        self.fila_capitan(resumen, "Meseros organizados", str(analisis["num_meseros"]) if analisis["num_meseros"] else "Sin organizacion")
        self.fila_capitan(resumen, "Faltantes sugeridos", str(analisis["faltantes_meseros"]) if analisis["faltantes_meseros"] > 0 else "Sin faltantes")

        refuerzo = self.tarjeta_capitan(izquierda, "Refuerzo de personal")
        tk.Label(refuerzo, text="La sugerencia usa 1 mesero por cada 2 mesas. El capitan puede decidir otra carga.",
                 font=("Arial", 9), bg="white", fg="#555", wraplength=430, justify="left").pack(anchor="w", padx=12, pady=(0, 6))
        tk.Button(refuerzo, text="Publicar necesidad de meseros",
                  command=lambda: self.publicar_necesidad_meseros(evento, analisis),
                  bg="#DC2626" if analisis["faltantes_meseros"] > 0 else "#6B7280",
                  fg="white", relief="flat", width=28, height=2).pack(anchor="w", padx=12, pady=(0, 10))

        meseros = self.tarjeta_capitan(izquierda, "Meseros y zonas")
        if analisis["organizacion"]:
            for color, personas in analisis["organizacion"].meseros.items():
                nombre = getattr(analisis["organizacion"], "nombres_meseros", {}).get(color, color)
                self.fila_color_capitan(meseros, color, f"{nombre}: {personas} personas asignadas")
        else:
            tk.Label(meseros, text="No hay organizacion guardada para este evento.",
                     font=("Arial", 9), bg="white", fg="#777").pack(anchor="w", padx=12, pady=(0, 10))

        comentarios = self.tarjeta_capitan(derecha, "Comentarios destacados")
        if analisis["destacados"]:
            for texto in analisis["destacados"]:
                tk.Label(comentarios, text=f"- {texto}", font=("Arial", 9), bg="white", fg="#555",
                         wraplength=460, justify="left").pack(anchor="w", padx=12, pady=2)
        else:
            tk.Label(comentarios, text="Sin comentarios registrados para este evento.",
                     font=("Arial", 9), bg="white", fg="#777").pack(anchor="w", padx=12, pady=(0, 10))

        estadisticas = self.tarjeta_capitan(derecha, "Desempeno del evento")
        calificacion = analisis["calificacion_promedio"]
        self.fila_capitan(estadisticas, "Calificacion promedio", f"{calificacion:.1f}/5" if calificacion else "Sin datos")
        self.fila_capitan(estadisticas, "Buenos", str(analisis["buenos"]))
        self.fila_capitan(estadisticas, "Neutrales", str(analisis["neutrales"]))
        self.fila_capitan(estadisticas, "Malos", str(analisis["malos"]))

        propinas = self.tarjeta_capitan(derecha, "Propinas aproximadas")
        self.fila_capitan(propinas, "Total registrado", formato_moneda(analisis["total_propinas"]) if analisis["total_propinas"] else "Sin datos")
        self.fila_capitan(propinas, "Promedio reportado", formato_moneda(analisis["promedio_propina"]) if analisis["promedio_propina"] else "Sin datos")
        self.fila_capitan(propinas, "Estimado por mesero", formato_moneda(analisis["propina_por_mesero"]) if analisis["propina_por_mesero"] else "Sin datos")

    def analizar_evento_capitan(self, evento):
        comentarios = []
        try:
            comentarios.extend([c for c in GestorArchivos.cargar_comentarios() if c.get("fecha") == evento.fecha])
        except Exception:
            pass
        try:
            comentarios.extend([c.to_dict() for c in GestorArchivos.cargar_comentarios_mesero() if c.fecha == evento.fecha])
        except Exception:
            pass
        try:
            comentarios.extend([c.to_dict() for c in GestorArchivos.cargar_comentarios_evento() if c.fecha == evento.fecha])
        except Exception:
            pass

        organizacion = GestorArchivos.buscar_organizacion_por_fecha(evento.fecha)
        num_meseros = len(organizacion.meseros) if organizacion else 0
        sugeridos = meseros_sugeridos_evento(evento)
        faltantes = max(sugeridos - num_meseros, 0)
        calificaciones = []
        ganancias = []
        destacados = []
        buenos = neutrales = malos = 0

        for comentario in comentarios:
            calificacion = numero_desde_texto(comentario.get("calificacion") or comentario.get("calificacion_promedio"))
            if calificacion:
                calificaciones.append(calificacion)
                if calificacion >= 4:
                    buenos += 1
                elif calificacion >= 3:
                    neutrales += 1
                else:
                    malos += 1
            ganancia = numero_desde_texto(comentario.get("ganancia") or comentario.get("ganancia_total"))
            if ganancia:
                ganancias.append(ganancia)
            for campo in ("sentir", "observaciones", "reporte", "satisfaccion_general"):
                texto = str(comentario.get(campo, "")).strip()
                if texto and texto.lower() not in {"n/a", "na", "ninguno"}:
                    destacados.append(texto)

        total_propinas = sum(ganancias)
        return {
            "organizacion": organizacion,
            "num_meseros": num_meseros,
            "meseros_sugeridos": sugeridos,
            "faltantes_meseros": faltantes,
            "destacados": destacados[:5],
            "buenos": buenos,
            "neutrales": neutrales,
            "malos": malos,
            "calificacion_promedio": sum(calificaciones) / len(calificaciones) if calificaciones else 0,
            "total_propinas": total_propinas,
            "promedio_propina": total_propinas / len(ganancias) if ganancias else 0,
            "propina_por_mesero": total_propinas / num_meseros if num_meseros else 0,
        }

    def publicar_necesidad_meseros(self, evento, analisis):
        faltantes = analisis.get("faltantes_meseros", 0)
        sugerido = analisis.get("meseros_sugeridos", 0)
        cantidad = simpledialog.askinteger(
            "Necesito mas meseros",
            "Meseros requeridos para publicar:",
            initialvalue=max(faltantes, 1),
            minvalue=1,
        )
        if not cantidad:
            return
        oferta = OfertaTrabajo(
            evento.fecha,
            titulo=f"Refuerzo de meseros - {evento.fecha}",
            descripcion=(
                f"Evento de {evento.total_invitados()} invitados y {len(mesas_visibles_evento(evento))} mesas. "
                f"Sugerencia automatica: {sugerido} mesero(s). Servicios: {servicios_evento_texto(evento)}."
            ),
            meseros_requeridos=cantidad,
        )
        GestorArchivos.guardar_oferta(oferta)
        messagebox.showinfo("Oferta preparada", f"Se guardo una oferta local para {cantidad} mesero(s).")

    def tarjeta_capitan(self, parent, titulo):
        frame = tk.Frame(parent, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
        frame.pack(fill="x", pady=6)
        tk.Label(frame, text=titulo, font=("Arial", 12, "bold"), bg="white", fg=TXT).pack(anchor="w", padx=12, pady=(9, 4))
        return frame

    def fila_capitan(self, parent, etiqueta, valor):
        fila = tk.Frame(parent, bg="white")
        fila.pack(fill="x", padx=12, pady=2)
        tk.Label(fila, text=f"{etiqueta}:", font=("Arial", 9, "bold"), bg="white", fg=TXT, width=20, anchor="w").pack(side="left")
        tk.Label(fila, text=valor, font=("Arial", 9), bg="white", fg="#555", anchor="w",
                 wraplength=300, justify="left").pack(side="left", fill="x", expand=True)

    def fila_color_capitan(self, parent, color, texto):
        fila = tk.Frame(parent, bg="white")
        fila.pack(fill="x", padx=12, pady=2)
        muestra = tk.Canvas(fila, width=18, height=18, bg="white", highlightthickness=0)
        muestra.pack(side="left", padx=(0, 6))
        muestra.create_rectangle(2, 2, 16, 16, fill=color, outline="#555")
        tk.Label(fila, text=texto, font=("Arial", 9), bg="white", fg="#555",
                 anchor="w").pack(side="left", fill="x", expand=True)

    def dibujar_croquis_capitan(self, parent, evento, organizacion=None):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", padx=12, pady=(0, 10))
        cell = 50
        canvas = tk.Canvas(frame, width=(COLUMNAS + 2) * cell, height=(FILAS + 1) * cell,
                           bg="#F8FAFC", highlightthickness=1, highlightbackground="#CBD5E1")
        canvas.pack(side="left")
        canvas.create_rectangle(3 * cell, 4, 5 * cell, int(cell * 0.75),
                                fill="#8B5E34", outline="#6B3F1D", width=2)
        canvas.create_text(4 * cell, int(cell * 0.38), text=f"Principal\n{evento.principal}",
                           fill="white", font=("Arial", 8, "bold"))
        canvas.create_rectangle(3 * cell, 1 * cell, 5 * cell, 3 * cell,
                                fill="#111827", outline="#030712", width=2)
        canvas.create_text(4 * cell, int(2 * cell), text="PISTA",
                           fill="white", font=("Arial", 10, "bold"))
        self.dibujar_servicios_capitan(canvas, evento, cell)
        colores = self.colores_organizacion_capitan(organizacion)
        for mesa in evento.mesas:
            x1 = mesa.col * cell
            y1 = mesa.fila * cell
            x2 = (mesa.col + 1) * cell
            y2 = (mesa.fila + 1) * cell
            color = colores.get((mesa.col, mesa.fila), mesa.color)
            if color == "lightgray":
                color = "#E5E7EB"
            canvas.create_oval(x1 + 7, y1 + 7, x2 - 7, y2 - 7,
                               fill=color, outline="#94A3B8", width=2)
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                               text=str(mesa.personas), fill=TXT, font=("Arial", 8, "bold"))

    def dibujar_servicios_capitan(self, canvas, evento, cell):
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

    def colores_organizacion_capitan(self, organizacion):
        colores = {}
        if not organizacion:
            return colores
        for clave, color in organizacion.colores.items():
            numeros = re.findall(r"\d+", str(clave))
            if len(numeros) >= 2:
                colores[(int(numeros[0]), int(numeros[1]))] = color
        return colores


class FrameListaEventos(DashboardCapitanMixin, FrameBase):
    """Frame para listar eventos no organizados."""
    def __init__(self, master, modo="cargar", **kwargs):
        self.modo = modo
        super().__init__(master, **kwargs)

    def configurar(self):
        tk.Label(self, text="Eventos asignados", font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(14, 2))
        tk.Label(self, text="Pendientes por organizar. Abre un evento para asignar mesas por color/mesero.",
                 font=("Arial", 10), bg=BG, fg="#555").pack()
        
        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        
        # Filtrar eventos no organizados
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        if not eventos_no_org:
            tk.Label(self, text="No hay eventos pendientes de organizar", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                     bg="#777", fg="white", activebackground="#777", activeforeground="white",
                     relief="flat", width=20, height=2, cursor="hand2").pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=64, height=15,
                                  yscrollcommand=scrollbar.set,
                                  font=("Arial", 11),
                                  selectbackground=BTN2,
                                  selectforeground="white")
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, evento in enumerate(eventos_no_org):
            total = evento.total_invitados()
            self.listbox.insert(tk.END, f"{i} - PENDIENTE - {evento.fecha} - {total} invitados")
            self.listbox.itemconfig(i, bg="#FEF2F2", fg="#991B1B")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir evento", command=self.abrir_evento,
                 bg=BTN, fg="white", activebackground=BTN, activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)
        tk.Button(frame_botones, text="Ver dashboard", command=self.ver_dashboard_evento,
                 bg="#7C3AED", fg="white", activebackground="#7C3AED", activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                 bg="#777", fg="white", activebackground="#777", activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)

    def abrir_evento(self):
        """Abre el evento seleccionado."""
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Selección", "Por favor, selecciona un evento")
            return
        
        # Obtener el índice real del evento
        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        
        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        evento = eventos_no_org[int(indice_texto)]
        self.master.cambiar_frame(FrameCroquis, modo="capitan", evento=evento)

    def ver_dashboard_evento(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Seleccion", "Por favor, selecciona un evento")
            return

        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        self.abrir_dashboard_capitan(eventos_no_org[int(indice_texto)])

class FrameListaOrganizaciones(DashboardCapitanMixin, FrameBase):
    """Frame para listar organizaciones guardadas."""
    def __init__(self, master, modo_mesero=False, **kwargs):
        self.modo_mesero = modo_mesero
        super().__init__(master, **kwargs)

    def configurar(self):
        titulo = "Organizaciones disponibles para meseros" if self.modo_mesero else "Organizaciones guardadas"
        tk.Label(self, text=titulo, font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(14, 2))
        tk.Label(self, text="Abre una organizacion para revisar o ajustar colores y nombres de meseros.",
                 font=("Arial", 10), bg=BG, fg="#555").pack()
        
        organizaciones = GestorArchivos.cargar_organizaciones()
        
        if not organizaciones:
            tk.Label(self, text="No hay organizaciones guardadas", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
            tk.Button(self, text="Volver", command=lambda: self.volver(btn_volver),
                     bg="#777", fg="white", activebackground="#777", activeforeground="white",
                     relief="flat", width=20, height=2, cursor="hand2").pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=64, height=15,
                                  yscrollcommand=scrollbar.set,
                                  font=("Arial", 11),
                                  selectbackground=BTN2,
                                  selectforeground="white")
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, org in enumerate(organizaciones):
            num_meseros = len(org.meseros)
            self.listbox.insert(tk.END, f"{i} - {org.fecha} - {num_meseros} meseros")
            self.listbox.itemconfig(i, bg="#F0FDF4", fg="#166534")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir organización", command=self.abrir_organizacion,
                 bg=BTN, fg="white", activebackground=BTN, activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)
        
        if not self.modo_mesero:
            tk.Button(frame_botones, text="Ver dashboard", command=self.ver_dashboard_organizacion,
                     bg="#7C3AED", fg="white", activebackground="#7C3AED", activeforeground="white",
                     relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)

        btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(btn_volver),
                 bg="#777", fg="white", activebackground="#777", activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)

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

    def ver_dashboard_organizacion(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Seleccion", "Por favor, selecciona una organizacion")
            return

        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        organizaciones = GestorArchivos.cargar_organizaciones()
        org = organizaciones[int(indice_texto)]
        evento = GestorArchivos.buscar_evento_por_fecha(org.fecha)
        if not evento:
            messagebox.showerror("Error", "No se encontro el evento asociado")
            return
        self.abrir_dashboard_capitan(evento)

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
            canvas = tk.Canvas(frame, width=(COLUMNAS+2)*CELL//2, height=(FILAS+1)*CELL//2, bg="white")
            canvas.pack(side="left", padx=10)
            
            scale = 0.5
            
            def sx(x): return int(x*scale)
            def sy(y): return int(y*scale)
            
            # Título
            canvas.create_text(sx((COLUMNAS + 2) * CELL / 2), sy(15), text=titulo, font=("Arial", 10, "bold"))
            
            # Mesa principal
            canvas.create_rectangle(sx(3*CELL), sy(20), sx(5*CELL), sy(20+CELL*0.7), fill="brown")
            canvas.create_text(sx(4*CELL), sy(20+0.35*CELL),
                              text=f"P:{evento.principal}", fill="white")
            
            # Pista
            canvas.create_rectangle(sx(3*CELL), sy(1*CELL+20), sx(5*CELL), sy(3*CELL+20), fill="black")
            canvas.create_text(sx(4*CELL), sy(2*CELL+20), text="PISTA", fill="white")
            
            # Mesas
            for mesa in evento.mesas:
                x1 = sx(mesa.col*CELL)
                y1 = sy(mesa.fila*CELL+20)
                x2 = sx((mesa.col+1)*CELL)
                y2 = sy((mesa.fila+1)*CELL+20)
                
                canvas.create_oval(x1+sx(5), y1+sy(5), x2-sx(5), y2-sy(5), fill="lightgray")
                canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(mesa.personas))
        
        frame_comp = tk.Frame(self.frame_canvas, bg=BG)
        frame_comp.pack()
        
        dibujar_uno(frame_comp, ev1, "Evento Actual")
        dibujar_uno(frame_comp, ev2, "Evento Siguiente")
