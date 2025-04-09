import time
import cv2
import numpy as np
import zenoh
import os

def load_yolo_model():
    
    net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
    layer_names = net.getLayerNames()

   
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

    
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    return net, output_layers, classes

def detect_people(frame, net, output_layers, classes):
    height, width, _ = frame.shape

    
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (1280, 1280), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids, confidences, boxes = [], [], []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

           
            if classes[class_id] == "person" and confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    return len(indexes) > 0 if len(indexes) > 0 else False

def main(conf):
    
    net, output_layers, classes = load_yolo_model()

  
    zenoh.init_log_from_env_or("error")

 
    with zenoh.open(conf) as session:
        env_input = os.environ.get('DISTRIMUSE_INPUT_0')
        if env_input is None:
            os.system("echo Error: The environment variable 'Distrimuse_input_0' is not defined.")
        env_output = os.environ.get('DISTRIMUSE_OUTPUT_0')
        if env_output is None:
            os.system("echo Error: The environment variable 'Distrimuse_output_0' is not defined.")
            
        print(f"The defined inputs -> outputs are: {env_input} -> {env_output}")
        pub = session.declare_publisher(env_output)

        def listener(sample: zenoh.Sample):
        
            frame_data = sample.payload.to_bytes()
            np_arr = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is not None:
       
                detected = detect_people(frame, net, output_layers, classes)
                if detected: 
                    pub.put("1")
                    os.system("echo A person has been detected")

        session.declare_subscriber(env_input, listener)

        os.system("echo Press CTRL-C to quit...")
        while True:
            time.sleep(1)

# --- Command line argument parsing --- --- --- --- --- ---
if __name__ == "__main__":
    import argparse
    import common

    parser = argparse.ArgumentParser(
        prog="Recognice_fall", 
        description="Detect people in frames and publish detection status."
    )
   
    zenoh_config= os.environ.get('DISTRIMUSE_CONFIG')
    print(zenoh_config)
    conf = zenoh.Config.from_json5(zenoh_config)
    main(conf)
