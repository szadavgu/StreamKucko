fetch('/api/filmek')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('film-tabla-test'); 
        if (!tableBody) return;
        
        tableBody.innerHTML = ''; 

        data.forEach(movie => {
            // Biztonságos MongoDB ID kinyerés
            const filmId = movie._id.$oid ? movie._id.$oid : movie._id;

            // Rövidítjük az elérési utat, hogy csak a fájlnevet mutassa a táblázatban
            let rovid_elerhetoseg = "Helyi média";
            if (movie.availability) {
                rovid_elerhetoseg = movie.availability.replace(/\\/g, '/').split('/').pop();
            }

            // JAVÍTÁS: Kivettük a style="color: #212529;" részt! 
            // Mostantól a .film-link-stilus osztály mindent visz a style.css-ből!
            const row = `
                <tr>
                    <td>
                        <a href="/film/${filmId}" class="film-link-stilus">
                            ${movie.title}
                        </a>
                    </td>
                    <td>${movie.genre || 'Nincs megadva'}</td>
                    <td><span class="badge ${movie.type}">${movie.type}</span></td>
                    <td class="path-cell" title="${movie.availability}">${rovid_elerhetoseg}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    })
    .catch(error => console.error("Hiba történt a filmek betöltésekor:", error));
