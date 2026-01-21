// frontend/js/auth.js

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const userid = document.getElementById("userid").value.trim();
    const password = document.getElementById("password").value;
    const errorDiv = document.querySelector(".error");

    errorDiv.textContent = "";

    if (!userid || !password) {
        errorDiv.textContent = "Please fill all fields";
        return;
    }

    const password_md5 = md5(password);

    try {
        const res = await apiRequest("/login", "POST", {
            userid,
            password_md5
        });

        localStorage.setItem("token", res.token);
        localStorage.setItem("role", res.role);

        // redirect based on role (later)
        window.location.href = "dashboard.html";

    } catch (err) {
        errorDiv.textContent = err.error || "Login failed";
    }
});

