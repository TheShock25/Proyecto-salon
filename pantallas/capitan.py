import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkcalendar import Calendar

from constantes import *
from datos import GestorArchivos
from entidades import Evento, Mesa, Organizacion
from .base import FrameBase
from .lazy import *

class FrameListaEventos(FrameBase):
    """Frame para listar eventos no organizados."""
    def __init__(self, master, modo="cargar", **kwargs):
        self.modo = modo
        super().__init__(master, **kwargs)

    def configurar(self):
        tk.Label(self, text="Eventos asignados", font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(14, 2))
        tk.Label(self, text="Pendientes por organizar. Abre un evento para asignar mesas por color/mesero.",
                 font=("Arial", 10), bg=BG, fg="#555").pack()
        
        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        
        # Filtrar eventos no organizados
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        if not eventos_no_org:
            tk.Label(self, text="No hay eventos pendientes de organizar", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                     bg="#777", fg="white", activebackground="#777", activeforeground="white",
                     relief="flat", width=20, height=2, cursor="hand2").pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=64, height=15,
                                  yscrollcommand=scrollbar.set,
                                  font=("Arial", 11),
                                  selectbackground=BTN2,
                                  selectforeground="white")
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, evento in enumerate(eventos_no_org):
            total = evento.total_invitados()
            self.listbox.insert(tk.END, f"{i} - PENDIENTE - {evento.fecha} - {total} invitados")
            self.listbox.itemconfig(i, bg="#FEF2F2", fg="#991B1B")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir evento", command=self.abrir_evento,
                 bg=BTN, fg="white", activebackground=BTN, activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                 bg="#777", fg="white", activebackground="#777", activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)

    def abrir_evento(self):
        """Abre el evento seleccionado."""
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Selección", "Por favor, selecciona un evento")
            return
        
        # Obtener el índice real del evento
        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        
        eventos = GestorArchivos.cargar_eventos_con_csv()
        organizaciones = GestorArchivos.cargar_organizaciones()
        fechas_organizadas = {o.fecha for o in organizaciones}
        eventos_no_org = [e for e in eventos if e.fecha not in fechas_organizadas]
        
        evento = eventos_no_org[int(indice_texto)]
        self.master.cambiar_frame(FrameCroquis, modo="capitan", evento=evento)

class FrameListaOrganizaciones(FrameBase):
    """Frame para listar organizaciones guardadas."""
    def __init__(self, master, modo_mesero=False, **kwargs):
        self.modo_mesero = modo_mesero
        super().__init__(master, **kwargs)

    def configurar(self):
        titulo = "Organizaciones disponibles para meseros" if self.modo_mesero else "Organizaciones guardadas"
        tk.Label(self, text=titulo, font=("Arial", 18, "bold"), bg=BG, fg=TXT).pack(pady=(14, 2))
        tk.Label(self, text="Abre una organizacion para revisar o ajustar colores y nombres de meseros.",
                 font=("Arial", 10), bg=BG, fg="#555").pack()
        
        organizaciones = GestorArchivos.cargar_organizaciones()
        
        if not organizaciones:
            tk.Label(self, text="No hay organizaciones guardadas", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
            tk.Button(self, text="Volver", command=lambda: self.volver(btn_volver),
                     bg="#777", fg="white", activebackground="#777", activeforeground="white",
                     relief="flat", width=20, height=2, cursor="hand2").pack(pady=10)
            return
        
        # Listbox
        frame_lista = tk.Frame(self, bg=BG)
        frame_lista.pack(pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(frame_lista, width=64, height=15,
                                  yscrollcommand=scrollbar.set,
                                  font=("Arial", 11),
                                  selectbackground=BTN2,
                                  selectforeground="white")
        self.listbox.pack(side="left")
        
        scrollbar.config(command=self.listbox.yview)
        
        for i, org in enumerate(organizaciones):
            num_meseros = len(org.meseros)
            self.listbox.insert(tk.END, f"{i} - {org.fecha} - {num_meseros} meseros")
            self.listbox.itemconfig(i, bg="#F0FDF4", fg="#166534")
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=20)
        
        tk.Button(frame_botones, text="Abrir organización", command=self.abrir_organizacion,
                 bg=BTN, fg="white", activebackground=BTN, activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)
        
        btn_volver = FrameMenuMesero if self.modo_mesero else FrameMenuCapitan
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(btn_volver),
                 bg="#777", fg="white", activebackground="#777", activeforeground="white",
                 relief="flat", width=20, height=2, cursor="hand2").pack(side="left", padx=10)

    def abrir_organizacion(self):
        """Abre la organización seleccionada."""
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Selección", "Por favor, selecciona una organización")
            return
        
        texto = self.listbox.get(idx[0])
        indice_texto = texto.split(" - ")[0]
        
        organizaciones = GestorArchivos.cargar_organizaciones()
        org = organizaciones[int(indice_texto)]
        
        # Buscar el evento correspondiente
        evento = GestorArchivos.buscar_evento_por_fecha(org.fecha)
        
        if not evento:
            messagebox.showerror("Error", "No se encontró el evento asociado")
            return
        
        modo = "mesero" if self.modo_mesero else "capitan"
        self.master.cambiar_frame(FrameCroquis, modo=modo, evento=evento, organizacion=org)

class FrameCompararEventos(FrameBase):
    """Frame para comparar dos eventos."""
    def configurar(self):
        tk.Label(self, text="Comparar eventos", font=("Arial", 16, "bold"), bg=BG).pack(pady=10)
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        if len(eventos_con_fecha) < 2:
            tk.Label(self, text="Se necesitan al menos 2 eventos para comparar", 
                    font=("Arial", 12), fg="red", bg=BG).pack(pady=30)
            tk.Button(self, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                     bg="#777", fg="white", width=20).pack(pady=10)
            return
        
        # Frame de selección
        frame_sel = tk.Frame(self, bg=BG)
        frame_sel.pack(pady=10)
        
        tk.Label(frame_sel, text="Evento actual", bg=BG, font=("Arial", 11, "bold")).grid(row=0, column=0, padx=20)
        tk.Label(frame_sel, text="Evento siguiente", bg=BG, font=("Arial", 11, "bold")).grid(row=0, column=1, padx=20)
        
        # Listboxes
        self.lb1 = tk.Listbox(frame_sel, width=30, height=10, exportselection=False)
        self.lb2 = tk.Listbox(frame_sel, width=30, height=10, exportselection=False)
        self.lb1.grid(row=1, column=0, padx=10)
        self.lb2.grid(row=1, column=1, padx=10)
        
        for i, e in enumerate(eventos_con_fecha):
            self.lb1.insert(tk.END, f"{i} - {e.fecha}")
        
        # Frame de información
        frame_info = tk.Frame(self, bg=BG)
        frame_info.pack(pady=10)
        
        self.lbl_info1 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info1.pack()
        self.lbl_info2 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info2.pack()
        self.lbl_info3 = tk.Label(frame_info, text="", font=("Arial", 11), bg=BG)
        self.lbl_info3.pack()
        
        # Frame para canvas
        self.frame_canvas = tk.Frame(self, bg=BG)
        self.frame_canvas.pack(pady=10, fill="both", expand=True)
        
        # Bind eventos
        self.lb1.bind("<<ListboxSelect>>", self.on_select_actual)
        
        # Botones
        frame_botones = tk.Frame(self, bg=BG)
        frame_botones.pack(pady=10)
        
        tk.Button(frame_botones, text="Comparar", command=self.comparar,
                 bg=BTN, fg="white", width=15).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Volver", command=lambda: self.volver(FrameMenuCapitan),
                 bg="#777", fg="white", width=15).pack(side="left", padx=10)

    def on_select_actual(self, event):
        """Maneja la selección del evento actual."""
        self.lb2.delete(0, tk.END)
        sel = self.lb1.curselection()
        if not sel:
            return
        
        idx = sel[0]
        texto = self.lb1.get(idx)
        indice = int(texto.split(" - ")[0])
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        try:
            fecha_actual = datetime.datetime.strptime(eventos_con_fecha[indice].fecha, "%m/%d/%y")
            
            for i, e in enumerate(eventos_con_fecha):
                fecha_e = datetime.datetime.strptime(e.fecha, "%m/%d/%y")
                if fecha_e > fecha_actual:
                    self.lb2.insert(tk.END, f"{i} - {e.fecha}")
        except:
            pass

    def comparar(self):
        """Compara los dos eventos seleccionados."""
        sel1 = self.lb1.curselection()
        sel2 = self.lb2.curselection()
        
        if not sel1 or not sel2:
            messagebox.showwarning("Error", "Selecciona dos eventos")
            return
        
        texto1 = self.lb1.get(sel1[0])
        texto2 = self.lb2.get(sel2[0])
        i1 = int(texto1.split(" - ")[0])
        i2 = int(texto2.split(" - ")[0])
        
        eventos = GestorArchivos.cargar_eventos()
        eventos_con_fecha = [e for e in eventos if e.fecha]
        
        ev1 = eventos_con_fecha[i1]
        ev2 = eventos_con_fecha[i2]
        
        # Limpiar canvas
        for widget in self.frame_canvas.winfo_children():
            widget.destroy()
        
        # Dibujar croquis
        self.dibujar_croquis_comparacion(ev1, ev2)
        
        # Calcular diferencias
        total1 = ev1.total_invitados()
        total2 = ev2.total_invitados()
        diff = total2 - total1
        
        org = GestorArchivos.buscar_organizacion_por_fecha(ev1.fecha)
        total_meseros = len(org.meseros) if org else 0
        
        if diff > 0:
            self.lbl_info1.config(text=f"Sillas que FALTAN: {diff}")
        else:
            self.lbl_info1.config(text=f"Sillas que SOBRAN: {abs(diff)}")
        
        self.lbl_info2.config(text=f"Meseros del evento actual: {total_meseros}")
        
        if diff < 0 and total_meseros > 0:
            sillas_por_mesero = abs(diff) // total_meseros
            self.lbl_info3.config(text=f"Sillas por mesero: {sillas_por_mesero}")
        else:
            self.lbl_info3.config(text="")

    def dibujar_croquis_comparacion(self, ev1, ev2):
        """Dibuja dos croquis para comparar."""
        def dibujar_uno(frame, evento, titulo):
            canvas = tk.Canvas(frame, width=COLUMNAS*CELL//2, height=(FILAS+1)*CELL//2, bg="white")
            canvas.pack(side="left", padx=10)
            
            scale = 0.5
            
            def sx(x): return int(x*scale)
            def sy(y): return int(y*scale)
            
            # Título
            canvas.create_text(150, sy(15), text=titulo, font=("Arial", 10, "bold"))
            
            # Mesa principal
            canvas.create_rectangle(sx(2*CELL), sy(20), sx(4*CELL), sy(20+CELL*0.7), fill="brown")
            canvas.create_text(sx(3*CELL), sy(20+0.35*CELL),
                              text=f"P:{evento.principal}", fill="white")
            
            # Pista
            canvas.create_rectangle(sx(2*CELL), sy(1*CELL+20), sx(4*CELL), sy(4*CELL+20), fill="black")
            canvas.create_text(sx(3*CELL), sy(2.5*CELL+20), text="PISTA", fill="white")
            
            # Mesas
            for mesa in evento.mesas:
                x1 = sx((mesa.col-1)*CELL)
                y1 = sy(mesa.fila*CELL+20)
                x2 = sx((mesa.col)*CELL)
                y2 = sy((mesa.fila+1)*CELL+20)
                
                canvas.create_oval(x1+sx(5), y1+sy(5), x2-sx(5), y2-sy(5), fill="lightgray")
                canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(mesa.personas))
        
        frame_comp = tk.Frame(self.frame_canvas, bg=BG)
        frame_comp.pack()
        
        dibujar_uno(frame_comp, ev1, "Evento Actual")
        dibujar_uno(frame_comp, ev2, "Evento Siguiente")
