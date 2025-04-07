import time
import zenoh
import common
import argparse
import os
import json

def fall_detection(ax, ay, az):

    umbral_min = 3.0  # Umbral mínimo de aceleración brusca indicando caída libre
    umbral_max = 12.0 # Umbral máximo que puede indicar un impacto
    total_acceleration = (ax**2 + ay**2 + az**2) ** 0.5
    return 1 if aceleracion_total < umbral_min or aceleracion_total > umbral_max else 0

def main(conf):
    env_input = os.environ.get('DISTRIMUSE_INPUT_0')
    if env_input is None:
        print("Error: The environment variable 'DISTRIMUSE_INPUT_0' is not defined.")
        return

    env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
    if env_output is None:
        print("Error: The environment variable 'DISTRIMUSE_OUTPUT_0' is not defined.")
        return

    print(f"The defined inputs -> outputs are: {env_input} -> {env_output}")

    # Inicializar el log de Zenoh
    zenoh.init_log_from_env_or("error")

    try:
        with zenoh.open(conf) as session:
            print("Zenoh session started.")

            # Declarar publisher y subscriber usando las variables de entorno
            pub = session.declare_publisher(env_output)
            print("The publisher has been declared.")

            def listener(sample: zenoh.Sample):
                try:
                    # Usamos eval en lugar de json.loads para interpretar el mensaje
                    data = json.loads(sample.payload.to_string())
                    ax, ay, az = data['ax'], data['ay'], data['az']
                    print(f"{data},{ax},{ay},{az}")
                    fall = fall_detection(ax, ay, az)
                    pub.put(str(fall))
                    if fall == 1:
                        print("¡A fall has been detected, sending data to video_sensor!")
                except Exception as e:
                    print(f"Error processing message: {e}")

            session.declare_subscriber(env_input, listener)
            print("The subscriber has been declared.")

            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="fall_detection",
        description="Listen to accelerometer data and detect falls."
    )
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    print(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config)
    main(conf)
