from django.shortcuts import render
from django.shortcuts import get_object_or_404
from . import models
from django.utils import timezone


def home(request):
    return render(request, "index.html")


def blog(request):
    posts = models.BlogPost.objects.filter(created_at__lte=timezone.now())
    return render(request, "blog/index.html", context={
        "posts": posts
    })


def blog_post(request, slug):
    post = get_object_or_404(models.BlogPost, slug=slug)
    return render(request, "blog/post.html", context={
        'post': post
    })


def page(request, slug):
    page = get_object_or_404(models.Page, slug=slug)
    return render(request, "page.html", context={
        'page': page
    })