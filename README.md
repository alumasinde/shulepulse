# ShulePulse

Production-oriented school SaaS foundation built for **local development with MySQL installed directly on the machine**. Docker is not required.

## Stack

FastAPI · Python 3.14 · MySQL · SQLAlchemy 2 · Alembic · Pydantic · Jinja2 · HTMX · Alpine.js · Tailwind CSS · Font Awesome

## Current phase

This build finishes the **foundation, dashboard and core people/academic workflows** without changing the existing database migrations.

### Foundation hardening

- School registration with validated, reserved-handle protection
- School tenant resolved from the request hostname
- Authentication tied to both `user_id` and `school_id`
- Active-user verification on every protected request
- No browser-supplied `school_id` is trusted for tenant access
- Tenant-scoped queries throughout the management workflows
- Cross-school class/stream validation when assigning students
- Cross-school parent validation when linking students
- MySQL ORM IDs explicitly use unsigned `BIGINT`, matching the migrations
- No SQL ENUMs
- Person names use `first_name` and `last_name`

### Dashboard

- Responsive sidebar
- Collapsible People and Academics navigation groups
- Font Awesome icons
- Student, parent, teacher, class and subject counts
- Academic setup progress
- Active academic year and term summary
- Recently added students
- Quick action to add students
- Coming-next modules shown as disabled rather than pretending they are implemented

### Student workflow

- Search by name or admission number
- Comprehensive student profile
- Add student
- Edit student
- Student status
- Class and stream placement validation
- Parent/guardian linking
- Primary parent handling
- Address and location fields
- Birth certificate number
- Medical notes and allergies
- Flexible `extra_data` JSON for future school-specific fields

### Parent workflow

- Create parent/guardian
- Search by name or phone
- School-scoped records
- Duplicate phone protection
- Linked-student count

### Teacher workflow

- Create teacher
- Search by name or employee number
- Employee number uniqueness per school
- Contact details, hire date and specialization

### Academic workflow

- Academic years
- Activate one academic year per school
- Terms
- Activate one term within an academic year
- Classes
- Streams tied to classes
- Subjects
- Duplicate protection
- Date validation
- Tenant validation on every operation

## Local setup — Windows/MySQL

### 1. Create the database

```sql
CREATE DATABASE shulepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure `.env`

Copy `.env.example` to `.env` and use your local MySQL credentials:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@127.0.0.1:3306/shulepulse
```

Use a random secret of at least 32 characters for `SECRET_KEY`.

### 3. Python environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Python 3.14 is supported by the dependency versions in this project.

### 4. Run migrations

```powershell
alembic upgrade head
alembic current
```

The expected head is:

```text
0002_academics_people
```

### 5. Build frontend assets

Node.js is only needed to compile Tailwind CSS:

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

Register a school such as `majimazuri`.

Then open:

```text
http://majimazuri.shulepulse.localhost:8000/login
```

Modern browsers normally resolve `*.localhost` to the local machine. If yours does not, add this to the Windows hosts file:

```text
127.0.0.1 majimazuri.shulepulse.localhost
```

## Important tenant rule

The application does not accept a school ID from forms or URLs for authorization.

The tenant is resolved from:

```text
majimazuri.shulepulse.localhost:8000
        ↓
majimazuri
        ↓
schools.slug
        ↓
school.id
        ↓
authenticated user's school_id
```

Every tenant-owned query should continue following this rule as new modules are added.

## Architecture rules

- **No SQL ENUMs.** Roles and statuses remain application-level strings.
- Person names always use `first_name` and `last_name`.
- Tenant-owned tables contain `school_id` where appropriate.
- JSON is reserved for configuration and genuinely flexible data; core relationships remain relational.
- Do not add a migration merely to introduce a new UI screen. Add schema only when a real persistent capability requires it.

## Next phase

The foundation is now ready for:

1. Assessment configuration
2. Flexible grading rubrics in school settings
3. Formative and summative assessment entry
4. Results and report cards
5. Fees and balances
6. WhatsApp automation
7. School subscriptions
