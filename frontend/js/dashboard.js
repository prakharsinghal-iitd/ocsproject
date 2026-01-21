// frontend/js/dashboard.js

async function loadDashboard() {
    try {
        const user = await apiRequest("/users/me");

        document.getElementById("welcome").textContent =
            `Welcome ${user.userid} (${user.role})`;

        if (user.role === "student") {
            loadStudentDashboard();
        } else if (user.role === "recruiter") {
            loadRecruiterView();
        } else if (user.role === "admin") {
            loadAdminView();
        }

    } catch (err) {
        // token invalid or expired
        localStorage.clear();
        window.location.href = "index.html";
    }
}

function loadStudentView() {
    document.getElementById("content").textContent =
        "Student dashboard coming next...";
}

function loadRecruiterView() {
    document.getElementById("content").textContent =
        "Recruiter dashboard coming next...";
}

function loadAdminView() {
    document.getElementById("content").textContent =
        "Admin dashboard coming next...";
}

loadDashboard();

