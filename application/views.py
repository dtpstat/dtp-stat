from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from data import models as data_models
from data import utils as data_utils
from application import models
from application import forms
from application import utils


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
    dtp_item = get_object_or_404(data_models.DTP, slug=slug)

    return render(request, "dtp/dtp.html", context={
        'dtp': dtp_item
    })


def dtp_fix_point(request, slug):
    dtp = get_object_or_404(data_models.DTP, slug=slug)
    error = ""

    is_moderator = utils.is_moderator(request.user)

    if is_moderator:
        form = forms.FixPointModerator()
    else:
        form = forms.FixPoint()

    if request.method == 'POST':
        if is_moderator:
            form = forms.FixPointModerator(request.POST)
        else:
            form = forms.FixPoint(request.POST)

        if form.is_valid():
            feedback_item, created = models.Feedback.objects.get_or_create(
                dtp=dtp
            )
            feedback_item.data={"lat": form.cleaned_data.get('lat'), "long": form.cleaned_data.get('long')}

            if is_moderator:
                if form.cleaned_data.get('lat') and form.cleaned_data.get('long'):
                    feedback_item.status = "done"
                else:
                    feedback_item.status = "no"

            feedback_item.save()

            return render(request, "dtp/fix_point.html", context={
                'message': "Спасибо за помощь! Мы проверим и скорректируем координаты!",
            })
        else:
            error = form.errors

    data_utils.get_geocode_point(dtp)

    if is_moderator:
        geo = {x.source:[x.point.coords[1], x.point.coords[0]] for x in dtp.geo_set.all()}
    else:
        geo = {x.source: [x.point.coords[1], x.point.coords[0]] for x in dtp.geo_set.all() if x.source != "user"}

    return render(request, "dtp/fix_point.html", context={
        'dtp': dtp,
        'form': form,
        "geo": geo,
        "error": error
    })


@login_required(login_url="/accounts/login/")
def board(request):
    return render(request, "board/index.html", context={})


@login_required(login_url="/accounts/login/")
def feedback_list(request):
    feedback_qs = utils.get_moderator_feedback(request)
    return render(request, "board/feedback_list.html", context={
        "feedback_new": feedback_qs.filter(status="new"),
        "feedback_done": feedback_qs.filter(status__in=["done","no"])
    })


@login_required(login_url="/accounts/login/")
def feedback(request, feedback_id):
    feedback_item = get_object_or_404(models.Feedback, id=feedback_id)
    feedback_qs = utils.get_moderator_feedback(request)

    if not feedback_item in feedback_qs:
        return redirect("feedback_list")
    else:
        return render(request, "board/feedback.html", context={
            "feedback_item": feedback_item
        })


