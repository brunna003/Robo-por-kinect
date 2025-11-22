#BIBLIOTECAS NECESSÁRIAS:

#pip install numpy
#pip install opencv-python
#pip install mediapipe
#pip install pykinect2 (pego do github, a do vscode é desatualizada)






import sys
import math
import numpy as np
import cv2
import mediapipe as mp
import socket
import time
from Database import inicializar_banco, salvar_gesto

# --- CONFIGURAÇÃO DO SERVIDOR ESP32 ---
ESP32_IP = "192.168.41.122"  # <-- Substitua pelo IP mostrado no monitor serial do ESP32
ESP32_PORT = 8080

# --- Inicializa o socket ---
try:
    esp32 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    esp32.connect((ESP32_IP, ESP32_PORT))
    print(f"Conectado ao ESP32 em {ESP32_IP}:{ESP32_PORT}")
except Exception as e:
    print("Falha ao conectar ao ESP32:", e)
    esp32 = None

# --- Importa o Kinect ---
try:
    from pykinect2 import PyKinectV2
    from pykinect2 import PyKinectRuntime
except Exception as e:
    print("Erro importando pykinect2:", e)
    sys.exit(1)

# --- Inicializa o MediaPipe ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def detectar_gesto(hand_landmarks):
    dedos = [(8,6),(12,10),(16,14),(20,18)]
    polegar = (4,2)
    dedos_estendidos = 0
    for tip, pip in dedos:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            dedos_estendidos += 1
    thumb_tip = hand_landmarks.landmark[polegar[0]]
    thumb_ip = hand_landmarks.landmark[polegar[1]]
    wrist = hand_landmarks.landmark[0]
    polegar_estendido = thumb_tip.x < wrist.x if thumb_tip.y < wrist.y else thumb_tip.x > wrist.x

    if dedos_estendidos == 0 and not polegar_estendido:
        return "Fechada"
    elif dedos_estendidos == 4 and polegar_estendido:
        return "Aberta"
    elif dedos_estendidos == 1 and not polegar_estendido:
        return "Um dedo"
    elif dedos_estendidos == 2 and not polegar_estendido:
        return "Dois dedos"
    elif dedos_estendidos == 0 and polegar_estendido:
        return "Joinha"
    else:
        return None

def main():
    print("Inicializando Kinect...")
    inicializar_banco()
    kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
    print("Kinect iniciado. Pressione ESC para sair.")

    with mp_hands.Hands(max_num_hands=1,
                        min_detection_confidence=0.6,
                        min_tracking_confidence=0.5) as hands:
        while True:
            if kinect.has_new_color_frame():
                frame = kinect.get_last_color_frame()
                w, h = kinect.color_frame_desc.Width, kinect.color_frame_desc.Height
                color_img = frame.reshape((h, w, 4)).astype(np.uint8)
                frame_bgr = color_img[:, :, :3].copy()

                image_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                results = hands.process(image_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        gesto = detectar_gesto(hand_landmarks)
                        if gesto:
                            print("Gesto detectado:", gesto)
                            salvar_gesto(gesto)
                            if esp32:
                                try:
                                    esp32.sendall((gesto + "\n").encode('utf-8'))
                                except Exception as e:
                                    print("Erro ao enviar gesto:", e)
                            cv2.putText(frame_bgr, gesto, (50, 80),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                cv2.imshow("Kinect + MediaPipe - Gestos", frame_bgr)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    kinect.close()
    cv2.destroyAllWindows()
    if esp32:
        esp32.close()
    print("Encerrado.")

if __name__ == '__main__':
    main()

