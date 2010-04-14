from django.http import HttpResponse

# This will be provided to the user that deactivates their Facebook account,
# to allow an independent account to be set up.
def account_reclaim(request):
    print "reclaim: " + str(request)
    return HttpResponse("reclaim")

# Facebook pings this URL when a user first authorizes the application
def post_authorize(request):
    #print request.facebook.uid
    # create a user profile for this facebook user in our system.
    return HttpResponse("post_authorize")

# Facebook pings this URL when a user removes the application
def post_remove(request):
    # TODO: If it is a "auto-created" user, then delete the user.
    # TODO: Otherwise, we need to treat this as a reclamation
    print "post_remove: " + str(request)
    return HttpResponse("post_authorize")
