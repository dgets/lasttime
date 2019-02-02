from django import forms
from django.db import models
from django.utils import timezone
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User

from subadd.forms import Substance


class Usage(models.Model):
    """
    Model holds the information relevant to each particular substance's
    administration.
    """

    sub = models.ForeignKey('subadd.Substance', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=6)
    dosage = models.DecimalField(max_digits=7, decimal_places=3)
    timestamp = models.DateTimeField('time administered', default=timezone.now)
    notes = models.CharField(max_length=512)

    def __str__(self):
        return str(self.sub) + " (" + str(self.dosage) + ") administered to: " + self.user.username + \
               " at " + str(self.timestamp)


class UsageForm(ModelForm):
    """
    Form is (clearly) derived from the Usage class, above; holds the fields
    necessary to be filled out by hand for the administration record.

    TODO: Find out how to append or prepend the dosage units to the dosage form
    """

    class Meta:
        model = Usage
        fields = ['sub', 'dosage', 'timestamp', 'notes']
        labels = {
            'sub': 'Substance',
            'dosage': 'Dosage in [what?]'
        }
        widgets = {
            'notes': Textarea(attrs={'cols': 60, 'rows': 9})
        }

