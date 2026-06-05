class LazyFrame:
    def __init__(self, nombre):
        self.nombre = nombre

    def __call__(self, *args, **kwargs):
        frame_class = resolver_frame(self.nombre)
        return frame_class(*args, **kwargs)


def resolver_frame(nombre):
    modulos = {
        "Aplicacion": "pantallas.app",
        "FrameLogin": "pantallas.login",
        "FrameMenuAdmin": "pantallas.menus",
        "FrameMenuCapitan": "pantallas.menus",
        "FrameMenuMesero": "pantallas.menus",
        "FrameSeleccionFecha": "pantallas.patron",
        "FrameCalendario": "pantallas.patron",
        "FrameInventario": "pantallas.inventario",
        "FrameDashboardPatron": "pantallas.dashboard_patron",
        "FrameCroquis": "pantallas.croquis",
        "FrameListaEventos": "pantallas.capitan",
        "FrameListaOrganizaciones": "pantallas.capitan",
        "FrameCompararEventos": "pantallas.capitan",
        "FrameComentariosMesero": "pantallas.mesero",
        "FrameEstadisticas": "pantallas.mesero",
    }
    if nombre not in modulos:
        raise ValueError(f"Pantalla no registrada: {nombre}")

    module_name = modulos[nombre]
    module = __import__(module_name, fromlist=[nombre])
    return getattr(module, nombre)


FrameLogin = LazyFrame("FrameLogin")
FrameMenuAdmin = LazyFrame("FrameMenuAdmin")
FrameMenuCapitan = LazyFrame("FrameMenuCapitan")
FrameMenuMesero = LazyFrame("FrameMenuMesero")
FrameSeleccionFecha = LazyFrame("FrameSeleccionFecha")
FrameCalendario = LazyFrame("FrameCalendario")
FrameInventario = LazyFrame("FrameInventario")
FrameDashboardPatron = LazyFrame("FrameDashboardPatron")
FrameCroquis = LazyFrame("FrameCroquis")
FrameListaEventos = LazyFrame("FrameListaEventos")
FrameListaOrganizaciones = LazyFrame("FrameListaOrganizaciones")
FrameCompararEventos = LazyFrame("FrameCompararEventos")
FrameComentariosMesero = LazyFrame("FrameComentariosMesero")
FrameEstadisticas = LazyFrame("FrameEstadisticas")

__all__ = [
    "FrameLogin",
    "FrameMenuAdmin",
    "FrameMenuCapitan",
    "FrameMenuMesero",
    "FrameSeleccionFecha",
    "FrameCalendario",
    "FrameInventario",
    "FrameDashboardPatron",
    "FrameCroquis",
    "FrameListaEventos",
    "FrameListaOrganizaciones",
    "FrameCompararEventos",
    "FrameComentariosMesero",
    "FrameEstadisticas",
]
