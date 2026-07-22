/**
 * Dummy client-side authentication (hardcoded single user, demo only).
 */
const DUMMY_USER = {
    username: 'user',
    password: 'user123',
};

function login(username, password) {
    if (username === DUMMY_USER.username && password === DUMMY_USER.password) {
        sessionStorage.setItem('authenticated', 'true');
        sessionStorage.setItem('username', username);
        return true;
    }
    return false;
}

function isAuthenticated() {
    return sessionStorage.getItem('authenticated') === 'true';
}

function logout() {
    sessionStorage.removeItem('authenticated');
    sessionStorage.removeItem('username');
    window.location.href = 'login.html';
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
    }
}
