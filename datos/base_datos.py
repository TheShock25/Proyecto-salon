import json
import os
import sqlite3
from datetime import datetime

from constantes import (
    ARCHIVO_BD,
    ARCHIVO_COMENTARIOS,
    ARCHIVO_COMENTARIOS_EVENTO,
    ARCHIVO_COMENTARIOS_MESERO,
    ARCHIVO_COMPARACIONES_INVENTARIO,
    ARCHIVO_EVENTOS,
    ARCHIVO_INVENTARIO,
    ARCHIVO_ORG,
)
from entidades.modelos import (
    ComentarioEvento,
    ComentarioMesero,
    Evento,
    InventarioCorte,
    InventarioItem,
    Mesa,
    OfertaTrabajo,
    Organizacion,
    PerfilMesero,
    Postulacion,
    ResultadoAnalizador,
    Salon,
    Mesero,
)


class BaseDatos:
    """Persistencia SQLite local para el sistema Salon."""

    _inicializada = False

    @staticmethod
    def conectar():
        BaseDatos.inicializar()
        conn = sqlite3.connect(ARCHIVO_BD)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def inicializar():
        if BaseDatos._inicializada:
            return
        conn = sqlite3.connect(ARCHIVO_BD)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        BaseDatos.crear_tablas(conn)
        BaseDatos.migrar_json_inicial(conn)
        conn.close()
        BaseDatos._inicializada = True

    @staticmethod
    def crear_tablas(conn):
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS salones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                direccion TEXT DEFAULT '',
                telefono TEXT DEFAULT '',
                correo TEXT DEFAULT '',
                zona TEXT DEFAULT '',
                logo TEXT DEFAULT '',
                precio_base REAL DEFAULT 0,
                precio_por_persona REAL DEFAULT 0,
                extra_json TEXT DEFAULT '{}',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS eventos (
                fecha TEXT PRIMARY KEY,
                salon_id INTEGER DEFAULT 1,
                principal INTEGER DEFAULT 2,
                servicios_json TEXT DEFAULT '{}',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (salon_id) REFERENCES salones(id)
            );

            CREATE TABLE IF NOT EXISTS evento_mesas (
                fecha TEXT NOT NULL,
                col INTEGER NOT NULL,
                fila INTEGER NOT NULL,
                personas INTEGER DEFAULT 0,
                nombre TEXT,
                color TEXT DEFAULT 'lightgray',
                adultos INTEGER,
                ninos INTEGER DEFAULT 0,
                PRIMARY KEY (fecha, col, fila),
                FOREIGN KEY (fecha) REFERENCES eventos(fecha) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS organizaciones (
                fecha TEXT PRIMARY KEY,
                meseros_json TEXT DEFAULT '{}',
                colores_json TEXT DEFAULT '{}',
                nombres_meseros_json TEXT DEFAULT '{}',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fecha) REFERENCES eventos(fecha) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS inventario_cortes (
                fecha TEXT PRIMARY KEY,
                notas TEXT DEFAULT '',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS inventario_items (
                corte_fecha TEXT NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT DEFAULT '',
                total INTEGER DEFAULT 0,
                danadas INTEGER DEFAULT 0,
                costo_unitario REAL DEFAULT 0,
                notas TEXT DEFAULT '',
                PRIMARY KEY (corte_fecha, nombre, categoria),
                FOREIGN KEY (corte_fecha) REFERENCES inventario_cortes(fecha) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS inventario_comparaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT DEFAULT '',
                costo_reposicion_total REAL DEFAULT 0,
                data_json TEXT NOT NULL,
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                usuario TEXT DEFAULT '',
                rol TEXT DEFAULT '',
                timestamp TEXT DEFAULT '',
                ganancia TEXT DEFAULT '',
                sentir TEXT DEFAULT '',
                observaciones TEXT DEFAULT '',
                reporte TEXT DEFAULT '',
                calificacion TEXT DEFAULT '5',
                ganancia_total TEXT DEFAULT '',
                satisfaccion_general TEXT DEFAULT '',
                num_meseros INTEGER DEFAULT 0,
                calificacion_promedio TEXT DEFAULT '',
                data_json TEXT DEFAULT '{}',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_comentario_general
            ON comentarios(tipo, fecha)
            WHERE tipo IN ('general', 'evento');

            CREATE UNIQUE INDEX IF NOT EXISTS idx_comentario_mesero
            ON comentarios(tipo, fecha, usuario)
            WHERE tipo = 'mesero';

            CREATE TABLE IF NOT EXISTS meseros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT DEFAULT '',
                correo TEXT DEFAULT '',
                zona TEXT DEFAULT '',
                experiencia TEXT DEFAULT '',
                habilidades_json TEXT DEFAULT '[]',
                estado TEXT DEFAULT 'activo',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS perfiles_mesero (
                mesero_id INTEGER PRIMARY KEY,
                entrevista_json TEXT DEFAULT '{}',
                habilidades_json TEXT DEFAULT '[]',
                resumen TEXT DEFAULT '',
                reputacion_json TEXT DEFAULT '{}',
                actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mesero_id) REFERENCES meseros(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ofertas_trabajo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                salon_id INTEGER DEFAULT 1,
                fecha_evento TEXT NOT NULL,
                titulo TEXT DEFAULT '',
                descripcion TEXT DEFAULT '',
                zona TEXT DEFAULT '',
                pago_ofrecido REAL DEFAULT 0,
                propina_esperada REAL DEFAULT 0,
                meseros_requeridos INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'activa',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (salon_id) REFERENCES salones(id)
            );

            CREATE TABLE IF NOT EXISTS postulaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oferta_id INTEGER NOT NULL,
                mesero_id INTEGER NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                mensaje TEXT DEFAULT '',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (oferta_id, mesero_id),
                FOREIGN KEY (oferta_id) REFERENCES ofertas_trabajo(id) ON DELETE CASCADE,
                FOREIGN KEY (mesero_id) REFERENCES meseros(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS resultados_analizador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entidad_tipo TEXT NOT NULL,
                entidad_id TEXT NOT NULL,
                fecha TEXT DEFAULT '',
                origen TEXT DEFAULT '',
                resumen TEXT DEFAULT '',
                sentimiento TEXT DEFAULT '',
                score REAL DEFAULT 0,
                tendencias_json TEXT DEFAULT '{}',
                data_json TEXT DEFAULT '{}',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        BaseDatos.migrar_esquema(conn)

    @staticmethod
    def asegurar_columna(conn, tabla, columna, definicion):
        columnas = {row["name"] for row in conn.execute(f"PRAGMA table_info({tabla})").fetchall()}
        if columna not in columnas:
            conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")

    @staticmethod
    def migrar_esquema(conn):
        BaseDatos.asegurar_columna(conn, "evento_mesas", "adultos", "INTEGER")
        BaseDatos.asegurar_columna(conn, "evento_mesas", "ninos", "INTEGER DEFAULT 0")
        conn.execute(
            """
            INSERT INTO salones (id, nombre)
            SELECT 1, 'Sistema Salon'
            WHERE NOT EXISTS (SELECT 1 FROM salones WHERE id = 1)
            """
        )
        conn.commit()

    @staticmethod
    def json_dumps(data):
        return json.dumps(data if data is not None else {}, ensure_ascii=False)

    @staticmethod
    def json_loads(texto, defecto):
        if not texto:
            return defecto
        try:
            return json.loads(texto)
        except (TypeError, ValueError):
            return defecto

    @staticmethod
    def leer_json(ruta, defecto):
        if not os.path.exists(ruta):
            return defecto
        try:
            with open(ruta, "r", encoding="utf8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return defecto

    @staticmethod
    def metadata(conn, clave):
        row = conn.execute("SELECT valor FROM metadata WHERE clave = ?", (clave,)).fetchone()
        return row["valor"] if row else None

    @staticmethod
    def set_metadata(conn, clave, valor):
        conn.execute(
            "INSERT OR REPLACE INTO metadata (clave, valor) VALUES (?, ?)",
            (clave, valor),
        )

    @staticmethod
    def migrar_json_inicial(conn):
        if BaseDatos.metadata(conn, "json_migrado") == "1":
            return

        for data in BaseDatos.leer_json(ARCHIVO_EVENTOS, []):
            BaseDatos.guardar_evento_conn(conn, Evento.from_dict(data))

        for data in BaseDatos.leer_json(ARCHIVO_ORG, []):
            BaseDatos.guardar_organizacion_conn(conn, Organizacion.from_dict(data))

        for data in BaseDatos.leer_json(ARCHIVO_COMENTARIOS, []):
            BaseDatos.guardar_comentario_general_conn(conn, data)

        for data in BaseDatos.leer_json(ARCHIVO_COMENTARIOS_MESERO, []):
            BaseDatos.guardar_comentario_mesero_conn(conn, ComentarioMesero.from_dict(data))

        for data in BaseDatos.leer_json(ARCHIVO_COMENTARIOS_EVENTO, []):
            BaseDatos.guardar_comentario_evento_conn(conn, ComentarioEvento.from_dict(data))

        for data in BaseDatos.leer_json(ARCHIVO_INVENTARIO, []):
            BaseDatos.guardar_corte_inventario_conn(conn, InventarioCorte.from_dict(data))

        for data in BaseDatos.leer_json(ARCHIVO_COMPARACIONES_INVENTARIO, []):
            BaseDatos.guardar_comparacion_inventario_conn(conn, data)

        BaseDatos.set_metadata(conn, "json_migrado", "1")
        conn.commit()

    # --- Eventos ---
    @staticmethod
    def guardar_evento_conn(conn, evento):
        conn.execute(
            """
            INSERT OR REPLACE INTO eventos (fecha, salon_id, principal, servicios_json)
            VALUES (?, 1, ?, ?)
            """,
            (evento.fecha, evento.principal, BaseDatos.json_dumps(getattr(evento, "servicios", {}))),
        )
        conn.execute("DELETE FROM evento_mesas WHERE fecha = ?", (evento.fecha,))
        for mesa in evento.mesas:
            conn.execute(
                """
                INSERT INTO evento_mesas (fecha, col, fila, personas, nombre, color, adultos, ninos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (evento.fecha, mesa.col, mesa.fila, mesa.personas, mesa.nombre, mesa.color, mesa.adultos, mesa.ninos),
            )

    @staticmethod
    def guardar_evento(evento):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_evento_conn(conn, evento)

    @staticmethod
    def cargar_eventos():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM eventos ORDER BY creado_en, fecha").fetchall()
            return [BaseDatos.evento_desde_row(conn, row) for row in rows]

    @staticmethod
    def evento_desde_row(conn, row):
        mesas_rows = conn.execute(
            "SELECT * FROM evento_mesas WHERE fecha = ? ORDER BY fila, col",
            (row["fecha"],),
        ).fetchall()
        mesas = [
            Mesa(m["col"], m["fila"], m["personas"], m["nombre"], m["color"], m["adultos"], m["ninos"])
            for m in mesas_rows
        ]
        return Evento(
            row["fecha"],
            row["principal"],
            mesas,
            BaseDatos.json_loads(row["servicios_json"], {}),
        )

    @staticmethod
    def buscar_evento_por_fecha(fecha):
        with BaseDatos.conectar() as conn:
            row = conn.execute("SELECT * FROM eventos WHERE fecha = ?", (fecha,)).fetchone()
            return BaseDatos.evento_desde_row(conn, row) if row else None

    @staticmethod
    def eliminar_evento(fecha):
        with BaseDatos.conectar() as conn:
            cur = conn.execute("DELETE FROM eventos WHERE fecha = ?", (fecha,))
            return cur.rowcount > 0

    # --- Organizaciones ---
    @staticmethod
    def guardar_organizacion_conn(conn, organizacion):
        conn.execute(
            """
            INSERT OR REPLACE INTO organizaciones
            (fecha, meseros_json, colores_json, nombres_meseros_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                organizacion.fecha,
                BaseDatos.json_dumps(organizacion.meseros),
                BaseDatos.json_dumps(organizacion.colores),
                BaseDatos.json_dumps(getattr(organizacion, "nombres_meseros", {})),
            ),
        )

    @staticmethod
    def guardar_organizacion(organizacion):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_organizacion_conn(conn, organizacion)

    @staticmethod
    def cargar_organizaciones():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM organizaciones ORDER BY creado_en, fecha").fetchall()
            return [BaseDatos.organizacion_desde_row(row) for row in rows]

    @staticmethod
    def organizacion_desde_row(row):
        return Organizacion(
            row["fecha"],
            BaseDatos.json_loads(row["meseros_json"], {}),
            BaseDatos.json_loads(row["colores_json"], {}),
            BaseDatos.json_loads(row["nombres_meseros_json"], {}),
        )

    @staticmethod
    def buscar_organizacion_por_fecha(fecha):
        with BaseDatos.conectar() as conn:
            row = conn.execute("SELECT * FROM organizaciones WHERE fecha = ?", (fecha,)).fetchone()
            return BaseDatos.organizacion_desde_row(row) if row else None

    @staticmethod
    def eliminar_organizacion(fecha):
        with BaseDatos.conectar() as conn:
            cur = conn.execute("DELETE FROM organizaciones WHERE fecha = ?", (fecha,))
            return cur.rowcount > 0

    # --- Comentarios ---
    @staticmethod
    def comentario_general_desde_row(row):
        data = BaseDatos.json_loads(row["data_json"], {})
        data.update({
            "fecha": row["fecha"],
            "timestamp": row["timestamp"],
            "ganancia": row["ganancia"],
            "sentir": row["sentir"],
            "observaciones": row["observaciones"],
            "reporte": row["reporte"],
            "calificacion": row["calificacion"],
        })
        return data

    @staticmethod
    def cargar_comentarios():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM comentarios WHERE tipo = 'general' ORDER BY creado_en").fetchall()
            return [BaseDatos.comentario_general_desde_row(row) for row in rows]

    @staticmethod
    def guardar_comentario_general_conn(conn, data):
        conn.execute(
            """
            INSERT OR REPLACE INTO comentarios
            (id, tipo, fecha, timestamp, ganancia, sentir, observaciones, reporte, calificacion, data_json)
            VALUES (
                (SELECT id FROM comentarios WHERE tipo = 'general' AND fecha = ?),
                'general', ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                data.get("fecha"),
                data.get("fecha"),
                data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                data.get("ganancia", ""),
                data.get("sentir", ""),
                data.get("observaciones", ""),
                data.get("reporte", ""),
                data.get("calificacion", "5"),
                BaseDatos.json_dumps(data),
            ),
        )

    @staticmethod
    def guardar_comentario(data):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_comentario_general_conn(conn, data)

    @staticmethod
    def cargar_comentarios_mesero():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM comentarios WHERE tipo = 'mesero' ORDER BY creado_en").fetchall()
            return [
                ComentarioMesero.from_dict(BaseDatos.comentario_mesero_dict(row))
                for row in rows
            ]

    @staticmethod
    def comentario_mesero_dict(row):
        data = BaseDatos.comentario_general_desde_row(row)
        data.update({"usuario": row["usuario"], "rol": row["rol"]})
        return data

    @staticmethod
    def guardar_comentario_mesero_conn(conn, comentario):
        data = comentario.to_dict()
        conn.execute(
            """
            INSERT OR REPLACE INTO comentarios
            (id, tipo, fecha, usuario, rol, timestamp, ganancia, sentir, observaciones, reporte, calificacion, data_json)
            VALUES (
                (SELECT id FROM comentarios WHERE tipo = 'mesero' AND fecha = ? AND usuario = ?),
                'mesero', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                comentario.fecha,
                comentario.usuario,
                comentario.fecha,
                comentario.usuario,
                comentario.rol,
                comentario.timestamp,
                comentario.ganancia,
                comentario.sentir,
                comentario.observaciones,
                comentario.reporte,
                comentario.calificacion,
                BaseDatos.json_dumps(data),
            ),
        )

    @staticmethod
    def guardar_comentario_mesero(comentario):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_comentario_mesero_conn(conn, comentario)

    @staticmethod
    def cargar_comentarios_evento():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM comentarios WHERE tipo = 'evento' ORDER BY creado_en").fetchall()
            return [
                ComentarioEvento.from_dict(BaseDatos.comentario_evento_dict(row))
                for row in rows
            ]

    @staticmethod
    def comentario_evento_dict(row):
        data = BaseDatos.comentario_general_desde_row(row)
        data.update({
            "ganancia_total": row["ganancia_total"],
            "satisfaccion_general": row["satisfaccion_general"],
            "num_meseros": row["num_meseros"],
            "calificacion_promedio": row["calificacion_promedio"],
        })
        return data

    @staticmethod
    def guardar_comentario_evento_conn(conn, comentario):
        data = comentario.to_dict()
        conn.execute(
            """
            INSERT OR REPLACE INTO comentarios
            (id, tipo, fecha, timestamp, ganancia, sentir, observaciones, reporte, calificacion,
             ganancia_total, satisfaccion_general, num_meseros, calificacion_promedio, data_json)
            VALUES (
                (SELECT id FROM comentarios WHERE tipo = 'evento' AND fecha = ?),
                'evento', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                comentario.fecha,
                comentario.fecha,
                comentario.timestamp,
                comentario.ganancia,
                comentario.sentir,
                comentario.observaciones,
                comentario.reporte,
                comentario.calificacion,
                comentario.ganancia_total,
                comentario.satisfaccion_general,
                comentario.num_meseros,
                comentario.calificacion_promedio,
                BaseDatos.json_dumps(data),
            ),
        )

    @staticmethod
    def guardar_comentario_evento(comentario):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_comentario_evento_conn(conn, comentario)

    # --- Inventario ---
    @staticmethod
    def guardar_corte_inventario_conn(conn, corte):
        conn.execute(
            "INSERT OR REPLACE INTO inventario_cortes (fecha, notas) VALUES (?, ?)",
            (corte.fecha, corte.notas),
        )
        conn.execute("DELETE FROM inventario_items WHERE corte_fecha = ?", (corte.fecha,))
        for item in corte.articulos:
            conn.execute(
                """
                INSERT INTO inventario_items
                (corte_fecha, nombre, categoria, total, danadas, costo_unitario, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (corte.fecha, item.nombre, item.categoria, item.total, item.danadas, item.costo_unitario, item.notas),
            )

    @staticmethod
    def guardar_corte_inventario(corte):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_corte_inventario_conn(conn, corte)

    @staticmethod
    def cargar_cortes_inventario():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM inventario_cortes ORDER BY fecha").fetchall()
            return [BaseDatos.corte_desde_row(conn, row) for row in rows]

    @staticmethod
    def corte_desde_row(conn, row):
        items_rows = conn.execute(
            "SELECT * FROM inventario_items WHERE corte_fecha = ? ORDER BY nombre, categoria",
            (row["fecha"],),
        ).fetchall()
        articulos = [
            InventarioItem(i["nombre"], i["categoria"], i["total"], i["danadas"], i["costo_unitario"], i["notas"])
            for i in items_rows
        ]
        return InventarioCorte(row["fecha"], articulos, row["notas"])

    @staticmethod
    def guardar_comparacion_inventario_conn(conn, data):
        conn.execute(
            """
            INSERT INTO inventario_comparaciones (fecha, costo_reposicion_total, data_json)
            VALUES (?, ?, ?)
            """,
            (
                data.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                float(data.get("costo_reposicion_total", 0) or 0),
                BaseDatos.json_dumps(data),
            ),
        )

    @staticmethod
    def guardar_comparacion_inventario(data):
        with BaseDatos.conectar() as conn:
            BaseDatos.guardar_comparacion_inventario_conn(conn, data)
        return data

    @staticmethod
    def cargar_comparaciones_inventario():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT data_json FROM inventario_comparaciones ORDER BY id").fetchall()
            return [BaseDatos.json_loads(row["data_json"], {}) for row in rows]

    # --- Salon ---
    @staticmethod
    def guardar_salon(salon, salon_id=1):
        with BaseDatos.conectar() as conn:
            cur = conn.execute(
                """
                UPDATE salones
                SET nombre=?, direccion=?, telefono=?, correo=?, zona=?, logo=?,
                    precio_base=?, precio_por_persona=?, extra_json=?
                WHERE id=?
                """,
                (
                    salon.nombre,
                    salon.direccion,
                    salon.telefono,
                    salon.correo,
                    salon.zona,
                    salon.logo,
                    salon.precio_base,
                    salon.precio_por_persona,
                    BaseDatos.json_dumps(salon.extra),
                    salon_id,
                ),
            )
            if cur.rowcount == 0:
                conn.execute(
                    """
                    INSERT INTO salones
                    (id, nombre, direccion, telefono, correo, zona, logo, precio_base, precio_por_persona, extra_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        salon_id,
                        salon.nombre,
                        salon.direccion,
                        salon.telefono,
                        salon.correo,
                        salon.zona,
                        salon.logo,
                        salon.precio_base,
                        salon.precio_por_persona,
                        BaseDatos.json_dumps(salon.extra),
                    ),
                )

    @staticmethod
    def cargar_salones():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM salones ORDER BY id").fetchall()
            return [
                Salon(
                    r["nombre"], r["direccion"], r["telefono"], r["correo"], r["zona"],
                    r["logo"], r["precio_base"], r["precio_por_persona"],
                    BaseDatos.json_loads(r["extra_json"], {}),
                )
                for r in rows
            ]

    # --- Meseros, ofertas y analizador: base para pantallas futuras ---
    @staticmethod
    def guardar_mesero(mesero):
        with BaseDatos.conectar() as conn:
            if mesero.id:
                conn.execute(
                    """
                    UPDATE meseros
                    SET nombre=?, telefono=?, correo=?, zona=?, experiencia=?, habilidades_json=?, estado=?
                    WHERE id=?
                    """,
                    (mesero.nombre, mesero.telefono, mesero.correo, mesero.zona, mesero.experiencia,
                     BaseDatos.json_dumps(mesero.habilidades), mesero.estado, mesero.id),
                )
                return mesero.id
            cur = conn.execute(
                """
                INSERT INTO meseros (nombre, telefono, correo, zona, experiencia, habilidades_json, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (mesero.nombre, mesero.telefono, mesero.correo, mesero.zona, mesero.experiencia,
                 BaseDatos.json_dumps(mesero.habilidades), mesero.estado),
            )
            return cur.lastrowid

    @staticmethod
    def cargar_meseros():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM meseros ORDER BY nombre").fetchall()
            return [
                Mesero(
                    r["nombre"], r["telefono"], r["correo"], r["zona"], r["experiencia"],
                    BaseDatos.json_loads(r["habilidades_json"], []), r["estado"], r["id"],
                )
                for r in rows
            ]

    @staticmethod
    def guardar_perfil_mesero(perfil):
        with BaseDatos.conectar() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO perfiles_mesero
                (mesero_id, entrevista_json, habilidades_json, resumen, reputacion_json, actualizado_en)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (perfil.mesero_id, BaseDatos.json_dumps(perfil.entrevista),
                 BaseDatos.json_dumps(perfil.habilidades), perfil.resumen,
                 BaseDatos.json_dumps(perfil.reputacion), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

    @staticmethod
    def cargar_perfiles_mesero():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM perfiles_mesero ORDER BY mesero_id").fetchall()
            return [
                PerfilMesero(
                    r["mesero_id"], BaseDatos.json_loads(r["entrevista_json"], {}),
                    BaseDatos.json_loads(r["habilidades_json"], []), r["resumen"],
                    BaseDatos.json_loads(r["reputacion_json"], {}),
                )
                for r in rows
            ]

    @staticmethod
    def guardar_oferta(oferta):
        with BaseDatos.conectar() as conn:
            if oferta.id:
                conn.execute(
                    """
                    UPDATE ofertas_trabajo
                    SET salon_id=?, fecha_evento=?, titulo=?, descripcion=?, zona=?, pago_ofrecido=?,
                        propina_esperada=?, meseros_requeridos=?, estado=?
                    WHERE id=?
                    """,
                    (oferta.salon_id, oferta.fecha_evento, oferta.titulo, oferta.descripcion, oferta.zona,
                     oferta.pago_ofrecido, oferta.propina_esperada, oferta.meseros_requeridos,
                     oferta.estado, oferta.id),
                )
                return oferta.id
            cur = conn.execute(
                """
                INSERT INTO ofertas_trabajo
                (salon_id, fecha_evento, titulo, descripcion, zona, pago_ofrecido, propina_esperada, meseros_requeridos, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (oferta.salon_id, oferta.fecha_evento, oferta.titulo, oferta.descripcion, oferta.zona,
                 oferta.pago_ofrecido, oferta.propina_esperada, oferta.meseros_requeridos, oferta.estado),
            )
            return cur.lastrowid

    @staticmethod
    def cargar_ofertas():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM ofertas_trabajo ORDER BY fecha_evento, id").fetchall()
            return [
                OfertaTrabajo(
                    r["fecha_evento"], r["titulo"], r["descripcion"], r["zona"], r["pago_ofrecido"],
                    r["propina_esperada"], r["meseros_requeridos"], r["salon_id"], r["estado"], r["id"],
                )
                for r in rows
            ]

    @staticmethod
    def guardar_postulacion(postulacion):
        with BaseDatos.conectar() as conn:
            cur = conn.execute(
                """
                INSERT OR REPLACE INTO postulaciones (id, oferta_id, mesero_id, estado, mensaje)
                VALUES (
                    COALESCE(?, (SELECT id FROM postulaciones WHERE oferta_id=? AND mesero_id=?)),
                    ?, ?, ?, ?
                )
                """,
                (postulacion.id, postulacion.oferta_id, postulacion.mesero_id,
                 postulacion.oferta_id, postulacion.mesero_id, postulacion.estado, postulacion.mensaje),
            )
            return postulacion.id or cur.lastrowid

    @staticmethod
    def cargar_postulaciones():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM postulaciones ORDER BY creado_en").fetchall()
            return [
                Postulacion(r["oferta_id"], r["mesero_id"], r["estado"], r["mensaje"], r["id"])
                for r in rows
            ]

    @staticmethod
    def guardar_resultado_analizador(resultado):
        with BaseDatos.conectar() as conn:
            if resultado.id:
                conn.execute(
                    """
                    UPDATE resultados_analizador
                    SET entidad_tipo=?, entidad_id=?, fecha=?, origen=?, resumen=?, sentimiento=?,
                        score=?, tendencias_json=?, data_json=?
                    WHERE id=?
                    """,
                    (resultado.entidad_tipo, resultado.entidad_id, resultado.fecha, resultado.origen,
                     resultado.resumen, resultado.sentimiento, resultado.score,
                     BaseDatos.json_dumps(resultado.tendencias), BaseDatos.json_dumps(resultado.data), resultado.id),
                )
                return resultado.id
            cur = conn.execute(
                """
                INSERT INTO resultados_analizador
                (entidad_tipo, entidad_id, fecha, origen, resumen, sentimiento, score, tendencias_json, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (resultado.entidad_tipo, resultado.entidad_id, resultado.fecha, resultado.origen,
                 resultado.resumen, resultado.sentimiento, resultado.score,
                 BaseDatos.json_dumps(resultado.tendencias), BaseDatos.json_dumps(resultado.data)),
            )
            return cur.lastrowid

    @staticmethod
    def cargar_resultados_analizador():
        with BaseDatos.conectar() as conn:
            rows = conn.execute("SELECT * FROM resultados_analizador ORDER BY creado_en").fetchall()
            return [
                ResultadoAnalizador(
                    r["entidad_tipo"], r["entidad_id"], r["fecha"], r["origen"], r["resumen"],
                    r["sentimiento"], r["score"], BaseDatos.json_loads(r["tendencias_json"], {}),
                    BaseDatos.json_loads(r["data_json"], {}), r["id"],
                )
                for r in rows
            ]
