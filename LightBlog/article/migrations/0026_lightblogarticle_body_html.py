# Generated by Django 2.2.5 on 2019-10-21 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0025_auto_20191021_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightblogarticle',
            name='body_html',
            field=models.TextField(default=' 默认 ', verbose_name=' Html 内容 '),
        ),
    ]