# Generated by Django 2.2.5 on 2019-10-17 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0021_lightblogspecialcolumn_ispublish'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightblogpersonalcolumn',
            name='status',
            field=models.IntegerField(default=1, verbose_name=' 栏目显示 '),
        ),
    ]
