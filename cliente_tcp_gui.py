import customtkinter as ctk
import sys
import queue
import socket
import threading
# el módulo cliente_tcp no es necesario aquí (la GUI gestiona sockets directamente)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


class ChatTCP(ctk.CTk):
    """
    Inicializa la interfaz gráfica del cliente de chat.
    Configura el layout principal con dos paneles:
    - Panel izquierdo: Lista de usuarios conectados
    - Panel derecho: Área de chat y entrada de mensajes
    Elementos creados:
    - panel_usuarios: Frame izquierdo con título y lista scrollable de usuarios
    - lista_usuarios: Frame scrollable para mostrar usuarios conectados
    - panel_chat: Frame derecho con chat_box, entry_msg y botón enviar
    - chat_box: Textbox de solo lectura para mostrar mensajes
    - entry_msg: Campo de entrada para escribir mensajes
    - btn_enviar: Botón para enviar mensaje (también activable con Enter)
    Establece la conexión TCP con el servidor de chat.
    Procesa:
    1. Crea un socket TCP (AF_INET, SOCK_STREAM)
    2. Se conecta al servidor en (SERVER_IP, SERVER_PORT)
    3. Intenta recibir un prompt inicial del servidor (con timeout de 2s)
    4. Envía el nombre de usuario al servidor
    5. Inicia un hilo daemon para recibir mensajes continuamente
    Excepciones:
    - En caso de error, coloca un mensaje de sistema en la cola de UI
    Hilo daemon que recibe mensajes continuamente del servidor.
    Procesa:
    - Recibe datos en bloques de 1024 bytes y decodifica UTF-8
    - Detecta notificaciones de sistema: "SISTEMA_DEL:<usuario>" indica desconexión
    - Filtra mensajes de sistema obsoletos (se unio/salio del chat)
    - Filtra privados reenviados al mismo autor
    - Coloca mensajes en cola_ui para procesamiento seguro en el hilo principal
    Finalización:
    - Se detiene cuando recv retorna vacío (conexión cerrada)
    - Notifica cierre de conexión mediante mensaje de sistema
    Procesa la cola de mensajes desde el hilo de red (cada 50ms).
    Tipos de eventos procesados:
    - 'mensaje': Muestra el mensaje en el chat_box
    - 'add': Añade usuario a la lista si no existe
    - 'del': Elimina usuario de la lista y refresca
    Se ejecuta recursivamente cada 50ms mediante self.after() para actualizar
    la UI de forma segura desde el hilo principal.
    Muestra un mensaje en el chat_box de forma segura.
    Parámetros:
        msg (str): Mensaje a mostrar (puede contener prefijos como [TÚ], [PRIVADO], etc.)
    Procesos:
    1. Cambia el estado del chat_box a 'normal' para permitir inserción
    2. Inserta el mensaje con indentación y espacios separadores
    3. Desplaza la vista hacia el final (autoscroll)
    4. Restaura el estado 'disabled' para evitar edición manual
    Actualiza el listado de usuarios conectados en el panel izquierdo.
    Procesos:
    1. Limpia todos los widgets actuales de lista_usuarios
    2. Para cada usuario en self.usuarios:
       - Si es el usuario actual: botón deshabilitado con etiqueta "(tú)"
       - Si es otro usuario: botón clickeable que abre submenu de acciones
    Se llama automáticamente cuando se detecta un cambio en la lista de usuarios.
    Muestra un menú contextual con acciones disponibles para un usuario.
    Parámetros:
        usuario (str): Nombre del usuario seleccionado
        frame_usuario (ctk.CTkFrame): Frame del usuario en la lista
    Procesos:
    1. Destruye submenu previo si existe
    2. Crea un nuevo submenu con opciones (actualmente solo "Mensaje privado")
    3. Posiciona el submenu después del frame del usuario
    4. Asigna referencia submenu al frame para control posterior
    Activa el modo de mensaje privado con un usuario específico.
    Parámetros:
        usuario (str): Usuario destinatario del mensaje privado
        submenu (ctk.CTkFrame): Submenu a cerrar tras activación
    Procesos:
    1. Establece self.destino_privado al usuario seleccionado
    2. Actualiza placeholder del entry_msg para indicar el modo privado
    3. Destruye el submenu si aún existe
    4. Da foco al campo de entrada para escribir inmediatamente
    Crea una ventana emergente con acciones para un usuario (DEPRECADO).
    Parámetros:
        usuario (str): Usuario sobre el que mostrar acciones
    Nota:
    Este método está deprecado en favor de mostrar_submenu() que integra
    las acciones directamente en la lista sin ventana emergente adicional.
    Envía un mensaje público o privado al servidor.
    Procesos:
    1. Obtiene el texto del entry_msg y elimina espacios
    2. Valida que no esté vacío (evita enviar placeholders)
    3. Si hay destino_privado:
       - Construye comando: "/priv <usuario> <mensaje>"
       - Envía por socket
       - Muestra en chat como "[PRIVADO → usuario]"
       - Resetea destino_privado y placeholder
    4. Si es mensaje público:
       - Envía mensaje directamente
       - Muestra en chat como "[TÚ]"
    5. Limpia el campo de entrada tras envío exitoso
    Excepciones:
    - Captura errores de envío y muestra notificación de sistema
    Cierra la conexión con el servidor y destruye la ventana.
    Procesos:
    1. Intenta enviar comando "/salir" al servidor
    2. Cierra el socket TCP
    3. Destruye la ventana principal
    Nota:
    Todos los pasos están envueltos en try-except para asegurar que
    la ventana se destruye incluso si hay errores en la desconexión.

    ChatTCP - TCP Chat Client with GUI
    A customtkinter-based TCP chat client that allows users to connect to a chat server,
    send public messages, and exchange private messages with other connected users.
    Attributes:
        usuario (str): The username of the connected client.
        usuarios (list): List of all connected users.
        destino_privado (str | None): The target user for private messages, if any.
        cola_ui (queue.Queue): Thread-safe queue for UI updates from network thread.
        sock (socket.socket): TCP socket for server communication.
        panel_usuarios (ctk.CTkFrame): Left panel displaying connected users.
        lista_usuarios (ctk.CTkScrollableFrame): Scrollable frame for user list.
        panel_chat (ctk.CTkFrame): Right panel containing chat interface.
        chat_box (ctk.CTkTextbox): Read-only text widget displaying messages.
        entry_msg (ctk.CTkEntry): Input field for typing messages.
        btn_enviar (ctk.CTkButton): Send message button.
    Methods:
        crear_ui(): Initializes the GUI layout with panels, chat box, and input fields.
        conectar_servidor(): Establishes TCP connection to server and starts receive thread.
        _recibir_mensajes(): Daemon thread that continuously receives and queues messages from server.
        procesar_cola_ui(): Processes queued UI updates from network thread (called every 50ms).
        _mostrar_mensaje(msg): Displays a message in the chat box.
        refrescar_lista(): Updates the user list display in the left panel.
        mostrar_submenu(usuario, frame_usuario): Shows action menu for a selected user.
        activar_privado(usuario, submenu): Activates private message mode for a user.
        menu_privado(usuario): Creates a popup window with user actions (deprecated).
        enviar_mensaje(): Sends public or private message to server based on destino_privado state.
        cerrar(): Closes the connection and destroys the window.
    """
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"Chat TCP - {usuario}")
        self.geometry("900x500")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.usuarios = [self.usuario]
        self.destino_privado = None
        self.cola_ui = queue.Queue()

        self.crear_ui()
        self.conectar_servidor()

        self.after(50, self.procesar_cola_ui)

    # ================= UI =================
    def crear_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.panel_usuarios = ctk.CTkFrame(self, width=220)
        self.panel_usuarios.grid(row=0, column=0, sticky="ns")
        self.panel_usuarios.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.panel_usuarios, text="Usuarios", font=("Arial", 16)).grid(row=0, column=0, pady=10)

        self.lista_usuarios = ctk.CTkScrollableFrame(self.panel_usuarios)
        self.lista_usuarios.grid(row=1, column=0, sticky="nsew", padx=10)

        self.panel_chat = ctk.CTkFrame(self)
        self.panel_chat.grid(row=0, column=1, sticky="nsew")
        self.panel_chat.grid_rowconfigure(0, weight=1)
        self.panel_chat.grid_columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkTextbox(self.panel_chat, state="disabled")
        self.chat_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.entry_msg = ctk.CTkEntry(self.panel_chat)
        self.entry_msg.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.entry_msg.bind("<Return>", lambda e: self.enviar_mensaje())

        self.btn_enviar = ctk.CTkButton(self.panel_chat, text="Enviar", command=self.enviar_mensaje)
        self.btn_enviar.grid(row=1, column=1, padx=10, pady=10)

    # ================= RED =================
    def conectar_servidor(self):
        # Conectar directamente usando sockets y enviar el nombre de usuario
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_IP, SERVER_PORT))

            # recibir prompt inicial (p. ej. "Usuario: ") si el servidor lo envía
            try:
                self.sock.settimeout(2.0)
                try:
                    _ = self.sock.recv(1024)
                except socket.timeout:
                    pass
                finally:
                    self.sock.settimeout(None)
            except:
                pass

            # enviar nombre de usuario
            self.sock.sendall(self.usuario.encode())

            # Iniciar hilo para recibir mensajes
            thread = threading.Thread(target=self._recibir_mensajes, daemon=True)
            thread.start()

        except Exception as e:
            self.cola_ui.put(("mensaje", f"[SISTEMA] Error al conectar: {e}\n"))

    def _recibir_mensajes(self):
        try:
            while True:
                msg = self.sock.recv(1024).decode()
                
                if not msg:
                    break

                if msg.startswith("SISTEMA_DEL:"):
                    nombre = msg.replace("SISTEMA_DEL:", "").strip()
                    self.cola_ui.put(("del", nombre))
                    continue

                # filtrar mensajes de sistema viejos
                if "se unio al chat" in msg or "salio del chat" in msg:
                    continue

                # filtrar privados reenviados al mismo autor
                if msg.startswith(f"[PRIVADO para {self.usuario}]"):
                    continue

                self.cola_ui.put(("mensaje", msg))
        except Exception:
            pass
        finally:
            # avisar cierre
            self.cola_ui.put(("mensaje", "[SISTEMA] Conexión cerrada por el servidor\n"))

    # ================= UI SEGURA =================
    def procesar_cola_ui(self):
        try:
            while True:
                tipo, data = self.cola_ui.get_nowait()

                if tipo == "mensaje":
                    self._mostrar_mensaje(data)

                elif tipo == "add":
                    if data not in self.usuarios:
                        self.usuarios.append(data)
                        self.refrescar_lista()

                elif tipo == "del":
                    if data in self.usuarios:
                        self.usuarios.remove(data)
                        self.refrescar_lista()

        except queue.Empty:
            pass

        self.after(50, self.procesar_cola_ui)

    def _mostrar_mensaje(self, msg):
        self.chat_box.configure(state="normal")
        texto = msg.strip()

        if texto.startswith("[TÚ]"):
            self.chat_box.insert("end", f"  {texto}\n\n")
        elif "PRIVADO" in texto:
            self.chat_box.insert("end", f"  {texto}\n\n")
        else:
            self.chat_box.insert("end", f"  {texto}\n\n")

        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    # ================= USUARIOS =================
    def refrescar_lista(self):
        for widget in self.lista_usuarios.winfo_children():
            widget.destroy()

        for user in self.usuarios:
            if user != self.usuario:
                frame = ctk.CTkFrame(self.lista_usuarios, fg_color="transparent")
                frame.pack(fill="x", pady=4)

                btn = ctk.CTkButton(frame, text=user, command=lambda u=user, f=frame: self.mostrar_submenu(u, f))
                btn.pack(fill="x")

            else:
                btn = ctk.CTkButton(self.lista_usuarios, text=f"{user} (tú)", state="disabled")
                btn.pack(fill="x", pady=4)

    def mostrar_submenu(self, usuario, frame_usuario):
        for widget in self.lista_usuarios.winfo_children():
            if hasattr(widget, "submenu"):
                widget.submenu.destroy()
                del widget.submenu

        submenu = ctk.CTkFrame(self.lista_usuarios, corner_radius=8)
        submenu.pack(after=frame_usuario, fill="x", padx=10, pady=3)

        btn_privado = ctk.CTkButton(
            submenu,
            text="Mensaje privado",
            fg_color="#f394cd",
            command=lambda: self.activar_privado(usuario, submenu)
        )
        btn_privado.pack(fill="x", padx=5, pady=5)

        frame_usuario.submenu = submenu

    def activar_privado(self, usuario, submenu):
        # Activar modo privado
        self.destino_privado = usuario
        self.entry_msg.configure(placeholder_text=f"Mensaje privado para {usuario}")
        
        # Cerrar el submenú
        if submenu.winfo_exists():
            submenu.destroy()
        
        # Dar foco al entry
        self.entry_msg.focus()



    def menu_privado(self, usuario):
        ventana = ctk.CTkToplevel(self)
        ventana.geometry("220x120")
        ventana.title(usuario)
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(ventana, text=f"Acciones con {usuario}").pack(pady=10)

        def activar_privado():
            self.destino_privado = usuario
            self.entry_msg.configure(placeholder_text=f"Mensaje privado para {usuario}")
            ventana.destroy()

        ctk.CTkButton(ventana, text="Enviar mensaje privado", command=activar_privado).pack(pady=10)

    # ================= ENVÍO =================
    def enviar_mensaje(self):
        msg = self.entry_msg.get().strip()

        # ✅ Evita enviar placeholder
        if not msg:
            return

        try:
            if self.destino_privado:
                comando = f"/priv {self.destino_privado} {msg}"
                try:
                    self.sock.sendall(comando.encode())
                except Exception:
                    self._mostrar_mensaje("[SISTEMA] Error al enviar mensaje privado\n")
                else:
                    self._mostrar_mensaje(f"[PRIVADO → {self.destino_privado}] {msg}\n")

                self.destino_privado = None
                self.entry_msg.configure(placeholder_text="Escribe un mensaje...")

            else:
                try:
                    self.sock.sendall(msg.encode())
                except Exception:
                    self._mostrar_mensaje("[SISTEMA] Error al enviar mensaje\n")
                else:
                    self._mostrar_mensaje(f"[TÚ] {msg}\n")
        finally:
            try:
                self.entry_msg.delete(0, "end")
            except Exception:
                pass

    def cerrar(self):
        try:
            try:
                self.sock.sendall(b"/salir")
            except:
                pass
            try:
                self.sock.close()
            except:
                pass
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cliente_tcp_gui.py <usuarioAingresar>")
        sys.exit(1)

    usuario = sys.argv[1]
    app = ChatTCP(usuario)
    app.mainloop()
