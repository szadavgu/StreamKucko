import os
import re
from pymongo import MongoClient
# Importáljuk a különálló, javított szervizedet
from tmdb_service import keres_tmdb_adatokat

# 1. MongoDB Kapcsolat felépítése
client = MongoClient("mongodb://localhost:27017/")
db = client['film_app']

# 2. Mappa elérési útja
FILM_MAPPA = r"C:\Users\szala\Videos\Filmek"

# Támogatott videóformátumok kiterjesztései
VIDEO_KITERJESZTESEK = ('.mp4', '.mkv', '.avi', '.mov')

def fajlnev_tisztitas(fajlnev):
    """
    Eltávolítja a kiterjesztést és a tipikus felesleges karaktereket.
    """
    nev, _ = os.path.splitext(fajlnev)
    nev = re.sub(r'[\._\-]', ' ', nev)
    nev = re.sub(r'(1080p|720p|Bluray|x264|x265|h264|BDRip|WEB-DL)', '', nev, flags=re.IGNORECASE)
    nev = ' '.join(nev.split())
    return nev

def fantom_filmek_takaritasa():
    """
    Átfésüli a MongoDB-ben lévő LOKÁLIS filmeket, és ha a fájl 
    már nem létezik a lemezen, törli a rekordot az adatbázisból.
    """
    print("[*] Fantom fájlok ellenőrzése az adatbázisban...")
    lokalis_adatbazis_filmek = db.movies.find({"type": "lokális"})
    torolt_fantomok_szama = 0

    for film in lokalis_adatbazis_filmek:
        eleresi_ut = film.get("availability")
        if eleresi_ut and not os.path.exists(eleresi_ut):
            print(f"[-] Fantom film észlelve (törölve): {film['title']}")
            db.movies.delete_one({"_id": film["_id"]})
            torolt_fantomok_szama += 1
            
    if torolt_fantomok_szama > 0:
        print(f"[CLEANUP] Összesen {torolt_fantomok_szama} szellem-link eltávolítva.")
    else:
        print("[CLEANUP] Nem találtam fantom fájlokat, az adatbázis tiszta!")

def lokalis_filmek_beolvasasa():
    print(f"[*] Lokális mappa átfésülése: {FILM_MAPPA}")
    
    if not os.path.exists(FILM_MAPPA):
        print(f"[!] A megadott mappa nem létezik! Létrehozás: {FILM_MAPPA}")
        os.makedirs(FILM_MAPPA)
        return

    fantom_filmek_takaritasa()
    print("-"*40)

    talalt_filmek_szama = 0
    uj_filmek_szama = 0

    for fajl in os.listdir(FILM_MAPPA):
        if fajl.lower().endswith(VIDEO_KITERJESZTESEK):
            talalt_filmek_szama += 1
            
            tiszta_cim = fajlnev_tisztitas(fajl)
            teljes_eleresi_ut = os.path.abspath(os.path.join(FILM_MAPPA, fajl))
            
            letezo_film = db.movies.find_one({"availability": teljes_eleresi_ut})
            
            if not letezo_film:
                print(f"[~] Új fájl észlelve, részletes adatok lekérése a TMDb-ről: {tiszta_cim}...")
                
                # Meghívjuk a különálló szervizt
                tmdb_adat = keres_tmdb_adatokat(tiszta_cim)
                
                if tmdb_adat:
                    # Kinyerjük az évet a release_date első 4 karakteréből (pl. "2006-06-09" -> "2006")
                    megjelenes = tmdb_adat.get("release_date")
                    evszam = megjelenes[:4] if megjelenes and len(megjelenes) >= 4 else None

                    # Gazdag, a details.html sablonodhoz tökéletesen passzoló struktúra
                    uj_film = {
                        "title": tmdb_adat.get("title", tiszta_cim), 
                        "original_title": tmdb_adat.get("original_title"),
                        "genre": tmdb_adat.get("genre", "Lokális videó"),        
                        "type": "lokális",               
                        "availability": teljes_eleresi_ut, 
                        "description": tmdb_adat.get("overview") if tmdb_adat.get("overview") else f"Eredeti fájlnév: {fajl}",
                        "year": evszam,
                        "stars": tmdb_adat.get("cast"),
                        "director": tmdb_adat.get("director"),
                        "poster_url": f"https://image.tmdb.org/t/p/w500{tmdb_adat.get('poster_path')}" if tmdb_adat.get('poster_path') else None,
                        "backdrop_url": f"https://image.tmdb.org/t/p/original{tmdb_adat.get('backdrop_path')}" if tmdb_adat.get('backdrop_path') else None,
                        "vote_average": tmdb_adat.get("vote_average"),
                        "api_source": "TMDb"
                    }
                else:
                    # Fallback ha az API nem találná meg a filmet
                    uj_film = {
                        "title": tiszta_cim,
                        "genre": "Lokális videó",        
                        "type": "lokális",               
                        "availability": teljes_eleresi_ut, 
                        "description": f"Helyileg tárolt médiafájl. Eredeti fájlnév: {fajl}",
                        "api_source": "None"
                    }
                
                db.movies.insert_one(uj_film)
                print(f"[+] Sikeresen mentve a MongoDB-be dúsított adatokkal: {uj_film['title']}")
                uj_filmek_szama += 1

    print("\n" + "="*40)
    print(f"[OK] Szkript lefutott.")
    print(f"Aktuális fájlok a mappában: {talalt_filmek_szama}")
    print(f"Ebből újonnan adatbázisba írt: {uj_filmek_szama}")
    print("="*40)

if __name__ == "__main__":
    lokalis_filmek_beolvasasa()
