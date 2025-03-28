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
    sounds = [{"sound" : left_sound,"squareName": "Left"},{"sound":right_sound, "squareName": "Right"}]
    sound = random.choice(sounds)
    sound["sound"].play()
    return sound['squareName']

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

    elapsed_time = 0

    has_userRemovedHands = False
    is_gameRunning = False

    handToRemove = ""
    tryNumber = 0

    has_won = has_lose = False

    running = True
    while running:

		# Timer logic
        if start_time is not None:
            elapsed_time = time.time() - start_time  # Timer counting

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

            # Check if both hands are hovering over the squares
            if all(square["color"] == default_hover_square_color for square in squares) and not countdown_active:
                if not is_gameRunning:
                    countdown_active = True
                    countdown_start_time = time.time()
                    has_lose = has_won = False
                has_userRemovedHands = False
            else:
                if handToRemove is not "":  # Check if handToRemove is not empty
                    removed_square = next((square for square in squares if square["name"] == handToRemove), None)
                    other_squares = [square for square in squares if square["name"] != handToRemove]
                    if removed_square["color"] == default_square_color and all(square["color"] == default_hover_square_color for square in other_squares):
                        start_time = None  # stops the running timer
                        handToRemove = ""
                        tryNumber += 1
                        is_gameRunning = False
                        has_won = True
                    else:
                        start_time = None
                        handToRemove = ""
                        is_gameRunning = False
                        has_lose = True
                elif all(square["color"] == default_square_color for square in squares) and countdown_active:  # checks if user removed hands from squares
                    has_userRemovedHands = True
                    countdown_active = False
                    countdown_active = False

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

		#Game mechanics

        # Draw starting Timer (CENTER)
        timer_text = timer_font.render(f"{elapsed_time:.1f} s", True, white)
        timer_rect = timer_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
        screen.blit(timer_text, timer_rect)

        instruction_text = "Coloque as mãos sobre os quadrados para começar!"
        # Instruction text
        if countdown_active:
            instruction_text = "De onde ouvir o som retire a mão!"
        elif has_userRemovedHands:
            instruction_text = "Não retire as mãos dos quadrados!"

        instruction = font.render(instruction_text, True, white)
        screen.blit(instruction, (screen_width // 2 - instruction.get_width() // 2, 20))

        # Draw Win / Lose message
        if has_won:
            win_text = font.render("Você ganhou!", True, green)
            screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2, screen_height // 2))
        elif has_lose:
            lose_text = font.render("Você perdeu! Tente novamente!", True, red)
            screen.blit(lose_text, (screen_width // 2 - lose_text.get_width() // 2, screen_height // 2))

        # Countdown logic
        if countdown_active:
            countdown_remaining = max(0, countdown - int(time.time() - countdown_start_time))

            if countdown_remaining == 0:
                countdown_active = False
                start_time = time.time()  # Start the main timer once countdown finishes
                handToRemove = play_random_sound()  # Toca o som aleatório aqui e devolve qual mão a remover do quadrado
                is_gameRunning = True
            else:
                countdown_text = timer_font.render(f"{countdown_remaining}", True, white)
                countdown_rect = countdown_text.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(countdown_text, countdown_rect)
            

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



