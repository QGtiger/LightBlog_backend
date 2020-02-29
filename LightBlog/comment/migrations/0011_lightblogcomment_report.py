# Generated by Django 2.2.5 on 2019-12-23 16:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comment', '0010_auto_20191223_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightBlogComment_report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_type', models.IntegerField(default=1, verbose_name='1 为主评论， 2为子评论')),
                ('commentId', models.IntegerField(verbose_name='评论id ')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('reported_text', models.TextField(blank=True, null=True)),
                ('report_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_all_report', to='comment.LightBlog_report')),
                ('report_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_report', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]