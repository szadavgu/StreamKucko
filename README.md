# StreamKuckó 🎬🧸

Üdvözlök mindenkit a **StreamKuckó** hivatalos repójában! Ez a projekt a diplomamunkám alapját képezi, egy saját fejlesztésű, kuckó-hangulatú streaming és média-kezelő alkalmazás.

> **Megjegyzés:** A projekt jelenleg **fejlesztés alatt áll**, még nem tekinthető teljes kész terméknek. A funkciók folyamatos bővítés alatt vannak.

---

## 🚀 Telepítés és Első Lépések

A projekt klónozása után az alábbi lépések szükségesek a futtatáshoz:

1. **Függőségek telepítése:**
   Bizonyosodj meg róla, hogy a szükséges Python csomagok telepítve vannak a virtuális környezetedben:
   ```bash
   pip install -r requirements.txt

2. **Környezeti változók (.env):**
   Hozz létre egy .env fájlt a gyökérben, és állítsd be a szükséges kapcsolódási paramétereket (pl. adatbázis elérés). Megjegyzés: biztonsági okokból a .env ki van zárva a verziókövetésből.

3. **Adatbázis előkészítése (Fontos!):**
   Mivel a projekt MongoDB adatbázissal dolgozik, az első használat előtt kötelező lefuttatni a mellékelt takarító scriptet, amely inicializálja és tiszta lappal indítja az adatbázist:
   ```bash
   python db_cleaner.py

4. **Az alkalmazás indítása:**
   Miután az adatbázis tiszta és elő van készítve, indítsd el a fő alkalmazást:
   ```bash
   python App.py

## 🛠️ Architektúra és Technológiák

- Backend: Flask / Python
- Adatbázis: MongoDB
- Stílus & Hangulat: 100% kuckó-kompatibilis maximális odafigyelés.

Jó kódolást és kellemes böngészést kívánok a kuckóban!

*By: Dae*
