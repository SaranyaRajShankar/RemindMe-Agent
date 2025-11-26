// API base URL
const API_BASE = '/api';

// DOM elements
const connectBtn = document.getElementById('connectBtn');
const refreshBtn = document.getElementById('refreshBtn');
const usersList = document.getElementById('usersList');

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});

// Connect Google Account
connectBtn.addEventListener('click', async () => {
    try {
        connectBtn.disabled = true;
        connectBtn.innerHTML = '<span class="btn-icon">⏳</span> Connecting...';
        
        const response = await fetch(`${API_BASE}/auth/start`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.auth_url) {
            // Redirect to OAuth flow
            window.location.href = data.auth_url;
        } else {
            throw new Error(data.error || 'Failed to get authorization URL');
        }
    } catch (error) {
        alert('Error starting authentication: ' + error.message);
        connectBtn.disabled = false;
        connectBtn.innerHTML = '<span class="btn-icon">🔗</span> Connect Google Account';
    }
});

// Refresh users list
refreshBtn.addEventListener('click', () => {
    loadUsers();
});

// Load users from API
async function loadUsers() {
    try {
        usersList.innerHTML = '<div class="loading">Loading users...</div>';
        
        const response = await fetch(`${API_BASE}/users`);
        const data = await response.json();
        
        if (data.users && data.users.length > 0) {
            renderUsers(data.users);
        } else {
            usersList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <p>No connected accounts yet.</p>
                    <p>Click "Connect Google Account" to get started!</p>
                </div>
            `;
        }
    } catch (error) {
        usersList.innerHTML = `
            <div class="empty-state">
                <p style="color: #e74c3c;">Error loading users: ${error.message}</p>
            </div>
        `;
    }
}

// Render users list
function renderUsers(users) {
    usersList.innerHTML = users.map(user => `
        <div class="user-item">
            <div>
                <div class="user-email">${user.email}</div>
            </div>
            <div class="user-actions">
                <button class="btn btn-danger" onclick="deleteUser('${user.email}')">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Delete user
async function deleteUser(email) {
    if (!confirm(`Are you sure you want to remove ${email}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${encodeURIComponent(email)}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            loadUsers(); // Refresh list
        } else {
            const error = await response.json();
            alert('Error deleting user: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Error deleting user: ' + error.message);
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Make deleteUser available globally
window.deleteUser = deleteUser;

