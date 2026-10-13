"""
=========================================================================================
 PROJEKT CÍM: Esti kikapcsolódást támogató, filmajánló webalkalmazás (StreamKuckó)
=========================================================================================
 Modul neve: App.py (Fő backend vezérlő / Entry Point)
 Készítő: Szalanics Dávid (Neptun: UTSY4C)
 Témavezető: Dr. Szathmáry László
 Intézmény: Debreceni Egyetem – Informatikai Kar (Műszaki Informatikus BSc)

 Leírás:
   A Flask-alapú webalkalmazás fő vezérlő modulja. Kezeli a routingot, a HTTP kéréseket,
   a felhasználói munkameneteket (Session), az autentikációt, valamint a MongoDB
   adatbázis-műveleteket és az adminisztrációs végpontokat.

 Felhasznált technológiák:
   - Python 3.x, Flask, Flask-PyMongo
   - MongoDB (NoSQL)
   - Dotenv (Környezeti változók kezelése)

 Hibakódok / HTTP Státuszok ezen modulban:
   - 200: Sikeres művelet / lekérdezés
   - 403: Hozzáférés megtagadva (Jogosultság hiánya / nem admin)
   - 404: Erőforrás (film vagy felhasználó) nem található
   - 500: Szerverhiba / kivételkezelés az adatbázis-műveletek során

 Verzió: Beta 0.0

 Eddigi verziók:
 - Alpha 0.0 (25. 06. 16)
 - Alpha 1.0 (25. 07. 09)
 - Beta 0.0 (26. 04. 21)
 - Beta 1.0 (26. 05. 16)
 HARD RESET
 - Alpha 0.0 (26. 05. 16)
 - Alpha 0.1 (26. 05. 18)
 - Alpha 0.2 (26. 05. 19)
 - Beta 0.0 (26. 10. 13.)

 Utolsó módosítás ideje: 2026. 10. 13.
=========================================================================================
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort
from flask_pymongo import PyMongo
from auth import AuthManager 
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv() # Betölti a .env fájlt

ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "default_pass")

# --- ATOMBIZTOS BELŐ ÚTVONALAK ---
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

# EGYSZER inicializáld!
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.urandom(24)

# --- MongoDB ---
app.config["MONGO_URI"] = "mongodb://localhost:27017/film_app" # Itt legyen 'film_app'!
mongo = PyMongo(app)
db = mongo.db

# Inicializáljuk az AuthManagert az adatbázisunkkal
auth = AuthManager(db)
# --- UTALÁSOK ÉS ROUTING ---

@app.route('/')
def index():
    """A Belépő kapu. Ha már be van lépve, egyből a főoldalra dobja."""
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('index.html') # Ez a login felületed!

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # 1. Ellenőrizzük, hogy az admin próbál-e belépni a .env adatokkal
    if username == ADMIN_USER and password == ADMIN_PASS:
        session['user'] = username
        session['is_admin'] = True  # Admin jog megadva!
        session['custom_bg'] = 'hatter.jpg'
        return redirect(url_for('admin_dashboard'))

    # 2. Ha nem admin, fut a sima user ellenőrzés az AuthManagerrel:
    result = auth.login_user(username, password)
    if result['success']:
        session['user'] = username
        session['is_admin'] = False # Sima user nem admin
        session['custom_bg'] = result['user']['custom_bg']
        return redirect(url_for('home'))
    else:
        return render_template('error.html', message=result['message'])

@app.route('/login-guest')
def login_guest():
    """Vendég mód aktiválása. Nem ment semmit, megkapja a hatter.jpg-t."""
    session['user'] = 'guest'
    session['custom_bg'] = 'hatter.jpg' # A hűséges hatter.jpg dedikáltan a Guesté!
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        custom_bg = request.form.get('custom_bg')
        
        result = auth.register_user(username, password, custom_bg)
        if result['success']:
            return redirect(url_for('index'))
        else:
            # ITT A JAVÍTÁS:
            return render_template('error.html', message=result['message'])
    return render_template('register.html')

@app.route('/home')
def home():
    """A Főoldal (a régi index.html, most már home.html)."""
    if 'user' not in session:
        return redirect(url_for('index')) # Ha nincs belépve, irány a login!
    
    # Átadjuk a sessionben tárolt egyedi hátteret a HTML-nek
    return render_template('home.html', 
                           username=session['user'], 
                           bg_image=session['custom_bg'])

@app.route('/logout')
def logout():
    session.clear() # Munkamenet törlése
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('admin.html', username=session.get('user'))

# --- KERESÉS ÉS API VÉGPONTOK (Ezek kellenek, hogy működjön a kereső!) ---

@app.route('/api/filmek')
def get_filmek():
    # .movies-t kérdezz le!
    filmek = list(db.movies.find()) 
    for film in filmek:
        film['_id'] = str(film['_id'])
    return jsonify(filmek)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Keresés a 'title' mezőben (MongoDB regex használatával)
    results = list(db.movies.find({"title": {"$regex": query, "$options": "i"}}))
    for r in results:
        r['_id'] = str(r['_id'])
    return jsonify(results)

# Amikor valaki megnyit egy filmet, elmentjük az előzményeibe!
@app.route('/film/<film_id>')
def film_details(film_id):
    if 'user' not in session:
        return redirect(url_for('index'))

    # Itt kell a .movies!
    film = db.movies.find_one({"_id": ObjectId(film_id)})
    
    if film:
        auth.add_to_history(session['user'], film_id, film.get('title', 'Ismeretlen film'))
        return render_template('details.html', film=film)
    return "A film nem található", 404

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    # Ellenőrizzük, hogy admin-e a felhasználó
    # (Itt majd a session-ben vagy az AuthManagerben ellenőrizzük a jogkört)
    if not session.get('is_admin'):
        return jsonify({"error": "Hozzáférés megtagadva!"}), 403

    try:
        # Lekérjük a felhasználókat a gyűjteményből
        users_cursor = db.users.find({})
        users_list = []

        for user in users_cursor:
            users_list.append({
                "_id": str(user.get("_id")),
                "username": user.get("username"),
                "email": user.get("email", "Nincs megadva"),
                "role": user.get("role", "user"),
                "is_banned": user.get("is_banned", False)
            })

        return jsonify(users_list), 200

    except Exception as e:
        print(f"Hiba az admin felhasználók lekérdezésekor: {e}")
        return jsonify({"error": "Szerverhiba történt."}), 500
    
@app.route('/api/admin/user/<user_id>/<action>', methods=['POST'])
def admin_toggle_ban(user_id, action):
    if not session.get('is_admin'):
        return jsonify({"error": "Hozzáférés megtagadva!"}), 403

    try:
        # Eldöntjük, hogy tiltani vagy feloldani kell-e
        is_banned_status = True if action == 'ban' else False
        
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_banned": is_banned_status}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "A felhasználó nem található."}), 404

        return jsonify({"success": True, "is_banned": is_banned_status}), 200

    except Exception as e:
        print(f"Hiba a státusz módosításakor: {e}")
        return jsonify({"error": "Szerverhiba történt."}), 500
    
@app.route('/api/admin/user/<user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        return jsonify({"error": "Hozzáférés megtagadva!"}), 403

    try:
        result = db.users.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            return jsonify({"error": "A felhasználó nem található."}), 404

        return jsonify({"success": True, "message": "Felhasználó sikeresen törölve."}), 200

    except Exception as e:
        print(f"Hiba a felhasználó törlésekor: {e}")
        return jsonify({"error": "Szerverhiba történt."}), 500

# --- A FLASK MOTOR BEINDÍTÁSA ---
if __name__ == '__main__':
    from lokalis_kereso import lokalis_filmek_beolvasasa
    lokalis_filmek_beolvasasa()
    app.run(debug=True)
