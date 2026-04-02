// Guild Request Board JavaScript

async function acceptRequest(requestId) {
    const userId = prompt('Enter your User ID:');
    if (!userId) return;

    try {
        const response = await fetch(`/api/requests/${requestId}/accept`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json();
        if (data.success) {
            alert('Request accepted successfully!');
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error accepting request: ' + error);
    }
}

function showRegisterForm() {
    const username = prompt('Enter username:');
    if (!username) return;

    registerUser(username);
}

async function registerUser(username) {
    try {
        const response = await fetch('/api/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username }),
        });

        const data = await response.json();
        if (data.success) {
            alert(`User registered successfully! User ID: ${data.user_id}`);
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
        const response = await fetch('/api/guilds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, description: description }),
        });

        const data = await response.json();
        if (data.success) {
            alert(`Guild created successfully! Guild ID: ${data.guild_id}`);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error creating guild: ' + error);
    }
}

async function saveBoard() {
    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();
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
        const response = await fetch('/api/load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading board: ' + error);
    }
}

// Fetch and display requests
async function loadRequests() {
    try {
        const response = await fetch('/api/requests');
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('requests-list');
            container.innerHTML = '';

            data.requests.forEach(request => {
                const card = document.createElement('div');
                card.className = 'request-card';
                card.innerHTML = `
                    <div class="request-header">
                        <h3>${request.title}</h3>
                        <span class="difficulty ${request.difficulty}">${request.difficulty}</span>
                    </div>
                    <p class="request-description">${request.description}</p>
                    <div class="request-meta">
                        <span class="type">${request.request_type}</span>
                        <span class="status">${request.status}</span>
                    </div>
                    <div class="reward-info">
                        <span class="gold">💰 ${request.reward.gold} Gold</span>
                        <span class="exp">⭐ ${request.reward.experience} EXP</span>
                    </div>
                    <button class="btn-accept" data-id="${request.id}">Accept Request</button>
                `;
                card.querySelector('.btn-accept').addEventListener('click', function() {
                    acceptRequest(this.dataset.id);
                });
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading requests:', error);
    }
}

// Load requests on page load
document.addEventListener('DOMContentLoaded', loadRequests);
