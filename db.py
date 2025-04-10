import mysql.connector

def connect():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="lost_found_db"
)
