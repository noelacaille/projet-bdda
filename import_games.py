import csv
import MySQLdb

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # Adaptez si besoin
DB_NAME = "playntrade"

def import_games_from_csv(csv_path, ratings_csv_path):
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    # 1. Chargement des thumbnails depuis ratings.csv
    thumbnails = {}
    with open(ratings_csv_path, newline='', encoding='utf-8') as ratingsfile:
        reader = csv.DictReader(ratingsfile)
        for row in reader:
            try:
                game_id = int(row['id'])
                thumbnail = row.get('thumbnail', '')
                if thumbnail:
                    thumbnails[game_id] = thumbnail
            except (KeyError, ValueError) as e:
                print(f"[ERREUR] Ligne ignorée dans ratings.csv : {e}")

    # 2. Import des jeux depuis details.csv
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        new_count = 0

        for row in reader:
            try:
                game_id = int(row['id'])
                description = row.get('description') or ''
                title = row.get('primary') or ''
                year = int(row['yearpublished']) if row['yearpublished'].isdigit() else None
                min_players = int(row['minplayers']) if row['minplayers'].isdigit() else None
                max_players = int(row['maxplayers']) if row['maxplayers'].isdigit() else None
                play_time = int(row['playingtime']) if row['playingtime'].isdigit() else None
                min_age = int(row['minage']) if row['minage'].isdigit() else None
                category = row.get('boardgamecategory', '')
                mechanic = row.get('boardgamemechanic', '')
                designer = row.get('boardgamedesigner', '')
                publisher = row.get('boardgamepublisher', '')
                
                # Récupération du thumbnail
                thumbnail = thumbnails.get(game_id, '')

                # Vérification doublon
                cursor.execute("SELECT id FROM games WHERE id = %s", (game_id,))
                if cursor.fetchone():
                    continue

                # Insertion avec thumbnail
                cursor.execute("""
                    INSERT INTO games 
                    (id, description, title, year_published, min_players, max_players,
                     playing_time, min_age, category, mechanic, designer, publisher, thumbnail)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (game_id, description, title, year, min_players, max_players, 
                      play_time, min_age, category, mechanic, designer, publisher, thumbnail))
                new_count += 1

            except Exception as e:
                print(f"[ERREUR] Ligne ignorée : {e}")

    # 4. Mise à jour des thumbnails pour les jeux existants
    update_count = 0
    for game_id, thumbnail in thumbnails.items():
        try:
            cursor.execute("""
                UPDATE games 
                SET thumbnail = %s 
                WHERE id = %s AND (thumbnail IS NULL OR thumbnail = '')
            """, (thumbnail, game_id))
            update_count += cursor.rowcount
        except Exception as e:
            print(f"[ERREUR] Mise à jour thumbnail pour {game_id} : {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[IMPORT] {new_count} nouveaux jeux ajoutés.")
    print(f"[IMPORT] {update_count} thumbnails mis à jour.")

if __name__ == "__main__":
    import_games_from_csv("details.csv", "ratings.csv")