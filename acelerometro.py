import time
import numpy as np
import zenoh
import common
import argparse
import os
def generar_aceleracion():
    """
    Genera datos simulados de aceleración en los ejes X, Y, Z.
    """
    ax = np.sin(time.time()) + np.random.uniform(-4, 4)
    ay = np.cos(time.time()) + np.random.uniform(-4, 4)
    az = 9.8 + np.random.uniform(-3, 3)  # Simula la gravedad en el eje Z
    return ax, ay, az

def main(conf: zenoh.Config):
    zenoh.init_log_from_env_or("error")
    with zenoh.open(conf) as session:
        env_input = os.getenv("Distrimuse_input_0")
        if env_input is None:
            os.system("Error: La variable de entorno 'Distrimuse_input_0' no está definida.")
        pub = session.declare_publisher(env_input)
        os.system("echo Publicando datos de acelerómetro cada segundo...")
        
        try:
            while True:
                ax, ay, az = generar_aceleracion()
                data = f"{{'ax': {ax:.2f}, 'ay': {ay:.2f}, 'az': {az:.2f}}}"
                pub.put(data)
                os.system(f"echo Publicado: {data}")
                time.sleep(1)
        except KeyboardInterrupt:
            os.system("echo Saliendo...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="simulador_acelerometro", description="Publica datos simulados de acelerómetro.")
    common.add_config_arguments(parser)
    args = parser.parse_args()
    conf = common.get_config_from_args(args)
    main(conf)
