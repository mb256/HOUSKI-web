# HOUSKI Web — Detailed Implementation Plan

> **How to use this plan:**
> - Each phase can be implemented independently and you can stop/resume at any phase boundary.
> - Each step has exact commands, file paths, and code snippets you can copy.
> - Checkboxes `[ ]` mark individual steps — check them off as you go.
> - Backend code and comments are in English. All user-facing text (labels, buttons, headings) is in Czech.

---

## Technology Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Runtime |
| Django | 5.x | Web framework |
| Poetry | 2.4.x | Dependency & virtualenv management |
| SQLite | built-in | Database (dev + PythonAnywhere prod) |
| Pillow | latest | Image handling & compression |
| django-summernote | latest | Rich text editor (no npm needed) |
| python-decouple | latest | Environment variable management |
| whitenoise | latest | Static file serving |
| pytest-django | latest | Testing |
| factory-boy | latest | Test data factories |

---

## Project Structure (target)

```
HOUSKI-web/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── test.py
│   │   └── prod.py          (added in Phase 8)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── users/               (Phase 1)
│   ├── home/                (Phase 1)
│   ├── board/               (Phase 3)
│   ├── articles/            (Phase 4)
│   ├── activities/          (Phase 5)
│   └── contacts/            (Phase 6)
├── templates/
│   ├── base.html
│   ├── registration/
│   │   ├── login.html
│   │   └── password_change_form.html
│   ├── users/
│   ├── home/
│   ├── board/
│   ├── articles/
│   ├── activities/
│   └── contacts/
├── static/
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   └── main.js
│   └── img/
│       └── logo.png         (placeholder)
├── media/                   (gitignored — user uploads)
├── .env                     (gitignored)
├── .env.example
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

---

## Phase 1 — Project Foundation

**Goal:** Runnable Django project with correct structure, custom User model, base layout, Home page.

---

### Step 1.1 — Poetry environment setup

```powershell
# In C:\Users\z0040c9z\workspace\HOUSKI-web
poetry init --no-interaction --name houski-web --description "HOUSKI Climbing Club Website" --author "Your Name <you@example.com>" --python "^3.12"

# Add runtime dependencies
poetry add django pillow python-decouple whitenoise django-summernote

# Add development dependencies
poetry add --group dev pytest pytest-django pytest-cov factory-boy django-debug-toolbar

# Configure venv inside project folder (optional but recommended)
poetry config virtualenvs.in-project true

# Install everything
poetry install --with dev
```

**Verify:**
```powershell
poetry run python -m django --version   # should print 5.x.x
```

---

### Step 1.2 — Django project scaffold

```powershell
# Create Django project into current directory
poetry run django-admin startproject config .

# Create apps package
mkdir apps
New-Item apps\__init__.py -ItemType File

# Create initial .gitignore
```

**`.gitignore` contents:**
```
.venv/
.env
*.pyc
__pycache__/
.pytest_cache/
.coverage
htmlcov/
staticfiles/
media/
db.sqlite3
*.log
*.sqlite3
```

---

### Step 1.3 — Settings split

**Delete** `config/settings.py` (the default single file) and **create** `config/settings/` directory:

```powershell
Remove-Item config\settings.py
mkdir config\settings
New-Item config\settings\__init__.py -ItemType File
```

**`config/settings/base.py`:**
```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS: list[str] = []

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'django_summernote',
]
LOCAL_APPS = [
    'apps.users',
    'apps.home',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.users.middleware.ForcePasswordChangeMiddleware',   # added in Phase 2
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'cs'           # Czech frontend
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Summernote config
SUMMERNOTE_CONFIG = {
    'summernote': {
        'width': '100%',
        'height': '300px',
        'toolbar': [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['insert', ['link']],
            ['view', ['fullscreen']],
        ],
        'lang': 'cs-CZ',
    },
    'attachment_filesize_limit': 5 * 1024 * 1024,   # 5 MB raw upload
}
```

**`config/settings/dev.py`:**
```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ['127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**`config/settings/test.py`:**
```python
from .base import *

DEBUG = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

SUMMERNOTE_CONFIG = {**SUMMERNOTE_CONFIG, 'attachment_require_authentication': True}
```

**`.env`** (never commit):
```
SECRET_KEY=django-dev-insecure-replace-this-in-prod
DEBUG=True
```

**`.env.example`** (commit this):
```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Update `manage.py`** — change settings module:
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
```

**`pytest.ini`** or add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

### Step 1.4 — Custom User model (`apps/users`)

```powershell
poetry run python manage.py startapp users apps\users
```

**`apps/users/models.py`:**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    ROLE_CHOICES = [
        ('predseda',   'Předseda'),
        ('tajemnik',   'Tajemník'),
        ('pokladnik',  'Pokladník'),
        ('clen',       'Člen'),
        ('instruktor', 'Instruktor'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    class Meta:
        verbose_name = 'role'
        verbose_name_plural = 'role'

    def __str__(self) -> str:
        return self.get_name_display()


class User(AbstractUser):
    telephone = models.CharField('telefon', max_length=20, blank=True)
    roles = models.ManyToManyField(Role, blank=True, verbose_name='role')
    must_change_password = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'uživatel'
        verbose_name_plural = 'uživatelé'

    def __str__(self) -> str:
        return self.username
```

**`apps/users/apps.py`:**
```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Uživatelé'
```

**`apps/users/admin.py`:**
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'telephone', 'is_staff', 'must_change_password']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HOUSKi', {'fields': ('telephone', 'roles', 'must_change_password')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('HOUSKi', {'fields': ('telephone', 'roles', 'must_change_password')}),
    )
```

**Run first migration:**
```powershell
poetry run python manage.py makemigrations users
poetry run python manage.py migrate
```

---

### Step 1.5 — Create superuser brouk

```powershell
poetry run python manage.py createsuperuser
# username: brouk
# email: (leave blank or add)
# password: Admin1234#
# must_change_password should be set to False for this admin user via admin panel after login
```

Or create a management command `apps/users/management/commands/create_default_superuser.py`:
```python
from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = 'Creates default superuser brouk if not exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='brouk').exists():
            user = User.objects.create_superuser('brouk', '', 'Admin1234#')
            user.must_change_password = False
            user.save()
            self.stdout.write(self.style.SUCCESS('Superuser brouk created.'))
        else:
            self.stdout.write('Superuser brouk already exists.')
```

```powershell
poetry run python manage.py create_default_superuser
```

---

### Step 1.6 — Base templates & static files

**`templates/base.html`:**
```html
{% load static %}
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}HOUSKi – Horolezecký oddíl{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header class="site-header">
        <div class="header-inner">
            <a href="{% url 'home:index' %}" class="logo-link">
                <img src="{% static 'img/logo.png' %}" alt="HOUSKi logo" class="logo">
                <span class="logo-text">HOUSKi</span>
            </a>
            <button class="nav-toggle" aria-label="Otevřít menu">☰</button>
            <nav class="main-nav">
                <ul>
                    <li><a href="{% url 'home:index' %}" {% if request.resolver_match.namespace == 'home' %}class="active"{% endif %}>Domů</a></li>
                    <li><a href="{% url 'board:list' %}" {% if request.resolver_match.namespace == 'board' %}class="active"{% endif %}>Nástěnka</a></li>
                    <li><a href="{% url 'articles:list' %}" {% if request.resolver_match.namespace == 'articles' %}class="active"{% endif %}>Články</a></li>
                    <li><a href="{% url 'activities:list' %}" {% if request.resolver_match.namespace == 'activities' %}class="active"{% endif %}>Plánované aktivity</a></li>
                    <li><a href="{% url 'contacts:index' %}" {% if request.resolver_match.namespace == 'contacts' %}class="active"{% endif %}>Kontakty</a></li>
                    {% if user.is_authenticated %}
                        <li><a href="{% url 'users:profile' %}">Profil</a></li>
                        <li>
                            <form method="post" action="{% url 'logout' %}" style="display:inline">
                                {% csrf_token %}
                                <button type="submit" class="nav-logout-btn">Odhlásit</button>
                            </form>
                        </li>
                    {% else %}
                        <li><a href="{% url 'login' %}">Přihlásit</a></li>
                    {% endif %}
                </ul>
            </nav>
        </div>
    </header>

    <main class="main-content">
        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="message message--{{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
        {% block content %}{% endblock %}
    </main>

    <footer class="site-footer">
        <div class="footer-inner">
            <p>© {% now "Y" %} HOUSKi – Horolezecký oddíl Plzeň</p>
            <p>Kontakt: <a href="{% url 'contacts:index' %}">Kontakty</a></p>
        </div>
    </footer>

    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**`static/css/main.css`** — dark minimalistic design:
```css
/* ===== CSS Custom Properties ===== */
:root {
    --bg-primary:    #0d0d0d;
    --bg-secondary:  #1a1a1a;
    --bg-card:       #222222;
    --border-color:  #333333;
    --text-primary:  #e8e8e8;
    --text-secondary:#a0a0a0;
    --text-muted:    #666666;
    --accent-yellow: #f0c040;
    --accent-hover:  #f5d060;
    --danger:        #e05555;
    --success:       #4caf50;
    --font-sans:     'Segoe UI', system-ui, -apple-system, sans-serif;
    --radius:        6px;
    --shadow:        0 2px 8px rgba(0,0,0,0.5);
}

/* ===== Reset & Base ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 16px; scroll-behavior: smooth; }

body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-sans);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

a { color: var(--accent-yellow); text-decoration: none; }
a:hover { color: var(--accent-hover); text-decoration: underline; }

h1, h2, h3, h4 { color: var(--text-primary); font-weight: 600; line-height: 1.3; }
h1 { font-size: 2rem; margin-bottom: 1rem; }
h2 { font-size: 1.5rem; margin-bottom: 0.75rem; }
h3 { font-size: 1.2rem; margin-bottom: 0.5rem; }

p { margin-bottom: 1rem; color: var(--text-secondary); }

/* ===== Header ===== */
.site-header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1.5rem;
    height: 64px;
    display: flex;
    align-items: center;
    gap: 2rem;
}

.logo-link { display: flex; align-items: center; gap: 0.5rem; text-decoration: none; }
.logo { height: 40px; width: auto; }
.logo-text { color: var(--accent-yellow); font-size: 1.4rem; font-weight: 700; letter-spacing: 1px; }

.main-nav { margin-left: auto; }
.main-nav ul { list-style: none; display: flex; gap: 0.25rem; align-items: center; }
.main-nav a, .nav-logout-btn {
    color: var(--text-secondary);
    padding: 0.4rem 0.75rem;
    border-radius: var(--radius);
    font-size: 0.95rem;
    transition: color 0.2s, background 0.2s;
}
.main-nav a:hover, .nav-logout-btn:hover {
    color: var(--text-primary);
    background: var(--bg-card);
    text-decoration: none;
}
.main-nav a.active { color: var(--accent-yellow); }

.nav-logout-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-family: var(--font-sans);
    font-size: 0.95rem;
}

.nav-toggle {
    display: none;
    background: none;
    border: none;
    color: var(--text-primary);
    font-size: 1.5rem;
    cursor: pointer;
    margin-left: auto;
}

/* ===== Main Content ===== */
.main-content {
    flex: 1;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

/* ===== Messages ===== */
.messages { margin-bottom: 1.5rem; }
.message {
    padding: 0.75rem 1rem;
    border-radius: var(--radius);
    margin-bottom: 0.5rem;
    border-left: 4px solid var(--border-color);
}
.message--success { border-color: var(--success); background: rgba(76,175,80,0.1); }
.message--error   { border-color: var(--danger);  background: rgba(224,85,85,0.1); }
.message--warning { border-color: var(--accent-yellow); background: rgba(240,192,64,0.1); }
.message--info    { border-color: #4a9eff; background: rgba(74,158,255,0.1); }

/* ===== Cards ===== */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}

/* ===== Buttons ===== */
.btn {
    display: inline-block;
    padding: 0.5rem 1.25rem;
    border-radius: var(--radius);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: background 0.2s, color 0.2s;
    text-decoration: none;
    font-family: var(--font-sans);
}
.btn-primary   { background: var(--accent-yellow); color: #111; }
.btn-primary:hover { background: var(--accent-hover); color: #111; text-decoration: none; }
.btn-secondary { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-color); }
.btn-secondary:hover { background: var(--border-color); text-decoration: none; }
.btn-danger    { background: var(--danger); color: #fff; }
.btn-danger:hover  { background: #c04040; text-decoration: none; }
.btn-sm { padding: 0.3rem 0.75rem; font-size: 0.82rem; }

/* ===== Forms ===== */
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; margin-bottom: 0.4rem; color: var(--text-secondary); font-size: 0.9rem; }
.form-control {
    width: 100%;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    color: var(--text-primary);
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    font-family: var(--font-sans);
    transition: border-color 0.2s;
}
.form-control:focus { outline: none; border-color: var(--accent-yellow); }
.form-errors { color: var(--danger); font-size: 0.85rem; margin-top: 0.25rem; }

/* ===== Pagination ===== */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.4rem;
    margin-top: 2rem;
    flex-wrap: wrap;
}
.pagination a, .pagination span {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 36px;
    padding: 0 0.5rem;
    border-radius: var(--radius);
    font-size: 0.9rem;
    border: 1px solid var(--border-color);
}
.pagination a { color: var(--text-secondary); background: var(--bg-card); }
.pagination a:hover { color: var(--text-primary); background: var(--border-color); text-decoration: none; }
.pagination .current { background: var(--accent-yellow); color: #111; border-color: var(--accent-yellow); font-weight: 600; }
.pagination .disabled { color: var(--text-muted); background: var(--bg-secondary); }

/* ===== Footer ===== */
.site-footer {
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
    padding: 1.5rem;
    text-align: center;
    margin-top: auto;
}
.footer-inner p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.25rem; }
.footer-inner a { color: var(--text-secondary); }

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .nav-toggle { display: block; }
    .main-nav {
        display: none;
        position: absolute;
        top: 64px;
        left: 0;
        right: 0;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem;
        z-index: 99;
    }
    .main-nav.open { display: block; }
    .main-nav ul { flex-direction: column; gap: 0.25rem; }
    .main-nav a, .nav-logout-btn { display: block; padding: 0.6rem 1rem; }
    .header-inner { position: relative; }
    .logo-text { font-size: 1.2rem; }
    .card-grid { grid-template-columns: 1fr; }
    h1 { font-size: 1.5rem; }
}
```

**`static/js/main.js`:**
```javascript
// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.main-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            nav.classList.toggle('open');
        });
    }
});
```

---

### Step 1.7 — Home app

```powershell
poetry run python manage.py startapp home apps\home
```

**`apps/home/models.py`:**
```python
from django.db import models
from django.conf import settings
from PIL import Image
import os


def compress_image(image_path, max_size_kb=400, max_width=1600):
    """Compress image to fit within max_size_kb and max_width."""
    img = Image.open(image_path)
    # Preserve EXIF orientation
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif:
            from PIL.ExifTags import TAGS
            for tag, value in exif.items():
                if TAGS.get(tag) == 'Orientation':
                    # handle rotation if needed
                    pass

    # Resize if too wide
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Convert RGBA to RGB for JPEG
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Save with quality reduction until under max_size_kb
    quality = 85
    while quality > 30:
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
        if os.path.getsize(image_path) <= max_size_kb * 1024:
            break
        quality -= 10


class PictureOfWeek(models.Model):
    image = models.ImageField(upload_to='picture_of_week/')
    description = models.CharField('popis', max_length=255)
    author = models.CharField('autor fotografie', max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField('aktivní', default=True)

    class Meta:
        verbose_name = 'fotografie týdne'
        verbose_name_plural = 'fotografie týdne'
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f'{self.description} ({self.author})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            compress_image(self.image.path)
```

**`apps/home/views.py`:**
```python
from django.shortcuts import render
from .models import PictureOfWeek


def index(request):
    picture = PictureOfWeek.objects.filter(is_active=True).first()
    return render(request, 'home/index.html', {'picture': picture})
```

**`apps/home/urls.py`:**
```python
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
]
```

**`apps/home/admin.py`:**
```python
from django.contrib import admin
from .models import PictureOfWeek


@admin.register(PictureOfWeek)
class PictureOfWeekAdmin(admin.ModelAdmin):
    list_display = ['description', 'author', 'uploaded_at', 'is_active']
    list_editable = ['is_active']
```

**`templates/home/index.html`:**
```html
{% extends 'base.html' %}

{% block title %}HOUSKi – Horolezecký oddíl Plzeň{% endblock %}

{% block content %}
<div class="home-layout">
    <div class="home-text">
        <h1>HOUSKi – Horolezecký oddíl Plzeň</h1>
        <p class="home-subtitle">Lezeme, horolezíme, lyžujeme a prostě žijeme v horách od roku ...</p>

        <h2>O nás</h2>
        <p>HOUSKi je místní horolezecký oddíl se sídlem v Plzni s bohatou historií.
           Sdružujeme přátele se společnými aktivitami jako lezení, horolezectví,
           expedice, bouldering, skialpinismus, běžecké lyžování a další outdoorové aktivity.</p>

        <h2>Co děláme</h2>
        <ul class="home-list">
            <li>🧗 Skalní lezení a bouldering</li>
            <li>⛰️ Horolezectví a expedice</li>
            <li>⛷️ Skialpinismus a běžky</li>
            <li>🚴 Cyklistické výlety</li>
            <li>🏕️ Trekking a outdoor aktivity</li>
        </ul>
    </div>

    {% if picture %}
    <aside class="home-picture">
        <div class="card">
            <img src="{{ picture.image.url }}" alt="{{ picture.description }}" class="picture-of-week-img">
            <p class="picture-caption">{{ picture.description }}</p>
            <p class="picture-author">Foto: {{ picture.author }}</p>
        </div>
    </aside>
    {% endif %}
</div>
{% endblock %}
```

Add to **`static/css/main.css`** (home section):
```css
/* ===== Home Page ===== */
.home-layout {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 2rem;
    align-items: start;
}
.home-list { padding-left: 1.5rem; color: var(--text-secondary); }
.home-list li { margin-bottom: 0.5rem; }
.home-subtitle { color: var(--accent-yellow); font-size: 1.1rem; margin-bottom: 1.5rem; }
.picture-of-week-img { width: 100%; border-radius: var(--radius); margin-bottom: 0.5rem; }
.picture-caption { color: var(--text-primary); font-size: 0.95rem; margin-bottom: 0.25rem; }
.picture-author { color: var(--text-muted); font-size: 0.85rem; }

@media (max-width: 900px) {
    .home-layout { grid-template-columns: 1fr; }
    .home-picture { order: -1; }
}
```

**`config/urls.py`:**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls', namespace='home')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Run migrations and test:**
```powershell
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py create_default_superuser
poetry run python manage.py runserver
```

✅ **Phase 1 complete checkpoint:** Visit `http://127.0.0.1:8000` — see home page. Visit `/admin/` — log in as brouk.

---

## Phase 2 — Authentication & User Management

**Goal:** Login/logout, forced password change on first login, profile edit page.

---

### Step 2.1 — URL wiring for auth

**Add to `config/urls.py`:**
```python
from django.contrib.auth import views as auth_views

urlpatterns += [
    path('login/',    auth_views.LoginView.as_view(template_name='registration/login.html'),    name='login'),
    path('logout/',   auth_views.LogoutView.as_view(),                                          name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/password-change/done/'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    path('profil/', include('apps.users.urls', namespace='users')),
]
```

### Step 2.2 — Login template

**`templates/registration/login.html`:**
```html
{% extends 'base.html' %}
{% block title %}Přihlášení – HOUSKi{% endblock %}
{% block content %}
<div class="auth-box">
    <h1>Přihlásit se</h1>
    <form method="post" class="auth-form">
        {% csrf_token %}
        {% for field in form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}">{{ field.label }}</label>
            <input type="{{ field.field.widget.input_type }}"
                   name="{{ field.html_name }}"
                   id="{{ field.id_for_label }}"
                   class="form-control {% if field.errors %}is-invalid{% endif %}"
                   value="{{ field.value|default_if_none:'' }}">
            {% for error in field.errors %}
                <p class="form-errors">{{ error }}</p>
            {% endfor %}
        </div>
        {% endfor %}
        {% if form.non_field_errors %}
            <p class="form-errors">{{ form.non_field_errors }}</p>
        {% endif %}
        <button type="submit" class="btn btn-primary" style="width:100%">Přihlásit se</button>
    </form>
</div>
{% endblock %}
```

Add to `static/css/main.css`:
```css
/* ===== Auth Box ===== */
.auth-box {
    max-width: 400px;
    margin: 3rem auto;
}
.auth-box h1 { margin-bottom: 1.5rem; }
```

### Step 2.3 — Forced password change middleware

**`apps/users/middleware.py`:**
```python
from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_URLS = [
    '/login/',
    '/logout/',
    '/password-change/',
    '/password-change/done/',
    '/admin/',
    '/static/',
    '/media/',
]


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and \
           getattr(request.user, 'must_change_password', False) and \
           not any(request.path.startswith(url) for url in EXEMPT_URLS):
            return redirect(reverse('password_change'))
        return self.get_response(request)
```

### Step 2.4 — Password change signal (reset flag)

**`apps/users/signals.py`:**
```python
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


# Flag is cleared when user successfully changes password via PasswordChangeView.
# We hook into the view's form_valid by overriding the view (see urls.py).
```

Override `PasswordChangeView` in `apps/users/views.py`:
```python
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages


class HOUSKiPasswordChangeView(BasePasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=['must_change_password'])
        messages.success(self.request, 'Heslo bylo úspěšně změněno.')
        return super().form_valid(form)
```

Update `config/urls.py` to use this view instead of the default `PasswordChangeView`.

### Step 2.5 — Profile view

**`apps/users/views.py`** (add):
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil byl aktualizován.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
```

**`apps/users/forms.py`:**
```python
from django import forms
from .models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone']
        labels = {
            'first_name': 'Jméno',
            'last_name':  'Příjmení',
            'email':      'E-mail',
            'telephone':  'Telefon',
        }
```

**`apps/users/urls.py`:**
```python
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.profile, name='profile'),
]
```

✅ **Phase 2 complete checkpoint:** Login at `/login/`, new users are redirected to change password, profile editable at `/profil/`.

---

## Phase 3 — Board (`apps/board`)

**Goal:** Board page with posts, pagination (25 per page), rich text, image upload, CRUD.

---

### Step 3.1 — Create app & model

```powershell
poetry run python manage.py startapp board apps\board
```

**`apps/board/models.py`:**
```python
from django.db import models
from django.conf import settings
from django_summernote.fields import SummernoteTextField
from apps.home.models import compress_image   # reuse helper


class BoardPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    headline = models.CharField('nadpis', max_length=200, blank=True)
    text = SummernoteTextField('text')
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('aktualizováno', auto_now=True)

    class Meta:
        verbose_name = 'příspěvek'
        verbose_name_plural = 'příspěvky'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.headline or f'Příspěvek #{self.pk}'


class BoardImage(models.Model):
    post = models.ForeignKey(BoardPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='board/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            compress_image(self.image.path)
```

### Step 3.2 — Board views

**`apps/board/views.py`:**
```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import BoardPost, BoardImage
from .forms import BoardPostForm, BoardImageFormSet


def board_list(request):
    posts = BoardPost.objects.select_related('author').prefetch_related('images')
    paginator = Paginator(posts, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'board/list.html', {'page_obj': page})


@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardPostForm(request.POST)
        formset = BoardImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            images = formset.save(commit=False)
            for i, img in enumerate(images):
                img.post = post
                img.order = i
                img.save()
            messages.success(request, 'Příspěvek byl přidán.')
            return redirect('board:list')
    else:
        form = BoardPostForm()
        formset = BoardImageFormSet(queryset=BoardImage.objects.none())
    return render(request, 'board/form.html', {'form': form, 'formset': formset, 'action': 'Přidat příspěvek'})


@login_required
def board_edit(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění upravit tento příspěvek.')
        return redirect('board:list')
    if request.method == 'POST':
        form = BoardPostForm(request.POST, instance=post)
        formset = BoardImageFormSet(request.POST, request.FILES, queryset=post.images.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            images = formset.save(commit=False)
            for img in images:
                img.post = post
                img.save()
            for img in formset.deleted_objects:
                img.delete()
            messages.success(request, 'Příspěvek byl upraven.')
            return redirect('board:list')
    else:
        form = BoardPostForm(instance=post)
        formset = BoardImageFormSet(queryset=post.images.all())
    return render(request, 'board/form.html', {'form': form, 'formset': formset, 'action': 'Upravit příspěvek', 'post': post})


@login_required
def board_delete(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění smazat tento příspěvek.')
        return redirect('board:list')
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Příspěvek byl smazán.')
        return redirect('board:list')
    return render(request, 'board/confirm_delete.html', {'post': post})
```

**`apps/board/forms.py`:**
```python
from django import forms
from django.forms import modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import BoardPost, BoardImage


class BoardPostForm(forms.ModelForm):
    class Meta:
        model = BoardPost
        fields = ['headline', 'text']
        labels = {'headline': 'Nadpis (nepovinný)', 'text': 'Text příspěvku'}
        widgets = {'text': SummernoteWidget()}


BoardImageFormSet = modelformset_factory(
    BoardImage,
    fields=['image'],
    extra=5,
    max_num=5,
    can_delete=True,
)
```

**`apps/board/urls.py`:**
```python
from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('',              views.board_list,   name='list'),
    path('novy/',         views.board_create, name='create'),
    path('<int:pk>/edit/', views.board_edit,  name='edit'),
    path('<int:pk>/smaz/', views.board_delete, name='delete'),
]
```

Add to `config/urls.py`:
```python
path('nastенka/', include('apps.board.urls', namespace='board')),
# Note: use ASCII-safe URL: 'nastенka' → 'nastanka' or 'board'
path('nastanka/', include('apps.board.urls', namespace='board')),
```

Add `'apps.board'` to `LOCAL_APPS` in settings.

### Step 3.3 — Board templates

**`templates/board/list.html`:**
```html
{% extends 'base.html' %}
{% block title %}Nástěnka – HOUSKi{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Nástěnka</h1>
    {% if user.is_authenticated %}
        <a href="{% url 'board:create' %}" class="btn btn-primary">+ Přidat příspěvek</a>
    {% endif %}
</div>

{% for post in page_obj %}
<article class="card board-post">
    <div class="post-meta">
        <span class="post-author">{{ post.author.username }}</span>
        <span class="post-date">{{ post.created_at|date:"j. n. Y H:i" }}</span>
    </div>
    {% if post.headline %}<h2 class="post-headline">{{ post.headline }}</h2>{% endif %}
    <div class="post-text">{{ post.text|safe }}</div>
    {% if post.images.exists %}
    <div class="post-images">
        {% for img in post.images.all %}
            <img src="{{ img.image.url }}" alt="" class="post-image-thumb">
        {% endfor %}
    </div>
    {% endif %}
    {% if user.is_authenticated and post.author == user or user.is_staff %}
    <div class="post-actions">
        <a href="{% url 'board:edit' post.pk %}" class="btn btn-secondary btn-sm">Upravit</a>
        <a href="{% url 'board:delete' post.pk %}" class="btn btn-danger btn-sm">Smazat</a>
    </div>
    {% endif %}
</article>
{% empty %}
<p>Zatím žádné příspěvky.</p>
{% endfor %}

{% include 'partials/pagination.html' with page_obj=page_obj %}
{% endblock %}
```

**`templates/partials/pagination.html`** (reusable):
```html
{% if page_obj.has_other_pages %}
<nav class="pagination" aria-label="Stránkování">
    {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}" aria-label="Předchozí">‹</a>
    {% else %}
        <span class="disabled">‹</span>
    {% endif %}

    {% for num in page_obj.paginator.page_range %}
        {% if page_obj.number == num %}
            <span class="current">{{ num }}</span>
        {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
            <a href="?page={{ num }}">{{ num }}</a>
        {% elif num == 1 or num == page_obj.paginator.num_pages %}
            <a href="?page={{ num }}">{{ num }}</a>
        {% elif num == page_obj.number|add:'-3' or num == page_obj.number|add:'3' %}
            <span class="disabled">…</span>
        {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}" aria-label="Další">›</a>
    {% else %}
        <span class="disabled">›</span>
    {% endif %}
</nav>
{% endif %}
```

Add board-specific CSS to `main.css`:
```css
/* ===== Board ===== */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.board-post { margin-bottom: 1.5rem; }
.post-meta { display: flex; gap: 1rem; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted); }
.post-author { color: var(--accent-yellow); }
.post-headline { font-size: 1.1rem; margin-bottom: 0.5rem; }
.post-text { color: var(--text-secondary); }
.post-text p { margin-bottom: 0.5rem; }
.post-images { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
.post-image-thumb { width: 120px; height: 90px; object-fit: cover; border-radius: var(--radius); }
.post-actions { margin-top: 1rem; display: flex; gap: 0.5rem; }
```

✅ **Phase 3 complete checkpoint:** Visit `/nastanka/` — see board with pagination.

---

## Phase 4 — Articles (`apps/articles`)

**Goal:** Article list/detail with categories, images, rich text, pagination.

---

### Step 4.1 — Create app & models

```powershell
poetry run python manage.py startapp articles apps\articles
```

**`apps/articles/models.py`:**
```python
from django.db import models
from django.conf import settings
from django.urls import reverse
from django_summernote.fields import SummernoteTextField
from apps.home.models import compress_image


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('climbing',     'Lezení'),
        ('mountains',    'Hory'),
        ('skialpinism',  'Skialpinismus'),
        ('trekking',     'Trekking'),
        ('other_sport',  'Jiný sport'),
        ('kids',         'Děti'),
        ('pub',          'Hospoda'),
    ]
    slug = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'kategorie'
        verbose_name_plural = 'kategorie'

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    headline = models.CharField('nadpis', max_length=300)
    text = SummernoteTextField('text')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='kategorie')
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('aktualizováno', auto_now=True)

    class Meta:
        verbose_name = 'článek'
        verbose_name_plural = 'články'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.headline

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'pk': self.pk})


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='articles/')
    caption = models.CharField('popisek', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            compress_image(self.image.path)
```

### Step 4.2 — Article views

Full CRUD views in `apps/articles/views.py` — same pattern as Board:
- `article_list(request)` — paginated, filter by category via `?category=climbing`
- `article_detail(request, pk)` — public detail
- `article_create(request)` — login required
- `article_edit(request, pk)` — login required + ownership
- `article_delete(request, pk)` — login required + ownership

**`apps/articles/urls.py`:**
```python
app_name = 'articles'
urlpatterns = [
    path('',                    views.article_list,   name='list'),
    path('<int:pk>/',           views.article_detail, name='detail'),
    path('novy/',               views.article_create, name='create'),
    path('<int:pk>/edit/',      views.article_edit,   name='edit'),
    path('<int:pk>/smaz/',      views.article_delete, name='delete'),
]
```

Add `path('clanky/', include('apps.articles.urls', namespace='articles'))` to `config/urls.py`.
Add `'apps.articles'` to `LOCAL_APPS`.

### Step 4.3 — Article templates

- `templates/articles/list.html` — card grid, category filter chips, pagination
- `templates/articles/detail.html` — full article with images
- `templates/articles/form.html` — summernote + multi-image formset + category checkboxes

✅ **Phase 4 complete checkpoint:** `/clanky/` shows article list with category filter and pagination.

---

## Phase 5 — Activities (`apps/activities`)

**Goal:** Planned activities list, CRUD for logged-in users.

---

### Step 5.1 — Create app & model

```powershell
poetry run python manage.py startapp activities apps\activities
```

**`apps/activities/models.py`:**
```python
from django.db import models
from django.conf import settings
from django_summernote.fields import SummernoteTextField


class Activity(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    name = models.CharField('název', max_length=200)
    start_date = models.DateField('datum začátku')
    end_date = models.DateField('datum konce', null=True, blank=True)
    location = models.CharField('místo', max_length=200)
    description = SummernoteTextField('popis')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'aktivita'
        verbose_name_plural = 'aktivity'
        ordering = ['start_date']

    def __str__(self) -> str:
        return self.name
```

### Step 5.2 — Activity views & URLs

- `activity_list(request)` — upcoming activities first (filter `start_date >= today`), then past
- `activity_create`, `activity_edit`, `activity_delete` — login required + ownership

URL path: `path('aktivity/', include('apps.activities.urls', namespace='activities'))`

### Step 5.3 — Activity templates

- `templates/activities/list.html` — upcoming section + past section, card layout
- `templates/activities/form.html` — date pickers + summernote description

✅ **Phase 5 complete checkpoint:** `/aktivity/` shows upcoming and past activities.

---

## Phase 6 — Contacts (`apps/contacts`)

**Goal:** Simple static page with club contact info.

---

### Step 6.1 — Create app & view

```powershell
poetry run python manage.py startapp contacts apps\contacts
```

**`apps/contacts/views.py`:**
```python
from django.shortcuts import render

def index(request):
    return render(request, 'contacts/index.html')
```

**`templates/contacts/index.html`:** Static HTML with contact names, emails, roles — fill in real data later.

URL: `path('kontakty/', include('apps.contacts.urls', namespace='contacts'))`

✅ **Phase 6 complete checkpoint:** `/kontakty/` shows static contacts page.

---

## Phase 7 — Polish & Refinement

**Goal:** All Czech labels verified, responsive QA, admin improved, README written.

---

### Step 7.1 — Admin customization for all apps

For each app, add `list_display`, `search_fields`, `list_filter` to admin classes:

```python
# articles admin example
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display  = ['headline', 'author', 'created_at']
    list_filter   = ['categories', 'created_at']
    search_fields = ['headline', 'text', 'author__username']
    date_hierarchy = 'created_at'
```

### Step 7.2 — Responsive QA checklist
- [ ] Test on 320px mobile width
- [ ] Mobile nav opens/closes correctly
- [ ] Images don't overflow on mobile
- [ ] Board post form usable on mobile (summernote)
- [ ] Pagination looks good on mobile

### Step 7.3 — Category seed data

Create a data migration or management command to populate `Category` table:
```python
# apps/articles/management/commands/seed_categories.py
categories = [
    ('climbing', 'Lezení'), ('mountains', 'Hory'), ('skialpinism', 'Skialpinismus'),
    ('trekking', 'Trekking'), ('other_sport', 'Jiný sport'), ('kids', 'Děti'), ('pub', 'Hospoda'),
]
```

### Step 7.4 — README

Document in `README.md`:
1. Prerequisites (Python 3.12+, Poetry 2.4.x)
2. Local setup commands
3. Creating superuser
4. Running dev server
5. Running tests
6. Project structure overview

✅ **Phase 7 complete checkpoint:** Everything works, README written, admin polished.

---

## Phase 8 — PythonAnywhere Deployment

**Goal:** Deploy to pythonanywhere.com and document update workflow.

---

### Step 8.1 — Production settings

**`config/settings/prod.py`:**
```python
from .base import *
from decouple import config, Csv

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

SECRET_KEY = config('SECRET_KEY')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security headers
SECURE_SSL_REDIRECT = False    # PythonAnywhere handles HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Step 8.2 — Export dependencies

```powershell
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Step 8.3 — PythonAnywhere deployment steps

1. **Upload code** — via git clone or zip upload:
   ```bash
   git clone https://github.com/yourrepo/houski-web.git
   ```

2. **Create virtualenv on PythonAnywhere:**
   ```bash
   python3.12 -m venv ~/.virtualenvs/houski
   source ~/.virtualenvs/houski/bin/activate
   pip install -r requirements.txt
   ```

3. **Set environment variables** — in PA dashboard → `.env` file or in WSGI config:
   ```
   SECRET_KEY=your-production-secret-key
   DJANGO_SETTINGS_MODULE=config.settings.prod
   ALLOWED_HOSTS=yourname.pythonanywhere.com
   ```

4. **Configure WSGI file** (PA dashboard → Web → WSGI configuration file):
   ```python
   import os, sys
   path = '/home/yourname/houski-web'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. **Static and media file mappings** (PA dashboard → Web → Static files):
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

7. **Reload web app** — PA dashboard → Web → Reload button.

### Step 8.4 — Update & redeploy workflow

```bash
# On PythonAnywhere console:
cd ~/houski-web
git pull origin main
source ~/.virtualenvs/houski/bin/activate
pip install -r requirements.txt     # only if dependencies changed
python manage.py migrate            # only if migrations changed
python manage.py collectstatic --noinput
# Then reload via PA dashboard or API:
# touch /var/www/yourname_pythonanywhere_com_wsgi.py
```

✅ **Phase 8 complete:** Site running on PythonAnywhere.

---

## Quick Reference — Daily Commands

```powershell
# Start dev server
poetry run python manage.py runserver

# Create migrations
poetry run python manage.py makemigrations

# Apply migrations
poetry run python manage.py migrate

# Run tests
poetry run pytest

# Open Django shell
poetry run python manage.py shell

# Collect static files
poetry run python manage.py collectstatic
```

---

## Dependency Summary

```toml
[tool.poetry.dependencies]
python           = "^3.12"
django           = "^5.0"
pillow           = "^10.0"
python-decouple  = "^3.8"
whitenoise       = "^6.6"
django-summernote = "^0.8"

[tool.poetry.group.dev.dependencies]
pytest           = "^8.0"
pytest-django    = "^4.8"
pytest-cov       = "^5.0"
factory-boy      = "^3.3"
django-debug-toolbar = "^4.3"
```
