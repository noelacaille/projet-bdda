from app import create_app
from db_init import initialize_database
from import_games import import_games_from_csv

IMPORT_GAMES = False

initialize_database()
if IMPORT_GAMES:
    import_games_from_csv("version python/details.csv", "version python/ratings.csv")
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
