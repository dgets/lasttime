from django.shortcuts import render
from django.http import HttpResponse

from .models import Substance

# Create your views here.

def subadd(request):
    all_subs = Substance.objects.all()
    context = {
        'all_subs': all_subs,
    }

    return render(request, 'subadd/index.html', context)


