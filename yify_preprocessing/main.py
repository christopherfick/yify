import sqlite3 as sql


conn = sql.connect("data/movie.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM movie
    """)
print(cursor.fetchone())



conn.close()