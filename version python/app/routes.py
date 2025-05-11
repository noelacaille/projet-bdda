from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import mysql, bcrypt

def init_routes(app):
    @app.route("/")
    def index():
        return redirect(url_for('home'))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password_input = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            if user and bcrypt.check_password_hash(user[2], password_input):
                user_obj = User(user[0], user[1], user[2])
                login_user(user_obj)
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials', 'danger')
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            cur = mysql.connection.cursor()
            cur.callproc("sp_InsertUser", (username, hashed, False))  # False pour is_admin
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))
        return render_template('signup.html')


    @app.route('/home')
    @login_required
    def home():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, title FROM games")
        games = cursor.fetchall()
        cursor.close()
        return render_template('home.html', games=games)

    @app.route('/exchange', methods=['POST'])
    @login_required
    def exchange_game():
        title = request.form['game_title']
        condition = request.form['condition']
        city = request.form['city']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM games WHERE title = %s", (title,))
        result = cursor.fetchone()

        if result:
            game_id = result[0]
            cursor.execute("""
                INSERT INTO user_games (user_id, game_id, game_condition, city)
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, game_id, condition, city))
            mysql.connection.commit()
            flash("Ton jeu a été ajouté à la liste d'échange !")
        else:
            flash("Jeu non trouvé, vérifie le nom.")

        cursor.close()
        return redirect(url_for('home'))
    
    @app.route('/find_game')
    @login_required
    def find_game():
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT * FROM vw_AvailableGames
            WHERE owner_username != %s
            AND user_game_id NOT IN (
                SELECT user_game_id FROM likes WHERE user_id = %s
            );
        """, (current_user.id, current_user.id))
        game = cursor.fetchall()
        cursor.close()
        if len(game) == 0:
            return render_template('find_game.html', game=[])
        return render_template('find_game.html', game=game[0])


    @app.route('/handle_game_action', methods=['POST'])
    @login_required
    def handle_game_action():
        user_game_id = request.form.get('user_game_id')
        action = request.form.get('action')

        cursor = mysql.connection.cursor()
        cursor.callproc("sp_HandleLike", (current_user.id, user_game_id, action == "like"))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('find_game'))

    @app.route("/games")
    @login_required
    def all_games():
        search_query = request.args.get("q", "").strip()

        cursor = mysql.connection.cursor()
        if search_query:
            cursor.execute("""
                SELECT ug.id, g.title, u.username, ug.city, ug.game_condition, g.thumbnail
                FROM user_games ug
                JOIN games g ON ug.game_id = g.id
                JOIN users u ON ug.user_id = u.id
                WHERE g.title LIKE %s
                ORDER BY g.title
            """, (f"%{search_query}%",))
        else:
            cursor.execute("""
                SELECT ug.id, g.title, u.username, ug.city, ug.game_condition, g.thumbnail
                FROM user_games ug
                JOIN games g ON ug.game_id = g.id
                JOIN users u ON ug.user_id = u.id
                ORDER BY g.title
            """)

        games = cursor.fetchall()
        return render_template("all_games.html", games=games, search_query=search_query)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
