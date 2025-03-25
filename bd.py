import mysql.connector

bd = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="estagios"
)

mycursor = bd.cursor()

