import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time


def process_camera(frame_queue, screen_size):
    camera = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    prev_time = time.time()

    while True:
        success, frame = camera.read()
        if not success:
            continue

        # Calcular FPS
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time))
        prev_time = curr_time

        # Processamento da mão
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Renderizar FPS no frame
        cv2.putText(frame, f"FPS: {fps}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Redimensionar frame para ocupar o ecrã inteiro
        frame = cv2.resize(frame, screen_size)

        if frame_queue.full():
            frame_queue.get()  # Remover o frame antigo para evitar lag
        frame_queue.put(frame)


def pygame_loop(frame_queue):
    pygame.init()
    
    # Configurar ecrã completo
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_size = screen.get_size()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            screen.blit(frame, (0, 0))

        pygame.display.flip()
        clock.tick(60)  # Definir FPS alvo para 60

    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    temp_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_size = temp_screen.get_size()
    pygame.quit()

    frame_queue = mp_proc.Queue(maxsize=1)  # Limitar o tamanho da fila para evitar lag
    camera_process = mp_proc.Process(target=process_camera, args=(frame_queue, screen_size))
    camera_process.start()
    
    pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue,))
    pygame_thread.start()
    
    pygame_thread.join()
    camera_process.terminate()
