import customtkinter as ctk
import subprocess
import sys

ctk.set_appearance_mode("System")  # Automático claro/oscuro
ctk.set_default_color_theme("blue")

class MenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat - Selección de Protocolo")
        self.geometry("400x300")
        self.resizable(False, False)

        self.usuario = None
        self.protocolo = None

        self.frame_principal()

    def frame_principal(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        titulo = ctk.CTkLabel(self.frame, text="Selecciona el protocolo", font=("Arial", 20))
        titulo.pack(pady=20)

        btn_tcp = ctk.CTkButton(self.frame, text="Cliente TCP", command=lambda: self.ir_login("TCP"))
        btn_tcp.pack(pady=10)

        btn_udp = ctk.CTkButton(self.frame, text="Cliente UDP", command=lambda: self.ir_login("UDP"))
        btn_udp.pack(pady=10)

        btn_salir = ctk.CTkButton(self.frame, text="Salir", fg_color="red", command=self.destroy)
        btn_salir.pack(pady=20)

    def ir_login(self, protocolo):
        self.protocolo = protocolo
        self.frame.destroy()

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        titulo = ctk.CTkLabel(self.frame, text=f"Registro de usuario ({protocolo})", font=("Arial", 18))
        titulo.pack(pady=20)

        self.entry_usuario = ctk.CTkEntry(self.frame, placeholder_text="Ingresa tu nombre")
        self.entry_usuario.pack(pady=10)

        btn_entrar = ctk.CTkButton(self.frame, text="Entrar al chat", command=self.abrir_cliente)
        btn_entrar.pack(pady=10)

        btn_volver = ctk.CTkButton(self.frame, text="Volver", command=self.volver_menu)
        btn_volver.pack(pady=10)

    def volver_menu(self):
        self.frame.destroy()
        self.frame_principal()

    def abrir_cliente(self):
        self.usuario = self.entry_usuario.get().strip()

        if not self.usuario:
            ctk.CTkMessageBox(title="Error", message="Debes ingresar un nombre de usuario")
            return

        if self.protocolo == "TCP":
            subprocess.Popen([sys.executable, "cliente_tcp_gui.py", self.usuario])

        elif self.protocolo == "UDP":
            subprocess.Popen([sys.executable, "cliente_udp_gui.py", self.usuario])

        self.destroy()


if __name__ == "__main__":
    app = MenuApp()
    app.mainloop()
