from src import layoutIMSI
import sys
from src import reaction_sound
from src import reaction_colors
from src import db

def iniciar(a):
    if a == 1:
        reaction_sound.main()
        layoutIMSI.main()
    elif a == 2:
        reaction_colors.main()
        layoutIMSI.main()
    else:
        sys.exit()

if __name__ == "__main__":
    running = True
    while running:
        algumaCoisa=layoutIMSI.main()
        iniciar(algumaCoisa)