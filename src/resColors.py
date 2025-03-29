import pygame
import sys
import mysql.connector
import subprocess

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
    # Tela em fullscreen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Resultado")
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Define fontes responsivas
    font_big = pygame.font.Font(None, int(screen_height * 0.1))
    font_small = pygame.font.Font(None, int(screen_height * 0.05))
    
    # Recebe a pontuação via linha de comando
    if len(sys.argv) < 2:
        print("Pontuação não informada!")
        sys.exit(1)
    score = sys.argv[1]
    
    # Configuração do input para o nome (centralizado)
    input_box_width = int(screen_width * 0.25)
    input_box_height = int(screen_height * 0.08)
    input_box = pygame.Rect((screen_width - input_box_width) // 2, int(screen_height * 0.4), input_box_width, input_box_height)
    
    # Cores e estados do input
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    input_color = color_inactive
    active = False
    user_text = ""
    
    # Configuração do botão "Enviar" (centralizado)
    button_width = int(screen_width * 0.15)
    button_height = int(screen_height * 0.08)
    button_rect = pygame.Rect((screen_width - button_width) // 2, int(screen_height * 0.55), button_width, button_height)
    
    clock = pygame.time.Clock()
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ativa ou desativa o input conforme o clique
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                input_color = color_active if active else color_inactive
                
                # Verifica se o botão foi clicado
                if button_rect.collidepoint(event.pos):
                    insert_score(score, user_text)
                    subprocess.run(["python", "src/layoutIMSI.py"])
                    done = True
            
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        insert_score(score, user_text)
                        subprocess.run(["python", "src/layoutIMSI.py"])
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
        
        # Fundo com tom escuro para um visual profissional
        screen.fill((40, 40, 40))
        
        # Exibe a pontuação na parte superior central
        score_text = font_big.render("Score: " + str(score), True, pygame.Color('white'))
        score_rect = score_text.get_rect(center=(screen_width // 2, int(screen_height * 0.2)))
        screen.blit(score_text, score_rect)
        
        # Renderiza o input do nome
        txt_surface = font_small.render(user_text, True, input_color)
        # Ajusta a largura do input de forma responsiva
        input_box.w = max(int(screen_width * 0.25), txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, input_color, input_box, 2)
        
        # Renderiza o botão "Enviar"
        pygame.draw.rect(screen, pygame.Color('green'), button_rect)
        button_text = font_small.render("Enviar", True, pygame.Color('black'))
        button_rect_text = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_rect_text)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
