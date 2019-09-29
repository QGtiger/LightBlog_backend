from django.shortcuts import render,get_object_or_404
from .models import BlogArticle
from django.contrib.auth.decorators import login_required

@login_required(login_url='/account/login/')
def blog_list(request):
    username = request.session.get('username')
    blogs = BlogArticle.objects.all()
    return render(request, "blog/blog_list.html",locals())

@login_required(login_url='/account/login/')
def blog_detail(request,article_id):
    # article = BlogArticle.objects.get(id = article_id)
    username = request.session.get('username')
    article = get_object_or_404(BlogArticle, id = article_id)
    publish = article.publish
    return render(request, "blog/blog_detail.html", locals())