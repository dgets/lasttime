from django.db import models
from django import forms
from django.forms import ModelForm

from .models import DosageUnit


class Substance(models.Model):
    """
    Class holds the details for each particular substance added to the
    available druggies database.

    TODO: add the ability to pick between the appropriate dosage Enums
    """

    common_name = models.CharField(max_length=40)
    sci_name = models.CharField(max_length=60)
    sub_class = models.ForeignKey('subadd.SubstanceClass', on_delete=models.CASCADE, default=-1)
    half_life = models.DecimalField(max_digits=7, decimal_places=3)
    active_half_life = models.DecimalField(max_digits=7, decimal_places=3)
    lipid_solubility = models.BooleanField(default=False)
    units = models.CharField(max_length=5)

    def __str__(self):
        # return_text = self.common_name + " (" + self.sci_name + "): half-life: " + str(self.half_life) + \
        #     "; detectable half-life: " + str(self.active_half_life)
        #
        # if self.lipid_solubility:
        #     return_text += " - lipid soluble"
        #
        # return return_text
        return self.common_name + " (" + self.sci_name + ")"


class SubstanceForm(ModelForm):
    """
    Derived from the substance class, this holds the fields that need to be
    filled out by the user in order to record a new substance's relevant
    characteristics for later administration records.
    """

    units = forms.ModelChoiceField(DosageUnit.objects.all(), empty_label="-Dosage Units-", to_field_name="abbreviation")

    class Meta:
        model = Substance
        fields = ['common_name', 'sci_name', 'half_life', 'active_half_life', 'lipid_solubility']


class SubstanceClass(models.Model):
    """
    Class holds the details for substance classes.
    """

    name = models.CharField(max_length=25)
    desc = models.CharField(max_length=160)


class SubstanceClassForm(ModelForm):
    """
    Pretty much goes without saying at this point, don't you agree?
    """

    class Meta:
        model = SubstanceClass
        fields = ['name', 'desc']
