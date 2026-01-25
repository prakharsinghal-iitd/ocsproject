# ocsproject

- **Frontend**: Static HTML, CSS, JavaScript  
- **Backend**: Flask (Python)  
- **Database**: PostgreSQL (hosted on Supabase)  
- **Authentication**: JWT-based authentication 

---

## Project Structure
```
ocsproject/
|-- backend/
| |-- app.py
| |-- requirements.txt
| |-- config.py
| |-- venv/
|
|-- frontend/
| |-- index.html
| |-- dashboard.html
| |
| |-- css/
| | |-- style.css
| |
| |-- js/
| | |-- api.js
| | |-- auth.js
| | |-- dashboard.js
| | |-- student.js
| | |-- recruiter.js
| | |-- admin.js
```
---

## Clone the Repository

```bash
git clone https://github.com/prakharsinghal-iitd/ocsproject.git
cd ocsproject
```
---

## Deployment

- **Frontend (Hosted)**:  
  https://ocsproject.vercel.app/

- **Backend**:  
  Runs locally using Flask.
> The backend must be running locally for the frontend to function correctly.

---

## Backend Setup (Local)

### Navigate to backend folder

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
python app.py
```
The Flask server will start at:
http://localhost:8000

---
## Frontend Usage

- The frontend is built using static HTML, CSS, and JavaScript

- It communicates with the backend via REST APIs

- JWT tokens are stored in localStorage for authentication

- All database access and sensitive logic happen only on the backend

You can:

- Open frontend files locally OR

- Use the hosted frontend at:
https://ocsproject.vercel.app/

---
## Authentication Flow

- User enters userid and password

- Browser computes the MD5 hash of the password

- Client sends { userid, password_md5 } to /api/login

- Server validates credentials

- Server returns a JWT token

- Token is sent in Authorization: Bearer <token> header for all protected API requests

- Raw passwords are never sent to the server.

---
## Roles & Features
### Student

- View own user record

- View available job/internship profiles

- Apply to profiles

- Accept or reject selected offers

- Can have only one accepted offer per session

### Recruiter

- View own details

- Create and manage own profiles

- View applications submitted to own profiles

- Change application status (e.g., Applied → Selected, Applied → Rejected)

### Admin

- View all users, profiles, and applications

- Create profiles for any recruiter

- Change application status (e.g., Applied → Selected)

- Full system visibility (excluding sensitive fields)

---
## Security Considerations

- Raw passwords are never stored or transmitted. Passwords are stored as MD5 hashes

- JWT-based authentication with role-based authorization

- Frontend contains no sensitive credentials. All database operations occur on the backend

---
## API Design

- REST-style JSON APIs

- All endpoints return JSON responses

- Errors are handled centrally and displayed via warning dialogs in the UI
