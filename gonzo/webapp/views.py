from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def index(request):
    return HttpResponse("index")

def hunt_by_id(request, slug):
    return HttpResponse("by id")

def hunt_comments(request, slug):
    return HttpResponse("comments")

def photo_index(request, slug):
    return HttpResponse("photo index")

def photo_by_id(request, slug, photo_id):
    return HttpResponse("photo by id")

def photo_votes(request, slug, photo_id):
    return HttpResponse("photo votes")

def photo_comments(request, slug, photo_id):
    return HttpResponse("photo comments")
