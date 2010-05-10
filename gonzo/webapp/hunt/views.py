from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse

from gonzo.hunt.models import Hunt,Submission
from gonzo.hunt.forms import *

def current_hunts(request):
    from datetime import datetime
    now = datetime.utcnow()
    return object_list(request,
                       queryset=Hunt.objects.filter(start_time__lte=now, vote_end_time__gt=now),
                       template_name='webapp/hunt_list.html',
                       template_object_name='hunt',
                       extra_context={ 'title': 'Current hunts',
                            'show_all': True
                       })

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
    hunt = get_object_or_404(Hunt,slug=slug)
    return object_list(request,
                       queryset=hunt.submission_set.filter(is_removed=False),
                       template_name='webapp/hunt_submission_list.html',
                       template_object_name='submission',
                       extra_context={ 'hunt': hunt })
