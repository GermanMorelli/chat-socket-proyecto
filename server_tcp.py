"""Servidor TCP para chat multiusuario con mensajes privados y grupales,
se importa la libreria socket para crear el servidor y manejar las conexiones de red
y threading para atender a los clientes de manera simultanea"""
import datetime
import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

"""se usa UN diccionario para almacenar los clientes conectados, donde la clave es el nombre de usuario
y el valor es el objeto de conexion del socket al que corresponde ese usuario PERMITIENDO enviar mensajes
a cualquier cliente usando solo su nombre.
threading.lock() funciona como un semaforo evitando problemas cuando varios hilos intentan acceder o modificar
el diccionario al mismo tiempo"""
clientes = {}          
lock = threading.Lock()


def broadcast(mensaje, remitente=None):
    """Envia un mensaje a todos los clientes conectados, excepto al remitente si se especifica, 
    de forma que itera sobre el diccionario de clientes y envia el mensaje a cada uno
    se usa un bloque try-catch por si falla un envio, continua con el siguiente cliente"""

    for nombre, conn in clientes.items():
        if nombre != remitente:
            try:
                conn.sendall(mensaje.encode())
            except:
                pass


def manejarCliente(conn, addr):
    """Maneja la comunicacion con un cliente conectado, registra el nombre de usuario,
    recibe mensajes y los procesa para mensajes privados o grupales, si el cliente se desconecta 
    elimina al cliente de la lista y avisa a los demas. Conn es el socket del cliente y addr es su direccion"""
    nombre = None
    try:
        conn.sendall(b"Usuario: ")
        nombre = conn.recv(1024).decode().strip()

        with lock:
            """with lock bloquea el acceso para evitar conflictos entre los hilos, despues se verifica
            si el nombre ingresado ya existe, si es asi se envia un error y se cierra la conexion,
            si no, se agrega el cliente al diccionario guardando su conexion"""

            if len(clientes) >= 5:
                conn.sendall(b"ERROR: Servidor lleno. Maximo 5 usuarios.\n")
                conn.close()
                return
            
            if nombre in clientes:
                conn.sendall(b"ERROR: Usuario ya existe\n")
                conn.close()
                return
            clientes[nombre] = conn

        """Muestra el servidor de quien se conecto y avisa a todos los cliengtes que alguien nuevo entro"""
        print(f"[TCP] {nombre} conectado desde {addr}")
        broadcast(f"*** {nombre} se unio al chat ***\n")

        while True:
            """Bucle principal para recibir mensajes del cliente, espera mensajes del cliengte y si
            el mensaje esta vacio significa que se desconecto, si hay algun error al recibir, se sale del ciclo"""
            msg = conn.recv(1024).decode()
            if not msg:
                break

            msg = msg.strip()

            """identifica cel comando del mensaje que es privado, despues separa el destinario y el mensaje
            y por ultimo reconstruye el mensaje completo. Se verifica si el destino existe, envia el mensaje, 
            envia la confirmacion al remitenete y despues salta al sig mensaje con continue"""
            
            fecha = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
            if msg.startswith("/priv"):
                _, destino, *contenido = msg.split()
                contenido = " ".join(contenido)

                if destino in clientes:
                    """envia el mensaje privado al destinario y la confirmacion al remitente con la fecha/hora"""
                    clientes[destino].sendall(f"[{fecha}] [PRIVADO de {nombre}] {contenido}\n".encode())
                    conn.sendall(f"[PRIVADO para {destino}] [Fecha:{fecha}] {contenido}\n".encode())
                else:
                    conn.sendall(b"ERROR: Usuario no encontrado\n")
                continue

            """envia mensajes grupales a todos los clientes conectados con la fecha/hora actual"""    
            broadcast(f"[{nombre}] [Fecha:{fecha}] {msg}\n", remitente=nombre)

    except:
        pass
   
    finally:
        """Bloquea para eliminar al cliente de forma segura, despues se quita al cliente de la lista
        y broadcast() avisa al grupo que el usuario se salio. por ultimo se cierra la conexion"""
        with lock:
            if nombre in clientes:
                del clientes[nombre]
        broadcast(f"*** {nombre} salio del chat ***\n")
        print(f"[TCP] {nombre} desconectado")
        conn.close()


def main():
    """Configutra e inicia el servidor creando un socket TCO, despues lo asocia al puerto y 
    pone al servidor en modo escucha"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    
    server.settimeout(1)

    print(f"[TCP] Servidor escuchando en {HOST}:{PORT}")

    try:
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=manejarCliente, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                pass  
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
