from main import app
from setup import setup_db

if __name__ == "__main__":
    setup_db()
    app.run()