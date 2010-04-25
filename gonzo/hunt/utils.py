
# Determines the source URI that can be stored in the DB.
def get_source_from_request(request):
    if request.user.is_authenticated():
        return "user:"+str(request.user.id)
    # TODO: Twitter?
    # TODO: Facebook?
    # TODO: Mobile app?
    ip = request.META.get('REMOTE_ADDR')
    if ip:
        return "anon:ipaddr="+str(ip)

# TODO: Make this better.
# For 'user:' urls, get the username and profile url
# For 'twitter:' urls, get the twitter username and twitter profile url
# For 'facebook:' urls, the same
# For 'anon:' urls, the phrase "anonymous"
def get_source_json(uri, via):
    return { 'uri': uri, 'via' : via }
