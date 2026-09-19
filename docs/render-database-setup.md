# Render database setup

Run these commands from the backend service directory after the service is connected to the production `DATABASE_URL`:

```bash
python manage.py migrate
python manage.py seed_content
python manage.py import_verified_courses
python manage.py createsuperuser
```

`seed_content` is safe to run again. It creates the regions, universities, pages, articles, FAQs, settings and verified University of Padua courses used by the local database. `import_verified_courses` bulk-loads the source-audited Italy catalogue from `platform_app/data/italy_courses.json`; it publishes only records marked verified and leaves pending rows unpublished. Existing admin edits are preserved by the initial import workflow.

For a Render web service, use a release/start command that runs migrations and seeding before Gunicorn starts, for example:

```bash
python manage.py migrate && python manage.py seed_content && gunicorn config.wsgi:application --chdir backend
```

Keep dependency installation and static collection in Render's **Build Command**, not its Start Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

If the service root is the repository root, use `pip install -r backend/requirements.txt && python backend/manage.py collectstatic --noinput` instead.

If Render’s service root is already `backend`, omit `--chdir backend` and run:

```bash
python manage.py migrate && python manage.py seed_content && gunicorn config.wsgi:application
```

Create the first admin account interactively with `createsuperuser`. Use a strong unique password; do not commit credentials or put them in frontend environment variables. Then open `/admin/` on the backend domain.

For a non-interactive Render shell, add these three environment variables temporarily:

```text
DJANGO_SUPERUSER_USERNAME=your-admin-username
DJANGO_SUPERUSER_EMAIL=you@example.com
DJANGO_SUPERUSER_PASSWORD=<strong-unique-password>
```

Then run:

```bash
python manage.py provision_admin
```

Remove the password variable from Render after the command succeeds. To intentionally reset an existing account, run `python manage.py provision_admin --reset-password`.
