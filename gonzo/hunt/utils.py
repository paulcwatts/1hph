
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
