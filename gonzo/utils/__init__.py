import re
import unicodedata
from htmlentitydefs import name2codepoint
from StringIO import StringIO

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    def smart_unicode(s):
        return s

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

# From http://www.djangosnippets.org/snippets/369/
def slugify(klass, s, exclude_pk=None, entities=True, decimal=True, hexadecimal=True,
   slug_field='slug', filter_dict=None):
    s = smart_unicode(s)
    #character entity reference
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)
    #decimal character reference
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass
    #hexadecimal character reference
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);', lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass
    #translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    #replace unwanted characters
    s = re.sub(r'[^-a-z0-9]+', '-', s.lower())
    #remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')
    slug = s
    def get_query():
        query = klass.objects.filter(**{slug_field: slug})
        if filter_dict:
            query = query.filter(**filter_dict)
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return query
    counter = 1
    while get_query():
        slug = "%s-%s" % (s, counter)
        counter += 1
    return slug


def assign_image_to_model(instance, field_name, file, name=None, content_type=None):
    """Makes assigning an image to a model field less of a PITA."""
    # Pumping it through a form seems to be the easiest way
    class MyForm(forms.Form):
        image = forms.ImageField()

    frm = MyForm(files={ 'image':
         SimpleUploadedFile(name=name,
                            content=file.read(),
                              content_type=content_type)
    })
    frm.full_clean()
    if not frm.is_valid():
        return False
    setattr(instance, field_name, frm.cleaned_data['image'])
    return True

