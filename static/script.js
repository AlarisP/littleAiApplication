// Guild Request Board JavaScript

// --- Current user session (persisted in localStorage) ---

function getCurrentUserId() {
    return localStorage.getItem('guildUserId');
}

function setCurrentUserId(id) {
    localStorage.setItem('guildUserId', id);
    updateUserBar();
    loadRequests();
    loadMyRequests();
}

function clearCurrentUser() {
    localStorage.removeItem('guildUserId');
    updateUserBar();
    loadRequests();
    document.getElementById('my-requests-section').style.display = 'none';
}

function updateUserBar() {
    const userId = getCurrentUserId();
    const bar = document.getElementById('user-bar');
    if (userId) {
        fetch(`/api/users/${userId}/profile`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const u = data.user;
                    bar.innerHTML = `
                        <span>Logged in as <strong>${u.username}</strong> &nbsp;|&nbsp;
                        Lv.${u.level} &nbsp;|&nbsp; 💰 ${u.gold} Gold &nbsp;|&nbsp; ⭐ ${u.experience} XP</span>
                        <button onclick="clearCurrentUser()" class="btn-logout">Log Out</button>
                    `;
                } else {
                    localStorage.removeItem('guildUserId');
                    bar.innerHTML = '<button onclick="showSetUserForm()" class="btn btn-primary">Set User</button>';
                }
            });
    } else {
        bar.innerHTML = '<button onclick="showSetUserForm()" class="btn btn-primary">Set User</button>';
    }
}

function showSetUserForm() {
    const userId = prompt('Enter your User ID (or register first using Quick Actions):');
    if (userId && userId.trim()) {
        setCurrentUserId(userId.trim());
    }
}

// --- Request board ---

async function loadRequests() {
    try {
        const userId = getCurrentUserId();
        let activeIds = new Set();
        let declinedIds = new Set();

        if (userId) {
            const myData = await fetch(`/api/users/${userId}/requests`).then(r => r.json());
            if (myData.success) {
                myData.active_requests.forEach(r => activeIds.add(r.id));
                myData.declined_requests.forEach(r => declinedIds.add(r.id));
            }
        }

        const data = await fetch('/api/requests').then(r => r.json());
        if (!data.success) return;

        const container = document.getElementById('requests-list');
        container.innerHTML = '';

        data.requests.forEach(request => {
            if (request.status === 'completed' || request.status === 'cancelled') return;

            const card = document.createElement('div');
            card.className = 'request-card';

            const isActive = activeIds.has(request.id);
            const isDeclined = declinedIds.has(request.id);

            let actionHTML = '';
            if (!userId) {
                actionHTML = `<button class="btn-accept" data-id="${request.id}">Accept Request</button>`;
            } else if (isActive) {
                actionHTML = `<button class="btn-finish" data-id="${request.id}">Finish Request</button>`;
            } else if (isDeclined) {
                actionHTML = `<span class="declined-label">Declined</span>`;
            } else {
                actionHTML = `
                    <div class="card-actions">
                        <button class="btn-accept" data-id="${request.id}">Accept</button>
                        <button class="btn-decline" data-id="${request.id}">Decline</button>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="request-header">
                    <h3></h3>
                    <span class="difficulty ${request.difficulty}">${request.difficulty}</span>
                </div>
                <p class="request-description"></p>
                <div class="request-meta">
                    <span class="type">${request.request_type}</span>
                    <span class="status">${request.status}</span>
                </div>
                <div class="reward-info">
                    <span class="gold">💰 ${request.reward.gold} Gold</span>
                    <span class="exp">⭐ ${request.reward.experience} EXP</span>
                </div>
                ${actionHTML}
            `;

            // Set text safely to avoid XSS
            card.querySelector('.request-header h3').textContent = request.title;
            card.querySelector('.request-description').textContent = request.description;

            const acceptBtn = card.querySelector('.btn-accept');
            if (acceptBtn) {
                acceptBtn.addEventListener('click', () => acceptRequest(acceptBtn.dataset.id));
            }
            const declineBtn = card.querySelector('.btn-decline');
            if (declineBtn) {
                declineBtn.addEventListener('click', () => declineRequest(declineBtn.dataset.id));
            }
            const finishBtn = card.querySelector('.btn-finish');
            if (finishBtn) {
                finishBtn.addEventListener('click', () => finishRequest(finishBtn.dataset.id));
            }

            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading requests:', error);
    }
}

async function loadMyRequests() {
    const userId = getCurrentUserId();
    const section = document.getElementById('my-requests-section');
    if (!userId) {
        section.style.display = 'none';
        return;
    }

    try {
        const data = await fetch(`/api/users/${userId}/requests`).then(r => r.json());
        if (!data.success) return;

        section.style.display = 'block';

        renderMyList('my-active-list', data.active_requests, 'active');
        renderMyList('my-declined-list', data.declined_requests, 'declined');
        renderMyList('my-completed-list', data.completed_requests, 'completed');
    } catch (error) {
        console.error('Error loading my requests:', error);
    }
}

function renderMyList(containerId, requests, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (!requests || requests.length === 0) {
        container.innerHTML = '<p class="empty-list">None yet.</p>';
        return;
    }

    requests.forEach(r => {
        const item = document.createElement('div');
        item.className = `my-request-item my-request-${type}`;

        let actionHTML = '';
        if (type === 'active') {
            actionHTML = `<button class="btn-finish btn-sm" data-id="${r.id}">Finish</button>`;
        }

        item.innerHTML = `
            <div class="my-request-info">
                <strong></strong>
                <span class="difficulty ${r.difficulty}">${r.difficulty}</span>
            </div>
            <div class="my-request-reward">
                <span class="gold">💰 ${r.reward.gold}</span>
                <span class="exp">⭐ ${r.reward.experience}</span>
            </div>
            ${actionHTML}
        `;
        item.querySelector('strong').textContent = r.title;

        const finishBtn = item.querySelector('.btn-finish');
        if (finishBtn) {
            finishBtn.addEventListener('click', () => finishRequest(finishBtn.dataset.id));
        }

        container.appendChild(item);
    });
}

// --- Actions ---

async function acceptRequest(requestId) {
    let userId = getCurrentUserId();
    if (!userId) {
        userId = prompt('Enter your User ID:');
        if (!userId) return;
    }

    try {
        const data = await fetch(`/api/requests/${requestId}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
        }).then(r => r.json());

        if (data.success) {
            await loadRequests();
            await loadMyRequests();
            updateUserBar();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error accepting request: ' + error);
    }
}

async function declineRequest(requestId) {
    let userId = getCurrentUserId();
    if (!userId) {
        userId = prompt('Enter your User ID:');
        if (!userId) return;
    }

    try {
        const data = await fetch(`/api/requests/${requestId}/decline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
        }).then(r => r.json());

        if (data.success) {
            await loadRequests();
            await loadMyRequests();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error declining request: ' + error);
    }
}

async function finishRequest(requestId) {
    let userId = getCurrentUserId();
    if (!userId) {
        userId = prompt('Enter your User ID:');
        if (!userId) return;
    }

    try {
        const data = await fetch(`/api/requests/${requestId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
        }).then(r => r.json());

        if (data.success) {
            alert(`Request completed! +${data.reward.gold} Gold, +${data.reward.experience} EXP`);
            await loadRequests();
            await loadMyRequests();
            updateUserBar();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error finishing request: ' + error);
    }
}

// --- User / Guild management ---

function showRegisterForm() {
    const username = prompt('Enter username:');
    if (!username) return;
    registerUser(username);
}

async function registerUser(username) {
    try {
        const data = await fetch('/api/users/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username }),
        }).then(r => r.json());

        if (data.success) {
            alert(`Registered! User ID: ${data.user_id}\n\nYou are now logged in as ${username}.`);
            setCurrentUserId(data.user_id);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error registering user: ' + error);
    }
}

function showCreateGuildForm() {
    const name = prompt('Enter guild name:');
    if (!name) return;
    const description = prompt('Enter guild description:');
    createGuild(name, description);
}

async function createGuild(name, description) {
    try {
        const data = await fetch('/api/guilds', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description }),
        }).then(r => r.json());

        if (data.success) {
            alert(`Guild created! Guild ID: ${data.guild_id}`);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error creating guild: ' + error);
    }
}

async function saveBoard() {
    try {
        const data = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        }).then(r => r.json());

        if (data.success) {
            alert(data.message);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error saving board: ' + error);
    }
}

async function loadBoard() {
    try {
        const data = await fetch('/api/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        }).then(r => r.json());

        if (data.success) {
            alert(data.message);
            await loadRequests();
            await loadMyRequests();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading board: ' + error);
    }
}

// --- Background music ---

function initMusic() {
    const music = document.getElementById('bg-music');
    const toggle = document.getElementById('music-toggle');
    const banner = document.getElementById('music-banner');

    music.volume = 0.4;

    // Try autoplay immediately
    music.play().then(() => {
        toggle.textContent = '🔊';
    }).catch(() => {
        // Autoplay blocked — show banner and wait for first interaction
        banner.style.display = 'block';
        const startOnInteraction = () => {
            music.play().then(() => {
                toggle.textContent = '🔊';
                banner.style.display = 'none';
            });
            document.removeEventListener('click', startOnInteraction);
            document.removeEventListener('keydown', startOnInteraction);
        };
        document.addEventListener('click', startOnInteraction);
        document.addEventListener('keydown', startOnInteraction);
    });

    toggle.addEventListener('click', (e) => {
        e.stopPropagation(); // don't trigger the interaction listener
        if (music.paused) {
            music.play();
            toggle.textContent = '🔊';
        } else {
            music.pause();
            toggle.textContent = '🔇';
        }
    });
}

// --- Init ---

document.addEventListener('DOMContentLoaded', () => {
    initMusic();
    updateUserBar();
    loadRequests();
    loadMyRequests();
});
