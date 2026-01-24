async function loadStudentDashboard() {
    const data = await apiRequest("/application/me");

    const applications = data.applications;

    let acceptedApp = null;
    let selectedApp = null;

    for (const app of applications) {
        if (app.status === "Accepted") {
            acceptedApp = app;
            break;
        }
        if (app.status === "Selected") {
            selectedApp = app;
        }
    }

    if (acceptedApp) {
        // ACCEPTED state
	renderAccepted(acceptedApp);
	return;
    }

    if (selectedApp) {
        // SELECTED state
        renderSelected(selectedApp);
        return;
    }

    // NONE state
    const appliedProfiles = new Map();
	for (const app of applications) {
    		appliedProfiles.set(app.profile_code, app.status);
	}
    renderProfileList(appliedProfiles);
}

function renderAccepted(app) {
    const content = document.getElementById("content");
    content.innerHTML = "";

    const heading = document.createElement("h2");
    heading.textContent = "Congratulations!";

    const msg = document.createElement("p");
    msg.textContent = `You have accepted an offer from ${app.company_name} (${app.designation}).`;

    content.appendChild(heading);
    content.appendChild(msg);
}

function renderSelected(app) {
    const content = document.getElementById("content");
    content.innerHTML = "";

    const heading = document.createElement("h2");
    heading.textContent = "You have been selected!";

    const details = document.createElement("p");
    details.textContent = `${app.company_name} -  ${app.designation}`;

    const acceptBtn = document.createElement("button");
    acceptBtn.textContent = "Accept";
    acceptBtn.classList.add("btn", "btn-select");

    const rejectBtn = document.createElement("button");
    rejectBtn.textContent = "Reject";
    rejectBtn.classList.add("btn", "btn-reject");

    acceptBtn.onclick = async () => {
        await apiRequest("/application/respond", "POST", {
            profile_code: app.profile_code,
	    new_status: "Accepted"
        });
        loadStudentDashboard();
    };

    rejectBtn.onclick = async () => {
        await apiRequest("/application/respond", "POST", {
            profile_code: app.profile_code,
	    new_status: "Rejected"
        });
        loadStudentDashboard();
    };

    content.appendChild(heading);
    content.appendChild(details);
    content.appendChild(acceptBtn);
    content.appendChild(rejectBtn);
}


async function renderProfileList(appliedProfiles) {
    const content = document.getElementById("content");
    content.innerHTML = "";

    const heading = document.createElement("h2");
    heading.textContent = "Available Profiles";
    content.appendChild(heading);

    const res = await apiRequest("/profiles");
    const profiles = res.profiles;

    if (profiles.length === 0) {
        content.appendChild(document.createTextNode("No profiles available"));
        return;
    }

    profiles.forEach(profile => {
        const row = document.createElement("div");

        const text = document.createElement("span");
        text.textContent = `${profile.company_name} - ${profile.designation}`;

        const btn = document.createElement("button");
	btn.classList.add("btn");
        if (appliedProfiles.has(profile.profile_code)) {
	    btn.textContent = appliedProfiles.get(profile.profile_code);
	    btn.disabled = true;
	} else {
	    btn.textContent = "Apply";
	    btn.onclick = async () => {
            await apiRequest("/apply", "POST", {
                profile_code: profile.profile_code
            });
            loadStudentDashboard();
        };
	}

        

        row.appendChild(text);
        row.appendChild(btn);
        content.appendChild(row);
    });
}

