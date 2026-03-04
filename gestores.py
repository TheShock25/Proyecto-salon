# gestores.py
import json
import os
import csv
from datetime import datetime
from modelos import Evento, Organizacion, Comentario, ComentarioMesero, ComentarioEvento
from constantes import *

class GestorArchivos:
    """Clase con métodos estáticos para manejar la persistencia de datos."""

    # --- Eventos ---
    @staticmethod
    def cargar_eventos():
        if not os.path.exists(ARCHIVO_EVENTOS):
            return []
        with open(ARCHIVO_EVENTOS, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [Evento.from_dict(data) for data in data_list]

    @staticmethod
    def guardar_evento(evento):
        eventos = GestorArchivos.cargar_eventos()
        # Reemplazar si ya existe
        for i, e in enumerate(eventos):
            if e.fecha == evento.fecha:
                eventos[i] = evento
                break
        else:
            eventos.append(evento)

        with open(ARCHIVO_EVENTOS, "w", encoding="utf8") as f:
            json.dump([e.to_dict() for e in eventos], f, indent=4, ensure_ascii=False)

    @staticmethod
    def buscar_evento_por_fecha(fecha):
        """Busca un evento por su fecha."""
        eventos = GestorArchivos.cargar_eventos()
        for evento in eventos:
            if evento.fecha == fecha:
                return evento
        return None

    # --- Organización ---
    @staticmethod
    def cargar_organizaciones():
        if not os.path.exists(ARCHIVO_ORG):
            return []
        with open(ARCHIVO_ORG, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [Organizacion.from_dict(data) for data in data_list]

    @staticmethod
    def guardar_organizacion(organizacion):
        orgs = GestorArchivos.cargar_organizaciones()
        for i, o in enumerate(orgs):
            if o.fecha == organizacion.fecha:
                orgs[i] = organizacion
                break
        else:
            orgs.append(organizacion)

        with open(ARCHIVO_ORG, "w", encoding="utf8") as f:
            json.dump([o.to_dict() for o in orgs], f, indent=4, ensure_ascii=False)

    @staticmethod
    def buscar_organizacion_por_fecha(fecha):
        """Busca una organización por su fecha."""
        orgs = GestorArchivos.cargar_organizaciones()
        for org in orgs:
            if org.fecha == fecha:
                return org
        return None

    # --- Comentarios generales ---
    @staticmethod
    def cargar_comentarios():
        if not os.path.exists(ARCHIVO_COMENTARIOS):
            return []
        with open(ARCHIVO_COMENTARIOS, "r", encoding="utf8") as f:
            return json.load(f)

    @staticmethod
    def guardar_comentario(data):
        lista = GestorArchivos.cargar_comentarios()
        
        # Buscar si ya existe un comentario para esta fecha
        encontrado = False
        for i, c in enumerate(lista):
            if c.get("fecha") == data.get("fecha"):
                lista[i] = data
                encontrado = True
                break
        
        if not encontrado:
            lista.append(data)
        
        with open(ARCHIVO_COMENTARIOS, "w", encoding="utf8") as f:
            json.dump(lista, f, indent=4, ensure_ascii=False)

    # --- Comentarios Mesero ---
    @staticmethod
    def cargar_comentarios_mesero():
        if not os.path.exists(ARCHIVO_COMENTARIOS_MESERO):
            return []
        with open(ARCHIVO_COMENTARIOS_MESERO, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [ComentarioMesero.from_dict(data) for data in data_list]

    @staticmethod
    def guardar_comentario_mesero(comentario):
        comentarios = GestorArchivos.cargar_comentarios_mesero()
        for i, c in enumerate(comentarios):
            if c.fecha == comentario.fecha and c.usuario == comentario.usuario:
                comentarios[i] = comentario
                break
        else:
            comentarios.append(comentario)

        with open(ARCHIVO_COMENTARIOS_MESERO, "w", encoding="utf8") as f:
            json.dump([c.to_dict() for c in comentarios], f, indent=4, ensure_ascii=False)

    # --- Comentarios Evento (Generales) ---
    @staticmethod
    def cargar_comentarios_evento():
        if not os.path.exists(ARCHIVO_COMENTARIOS_EVENTO):
            return []
        with open(ARCHIVO_COMENTARIOS_EVENTO, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [ComentarioEvento.from_dict(data) for data in data_list]

    @staticmethod
    def guardar_comentario_evento(comentario):
        comentarios = GestorArchivos.cargar_comentarios_evento()
        for i, c in enumerate(comentarios):
            if c.fecha == comentario.fecha:
                comentarios[i] = comentario
                break
        else:
            comentarios.append(comentario)

        with open(ARCHIVO_COMENTARIOS_EVENTO, "w", encoding="utf8") as f:
            json.dump([c.to_dict() for c in comentarios], f, indent=4, ensure_ascii=False)

    # --- Exportación ---
    @staticmethod
    def exportar_comentarios_a_excel():
        """Exporta todos los comentarios a formato CSV para estadísticas."""
        archivos_generados = []
        
        # Exportar comentarios de meseros
        comentarios_mesero = GestorArchivos.cargar_comentarios_mesero()
        if comentarios_mesero:
            nombre_archivo_mesero = f"comentarios_meseros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(nombre_archivo_mesero, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha Evento', 'Usuario', 'Rol', 'Ganancia', 'Satisfaccion', 
                               'Observaciones', 'Reportes', 'Calificacion', 'Timestamp'])
                for c in comentarios_mesero:
                    writer.writerow([
                        c.fecha,
                        c.usuario,
                        c.rol,
                        c.ganancia,
                        c.sentir,
                        c.observaciones,
                        c.reporte,
                        c.calificacion,
                        c.timestamp
                    ])
            archivos_generados.append(nombre_archivo_mesero)
        
        # Exportar comentarios de eventos
        comentarios_evento = GestorArchivos.cargar_comentarios_evento()
        if comentarios_evento:
            nombre_archivo_evento = f"comentarios_eventos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(nombre_archivo_evento, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Fecha Evento', 'Ganancia Total', 'Satisfaccion General', 
                               'Observaciones', 'Reportes', 'Calificacion Promedio', 'Numero Meseros', 'Timestamp'])
                for c in comentarios_evento:
                    writer.writerow([
                        c.fecha,
                        c.ganancia_total,
                        c.satisfaccion_general,
                        c.observaciones,
                        c.reporte,
                        c.calificacion_promedio,
                        c.num_meseros,
                        c.timestamp
                    ])
            archivos_generados.append(nombre_archivo_evento)
        
        return archivos_generados