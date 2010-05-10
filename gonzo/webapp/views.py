from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def hunt_comments(request, slug):
    return HttpResponse("comments")

def photo_index(request, slug):
    return HttpResponse("photo index")
