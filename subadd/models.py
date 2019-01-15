from django.db import models


class DosageUnit(models.Model):
    """
    Contains all of the possible dosing units for the different available
    substances.
    """

    abbreviation = models.CharField("unit abbreviation", max_length=5)
    description = models.CharField("unit description", max_length=20)

    def __str__(self):
        return self.abbreviation
