# gestores.py
import json
import os
import csv
from datetime import datetime
from entidades.modelos import Evento, Mesa, Organizacion, Comentario, ComentarioMesero, ComentarioEvento, InventarioCorte
from constantes import *

class GestorArchivos:
    """Clase con métodos estáticos para manejar la persistencia de datos."""

    @staticmethod
    def asegurar_carpeta(ruta_archivo):
        carpeta = os.path.dirname(ruta_archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

    # --- Eventos ---
    @staticmethod
    def cargar_eventos():
        if not os.path.exists(ARCHIVO_EVENTOS):
            return []
        with open(ARCHIVO_EVENTOS, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [Evento.from_dict(data) for data in data_list]

    @staticmethod
    def cargar_eventos_con_csv():
        eventos = GestorArchivos.cargar_eventos()
        fechas_existentes = {evento.fecha for evento in eventos}
        if not os.path.exists(ARCHIVO_EVENTOS_CSV):
            return eventos

        eventos_csv = {}
        with open(ARCHIVO_EVENTOS_CSV, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fecha = (row.get("fecha") or "").strip()
                if not fecha or fecha in fechas_existentes:
                    continue
                principal = int(float(row.get("mesa_principal") or 2))
                evento = eventos_csv.setdefault(fecha, Evento(fecha, principal, []))
                try:
                    col = row.get("columna")
                    fila = row.get("fila")
                    personas = row.get("personas")
                    if col and fila and personas:
                        evento.mesas.append(Mesa(
                            int(float(col)),
                            int(float(fila)),
                            int(float(personas)),
                            row.get("nombre_mesa") or None,
                            row.get("color") or "lightgray",
                        ))
                except ValueError:
                    continue
        return eventos + list(eventos_csv.values())

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
        GestorArchivos.exportar_eventos_csv(eventos)

    @staticmethod
    def buscar_evento_por_fecha(fecha):
        """Busca un evento por su fecha."""
        eventos = GestorArchivos.cargar_eventos()
        for evento in eventos:
            if evento.fecha == fecha:
                return evento
        return None

    @staticmethod
    def exportar_eventos_csv(eventos=None):
        eventos = eventos if eventos is not None else GestorArchivos.cargar_eventos()
        GestorArchivos.asegurar_carpeta(ARCHIVO_EVENTOS_CSV)
        with open(ARCHIVO_EVENTOS_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["fecha", "mesa_principal", "total_invitados", "columna", "fila", "personas", "nombre_mesa", "color"])
            for evento in eventos:
                if evento.mesas:
                    for mesa in evento.mesas:
                        writer.writerow([
                            evento.fecha,
                            evento.principal,
                            evento.total_invitados(),
                            mesa.col,
                            mesa.fila,
                            mesa.personas,
                            mesa.nombre or "",
                            mesa.color,
                        ])
                else:
                    writer.writerow([evento.fecha, evento.principal, evento.total_invitados(), "", "", "", "", ""])

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
        GestorArchivos.exportar_organizaciones_csv(orgs)

    @staticmethod
    def buscar_organizacion_por_fecha(fecha):
        """Busca una organización por su fecha."""
        orgs = GestorArchivos.cargar_organizaciones()
        for org in orgs:
            if org.fecha == fecha:
                return org
        return None

    @staticmethod
    def exportar_organizaciones_csv(orgs=None):
        orgs = orgs if orgs is not None else GestorArchivos.cargar_organizaciones()
        GestorArchivos.asegurar_carpeta(ARCHIVO_ORGANIZACIONES_CSV)
        with open(ARCHIVO_ORGANIZACIONES_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["fecha", "color_mesero", "nombre_mesero", "personas_asignadas", "mesa_posicion"])
            for org in orgs:
                if org.colores:
                    for posicion, color in org.colores.items():
                        writer.writerow([org.fecha, color, getattr(org, "nombres_meseros", {}).get(color, ""), org.meseros.get(color, ""), posicion])
                else:
                    for color, personas in org.meseros.items():
                        writer.writerow([org.fecha, color, getattr(org, "nombres_meseros", {}).get(color, ""), personas, ""])

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

    # --- Inventario ---
    @staticmethod
    def cargar_cortes_inventario():
        if not os.path.exists(ARCHIVO_INVENTARIO):
            return []
        with open(ARCHIVO_INVENTARIO, "r", encoding="utf8") as f:
            data_list = json.load(f)
            return [InventarioCorte.from_dict(data) for data in data_list]

    @staticmethod
    def guardar_corte_inventario(corte):
        cortes = GestorArchivos.cargar_cortes_inventario()
        for i, corte_guardado in enumerate(cortes):
            if corte_guardado.fecha == corte.fecha:
                cortes[i] = corte
                break
        else:
            cortes.append(corte)

        with open(ARCHIVO_INVENTARIO, "w", encoding="utf8") as f:
            json.dump([c.to_dict() for c in cortes], f, indent=4, ensure_ascii=False)
        return GestorArchivos.exportar_corte_inventario_csv(corte)

    @staticmethod
    def ultimo_corte_inventario():
        cortes = GestorArchivos.cargar_cortes_inventario()
        if not cortes:
            return None
        return sorted(cortes, key=lambda c: c.fecha)[-1]

    @staticmethod
    def exportar_corte_inventario_csv(corte):
        nombre_fecha = corte.fecha.replace(":", "-").replace(" ", "_")
        ruta = os.path.join(CARPETA_INVENTARIOS, f"inventario_{nombre_fecha}.csv")
        GestorArchivos.asegurar_carpeta(ruta)
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["articulo", "categoria", "total", "danadas", "disponibles", "costo_unitario", "reposicion", "notas"])
            for item in corte.articulos:
                writer.writerow([
                    item.nombre,
                    item.categoria,
                    item.total,
                    item.danadas,
                    item.disponibles,
                    item.costo_unitario,
                    item.costo_reposicion,
                    item.notas,
                ])
        return ruta

    @staticmethod
    def cargar_comparaciones_inventario():
        if not os.path.exists(ARCHIVO_COMPARACIONES_INVENTARIO):
            return []
        with open(ARCHIVO_COMPARACIONES_INVENTARIO, "r", encoding="utf8") as f:
            return json.load(f)

    @staticmethod
    def guardar_comparacion_inventario(data):
        comparaciones = GestorArchivos.cargar_comparaciones_inventario()
        comparaciones.append(data)
        with open(ARCHIVO_COMPARACIONES_INVENTARIO, "w", encoding="utf8") as f:
            json.dump(comparaciones, f, indent=4, ensure_ascii=False)
        return data

    @staticmethod
    def promedio_reposicion_inventario():
        comparaciones = GestorArchivos.cargar_comparaciones_inventario()
        costos = [float(c.get("costo_reposicion_total", 0) or 0) for c in comparaciones]
        if not costos:
            return 0
        return sum(costos) / len(costos)

    @staticmethod
    def resumen_reposicion_inventario():
        comparaciones = GestorArchivos.cargar_comparaciones_inventario()
        costos = [float(c.get("costo_reposicion_total", 0) or 0) for c in comparaciones]
        total_comparaciones = len(costos)
        promedio = (sum(costos) / total_comparaciones) if total_comparaciones else 0
        return {
            "total_comparaciones": total_comparaciones,
            "promedio": promedio,
            "ultimo_total": costos[-1] if costos else 0,
        }
