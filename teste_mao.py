import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time

def process_camera(frame_queue):
    camera = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    while True:
        success, frame = camera.read()
        if not success:
            continue

        # frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        if frame_queue.full():
            frame_queue.get()  # Remove old frame to prevent lag
        frame_queue.put(frame)


def pygame_loop(frame_queue):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for FPS display

    running = True
    while running:
        start_time = time.time()  # Start frame time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            screen.blit(frame, (0, 0))

        # Calculate FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)  # Set target FPS to 60

    pygame.quit()


if __name__ == "__main__":
    frame_queue = mp_proc.Queue(maxsize=1)  # Limit queue size to prevent lag
    camera_process = mp_proc.Process(target=process_camera, args=(frame_queue,))
    camera_process.start()
    
    pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue,))
    pygame_thread.start()
    
    pygame_thread.join()
    camera_process.terminate()
