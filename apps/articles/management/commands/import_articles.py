import csv
import html
import re
import unicodedata
from datetime import datetime, time
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.articles.models import Article
from apps.home.models import SummernoteAttachment
from apps.users.models import User

AUTHOR_USERNAME = 'brouk'
SKIP_FOLDERS = {'HomePage'}
DATES_FILE = 'article_dates.csv'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
OTHER_FILES_DIR = 'articles/files'

_H1 = re.compile(r'<h1>(.*?)</h1>', re.S)
_H2 = re.compile(r'<h2>(.*?)(?:<br\s*/?>)?\s*</h2>', re.S)
_POST_DATE = re.compile(r'class="post-date">\s*([^<]+?)\s*<')
_BLOCK_START = re.compile(r'<div class="post-(?:text|images)">')
_IMG = re.compile(r'<img[^>]*?src="([^"]+)"')
_CENTER = re.compile(r'<p>\s*<div class="center">(.*?)</div>\s*</p>', re.S)
_FIGCAPTION = re.compile(r'<figcaption>(.*?)</figcaption>', re.S)


def parse_article(html_text):
    """Return (headline, subtitle, post_date, blocks); each block is
    ('text', html) or ('images', [(src, caption_or_None), ...])."""
    headline = html.unescape(_H1.search(html_text).group(1).strip())
    h2 = _H2.search(html_text)
    subtitle = h2.group(1).strip() if h2 else ''
    post_date = _POST_DATE.search(html_text).group(1)

    starts = list(_BLOCK_START.finditer(html_text))
    blocks = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(html_text)
        chunk = html_text[m.end():end].rstrip()
        chunk = chunk[:-len('</div>')] if chunk.endswith('</div>') else chunk
        if 'post-images' in m.group(0):
            figures = [(_IMG.search(f).group(1), (_FIGCAPTION.search(f) or [None, None])[1])
                       for f in chunk.split('<figure>')[1:]]
            blocks.append(('images', figures))
        else:
            blocks.append(('text', _CENTER.sub(r'<p align="center">\1</p>', chunk.strip())))
    return headline, subtitle, post_date, blocks


def load_dates(path):
    if not path.exists():
        return {}
    with open(path, encoding='utf-8', newline='') as f:
        return {row['folder']: row['created_at'] for row in csv.DictReader(f)}


def to_aware(value):
    if len(value) == 10:
        naive = datetime.combine(datetime.strptime(value, '%Y-%m-%d').date(), time(12, 0))
    else:
        naive = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return timezone.make_aware(naive)


def resolve_file(folder, src):
    """folder/src, tolerating Unicode normalization (NFC/NFD) differences
    between the HTML and the file name on disk (zip/unzip may change them)."""
    path = folder / src
    if path.is_file():
        return path
    wanted = unicodedata.normalize('NFC', src)
    for candidate in folder.iterdir():
        if unicodedata.normalize('NFC', candidate.name) == wanted and candidate.is_file():
            return candidate
    raise FileNotFoundError(path)


class Command(BaseCommand):
    help = (
        'Imports articles from <root>/<folder>/index.html (images next to it). '
        'Dates come from <root>/article_dates.csv, falling back to the HTML post-date.'
    )

    def add_arguments(self, parser):
        parser.add_argument('root', type=Path)
        parser.add_argument('--author', default=AUTHOR_USERNAME)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, root, author, dry_run, **options):
        try:
            author_user = User.objects.get(username=author)
        except User.DoesNotExist:
            raise CommandError(f'User "{author}" does not exist.')
        if not root.is_dir():
            raise CommandError(f'{root} is not a directory.')

        dates = load_dates(root / DATES_FILE)
        counts = {'created': 0, 'skipped': 0, 'failed': 0}
        for folder in sorted(p for p in root.iterdir() if (p / 'index.html').is_file()):
            if folder.name in SKIP_FOLDERS:
                continue
            try:
                result = self.import_folder(folder, author_user, dates, dry_run)
            except Exception as exc:
                result = 'failed'
                self.stderr.write(f'{folder.name}: FAILED - {exc!r}')
            counts[result] += 1
            self.stdout.write(f'{folder.name}: {result}')

        suffix = ' (dry run)' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{counts["created"]} created, {counts["skipped"]} skipped, {counts["failed"]} failed{suffix}.'
        ))

    def import_folder(self, folder, author_user, dates, dry_run):
        headline, subtitle, post_date, blocks = parse_article(
            (folder / 'index.html').read_text(encoding='utf-8'))
        created_at = to_aware(dates.get(folder.name, post_date))

        if Article.objects.filter(headline=headline, created_at=created_at).exists():
            return 'skipped'

        for kind, content in blocks:
            if kind == 'images':
                for src, _caption in content:
                    resolve_file(folder, src)
        if dry_run:
            return 'created'

        created_files = []
        stored_files = []
        try:
            with transaction.atomic():
                urls = {}
                parts = [f'<p><b>{subtitle}</b></p>'] if subtitle else []
                for kind, content in blocks:
                    if kind == 'text':
                        parts.append(content)
                        continue
                    for src, caption in content:
                        if src not in urls:
                            urls[src] = self.store(resolve_file(folder, src), created_files, stored_files)
                        if Path(src).suffix.lower() in IMAGE_EXTENSIONS:
                            parts.append(f'<p><img src="{urls[src]}" alt="image"></p>')
                        else:
                            parts.append(f'<p><a href="{urls[src]}">{Path(src).name}</a></p>')
                        if caption:
                            parts.append(f'<p><i>{caption}</i></p>')
                Article.objects.create(
                    author=author_user, headline=headline,
                    text='\n'.join(parts), created_at=created_at,
                )
        except Exception:
            for attachment in created_files:
                attachment.file.delete(save=False)
                attachment.thumbnail.delete(save=False)
            for name in stored_files:
                default_storage.delete(name)
            raise
        return 'created'

    @staticmethod
    def store(path, created_files, stored_files):
        """Store `path` and return its media URL. Images become
        SummernoteAttachments (save() compresses to JPEG and makes the
        thumbnail); anything else (e.g. a PDF) is stored as a plain file."""
        with open(path, 'rb') as f:
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                attachment = SummernoteAttachment(name=path.name)
                attachment.file.save(path.name, File(f), save=True)
                created_files.append(attachment)
                return settings.MEDIA_URL + attachment.file.name
            name = default_storage.save(f'{OTHER_FILES_DIR}/{path.name}', File(f))
            stored_files.append(name)
            return settings.MEDIA_URL + name
