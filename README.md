# IN CAMP Student Portal

IN CAMP is a Django student management portal for registration, academic records, coursework, and campus notices. Students use private accounts to view their own information; authorized staff manage records through Django admin.

## Features

- Student registration with validated details and Django password hashing
- Username or email sign-in, secure session logout, and profile editing
- Student dashboard with student ID, subjects, attendance summary, grades, upcoming assignments, and notices
- Student-specific subject, attendance, grade, assignment, and notice pages
- Assignment submissions with instructor-managed scores and feedback
- Normalized models for students, subjects, enrollments, attendance, assessments, grades, assignments, submissions, and notices
- Staff-only portal statistics and searchable, filterable Django admin management
- Responsive templates, CSRF protection, and WhiteNoise static serving
- SQLite for local development; optional PostgreSQL through `DATABASE_URL`

## Tech Stack

- Python 3.12 or later and Django 6.1
- SQLite locally; PostgreSQL supported for deployment
- WhiteNoise for static files and Gunicorn for production WSGI serving

## Project Structure

```text
STUDENTS/
	migrations/        Database schema history
	static/STUDENTS/   Portal stylesheet
	templates/STUDENTS/Shared layout and student/staff pages
	admin.py           Staff data management
	forms.py           Registration, profile, login, and submission forms
	models.py          Student and academic data models
	tests.py           Behavior and authorization tests
	views.py           Registration and portal views
student_portal/
	settings.py        Environment-aware configuration
	urls.py            Application routes
	wsgi.py            Production WSGI entry point
manage.py
requirements.txt
```

## Local Setup

Create and activate a virtual environment from the repository root.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:DEBUG = "True"
$env:SECRET_KEY = "replace-with-a-local-development-secret"
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export DEBUG=True
export SECRET_KEY="replace-with-a-local-development-secret"
```

Apply migrations and create a staff administrator:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Run locally with `python manage.py runserver`, then open <http://127.0.0.1:8000/>. Staff can use `/admin/` or `/staff/`. Without `SECRET_KEY`, local development generates a temporary key; set one locally to retain sessions across restarts.

## Checks and Tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Required for production; local development can generate a temporary key. |
| `DEBUG` | Defaults to `True` locally. Set to `False` in production. |
| `ALLOWED_HOSTS` | Comma-separated hostnames; defaults to `127.0.0.1,localhost`. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated full origins, including `https://`, for hosted domains. |
| `DATABASE_URL` | Optional PostgreSQL URL. Without it, SQLite is used. |
| `SECURE_SSL_REDIRECT` | Defaults to enabled when `DEBUG=False`; configure for the host's HTTPS proxy. |
| `SECURE_HSTS_SECONDS` | HSTS duration; defaults to one year when `DEBUG=False`. |
| `EMAIL_BACKEND` | Defaults to Django's console backend; configure SMTP for real email delivery. |

Do not commit `.env` files, production secrets, or the local SQLite database.

## Render Deployment

1. Push the repository to GitHub and create a Render PostgreSQL database.
2. Create a Render Web Service using Python 3.12 or later.
3. Set the build command:

	 ```bash
	 pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
	 ```

4. Set the start command to `gunicorn student_portal.wsgi:application`.
5. Configure `DEBUG=False`, a generated `SECRET_KEY`, `ALLOWED_HOSTS=<service>.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://<service>.onrender.com`, and the Render connection URL as `DATABASE_URL`.
6. Create a production staff account with `python manage.py createsuperuser` from the service shell or a one-off command.
7. Review `python manage.py check --deploy`, confirm HTTPS behavior, and back up the production database.

Do not rely on ephemeral SQLite storage for hosted data. WhiteNoise serves collected static files; profile uploads are not currently enabled.

## Future Improvements

- Password reset and verified email workflows
- Profile image uploads with validated storage
- Pagination and bulk import/export for larger cohorts
- Automated attendance and grade reports
- CI checks and a managed email provider
