from django.contrib import admin

from .forms import Substance, SubstanceClass
from .models import DosageUnit

# Register your models here.

admin.site.register(Substance)
admin.site.register(DosageUnit)
admin.site.register(SubstanceClass)
