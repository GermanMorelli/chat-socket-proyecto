"""Servidor de chat UDP que maneja multiples clientes y permite mensajes privados. El servidorUDP
procesa un mensaje donde: recibe, procesa y envia respuesta """
import socket
import datetime

HOST = "127.0.0.1"
PORT = 6000

"""Se usan diccionarios para almacenar los usuarios conectados. 
usuarios: clave es la direccion del cliente (IP, puerto) y valor es el nombre de usuario, permite identificar al cliente por su direccion
usuariosPorNombre: clave es el nombre de usuario y valor es la direccion del cliente, permite enviar mensajes privados facilmente buscando
la direccion del destinatario por su nombre.
"""
usuarios = {}         
usuariosPorNombre = {}


def main():
    """Crea el socket UDP donde AF_INET es para IPv4 y SOCK_DGRAM para UDP,
    luego lo enlaza el socket a la direccion y puerto. En un ciclo infinito,
    espera mensajes de los clientes, procesa mensajes privados o grupales, (siempre esta escuhando
    mensajes)"""
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    
    server.settimeout(1)

    print(f"[UDP] Servidor escuchando en {HOST}:{PORT}")

    try:
        while True:
            """Bucle principal que espera mensajes de los clientes y los procesa"""
            try:
                data, addr = server.recvfrom(4096)
            except socket.timeout:
                continue
            texto = data.decode().strip()

            """Si la direccion del cliente no esta en el diccionario de usuarios, se asume que es un nuevo usuario
            y se agrega al diccionario con su nombre."""
            if addr not in usuarios:
                
                if len(usuarios) >= 5:
                    server.sendto(b"[ERROR] Servidor lleno. Maximo 5 usuarios.", addr)
                    continue
                
                usuarios[addr] = texto
                usuariosPorNombre[texto] = addr
                print(f"[UDP] {texto} conectado desde {addr}")
                continue

            #para obtener el nombre del usuario que envio el mensaje
            nombre = usuarios[addr]

        
            
            """Obtiene la fecha y hora actual en formato dia/mes/año horas:minutos:segundos AM/PM"""
            fecha = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
            
            """para mensajes privados se verifica si el mensaje empieza con /priv, despues se separa el destinatario y el contenido
            se verifica si el destinatario existe, si no existe se envia un mensaje de error al remitente"""
            if texto.startswith("/priv"):
                _, destino, *contenido = texto.split()
                contenido = " ".join(contenido)

                if destino not in usuariosPorNombre:
                    server.sendto(f"[ERROR] Usuario '{destino}' no existe".encode(), addr)
                    continue

                addr_destino = usuariosPorNombre[destino]

                #enviar al destinatario
                server.sendto(f"[PRIVADO de {nombre}] [Fecha:{fecha}] {contenido}".encode(), addr_destino)
                #confirmar al remitente
                server.sendto(f"[PRIVADO para {destino}] [Fecha:{fecha}] {contenido}".encode(), addr)

                continue

            """Si no es priavdo significa que es un mensaje grupal"""
            mensajeFinal = f"[{nombre}] [Fecha:{fecha}] {texto}"

            """envia el mensaje a todos los clientes conectados excepto al remitente"""
            for cliente in usuarios:
                if cliente != addr:
                    server.sendto(mensajeFinal.encode(), cliente)
    except KeyboardInterrupt:
        print("\nCerrando servidor UDP...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
