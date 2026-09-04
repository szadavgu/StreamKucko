document.addEventListener("DOMContentLoaded", () => {
    fetchUsers();
});

async function fetchUsers() {
    try {
        const response = await fetch('/api/admin/users');
        if (!response.ok) throw new Error('Hiba történt az adatok lekérésekor!');
        
        const users = await response.json();
        const tbody = document.getElementById('userTableBody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td><span style="color: ${user.is_banned ? '#ff4c4c' : '#66fcf1'}">${user.is_banned ? 'Tiltva' : 'Aktív'}</span></td>
                <td>
                    <button class="btn-action" onclick="toggleBan('${user._id}', ${user.is_banned})">
                        ${user.is_banned ? 'Feloldás' : 'Tiltás'}
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteUser('${user._id}', '${user.username}')" style="background-color: #ff4c4c; color: white; margin-left: 5px;">
                        Törlés
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Hiba:', error);
    }
}

async function toggleBan(userId, currentStatus) {
    const action = currentStatus ? 'unban' : 'ban';
    const response = await fetch(`/api/admin/user/${userId}/${action}`, {
        method: 'POST'
    });
    
    if (response.ok) {
        fetchUsers(); // Frissítjük a táblázatot
    } else {
        alert('Nem sikerült végrehajtani a műveletet.');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Biztosan törölni akarod ezt a felhasználót: ${username}?`)) {
        return;
    }

    const response = await fetch(`/api/admin/user/${userId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        fetchUsers(); // Újratöltjük a listát, így teszt_jano elköszön
    } else {
        alert('Nem sikerült törölni a felhasználót.');
    }
}
