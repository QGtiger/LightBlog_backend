# Generated by Django 2.1.5 on 2019-05-31 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0016_auto_20190528_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepost',
            name='word_count',
            field=models.IntegerField(default=233, verbose_name=' 文章字数 '),
        ),
    ]
