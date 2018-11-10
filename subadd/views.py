from django.shortcuts import render, get_object_or_404
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
    return render(request, 'subadd/add.html', {'substance': None})


def addentry(request):
    substance = Substance(common_name = request.POST['common_name'],
        sci_name = request.POST['scientific_name'],
        half_life = request.POST['half_life'],
        active_half_life = request.POST['detectable_half_life'],
        lipid_solubility = request.POST.get('fat_soluble', False))

    #we'll need to do validation here, of course

    try:
        substance.save()
    except:
        error_message = "Unable to save record to database (unknown reason)!"
        return render(request, 'subadd/addentry.html', substance)

    return render(request, 'subadd/index.html', {'all_subs':
        Substance.objects.all()})


def detail(request, substance_id):
    try:
        substance = get_object_or_404(Substance, pk=substance_id)
    except Substance.DoesNotExist:
        raise Http404("Substance does not exist :|")

    return render(request, 'subadd/detail.html', {'substance': substance})


