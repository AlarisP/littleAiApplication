// Guild Request Board JavaScript

// --- System guild (set on load) ---
let systemGuildId = null;

async function loadSystemGuild() {
    const data = await fetch('/api/system-guild').then(r => r.json());
    if (data.success) systemGuildId = data.guild_id;
}

// --- Current user session (persisted in localStorage) ---

function getCurrentUserId() {
    return localStorage.getItem('guildUserId');
}

async function setCurrentUserId(id) {
    localStorage.setItem('guildUserId', id);
    updateUserBar();
    await loadRequests();
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
                        <span>Welcome, <strong>${u.username}</strong> &nbsp;|&nbsp;
                        Lv.${u.level} &nbsp;|&nbsp; 💰 ${u.gold} Gold &nbsp;|&nbsp; ⭐ ${u.experience} XP</span>
                        <button onclick="clearCurrentUser()" class="btn-logout">Log Out</button>
                    `;
                } else {
                    // Stale ID (server restarted) — clear it and refresh board state
                    localStorage.removeItem('guildUserId');
                    bar.innerHTML = '<button onclick="showLoginModal()" class="btn btn-primary">Join / Log In</button>';
                    loadRequests();
                }
            });
    } else {
        bar.innerHTML = '<button onclick="showLoginModal()" class="btn btn-primary">Join / Log In</button>';
    }
}

// --- Login / Register modal ---

let _pendingAction = null;

function showLoginModal(afterLogin) {
    _pendingAction = afterLogin || null;
    document.getElementById('login-modal').style.display = 'flex';
    setTimeout(() => document.getElementById('login-username').focus(), 50);
}

function closeLoginModal() {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('login-username').value = '';
}

async function submitLogin() {
    const username = document.getElementById('login-username').value.trim();
    if (!username) return;

    try {
        // Try login first
        let data = await fetch('/api/users/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username }),
        }).then(r => r.json());

        if (!data.success) {
            // Not found — register as new adventurer
            data = await fetch('/api/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username }),
            }).then(r => r.json());
        }

        if (data.success) {
            closeLoginModal();
            await setCurrentUserId(data.user_id);
            // Execute any pending action (e.g. accept a request they clicked before logging in)
            if (_pendingAction) {
                const action = _pendingAction;
                _pendingAction = null;
                action();
            }
        } else {
            alert('Could not join: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error);
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

            const isOwner = userId && request.posted_by_user === userId;

            let actionHTML = '';
            if (isActive) {
                actionHTML = `<button class="btn-finish" data-id="${request.id}">Finish Request</button>`;
            } else if (request.status === 'in_progress') {
                actionHTML = `<span class="taken-label">⚔️ In Progress</span>`;
            } else if (!userId) {
                actionHTML = `<button class="btn-accept" data-id="${request.id}">Accept Request</button>`;
            } else if (isDeclined) {
                actionHTML = `<span class="declined-label">Declined</span>`;
            } else if (isOwner) {
                actionHTML = `<button class="btn-delete" data-id="${request.id}">Delete Request</button>`;
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
            const deleteBtn = card.querySelector('.btn-delete');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => deleteRequest(deleteBtn.dataset.id));
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
    const userId = getCurrentUserId();
    if (!userId) {
        showLoginModal(() => acceptRequest(requestId));
        return;
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
        } else if (data.error === 'session_expired') {
            localStorage.removeItem('guildUserId');
            await loadRequests();
            showLoginModal(() => acceptRequest(requestId));
        } else {
            alert(data.error);
            await loadRequests();
        }
    } catch (error) {
        alert('Server error — please refresh the page and try again.');
        await loadRequests();
    }
}

async function declineRequest(requestId) {
    const userId = getCurrentUserId();
    if (!userId) {
        showLoginModal(() => declineRequest(requestId));
        return;
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
        } else if (data.error === 'session_expired') {
            localStorage.removeItem('guildUserId');
            await loadRequests();
            showLoginModal(() => declineRequest(requestId));
        } else {
            alert(data.error);
            await loadRequests();
        }
    } catch (error) {
        alert('Server error — please refresh the page and try again.');
        await loadRequests();
    }
}

async function finishRequest(requestId) {
    const userId = getCurrentUserId();
    if (!userId) {
        showLoginModal();
        return;
    }

    try {
        const data = await fetch(`/api/requests/${requestId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
        }).then(r => r.json());

        if (data.success) {
            alert(`Request completed! +${data.reward.gold} Gold, +${data.reward.experience} EXP`);

            const total = (parseInt(localStorage.getItem('guildTotalCompleted') || '0')) + 1;
            localStorage.setItem('guildTotalCompleted', total);
            if (total % 10 === 0) playWellArmedPeasants();

            await loadRequests();
            await loadMyRequests();
            updateUserBar();
        } else if (data.error === 'session_expired') {
            localStorage.removeItem('guildUserId');
            await loadRequests();
            showLoginModal();
        } else {
            alert(data.error);
            await loadRequests();
        }
    } catch (error) {
        alert('Server error — please refresh the page and try again.');
        await loadRequests();
    }
}

// --- Guild management ---

function showCreateGuildForm() {
    const name = prompt('Enter guild name:');
    if (!name) return;
    const description = prompt('Enter guild description (optional):') || '';
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
            alert(`Guild "${name}" created!`);
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

// --- Post / Delete requests ---

function showPostRequestModal() {
    if (!getCurrentUserId()) {
        showLoginModal(() => showPostRequestModal());
        return;
    }
    document.getElementById('post-request-modal').style.display = 'flex';
}

function closePostRequestModal() {
    document.getElementById('post-request-modal').style.display = 'none';
}

async function submitPostRequest() {
    const userId = getCurrentUserId();
    if (!userId) return;

    const title = document.getElementById('pr-title').value.trim();
    const description = document.getElementById('pr-description').value.trim();
    const type = document.getElementById('pr-type').value;
    const difficulty = document.getElementById('pr-difficulty').value;
    const gold = parseInt(document.getElementById('pr-gold').value) || 0;
    const exp = parseInt(document.getElementById('pr-exp').value) || 0;

    if (!title || !description) {
        alert('Please fill in the title and description.');
        return;
    }

    try {
        const data = await fetch('/api/requests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                guild_id: systemGuildId,
                user_id: userId,
                title,
                description,
                type,
                difficulty,
                reward_gold: gold,
                reward_experience: exp,
            }),
        }).then(r => r.json());

        if (data.success) {
            closePostRequestModal();
            document.getElementById('pr-title').value = '';
            document.getElementById('pr-description').value = '';
            await loadRequests();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error posting request: ' + error);
    }
}

async function deleteRequest(requestId) {
    if (!confirm('Delete this request? This cannot be undone.')) return;

    const userId = getCurrentUserId();
    try {
        const data = await fetch(`/api/requests/${requestId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
        }).then(r => r.json());

        if (data.success) {
            await loadRequests();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error deleting request: ' + error);
    }
}

// --- Background music ---

let chosenTrack = 'medieval'; // 'medieval' or 'one_hour'
let jinglePlaying = false;

function getTrackUrl(track) {
    return track === 'one_hour'
        ? '/static/one_hour_medieval.mp3'
        : '/static/medieval_inn_music.mp3';
}

function updateMusicSelectorUI() {
    document.querySelectorAll('.music-option').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.track === chosenTrack);
    });
}

function switchTrack(track) {
    chosenTrack = track;
    localStorage.setItem('guildMusicChoice', track);
    updateMusicSelectorUI();

    if (jinglePlaying) return; // will resume correct track after jingle ends

    const bgMusic = document.getElementById('bg-music');
    const wasPlaying = !bgMusic.paused;
    bgMusic.src = getTrackUrl(track);
    bgMusic.loop = true;
    if (wasPlaying) bgMusic.play();
}

function startBgMusic() {
    const bgMusic = document.getElementById('bg-music');
    const toggle = document.getElementById('music-toggle');
    const banner = document.getElementById('music-banner');

    bgMusic.src = getTrackUrl(chosenTrack);
    bgMusic.loop = true;
    bgMusic.volume = 0.4;

    bgMusic.play().then(() => {
        toggle.textContent = '🔊';
        banner.style.display = 'none';
    }).catch(() => {
        banner.style.display = 'block';
        const startOnInteraction = () => {
            bgMusic.play().then(() => {
                toggle.textContent = '🔊';
                banner.style.display = 'none';
            });
            document.removeEventListener('click', startOnInteraction);
            document.removeEventListener('keydown', startOnInteraction);
        };
        document.addEventListener('click', startOnInteraction);
        document.addEventListener('keydown', startOnInteraction);
    });
}

function playIntroThenBg() {
    const intro = new Audio('/static/never.mp3');
    intro.volume = 0.5;
    intro.currentTime = 50;

    const onTimeUpdate = () => {
        if (intro.currentTime >= 90) {
            intro.pause();
            intro.removeEventListener('timeupdate', onTimeUpdate);
            startBgMusic();
        }
    };

    intro.addEventListener('loadedmetadata', () => {
        intro.currentTime = 50;
    }, { once: true });

    intro.addEventListener('timeupdate', onTimeUpdate);
    intro.addEventListener('ended', startBgMusic, { once: true });

    intro.play().catch(() => {
        // Autoplay blocked — skip intro and go straight to bg music
        intro.removeEventListener('timeupdate', onTimeUpdate);
        startBgMusic();
    });
}

function playWellArmedPeasants() {
    const bgMusic = document.getElementById('bg-music');
    const toggle = document.getElementById('music-toggle');
    const wasPaused = bgMusic.paused;

    jinglePlaying = true;
    bgMusic.pause();

    const jingle = new Audio('/static/well_armed_peasants.mp3');
    jingle.volume = 0.7;

    jingle.addEventListener('ended', () => {
        jinglePlaying = false;
        bgMusic.src = getTrackUrl(chosenTrack);
        bgMusic.loop = true;
        if (!wasPaused) {
            bgMusic.play().then(() => { toggle.textContent = '🔊'; });
        }
    }, { once: true });

    jingle.play().catch(() => {
        jinglePlaying = false;
    });
}

function initMusic() {
    const bgMusic = document.getElementById('bg-music');
    const toggle = document.getElementById('music-toggle');

    chosenTrack = localStorage.getItem('guildMusicChoice') || 'medieval';
    updateMusicSelectorUI();

    bgMusic.volume = 0.4;

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        if (bgMusic.paused) {
            bgMusic.play();
            toggle.textContent = '🔊';
        } else {
            bgMusic.pause();
            toggle.textContent = '🔇';
        }
    });

    // Play Never.mp3 intro (0:50–1:30) on first visit this session
    if (!sessionStorage.getItem('introPlayed')) {
        sessionStorage.setItem('introPlayed', '1');
        playIntroThenBg();
    } else {
        startBgMusic();
    }
}

// --- Init ---

document.addEventListener('DOMContentLoaded', () => {
    initMusic();
    loadSystemGuild();
    updateUserBar();
    loadRequests();
    loadMyRequests();
});
