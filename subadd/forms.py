from django.db import models
from django.forms import ModelForm

import lasttime.myglobals

# dosage & duration choices are now provided via an Enum in the main project
# level home (myglobals.py)


class Substance(models.Model):
    """
    Class holds the details for each particular substance added to the
    available druggies database.

    TODO: add the ability to pick between the appropriate dosage Enums
    """

    DOSAGE_UNIT_CHOICE = (
        (lasttime.myglobals.Units.mcg, 'mcg'),
        (lasttime.myglobals.Units.mg, 'mg'),
        (lasttime.myglobals.Units.ml, 'ml'),
        (lasttime.myglobals.Units.floz, 'fl oz'),
        (lasttime.myglobals.Units.tsp, 'tsp'),
    )

    common_name = models.CharField(max_length=40)
    sci_name = models.CharField(max_length=60)
    half_life = models.DecimalField(max_digits=7, decimal_places=3)
    active_half_life = models.DecimalField(max_digits=7, decimal_places=3)
    lipid_solubility = models.BooleanField(default=False)
    units = models.CharField(choices=DOSAGE_UNIT_CHOICE, default=lasttime.myglobals.Units.mg, max_length=5)

    def __str__(self):
        return self.common_name + " (" + self.sci_name + ")"


class SubstanceForm(ModelForm):
    """
    Derived from the substance class, this holds the fields that need to be
    filled out by the user in order to record a new substance's relevant
    characteristics for later administration records.
    """

    class Meta:
        model = Substance
        fields = ['common_name', 'sci_name', 'half_life', 'active_half_life', 'lipid_solubility', 'units']


