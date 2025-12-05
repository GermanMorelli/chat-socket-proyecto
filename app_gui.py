import streamlit as st
import time
import threading
import datetime
from cliente_tcp import ClienteTCP
from cliente_udp import ClienteUDP

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Chat TCP/UDP", 
    page_icon="💬",
    layout="wide"
)

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if 'cliente_obj' not in st.session_state:
    st.session_state.cliente_obj = None
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
if 'tipo_conexion' not in st.session_state:
    st.session_state.tipo_conexion = ""
if 'nombre_usuario' not in st.session_state:
    st.session_state.nombre_usuario = ""

# --- HILO DE ESCUCHA (MODIFICADO) ---
# NOTA: Quitamos todas las referencias a 'st.session_state' de aquí dentro.
# Recibimos las referencias como argumentos explícitos.
def hilo_escucha(cliente_instancia, lista_mensajes_referencia):
    """
    Escucha mensajes entrantes. 
    NO usa st.session_state directamente para evitar errores de contexto.
    """
    # Usamos la propiedad .conectado del objeto cliente, no la de Streamlit
    while cliente_instancia.conectado:
        try:
            # Bloqueante hasta recibir algo
            mensaje = cliente_instancia.recibir_mensaje()
            
            if mensaje:
                print(f"[DEBUG Hilo] Recibido: {mensaje}")
                # Al ser una lista mutable, podemos hacer append y Streamlit lo verá
                lista_mensajes_referencia.append(mensaje)
            else:
                # Si retorna None, el servidor cerró o hubo error
                break
        except Exception as e:
            print(f"[ERROR Hilo]: {e}")
            break
        
        time.sleep(0.1)

# --- BARRA LATERAL (LOGIN Y CONFIGURACIÓN) ---
with st.sidebar:
    st.header("🔌 Conexión")
    
    if not st.session_state.conectado:
        nombre_input = st.text_input("Nombre de Usuario", placeholder="Ej: Maria")
        protocolo = st.selectbox("Protocolo", ["TCP", "UDP"])
        
        if st.button("Conectar", type="primary"):
            if nombre_input:
                st.session_state.nombre_usuario = nombre_input
                
                # Instanciamos la clase correcta
                if protocolo == "TCP":
                    cliente = ClienteTCP()
                    st.session_state.tipo_conexion = "TCP"
                else:
                    cliente = ClienteUDP()
                    st.session_state.tipo_conexion = "UDP"

                # Conectamos
                exito, info = cliente.conectar(nombre_input)
                
                if exito:
                    st.session_state.cliente_obj = cliente
                    st.session_state.conectado = True
                    st.success(info)
                    
                    # --- CORRECCIÓN CRÍTICA AQUÍ ---
                    # Pasamos los objetos EXPLICITAMENTE al hilo.
                    # Así el hilo no tiene que buscar 'st.session_state'
                    t = threading.Thread(
                        target=hilo_escucha, 
                        args=(st.session_state.cliente_obj, st.session_state.historial), 
                        daemon=True
                    )
                    t.start()
                    
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"Error: {info}")
            else:
                st.warning("El nombre es obligatorio.")
                
        st.info("Asegúrate de correr `servidores.py` primero.")
        
    else:
        st.success(f"🟢 En línea como **{st.session_state.nombre_usuario}**")
        st.write(f"Protocolo: **{st.session_state.tipo_conexion}**")
        
        st.markdown("---")
        st.caption("Comandos especiales:")
        st.code("/priv usuario mensaje")
        st.markdown("---")
        
        if st.button("Desconectar", type="primary"):
            if st.session_state.cliente_obj:
                st.session_state.cliente_obj.cerrar()
            st.session_state.conectado = False
            st.session_state.cliente_obj = None
            st.session_state.historial = []
            st.rerun()

# --- ÁREA PRINCIPAL DE CHAT ---
st.title(f"Sala de Chat {st.session_state.tipo_conexion}")

contenedor_mensajes = st.container(height=500)

with contenedor_mensajes:
    if len(st.session_state.historial) == 0:
        st.info("Esperando mensajes... ¡Saluda!")
    
    for msj in st.session_state.historial:
        if "[PRIVADO" in msj:
            st.warning(msj, icon="🔒")
        elif "[Yo]" in msj:
            st.markdown(f"**{msj}**")
        elif "***" in msj:
             st.caption(msj)
        elif "[ERROR]" in msj:
            st.error(msj)
        else:
            st.text(msj)

# --- INPUT DE MENSAJES ---
if st.session_state.conectado:
    prompt = st.chat_input(f"Escribe un mensaje como {st.session_state.nombre_usuario}...")
    
    if prompt:
        # Enviar al servidor
        st.session_state.cliente_obj.enviar_mensaje(prompt)
        
        # ECO LOCAL
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        mi_mensaje_formateado = f"[Yo] [{hora_actual}] {prompt}"
        st.session_state.historial.append(mi_mensaje_formateado)
        
        st.rerun()

    # --- AUTO REFRESCO ---
    # Esto mantiene la UI actualizada con lo que el hilo recibe
    time.sleep(1)
    st.rerun()

else:
    st.write("👈 Por favor, inicia sesión en el menú de la izquierda.")