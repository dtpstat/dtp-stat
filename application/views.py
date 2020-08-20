from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point

from data import models as data_models
from data import utils as data_utils
from application import models
from application import forms
from application import utils

import requests
import datetime


def home(request):
    dtps = data_models.DTP.objects.all()

    return render(request, "index.html", context={
        "dtps": dtps
    })


def blog(request, tag=None):
    posts = models.BlogPost.objects.filter(created_at__lte=timezone.now())
    header = "Статьи и исследования"

    if tag:
        posts = posts.filter(tags__name=tag)
        header = header + " – " + tag

    return render(request, "blog/index.html", context={
        "posts": posts,
        "header": header
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


def donate(request):
    try:
        text = get_object_or_404(models.Page, slug="donate").text
    except:
        text = None

    return render(request, "donate.html", context={
        "text": text
    })


def dtp(request, slug):
    dtp_item = get_object_or_404(data_models.DTP, slug=slug)
    participants = dtp_item.participant_set.order_by('violations')
    vehicles = data_models.Vehicle.objects.filter(participant__dtp=dtp_item).distinct()
    injured = dtp_item.participant_set.filter(severity__level__in=[1,2,3]).count()
    dead = dtp_item.participant_set.filter(severity__level__in=[4]).count()

    return render(request, "dtp/dtp.html", context={
        'dtp': dtp_item,
        'participants': participants,
        'vehicles': vehicles,
        'injured': injured,
        'dead': dead
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
            ticket_item, created = models.Ticket.objects.get_or_create(
                dtp=dtp
            )
            ticket_item.data={"lat": form.cleaned_data.get('lat'), "long": form.cleaned_data.get('long')}
            ticket_item.category = 'fix_point'
            if is_moderator:
                if form.cleaned_data.get('lat') and form.cleaned_data.get('long'):
                    ticket_item.status = "done"
                    dtp.point = Point(form.cleaned_data.get('long'), form.cleaned_data.get('lat'))
                    dtp.save()
                else:
                    ticket_item.status = "no"

            ticket_item.save()

            return render(request, "dtp/fix_point.html", context={
                'dtp': dtp,
                "is_moderator": is_moderator,
                'message': "Спасибо за помощь! Мы проверим и скорректируем координаты!",
            })
        else:
            error = form.errors

    geocode_point_data = data_utils.geocode(dtp)

    geo = {
        "source": [dtp.point.coords[1], dtp.point.coords[0]],
        "geocode": [geocode_point_data['lat'], geocode_point_data['long']]
    }

    if is_moderator:
        coordinates_tickets = dtp.ticket_set.filter(status="new", category="fix_point")
        if coordinates_tickets:
            coordinates_ticket = coordinates_tickets.latest('created_at')
            if coordinates_ticket and coordinates_ticket.data.get('lat') and coordinates_ticket.data.get('long'):
                geo['ticket'] = [coordinates_ticket.data.get('lat'), coordinates_ticket.data.get('long')]

    return render(request, "dtp/fix_point.html", context={
        'dtp': dtp,
        'form': form,
        "geo": geo,
        "error": error,
        "is_moderator": is_moderator
    })


@login_required(login_url="/accounts/login/")
def board(request):
    return redirect("tickets_list")
    #return render(request, "board/index.html", context={})


@login_required(login_url="/accounts/login/")
def tickets_list(request):
    tickets_qs = utils.get_moderator_tickets(request)
    return render(request, "board/tickets_list.html", context={
        "tickets_new": tickets_qs.all().order_by('-created_at'),
        "tickets_done": tickets_qs.filter(status__in=["done","no"])
    })


@login_required(login_url="/accounts/login/")
def ticket(request, ticket_id):
    ticket_item = get_object_or_404(models.Ticket, id=ticket_id)
    ticket_qs = utils.get_moderator_tickets(request)

    if not ticket_item in ticket_qs:
        return redirect("tickets_list")
    elif ticket_item.category == "fix_point" and ticket_item.status == "new":
        return redirect("dtp_fix_point", ticket_item.dtp.slug)
    else:
        return render(request, "board/ticket.html", context={
            "ticket_item": ticket_item
        })


