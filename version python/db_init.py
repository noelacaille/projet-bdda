import MySQLdb
import os
from flask_bcrypt import Bcrypt

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # à adapter si tu as un mot de passe
DB_NAME = "playntrade"

def initialize_database():
    print("[DB INIT] Connexion à MySQL...")
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD
    )
    cursor = conn.cursor()

    print(f"[DB INIT] Création de la base {DB_NAME} si inexistante...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    print("[DB INIT] Création des tables...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INT PRIMARY KEY,  -- correspond à l'id unique du jeu
            description TEXT,
            title TEXT,
            year_published INT,
            min_players INT,
            max_players INT,
            playing_time INT,
            min_age INT,
            category TEXT,
            mechanic TEXT,
            designer TEXT,
            publisher TEXT
        );

    """)

    print("[DB INIT] Vérification de l'existence de l'admin...")
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        print("[DB INIT] Insertion de l'utilisateur admin...")
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash("admin").decode('utf-8')
        cursor.execute("""
            INSERT INTO users (username, password, is_admin)
            VALUES (%s, %s, TRUE)
        """, ('admin', hashed_password))
    else:
        print("[DB INIT] Admin déjà existant.")

    conn.commit()
    cursor.close()
    conn.close()
    print("[DB INIT] Initialisation terminée.")

if __name__ == "__main__":
    initialize_database()
