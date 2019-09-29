from django import template
from django.db.models import Count
from article.models import ArticlePost
from django.conf import settings
import redis
import re
from article.models import Carousel
register = template.Library()
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


@register.simple_tag
def total_articles():
    return ArticlePost.objects.count()


@register.simple_tag
def author_total_articles(user):
    return user.article_post.count()


@register.inclusion_tag('article/list/latest_articles.html')
def latest_articles(n=5):
    latest_articles = ArticlePost.objects.order_by('-created')[:n]
    return {"latest_articles": latest_articles}


@register.simple_tag
def most_commented_articles(n=5):
    return ArticlePost.objects.annotate(total_comments=Count(
        'comments')).order_by('-total_comments')[:n]


@register.inclusion_tag('article/list/most_views.html')
def most_views():
    length = r.zcard('article_ranking')
    article_ranking = r.zrange("article_ranking", 0, length, desc=True)[:5]
    article_ranking_ids = [int(id) for id in article_ranking]
    most_viewed = list(ArticlePost.objects.filter(id__in=article_ranking_ids))
    most_viewed.sort(key=lambda x: article_ranking_ids.index(x.id))
    return {'most_viewed': most_viewed}


@register.filter
def init_blog(content):
    content_text1 = content.replace(
        '<p>',
        '').replace(
        '</p>',
        '').replace(
            "'",
        '')
    # 去掉图片链接
    content_text2 = re.sub(r'(!\[.*?\]\(.*?\))', '', content_text1)
    # 去掉markdown标签
    pattern = r'[\\\`\*\_\[\]\#\+\-\!\>]'
    content_text3 = re.sub(pattern, '', content_text2)
    return content_text3


@register.inclusion_tag('article/list/Carousel.html')
def carousel_img():
    carousels = Carousel.objects.all()
    return {'img_urls': carousels}
