import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time
import random
import os
import subprocess
import sys

# Tempo máximo antes do quadrado mudar sozinho (em segundos)
SQUARE_LIFETIME = 1.0  

def process_camera(frame_queue, hand_position_queue, width, height, terminate_event):
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    try:
        while not terminate_event.is_set():
            success, frame = camera.read()
            if not success:
                continue

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            hand_landmarks_list = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.append((landmark.x, landmark.y))
                    hand_landmarks_list.append(landmarks)

            if hand_position_queue.full():
                hand_position_queue.get()
            hand_position_queue.put(hand_landmarks_list)

            if frame_queue.full():
                frame_queue.get()
            frame_queue.put(frame)
    finally:
        camera.release()
        cv2.destroyAllWindows()


def pygame_loop(frame_queue, hand_position_queue):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    red = (255, 0, 0)
    green = (0, 255, 0)

    default_square_size = 150
    default_square_color = red
    default_hover_square_color = green

    squares = [{
        "name": "TopLeft",
        "x": random.randint(0, screen_width - default_square_size),
        "y": random.randint(0, screen_height - default_square_size),
        "size": default_square_size,
        "color": default_square_color,
        "time": time.time()
    }]
    for square in squares:
        square['draw'] = pygame.Rect(square["x"], square["y"], square["size"], square["size"])

    score = 0
    combo = 0
    game_duration = 59  
    start_time = time.time()

    running = True
    while running:
        current_time = time.time()
        elapsed = current_time - start_time
        remaining_time = game_duration - elapsed

        if remaining_time <= 0:
            pygame.quit()
            os.execl(sys.executable, sys.executable, "src/resColors.py", str(score))
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        if not hand_position_queue.empty():
            hand_landmarks_list = hand_position_queue.get()
            for landmarks in hand_landmarks_list:
                x1, y1 = landmarks[8]
                x1 = int((1.0 - x1) * screen_width)
                y1 = int(y1 * screen_height)

                for square in squares:
                    if square['draw'].collidepoint(x1, y1):
                        if square["color"] != default_hover_square_color:
                            square["color"] = default_hover_square_color
                            square["time"] = time.time()
                            combo += 1
                            score += 1 * combo
                            square["x"] = random.randint(0, screen_width - square["size"])
                            square["y"] = random.randint(0, screen_height - square["size"])
                            square['draw'] = pygame.Rect(square["x"], square["y"], square["size"], square["size"])
                            square["color"] = default_square_color

        for square in squares:
            if current_time - square["time"] >= SQUARE_LIFETIME:
                combo = 0
                square["x"] = random.randint(0, screen_width - square["size"])
                square["y"] = random.randint(0, screen_height - square["size"])
                square["color"] = default_square_color
                square["time"] = time.time()
                square['draw'] = pygame.Rect(square["x"], square["y"], square["size"], square["size"])

        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            screen.blit(frame, (0, 0))

        for square in squares:
            pygame.draw.rect(screen, square['color'], square['draw'])

        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 50))

        combo_text = font.render(f"Combo: {combo}", True, (255, 255, 255))
        screen.blit(combo_text, (10, 90))

        timer_text = font.render(f"Time: {int(remaining_time)}", True, (255, 255, 255))
        screen.blit(timer_text, (screen_width - 150, 10))

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

def restart_camera(frame_queue, hand_position_queue, width, height, terminate_event):
    """
    Reinicia o processo da câmera.
    """
    terminate_event.set()  # Primeiro, termina o processo atual da câmera
    terminate_event.clear()  # Limpa o evento para reiniciar

    # Recria o processo da câmera
    camera_process = mp_proc.Process(
        target=process_camera,
        args=(frame_queue, hand_position_queue, width, height, terminate_event)
    )
    camera_process.start()
    return camera_process

def main():
    pygame.init()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    pygame.quit()

    frame_queue = mp_proc.Queue(maxsize=1)
    hand_position_queue = mp_proc.Queue(maxsize=1)
    terminate_event = mp_proc.Event()  # Evento para sinalizar o término

    # Reinicia a câmera ao iniciar
    camera_process = restart_camera(frame_queue, hand_position_queue, width, height, terminate_event)

    pygame_loop(frame_queue, hand_position_queue)

    # Sinaliza para o processo da câmera encerrar o loop e liberar o dispositivo
    terminate_event.set()
    camera_process.join()

if __name__ == "__main__":
    main()
