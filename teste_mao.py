import cv2
import mediapipe as mp 
import time

camera = cv2.VideoCapture(0)
mpMaos = mp.solutions.hands
maos   = mpMaos.Hands()
mpDesenho = mp.solutions.drawing_utils

tic = 0
tac = 0
# cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("Camera", 800, 600)

# while True:
#     sucesso, imagem = camera.read()
#     imagemRGB = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
#     resultados = maos.process(imagemRGB)
    
#     imagem = cv2.flip(imagem, 1)
    
#     if resultados.multi_hand_landmarks:
#         for maosPntRef in resultados.multi_hand_landmarks:
#             mpDesenho.draw_landmarks(imagem, maosPntRef, mpMaos.HAND_CONNECTIONS)
    
#     tac = time.time()
#     fps = 1/(tac-tic)
#     tic = tac

#     cv2.putText(imagem, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 3)

#     cv2.imshow("Camera", imagem)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break


while True:
	sucesso, imagem = camera.read()
	imagemRGB = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
	resultados = maos.process(imagemRGB)
	
	imagem = cv2.flip(imagem, 1)
	
	cv2.imshow("Camera", imagem)
	
	if resultados.multi_hand_landmarks:
		for maosPntRef in resultados.multi_hand_landmarks:
			# Flip the hand landmarks horizontally
			for ponto in maosPntRef.landmark:
				ponto.x = 1 - ponto.x
			mpDesenho.draw_landmarks(imagem, maosPntRef, mpMaos.HAND_CONNECTIONS)
	
	tac = time.time()
	fps = 1/(tac-tic)
	tic = tac

	cv2.putText(imagem, str(int(fps)), (5,35), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 3)

	# Define the square's position and size
	square_top_left = (50, 50)
	square_bottom_right = (150, 150)
	square_color = (0, 0, 255)  # Red

	# Check if the index finger is over the square
	if resultados.multi_hand_landmarks:
		for maosPntRef in resultados.multi_hand_landmarks:
			index_finger_tip = maosPntRef.landmark[mpMaos.HandLandmark.INDEX_FINGER_TIP]
			x, y = int(index_finger_tip.x * imagem.shape[1]), int(index_finger_tip.y * imagem.shape[0])
			if square_top_left[0] <= x <= square_bottom_right[0] and square_top_left[1] <= y <= square_bottom_right[1]:
				square_color = (0, 255, 0)  # Green
				break  # No need to check other hands if one is already over the square
		else:
			square_color = (0, 0, 255)  # Red
	else:
		square_color = (0, 0, 255)  # Red

	# Draw the square
	cv2.rectangle(imagem, square_top_left, square_bottom_right, square_color, -1)

	cv2.imshow("Camera", imagem)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break