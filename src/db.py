import mysql.connector

def buscar_top_reacoes():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="expocic"
    )
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, tempo FROM reacoes ORDER BY tempo ASC LIMIT 3")
    resultados = cursor.fetchall()
    conexao.close()

    top_reacoes = []
    posicao = 1
    for nome, tempo in resultados:
        # Aqui usamos a formatação de 3 casas decimais
        top_reacoes.append(f"{posicao}. {nome} - {tempo:.3f}s")
        posicao += 1
    return top_reacoes

def buscar_top_movimentos():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="expocic"
        )
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, pontos FROM movimento ORDER BY pontos DESC LIMIT 3")
        resultados = cursor.fetchall()
        conexao.close()

        top_movimentos = []
        posicao = 1
        for nome, pontos in resultados:
            top_movimentos.append(f"{posicao}. {nome} - {pontos}")
            posicao += 1
        return top_movimentos
    except Exception as e:
        print("Erro ao buscar top movimentos:", e)
        return []