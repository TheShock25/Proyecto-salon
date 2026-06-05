import tkinter as tk

from constantes import BG
from .lazy import FrameLogin

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
