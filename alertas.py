import time
import zenoh
import os
def main(conf: zenoh.Config):
    # Configurar sesión de Zenoh
    zenoh.init_log_from_env_or("error")

    os.system("echo Opening session...")
    with zenoh.open(conf) as session:

        os.system("echo Declaring Subscriber on 'casa/persona1/caida' and 'casa/habitacion1/video'...")
        os.system("echo Declaring Publisher on 'casa/alerta'...")
        pub_alert = session.declare_publisher("casa/alerta")

        caida_detected = False

        def listener_caida(sample: zenoh.Sample):
            nonlocal caida_detected
            #os.system(f"Received fall detection data on '{sample.key_expr}': {sample.payload.to_bytes()}")

            # Convertir el dato recibido a entero
            caida_value = int(sample.payload.to_bytes())

            if caida_value == 1:
                caida_detected = True
                os.system("echo Fall detected, waiting for recognition data...")

        def listener_recognition(sample: zenoh.Sample):
            nonlocal caida_detected

            os.system(f"echo Received recognition data on '{sample.key_expr}'")
            try:
                # Convertir los datos recibidos a un entero
                recognition_value = int(sample.payload.to_bytes().decode(errors='ignore').strip())

                if caida_detected:
                    if recognition_value == 1:
                        os.system("echo ALERT: Fall and recognition detected!")
                        pub_alert.put("1")
                    else:
                        os.system("echo No recognition detected. Resetting state.")
                        pub_alert.put("0")

                    caida_detected = False
            except Exception as e:
                os.system(f"echo Error processing recognition data: {e}")



        # Declarar los suscriptores
        session.declare_subscriber("casa/**/caida", listener_caida)
        session.declare_subscriber("casa/**/deteccion", listener_recognition)

        os.system("echo Listening for fall detection and recognition... Press CTRL-C to quit.")
        try:
            while True:
                time.sleep(1)  # Mantener el programa en ejecución
        except KeyboardInterrupt:
            os.system("echo Exiting...")

# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse
    import common

    parser = argparse.ArgumentParser(prog="alert_detection", description="Listen for fall detection and recognition to send alerts.")
    common.add_config_arguments(parser)

    args = parser.parse_args()
    conf = common.get_config_from_args(args)

    main(conf)
