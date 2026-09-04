from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db = client['film_app']
    
    # Teljesen eldobjuk a kollekciót, nincs kegyelem a régi adatoknak
    db.movies.drop()
    print("[*] A 'movies' kollekció sikeresen kiürítve. Tiszta lap!")
    
    # Újraépítjük a tiszta egyedi indexet
    db.movies.create_index("availability", unique=True)
    print("[*] Egyedi adatbázis index létrehozva az 'availability' mezőre.")
    
    print("\n[OK] Az adatbázis teljesen tiszta, készen áll a szinkronizációra!")
except Exception as e:
    print(f"[!] Hiba az inicializálás során: {e}")
