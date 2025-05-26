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
            description VARCHAR(10000),
            title VARCHAR(255),
            year_published INT,
            min_players INT,
            max_players INT,
            playing_time INT,
            min_age INT,
            category VARCHAR(1000),
            mechanic VARCHAR(1000),
            designer VARCHAR(1000),
            publisher VARCHAR(2000),
            thumbnail VARCHAR(1000)
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


    cursor.execute("DROP TRIGGER IF EXISTS tr_GameInsert")
    cursor.execute("""
        CREATE TRIGGER tr_GameInsert
        AFTER INSERT ON games
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            VALUES ('GAME_CREATED', 'admin');
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_GameUpdate")
    cursor.execute("""
        CREATE TRIGGER tr_GameUpdate
        AFTER UPDATE ON games
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            VALUES ('GAME_UPDATED', 'admin');
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_GameDelete")
    cursor.execute("""
        CREATE TRIGGER tr_GameDelete
        BEFORE DELETE ON games
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            VALUES ('GAME_DELETED', 'admin');
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_LikeInsert")
    cursor.execute("""
        CREATE TRIGGER tr_LikeInsert
        AFTER INSERT ON likes
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            SELECT 'LIKE_ADDED', username FROM users WHERE id = NEW.user_id;
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_LikeDelete")
    cursor.execute("""
        CREATE TRIGGER tr_LikeDelete
        BEFORE DELETE ON likes
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            SELECT 'LIKE_REMOVED', username FROM users WHERE id = OLD.user_id;
        END
    """)

    cursor.execute("DROP TRIGGER IF EXISTS tr_MatchInsert")
    cursor.execute("""
        CREATE TRIGGER tr_MatchInsert
        AFTER INSERT ON matches
        FOR EACH ROW
        BEGIN
            INSERT INTO audit_log (action, username)
            SELECT 'MATCH_CREATED', u.username
            FROM likes l
            JOIN users u ON l.user_id = u.id
            WHERE l.id = NEW.like_id;
        END
    """)

    cursor.execute("DROP VIEW IF EXISTS vw_LikesWithDetails")
    cursor.execute("""
            CREATE OR REPLACE VIEW vw_LikesWithDetails AS
            SELECT 
                l.id AS like_id,
                l.user_id AS liker_id,
                u.username AS liker_username,
                ug.id AS liked_user_game_id,
                ug.user_id AS owner_id,
                o.username AS owner_username,
                g.title AS game_title,
                g.thumbnail AS game_thumbnail,
                ug.city,
                ug.game_condition,
                l.liked,
                l.user_game_id,
                l.id
            FROM likes l
            JOIN user_games ug ON l.user_game_id = ug.id
            JOIN users o ON ug.user_id = o.id
            JOIN users u ON l.user_id = u.id
            JOIN games g ON ug.game_id = g.id
        """)

    
    def create_index_if_not_exists(cursor, table_name, index_name, index_sql):
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.STATISTICS 
            WHERE table_schema = %s AND table_name = %s AND index_name = %s
        """, (DB_NAME, table_name, index_name))
        exists = cursor.fetchone()[0]
        if exists == 0:
            print(f"[DB INIT] Création de l'index {index_name}...")
            cursor.execute(index_sql)

        print("[DB INIT] Création des index...")
    

    create_index_if_not_exists(cursor, 'users', 'idx_users_username', 
        "CREATE INDEX idx_users_username ON users(username)")

    create_index_if_not_exists(cursor, 'games', 'idx_games_title', 
        "CREATE INDEX idx_games_title ON games(title)")

    create_index_if_not_exists(cursor, 'user_games', 'idx_user_games_user_id', 
        "CREATE INDEX idx_user_games_user_id ON user_games(user_id)")

    create_index_if_not_exists(cursor, 'user_games', 'idx_user_games_game_id', 
        "CREATE INDEX idx_user_games_game_id ON user_games(game_id)")

    create_index_if_not_exists(cursor, 'likes', 'idx_likes_user_id', 
        "CREATE INDEX idx_likes_user_id ON likes(user_id)")

    create_index_if_not_exists(cursor, 'likes', 'idx_likes_user_game_id', 
        "CREATE INDEX idx_likes_user_game_id ON likes(user_game_id)")

    create_index_if_not_exists(cursor, 'matches', 'idx_matches_like_id', 
        "CREATE INDEX idx_matches_like_id ON matches(like_id)")

    create_index_if_not_exists(cursor, 'matches', 'idx_matches_offered_game_id', 
        "CREATE INDEX idx_matches_offered_game_id ON matches(offered_game_id)")

    create_index_if_not_exists(cursor, 'audit_log', 'idx_audit_log_created_at', 
        "CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC)")



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
