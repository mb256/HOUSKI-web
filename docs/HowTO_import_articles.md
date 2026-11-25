# HowTO: Import articles on PythonAnywhere

Imports the legacy articles (`<root>/<Folder>/index.html` + images) with
`manage.py import_articles`. Idempotent: an article with the same headline and
date is skipped, so re-running is safe.

Source content: `HOUSKI-web-content\horoweb_clanky\horoweb_clanky`
(85 folders, `HomePage` is skipped by the command, plus `article_dates.csv`).

## 1. Prerequisites (local)

- The `import_articles` command is committed and pushed to `main`
  (`apps/articles/management/commands/import_articles.py`).
- Dates are reviewed in `article_dates.csv` (columns `folder,created_at`;
  `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`). Missing folders fall back to the
  HTML `post-date`.

## 2. Deploy code (PythonAnywhere Bash console)

```bash
~/houski-web/scripts/pa_update.sh
```

## 3. Back up the production DB and media

```bash
cd ~/houski-web
cp db.sqlite3 ~/db.sqlite3.bak_$(date +%F)
tar czf ~/media.bak_$(date +%F).tgz media
```

(If production uses MySQL instead of SQLite, use `mysqldump` instead.)

## 4. Upload the content folder

Local (PowerShell) - zip the folder:

```powershell
Compress-Archive -Path C:\Users\z0040c9z\workspace\HOUSKI-web-content\horoweb_clanky\horoweb_clanky -DestinationPath $HOME\horoweb_clanky.zip -Force
```

PythonAnywhere: Files tab -> upload `horoweb_clanky.zip` to `/home/<user>/`
(upload limit applies; for larger archives split it or use `git`/`scp` from a
paid account). Then in Bash:

```bash
cd ~ && mkdir -p horoweb_clanky && unzip -q horoweb_clanky.zip -d horoweb_clanky
ls horoweb_clanky            # check if there is one more nested horoweb_clanky/ level
```

Use the directory that directly contains `article_dates.csv` as `<root>` below.

## 5. Dry run, then real import

```bash
cd ~/houski-web
source ~/.virtualenvs/houski/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod

python manage.py import_articles ~/horoweb_clanky/horoweb_clanky --dry-run
python manage.py import_articles ~/horoweb_clanky/horoweb_clanky
```

Expected: `84 created, 0 skipped, 0 failed.` (second run: `0 created, 84 skipped`).
Requires user `brouk` to exist (`--author <username>` to override).

## 6. Verify and reload

- Reload the web app (Web tab, or `touch /var/www/<user>_pythonanywhere_com_wsgi.py`).
- Check the article list and a few articles with images/PDFs.
- Images land in `media/` (as Summernote attachments with thumbnails), other
  files in `media/articles/files/`. Make sure the Web tab serves `/media/` from
  the project `media/` directory.

## 7. Cleanup / rollback

```bash
rm -rf ~/horoweb_clanky ~/horoweb_clanky.zip
```

Rollback: restore `~/db.sqlite3.bak_<date>` to `db.sqlite3` and extract
`~/media.bak_<date>.tgz` over `media/`.
