import threading
import server_tcp
import server_udp

def main():
    # Hilo para servidor TCP
    hilo_tcp = threading.Thread(target=server_tcp.main, daemon=True)
    
    # Hilo para servidor UDP
    hilo_udp = threading.Thread(target=server_udp.main, daemon=True)

    hilo_tcp.start()
    hilo_udp.start()

    print("Servidores TCP y UDP corriendo simultáneamente...\nPresiona CTRL+C para detener.")

    try:
        # Mantener el programa principal vivo
        while True:
            pass
    except KeyboardInterrupt:
        print("\nCerrando servidores...")

if __name__ == "__main__":
    main()
