import io

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from PIL import Image

from apps.articles.models import Article
from apps.home.models import SummernoteAttachment
from apps.users.models import User

ARTICLE_HTML = '''
    <h1>Test &amp; clanek</h1>
    <h2>podtitul<br></h2>
    <p class="post-meta">
        <span class="post-date">2009-07-07 14:39:00</span>
    </p>
    <div class="post-text"><p>Text</p></div>
    <div class="post-images">
        <figure>
            <img class="article-image" src="pic one.png" alt="image">
            <figcaption>Popisek</figcaption>
        </figure>
    </div>
    <div class="post-text"><p><div class="center">Vnorene</div></p></div>
'''


@pytest.fixture
def root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / 'media'
    root = tmp_path / 'articles'
    folder = root / 'Test2009'
    folder.mkdir(parents=True)
    (folder / 'index.html').write_text(ARTICLE_HTML, encoding='utf-8')
    buf = io.BytesIO()
    Image.new('RGB', (10, 10)).save(buf, 'PNG')
    (folder / 'pic one.png').write_bytes(buf.getvalue())
    (root / 'article_dates.csv').write_text(
        'folder,created_at,confidence,evidence\nTest2009,2009-06-25,specific,x\n', encoding='utf-8')
    (root / 'HomePage').mkdir()
    (root / 'HomePage' / 'index.html').write_text(ARTICLE_HTML, encoding='utf-8')
    return root


@pytest.fixture
def brouk(db):
    return User.objects.create_user(username='brouk', password='Pass123!', must_change_password=False)


def test_import_creates_article_with_csv_date_and_jpeg_image(root, brouk):
    call_command('import_articles', root)

    article = Article.objects.get()
    assert article.headline == 'Test & clanek'
    assert article.author == brouk
    assert (article.created_at.year, article.created_at.month, article.created_at.day) == (2009, 6, 25)
    attachment = SummernoteAttachment.objects.get()
    assert attachment.file.name.endswith('.jpg')
    assert f'src="/media/{attachment.file.name}"' in article.text
    assert '<p><b>podtitul</b></p>' in article.text
    assert '<p><i>Popisek</i></p>' in article.text
    assert '<p align="center">Vnorene</p>' in article.text
    assert attachment.owner == article


def test_non_image_file_becomes_download_link(root, brouk):
    folder = root / 'Test2009'
    (folder / 'doc.pdf').write_bytes(b'%PDF-1.4')
    html = (folder / 'index.html').read_text(encoding='utf-8')
    (folder / 'index.html').write_text(
        html + '<div class="post-images"><figure><img src="doc.pdf" alt="image"></figure></div>',
        encoding='utf-8')

    call_command('import_articles', root)

    assert '<a href="/media/articles/files/doc.pdf">doc.pdf</a>' in Article.objects.get().text
    assert SummernoteAttachment.objects.count() == 1


def test_import_is_idempotent(root, brouk):
    call_command('import_articles', root)
    call_command('import_articles', root)
    assert Article.objects.count() == 1
    assert SummernoteAttachment.objects.count() == 1


def test_dry_run_writes_nothing(root, brouk):
    call_command('import_articles', root, '--dry-run')
    assert Article.objects.count() == 0
    assert SummernoteAttachment.objects.count() == 0


def test_unknown_author_fails(root, db):
    with pytest.raises(CommandError):
        call_command('import_articles', root)
