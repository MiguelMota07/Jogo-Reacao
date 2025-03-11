import pygame
import sys
import webbrowser

pygame.init()
pygame.mixer.init() 
pygame.mixer.music.load('Desktop\musica.mp3')  
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(-1, 0.0) 

# Configurações
SCREEN = pygame.display.set_mode((0, 0))
WIDTH, HEIGHT = SCREEN.get_width(), SCREEN.get_height()
pygame.display.set_caption("Menu Principal")
FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 56)
SUBTITLE_FONT = pygame.font.Font(None, 36)
WHITE = (255, 255, 255)
COLORS = [(70, 130, 180), (34, 139, 34), (218, 165, 32), (138, 43, 226)]
HOVER_COLORS = [(100, 160, 210), (50, 180, 50), (240, 200, 60), (160, 80, 250)]
GRAY = (100, 100, 100)
DARK_RED = (200, 0, 0)
LIGHT_GRAY = (150, 150, 150)
LIGHT_RED = (255, 50, 50)

BUTTON_TEXTS = ["Jogo \"Desenho\"", "Jogo \"Movimentos\""]
BUTTON_RECTS = []

sound_effects_enabled = True
music_volume = 50

# Top 3 jogadores fictícios
top_players = ["1. João", "2. Maria", "3. Pedro"]

# Criar botões ao centro
y_offset = HEIGHT // 2.5
for i, text in enumerate(BUTTON_TEXTS):
    rect = pygame.Rect(WIDTH // 2 - 150, y_offset, 300, 90)  
    BUTTON_RECTS.append((rect, COLORS[i], HOVER_COLORS[i]))  
    y_offset += 100  # Ajustar espaçamento


# Botão de ranking abaixo
top_ranking_button = pygame.Rect(50, HEIGHT // 2.1, 250, 60)

# Botão de ver todos os desenhos do lado direito
view_drawings_button = pygame.Rect(WIDTH - 300, HEIGHT // 2 - 30, 250, 60)

# Botão de definições acima do botão de créditos
settings_button = pygame.Rect(WIDTH - 200, HEIGHT - 180, 150, 50)

# Botão de créditos
credits_button = pygame.Rect(WIDTH - 200, HEIGHT - 120, 150, 50)

# Botão de sair
exit_button = pygame.Rect(WIDTH - 200, HEIGHT - 60, 150, 50)

# Variável para controlar o estado do menu
show_settings = False

# Botão de Voltar no menu de definições
back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)

show_settings = False
show_credits = False  # Nova variável para o menu de créditos

# Botão de Voltar no menu de créditos
back_credits_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)
# Função para desenhar os créditos
def draw_credits():
    SCREEN.fill((30, 30, 30))

    # Desenha o painel de créditos
    credits_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 5, 400, 600)
    pygame.draw.rect(SCREEN, GRAY, credits_rect, border_radius=15)

    # Título dos créditos
    title = TITLE_FONT.render("Créditos", True, WHITE)
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 + 20))

    # Título Desenvolvedores
    dev_title = SUBTITLE_FONT.render("Desenvolvedores:", True, WHITE)  # Título dos desenvolvedores
    SCREEN.blit(dev_title, (WIDTH // 2 - dev_title.get_width() // 2, HEIGHT // 4 + 100))

    dev_text1 = FONT.render("André Nicolau (a13742)", True, WHITE)
    SCREEN.blit(dev_text1, (WIDTH // 2 - dev_text1.get_width() // 2, HEIGHT // 4 + 140))

    dev_text2 = FONT.render("Miguel Mota (a13741)", True, WHITE)
    SCREEN.blit(dev_text2, (WIDTH // 2 - dev_text2.get_width() // 2, HEIGHT // 4 + 180))

    # Título Músicas Utilizadas
    music_title = SUBTITLE_FONT.render("Músicas utilizadas:", True, WHITE)  # Título das músicas
    SCREEN.blit(music_title, (WIDTH // 2 - music_title.get_width() // 2, HEIGHT // 4 + 240))

    music_text1 = FONT.render("Age of War - Theme Soundtrack", True, WHITE)
    SCREEN.blit(music_text1, (WIDTH // 2 - music_text1.get_width() // 2, HEIGHT // 4 + 280))

    music_text2 = FONT.render("Puto Roger - ssssss", True, WHITE)
    SCREEN.blit(music_text2, (WIDTH // 2 - music_text2.get_width() // 2, HEIGHT // 4 + 320))

    music_text3 = FONT.render("Teste - 123 e ola meioRei", True, WHITE)
    SCREEN.blit(music_text3, (WIDTH // 2 - music_text3.get_width() // 2, HEIGHT // 4 + 360))

    # Botão de Voltar
    back_color = (255, 0, 0) if back_button.collidepoint(pygame.mouse.get_pos()) else (200, 0, 0)
    pygame.draw.rect(SCREEN, back_color, back_button, border_radius=10)
    back_text = FONT.render("Voltar", True, WHITE)
    SCREEN.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + 15))

    pygame.display.flip()

# Modificar a lógica para exibir os créditos
def draw_menu():
    SCREEN.fill((30, 30, 30))

    if show_settings:
        # Desenha o menu de definições
        settings_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 5, 400, 600)
        pygame.draw.rect(SCREEN, GRAY, settings_rect, border_radius=15)

        # Título do menu de definições
        title = TITLE_FONT.render("Definições", True, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4 + 20))

        # Opção de Efeitos Sonoros (Checkbox)
        checkbox_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 4 + 100, 20, 20)
        pygame.draw.rect(SCREEN, WHITE, checkbox_rect, border_radius=5)
        if sound_effects_enabled:
            pygame.draw.line(SCREEN, BLACK, (checkbox_rect.x + 4, checkbox_rect.y + 10), (checkbox_rect.x + 10, checkbox_rect.y + 16), 3)
            pygame.draw.line(SCREEN, BLACK, (checkbox_rect.x + 10, checkbox_rect.y + 16), (checkbox_rect.x + 16, checkbox_rect.y + 4), 3)
        sound_text = FONT.render("Efeitos Sonoros", True, WHITE)
        SCREEN.blit(sound_text, (checkbox_rect.x + 30, checkbox_rect.y - 5))

        # Slider para controle do volume da música
        slider_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 4 + 150, 200, 10)
        pygame.draw.rect(SCREEN, WHITE, slider_rect)
        handle_x = int(slider_rect.x + (music_volume * slider_rect.width))
        pygame.draw.circle(SCREEN, RED, (handle_x, slider_rect.y + 5), 8)
        music_text = FONT.render("Música", True, WHITE)
        SCREEN.blit(music_text, (slider_rect.x, slider_rect.y - 25))

        # Botão de Voltar
        back_color = (255, 0, 0) if back_button.collidepoint(pygame.mouse.get_pos()) else (200, 0, 0)
        pygame.draw.rect(SCREEN, back_color, back_button, border_radius=10)
        back_text = FONT.render("Voltar", True, WHITE)
        SCREEN.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + 15))

    elif show_credits:
        draw_credits()  # Chama a função que desenha os créditos

    else:
        # Renderiza o menu principal
        title = TITLE_FONT.render("Desenhar e Desafiar", True, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Renderizar top 3 jogadores
        y_text_offset = HEIGHT // 4
        tit = FONT.render("Top 3 do jogo de movimentos:", True, WHITE)
        SCREEN.blit(tit, (50, HEIGHT - 350))
        for player in top_players:
            text = FONT.render(player, True, WHITE)
            SCREEN.blit(text, (50, y_text_offset + 350))
            y_text_offset += 30

        mouse_pos = pygame.mouse.get_pos()

        # Renderizar botões com hover
        for rect, color, hover_color in BUTTON_RECTS:
            current_color = hover_color if rect.collidepoint(mouse_pos) else color
            pygame.draw.rect(SCREEN, current_color, rect, border_radius=10)
            
            # Obter o índice do botão e o texto correspondente
            index = BUTTON_RECTS.index((rect, color, hover_color))
            text = FONT.render(BUTTON_TEXTS[index], True, WHITE)
            
            # Centralizar o texto dentro do botão
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            
            SCREEN.blit(text, (text_x, text_y))

        # Botão de ranking
        ranking_color = (240, 200, 60) if top_ranking_button.collidepoint(mouse_pos) else COLORS[2]
        pygame.draw.rect(SCREEN, ranking_color, top_ranking_button, border_radius=10)
        ranking_text = FONT.render("Ranking Movimentos", True, WHITE)
        SCREEN.blit(ranking_text, (top_ranking_button.x + (top_ranking_button.width - ranking_text.get_width()) // 2, top_ranking_button.y + 15))

        # Botão de ver todos os desenhos
        view_color = (160, 80, 250) if view_drawings_button.collidepoint(mouse_pos) else COLORS[3]
        pygame.draw.rect(SCREEN, view_color, view_drawings_button, border_radius=10)
        view_text = FONT.render("Ver Todos os Desenhos", True, WHITE)
        SCREEN.blit(view_text, (view_drawings_button.x + (view_drawings_button.width - view_text.get_width()) // 2, view_drawings_button.y + 15))

        # Botão de definições
        settings_color = LIGHT_GRAY if settings_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(SCREEN, settings_color, settings_button, border_radius=10)
        settings_text = FONT.render("Definições", True, WHITE)
        SCREEN.blit(settings_text, (settings_button.x + (settings_button.width - settings_text.get_width()) // 2, settings_button.y + 15))

        # Botão de créditos
        credits_color = LIGHT_GRAY if credits_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(SCREEN, credits_color, credits_button, border_radius=10)
        credits_text = FONT.render("Créditos", True, WHITE)
        SCREEN.blit(credits_text, (credits_button.x + (credits_button.width - credits_text.get_width()) // 2, credits_button.y + 15))

        # Botão de sair
        exit_color = LIGHT_RED if exit_button.collidepoint(mouse_pos) else DARK_RED
        pygame.draw.rect(SCREEN, exit_color, exit_button, border_radius=10)
        exit_text = FONT.render("Sair", True, WHITE)
        SCREEN.blit(exit_text, (exit_button.x + (exit_button.width - exit_text.get_width()) // 2, exit_button.y + 15))

    pygame.display.flip()

# Atualização da lógica de controle de eventos para o botão de créditos
running = True
while running:
    draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, item in enumerate(BUTTON_RECTS):
                rect, _, _ = item  # Desempacota corretamente
                if rect.collidepoint(event.pos):
                    print(f"Clicou em: {BUTTON_TEXTS[i]}")
            if top_ranking_button.collidepoint(event.pos):
                print("Clicou em: Ranking Movimentos")
                webbrowser.open("http://localhost/ranking")
            if view_drawings_button.collidepoint(event.pos):
                print("Clicou em: Ver Todos os Desenhos")
                webbrowser.open("http://localhost/desenhos")
            if settings_button.collidepoint(event.pos):
                print("Clicou em: Definições")
                show_settings = True  # Mostra o menu de definições
            if credits_button.collidepoint(event.pos):
                print("Clicou em: Créditos")
                show_credits = True  # Mostra o menu de créditos
            if exit_button.collidepoint(event.pos):
                running = False
            if back_button.collidepoint(event.pos):
                print("Clicou em: Voltar")
                show_settings = False  # Retorna ao menu principal
                show_credits = False  # Retorna ao menu principal

pygame.quit()
sys.exit()
