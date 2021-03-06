# Generated by Django 2.1.5 on 2019-05-28 22:53

import article.models
from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0015_auto_20190528_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='image_preview',
            field=imagekit.models.fields.ProcessedImageField(default='default/preview.jpg', upload_to=article.models.article_img_path, verbose_name='展示图片'),
        ),
    ]
