import csv
import MySQLdb

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # adapte si besoin
DB_NAME = "playntrade"

def import_games_from_csv(csv_path):
    conn = MySQLdb.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0

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

                # éviter les doublons
                cursor.execute("SELECT id FROM games WHERE id = %s", (game_id,))
                if cursor.fetchone():
                    continue

                cursor.execute("""
                    INSERT INTO games (id, description, title, year_published, min_players, max_players,
                                       playing_time, min_age, category, mechanic, designer, publisher)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    game_id, description, title, year, min_players, max_players,
                    play_time, min_age, category, mechanic, designer, publisher
                ))
                count += 1
            except Exception as e:
                print(f"[ERREUR] Ligne ignorée : {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[IMPORT] {count} jeux importés avec succès.")

if __name__ == "__main__":
    import_games_from_csv("details.csv")
