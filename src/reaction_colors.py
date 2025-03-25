import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time

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

        # Create a list to store hand landmarks
        hand_landmarks_list = []
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract landmark coordinates and add to list
                landmarks = []
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    # Convert normalized coordinates to pixel coordinates
                    h, w, _ = frame.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmarks.append((landmark.x, landmark.y))  # Store normalized coordinates
                
                hand_landmarks_list.append(landmarks)
        
        # Pass hand landmarks to pygame process
        if hand_position_queue.full():
            hand_position_queue.get()  # Remove old data
        hand_position_queue.put(hand_landmarks_list)
        
        if frame_queue.full():
            frame_queue.get()  # Remove old frame to prevent lag
        frame_queue.put(frame)

def pygame_loop(frame_queue, hand_position_queue):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()  # Get the actual screen dimensions
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for FPS display

    # Initialize colors
    red = (255, 0, 0)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    
    # Initialize square default variables
    default_square_size = 150
    default_square_color = red
    default_hover_square_color = green
    squares = []

    # Define squares on each side
    squares.append({
        "name": "TopLeft",
        "x": 50,
        "y": 50,
        "size": default_square_size,
        "color": default_square_color
    })

    for square in squares:
        square['draw'] = pygame.Rect(square["x"], square["y"], square["size"], square["size"])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break
        
        # Check hand positions
        if not hand_position_queue.empty():
            hand_landmarks_list = hand_position_queue.get()
            hover = []
            for landmarks in hand_landmarks_list:
                x1, y1 = landmarks[8]  # Index finger tip
                x1 = int((1.0 - x1) * screen_width)
                y1 = int(y1 * screen_height)

                # x2, y2 = landmarks[]
                # x2 = int((1.0 - x) * screen_width)
                # y2 = int(y * screen_height)
                for square in squares:
                    if square['draw'].collidepoint(x1, y1) and square['name'] not in hover:
                        hover.append(square['name'])
                        square["color"] = default_hover_square_color
                    elif square['name'] not in hover:
                        square["color"] = default_square_color

            
        
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            # Scale the camera feed to fill the entire screen
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            screen.blit(frame, (0, 0))
        
        # Draw squares
        for square in squares:
            pygame.draw.rect(screen, square['color'], square['draw'])

        # Calculate FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        pygame.display.flip()
        clock.tick(120)  # Set target FPS to 60

    pygame.quit()



def main():
    pygame.init()
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    pygame.quit()

    frame_queue = mp_proc.Queue(maxsize=1)  # Limit queue size to prevent lag
    hand_position_queue = mp_proc.Queue(maxsize=1)  # Queue to share hand positions
    
    camera_process = mp_proc.Process(target=process_camera, args=(frame_queue, hand_position_queue, width, height))
    camera_process.start()
    
    pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue, hand_position_queue))
    pygame_thread.start()
    
    pygame_thread.join()
    camera_process.terminate()
    
if __name__ == "__main__":
    main()