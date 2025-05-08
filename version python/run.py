from app import create_app
from db_init import initialize_database

initialize_database()
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
