# Generated by Django 2.2.5 on 2019-12-23 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0009_auto_20191220_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightblogcomment',
            name='report_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lightblogcomment_reply',
            name='report_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
