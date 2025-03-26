import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time
import random

pygame.init()
pygame.mixer.init()
left_sound = pygame.mixer.Sound("assets/musics/Left.mp3")
right_sound = pygame.mixer.Sound("assets/musics/Right.mp3")

def play_random_sound():
    sound = random.choice([left_sound, right_sound])
    sound.play()

def process_camera(frame_queue, hand_position_queue, width, height):
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    while True:
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
                    h, w, _ = frame.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmarks.append((landmark.x, landmark.y))  # Normalized
                hand_landmarks_list.append(landmarks)

        if hand_position_queue.full():
            hand_position_queue.get()
        hand_position_queue.put(hand_landmarks_list)

        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(frame)

def pygame_loop(frame_queue, hand_position_queue):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # FPS Font
    timer_font = pygame.font.Font(None, 100)  # Bigger font for Timer

    # Timer setup
    start_time = None  # Timer will not start yet
    timer_started = False  # Flag to control timer start

    # Colors
    red = (255, 0, 0)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    white = (255, 255, 255)

    default_square_size = 200
    default_square_color = red
    default_hover_square_color = green
    squares = [
        {"name": "Left", "x": 50, "y": (screen_height - default_square_size) // 2, "size": default_square_size, "color": default_square_color},
        {"name": "Right", "x": (screen_width - default_square_size) - 50, "y": (screen_height - default_square_size) // 2, "size": default_square_size, "color": default_square_color}
    ]

    for square in squares:
        square['draw'] = pygame.Rect(square["x"], square["y"], square["size"], square["size"])

    # Count down variables
    countdown_active = False
    countdown = 5  # Start at 5 seconds

    running = True
    while running:
        if start_time is not None:
            elapsed_time = time.time() - start_time  # Timer counting
        else:
            elapsed_time = 0  # If timer hasn't started yet

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        if not hand_position_queue.empty():
            hand_landmarks_list = hand_position_queue.get()
            hover = []
            for landmarks in hand_landmarks_list:
                x1, y1 = landmarks[8]  # Index finger tip
                x1 = int((1.0 - x1) * screen_width)
                y1 = int(y1 * screen_height)

                for square in squares:
                    if square['draw'].collidepoint(x1, y1) and square['name'] not in hover:
                        hover.append(square['name'])
                        square["color"] = default_hover_square_color
                    elif square['name'] not in hover:
                        square["color"] = default_square_color

            # Check if both squares are green
            if all(square["color"] == green for square in squares) and not countdown_active:
                countdown_active = True
                countdown_start_time = time.time()

        # Draw everything
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            screen.blit(frame, (0, 0))

        # Draw squares
        for square in squares:
            pygame.draw.rect(screen, square['color'], square['draw'])

        # Draw FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        # Draw Timer (CENTER)
        timer_text = timer_font.render(f"{elapsed_time:.1f} s", True, white)
        timer_rect = timer_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
        screen.blit(timer_text, timer_rect)

        # Display the instruction text
        instruction_text = font.render("Coloque as mãos nos quadrados", True, white)
        screen.blit(instruction_text, (screen_width // 2 - instruction_text.get_width() // 2, 20))

        # Countdown logic
        if countdown_active:
            countdown_remaining = max(0, countdown - int(time.time() - countdown_start_time))
            countdown_text = timer_font.render(f"{countdown_remaining}", True, white)
            countdown_rect = countdown_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(countdown_text, countdown_rect)

            if countdown_remaining == 0:
                countdown_active = False
                start_time = time.time()  # Start the main timer once countdown finishes
                play_random_sound()  # Toca o som aleatório aqui


        pygame.display.flip()
        clock.tick(120)  # High FPS if possible

    pygame.quit()


def main():
    pygame.init()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    pygame.quit()

    frame_queue = mp_proc.Queue(maxsize=1)
    hand_position_queue = mp_proc.Queue(maxsize=1)

    camera_process = mp_proc.Process(target=process_camera, args=(frame_queue, hand_position_queue, width, height))
    camera_process.start()

    pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue, hand_position_queue))
    pygame_thread.start()

    pygame_thread.join()
    camera_process.terminate()

if __name__ == "__main__":
    main()



