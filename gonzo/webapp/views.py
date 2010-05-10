from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from gonzo.hunt.models import Hunt,Submission
from gonzo.hunt.forms import *

def hunt_comments(request, slug):
    hunt = get_object_or_404(Hunt,slug=slug)
    return object_list(request,
                       queryset=hunt.comment_set.filter(is_removed=False),
                       template_name='webapp/hunt_comment_list.html',
                       template_object_name='comment',
                       extra_context={ 'comment_form': CommentForm(),
                            'hunt': hunt
                        })

def photo_index(request, slug):
    return HttpResponse("photo index")
