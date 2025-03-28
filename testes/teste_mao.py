import cv2
import mediapipe as mp
import pygame
import numpy as np
import multiprocessing as mp_proc
import threading
import time

def process_camera(frame_queue, width, height):
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

		if results.multi_hand_landmarks:
			for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
				mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
		
		if frame_queue.full():
			frame_queue.get()  # Remove old frame to prevent lag
		frame_queue.put(frame)

def pygame_loop(frame_queue):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()  # Get the actual screen dimensions
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for FPS display

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                break

        # Remove the duplicate event processing loop
        
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            # Scale the camera feed to fill the entire screen
            frame = pygame.transform.scale(frame, (screen_width, screen_height))
            screen.blit(frame, (0, 0))

        # Calculate FPS
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)  # Set target FPS to 60

    pygame.quit()

def main():
	pygame.init()
	info = pygame.display.Info()
	width, height = info.current_w, info.current_h
	pygame.quit()

	frame_queue = mp_proc.Queue(maxsize=1)  # Limit queue size to prevent lag
	camera_process = mp_proc.Process(target=process_camera, args=(frame_queue, width, height))
	camera_process.start()
	
	pygame_thread = threading.Thread(target=pygame_loop, args=(frame_queue,))
	pygame_thread.start()
	
	pygame_thread.join()
	camera_process.terminate()

if __name__ == "__main__":
	main()