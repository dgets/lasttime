from django.shortcuts import render
from django.http import HttpResponse

from .models import Substance

# Create your views here.

def index(request):
    all_subs = Substance.objects.all()
    context = {
        'all_subs': all_subs,
    }

    return render(request, 'subadd/index.html', context)

def add(request):
    #context = {
    #    'substance': None,
    #}
    return render(request, 'subadd/add.html', {'substance': None})

def addentry(request):
    #if context['substance'] is None:
    substance = Substance(common_name = request.POST['common_name'],
        sci_name = request.POST['scientific_name'],
        half_life = request.POST['half_life'],
        active_half_life = request.POST['detectable_half_life'],
        lipid_solubility = request.POST.get('fat_soluble', False))
    #are the ints or fat_soluble going to have to be processed diff?
    #else:
    #    substance = context['substance']

    #we'll need to do validation here, of course

    try:
        substance.save()
    except:
        error_message = "Unable to save record to database (unknown reason)!"
        return render(request, 'subadd/addentry.html', substance)

    return render(request, 'subadd/index.html', {'all_subs':
        Substance.objects.all()})

