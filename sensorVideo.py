import time
import cv2
import itertools
import zenoh
import numpy as np
import os

def main(conf: zenoh.Config):
    # Zenoh sesion configured
    zenoh.init_log_from_env_or("error")
    camera_id = None
    print("Opening session...")

    for i in range(5):  # Trys the first 5 videos searching for a camera
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"echo Camera available in the index: {i}")
                camera_id = i
                cap.release()
                break
            else:
                print(f"echo No camera found in the index: {i}")
        except Exception as e:
            print(f"echo Error trying to open the camera in the index {i}: {e}")
            # Continues with the next one
            pass

    if camera_id is None:
        print("echo No cameras available.")
    else:
        print(f"echo Using the camera on the index finger: {camera_id}")
    

    with zenoh.open(conf) as session:
        env_input = os.environ.get('DISTRIMUSE_INPUT_0')
        if env_input is None:
            os.system("echo Error: The environment variable 'Distrimuse_input_0' is not defined.")
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os.system("echo Error: The environment variable 'Distrimuse_output_0' is not defined.")

        # Declarar publisher utilizando la variable de entorno
        pub_video = session.declare_publisher(env_output)
        
        # Inicializar cámara
        cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)  # Para Linux

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        def listener_caida(sample: zenoh.Sample):
            # Convertir el dato recibido a entero
            fall_detected = int(sample.payload.to_string())
            if fall_detected == 1:
                print("Fall detected. Capturing and sending video frame.")
                # Capturar un solo frame de la cámara
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame from camera.")
                    return
                # Procesar y enviar el frame
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                pub_video.put(frame_data)
                print("Published processed video frame.")

        # Declarar el suscriptor
        session.declare_subscriber(env_input, listener_caida)
        print("Listening for fall detection... Press CTRL-C to quit.")
        try:
            while True:
                time.sleep(1)  # Mantener el programa en ejecución
        except KeyboardInterrupt:
            print("Exiting...")
        # Liberar recursos
        cap.release()

# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse
    import common

    parser = argparse.ArgumentParser(
        prog="fall_video_detection",
        description="Listen for fall detection and send video frames."
    )
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    print(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config)
    main(conf)
