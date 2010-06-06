import random,re

from gonzo.phrase.models import *

def phrase_choices():
    result = []
    for phrase in Phrase.objects.all():
        result.extend([phrase.value]*phrase.weight)
    return result

RE=re.compile("%\w*?%")

REPLACEMENTS={
    '%adjective1%': Adjective1,
    '%adjective2%': Adjective2,
    '%noun1%': Noun1,
    '%%': '%'
    #'phrase': Theoretically
}

def random_replace(fmt):
    t = REPLACEMENTS.get(fmt)
    if type(t) == str:
        return t
    elif t is not None:
        return random.choice(t.objects.all()).value
    else:
        raise ValueError("Unknown formatting code: " + fmt)

def format(phrase, replacer=random_replace):
    result = ''
    lastend = 0
    # The tag will be the first two replaced phrases contatenated
    replacements=[]

    for m in RE.finditer(phrase):
        result += (phrase[lastend:m.start()])
        r = replacer(m.group())
        replacements.append(r)
        result += r
        lastend = m.end()

    result += phrase[lastend:]

    # if there are no replacements, then what is it?
    if replacements:
        tag = ''.join(replacements[:2])
    else:
        # If there are no replacements, then I suppose we can just
        # choose the first two words
        tag = ''.join(result.split()[:2])

    return (result,tag)


def new_phrase():
    """Returns a tuple: (phrase,tag)"""
    return format(random.choice(phrase_choices()))
