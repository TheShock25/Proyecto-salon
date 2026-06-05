import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

class FrameComentariosMesero(FrameBase):
    """Frame para que los meseros agreguen comentarios."""
    def configurar(self):
        self.master.origen_actual = "comentarios"
        
        tk.Label(self, text="Comentarios del evento", font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        # Cargar eventos pasados y de hoy
        eventos = GestorArchivos.cargar_eventos()
        hoy = datetime.date.today()
        self.eventos_comentables = []
        
        for e in eventos:
            try:
                fecha_str = e.fecha
                if not fecha_str:
                    continue
                
                fecha_dt = None
                for formato in ["%m/%d/%yy", "%m/%d/%y"]:
                    try:
                        fecha_dt = datetime.datetime.strptime(fecha_str, formato).date()
                        break
                    except ValueError:
                        continue
                
                if fecha_dt and fecha_dt <= hoy:
                    self.eventos_comentables.append((fecha_dt, e))
            except:
                continue
        
        self.eventos_comentables.sort(key=lambda x: x[0], reverse=True)
        
        if not self.eventos_comentables:
            tk.Label(self, text="No hay eventos pasados o del día de hoy para comentar.",
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuMesero),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Variable para el evento seleccionado
        self.evento_seleccionado = tk.StringVar()
        
        # Frame para selección con scroll
        self.crear_selector_eventos()
        
        # Frame para el formulario
        self.frame_formulario = tk.Frame(self, bg=BG, relief="groove", bd=2)
        self.crear_formulario()
        
        # Botón volver
        tk.Button(self, text="Volver al menú", command=lambda: self.volver(FrameMenuMesero),
                 bg="#777", fg="white", width=20, height=2).pack(pady=10)

    def crear_selector_eventos(self):
        """Crea el selector de eventos con scroll."""
        frame_seleccion = tk.Frame(self, bg=BG)
        frame_seleccion.pack(pady=10, fill="x", padx=20)
        
        tk.Label(frame_seleccion, text="Selecciona el evento:", 
                font=("Arial", 11, "bold"), bg=BG).pack(anchor="w")
        
        # Frame con scroll
        frame_scroll = tk.Frame(self, bg=BG)
        frame_scroll.pack(pady=5, fill="both", expand=True, padx=20)
        
        canvas_scroll = tk.Canvas(frame_scroll, height=150, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas_scroll.yview)
        self.scrollable_frame = tk.Frame(canvas_scroll, bg=BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar eventos
        for fecha_dt, evento in self.eventos_comentables:
            fecha_str = fecha_dt.strftime("%d/%m/%Y")
            total_personas = evento.total_invitados()
            estado = "HOY" if fecha_dt == datetime.date.today() else "PASADO"
            
            frame_opcion = tk.Frame(self.scrollable_frame, bg=BG)
            frame_opcion.pack(fill="x", pady=2)
            
            rb = tk.Radiobutton(frame_opcion, 
                               text=f"{fecha_str} - {estado} - {total_personas} invitados",
                               variable=self.evento_seleccionado, 
                               value=evento.fecha,
                               font=("Arial", 10), bg=BG,
                               command=self.habilitar_formulario)
            rb.pack(side="left")
            
            btn_ver = tk.Button(frame_opcion, text="Ver croquis",
                               command=lambda ev=evento: self.ver_croquis(ev),
                               bg=BTN2, fg="white", font=("Arial", 8))
            btn_ver.pack(side="right", padx=5)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def crear_formulario(self):
        """Crea el formulario de comentarios."""
        tk.Label(self.frame_formulario, text="Formulario de comentarios", 
                font=("Arial", 12, "bold"), bg=BG).pack(pady=5)
        
        frame_campos = tk.Frame(self.frame_formulario, bg=BG)
        frame_campos.pack(pady=10, padx=20)
        
        # Campos
        labels = ["¿Cuánto ganaste? ($):", "¿Cómo sentiste el evento?:", 
                 "Observaciones:", "¿Hubo desperfectos o quejas?:"]
        
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame_campos, text=label, font=("Arial", 10), bg=BG).grid(row=i, column=0, sticky="w", pady=5)
            entry = tk.Entry(frame_campos, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[f"field_{i}"] = entry
        
        # Calificación
        tk.Label(frame_campos, text="Calificación (1-5):", font=("Arial", 10), bg=BG).grid(row=4, column=0, sticky="w", pady=5)
        self.calificacion_var = tk.StringVar(value="5")
        calificacion_combo = tk.Spinbox(frame_campos, from_=1, to=5, textvariable=self.calificacion_var, width=5)
        calificacion_combo.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # Etiqueta de edición
        self.lbl_editando = tk.Label(self.frame_formulario, text="", font=("Arial", 9, "italic"), 
                                    fg=BTN2, bg=BG)
        self.lbl_editando.pack(pady=2)
        
        # Botones del formulario
        frame_botones = tk.Frame(self.frame_formulario, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Guardar comentario", 
                 command=self.guardar, bg=BTN, fg="white", 
                 width=20, height=2, font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        tk.Button(frame_botones, text="Ver comentarios guardados", 
                 command=self.mostrar_comentarios_guardados, bg=BTN2, fg="white", 
                 width=25).pack(side="left", padx=10)

    def habilitar_formulario(self):
        """Habilita el formulario cuando se selecciona un evento."""
        self.frame_formulario.pack(pady=20, fill="x", padx=20)
        fecha = self.evento_seleccionado.get()
        if fecha:
            self.cargar_comentarios_existentes()

    def cargar_comentarios_existentes(self):
        """Carga comentarios existentes para el evento seleccionado."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            return
        
        comentarios = GestorArchivos.cargar_comentarios()
        encontrado = False
        
        for c in comentarios:
            if c.get("fecha") == fecha:
                self.entries["field_0"].delete(0, tk.END)
                self.entries["field_0"].insert(0, c.get("ganancia", ""))
                
                self.entries["field_1"].delete(0, tk.END)
                self.entries["field_1"].insert(0, c.get("sentir", ""))
                
                self.entries["field_2"].delete(0, tk.END)
                self.entries["field_2"].insert(0, c.get("observaciones", ""))
                
                self.entries["field_3"].delete(0, tk.END)
                self.entries["field_3"].insert(0, c.get("reporte", ""))
                
                self.calificacion_var.set(c.get("calificacion", "5"))
                
                self.lbl_editando.config(text="✎ Editando comentario existente")
                encontrado = True
                break
        
        if not encontrado:
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.calificacion_var.set("5")
            self.lbl_editando.config(text="+ Nuevo comentario")

    def guardar(self):
        """Guarda el comentario."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            messagebox.showwarning("Error", "Por favor, selecciona un evento")
            return
        
        if not self.entries["field_0"].get().strip():
            messagebox.showwarning("Error", "Por favor, ingresa cuánto ganaste")
            return
        
        if not self.entries["field_1"].get().strip():
            messagebox.showwarning("Error", "Por favor, describe cómo sentiste el evento")
            return
        
        data = {
            "fecha": fecha,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ganancia": self.entries["field_0"].get(),
            "sentir": self.entries["field_1"].get(),
            "observaciones": self.entries["field_2"].get(),
            "reporte": self.entries["field_3"].get(),
            "calificacion": self.calificacion_var.get()
        }
        
        GestorArchivos.guardar_comentario(data)
        
        messagebox.showinfo("Gracias", f"Comentario guardado para el evento del {fecha}")
        
        respuesta = messagebox.askyesno("Continuar", "¿Quieres agregar otro comentario?")
        if respuesta:
            self.evento_seleccionado.set("")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.calificacion_var.set("5")
            self.lbl_editando.config(text="")
            self.frame_formulario.pack_forget()
        else:
            self.volver(FrameMenuMesero)

    def mostrar_comentarios_guardados(self):
        """Muestra los comentarios guardados para el evento seleccionado."""
        fecha = self.evento_seleccionado.get()
        if not fecha:
            messagebox.showinfo("Info", "Selecciona un evento para ver sus comentarios")
            return
        
        comentarios = GestorArchivos.cargar_comentarios()
        comentarios_evento = [c for c in comentarios if c.get("fecha") == fecha]
        
        if not comentarios_evento:
            messagebox.showinfo("Info", "No hay comentarios guardados para este evento")
            return
        
        ventana_comentarios = tk.Toplevel(self)
        ventana_comentarios.title(f"Comentarios - {fecha}")
        ventana_comentarios.geometry("500x400")
        ventana_comentarios.configure(bg=BG)
        
        frame_ver = tk.Frame(ventana_comentarios, bg=BG)
        frame_ver.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame_ver, text=f"Comentarios del evento {fecha}", 
                font=("Arial", 14, "bold"), bg=BG).pack(pady=10)
        
        for c in comentarios_evento:
            frame_com = tk.Frame(frame_ver, bg=BG, relief="groove", bd=1)
            frame_com.pack(fill="x", pady=5)
            
            tk.Label(frame_com, text=f"Ganancia: ${c.get('ganancia', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Cómo sintió: {c.get('sentir', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Observaciones: {c.get('observaciones', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Reporte: {c.get('reporte', 'N/A')}", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Calificación: {c.get('calificacion', 'N/A')}/5", 
                    font=("Arial", 10), bg=BG).pack(anchor="w", padx=5)
            tk.Label(frame_com, text=f"Registrado: {c.get('timestamp', 'N/A')}", 
                    font=("Arial", 8, "italic"), fg="gray", bg=BG).pack(anchor="e", padx=5)
        
        tk.Button(frame_ver, text="Cerrar", command=ventana_comentarios.destroy,
                 bg="#777", fg="white", width=15).pack(pady=10)

    def ver_croquis(self, evento):
        """Muestra el croquis del evento."""
        self.master.origen_actual = "comentarios"
        self.master.cambiar_frame(FrameCroquis, modo="visualizacion", evento=evento)

class FrameEstadisticas(FrameBase):
    """Frame para mostrar estadísticas."""
    def configurar(self):
        tk.Label(self, text="Estadísticas de desempeño", font=("Arial", 16, "bold"), bg=BG).pack(pady=20)
        
        # Aquí iría la lógica de estadísticas
        tk.Label(self, text="Próximamente: Estadísticas detalladas", 
                font=("Arial", 12), bg=BG).pack(pady=10)
        
        # Botón para exportar comentarios
        tk.Button(self, text="Exportar comentarios a Excel", 
                 command=self.exportar_comentarios, bg=BTN, fg="white",
                 width=25, height=2).pack(pady=10)
        
        tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuMesero),
                 bg="#777", fg="white", width=20, height=2).pack(pady=20)

    def exportar_comentarios(self):
        """Exporta los comentarios a CSV."""
        archivos = GestorArchivos.exportar_comentarios_a_excel()
        if archivos:
            mensaje = "Archivos generados:\n" + "\n".join(archivos)
            messagebox.showinfo("Exportación exitosa", mensaje)
        else:
            messagebox.showinfo("Sin datos", "No hay comentarios para exportar")
