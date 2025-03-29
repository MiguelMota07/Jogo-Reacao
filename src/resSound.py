import pygame
import sys
import mysql.connector
import os

def insert_score(score, nome):
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="expocic"
        )
        cursor = conexao.cursor()
        sql = "INSERT INTO movimento (pontos, nome) VALUES (%s, %s)"
        cursor.execute(sql, (score, nome))
        conexao.commit()
        cursor.close()
        conexao.close()
    except Exception as e:
        print("Erro ao inserir no banco de dados:", e)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Resultado")
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    if len(sys.argv) < 2:
        print("Pontuação não informada!")
        sys.exit(1)
    score = sys.argv[1]
    
    input_box = pygame.Rect(300, 300, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    input_color = color_inactive
    active = False
    user_text = ""
    
    button_rect = pygame.Rect(300, 400, 200, 50)
    
    clock = pygame.time.Clock()
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                input_color = color_active if active else color_inactive
                
                if button_rect.collidepoint(event.pos):
                    insert_score(score, user_text)
                    os.system("python layoutIMSI.py")
                    done = True
            
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
        
        screen.fill((30, 30, 30))
        
        score_text = font_big.render("Score: " + str(score), True, pygame.Color('white'))
        screen.blit(score_text, (300, 100))
        
        txt_surface = font_small.render(user_text, True, input_color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, input_color, input_box, 2)
        
        pygame.draw.rect(screen, pygame.Color('green'), button_rect)
        button_text = font_small.render("Enviar", True, pygame.Color('black'))
        screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width())//2,
                                  button_rect.y + (button_rect.height - button_text.get_height())//2))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
