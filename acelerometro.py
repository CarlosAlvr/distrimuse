import time
import numpy as np
import zenoh
import common
import argparse
import os
import json

def generar_aceleracion():
    # This is the simulator of an accelerometer 
    ax = np.sin(time.time()) + np.random.uniform(-4, 4)
    ay = np.cos(time.time()) + np.random.uniform(-4, 4)
    az = 9.8 + np.random.uniform(-3, 3)  # Simulates gravity 
    return ax, ay, az

def main(conf: zenoh.Config):
    zenoh.init_log_from_env_or("error")
    with zenoh.open(conf) as session:
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os.system("Error: The environment variable 'Distrimuse_output_0' is not defined.")
        print(f"Input: {env_output}")
        pub = session.declare_publisher(env_output)
        os.system("echo Publishing accelerometer data every second...")
        
        try:
            while True:
                ax, ay, az = generar_aceleracion()
                data = json.dumps({'ax': round(ax, 2), 'ay': round(ay, 2), 'az': round(az, 2)})
                pub.put(data)
                os.system(f"echo Published: {data}")
                time.sleep(1)
        except KeyboardInterrupt:
            os.system("echo Exited...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="simulador_acelerometro", description="Publishes simulated accelerometer data.")
    common.add_config_arguments(parser)
    args = parser.parse_args()
    conf = common.get_config_from_args(args)
    main(conf)
