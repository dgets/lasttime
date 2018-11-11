from django import forms
from django.db import models
from django.utils import timezone
from django.forms import ModelForm

from subadd.forms import Substance

DOSAGE_CHOICES = (
    ('MCG', 'mcg'),
    ('MG', 'mg'),
    ('OZ', 'oz'),
    ('ML', 'ml'),
    ('TSP', 'tsp'),
)


class Usage(models.Model):
    """
    Model holds the information relevant to each particular substance's
    administration
    """
    sub = models.ForeignKey('subadd.Substance', on_delete=models.CASCADE)
    dosage = models.DecimalField(max_digits=7, decimal_places=3)
    timestamp = models.DateTimeField('time administered', default=timezone.now)
    notes = models.CharField(max_length=160)

    def __str__(self):
        return str(self.sub) + " (" + str(self.dosage) + ") administered at " + str(self.timestamp)


class UsageForm(ModelForm):
    """
    Form is (clearly) derived from the Usage class, above; holds the fields
    necessary to be filled out by hand for the administration record
    """
    class Meta:
        model = Usage
        fields = ['sub', 'dosage', 'notes']


