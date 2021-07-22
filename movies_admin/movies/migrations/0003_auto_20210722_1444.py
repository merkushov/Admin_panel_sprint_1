# Generated by Django 3.1 on 2021-07-22 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_auto_20210721_1202'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='moviegenre',
            constraint=models.UniqueConstraint(fields=('movie_id', 'genre_id'), name='movie_genre_main_uidx'),
        ),
    ]
