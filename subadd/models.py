from django.db import models
from django.utils import timezone

# Create your models here.

class Substance(models.Model):
    common_name = models.CharField(max_length=40)
    sci_name = models.CharField(max_length=60)
    half_life = models.IntegerField()
    active_half_life = models.IntegerField()
    lipid_solubility = models.BooleanField()    

    def __str__(self):
        return common_name + " (" + sci_name + "): half-life: " + half_life.str() + "; detectable half-life: " + active_half_life.str()

