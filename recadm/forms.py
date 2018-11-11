from django import forms
from django.db import models
from django.utils import timezone
from django.forms import ModelForm

from subadd.forms import Substance


class Usage(models.Model):
    sub = models.ForeignKey('subadd.Substance', on_delete=models.CASCADE)
    dosage = models.IntegerField()
    timestamp = models.DateTimeField('time administered', default=timezone.now)
    notes = models.CharField(max_length=160)

    def __str__(self):
        return str(self.sub) + " (" + str(self.dosage) + ") administered at " + str(self.timestamp)


class UsageForm(ModelForm):
    class Meta:
        model = Usage
        fields = ['sub', 'dosage', 'notes']


