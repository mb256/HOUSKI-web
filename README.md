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

These steps use **Poetry** directly on PythonAnywhere (no `requirements.txt` export
needed). Free accounts get one web app, a Bash console, and PyPI/GitHub access, which is
all this requires.

### One-time setup

1. **Open a Bash console** (Dashboard → Consoles → Bash).

2. **Clone the repo:**
   ```bash
   git clone https://github.com/mb256/HOUSKI-web.git
   cd HOUSKI-web
   ```

3. **Create a virtualenv** matching the Python version you'll pick on the Web tab
   (3.12 if available on your account; otherwise use the closest 3.x offered):
   ```bash
   mkvirtualenv houski --python=/usr/bin/python3.12
   ```
   This activates the venv automatically and creates it at `~/.virtualenvs/houski`.

4. **Install Poetry into that same virtualenv**, and tell it not to create a second,
   separate virtualenv of its own:
   ```bash
   pip install poetry
   poetry config virtualenvs.create false --local
   ```

5. **Install dependencies:**
   ```bash
   poetry install --no-interaction --without dev
   ```

6. **Create `.env`** in the project root (`~/HOUSKI-web/.env`):
   ```
   SECRET_KEY=your-production-secret-key
   DJANGO_SETTINGS_MODULE=config.settings.prod
   ALLOWED_HOSTS=yourname.pythonanywhere.com
   ```

7. **Create the web app**: Dashboard → Web → Add a new web app → **Manual configuration**
   → pick the same Python version as step 3.

8. **Set the virtualenv path** (Web tab → Virtualenv section): enter `houski` (or the
   full path `/home/yourname/.virtualenvs/houski`).

9. **Edit the WSGI configuration file** (Web tab → WSGI configuration file link) so it
   reads:
   ```python
   import os, sys
   path = '/home/yourname/HOUSKI-web'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
   Replace `yourname` with your PythonAnywhere username.

10. **Static/media file mappings** (Web tab → Static files):
    ```
    URL: /static/    →  Directory: /home/yourname/HOUSKI-web/staticfiles
    URL: /media/     →  Directory: /home/yourname/HOUSKI-web/media
    ```

11. **Run the setup/update script** (see below) to migrate the DB, collect static files,
    and seed initial data:
    ```bash
    cd ~/HOUSKI-web
    bash scripts/pa_update.sh
    ```

12. **Reload the web app** via the Web tab → Reload button, then visit
    `https://yourname.pythonanywhere.com/`.

> ⚠️ Change the `brouk` password after first login — it's a known default credential.

### Update & redeploy workflow

After pushing new commits to GitHub, from a PythonAnywhere Bash console:

```bash
cd ~/HOUSKI-web
bash scripts/pa_update.sh
```

[`scripts/pa_update.sh`](scripts/pa_update.sh) pulls the latest `main`, activates the
`houski` virtualenv, runs `poetry install` to sync dependencies, applies migrations,
collects static files, and re-runs the idempotent `create_default_superuser` /
`seed_categories` commands. It prints a reminder to reload the web app afterwards
(Web tab → Reload), or set `WSGI_FILE=/var/www/yourname_pythonanywhere_com_wsgi.py`
before running it to have the script trigger the reload itself.

If your virtualenv is named something other than `houski`, pass it via
`VENV_NAME=your-venv-name bash scripts/pa_update.sh`.
