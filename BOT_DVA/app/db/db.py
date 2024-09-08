import sqlite3


connection = sqlite3.connect('betbot_db.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS statement(
id int auto_increment primary_key,
date text,               
trade text, 
instrument text,
price real,
depo real,
pl real)""")


connection.commit()
connection.close()