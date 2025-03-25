import layoutIMSI
import sys
import reaction
import teste_mao as teste

def iniciar(a):
    if a == 1:
       reaction.main()
       layoutIMSI.main()
    elif a ==2:
        teste.main()
        layoutIMSI.main()



if __name__ == "__main__":
    algumaCoisa = layoutIMSI.main()
    iniciar(algumaCoisa)
    