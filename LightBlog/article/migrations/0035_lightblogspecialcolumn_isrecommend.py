# Generated by Django 2.2.5 on 2019-11-28 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0034_lightblogarticle_checktime'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightblogspecialcolumn',
            name='isRecommend',
            field=models.BooleanField(default=False, verbose_name=' 是否推荐 '),
        ),
    ]