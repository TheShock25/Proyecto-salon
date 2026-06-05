# vistas.py
#
# Fachada de compatibilidad. Las pantallas reales viven en el paquete pantallas/.
from pantallas import (
    Aplicacion,
    FrameBase,
    FrameCalendario,
    FrameComentariosMesero,
    FrameCompararEventos,
    FrameCroquis,
    FrameDashboardPatron,
    FrameEstadisticas,
    FrameInventario,
    FrameListaEventos,
    FrameListaOrganizaciones,
    FrameLogin,
    FrameMenuAdmin,
    FrameMenuCapitan,
    FrameMenuMesero,
    FrameSeleccionFecha,
)

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
