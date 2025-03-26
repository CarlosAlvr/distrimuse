import time
import cv2
import itertools
import zenoh
import numpy as np
import os

def main(conf: zenoh.Config):
    # Configurar sesión de Zenoh
    zenoh.init_log_from_env_or("error")
    camera_id = None
    print("Opening session...")

    for i in range(5):  # Prueba los primeros 5 índices de cámara
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Cámara disponible en el índice: {i}")
                camera_id = i
                cap.release()
                break
            else:
                print(f"No se encontró cámara en el índice: {i}")
        except Exception as e:
            print(f"Error al intentar abrir la cámara en el índice {i}: {e}")
            # Continúa con el siguiente índice
            pass

    if camera_id is None:
        print("No se encontró ninguna cámara disponible.")
    else:
        print(f"Usando la cámara en el índice: {camera_id}")
    
    # Resto del código...
    with zenoh.open(conf) as session:
        env_input = os.environ.get('DISTRIMUSE_INPUT_0')
        if env_input is None:
            os.system("Error: La variable de entorno 'Distrimuse_input_0' no está definida.")
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os
