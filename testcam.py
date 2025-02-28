import cv2

for i in range(5):  # Prueba los primeros 5 índices de cámara
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Cámara disponible en el índice: {i}")
        cap.release()
    else:
        print(f"No se encontró cámara en el índice: {i}")
