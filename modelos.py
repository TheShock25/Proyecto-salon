# modelos.py
import datetime

class Mesa:
    """Representa una mesa en un evento."""
    def __init__(self, col, fila, personas=0, nombre=None, color="lightgray"):
        self.col = col
        self.fila = fila
        self.personas = personas
        self.nombre = nombre
        self.color = color

    def to_dict(self):
        """Convierte la mesa a diccionario para guardar en JSON."""
        return {
            "col": self.col,
            "fila": self.fila,
            "personas": self.personas,
            "nombre": self.nombre,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una mesa desde un diccionario (desde JSON)."""
        return cls(
            data["col"], 
            data["fila"], 
            data.get("personas", 0), 
            data.get("nombre"), 
            data.get("color", "lightgray")
        )


class Evento:
    """Representa un evento/reservación."""
    def __init__(self, fecha, principal=2, mesas=None):
        self.fecha = fecha  # Formato string "MM/DD/AA"
        self.principal = principal
        self.mesas = mesas if mesas is not None else []  # Lista de objetos Mesa

    def total_invitados(self):
        """Calcula el total de invitados del evento."""
        return self.principal + sum(m.personas for m in self.mesas)

    def to_dict(self):
        """Convierte el evento a diccionario para guardar en JSON."""
        return {
            "fecha": self.fecha,
            "principal": self.principal,
            "mesas": [m.to_dict() for m in self.mesas]
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un evento desde un diccionario (desde JSON)."""
        mesas = [Mesa.from_dict(m) for m in data.get("mesas", [])]
        return cls(data["fecha"], data.get("principal", 2), mesas)


class Organizacion:
    """Representa la organización de un evento (asignación de meseros)."""
    def __init__(self, fecha, meseros=None, colores=None):
        self.fecha = fecha
        # meseros: dict { "nombre_color": total_personas_asignadas }
        self.meseros = meseros if meseros is not None else {}
        # colores: dict { "(col,fila)": "nombre_color" } para guardar qué mesa es de qué color
        self.colores = colores if colores is not None else {}

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "meseros": self.meseros,
            "colores": self.colores
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["fecha"], data.get("meseros", {}), data.get("colores", {}))


class Comentario:
    """Clase base para comentarios."""
    def __init__(self, fecha, timestamp=None, ganancia="", sentir="", observaciones="", reporte="", calificacion="5"):
        self.fecha = fecha
        self.timestamp = timestamp if timestamp else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ganancia = ganancia
        self.sentir = sentir
        self.observaciones = observaciones
        self.reporte = reporte
        self.calificacion = calificacion

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "timestamp": self.timestamp,
            "ganancia": self.ganancia,
            "sentir": self.sentir,
            "observaciones": self.observaciones,
            "reporte": self.reporte,
            "calificacion": self.calificacion
        }


class ComentarioMesero(Comentario):
    """Comentario hecho por un mesero."""
    def __init__(self, fecha, usuario, rol, **kwargs):
        super().__init__(fecha, **kwargs)
        self.usuario = usuario
        self.rol = rol

    def to_dict(self):
        data = super().to_dict()
        data.update({"usuario": self.usuario, "rol": self.rol})
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["fecha"], data["usuario"], data["rol"],
            timestamp=data.get("timestamp"),
            ganancia=data.get("ganancia", ""),
            sentir=data.get("sentir", ""),
            observaciones=data.get("observaciones", ""),
            reporte=data.get("reporte", ""),
            calificacion=data.get("calificacion", "5")
        )


class ComentarioEvento(Comentario):
    """Comentario general del evento."""
    def __init__(self, fecha, ganancia_total="", satisfaccion_general="", num_meseros=0, calificacion_promedio="", **kwargs):
        super().__init__(fecha, **kwargs)
        self.ganancia_total = ganancia_total
        self.satisfaccion_general = satisfaccion_general
        self.num_meseros = num_meseros
        self.calificacion_promedio = calificacion_promedio

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "ganancia_total": self.ganancia_total,
            "satisfaccion_general": self.satisfaccion_general,
            "num_meseros": self.num_meseros,
            "calificacion_promedio": self.calificacion_promedio
        })
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["fecha"],
            ganancia_total=data.get("ganancia_total", ""),
            satisfaccion_general=data.get("satisfaccion_general", ""),
            num_meseros=data.get("num_meseros", 0),
            calificacion_promedio=data.get("calificacion_promedio", ""),
            timestamp=data.get("timestamp"),
            ganancia=data.get("ganancia", ""),
            sentir=data.get("sentir", ""),
            observaciones=data.get("observaciones", ""),
            reporte=data.get("reporte", ""),
            calificacion=data.get("calificacion", "5")
        )