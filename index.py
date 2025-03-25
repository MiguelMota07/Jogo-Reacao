from src import layoutIMSI
import sys
from testes import reaction
from testes import teste_mao as teste

def iniciar(a):
    if a == 1:
        reaction.main()
    elif a == 2:
        teste.main()
        layoutIMSI.main()
    else:
        sys.exit()



if __name__ == "__main__":
    running = True
    while running:
        algumaCoisa=layoutIMSI.main()
        iniciar(algumaCoisa)