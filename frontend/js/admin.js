async function loadAdminDashboard() {
    const content = document.getElementById("content");
    content.innerHTML = "";

    const heading = document.createElement("h2");
    heading.textContent = "Admin Dashboard";
    content.appendChild(heading);

    renderAdminCreateProfile(content);

    await renderUsers(content);

    const data = await apiRequest("/application/me"); 
    const applications = data.applications;
    const grouped = groupByProfile(applications);
    
    await renderAdminProfiles(content);
    await renderAdminApplications(grouped,content);
}

function renderAdminCreateProfile(parent) {
    const title = document.createElement("h3");
    title.textContent = "Create Profile (Admin)";

    const recruiterInput = document.createElement("input");
    recruiterInput.placeholder = "Recruiter Email";

    const companyInput = document.createElement("input");
    companyInput.placeholder = "Company Name";

    const designationInput = document.createElement("input");
    designationInput.placeholder = "Designation";

    const btn = document.createElement("button");
    btn.textContent = "Create Profile";
    btn.classList.add("btn");

    btn.onclick = async () => {
        if (!recruiterInput.value || !companyInput.value || !designationInput.value) {
            alert("Missing fields");
            return;
        }

        await apiRequest("/create_profile", "POST", {
            recruiter_email: recruiterInput.value,
            company_name: companyInput.value,
            designation: designationInput.value
        });

        loadAdminDashboard();
    };

    parent.append(title, recruiterInput, companyInput, designationInput, btn);
}

async function renderUsers(parent) {
    const res = await apiRequest("/users");

    const title = document.createElement("h3");
    title.textContent = "Users";
    parent.appendChild(title);

    res.users.forEach(user => {
        const div = document.createElement("div");
        div.textContent = `${user.userid} | Role: ${user.role}`;
        parent.appendChild(div);
    });
}

async function renderAdminProfiles(parent) {
    const res = await apiRequest("/profiles");

    const title = document.createElement("h3");
    title.textContent = "Profiles";
    parent.appendChild(title);

    res.profiles.forEach(p => {
        const div = document.createElement("div");
        div.textContent = `${p.profile_code} | ${p.company_name} - ${p.designation} | Recruiter: ${p.recruiter_email}`;
        parent.appendChild(div);
    });
}

/* ---------------- APPLICATIONS LIST ---------------- */

function renderAdminApplications(groupedApplications,parent) {
    

    for (const profileCode in groupedApplications) {
        // Profile heading
        const profileDiv = document.createElement("div");
        profileDiv.className = "profile-block";

        const heading = document.createElement("h3");
        heading.textContent = `Profile Code: ${profileCode}`;
        profileDiv.appendChild(heading);

        // Applications under this profile
        groupedApplications[profileCode].forEach(app => {
            const row = document.createElement("div");
            row.className = "application-row";

            row.innerHTML = `
                <span>${app.entry_number}</span>
                <span>Status: ${app.status}</span>
            `;

            // Action buttons (example)
            if (app.status === "Applied") {
                const selectBtn = document.createElement("button");
                selectBtn.textContent = "Select";
                selectBtn.dataset.profileCode = profileCode;
                selectBtn.dataset.entryNumber = app.entry_number;
                selectBtn.onclick = changeAdminStatus;
		selectBtn.classList.add("btn","btn-select");

                row.appendChild(selectBtn);
            }

            profileDiv.appendChild(row);
        });

        parent.appendChild(profileDiv);
    }
}


async function changeAdminStatus(e) {
    const profileCode = e.target.dataset.profileCode;
    const entryNumber = e.target.dataset.entryNumber;

    await apiRequest("/application/change_status", "POST", {
        profile_code: profileCode,
        entry_number: entryNumber,
        new_status: "Selected"
    });

    loadAdminDashboard(); // refresh
}


