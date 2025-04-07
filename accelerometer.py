import time
import numpy as np
import zenoh
import common
import argparse
import os
import json

def acceleration():
    # This is the simulator of an accelerometer 
    ax = np.sin(time.time()) + np.random.uniform(-4, 4)
    ay = np.cos(time.time()) + np.random.uniform(-4, 4)
    az = 9.8 + np.random.uniform(-3, 3)  # Simulates gravity 
    return ax, ay, az

def main(conf):
    zenoh.init_log_from_env_or("error")
    with zenoh.open(conf) as session:
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os.system("Error: The environment variable 'Distrimuse_output_0' is not defined.")
        os.system(f"The input variable is: {env_output}")
        pub = session.declare_publisher(env_output)
        os.system("Publishing accelerometer data every second...")
        
        try:
            while True:
                ax, ay, az = acceleration()
                data = json.dumps({'X axis': round(ax, 2), 'Y axis': round(ay, 2), 'Z axis': round(az, 2)})
                pub.put(data)
                os.system(f"The data pubished is: {data}")
                time.sleep(1)
        except KeyboardInterrupt:
            os.system("The app is closing...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="simulador_acelerometro", description="Publishes simulated accelerometer data.")
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    os.system(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config)
    main(conf)
