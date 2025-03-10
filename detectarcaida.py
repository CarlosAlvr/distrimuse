import time
import zenoh
import common
import argparse
import os

def detectar_caida(ax, ay, az):
    """
    Detecta una caída basándose en los valores de aceleración.
    """
    umbral_min = 3.0  # Umbral mínimo de aceleración brusca indicando caída libre
    umbral_max = 12.0 # Umbral máximo que puede indicar un impacto
    aceleracion_total = (ax**2 + ay**2 + az**2) ** 0.5
    
    # Detecta una caída si la aceleración cae por debajo del umbral mínimo y luego sube bruscamente
    if aceleracion_total < umbral_min or aceleracion_total > umbral_max:
        return 1
    return 0

def main(conf: zenoh.Config):
    """
    Escucha datos de acelerómetro y publica detección de caídas.
    """
    zenoh.init_log_from_env_or("error")
    with zenoh.open(conf) as session:
        pub = session.declare_publisher("casa/persona1/caida")
        
        def listener(sample: zenoh.Sample):
            data = eval(sample.payload.to_string())
            ax, ay, az = data['ax'], data['ay'], data['az']
            caida = detectar_caida(ax, ay, az)
            pub.put(str(caida))
            if caida == 1:
                os.system("echo ¡Caída detectada!")
        
        session.declare_subscriber("casa/persona1/acelerometro", listener)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Saliendo...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="detectar_caida", description="Escucha datos del acelerómetro y detecta caídas.")
    common.add_config_arguments(parser)
    args = parser.parse_args()
    conf = common.get_config_from_args(args)
    main(conf)
