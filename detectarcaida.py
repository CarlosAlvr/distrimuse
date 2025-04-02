import time
import zenoh
import common
import argparse
import os
import json

def detectar_caida(ax, ay, az):

    umbral_min = 3.0  # Umbral mínimo de aceleración brusca indicando caída libre
    umbral_max = 12.0 # Umbral máximo que puede indicar un impacto
    aceleracion_total = (ax**2 + ay**2 + az**2) ** 0.5
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

    print(f"Defined inputs/outputs: {env_input} -> {env_output}")

    # Inicializar el log de Zenoh
    zenoh.init_log_from_env_or("error")

    try:
        with zenoh.open(conf) as session:
            print("Zenoh session started.")

            # Declarar publisher y subscriber usando las variables de entorno
            pub = session.declare_publisher(env_output)
            print("Declared publisher.")

            def listener(sample: zenoh.Sample):
                try:
                    # Usamos eval en lugar de json.loads para interpretar el mensaje
                    data = json.loads(sample.payload.to_string())
                    ax, ay, az = data['ax'], data['ay'], data['az']
                    print(f"{data},{ax},{ay},{az}")
                    caida = detectar_caida(ax, ay, az)
                    pub.put(str(caida))
                    if caida == 1:
                        print("¡Fall detected!")
                except Exception as e:
                    print(f"Error processing message: {e}")

            session.declare_subscriber(env_input, listener)
            print("Declared subscriber.")

            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="detectar_caida",
        description="Listen to accelerometer data and detect falls."
    )
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    print(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config_json)
    main(conf)
