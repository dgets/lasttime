from django.db import models
from django.utils import timezone

from .models import Substance

# Create your models here.

class Usage(models.Model):
    sub = models.ForeignKey(Substance)
    dosage = models.IntegerField()
    timestamp = models.DateTimeField('time administered', default=timezone.now)
    notes = models.CharField(max_length=160)


