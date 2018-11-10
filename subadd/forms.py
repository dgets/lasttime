from django.db import models
from django.forms import ModelForm

DOSAGE_CHOICES = (
    ('MCG', 'mcg'),
    ('MG', 'mg'),
    ('OZ', 'oz'),
    ('ML', 'ml'),
    ('TSP', 'tsp'),
)

DURATION_CHOICES = (
    ('MIN', 'min'),
    ('HRS', 'hrs'),
    ('DAYS', 'days'),
)


class Substance(models.Model):
    common_name = models.CharField(max_length=40)
    sci_name = models.CharField(max_length=60)
    half_life = models.IntegerField(default=16)
    active_half_life = models.IntegerField(default=24)
    lipid_solubility = models.BooleanField(default=False)    

    def __str__(self):
        return_text = self.common_name + " (" + self.sci_name + \
            "): half-life: " + str(self.half_life) + \
            "; detectable half-life: " + str(self.active_half_life)

        if self.lipid_solubility:
            return_text += " - lipid soluble"

        return return_text

class SubstanceForm(ModelForm):
    class Meta:
        model = Substance
        fields = ['common_name', 'sci_name', 'half_life', 'active_half_life', \
                  'lipid_solubility']


