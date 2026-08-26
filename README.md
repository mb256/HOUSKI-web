# HOUSKI-web

Web presentation of local climbing club HOUSKi (Plzeň).

## Prerequisites

- Python 3.12+ (tested with 3.14)
- [Poetry](https://python-poetry.org/) 2.4.x

## Local setup

```powershell
# Clone and enter the repo, then install dependencies
poetry install --with dev

# Copy the environment template and adjust SECRET_KEY as needed
Copy-Item .env.example .env

# Apply database migrations
poetry run python manage.py migrate

# Create the default superuser (username: brouk, password: Admin1234#)
poetry run python manage.py create_default_superuser

# Seed article categories
poetry run python manage.py seed_categories
```

> ⚠️ Change the `brouk` password after first login in production — it's a known
> default credential documented in the implementation plan.

## Running the dev server

```powershell
poetry run python manage.py runserver
```

Visit http://127.0.0.1:8000/.

## Running tests

```powershell
poetry run pytest
```

## Project structure

```
HOUSKI-web/
├── config/                  # Django project settings & root URLconf
│   └── settings/            # base.py / dev.py / test.py / prod.py
├── apps/
│   ├── users/               # Custom User model, auth, profile
│   ├── home/                # Home page, Picture of the Week
│   ├── board/                # Nástěnka (board) posts
│   ├── articles/            # Články (articles) with categories
│   ├── activities/          # Plánované aktivity (planned activities)
│   └── contacts/            # Static Kontakty page
├── templates/                # Shared base template + per-app templates
├── static/                   # CSS / JS / images
├── media/                    # User-uploaded files (gitignored)
└── manage.py
```

Backend code/comments are in English; all user-facing text is in Czech.

## Deployment to PythonAnywhere

1. **Export dependencies** (run locally before pushing, or regenerate on PA):
   ```powershell
   poetry export -f requirements.txt --output requirements.txt --without-hashes
   ```

2. **On PythonAnywhere**, clone the repo and create a virtualenv:
   ```bash
   git clone https://github.com/yourrepo/houski-web.git
   python3.12 -m venv ~/.virtualenvs/houski
   source ~/.virtualenvs/houski/bin/activate
   pip install -r requirements.txt
   ```

3. **Set environment variables** (PA dashboard → Web → environment variables, or a `.env`
   file next to `manage.py`):
   ```
   SECRET_KEY=your-production-secret-key
   DJANGO_SETTINGS_MODULE=config.settings.prod
   ALLOWED_HOSTS=yourname.pythonanywhere.com
   ```

4. **Configure the WSGI file** (PA dashboard → Web → WSGI configuration file):
   ```python
   import os, sys
   path = '/home/yourname/houski-web'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. **Static/media file mappings** (PA dashboard → Web → Static files):
   ```
   URL: /static/    →  Directory: /home/yourname/houski-web/staticfiles
   URL: /media/     →  Directory: /home/yourname/houski-web/media
   ```

6. **Run database setup:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py create_default_superuser
   python manage.py seed_categories
   ```

7. **Reload the web app** via the PA dashboard → Web → Reload button.

### Update & redeploy workflow

```bash
cd ~/houski-web
git pull origin main
source ~/.virtualenvs/houski/bin/activate
pip install -r requirements.txt     # only if dependencies changed
python manage.py migrate            # only if migrations changed
python manage.py collectstatic --noinput
# Then reload via PA dashboard, or:
# touch /var/www/yourname_pythonanywhere_com_wsgi.py
```
