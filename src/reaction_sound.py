import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time
import random
import subprocess  # Para chamar o resSound.py
import sys

pygame.init()
pygame.mixer.init()
left_sound = pygame.mixer.Sound("assets/musics/Left.mp3")
right_sound = pygame.mixer.Sound("assets/musics/Right.mp3")

def play_random_sound():
    sounds = [{"sound": left_sound, "squareName": "Left"}, {"sound": right_sound, "squareName": "Right"}]
    sound = random.choice(sounds)
    sound["sound"].play()
    return sound['squareName']

def process_camera(frame_queue, hand_position_queue, width, height, stop_event):
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    while not stop_event.is_set():
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
                    landmarks.append((landmark.x, landmark.y))
                hand_landmarks_list.append(landmarks)

        if hand_position_queue.full():
            hand_position_queue.get()
        hand_position_queue.put(hand_landmarks_list)

        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(frame)

    camera.release()  # Libera a câmera antes de encerrar o processo


def pygame_loop(frame_queue, hand_position_queue, stop_event):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    timer_font = pygame.font.Font(None, 100)

    # Variáveis para controle do timer
    start_time = None  # Timer não iniciado ainda

    # Cores
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

    # Variáveis para contagem regressiva
    countdown_active = False
    countdown = 5  # Inicia com 5 segundos

    elapsed_time = 0

    has_userRemovedHands = False
    is_gameRunning = False

    handToRemove = ""
    tryNumber = 0
    max_rounds = 5  # Número máximo de rodadas
    round_times = []  # Armazena o tempo de cada rodada

    has_won = has_lose = False

    running = True
    while running:

        # Lógica do timer
        if start_time is not None:
            elapsed_time = time.time() - start_time  # Atualiza o tempo decorrido

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        if not hand_position_queue.empty():
            hand_landmarks_list = hand_position_queue.get()
            hover = []
            for landmarks in hand_landmarks_list:
                x1, y1 = landmarks[8]  # Ponta do dedo indicador
                x1 = int((1.0 - x1) * screen_width)
                y1 = int(y1 * screen_height)

                for square in squares:
                    if square['draw'].collidepoint(x1, y1) and square['name'] not in hover:
                        hover.append(square['name'])
                        square["color"] = default_hover_square_color
                    elif square['name'] not in hover:
                        square["color"] = default_square_color

            # Verifica se as duas mãos estão sobre os quadrados para iniciar a contagem
            if all(square["color"] == default_hover_square_color for square in squares) and not countdown_active:
                if not is_gameRunning:
                    countdown_active = True
                    countdown_start_time = time.time()
                    has_lose = has_won = False
                has_userRemovedHands = False
            else:
                if handToRemove != "":  # Verifica se há um quadrado para remover
                    removed_square = next((square for square in squares if square["name"] == handToRemove), None)
                    other_squares = [square for square in squares if square["name"] != handToRemove]
                    if removed_square and removed_square["color"] == default_square_color and all(square["color"] == default_hover_square_color for square in other_squares):
                        # Vitória: o tempo da rodada é o tempo decorrido
                        round_time = elapsed_time
                        has_won = True
                    else:
                        # Derrota: o tempo da rodada é fixado em 5 segundos
                        round_time = 5.0
                        has_lose = True
                    start_time = None  # Para o timer
                    handToRemove = ""
                    tryNumber += 1
                    is_gameRunning = False
                    round_times.append(round_time)
                    # Se atingir o número máximo de rodadas, calcula a média e chama resSound.py
                    # Dentro da função pygame_loop, no bloco onde tryNumber >= max_rounds:
                    if tryNumber >= max_rounds:
                        avg_time = sum(round_times) / max_rounds
                        pygame.quit()
                        subprocess.call(['python', 'src/resSound.py', str(avg_time)])
                        running = False  # Remove sys.exit() e define running como False para sair do loop
                elif all(square["color"] == default_square_color for square in squares) and countdown_active:  # Checa se o usuário retirou as mãos
                    has_userRemovedHands = True
                    countdown_active = False

        # Desenhar tudo na tela
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            screen.blit(frame, (0, 0))

        # Desenhar os quadrados
        for square in squares:
            pygame.draw.rect(screen, square['color'], square['draw'])

        # Desenhar FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        # Lógica do timer principal (CENTRAL)
        timer_text = timer_font.render(f"{elapsed_time:.1f} s", True, white)
        timer_rect = timer_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
        screen.blit(timer_text, timer_rect)

        instruction_text = "Coloque as mãos sobre os quadrados para começar!"
        # Instrução de acordo com a situação
        if countdown_active:
            instruction_text = "De onde ouvir o som, retire a mão!"
        elif has_userRemovedHands:
            instruction_text = "Não retire as mãos dos quadrados!"

        instruction = font.render(instruction_text, True, white)
        screen.blit(instruction, (screen_width // 2 - instruction.get_width() // 2, 20))

        # Mensagens de Vitória / Derrota
        if has_won:
            win_text = font.render("Você acertou.", True, green)
            screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2, screen_height // 2))
        elif has_lose:
            lose_text = font.render("Você errou. Tempo adicionado de +5s.", True, red)
            screen.blit(lose_text, (screen_width // 2 - lose_text.get_width() // 2, screen_height // 2))

        # Exibe label com o número de rodadas jogadas e, se já tiver 5, a média
        rounds_label = font.render(f"Rodada: {tryNumber} / 5", True, white)
        screen.blit(rounds_label, (10, 50))
        if tryNumber >= max_rounds:
            avg_time = sum(round_times) / max_rounds
            pygame.quit()
            stop_event.set()
            subprocess.call(['python', 'src/resSound.py', str(avg_time)])
            running = False
            
        # Lógica da contagem regressiva
        if countdown_active:
            countdown_remaining = max(0, countdown - int(time.time() - countdown_start_time))

            if countdown_remaining == 0:
                countdown_active = False
                start_time = time.time()  # Inicia o timer principal após a contagem
                handToRemove = play_random_sound()  # Toca o som e retorna o quadrado que deverá ser removido
                is_gameRunning = True
            else:
                countdown_text = timer_font.render(f"{countdown_remaining}", True, white)
                countdown_rect = countdown_text.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(countdown_text, countdown_rect)

        pygame.display.flip()
        clock.tick(120)  # Máximo FPS se possível

    pygame.quit()

def main():
    pygame.init()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    pygame.quit()

    frame_queue = mp_proc.Queue(maxsize=1)
    hand_position_queue = mp_proc.Queue(maxsize=1)
    stop_event = mp_proc.Event()

    camera_process = mp_proc.Process(target=process_camera, args=(frame_queue, hand_position_queue, width, height, stop_event))
    camera_process.start()

    pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue, hand_position_queue, stop_event))
    pygame_thread.start()

    pygame_thread.join()
    stop_event.set()  # Sinaliza para o processo da câmera encerrar
    camera_process.join()


if __name__ == "__main__":
    main()
