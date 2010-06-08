import email, time, urllib
from datetime import datetime, timedelta
from cStringIO import StringIO

from django.contrib.auth.models import User

from gonzo.hunt.models import Hunt,Submission
from gonzo.utils import assign_image_to_model

class InvalidAddress(Exception):
    pass

class HuntDoesNotExist(Hunt.DoesNotExist):
    pass

class HuntNotCurrent(Exception):
    pass

class NoImage(Exception):
    pass

def submit_from_file(environ, fp):
    return submit_message(environ, email.message_from_file(fp))

#def submit_from_string(environ, s):
#    return submit(environ, email.message_from_string(s))

def submit_message(environ, message):
    if not message.is_multipart():
        raise NoImage()

    email_to = environ.get('RECIPIENT')
    email_from = message.get('from', environ.get('SENDER'))
    if not email_to:
        raise InvalidAddress("Missing recipient")

    # For the time being, ignore the actual 'to' and focus on the
    # local extension
    try:
        (realname,addr) = email.utils.parseaddr(email_to)
        (user,local) = addr.split('@')[0].split('+')
    except ValueError:
        raise InvalidAddress("Invalid hunt address: " + email_to)

    try:
        hunt = Hunt.objects.get(tag=local)
    except Hunt.DoesNotExist:
        raise HuntDoesNotExist()

    date = email.utils.parsedate_tz(message.get('date'))
    if not date:
        date = datetime.utcnow()
    else:
        offset = date[9]
        date = datetime(*date[:6]) - timedelta(seconds=offset)

    if date < hunt.start_time:
        raise HuntNotCurrent("Hunt hasn't started yet")
    if date >= hunt.end_time:
        raise HuntNotCurrent("Hunt has ended")

    submission = Submission(hunt=hunt,
                            time=date,
                            via='email',
                            ip_address=environ.get('CLIENT_ADDRESS',''))
    # photo
    # description?
    # user
    # anon_source

    # Find the image by walking the payload
    for part in message.walk():
        if part.get_content_maintype() == 'image' and not part.is_multipart():
            image_data = part.get_payload(decode=True)
            assign_image_to_model(submission,
                                  'photo',
                                  StringIO(image_data),
                                  part.get_filename(addr+"."+part.get_content_subtype()),
                                  part.get_content_type())
            break

    if not submission.photo:
        raise NoImage()

    # Get the sender and see if it's a user
    (realname,addr) = email.utils.parseaddr(email_from)
    try:
        user = User.objects.get(email=addr)
        submission.user = user
    except User.DoesNotExist:
        # Override the addr with what we get from postfix
        addr = environ.get('SENDER', addr)
        submission.anon_source = 'email:'+urllib.urlencode({'name':realname, 'addr':addr})

    submission.submit()
    return submission
