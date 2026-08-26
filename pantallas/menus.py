import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

class FrameMenuAdmin(FrameBase):
    def configurar(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(expand=True)

        tk.Label(frame, text="Panel Patron", font=("Arial", 24, "bold"), bg=BG, fg=TXT).pack(pady=(0, 6))
        tk.Label(frame, text="Reservas, disponibilidad y croquis del salon.", font=("Arial", 11), bg=BG, fg="#555").pack(pady=(0, 18))

        acciones = [
            ("Demostracion de croquis", "Probar acomodo automatico de invitados.", BTN2, lambda: self.volver(FrameCroquis, modo="demo")),
            ("Nueva reservacion", "Apartar fecha y preparar el croquis del evento.", BTN, lambda: self.volver(FrameSeleccionFecha)),
            ("Calendario de eventos", "Revisar fechas ocupadas y eventos guardados.", "#0F766E", lambda: self.volver(FrameCalendario)),
            ("Inventario y costos", "Capturar articulos, reposicion y comparaciones.", "#7C3AED", lambda: self.volver(FrameInventario)),
            ("Perfil del salon", "Guardar contacto, zona, logo y precios aproximados.", "#B45309", lambda: self.volver(FramePerfilSalon)),
            ("Estadisticas del salon", "Ver tendencias generales del salon y clientes.", "#1D4ED8", lambda: self.volver(FrameDashboardPatron)),
        ]

        for titulo, descripcion, color, comando in acciones:
            fila = tk.Frame(frame, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
            fila.pack(fill="x", pady=6)
            texto = tk.Frame(fila, bg="white")
            texto.pack(side="left", padx=14, pady=10)
            tk.Label(texto, text=titulo, font=("Arial", 12, "bold"), bg="white", fg=TXT, anchor="w").pack(anchor="w")
            tk.Label(texto, text=descripcion, font=("Arial", 9), bg="white", fg="#666", anchor="w").pack(anchor="w")
            tk.Button(fila, text="Abrir", bg=color, fg="white", activebackground=color, activeforeground="white",
                      relief="flat", width=12, height=2, cursor="hand2", command=comando).pack(side="right", padx=14)

        tk.Button(frame, text="Volver", bg="#777", fg="white", activebackground="#777", activeforeground="white",
                  relief="flat", width=20, height=2, cursor="hand2",
                  command=lambda: self.volver(FrameLogin)).pack(pady=(16, 0))

class FrameMenuCapitan(FrameBase):
    def configurar(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(expand=True)

        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {org.fecha for org in organizaciones}
        pendientes = [evento for evento in eventos if evento.fecha not in fechas_organizadas]

        tk.Label(frame, text="Panel Capitan", font=("Arial", 24, "bold"), bg=BG, fg=TXT).pack(pady=(0, 6))
        tk.Label(frame, text=f"Eventos pendientes por organizar: {len(pendientes)}", font=("Arial", 11, "bold"),
                 bg=BG, fg="#B45309" if pendientes else "#15803D").pack(pady=(0, 18))

        acciones = [
            ("Eventos asignados", "Abrir eventos pendientes y asignar mesas por mesero.", "#DC2626" if pendientes else BTN, lambda: self.volver(FrameListaEventos, modo="cargar")),
            ("Organizaciones guardadas", "Consultar o editar organizaciones ya preparadas.", BTN2, lambda: self.volver(FrameListaOrganizaciones)),
            ("Comparar eventos", "Revisar diferencia de invitados/sillas entre eventos.", "#0F766E", lambda: self.volver(FrameCompararEventos)),
        ]

        for titulo, descripcion, color, comando in acciones:
            fila = tk.Frame(frame, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
            fila.pack(fill="x", pady=6)
            texto = tk.Frame(fila, bg="white")
            texto.pack(side="left", padx=14, pady=10)
            tk.Label(texto, text=titulo, font=("Arial", 12, "bold"), bg="white", fg=TXT, anchor="w").pack(anchor="w")
            tk.Label(texto, text=descripcion, font=("Arial", 9), bg="white", fg="#666", anchor="w").pack(anchor="w")
            tk.Button(fila, text="Abrir", bg=color, fg="white", activebackground=color, activeforeground="white",
                      relief="flat", width=12, height=2, cursor="hand2", command=comando).pack(side="right", padx=14)

        tk.Button(frame, text="Volver", bg="#777", fg="white", activebackground="#777", activeforeground="white",
                  relief="flat", width=20, height=2, cursor="hand2",
                  command=lambda: self.volver(FrameLogin)).pack(pady=(16, 0))

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
