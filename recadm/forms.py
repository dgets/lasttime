from django import forms
from django.utils import timezone

class UsageForm(forms.Form):
    sub = forms.ForeignKey('subadd.Substance', on_delete=models.CASCADE)
    dosage = forms.IntegerField()
    #not completely sure, but I don't think this is needed for the form, it
    #should just be the model, I think
    #timestamp = forms.DataTimeField('time administered', default=timezone.now)
    notes = forms.CharField(max_length=160)

