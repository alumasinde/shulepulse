# ShulePulse architecture

FastAPI + Jinja2/HTMX/Alpine/Tailwind + SQLAlchemy + MySQL.

Tenant resolution: hostname -> slug -> schools.id -> request context. Tenant users must never choose an arbitrary school_id for authorization.

Planned modules: schools, users, students, parents, teachers, academics, classes, streams, subjects, assessments, exams, results, reports, attendance, fees, subscriptions, whatsapp.

No SQL ENUMs. Person names use first_name and last_name. JSON is for configurable settings; core records stay relational.
