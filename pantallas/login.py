import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

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
