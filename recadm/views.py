from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime
from pytz import timezone

from lasttime.myglobals import MiscMethods, Const

from subadd.forms import Substance
from .forms import Usage, UsageForm, UsualSuspect, UsualSuspectForm


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

    recent_administrations = Usage.objects.filter(user=request.user).order_by('sub', '-timestamp')
    paginator = Paginator(recent_administrations, 15)   # 15 admins per page

    page = request.GET.get('page')
    administrations = paginator.get_page(page)

    mydata = []
    local_dt = None
    for administration in administrations:  # recent_administrations:
        # localize timestamp?
        if MiscMethods.is_localization_needed(administration.timestamp):
            local_dt = MiscMethods.localize_timestamp(administration.timestamp)
        else:
            local_dt = administration.timestamp

        mydata.append({'ts': local_dt,
                       'id': administration.id,
                       'dosage': administration.dosage,
                       'units': administration.sub.units,
                       'substance_name': administration.sub,})

    context = {'mydata': mydata, 'user': request.user, 'administrations': administrations,}

    return render(request, 'recadm/index.html',
                  MiscMethods.add_pagination_info(MiscMethods.add_header_info(context), administrations))


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

    return render(request, 'recadm/add_entry.html', MiscMethods.add_header_info(context))


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
        # localize the timestamp
        central_tz = timezone(Const.Time_Zone)
        timestamp = central_tz.localize(datetime.strptime(request.POST['timestamp'], '%Y-%m-%d %H:%M:%S'))
        print(str(timestamp))
        new_administration = Usage(sub=Substance.objects.get(id=request.POST['sub']), user=request.user,
                                   dosage=request.POST['dosage'], timestamp=timestamp,
                                   notes=request.POST['notes'])

        try:
            new_administration.save()
        except Exception as e:
            error_message = "Unable to save to db: " + str(e) + "admin: " + str(new_administration)

            context = {'add_admin_form': add_administration_form,
                       'error_message': error_message,}

            return render(request, 'recadm/add_entry.html', MiscMethods.add_header_info(context))

    # code for the successful save of the record and return to the index
    # follows here
    mydata = []

    recent_administrations = Usage.objects.filter(user=request.user).order_by('-timestamp')
    paginator = Paginator(recent_administrations, 15)  # 15 admins per page

    page = request.GET.get('page')
    administrations = paginator.get_page(page)

    tmp_dt = None
    for administration in administrations:
        # localization needed?
        if MiscMethods.is_localization_needed(administration.timestamp):
            tmp_dt = MiscMethods.localize_timestamp(administration.timestamp)
        else:
            tmp_dt = administration.timestamp

        mydata.append({'ts': tmp_dt,
                       'id': administration.id,
                       'dosage': administration.dosage,
                       'substance_name': administration.sub,})

    context = {'mydata': mydata, 'administrations': administrations,}

    return render(request, 'recadm/index.html', MiscMethods.add_header_info(context))


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

    try:
        admin_details = Usage.objects.get(id=topic_id, user=request.user)
    except Usage.DoesNotExist:
        return render(request, 'recadm/details.html',
                      MiscMethods.add_header_info({'error_message':
                                                   "The Usage records you requested do not seem to exist...",}))

    # localization needed?
    if MiscMethods.is_localization_needed(admin_details.timestamp):
        tmp_dt = MiscMethods.localize_timestamp(admin_details.timestamp)
    else:
        tmp_dt = admin_details.timestamp

    context = {
        'sub': admin_details.sub,
        'dosage': admin_details.dosage,
        'units': admin_details.sub.units,
        'timestamp': tmp_dt,
        'notes': admin_details.notes,
        'admin_id': admin_details.id,
    }

    return render(request, 'recadm/details.html', MiscMethods.add_header_info(context))


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

            return render(request, 'recadm/edit_admin.html', MiscMethods.add_header_info(context))

        return render(request, 'recadm/edit_admin.html', MiscMethods.add_header_info(context))

    new_admin_deets = Usage.objects.get(id=admin_id, user=request.user)
    new_admin_deets.sub = Substance.objects.get(id=request.POST['sub'])
    new_admin_deets.dosage = request.POST['dosage']
    new_admin_deets.timestamp = MiscMethods.str_to_datetime(request.POST['timestamp'])
    new_admin_deets.notes = request.POST['notes']

    # localize?
    if MiscMethods.is_localization_needed(new_admin_deets.timestamp):
        new_admin_deets.timestamp = MiscMethods.localize_timestamp(new_admin_deets.timestamp)

    try:
        new_admin_deets.save()
    except Exception as ex:
        context['error_message'] = "Unable to save new administration details: " + str(ex)
        context['admin_form'] = UsageForm(instance=new_admin_deets)

        return render(request, 'recadm/edit_admin.html', MiscMethods.add_header_info(context))

    # again, this is another one waiting for the global user/error message
    # displaying code, but in another area
    context['user_message'] = "Saved new administration details."
    context['admin_form'] = UsageForm(instance=new_admin_deets)

    # return render(request, 'recadm/edit_admin.html', MiscMethods.add_header_info(context))
    # so below here...  this really isn't the way to be doing this, with an absolute URL/path, but the other ways
    # weren't working, and this one was, so I took the easy out...  :P
    return redirect('/recadm/', context=MiscMethods.add_header_info(context))


@login_required
def add_usual_suspect(request):
    """
    Provides capability for adding a usual suspect to the database.

    :param request:
    :return:
    """

    if request.method != 'POST':
        # display the form and get what we need for a new US entry
        # add_usual_suspect_form = UsualSuspectForm()

        return render(request, 'recadm/add_usual_suspect.html', MiscMethods.add_header_info({'add_usual_suspect_form':
                                                                                             UsualSuspectForm(),}))

    # else:
        # validate (if necessary) and save the form contents
