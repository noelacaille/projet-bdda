from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import mysql, bcrypt
import ast
import json

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
                user_obj = User(user[0], user[1], user[2], user[3])
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

        # D'abord vérifier si l'utilisateur a des jeux à proposer
        cursor.execute("""
            SELECT COUNT(*) 
            FROM user_games 
            WHERE user_id = %s
        """, (current_user.id,))
        test = cursor.fetchone()[0]
        user_has_games = test > 0

        if not user_has_games:
            flash("Vous devez d'abord proposer des jeux avant de pouvoir échanger", 'warning')
            return redirect(url_for('home'))

        # Si l'utilisateur a des jeux, continuer avec la recherche normale

        cursor.execute("""
            SELECT * FROM vw_AvailableGames
            WHERE owner_id != %s
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
        try:
            # 1. Insertion du like
            cursor.execute("""
                INSERT INTO likes (user_id, user_game_id, liked)
                VALUES (%s, %s, %s)
            """, (current_user.id, user_game_id, action == "like"))
            like_id = cursor.lastrowid

            # 2. Validation IMMÉDIATE
            mysql.connection.commit()

            if action == "like":
                # 3. Récupération des jeux de l'utilisateur
                cursor.execute("""
                    SELECT ug.id, g.title 
                    FROM user_games ug
                    JOIN games g ON ug.game_id = g.id
                    WHERE ug.user_id = %s
                """, (current_user.id,))
                my_games = cursor.fetchall()
                
                # 4. Vérification de like_id
                if not like_id:
                    raise Exception("Erreur : like_id non généré")
                
                return render_template('match_popup.html', 
                                    like_id=like_id,
                                    my_games=my_games)
            else:
                return redirect(url_for('find_game'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur : {str(e)}", 'danger')
            return redirect(url_for('find_game'))
        finally:
            cursor.close()

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
                WHERE g.title LIKE %s AND
                ug.user_id != %s
                ORDER BY g.title
            """, (f"%{search_query}%",current_user.id,))
        else:
            cursor.execute("""
                SELECT ug.id, g.title, u.username, ug.city, ug.game_condition, g.thumbnail
                FROM user_games ug
                JOIN games g ON ug.game_id = g.id
                JOIN users u ON ug.user_id = u.id
                WHERE ug.user_id != %s
                ORDER BY g.title
            """, (current_user.id,))

        games = cursor.fetchall()
        return render_template("all_games.html", games=games, search_query=search_query)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/create_match', methods=['POST'])
    @login_required
    def create_match():
        like_id = request.form['like_id']
        offered_game_id = request.form['offered_game_id']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO matches (like_id, offered_game_id)
                VALUES (%s, %s)
            """, (like_id, offered_game_id))
            
            mysql.connection.commit()
            flash('Échange proposé avec succès!', 'success')
        except Exception as e:
            print(e)
            mysql.connection.rollback()
            flash("Erreur lors de la création de l'échange", 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('find_game'))
    
    @app.route('/my_likes')
    @login_required
    def my_likes():
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT 
                l.id AS like_id,
                g.title AS game_title,
                o.username AS owner_username,
                ug.city,
                ug.game_condition,
                g.thumbnail
            FROM likes l
            JOIN user_games ug ON l.user_game_id = ug.id
            JOIN users o ON ug.user_id = o.id
            JOIN games g ON ug.game_id = g.id
            WHERE l.user_id = %s AND l.liked = TRUE
            ORDER BY l.id DESC
        """, (current_user.id,))

        matches = cursor.fetchall()
        cursor.close()

        return render_template('my_likes.html', matches=matches)

    
    @app.route('/reciprocal_matches')
    @login_required
    def reciprocal_matches():
        cursor = mysql.connection.cursor()
        
        # Requête pour trouver les matchs réciproques
        cursor.execute("""
            SELECT 
                u1.username AS c_user,
                u2.username AS other_user,
                g1.title AS your_liked_game_title,
                g2.title AS their_liked_game_title
            FROM likes l1
            JOIN user_games ug1 ON l1.user_game_id = ug1.id
            JOIN games g1 ON ug1.game_id = g1.id
            JOIN users u1 ON l1.user_id = u1.id

            JOIN likes l2 ON l1.user_id = l2.user_game_id  -- mauvaise jointure supprimée
            JOIN user_games ug2 ON l2.user_game_id = ug2.id
            JOIN games g2 ON ug2.game_id = g2.id
            JOIN users u2 ON ug2.user_id = u2.id

            WHERE l1.user_id = %s  -- l'utilisateur connecté
            AND l1.liked = TRUE
            AND l2.liked = TRUE
            AND l2.user_id = ug1.user_id   -- l'autre user a liké un de mes jeux
            AND ug2.user_id = l1.user_id   -- le jeu que j’ai liké appartient à l’autre

        """, (current_user.id,))
        
        reciprocal = cursor.fetchall()
        cursor.close()
        
        return render_template('reciprocal_matches.html', matches=reciprocal)

    @app.route('/delete_like/<int:like_id>', methods=['POST'])
    @login_required
    def delete_like(like_id):
        cursor = mysql.connection.cursor()
        try:
            # Vérifier que le like appartient bien à l'utilisateur courant
            cursor.execute("SELECT id FROM likes WHERE id = %s AND user_id = %s", 
                        (like_id, current_user.id))
            if not cursor.fetchone():
                flash("Ce like ne vous appartient pas", 'danger')
                return redirect(url_for('my_likes'))
            
            # Supprimer le like et les matches associés
            cursor.execute("DELETE FROM matches WHERE like_id = %s", (like_id,))
            cursor.execute("DELETE FROM likes WHERE id = %s", (like_id,))
            
            mysql.connection.commit()
            flash("Like supprimé avec succès", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de la suppression: {str(e)}", 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('my_likes'))
    

    @app.route('/my_offered_games')
    @login_required
    def my_offered_games():
        cursor = mysql.connection.cursor()
        
        # Récupérer les jeux proposés par l'utilisateur avec leurs infos
        cursor.execute("""
            SELECT 
                ug.id,
                g.title,
                g.thumbnail,
                ug.game_condition,
                ug.city,
                COUNT(l.id) AS like_count
            FROM user_games ug
            JOIN games g ON ug.game_id = g.id
            LEFT JOIN likes l ON ug.id = l.user_game_id
            WHERE ug.user_id = %s
            GROUP BY ug.id
            ORDER BY g.title
        """, (current_user.id,))
        
        games = cursor.fetchall()
        cursor.close()
        
        return render_template('my_offered_games.html', games=games)

    @app.route('/delete_offered_game/<int:game_id>', methods=['POST'])
    @login_required
    def delete_offered_game(game_id):
        cursor = mysql.connection.cursor()
        try:
            # 1. Vérification de propriété
            cursor.execute("SELECT id FROM user_games WHERE id = %s AND user_id = %s", 
                        (game_id, current_user.id))
            if not cursor.fetchone():
                flash("Action non autorisée", 'danger')
                return redirect(url_for('my_offered_games'))

            # 2. Suppression en cascade manuelle
            # D'abord les matches associés via like_id
            cursor.execute("""
                DELETE m FROM matches m
                JOIN likes l ON m.like_id = l.id
                WHERE l.user_game_id = %s
            """, (game_id,))
            
            # Ensuite les likes directs
            cursor.execute("DELETE FROM likes WHERE user_game_id = %s", (game_id,))
            
            # Enfin le jeu lui-même
            cursor.execute("DELETE FROM user_games WHERE id = %s", (game_id,))
            
            mysql.connection.commit()
            flash("Jeu et données associées supprimés avec succès", 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur technique lors de la suppression: {str(e)}", 'danger')
        finally:
            cursor.close()
        
        return redirect(url_for('my_offered_games'))
    
    @app.route('/game/<string:game_title>')
    def game_detail(game_title):
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT id, title, description, year_published, min_players, max_players,
                playing_time, min_age, category, mechanic, designer, publisher, thumbnail
            FROM games
            WHERE title = %s
        """, (game_title,))
        
        game = cursor.fetchone()

        if not game:
            return "Jeu non trouvé", 404
        
        # Normalize list fields
        # Tupe does not support item assignment
        # Convert to list for easier manipulation
        game = list(game)
        for i in [8, 9, 10, 11]:  # indexes of list fields
            game[i] = ast.literal_eval(game[i])
            game[i] = ", ".join(game[i]) if isinstance(game[i], list) else game[i]

        return render_template("game_detail.html", game=game)

    @app.route('/admin')
    @login_required
    def admin_panel():
        # Vérifier que l'utilisateur est admin
        if not current_user.is_admin:
            flash("Accès refusé : droits insuffisants", "danger")
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor()

        # Récupérer les statistiques
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM games")
        games_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_games")
        exchanges_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM matches")
        matches_count = cursor.fetchone()[0]

        stats = {
            'users': users_count,
            'games': games_count,
            'exchanges': exchanges_count,
            'matches': matches_count
        }

        # Récupérer les logs
        cursor.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 50")
        logs = cursor.fetchall()

        # Liste des utilisateurs
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = cursor.fetchall()

        # Liste des jeux
        # Pagination des jeux
        page = request.args.get('page', default=1, type=int)
        per_page = 10  # Nombre de jeux par page
        offset = (page - 1) * per_page

        cursor.execute("SELECT id, title, year_published, description FROM games ORDER BY title LIMIT %s OFFSET %s", (per_page, offset))
        games = cursor.fetchall()

        # Nombre total de pages
        total_pages = (games_count + per_page - 1) // per_page  # arrondi vers le haut

        cursor.close()
        return render_template(
        'admin_panel.html',
        stats=stats,
        logs=logs,
        users=users,
        games=games,
        current_page=page,
        total_pages=total_pages
    )

    
    # Routes pour la gestion des utilisateurs
    @app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        if not current_user.is_admin:
            flash("Accès refusé", "danger")
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if request.method == 'POST':
            is_admin = 'is_admin' in request.form
            username = request.form.get('username')
            cursor.execute("""
                UPDATE users 
                SET username = %s,
                is_admin = %s 
                WHERE id = %s
            """, (username, is_admin, user_id))
            mysql.connection.commit()
            flash("Utilisateur mis à jour", "success")
            return redirect(url_for('admin_panel'))

        cursor.close()
        return render_template('edit_user.html', user=user)

    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.is_admin:
            flash("Accès refusé", "danger")
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                flash("Utilisateur non trouvé", "danger")
                return redirect(url_for('admin_panel'))

            if result[0]:  # Si is_admin est True
                flash("Impossible de supprimer un admin", "danger")
                return redirect(url_for('admin_panel'))

            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            mysql.connection.commit()
            flash("Utilisateur supprimé avec succès", "success")

        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de la suppression: {str(e)}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('admin_panel'))


    # Routes pour la gestion des jeux
    @app.route('/admin/games/add', methods=['GET', 'POST'])
    @login_required
    def add_game():
        if not current_user.is_admin:
            flash("Accès refusé", "danger")
            return redirect(url_for('home'))

        if request.method == 'POST':
            try:
                data = request.form.to_dict()
                # Convertir les listes en strings JSON
                for field in ['category', 'mechanic', 'designer', 'publisher']:
                    if field in data:
                        data[field] = json.dumps([x.strip() for x in data[field].split(',')])

                cursor = mysql.connection.cursor()
                cursor.execute("""
                    INSERT INTO games (
                        id, title, description, year_published, min_players, 
                        max_players, playing_time, min_age, category, 
                        mechanic, designer, publisher, thumbnail
                    ) VALUES (
                        %(id)s, %(title)s, %(description)s, %(year_published)s, 
                        %(min_players)s, %(max_players)s, %(playing_time)s, 
                        %(min_age)s, %(category)s, %(mechanic)s, %(designer)s, 
                        %(publisher)s, %(thumbnail)s
                    )
                """, data)
                mysql.connection.commit()
                flash("Jeu ajouté avec succès", "success")
                return redirect(url_for('admin_panel'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Erreur: {str(e)}", "danger")

        return render_template('add_game.html')

    @app.route('/admin/games/<int:game_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_game(game_id):
        if not current_user.is_admin:
            flash("Accès refusé", "danger")
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
        game = cursor.fetchone()

        if not game:
            flash("Jeu introuvable", "danger")
            cursor.close()
            return redirect(url_for('admin_panel'))

        if request.method == 'POST':
            try:
                data = request.form.to_dict()
                data['id'] = game_id

                # Convertir les champs liste en JSON strings
                for field in ['category', 'mechanic', 'designer', 'publisher']:
                    if field in data and data[field].strip():
                        items = [x.strip() for x in data[field].split(',') if x.strip()]
                        data[field] = json.dumps(items)
                    else:
                        data[field] = json.dumps([])  # Vide = liste vide

                cursor.execute("""
                    UPDATE games SET
                        title = %(title)s,
                        description = %(description)s,
                        year_published = %(year_published)s,
                        min_players = %(min_players)s,
                        max_players = %(max_players)s,
                        playing_time = %(playing_time)s,
                        min_age = %(min_age)s,
                        category = %(category)s,
                        mechanic = %(mechanic)s,
                        designer = %(designer)s,
                        publisher = %(publisher)s,
                        thumbnail = %(thumbnail)s
                    WHERE id = %(id)s
                """, data)

                mysql.connection.commit()
                flash("Jeu mis à jour", "success")
                return redirect(url_for('admin_panel'))

            except Exception as e:
                mysql.connection.rollback()
                flash(f"Erreur: {str(e)}", "danger")

        # Préparer le jeu pour l'affichage (conversion des champs JSON en texte simple)
        game = list(game)
        for i in [8, 9, 10, 11]:  # indexes de category, mechanic, designer, publisher
            try:
                if game[i] and isinstance(game[i], str) and game[i].strip().startswith('['):
                    game[i] = ", ".join(json.loads(game[i]))
                else:
                    game[i] = ""
            except (json.JSONDecodeError, TypeError):
                game[i] = ""

        cursor.close()
        return render_template('edit_game.html', game=game)

    @app.route('/admin/games/<int:game_id>/delete', methods=['POST'])
    @login_required
    def delete_game(game_id):
        if not current_user.is_admin:
            flash("Accès refusé", "danger")
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("DELETE FROM games WHERE id = %s", (game_id,))
            mysql.connection.commit()
            flash("Jeu supprimé", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur: {str(e)}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('admin_panel'))