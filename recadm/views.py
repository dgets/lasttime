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
    substances = Substance.objects.all()
    mydata = [ ] #what the hell is different here compared to above w/my
                      #data structure, construction, and access/storing
                      #logic?!?

    for sub in substances:
        mydata.append({'name': sub.common_name, 'id': sub.id, })

    context = {
        'mydata': mydata,
    }

    return render(request, 'recadm/add_entry.html', context)

def save_admin(request):
    administration = Usage({'sub': request.POST['substance'],
        'dosage': request.POST['dosage'], 'notes': request.POST['notes']})

    try:
        administration.save()
    except Exception as e:
        substances = Substance.objects.all()
        mydata = [ ]

        for sub in substances: 
            mydata.append({'name': sub.common_name, 'id': sub.id, })

        error_message = "Unable to save to db: " + str(e)
        context = {
            'mydata': mydata,
            'administration': administration,
            'error_message': error_message,
            'dosage': request.POST['dosage'], #debugging
        }

        return render(request, 'recadm/add_entry.html', context)

    return render(request, 'recadm/index.html')

def detail(request, usage_id):
    return HttpResponse("Soon there will be code doing shit here, also...")

