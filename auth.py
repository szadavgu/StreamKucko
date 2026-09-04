from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

class AuthManager:
    def __init__(self, db):
        # Megkapja a fő app.py-tól a MongoDB adatbázis kapcsolatot
        self.users_collection = db['users']

    def register_user(self, username, password, custom_bg=None):
        """Regisztrál egy új felhasználót biztonságos jelszó-titkosítással."""
        # Ellenőrizzük, létezik-e már a felhasználó
        if self.users_collection.find_one({"username": username}):
            return {"success": False, "message": "Ez a felhasználónév már foglalt!"}

        # Jelszó titkosítása (Hashing) - A nyers jelszót SOHA nem mentjük el!
        hashed_password = generate_password_hash(password)

        # Új felhasználó alapmodellje előzményekkel és preferenciákkal
        user_data = {
            "username": username,
            "password_hash": hashed_password,
            "custom_bg": custom_bg if custom_bg else "#0f1115", # Alapértelmezett sötét mód
            "history": [],      # Filmelőzmények üres listája
            "preferences": {    # Alapértelmezett preferenciák
                "favorite_genres": [],
                "kucko_mode": True
            }
        }

        self.users_collection.insert_one(user_data)
        return {"success": True, "message": "Sikeres regisztráció!"}

    def login_user(self, username, password):
        """Bejelentkezteti a felhasználót, ha a jelszó egyezik."""
        user = self.users_collection.find_one({"username": username})
        
        if user and check_password_hash(user['password_hash'], password):
            return {"success": True, "user": user}
        
        return {"success": False, "message": "Hibás felhasználónév vagy jelszó!"}

    def add_to_history(self, username, film_id, film_title):
        """Hozzáad egy filmet a felhasználó előzményeihez időbélyeggel."""
        if username == "guest":
            return # A Guest nem ment el előzményeket!

        history_entry = {
            "film_id": str(film_id),
            "title": film_title,
            "watched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Beillesztjük a history lista elejére ($position: 0), hogy a legfrissebb legyen legfelül
        self.users_collection.update_one(
            {"username": username},
            {"$push": {
                "history": {
                    "$each": [history_entry],
                    "$position": 0
                }
            }}
        )
