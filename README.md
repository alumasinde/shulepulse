# ShulePulse

Production-oriented Phase 1–2 school SaaS foundation built for **local development with MySQL installed directly on the machine**. Docker is not required.

## Stack

FastAPI · Python · MySQL · SQLAlchemy 2 · Alembic · Pydantic · Jinja2 · HTMX · Alpine.js · Tailwind CSS · Font Awesome

## Included in this phase

- School registration and tenant handles
- Local subdomain tenancy
- Admin authentication
- School-scoped authorization
- Academic years and terms
- Classes and streams
- Subjects
- Teachers
- Students with a comprehensive profile
- Parents/guardians
- Student ↔ parent linking
- Dashboard counts
- Responsive management screens
- MySQL migration for all Phase 2 tables

## Local setup — Windows/MySQL

### 1. Create the database

In MySQL Workbench or the MySQL CLI:

```sql
CREATE DATABASE shulepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure `.env`

Copy `.env.example` to `.env` and use your local MySQL credentials:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@127.0.0.1:3306/shulepulse
```

Generate a long random `SECRET_KEY`.

### 3. Python environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Run migrations

```powershell
alembic upgrade head
```

This applies both the foundation migration and the Phase 2 academic/people migration.

### 5. Build the frontend assets

Install Node.js, then:

```powershell
npm install
npm run build
```

### 6. Start FastAPI

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://localhost:8000/register
```

Register a school such as `majimazuri`. Then use:

```text
http://majimazuri.shulepulse.localhost:8000/login
```

Modern browsers normally resolve `*.localhost` to your machine. If yours does not, add an entry to the Windows hosts file:

```text
127.0.0.1 majimazuri.shulepulse.localhost
```

## Phase 2 modules

### Academic setup

`/academics` manages:

- Academic years
- Terms
- Classes
- Streams
- Subjects

### Students

`/students` supports:

- Admission number
- First/last/other names
- Date of birth
- Gender
- Nationality
- Photo URL field
- Class/stream
- Admission date
- Previous school
- Address/city/county
- Birth certificate number
- Medical notes
- Allergies
- Flexible `extra_data` JSON for future school-specific fields
- Student status

### Parents

`/parents` supports parent/guardian records and `/students/{id}` supports linking parents to students.

### Teachers

`/teachers` supports teacher profiles, employee numbers, contact details, hire date and specialization.

## Architecture rules

- **No SQL ENUMs.** Statuses and roles are strings so the system remains extensible.
- Person names always use `first_name` and `last_name`.
- Tenant-owned tables contain `school_id`.
- Tenant authorization comes from the hostname + authenticated session, not a browser-supplied school ID.
- JSON is reserved for configuration and genuinely flexible data; core relationships remain relational.

## Production transition later

When local development is complete, the same application can move behind a reverse proxy with:

```text
*.shulepulse.com → FastAPI
```

and production MySQL. Secure cookies, HTTPS, secret management, backups, monitoring and a real object-storage provider should be configured before launch.
