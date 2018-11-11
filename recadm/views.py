from django.shortcuts import render
from django.http import HttpResponse

#from .models import Usage
from .forms import Usage, UsageForm

from subadd.forms import Substance

# Create your views here.


def index(request):
    recent_administrations = Usage.objects.all()
    substances = Substance.objects.all()
    mydata = [ ] #this can no doubt be handled better via the db

    for administration in recent_administrations:
        #we only need admin timestamp, dosage, and substance name
        mydata.append({'ts': administration.timestamp,
            'id': administration.id,
            'dosage': administration.dosage,
            'substance_name': administration.sub,})  # .get(pk=administration.sub),})

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

    add_administration_form = UsageForm()

    for sub in substances:
        mydata.append({'name': sub.common_name, 'id': sub.id, })

    context = {
        'mydata': mydata,
        'add_admin_form': add_administration_form,
    }

    return render(request, 'recadm/add_entry.html', context)

# def save_admin(request):
#     context = request.POST['context']
#     mydata = context['mydata']
#
#     sub = context['substance']
#     dosage = context['dosage']
#     notes = context['notes']
#
#     administration = Usage({'sub': request.POST['substance'],
#         'dosage': request.POST['dosage'], 'notes': request.POST['notes']})
#
#     try:
#         administration.save()
#     except Exception as e:
#         substances = Substance.objects.all()
#         #mydata = [ ]
#
#         for sub in substances:
#             mydata.append({'name': sub.common_name, 'id': sub.id, })
#
#         error_message = "Unable to save to db: " + str(e) + \
#             "<br>sub: " + sub + " dose: " + dosage + " notes: " + notes
#
#         context = {
#             'mydata': mydata,
#             'administration': administration,
#             'error_message': error_message,
#             'dosage': request.POST['dosage'], #debugging
#         }
#
#         return render(request, 'recadm/add_entry.html', context)
#
#     return render(request, 'recadm/index.html')


def save_admin(request):
    # administration = Usage({'sub': request.POST['sub'],
    #                         'dosage': request.POST['dosage'],
    #                         'notes': request.POST['notes']})

    add_administration_form = UsageForm({'sub': request.POST['sub'],
                                         'dosage': request.POST['dosage'],
                                         'notes': request.POST['notes']})

    try:
        #administration.save()
        add_administration_form.save()
    except Exception as e:
        substances = Substance.objects.all()

        for sub in substances:
            mydata.append({'name': sub.common_name,
                           'id': sub.id,})

            error_message = "Unable to save to db: " + str(e) + "<br>sub: " + sub + " dose: " + dosage + " notes: " +\
                notes

            context = {'mydata': mydata,
                       #'administration', administration,
                       'add_admin_form': add_administration_form,
                       'error_message': error_message,}

            return render(request, 'recadm/add_entry.html', context)

    mydata = []

    recent_administrations = Usage.objects.all()
    for administration in recent_administrations:
        #we only need admin timestamp, dosage, and substance name
        mydata.append({'ts': administration.timestamp,
            'id': administration.id,
            'dosage': administration.dosage,
            'substance_name': administration.sub,})  # .get(pk=administration.sub),})

    context = {
        #'substances': substances,
        #'recent_administrations': recent_administrations,
        'mydata': mydata,
    }

    return render(request, 'recadm/index.html', context)


def detail(request, topic_id):
    admin_details = Usage.objects.get(id=topic_id)

    context = {
        'sub': admin_details.sub,
        'dosage': admin_details.dosage,
        'timestamp': admin_details.timestamp,
        'notes': admin_details.notes,
    }

    return render(request, 'recadm/details.html', context)
