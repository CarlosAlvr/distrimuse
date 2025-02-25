import time
import zenoh

def main():
    # Configurar sesión de Zenoh

    print("Opening session...")
    with zenoh.open() as session:

        #print("Declaring Subscriber on 'casa/**/acelerometro'...")
        #print("Declaring Publisher on 'casa/persona1/caida'...")
        pub = session.declare_publisher("casa/persona1/caida")

        def listener(sample: zenoh.Sample):
            #print(f"Received data on '{sample.key_expr}': {sample.payload.to_string()}")

            # Convertir el dato recibido a entero
            accelerometer_value = int(sample.payload.to_string())

            # Publicar 1 si se detecta un 1, 0 en caso contrario
            fall_detected = 1 if accelerometer_value == 1 else 0
            pub.put(str(fall_detected))
            if(fall_detected == 1):
                print(f"Published fall detection: {fall_detected}")
            

        # Declarar el suscriptor
        session.declare_subscriber("casa/**/acelerometro", listener)

        #print("Listening for data... Press CTRL-C to quit.")
        try:
            while True:
                time.sleep(1)  # Mantener el programa en ejecución
        except KeyboardInterrupt:
            print("Exiting...")

# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="fall_detection", description="Listen for accelerometer data and publish fall detection.")
  

    args = parser.parse_args()
   

    main()
