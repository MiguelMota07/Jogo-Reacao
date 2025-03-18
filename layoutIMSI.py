import pygame
import sys
import webbrowser  # Adicionado para abrir páginas web
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('musica.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Configurações Gerais
SCREEN = pygame.display.set_mode((0, 0))
WIDTH, HEIGHT = SCREEN.get_width(), SCREEN.get_height()
pygame.display.set_caption("Desafia-te!")

# Cores
WHITE = (245, 245, 245)
DARK_BG = (25, 25, 30)
GRAY = (100, 100, 100)
LIGHT_GRAY = (170, 170, 170)
RED = (200, 30, 30)
HOVER_RED = (255, 50, 50)
BLUE = (30, 144, 255)
HOVER_BLUE = (65, 180, 255)

# Fontes
FONT = pygame.font.SysFont('arial', 26)
TITLE_FONT = pygame.font.SysFont('arial', 72, bold=True)
SUB_FONT = pygame.font.SysFont('arial', 32, bold=True)

# Botões e Textos
BUTTONS = [
    {"text": "JOGAR", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 100, 340, 80), "color": BLUE, "hover": HOVER_BLUE},
    {"text": "RANKING", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2, 340, 80), "color": BLUE, "hover": HOVER_BLUE},
    {"text": "DEFINIÇÕES", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 100, 340, 80), "color": BLUE, "hover": HOVER_BLUE},
    {"text": "CRÉDITOS", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 200, 340, 80), "color": BLUE, "hover": HOVER_BLUE},
    {"text": "SAIR", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 300, 340, 80), "color": RED, "hover": HOVER_RED},
]

top_reaction = ["1. João - 10s", "2. Maria - 12s", "3. Pedro - 14s"]
top_movement = ["1. Carlos - 8752 pontos", "2. Ana - 6241 pontos", "3. Rui - 6211 pontos"]

clock = pygame.time.Clock()

# Variável de estado para controlar a exibição do menu de créditos e definições
show_credits = False
show_settings = False

# Definição do botão "VOLTAR" globalmente
back_button = {"text": "VOLTAR", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 200, 340, 80), "color": BLUE, "hover": HOVER_BLUE}

# Variáveis de configuração
volume_music = 0.5
sound_effects = True

def draw_button(button, mouse_pos):
    color = button["hover"] if button["rect"].collidepoint(mouse_pos) else button["color"]
    pygame.draw.rect(SCREEN, color, button["rect"], border_radius=12)
    text_surface = FONT.render(button["text"], True, WHITE)
    SCREEN.blit(text_surface, (button["rect"].centerx - text_surface.get_width() // 2,
                               button["rect"].centery - text_surface.get_height() // 2))

def draw_menu():
    SCREEN.fill(DARK_BG)
    
    # Título com sombra
    title = TITLE_FONT.render("DESAFIA-TE!", True, WHITE)
    shadow = TITLE_FONT.render("DESAFIA-TE!", True, GRAY)
    SCREEN.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 54))
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    # Top 3 - Reação
    SCREEN.blit(SUB_FONT.render("Top Reação", True, WHITE), (50, 150))
    for i, player in enumerate(top_reaction):
        player_text = FONT.render(player, True, LIGHT_GRAY)
        SCREEN.blit(player_text, (50, 200 + i * 40))
    
    # Top 3 - Movimento
    SCREEN.blit(SUB_FONT.render("Top Movimento", True, WHITE), (WIDTH - 320, 150))
    for i, player in enumerate(top_movement):
        player_text = FONT.render(player, True, LIGHT_GRAY)
        SCREEN.blit(player_text, (WIDTH - 320, 200 + i * 40))
    
    # Desenhar botões
    mouse_pos = pygame.mouse.get_pos()
    for button in BUTTONS:
        draw_button(button, mouse_pos)

    pygame.display.flip()

def draw_credits_menu():
    SCREEN.fill(DARK_BG)
    
    # Título com sombra
    title = TITLE_FONT.render("CRÉDITOS", True, WHITE)
    shadow = TITLE_FONT.render("CRÉDITOS", True, GRAY)
    SCREEN.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 54))
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Centralizando os textos
    developers_text = SUB_FONT.render("Desenvolvedores:", True, WHITE)
    musicas_text = SUB_FONT.render("Músicas utilizadas:", True, WHITE)

    # Posicionamento centralizado
    developers_pos = (WIDTH // 2 - developers_text.get_width() // 2, 200)
    musicas_pos = (WIDTH // 2 - musicas_text.get_width() // 2, 400)

    # Desenhando os títulos centralizados
    SCREEN.blit(developers_text, developers_pos)
    SCREEN.blit(musicas_text, musicas_pos)
    
    # Desenvolvedores
    developers = ["André Nicolau", "Miguel Mota"]
    for i, dev in enumerate(developers):
        dev_text = FONT.render(dev, True, LIGHT_GRAY)
        SCREEN.blit(dev_text, (WIDTH // 2 - dev_text.get_width() // 2, 250 + i * 40))  # Ajustado a posição vertical
    
    # Músicas utilizadas
    musicas = ["Age of War", "Puto Roger", "123"]
    for i, musica in enumerate(musicas):
        musica_text = FONT.render(musica, True, LIGHT_GRAY)
        SCREEN.blit(musica_text, (WIDTH // 2 - musica_text.get_width() // 2, 450 + i * 40))  # Ajustado a posição vertical
    
    # Botão Voltar
    draw_button(back_button, pygame.mouse.get_pos())
    
    pygame.display.flip()

def draw_settings_menu():
    SCREEN.fill(DARK_BG)
    
    # Título com sombra
    title = TITLE_FONT.render("DEFINIÇÕES", True, WHITE)
    shadow = TITLE_FONT.render("DEFINIÇÕES", True, GRAY)
    SCREEN.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 54))
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    # Ajuste de volume de música
    volume_text = FONT.render(f"Volume Música: {int(volume_music * 100)}%", True, WHITE)
    SCREEN.blit(volume_text, (WIDTH // 2 - volume_text.get_width() // 2, 200))
    
    # Botões para ajustar volume
    plus_button = FONT.render("+", True, WHITE)
    minus_button = FONT.render("-", True, WHITE)
    pygame.draw.rect(SCREEN, BLUE, pygame.Rect(WIDTH // 2 - 100, 250, 50, 50), border_radius=12)
    pygame.draw.rect(SCREEN, BLUE, pygame.Rect(WIDTH // 2 + 50, 250, 50, 50), border_radius=12)
    
    SCREEN.blit(plus_button, (WIDTH // 2 + 50 + 25 - plus_button.get_width() // 2, 250 + 25 - plus_button.get_height() // 2))
    SCREEN.blit(minus_button, (WIDTH // 2 - 100 + 25 - minus_button.get_width() // 2, 250 + 25 - minus_button.get_height() // 2))
    
    # Efeitos sonoros
    sound_text = FONT.render(f"Efeitos Sonoros: {'Ativos' if sound_effects else 'Desativados'}", True, WHITE)
    SCREEN.blit(sound_text, (WIDTH // 2 - sound_text.get_width() // 2, 350))
    
    # Botão para ativar/desativar efeitos sonoros
    sound_button_color = BLUE if sound_effects else RED
    draw_button({"text": "Ativar/Desativar Efeitos Sonoros", "rect": pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 300, 340, 80), "color": sound_button_color, "hover": HOVER_BLUE}, pygame.mouse.get_pos())
    
    # Botão Voltar
    draw_button(back_button, pygame.mouse.get_pos())
    
    pygame.display.flip()


# Exemplo de loop principal
while True:
    if show_credits:
        draw_credits_menu()
    elif show_settings:
        draw_settings_menu()
    else:
        draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if show_credits:  # Se estamos no menu de créditos
                if back_button["rect"].collidepoint(mouse_pos):
                    show_credits = False  # Volta para o menu principal
            elif show_settings:  # Se estamos no menu de definições
                if back_button["rect"].collidepoint(mouse_pos):
                    show_settings = False  # Volta para o menu principal
                elif pygame.Rect(WIDTH // 2 - 100, 250, 50, 50).collidepoint(mouse_pos):  # Botão de diminuir volume
                    volume_music = max(0, volume_music - 0.05)
                    pygame.mixer.music.set_volume(volume_music)
                elif pygame.Rect(WIDTH // 2 + 50, 250, 50, 50).collidepoint(mouse_pos):  # Botão de aumentar volume
                    volume_music = min(1, volume_music + 0.05)
                    pygame.mixer.music.set_volume(volume_music)
                elif pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 300, 340, 80).collidepoint(mouse_pos):  # Botão de ativar/desativar efeitos sonoros
                    sound_effects = not sound_effects
            else:  # Se estamos no menu principal
                for button in BUTTONS:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["text"] == "SAIR":
                            pygame.quit()
                            sys.exit()
                        elif button["text"] == "JOGAR":
                            print("Iniciar o Jogo...")
                        elif button["text"] == "RANKING":
                            webbrowser.open("http://localhost")  # Abre a página localhost
                        elif button["text"] == "DEFINIÇÕES":
                            show_settings = True  # Exibe o menu de definições
                        elif button["text"] == "CRÉDITOS":
                            show_credits = True  # Exibe o menu de créditos

    clock.tick(60)

pygame.quit()
sys.exit()
