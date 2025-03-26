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
		top_reacoes.append(f"{posicao}. {nome} - {tempo}s")
		posicao += 1
	return top_reacoes