from django.db import migrations, models


class Migration(migrations.Migration):
    """Rows existing at migration time are historical: they get False.
    The field default is then switched to True for all future articles."""

    dependencies = [
        ('articles', '0007_alter_article_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='show_author',
            field=models.BooleanField(default=False, verbose_name='zobrazit autora'),
        ),
        migrations.AlterField(
            model_name='article',
            name='show_author',
            field=models.BooleanField(default=True, verbose_name='zobrazit autora'),
        ),
    ]
