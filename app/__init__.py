from flask import Flask
from config import Config
from .extensions import mysql, bcrypt, login_manager
from . import routes
import os
import MySQLdb
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ➤ Connexion temporaire pour créer la DB si elle n'existe pas
    tmp_conn = MySQLdb.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        passwd=app.config['MYSQL_PASSWORD']
    )
    tmp_cursor = tmp_conn.cursor()
    tmp_cursor.execute("CREATE DATABASE IF NOT EXISTS playntrade")
    tmp_conn.commit()
    tmp_cursor.close()
    tmp_conn.close()

    # ➤ Initialiser les extensions APRES que la base existe
    mysql.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"

    with app.app_context():
        conn = mysql.connection
        cursor = conn.cursor()

        try:
            # Exécution des scripts SQL
            sql_path = Path(__file__).parent
            for file in ["models.sql", "setup.sql"]:
                full_path = sql_path / file
                if full_path.exists():
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        statements = content.split("$$") if "$$" in content else content.split(";")
                        for statement in statements:
                            if statement.strip():
                                cursor.execute(statement)

            # ➤ Ajout admin si absent
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_pw = bcrypt.generate_password_hash('adminpass').decode('utf-8')
                cursor.execute("""
                    INSERT INTO users (username, password, is_admin)
                    VALUES (%s, %s, TRUE)
                """, ('admin', hashed_pw))

            conn.commit()
        except Exception as e:
            print("Erreur d'initialisation :", e)
        finally:
            cursor.close()

    routes.init_routes(app)
    return app
