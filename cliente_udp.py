import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 6000

class ClienteUDP:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0)) # Puerto aleatorio
        self.conectado = False

    def conectar(self, nombre_usuario):
        """En UDP no hay conexión real, pero enviamos el nombre para registrarnos."""
        try:
            self.sock.sendto(nombre_usuario.encode(), (SERVER_IP, SERVER_PORT))
            self.conectado = True
            return True, "Registrado en UDP"
        except Exception as e:
            return False, f"Error UDP: {e}"

    def enviar_mensaje(self, mensaje):
        if self.conectado:
            try:
                self.sock.sendto(mensaje.encode(), (SERVER_IP, SERVER_PORT))
            except Exception as e:
                print(f"Error enviando UDP: {e}")

    def recibir_mensaje(self):
        if self.conectado:
            try:
                data, addr = self.sock.recvfrom(4096)
                return data.decode()
            except:
                return None
        return None

    def cerrar(self):
        self.conectado = False
        try:
            self.sock.close()
        except:
            pass

# --- COMPATIBILIDAD CON TERMINAL ---
def escuchar(cliente_obj):
    while cliente_obj.conectado:
        msg = cliente_obj.recibir_mensaje()
        if msg:
            print("\n" + msg)
            print("> ", end="", flush=True)

def main():
    cliente = ClienteUDP()
    nombre = input("Tu nombre de usuario: ")
    cliente.conectar(nombre)

    threading.Thread(target=escuchar, args=(cliente,), daemon=True).start()

    print("Comandos:\n/priv usuario mensaje\n/salir")
    while True:
        msg = input("> ").strip()
        if msg == "/salir":
            cliente.cerrar()
            break
        cliente.enviar_mensaje(msg)

if __name__ == "__main__":
    main()