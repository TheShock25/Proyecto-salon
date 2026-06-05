import tkinter as tk

from constantes import BG

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
