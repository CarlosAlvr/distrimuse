import time
import zenoh
import common
import argparse
import os
import json

def detectar_caida(ax, ay, az):
    """
    Detecta una caída basándose en los valores de aceleración.
    """
    umbral_min = 3.0  # Umbral mínimo de aceleración brusca indicando caída libre
    umbral_max = 12.0 # Umbral máximo que puede indicar un impacto
    aceleracion_total = (ax**2 + ay**2 + az**2) ** 0.5
    return 1 if aceleracion_total < umbral_min or aceleracion_total > umbral_max else 0

def main(conf: zenoh.Config):
    env_input = os.environ.get('DISTRIMUSE_INPUT_0')
    if env_input is None:
        print("Error: La variable de entorno 'DISTRIMUSE_INPUT_0' no está definida.")
        return

    env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
    if env_output is None:
        print("Error: La variable de entorno 'DISTRIMUSE_OUTPUT_0' no está definida.")
        return

    print(f"Entradas/salidas definidas: {env_input} -> {env_output}")

    # Inicializar el log de Zenoh
    zenoh.init_log_from_env_or("error")

    try:
        with zenoh.open(conf) as session:
            print("Sesión Zenoh iniciada.")

            # Declarar publisher y subscriber usando las variables de entorno
            pub = session.declare_publisher(env_output)
            print("Publicador declarado.")

            def listener(sample: zenoh.Sample):
                try:
                    # Usamos eval en lugar de json.loads para interpretar el mensaje
                    data = json.loads(sample.payload.to_string())
                    ax, ay, az = data['ax'], data['ay'], data['az']
                    print(f"{data},{ax},{ay},{az}")
                    caida = detectar_caida(ax, ay, az)
                    pub.put(str(caida))
                    if caida == 1:
                        print("¡Caída detectada!")
                except Exception as e:
                    print(f"Error procesando mensaje: {e}")

            session.declare_subscriber(env_input, listener)
            print("Subscriptor declarado.")

            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("Saliendo...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="detectar_caida",
        description="Escucha datos del acelerómetro y detecta caídas."
    )
    common.add_config_arguments(parser)
    args = parser.parse_args()
    conf = common.get_config_from_args(args)
    main(conf)
