from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 获取settings 的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LightBlog.settings')

# 定义Celery对象，并将项目配置信息加载到对象中去
# Celery的参数一般以项目名命名
app = Celery('LightBlog')

# 配置文件需要写在setting.py中，并且配置项需要使用`CELERY_`作为前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 能够自动加载所有在django中注册的app，也就是setting.py中的INSTALLED_APPS
app.autodiscover_tasks()


# 测试代码
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
