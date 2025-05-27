from app import create_app
from db_init import initialize_database
from import_games import import_games_from_csv

IMPORT_GAMES = True

initialize_database()
if IMPORT_GAMES:
    import_games_from_csv("details.csv", "ratings.csv")
app = create_app()

@app.template_filter('to_list')
def to_list_filter(s):
    if s is None:
        return []
    if isinstance(s, str):
        # Si c'est une chaîne, on la retourne telle quelle
        return [s]
    return list(s)

if __name__ == "__main__":
    app.run(debug=True)
