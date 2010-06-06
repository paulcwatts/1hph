from django.db import models

class Adjective1(models.Model):
    value = models.CharField(max_length=64,primary_key=True)
    def __unicode__(self):
        return self.value

class Adjective2(models.Model):
    value = models.CharField(max_length=64,primary_key=True)
    def __unicode__(self):
        return self.value

class Noun1(models.Model):
    value = models.CharField(max_length=64,primary_key=True)
    def __unicode__(self):
        return self.value

class Phrase(models.Model):
    """
    The 'value' is a format that defines particular phrase.
    The variables correspond to the model from which to pull
    the replacement phrase:
        %noun1%
        %adjective1%
        %adjective2%

    The weight specifies the how often these phrases should appear.
    A weight of 2 will appear twice as often as a weight of 1.
    """
    value = models.CharField(max_length=64,primary_key=True)
    weight = models.IntegerField(default=1)

    def __unicode__(self):
        return self.weight + ':' + self.value
