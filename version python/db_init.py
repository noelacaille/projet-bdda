import MySQLdb
from flask_bcrypt import Bcrypt

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
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
            id INT PRIMARY KEY,
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
            publisher TEXT,
            thumbnail VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            game_id INT NOT NULL,
            game_condition ENUM('neuf', 'très bon état', 'bon état', 'acceptable') NOT NULL,
            city VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_game_id INT NOT NULL,
            liked BOOLEAN NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (user_game_id) REFERENCES user_games(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            like_id INT NOT NULL,
            offered_game_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (like_id) REFERENCES likes(id) ON DELETE CASCADE,
            FOREIGN KEY (offered_game_id) REFERENCES user_games(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            action VARCHAR(50),
            username VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("DROP PROCEDURE IF EXISTS sp_InsertUser")
    cursor.execute("""
        CREATE PROCEDURE sp_InsertUser(
            IN p_username VARCHAR(50),
            IN p_password VARCHAR(255),
            IN p_is_admin BOOLEAN
        )
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM users WHERE username = p_username) THEN
                INSERT INTO users (username, password, is_admin)
                VALUES (p_username, p_password, p_is_admin);
            END IF;
        END
    """)

    cursor.execute("DROP PROCEDURE IF EXISTS sp_HandleLike")
    cursor.execute("""
        CREATE PROCEDURE sp_HandleLike(
            IN p_user_id INT,
            IN p_user_game_id INT,
            IN p_liked BOOLEAN
        )
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM likes 
                WHERE user_id = p_user_id AND user_game_id = p_user_game_id
            ) THEN
                INSERT INTO likes (user_id, user_game_id, liked)
                VALUES (p_user_id, p_user_game_id, p_liked);
            END IF;
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_AfterUserInsert")
    cursor.execute("""
        CREATE TRIGGER tr_AfterUserInsert
        AFTER INSERT ON users
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            VALUES ('USER_CREATED', NEW.username);
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_PreventAdminDeletion")
    cursor.execute("""
        CREATE TRIGGER tr_PreventAdminDeletion
        BEFORE DELETE ON users
        FOR EACH ROW
        BEGIN
            IF OLD.username = 'admin' THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Cannot delete admin account';
            END IF;
        END
    """)

    cursor.execute("DROP VIEW IF EXISTS vw_AvailableGames")
    cursor.execute("""
        CREATE OR REPLACE VIEW vw_AvailableGames AS
        SELECT 
            ug.id AS user_game_id,
            g.title AS game_title,
            g.thumbnail AS game_thumbnail,
            u.username AS owner_username,
            ug.city, 
            ug.game_condition,
            l.user_id AS liked_by_user,
            l.liked AS liked_value,
            u.id AS owner_id
        FROM user_games ug
        JOIN games g ON ug.game_id = g.id
        JOIN users u ON ug.user_id = u.id
        LEFT JOIN likes l ON ug.id = l.user_game_id
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
