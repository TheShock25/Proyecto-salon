# gestores.py
import json
import os
import csv
import unicodedata
from datetime import datetime
from datos.base_datos import BaseDatos
from entidades.modelos import Evento, Mesa, Organizacion, Comentario, ComentarioMesero, ComentarioEvento, InventarioCorte
from constantes import *

class GestorArchivos:
    """Clase con métodos estáticos para manejar la persistencia de datos."""

    @staticmethod
    def texto_a_bool(valor):
        if isinstance(valor, bool):
            return valor
        texto = unicodedata.normalize("NFKD", str(valor or ""))
        texto = texto.encode("ascii", "ignore").decode("ascii").strip().lower()
        return texto in {"1", "si", "s", "true", "x", "yes", "y"}

    @staticmethod
    def asegurar_carpeta(ruta_archivo):
        carpeta = os.path.dirname(ruta_archivo)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

    # --- Eventos ---
    @staticmethod
    def cargar_eventos():
        return BaseDatos.cargar_eventos()

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
                servicios = {
                    "pantalla": GestorArchivos.texto_a_bool(row.get("pantalla")),
                    "mesa_pastel": GestorArchivos.texto_a_bool(row.get("mesa_pastel")),
                    "dulces": GestorArchivos.texto_a_bool(row.get("dulces")),
                    "cocina": GestorArchivos.texto_a_bool(row.get("cocina")),
                    "barra": GestorArchivos.texto_a_bool(row.get("barra")),
                    "area_fotos": True if row.get("area_fotos") is None else GestorArchivos.texto_a_bool(row.get("area_fotos")),
                    "animador": GestorArchivos.texto_a_bool(row.get("animador")),
                    "menu_infantil": GestorArchivos.texto_a_bool(row.get("menu_infantil")),
                }
                evento = eventos_csv.setdefault(fecha, Evento(fecha, principal, [], servicios))
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
                            int(float(row.get("adultos") or personas)),
                            int(float(row.get("ninos") or 0)),
                        ))
                except ValueError:
                    continue
        return eventos + list(eventos_csv.values())

    @staticmethod
    def guardar_evento(evento):
        BaseDatos.guardar_evento(evento)
        GestorArchivos.exportar_eventos_csv()

    @staticmethod
    def buscar_evento_por_fecha(fecha):
        """Busca un evento por su fecha."""
        return BaseDatos.buscar_evento_por_fecha(fecha)

    @staticmethod
    def eliminar_evento(fecha):
        eliminado = BaseDatos.eliminar_evento(fecha)
        if eliminado:
            GestorArchivos.exportar_eventos_csv()
            GestorArchivos.exportar_organizaciones_csv()
        return eliminado

    @staticmethod
    def exportar_eventos_csv(eventos=None):
        eventos = eventos if eventos is not None else GestorArchivos.cargar_eventos()
        GestorArchivos.asegurar_carpeta(ARCHIVO_EVENTOS_CSV)
        with open(ARCHIVO_EVENTOS_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "fecha",
                "mesa_principal",
                "total_invitados",
                "columna",
                "fila",
                "personas",
                "adultos",
                "ninos",
                "nombre_mesa",
                "color",
                "pantalla",
                "mesa_pastel",
                "dulces",
                "cocina",
                "barra",
                "area_fotos",
                "animador",
                "menu_infantil",
            ])
            for evento in eventos:
                servicios = getattr(evento, "servicios", {})
                servicios_fila = [
                    "si" if servicios.get("pantalla") else "no",
                    "si" if servicios.get("mesa_pastel") else "no",
                    "si" if servicios.get("dulces") else "no",
                    "si" if servicios.get("cocina") else "no",
                    "si" if servicios.get("barra") else "no",
                    "si" if servicios.get("area_fotos", True) else "no",
                    "si" if servicios.get("animador") else "no",
                    "si" if servicios.get("menu_infantil") else "no",
                ]
                if evento.mesas:
                    for mesa in evento.mesas:
                        writer.writerow([
                            evento.fecha,
                            evento.principal,
                            evento.total_invitados(),
                            mesa.col,
                            mesa.fila,
                            mesa.personas,
                            mesa.adultos,
                            mesa.ninos,
                            mesa.nombre or "",
                            mesa.color,
                            *servicios_fila,
                        ])
                else:
                    writer.writerow([evento.fecha, evento.principal, evento.total_invitados(), "", "", "", "", "", "", "", *servicios_fila])

    # --- Organización ---
    @staticmethod
    def cargar_organizaciones():
        return BaseDatos.cargar_organizaciones()

    @staticmethod
    def guardar_organizacion(organizacion):
        BaseDatos.guardar_organizacion(organizacion)
        GestorArchivos.exportar_organizaciones_csv()

    @staticmethod
    def buscar_organizacion_por_fecha(fecha):
        """Busca una organización por su fecha."""
        return BaseDatos.buscar_organizacion_por_fecha(fecha)

    @staticmethod
    def eliminar_organizacion(fecha):
        eliminado = BaseDatos.eliminar_organizacion(fecha)
        if eliminado:
            GestorArchivos.exportar_organizaciones_csv()
        return eliminado

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
        return BaseDatos.cargar_comentarios()

    @staticmethod
    def guardar_comentario(data):
        BaseDatos.guardar_comentario(data)

    # --- Comentarios Mesero ---
    @staticmethod
    def cargar_comentarios_mesero():
        return BaseDatos.cargar_comentarios_mesero()

    @staticmethod
    def guardar_comentario_mesero(comentario):
        BaseDatos.guardar_comentario_mesero(comentario)

    # --- Comentarios Evento (Generales) ---
    @staticmethod
    def cargar_comentarios_evento():
        return BaseDatos.cargar_comentarios_evento()

    @staticmethod
    def guardar_comentario_evento(comentario):
        BaseDatos.guardar_comentario_evento(comentario)

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
        return BaseDatos.cargar_cortes_inventario()

    @staticmethod
    def guardar_corte_inventario(corte):
        BaseDatos.guardar_corte_inventario(corte)
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
        return BaseDatos.cargar_comparaciones_inventario()

    @staticmethod
    def guardar_comparacion_inventario(data):
        return BaseDatos.guardar_comparacion_inventario(data)

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

    # --- Salon, meseros, ofertas y analizador ---
    @staticmethod
    def cargar_salones():
        return BaseDatos.cargar_salones()

    @staticmethod
    def guardar_salon(salon, salon_id=1):
        return BaseDatos.guardar_salon(salon, salon_id)

    @staticmethod
    def cargar_meseros():
        return BaseDatos.cargar_meseros()

    @staticmethod
    def guardar_mesero(mesero):
        return BaseDatos.guardar_mesero(mesero)

    @staticmethod
    def cargar_perfiles_mesero():
        return BaseDatos.cargar_perfiles_mesero()

    @staticmethod
    def guardar_perfil_mesero(perfil):
        return BaseDatos.guardar_perfil_mesero(perfil)

    @staticmethod
    def cargar_ofertas():
        return BaseDatos.cargar_ofertas()

    @staticmethod
    def guardar_oferta(oferta):
        return BaseDatos.guardar_oferta(oferta)

    @staticmethod
    def cargar_postulaciones():
        return BaseDatos.cargar_postulaciones()

    @staticmethod
    def guardar_postulacion(postulacion):
        return BaseDatos.guardar_postulacion(postulacion)

    @staticmethod
    def cargar_resultados_analizador():
        return BaseDatos.cargar_resultados_analizador()

    @staticmethod
    def guardar_resultado_analizador(resultado):
        return BaseDatos.guardar_resultado_analizador(resultado)
