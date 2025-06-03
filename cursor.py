import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# --- Configurações e Inicializações ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# OpenCV - Captura de Vídeo
wCam, hCam = 1280, 720
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()
cap.set(3, wCam)
cap.set(4, hCam)

# PyAutoGUI
screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = False

# --- Variáveis para Controle e Suavização ---
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# --- Constantes para os dedos (Landmark IDs) ---
THUMB_TIP_ID = 4
INDEX_FINGER_TIP_ID = 8
INDEX_FINGER_PIP_ID = 6  # Junta Proximal Interfalangeana do Indicador
MIDDLE_FINGER_TIP_ID = 12
MIDDLE_FINGER_PIP_ID = 10  # Junta Proximal Interfalangeana do Médio
RING_FINGER_TIP_ID = 16
RING_FINGER_PIP_ID = 14  # Junta Proximal Interfalangeana do Anelar
PINKY_TIP_ID = 20
PINKY_PIP_ID = 18  # Junta Proximal Interfalangeana do Mínimo

# --- Variáveis para controle de clique ---
CLICK_COOLDOWN_TIME = 0.5
last_left_click_time = 0
last_right_click_time = 0
left_click_active = False

# --- Variáveis para controle de Rolagem ---
scroll_mode_active = False
previous_scroll_mid_y = 0
SCROLL_SENSITIVITY = 30  # Quantidade de rolagem (ajuste conforme necessário)
SCROLL_ACTIVATION_THRESHOLD_Y = 15  # Movimento vertical mínimo para ativar rolagem (em pixels da câmera)
FINGERS_CLOSE_THRESHOLD_X_SCROLL = 60  # Distância horizontal máxima entre indicador e médio para scroll
FINGER_EXTENDED_THRESHOLD_FACTOR = 0.8  # Fator para considerar dedo esticado (ponta_y < pip_y * FATOR)

# --- Loop Principal ---
try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignorando frame vazio da câmera.")
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Resetar estado de rolagem se nenhuma mão for detectada
        if not results.multi_hand_landmarks:
            if scroll_mode_active:
                scroll_mode_active = False
                # print("Scroll mode DEACTIVATED (no hand)")
            left_click_active = False

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                landmarks = hand_landmarks.landmark

                # Coordenadas dos dedos para MOVIMENTO e CLIQUE
                ix_tip, iy_tip = int(landmarks[INDEX_FINGER_TIP_ID].x * wCam), int(
                    landmarks[INDEX_FINGER_TIP_ID].y * hCam)
                tx_tip, ty_tip = int(landmarks[THUMB_TIP_ID].x * wCam), int(landmarks[THUMB_TIP_ID].y * hCam)
                mx_tip, my_tip = int(landmarks[MIDDLE_FINGER_TIP_ID].x * wCam), int(
                    landmarks[MIDDLE_FINGER_TIP_ID].y * hCam)

                # Coordenadas para checar se dedos estão ESTICADOS ou CURVADOS (para gesto de rolagem)
                # (Comparando a posição Y da ponta com a junta PIP)
                index_tip_y = landmarks[INDEX_FINGER_TIP_ID].y
                index_pip_y = landmarks[INDEX_FINGER_PIP_ID].y
                middle_tip_y = landmarks[MIDDLE_FINGER_TIP_ID].y
                middle_pip_y = landmarks[MIDDLE_FINGER_PIP_ID].y
                ring_tip_y = landmarks[RING_FINGER_TIP_ID].y
                ring_pip_y = landmarks[RING_FINGER_PIP_ID].y
                pinky_tip_y = landmarks[PINKY_TIP_ID].y
                pinky_pip_y = landmarks[PINKY_PIP_ID].y

                # Verifica se os dedos estão esticados (ponta acima da junta PIP)
                # Um dedo está esticado se a coordenada Y da ponta for MENOR que a da junta PIP
                index_extended = index_tip_y < index_pip_y
                middle_extended = middle_tip_y < middle_pip_y
                # Verifica se os dedos estão curvados (ponta abaixo ou na mesma altura da junta PIP)
                ring_curled = ring_tip_y > ring_pip_y * FINGER_EXTENDED_THRESHOLD_FACTOR
                pinky_curled = pinky_tip_y > pinky_pip_y * FINGER_EXTENDED_THRESHOLD_FACTOR

                # Distância horizontal entre ponta do indicador e médio
                dist_index_middle_x = abs(landmarks[INDEX_FINGER_TIP_ID].x - landmarks[MIDDLE_FINGER_TIP_ID].x) * wCam

                # --- LÓGICA DE DETECÇÃO DE MODO (ROLAGEM ou CURSOR/CLIQUE) ---
                # Gesto para MODO ROLAGEM: Indicador e Médio esticados e próximos, Anelar e Mínimo curvados
                is_scroll_gesture = (index_extended and middle_extended and
                                     ring_curled and pinky_curled and
                                     dist_index_middle_x < FINGERS_CLOSE_THRESHOLD_X_SCROLL)

                if is_scroll_gesture:
                    cv2.putText(image, "MODO ROLAGEM", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2,
                                cv2.LINE_AA)
                    # Ponto central entre indicador e médio para rolagem
                    current_scroll_mid_y = (landmarks[INDEX_FINGER_TIP_ID].y + landmarks[
                        MIDDLE_FINGER_TIP_ID].y) / 2 * hCam
                    cv2.circle(image,
                               (int((landmarks[INDEX_FINGER_TIP_ID].x + landmarks[MIDDLE_FINGER_TIP_ID].x) / 2 * wCam),
                                int(current_scroll_mid_y)), 10, (0, 255, 255), cv2.FILLED)

                    if not scroll_mode_active:  # Acabou de entrar no modo rolagem
                        scroll_mode_active = True
                        previous_scroll_mid_y = current_scroll_mid_y  # Inicializa Y anterior
                        # print("Modo Rolagem ATIVADO")
                    else:  # Já está no modo rolagem, verifica movimento
                        delta_y = current_scroll_mid_y - previous_scroll_mid_y
                        # print(f"Delta Y Rolagem: {delta_y}") # Para debug

                        if abs(delta_y) > SCROLL_ACTIVATION_THRESHOLD_Y:
                            if delta_y > 0:  # Dedos moveram PARA BAIXO na tela -> Rolar página PARA BAIXO
                                pyautogui.scroll(-SCROLL_SENSITIVITY)
                                # print(f"Scroll Para Baixo: {-SCROLL_SENSITIVITY}")
                            else:  # Dedos moveram PARA CIMA na tela -> Rolar página PARA CIMA
                                pyautogui.scroll(SCROLL_SENSITIVITY)
                                # print(f"Scroll Para Cima: {SCROLL_SENSITIVITY}")
                            previous_scroll_mid_y = current_scroll_mid_y  # Atualiza Y após rolagem

                else:  # Não é o gesto de rolagem -> MODO CURSOR/CLIQUE
                    if scroll_mode_active:  # Se estava no modo rolagem, desativa
                        scroll_mode_active = False
                        # print("Modo Rolagem DESATIVADO (gesto mudou)")

                    cv2.putText(image, "MODO CURSOR", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2,
                                cv2.LINE_AA)
                    # Desenha círculos nos dedos de controle
                    cv2.circle(image, (ix_tip, iy_tip), 10, (255, 0, 255), cv2.FILLED)  # Indicador
                    cv2.circle(image, (tx_tip, ty_tip), 10, (255, 0, 0), cv2.FILLED)  # Polegar
                    cv2.circle(image, (mx_tip, my_tip), 10, (0, 255, 0), cv2.FILLED)  # Médio

                    # --- Mapeamento de Coordenadas e Movimento do Mouse ---
                    frame_reduction = 100
                    screen_x = np.interp(ix_tip, (frame_reduction, wCam - frame_reduction), (0, screen_width))
                    screen_y = np.interp(iy_tip, (frame_reduction, hCam - frame_reduction), (0, screen_height))

                    clocX = plocX + (screen_x - plocX) / smoothening
                    clocY = plocY + (screen_y - plocY) / smoothening

                    final_screen_x = max(0, min(screen_width - 1, clocX))
                    final_screen_y = max(0, min(screen_height - 1, clocY))
                    pyautogui.moveTo(final_screen_x, final_screen_y)
                    plocX, plocY = clocX, clocY

                    # --- Detecção de Clique ---
                    distance_left_click = np.sqrt((tx_tip - ix_tip) ** 2 + (ty_tip - iy_tip) ** 2)
                    current_time = time.time()

                    if distance_left_click < 40:
                        if not left_click_active and (current_time - last_left_click_time > CLICK_COOLDOWN_TIME):
                            pyautogui.click(button='left')
                            # print("Clique Esquerdo!")
                            cv2.circle(image, (ix_tip, iy_tip), 15, (0, 255, 0), cv2.FILLED)
                            last_left_click_time = current_time
                            left_click_active = True
                    else:
                        left_click_active = False

                    distance_right_click = np.sqrt((tx_tip - mx_tip) ** 2 + (ty_tip - my_tip) ** 2)
                    if distance_right_click < 40:
                        if current_time - last_right_click_time > CLICK_COOLDOWN_TIME:
                            pyautogui.click(button='right')
                            # print("Clique Direito!")
                            cv2.circle(image, (mx_tip, my_tip), 15, (0, 0, 255), cv2.FILLED)
                            last_right_click_time = current_time

        cv2.imshow("Controle de Cursor com Mao", image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Programa interrompido pelo usuário.")
finally:
    print("Encerrando...")
    cap.release()
    cv2.destroyAllWindows()
    hands.close()