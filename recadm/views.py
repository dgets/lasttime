from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import Usage, UsageForm

from lasttime.myglobals import MiscMethods

from home.models import HeaderInfo, NavInfo
from subadd.forms import Substance


@login_required
def index(request):
    """
    View shows the details of administrations; it will, at some point,
    obviously have to be chopped down for a reasonable subset of the
    list, but it's good for testing purposes.  Passes the view off via
    the recadm/index template.

    :param request:
    :return:
    """

    recent_administrations = Usage.objects.filter(user=request.user).order_by('-timestamp')
    paginator = Paginator(recent_administrations, 15)   # 15 admins per page

    page = request.GET.get('page')
    administrations = paginator.get_page(page)

    mydata = []
    for administration in administrations:  # recent_administrations:
        mydata.append({'ts': administration.timestamp,
                       'id': administration.id,
                       'dosage': administration.dosage,
                       'units': administration.sub.units,
                       'substance_name': administration.sub,})

    context = {'mydata': mydata, 'user': request.user, 'administrations': administrations,}

    return render(request, 'recadm/index.html',
                  MiscMethods.add_pagination_info(add_header_info(context), administrations))


@login_required
def add(request):
    """
    View for adding a particular administration record.  Passes the view off
    to the add_entry template.

    :param request:
    :return:
    """

    substances = Substance.objects.all()
    mydata = []

    add_administration_form = UsageForm()

    for sub in substances:
        mydata.append({'name': sub.common_name, 'id': sub.id, })

    context = {
        'mydata': mydata,
        'add_admin_form': add_administration_form,
    }

    return render(request, 'recadm/add_entry.html', add_header_info(context))


@login_required
def save_admin(request):
    """
    View is called when add_entry is submitted and passes the data off here in
    order to save it to the database.  It returns the viewer back to the index
    template, in order to see the results of the database addition at the top
    of the administration records.

    :param request:
    :return:
    """

    if request.method == "POST":
        add_administration_form = UsageForm({'sub': request.POST['sub'],
                                             'dosage': request.POST['dosage'],
                                             'timestamp': request.POST['timestamp'],
                                             'notes': request.POST['notes']})
        new_administration = Usage(sub=Substance.objects.get(id=request.POST['sub']), user=request.user,
                                   dosage=request.POST['dosage'], timestamp=request.POST['timestamp'],
                                   notes=request.POST['notes'])

        try:
            new_administration.save()
        except Exception as e:
            error_message = "Unable to save to db: " + str(e) + "admin: " + str(new_administration)

            context = {'add_admin_form': add_administration_form,
                       'error_message': error_message,}

            return render(request, 'recadm/add_entry.html', add_header_info(context))

    # code for the successful save of the record and return to the index
    # follows here
    mydata = []

    recent_administrations = Usage.objects.filter(user=request.user).order_by('-timestamp')
    paginator = Paginator(recent_administrations, 15)  # 15 admins per page

    page = request.GET.get('page')
    administrations = paginator.get_page(page)

    for administration in administrations:
        mydata.append({'ts': administration.timestamp,
                       'id': administration.id,
                       'dosage': administration.dosage,
                       'substance_name': administration.sub,})

    context = {'mydata': mydata, 'administrations': administrations,}

    return render(request, 'recadm/index.html', add_header_info(context))


@login_required
def detail(request, topic_id):
    """
    Provides the details on any particular administration's notes, primarily
    (or maybe solely) linked via the index page's summary of different
    administration details.

    :param request:
    :param topic_id:
    :return:
    """

    admin_details = Usage.objects.get(id=topic_id, user=request.user)

    context = {
        'sub': admin_details.sub,
        'dosage': admin_details.dosage,
        'units': admin_details.sub.units,
        'timestamp': admin_details.timestamp,
        'notes': admin_details.notes,
        'admin_id': admin_details.id,
    }

    return render(request, 'recadm/details.html', add_header_info(context))


@login_required
def edit(request, admin_id):
    """
    Provides the capability to edit an existing administration.

    :param request:
    :param admin_id:
    :return:
    """

    context = {
        'id': admin_id,
    }

    if request.method != "POST":
        # give 'em the form
        try:
            admin_details = Usage.objects.get(id=admin_id, user=request.user)
            context['admin_form'] = UsageForm(instance=admin_details)
            
        except Exception as ex:
            context['error_message'] = "Invalid administration record request: " + str(ex)
            # here we should really be throwing things back to the detail view,
            # but with an error message explaining what happened; waiting until
            # global error message handling is completed before doing this,
            # however

            return render(request, 'recadm/edit_admin.html', add_header_info(context))

        # context['admin_form'] = UsageForm({
        #     'sub': admin_details['sub'], 'dosage': admin_details['dosage'],
        #     'timestamp': admin_details['timestamp'], 'notes': admin_details['notes'], 'user': request.user,
        # })

        return render(request, 'recadm/edit_admin.html', add_header_info(context))

    # save the results
    # new_admin_deets = Usage(sub=Substance.objects.get(id=request.POST['sub']), dosage=request.POST['dosage'],
    #                         timestamp=request.POST['timestamp'], notes=request.POST['notes'], user=request.user)
    new_admin_deets = Usage.objects.get(id=admin_id, user=request.user)
    new_admin_deets.sub = Substance.objects.get(id=request.POST['sub'])
    new_admin_deets.dosage = request.POST['dosage']
    new_admin_deets.timestamp = request.POST['timestamp']
    new_admin_deets.notes = request.POST['notes']

    try:
        new_admin_deets.save()
    except Exception as ex:
        context['error_message'] = "Unable to save new administration details: " + str(ex)
        context['admin_form'] = UsageForm(instance=new_admin_deets)

        return render(request, 'recadm/edit_admin.html', add_header_info(context))

    # again, this is another one waiting for the global user/error message
    # displaying code, but in another area
    context['user_message'] = "Saved new administration details."
    context['admin_form'] = UsageForm(instance=new_admin_deets)

    return render(request, 'recadm/edit_admin.html', add_header_info(context))


def add_header_info(page_data):
    """
    Method takes whatever (presumably context) dict that is passed to it and
    adds the 'NavInfo' and 'HeaderInfo' keys to it, pointing to the
    applicable data for the header & footer schitt.

    :param previous_context:
    :return: new context (dict)
    """

    page_data['header_info'] = HeaderInfo.objects.first()
    page_data['links'] = NavInfo.objects.all()

    return page_data
