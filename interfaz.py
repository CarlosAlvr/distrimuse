import argparse
import json
import time
import zenoh
import flet as ft
from datetime import datetime
import pytz
import os

def flet_app(page: ft.Page, conf: zenoh.Config, key: str):
    # Configuración de la UI en Flet
    page.title = "Zenoh Alert Subscriber"
    alert_messages = []  # Lista para almacenar los últimos 10 mensajes
    max_messages = 10

    def update_alerts():
        page.controls.clear()
        for msg in alert_messages:
            page.controls.append(ft.Text(msg, style="color: blue; font-weight: bold;"))
        page.update()

    # Abrir la sesión Zenoh
    session = zenoh.open(conf)
    
    def listener(sample: zenoh.Sample):
        topic = sample.key_expr
        os.system(f"echo {topic}")
        
        
        
        
        
        # Obtener la hora actual en España
        tz = pytz.timezone('Europe/Madrid')
        hora_actual = datetime.now(tz).strftime('%H:%M:%S')
        
        # Formatear el mensaje de alerta
        message = f"Hemos detectado un caído en la {topic} a la hora {hora_actual}"
        os.system(f"echo {message}")     
        
        # Almacenar los últimos 10 mensajes
        if len(alert_messages) >= max_messages:
            alert_messages.pop(0)
        alert_messages.append(message)
        
        update_alerts()
    
    session.declare_subscriber(key, listener)

    # Mantener el hilo vivo para recibir eventos
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        session.close()
        os.system("echo Zenoh session closed.")

def main():
    parser = argparse.ArgumentParser(description="Zenoh alert subscriber")
    parser.add_argument("--mode", "-m", choices=["peer", "client"], type=str)
    parser.add_argument("--connect", "-e", metavar="ENDPOINT", action="append", type=str)
    parser.add_argument("--listen", "-l", metavar="ENDPOINT", action="append", type=str)
    parser.add_argument("--key", "-k", default="casa/**/deteccion", type=str)
    parser.add_argument("--config", "-c", metavar="FILE", type=str)
    args = parser.parse_args()

    # Construir la configuración de Zenoh
    conf = zenoh.Config.from_file(args.config) if args.config else zenoh.Config()
    if args.mode:
        conf.insert_json5("mode", json.dumps(args.mode))
    if args.connect:
        conf.insert_json5("connect/endpoints", json.dumps(args.connect))
    if args.listen:
        conf.insert_json5("listen/endpoints", json.dumps(args.listen))

    # Iniciar la aplicación Flet con la configuración y la clave
    ft.app(target=lambda p: flet_app(p, conf, args.key))

if __name__ == "__main__":
    main()
