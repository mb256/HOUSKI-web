#!/usr/bin/env bash
# Update & redeploy HOUSKI-web on PythonAnywhere.
#
# Run this from a Bash console on PythonAnywhere after the initial setup
# described in README.md ("Deployment to PythonAnywhere"). It is safe to
# run repeatedly: git pull, poetry sync, migrate, collectstatic and the
# two seed commands are all idempotent.
#
# Usage:
#   ~/houski-web/scripts/pa_update.sh
#
# Optional env vars (export before running, or put in ~/.bashrc):
#   VENV_NAME   name of the virtualenv (default: houski)
#   WSGI_FILE   path to the PA wsgi file to touch for auto-reload
#               e.g. /var/www/yourname_pythonanywhere_com_wsgi.py
#               If unset, reload manually via the Web tab instead.

set -euo pipefail

VENV_NAME="${VENV_NAME:-houski}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Project dir: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "==> Pulling latest changes"
git pull --ff-only

echo "==> Activating virtualenv: $VENV_NAME"
source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"

# Ensure poetry installs into the already-active PythonAnywhere virtualenv
# instead of creating its own.
export POETRY_VIRTUALENVS_CREATE=false

echo "==> Installing/updating dependencies with Poetry"
poetry install --no-interaction --without dev

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Ensuring default superuser exists"
python manage.py create_default_superuser

echo "==> Seeding article categories"
python manage.py seed_categories

if [[ -n "${WSGI_FILE:-}" ]]; then
    echo "==> Reloading web app (touching $WSGI_FILE)"
    touch "$WSGI_FILE"
else
    echo "==> Done. Reload the web app via the PythonAnywhere Web tab (or set WSGI_FILE and re-run)."
fi
