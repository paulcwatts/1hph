"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from gonzo import phrase

class PhraseTest(TestCase):
    def test_format_phrase(self):
        def replacer(text):
            self.assertEquals(text, "%xxx%")
            return 'FOO'

        TESTS=(
            ("",                    "",                 ""),
            ("%xxx%",               "FOO",              "FOO"),
            ("begin%xxx%",          "beginFOO",         "FOO"),
            ("front %xxx% back",    "front FOO back",   "FOO"),
            ("%xxx% end",           "FOO end",          "FOO"),
            ("%xxx% MID %xxx%",     "FOO MID FOO",      "FOOFOO"),
            ("%xxx%%xxx%%xxx%",     "FOOFOOFOO",        "FOOFOO"),
            ("no replace here",     "no replace here",  "noreplace")
        )
        for t in TESTS:
            (result,tag) = phrase.format(t[0], replacer)
            self.assertEquals(result, t[1])
            self.assertEquals(tag, t[2])

        # We can test a few basic cases with the default replacer
        (result,tag) = phrase.format("")
        self.assertEquals(result, "")
        self.assertEquals(tag, "")

        (result,tag) = phrase.format("%%")
        self.assertEquals(result, "%")
        self.assertEquals(tag, "%")

        self.assertRaises(ValueError, lambda: phrase.format("%fail%"))

    def test_new_phrase(self):
        new = phrase.new_phrase()
        self.assert_(new)
        self.assertEquals(len(new),2)

__test__ = {}

