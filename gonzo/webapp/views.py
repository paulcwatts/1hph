from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def hunt_comments(request, slug):
    return HttpResponse("comments")

def photo_index(request, slug):
    return HttpResponse("photo index")

def photo_votes(request, slug, photo_id):
    return HttpResponse("photo votes")

def photo_comments(request, slug, photo_id):
    return HttpResponse("photo comments")
