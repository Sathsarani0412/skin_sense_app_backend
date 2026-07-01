import sqlite3

connection = sqlite3.connect(
    "users.db"
)

cursor = connection.cursor()



cursor.execute("""

CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    email TEXT UNIQUE,

    password TEXT
)

""")



cursor.execute("""

CREATE TABLE IF NOT EXISTS skin_results(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    email TEXT,

    blackheads REAL,

    dark_spots REAL,

    whiteheads REAL,

    wrinkles REAL,

    predicted_class TEXT,

    confidence REAL,

    recommendation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

""")

connection.commit()

connection.close()

print("Database Created Successfully")
