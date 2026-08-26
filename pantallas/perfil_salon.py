import tkinter as tk
from tkinter import filedialog, messagebox

from constantes import *
from datos import GestorArchivos
from entidades import Salon
from .base import FrameBase
from .lazy import FrameMenuAdmin


class FramePerfilSalon(FrameBase):
    def configurar(self):
        salones = GestorArchivos.cargar_salones()
        self.salon = salones[0] if salones else Salon()

        contenedor = tk.Frame(self, bg=BG)
        contenedor.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(contenedor, text="Perfil del salon", font=("Arial", 20, "bold"), bg=BG, fg=TXT).pack(anchor="w")
        tk.Label(contenedor, text="Datos base para reservas, dashboard y futura vista publica.",
                 font=("Arial", 10), bg=BG, fg="#555").pack(anchor="w", pady=(0, 14))

        panel = tk.Frame(contenedor, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
        panel.pack(fill="x", pady=8)

        campos = [
            ("Nombre del salon", "nombre", 42),
            ("Direccion", "direccion", 58),
            ("Telefono", "telefono", 24),
            ("Correo", "correo", 34),
            ("Zona", "zona", 30),
            ("Logo / imagen", "logo", 58),
            ("Precio base aproximado", "precio_base", 18),
            ("Precio por persona", "precio_por_persona", 18),
        ]
        self.entries = {}
        for i, (label, key, width) in enumerate(campos):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(panel, text=label, font=("Arial", 9, "bold"), bg="white", fg=TXT).grid(
                row=row * 2, column=col, padx=12, pady=(10, 2), sticky="w"
            )
            entry = tk.Entry(panel, width=width)
            entry.grid(row=row * 2 + 1, column=col, padx=12, pady=(0, 8), sticky="w")
            entry.insert(0, str(getattr(self.salon, key, "") or ""))
            self.entries[key] = entry

        tk.Button(panel, text="Buscar logo", command=self.seleccionar_logo,
                  bg=BTN2, fg="white", relief="flat", width=14, cursor="hand2").grid(
            row=5, column=3, padx=4, sticky="w"
        )

        resumen = tk.Frame(contenedor, bg="white", highlightbackground="#D1D5DB", highlightthickness=1)
        resumen.pack(fill="x", pady=8)
        tk.Label(resumen, text="Uso de estos datos", font=("Arial", 11, "bold"), bg="white", fg=TXT).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Label(resumen, text="El dashboard toma el nombre/logo. La futura vista publica usara zona, contacto y precios aproximados.",
                 font=("Arial", 9), bg="white", fg="#555", wraplength=780, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        acciones = tk.Frame(contenedor, bg=BG)
        acciones.pack(fill="x", pady=12)
        tk.Button(acciones, text="Guardar perfil", command=self.guardar,
                  bg=BTN, fg="white", relief="flat", width=18, height=2, cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Button(acciones, text="Volver", command=lambda: self.volver(FrameMenuAdmin),
                  bg="#777", fg="white", relief="flat", width=18, height=2, cursor="hand2").pack(side="left")

    def seleccionar_logo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar logo o imagen",
            filetypes=[("Imagen", "*.png *.jpg *.jpeg *.gif"), ("Todos", "*.*")]
        )
        if ruta:
            self.entries["logo"].delete(0, tk.END)
            self.entries["logo"].insert(0, ruta)

    def guardar(self):
        try:
            precio_base = float(self.entries["precio_base"].get().strip() or 0)
            precio_por_persona = float(self.entries["precio_por_persona"].get().strip() or 0)
        except ValueError:
            messagebox.showerror("Perfil del salon", "Los precios deben ser numeros.")
            return

        salon = Salon(
            self.entries["nombre"].get().strip() or "Sistema Salon",
            self.entries["direccion"].get().strip(),
            self.entries["telefono"].get().strip(),
            self.entries["correo"].get().strip(),
            self.entries["zona"].get().strip(),
            self.entries["logo"].get().strip(),
            precio_base,
            precio_por_persona,
            getattr(self.salon, "extra", {}),
        )
        GestorArchivos.guardar_salon(salon)
        messagebox.showinfo("Perfil del salon", "Perfil guardado correctamente.")
