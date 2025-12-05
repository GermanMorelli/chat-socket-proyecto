#!/bin/bash
# 1. Arrancamos los servidores TCP/UDP en el fondo
python servidores.py &

# 2. Esperamos unos segundos para asegurar que arranquen
sleep 3

# 3. Arrancamos la interfaz web
streamlit run app_gui.py --server.port $PORT --server.address 0.0.0.0