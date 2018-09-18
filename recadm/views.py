from django.shortcuts import render
from django.http import HttpResponse

from .models import Usage
from subadd.models import Substance

# Create your views here.

def index(request):
    recent_administrations = Usage.objects.all()
    substances = Substance.objects.all()
    mydata = [ ] #this can no doubt be handled better via the db

    for administration in recent_administrations:
        #we only need admin timestamp, dosage, and substance name
        mydata.add({'ts': administration.timestamp,
            'id': administration.id,
            'dosage': administration.dosage,
            'substance_name': substances.object.get(pk=administration.sub),})

    context = {
        #'substances': substances,
        #'recent_administrations': recent_administrations,
        'mydata': mydata,
    }

    return render(request, 'recadm/index.html', context)

def add(request):
    return HttpResponse("Soon there will be shit here...")

def add_new(request):
    return HttpResponse("AhDittoThayat")

def detail(request, usage_id):
    return HttpResponse("Soon there will be code doing shit here, also...")

