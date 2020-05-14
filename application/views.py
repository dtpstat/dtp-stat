from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from data import models as data_models
from data import utils as data_utils
from application import models
from application import forms


import datetime


def home(request):
    dtps = data_models.DTP.objects.all()

    return render(request, "index.html", context={
        "dtps": dtps
    })


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


def opendata(request):
    opendata = models.OpenData.objects.all().order_by("region__name")
    start_date = datetime.datetime(2015, 1, 1)
    return render(request, "opendata.html", context={
        'opendata': opendata,
        'start_date': start_date
    })


def dtp(request, slug):
    dtp = get_object_or_404(data_models.DTP, slug=slug)

    return render(request, "dtp/dtp.html", context={
        'dtp': dtp
    })


def dtp_fix_point(request, slug):
    dtp = get_object_or_404(data_models.DTP, slug=slug)
    error = ""
    form = forms.FixPoint()

    if request.method == 'POST':
        form = forms.FixPoint(request.POST)
        if form.is_valid():
            feedback_item = models.Feedback(
                dtp=dtp,
                data={"lat": form.cleaned_data.get('lat'), "long": form.cleaned_data.get('long')}
            )
            feedback_item.save()

            return render(request, "dtp/fix_point.html", context={
                'message': "Спасибо за помощь! Мы проверим и скорректируем координаты!",
            })
        else:
            error = form.errors

    data_utils.get_geocode_point(dtp)

    return render(request, "dtp/fix_point.html", context={
        'dtp': dtp,
        'form': form,
        "geo": {x.source:[x.point.coords[1], x.point.coords[0]] for x in dtp.geo_set.all()},
        "error": error
    })




