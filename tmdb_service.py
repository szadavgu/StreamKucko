import requests

TMDB_API_KEY = "606b754c4d136e7b4648ab95b83f4768"

def keres_tmdb_adatokat(film_cim):
    """
    Lekéri egy film részletes metaadatait, műfajait és stáblistáját a TMDb API-ról.
    """
    # 1. lépés: Keresés a cím alapján
    keres_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={film_cim}&language=hu-HU"
    
    try:
        response = requests.get(keres_url, timeout=5)
        response.raise_for_status()
        keres_eredmeny = response.json()
        
        if not keres_eredmeny.get('results'):
            return None
            
        # Megvan a legrelevánsabb film, kikapjuk az ID-ját
        film_id = keres_eredmeny['results'][0]['id']
        
        # 2. lépés: Részletes adatlap + Stáblista (credits) lekérése egy füst alatt
        reszletes_url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={TMDB_API_KEY}&language=hu-HU&append_to_response=credits"
        
        reszletes_resp = requests.get(reszletes_url, timeout=5)
        reszletes_resp.raise_for_status()
        film_adatok = reszletes_resp.json()
        
        # Műfajok összefűzése (pl.: "Animációs, Kaland, Családi")
        mufajok = [g['name'] for g in film_adatok.get('genres', [])]
        mufaj_szoveg = ", ".join(mufajok) if mufajok else "Lokális videó"
        
        # Stáblista feldolgozása (Rendező + Top 5 Szereplő)
        credits = film_adatok.get('credits', {})
        
        # Megkeressük a rendezőt (Director)
        rendezok = [tag['name'] for tag in credits.get('crew', []) if tag.get('job') == 'Director']
        rendezo_szoveg = ", ".join(rendezok) if rendezok else "Nincs megadva"
        
        # Kivesszük az első 5 színészt
        szineszek = [szinesz['name'] for szinesz in credits.get('cast', [])[:5]]
        szereplok_szoveg = ", ".join(szineszek) if szineszek else "Nincs megadva"
        
        # Összerakjuk a dúsított adatcsomagot
        return {
            "title": film_adatok.get("title"),
            "original_title": film_adatok.get("original_title"),
            "overview": film_adatok.get("overview"),
            "release_date": film_adatok.get("release_date"),
            "poster_path": film_adatok.get("poster_path"),
            "backdrop_path": film_adatok.get("backdrop_path"),
            "vote_average": film_adatok.get("vote_average"),
            "genre": mufaj_szoveg,
            "director": rendezo_szoveg,
            "cast": szereplok_szoveg
        }
            
    except requests.exceptions.RequestException as e:
        print(f"[!] TMDb részletes API hiba ({film_cim}): {e}")
        
    return None
