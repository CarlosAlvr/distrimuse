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
                print(f"No camera found in the index: {i}")
        except Exception as e:
            print(f"Error trying to open the camera in the index {i}: {e}")
            # Continues with the next one
            pass

    if camera_id is None:
        print("No cameras available.")
    else:
        print(f"Using the camera on the index finger: {camera_id}")
    

    with zenoh.open(conf) as session:
        env_input = os.environ.get('DISTRIMUSE_INPUT_0')
        if env_input is None:
            os.system("Error: The environment variable 'Distrimuse_input_0' is not defined.")
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os.system("Error: The environment variable 'Distrimuse_output_0' is not defined.")
            
        print(f"The defined inputs -> outputs are: {env_input} -> {env_output}")
       
        pub_video = session.declare_publisher(env_output)
        
        
        cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)  

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        def listener_caida(sample: zenoh.Sample):
            
            fall_detected = int(sample.payload.to_string())
            if fall_detected == 1:
                print("A fall has been detected. Capturing and sending a video frame.")
                
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame from camera.")
                    return
                
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                pub_video.put(frame_data)
                print(f"Published on {env_output} processed video frame.")

        
        session.declare_subscriber(env_input, listener_caida)
        print("Waiting for a fall detection...")
        try:
            while True:
                time.sleep(1)  
        except KeyboardInterrupt:
            print("Exiting...")
        
        cap.release()

# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse
    import common

    parser = argparse.ArgumentParser(
        prog="videoSensor",
        description="Listen for fall detection and send video frames."
    )
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    print(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config)
    main(conf)
