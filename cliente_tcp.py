import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

class ClienteTCP:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectado = False

    def conectar(self, nombre_usuario):
        """Conecta al socket y realiza el 'handshake' inicial del nombre."""
        try:
            self.sock.connect((SERVER_IP, SERVER_PORT))
            
            # El servidor envía un prompt inicial (lo leemos para limpiar el buffer)
            prompt = self.sock.recv(1024).decode()
            
            # Enviamos el nombre inmediatamente como pide tu protocolo
            self.sock.sendall(nombre_usuario.encode())
            self.conectado = True
            return True, "Conectado exitosamente"
        except Exception as e:
            return False, f"Error de conexión: {e}"

    def enviar_mensaje(self, mensaje):
        """Envía bytes al servidor."""
        if self.conectado:
            try:
                self.sock.sendall(mensaje.encode())
            except Exception as e:
                print(f"Error enviando: {e}")

    def recibir_mensaje(self):
        """Intenta recibir mensajes. Retorna el mensaje o None si falla."""
        if self.conectado:
            try:
                msg = self.sock.recv(4096).decode()
                if not msg:
                    self.cerrar()
                    return None
                return msg
            except:
                return None
        return None

    def cerrar(self):
        self.conectado = False
        try:
            self.sock.close()
        except:
            pass

# --- COMPATIBILIDAD CON TERMINAL (Para que menu.py siga sirviendo) ---
def escucharServidor(cliente_obj):
    while cliente_obj.conectado:
        msg = cliente_obj.recibir_mensaje()
        if msg:
            print("\n" + msg, end="")
            print("> ", end="", flush=True)
        else:
            break

def main():
    cliente = ClienteTCP()
    # Simulación del input original
    # Primero conectamos 'físicamente' para recibir el banner
    # Nota: Modifiqué ligeramente el flujo para adaptar la clase
    cliente.sock.connect((SERVER_IP, SERVER_PORT)) 
    banner = cliente.sock.recv(1024).decode()
    nombre = input(banner)
    cliente.sock.sendall(nombre.encode())
    cliente.conectado = True

    threading.Thread(target=escucharServidor, args=(cliente,), daemon=True).start()

    print("Comandos:\n /priv usuario mensaje\n /salir")
    while True:
        texto = input("> ").strip()
        if texto == "/salir":
            cliente.cerrar()
            break
        cliente.enviar_mensaje(texto)

if __name__ == "__main__":
    main()
    