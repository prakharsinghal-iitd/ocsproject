async function loadRecruiterDashboard() {
    const content = document.getElementById("content");
    content.innerHTML = "";

    // Heading
    const heading = document.createElement("h2");
    heading.textContent = "Recruiter Dashboard";
    content.appendChild(heading);

    // Profile creation form
    renderCreateProfileForm(content);

    // Load applications
    const data = await apiRequest("/application/me"); 
    const applications = data.applications;
    const grouped = groupByProfile(applications);
    await renderRecruiterProfiles(content);
    await renderRecruiterApplications(grouped,content);

}

/* ---------------- PROFILE CREATION ---------------- */

function renderCreateProfileForm(parent) {
    const formTitle = document.createElement("h3");
    formTitle.textContent = "Create New Profile";

    const companyInput = document.createElement("input");
    companyInput.placeholder = "Company Name";

    const designationInput = document.createElement("input");
    designationInput.placeholder = "Designation";

    const btn = document.createElement("button");
    btn.textContent = "Create Profile";

    btn.onclick = async () => {
        if (!companyInput.value || !designationInput.value) {
            alert("Missing fields");
            return;
        }

        await apiRequest("/create_profile", "POST", {
            company_name: companyInput.value,
            designation: designationInput.value
        });

        loadRecruiterDashboard(); // refresh everything
    };

    parent.appendChild(formTitle);
    parent.appendChild(companyInput);
    parent.appendChild(designationInput);
    parent.appendChild(btn);
}

/* ---------------- PROFILES LIST ---------------- */

async function renderRecruiterProfiles(parent) {
    const res = await apiRequest("/profiles");
    const profiles = res.profiles;

    const title = document.createElement("h3");
    title.textContent = "Your Profiles";
    parent.appendChild(title);

    if (profiles.length === 0) {
        parent.appendChild(document.createTextNode("No profiles created yet."));
        return;
    }

    profiles.forEach(profile => {
        const div = document.createElement("div");
        div.textContent = `${profile.company_name} - ${profile.designation} (Code: ${profile.profile_code})`;
        parent.appendChild(div);
    });
}

function groupByProfile(applications) {
    const grouped = {};

    for (const app of applications) {
        const code = app.profile_code;

        if (!grouped[code]) {
            grouped[code] = [];
        }

        grouped[code].push(app);
    }

    return grouped;
}

/* ---------------- APPLICATIONS LIST ---------------- */

function renderRecruiterApplications(groupedApplications,parent) {
    

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
                selectBtn.onclick = changeRecruiterStatus;

                row.appendChild(selectBtn);
            }

            profileDiv.appendChild(row);
        });

        parent.appendChild(profileDiv);
    }
}


async function changeRecruiterStatus {
    const profileCode = e.target.dataset.profileCode;
    const entryNumber = e.target.dataset.entryNumber;

    await apiRequest("/application/change_status", "POST", {
        profile_code: profileCode,
        entry_number: entryNumber,
        new_status: "Selected"
    });

    loadRecruiterDashboard(); // refresh
}

