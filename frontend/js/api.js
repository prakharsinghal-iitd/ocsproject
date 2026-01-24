// frontend/js/api.js

const API_BASE = "https://ocsproject-backend.vercel.app/api";

function getToken() {
    return localStorage.getItem("token");
}

async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = {
        "Content-Type": "application/json"
    };

    const token = getToken();
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    const response = await fetch(API_BASE + endpoint, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null
    });

    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}

