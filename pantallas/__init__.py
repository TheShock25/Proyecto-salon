from .app import Aplicacion
from .base import FrameBase
from .capitan import FrameCompararEventos, FrameListaEventos, FrameListaOrganizaciones
from .croquis import FrameCroquis
from .dashboard_patron import FrameDashboardPatron
from .inventario import FrameInventario
from .login import FrameLogin
from .menus import FrameMenuAdmin, FrameMenuCapitan, FrameMenuMesero
from .mesero import FrameComentariosMesero, FrameEstadisticas
from .patron import FrameCalendario, FrameSeleccionFecha

__all__ = [
    "Aplicacion",
    "FrameBase",
    "FrameLogin",
    "FrameMenuAdmin",
    "FrameMenuCapitan",
    "FrameMenuMesero",
    "FrameSeleccionFecha",
    "FrameCroquis",
    "FrameCalendario",
    "FrameInventario",
    "FrameDashboardPatron",
    "FrameListaEventos",
    "FrameListaOrganizaciones",
    "FrameCompararEventos",
    "FrameComentariosMesero",
    "FrameEstadisticas",
]
