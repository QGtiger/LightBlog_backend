# Generated by Django 2.2.5 on 2019-10-21 15:08

import article.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0026_lightblogarticle_body_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightblogarticleimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=article.models.lightblog_articleimgs),
        ),
    ]
