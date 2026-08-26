# modelos.py
import datetime


class Salon:
    """Datos publicos y operativos de un salon."""
    def __init__(self, nombre="Sistema Salon", direccion="", telefono="", correo="", zona="", logo="", precio_base=0.0, precio_por_persona=0.0, extra=None):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo
        self.zona = zona
        self.logo = logo
        self.precio_base = float(precio_base or 0)
        self.precio_por_persona = float(precio_por_persona or 0)
        self.extra = extra if extra is not None else {}

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "zona": self.zona,
            "logo": self.logo,
            "precio_base": self.precio_base,
            "precio_por_persona": self.precio_por_persona,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("nombre", "Sistema Salon"),
            data.get("direccion", ""),
            data.get("telefono", ""),
            data.get("correo", ""),
            data.get("zona", ""),
            data.get("logo", ""),
            data.get("precio_base", 0),
            data.get("precio_por_persona", 0),
            data.get("extra", {}),
        )


class Mesero:
    """Persona que busca servicios y construye historial laboral."""
    def __init__(self, nombre, telefono="", correo="", zona="", experiencia="", habilidades=None, estado="activo", mesero_id=None):
        self.id = mesero_id
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.zona = zona
        self.experiencia = experiencia
        self.habilidades = habilidades if habilidades is not None else []
        self.estado = estado

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "correo": self.correo,
            "zona": self.zona,
            "experiencia": self.experiencia,
            "habilidades": self.habilidades,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("nombre", ""),
            data.get("telefono", ""),
            data.get("correo", ""),
            data.get("zona", ""),
            data.get("experiencia", ""),
            data.get("habilidades", []),
            data.get("estado", "activo"),
            data.get("id"),
        )


class PerfilMesero:
    """Perfil generado desde entrevista, habilidades e historial."""
    def __init__(self, mesero_id, entrevista=None, habilidades=None, resumen="", reputacion=None):
        self.mesero_id = mesero_id
        self.entrevista = entrevista if entrevista is not None else {}
        self.habilidades = habilidades if habilidades is not None else []
        self.resumen = resumen
        self.reputacion = reputacion if reputacion is not None else {}

    def to_dict(self):
        return {
            "mesero_id": self.mesero_id,
            "entrevista": self.entrevista,
            "habilidades": self.habilidades,
            "resumen": self.resumen,
            "reputacion": self.reputacion,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("mesero_id"),
            data.get("entrevista", {}),
            data.get("habilidades", []),
            data.get("resumen", ""),
            data.get("reputacion", {}),
        )


class OfertaTrabajo:
    """Oferta publicada por un capitan o salon para cubrir meseros."""
    def __init__(self, fecha_evento, titulo="", descripcion="", zona="", pago_ofrecido=0.0, propina_esperada=0.0, meseros_requeridos=0, salon_id=1, estado="activa", oferta_id=None):
        self.id = oferta_id
        self.salon_id = salon_id
        self.fecha_evento = fecha_evento
        self.titulo = titulo
        self.descripcion = descripcion
        self.zona = zona
        self.pago_ofrecido = float(pago_ofrecido or 0)
        self.propina_esperada = float(propina_esperada or 0)
        self.meseros_requeridos = int(meseros_requeridos or 0)
        self.estado = estado

    def to_dict(self):
        return {
            "id": self.id,
            "salon_id": self.salon_id,
            "fecha_evento": self.fecha_evento,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "zona": self.zona,
            "pago_ofrecido": self.pago_ofrecido,
            "propina_esperada": self.propina_esperada,
            "meseros_requeridos": self.meseros_requeridos,
            "estado": self.estado,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("fecha_evento", ""),
            data.get("titulo", ""),
            data.get("descripcion", ""),
            data.get("zona", ""),
            data.get("pago_ofrecido", 0),
            data.get("propina_esperada", 0),
            data.get("meseros_requeridos", 0),
            data.get("salon_id", 1),
            data.get("estado", "activa"),
            data.get("id"),
        )


class Postulacion:
    """Postulacion de un mesero a una oferta."""
    def __init__(self, oferta_id, mesero_id, estado="pendiente", mensaje="", postulacion_id=None):
        self.id = postulacion_id
        self.oferta_id = oferta_id
        self.mesero_id = mesero_id
        self.estado = estado
        self.mensaje = mensaje

    def to_dict(self):
        return {
            "id": self.id,
            "oferta_id": self.oferta_id,
            "mesero_id": self.mesero_id,
            "estado": self.estado,
            "mensaje": self.mensaje,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("oferta_id"),
            data.get("mesero_id"),
            data.get("estado", "pendiente"),
            data.get("mensaje", ""),
            data.get("id"),
        )


class ResultadoAnalizador:
    """Resultado preparado para conectar el analizador de sentimientos."""
    def __init__(self, entidad_tipo, entidad_id, fecha="", origen="", resumen="", sentimiento="", score=0.0, tendencias=None, data=None, resultado_id=None):
        self.id = resultado_id
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.fecha = fecha
        self.origen = origen
        self.resumen = resumen
        self.sentimiento = sentimiento
        self.score = float(score or 0)
        self.tendencias = tendencias if tendencias is not None else {}
        self.data = data if data is not None else {}

    def to_dict(self):
        return {
            "id": self.id,
            "entidad_tipo": self.entidad_tipo,
            "entidad_id": self.entidad_id,
            "fecha": self.fecha,
            "origen": self.origen,
            "resumen": self.resumen,
            "sentimiento": self.sentimiento,
            "score": self.score,
            "tendencias": self.tendencias,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("entidad_tipo", ""),
            data.get("entidad_id", ""),
            data.get("fecha", ""),
            data.get("origen", ""),
            data.get("resumen", ""),
            data.get("sentimiento", ""),
            data.get("score", 0),
            data.get("tendencias", {}),
            data.get("data", {}),
            data.get("id"),
        )

class Mesa:
    """Representa una mesa en un evento."""
    def __init__(self, col, fila, personas=0, nombre=None, color="lightgray", adultos=None, ninos=0):
        self.col = col
        self.fila = fila
        self.personas = int(personas or 0)
        self.nombre = nombre
        self.color = color
        self.ninos = int(ninos or 0)
        self.adultos = int(adultos) if adultos is not None else max(self.personas - self.ninos, 0)

    def to_dict(self):
        """Convierte la mesa a diccionario para guardar en JSON."""
        return {
            "col": self.col,
            "fila": self.fila,
            "personas": self.personas,
            "nombre": self.nombre,
            "color": self.color,
            "adultos": self.adultos,
            "ninos": self.ninos
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una mesa desde un diccionario (desde JSON)."""
        return cls(
            data["col"], 
            data["fila"], 
            data.get("personas", 0), 
            data.get("nombre"), 
            data.get("color", "lightgray"),
            data.get("adultos"),
            data.get("ninos", 0)
        )


class Evento:
    """Representa un evento/reservación."""
    def __init__(self, fecha, principal=2, mesas=None, servicios=None):
        self.fecha = fecha  # Formato string "MM/DD/AA"
        self.principal = principal
        self.mesas = mesas if mesas is not None else []  # Lista de objetos Mesa
        servicios = servicios if servicios is not None else {}
        self.servicios = {
            "pantalla": bool(servicios.get("pantalla", False)),
            "mesa_pastel": bool(servicios.get("mesa_pastel", False)),
            "dulces": bool(servicios.get("dulces", False)),
            "cocina": bool(servicios.get("cocina", False)),
            "barra": bool(servicios.get("barra", False)),
            "area_fotos": bool(servicios.get("area_fotos", True)),
            "animador": bool(servicios.get("animador", False)),
            "menu_infantil": bool(servicios.get("menu_infantil", False)),
        }

    def total_invitados(self):
        """Calcula el total de invitados del evento."""
        return self.principal + sum(m.personas for m in self.mesas)

    def to_dict(self):
        """Convierte el evento a diccionario para guardar en JSON."""
        return {
            "fecha": self.fecha,
            "principal": self.principal,
            "mesas": [m.to_dict() for m in self.mesas],
            "servicios": self.servicios
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un evento desde un diccionario (desde JSON)."""
        mesas = [Mesa.from_dict(m) for m in data.get("mesas", [])]
        return cls(data["fecha"], data.get("principal", 2), mesas, data.get("servicios", {}))


class Organizacion:
    """Representa la organización de un evento (asignación de meseros)."""
    def __init__(self, fecha, meseros=None, colores=None, nombres_meseros=None):
        self.fecha = fecha
        # meseros: dict { "nombre_color": total_personas_asignadas }
        self.meseros = meseros if meseros is not None else {}
        # colores: dict { "(col,fila)": "nombre_color" } para guardar qué mesa es de qué color
        self.colores = colores if colores is not None else {}
        self.nombres_meseros = nombres_meseros if nombres_meseros is not None else {}

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "meseros": self.meseros,
            "colores": self.colores,
            "nombres_meseros": self.nombres_meseros
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["fecha"], data.get("meseros", {}), data.get("colores", {}), data.get("nombres_meseros", {}))


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


class InventarioItem:
    """Representa un articulo contado dentro del inventario del salon."""
    def __init__(self, nombre, categoria="", total=0, danadas=0, costo_unitario=0.0, notas=""):
        self.nombre = nombre
        self.categoria = categoria
        self.total = int(total or 0)
        self.danadas = int(danadas or 0)
        self.costo_unitario = float(costo_unitario or 0)
        self.notas = notas

    @property
    def disponibles(self):
        return max(self.total - self.danadas, 0)

    @property
    def costo_reposicion(self):
        return self.danadas * self.costo_unitario

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "categoria": self.categoria,
            "total": self.total,
            "danadas": self.danadas,
            "costo_unitario": self.costo_unitario,
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("nombre", ""),
            data.get("categoria", ""),
            data.get("total", 0),
            data.get("danadas", 0),
            data.get("costo_unitario", 0),
            data.get("notas", ""),
        )


class InventarioCorte:
    """Foto del inventario en una fecha determinada."""
    def __init__(self, fecha, articulos=None, notas=""):
        self.fecha = fecha
        self.articulos = articulos if articulos is not None else []
        self.notas = notas

    def costo_reposicion_total(self):
        return sum(item.costo_reposicion for item in self.articulos)

    def to_dict(self):
        return {
            "fecha": self.fecha,
            "articulos": [item.to_dict() for item in self.articulos],
            "notas": self.notas,
        }

    @classmethod
    def from_dict(cls, data):
        articulos = [InventarioItem.from_dict(item) for item in data.get("articulos", [])]
        return cls(data.get("fecha", ""), articulos, data.get("notas", ""))
