from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
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
    usual_suspects = UsualSuspect.objects.all()

    mydata = []

    add_administration_form = UsageForm()

    for sub in substances:
        mydata.append({'name': sub.common_name, 'id': sub.id,})

    context = {
        'mydata': mydata,
        'timestamp': "YYYY-mm-dd HH:MM:SS",
        # 'timestamp': datetime.now(),  # the other option
        'usual_suspects': usual_suspects,
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

    else:
        context = {}
        # validate (if necessary) and save the form contents
        new_us = UsualSuspect()

        new_us.name = request.POST['name']
        new_us.sub_id = Substance.objects.get(id=request.POST['sub_id'])
        new_us.dosage = request.POST['dosage']
        new_us.notes = request.POST['notes']

        try:
            new_us.save()
        except Exception as ex:
            context['error_message'] = "Unable to save new usual suspect: " + str(ex)
            context['add_usual_suspect_form'] = UsualSuspectForm(instance=new_us)

            return render(request, 'recadm/add_usual_suspect.html', MiscMethods.add_header_info(context))

        context['user_message'] = "Saved new usual suspect."

        return redirect('/recadm/')


@login_required
def save_usual_suspect_admin(request):
    """
    Saves the administration of a usual_suspect from the 'add' view above.

    :param request:
    :return:
    """

    context = {}

    if request.method != 'POST':
        # we have some sort of funky error here
        context['error_message'] = "We had some sort of funky error here."

    else:
        us = UsualSuspect.objects.get(id=request.POST['us_value'])

        # save our administration here
        new_usage = Usage()
        new_usage.user = request.user
        new_usage.sub = us.sub_id
        new_usage.dosage = us.dosage
        new_usage.notes = us.notes
        if request.POST['timestamp'] == "" or request.POST['timestamp'] == "YYYY-mm-dd HH:MM:SS":
            new_usage.timestamp = datetime.now()
        else:
            new_usage.timestamp = datetime.strptime(request.POST['timestamp'], '%Y-%m-%d %H:%M:%S')

        try:
            new_usage.save()

            context['user_message'] = "Saved usual suspect administration."
        except Exception as e:
            context['error_message'] = "Houston, we have a friggin' problem: " + str(e)

    return render(request, 'recadm/usual_suspect_admin_added.html', MiscMethods.add_header_info(context))


@login_required
def delete_admin(request):
    """
    Provides capability for deleting an administration (or several).

    :param request:
    :return:
    """

    context = {}

    if request.method != 'POST':
        # display the administrations available for deletion
        context['admins'] = Usage.objects.filter(user=request.user)

    elif 'admin_checks' in request.POST:
        # confirm and delete the checked administrations
        # first build a set of the administrations
        # admins = []
        context['selected_admins'] = []
        context['selected_admin_ids'] = []
        for admin in request.POST.getlist('admin_checks'):
            tmp_usage = Usage.objects.get(id=admin)
            context['selected_admins'].append(str(tmp_usage))
            context['selected_admin_ids'].append(tmp_usage.id)

    elif 'delete_confirmed' in request.POST:
        # now we will go ahead and wipe what has been confirmed for deletion
        # for use_id in context['selected_admin_ids']:
        for use_id in request.POST.getlist('selected_admin_ids'):
            print("Deleting administration: " + use_id)
            Usage.objects.filter(id=use_id).delete()

        context['user_message'] = "Administrations deleted!"
        context['admins'] = Usage.objects.filter(user=request.user)

    else:
        # whayit
        context['error_message'] = "Whayit?"

    return render(request, 'recadm/delete_admin.html', MiscMethods.add_header_info(context))


@login_required
def prune_database_by_date(request):
    """
    Provides capability for deleting the administrations from the database that
    are older than a specified date/time.  Only for the current user, of
    course.

    :param request:
    :return:
    """

    context = {}

    if request.method != 'POST':
        context['all_subs'] = Substance.objects.all()

    elif 'need_verification' in request.POST:
        # context['all_subs'] = Substance.objects.all()

        try:
            prune_prior_to_date = datetime.strptime(request.POST['prune_prior_to_date'], '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            context['error_message'] = "Could not parse date: " + str(e)
            return render(request, 'recadm/prune_database_by_date.html', MiscMethods.add_header_info(context))

        admins = Usage.objects.filter(
            user=request.user, sub=request.POST['sub_to_prune'], timestamp__lte=prune_prior_to_date).\
            order_by('-timestamp')

        paginator = Paginator(admins, 15)  # 15 admins per page

        page = request.GET.get('page')
        administrations = paginator.get_page(page)

        context['administrations'] = administrations
        context['need_verification'] = True
        context['user_message'] = "Please verify pruning the database prior to " + request.POST['prune_prior_to_date'] \
            + ", as this is irreversible!"
        context['prune_prior_to_date'] = str(prune_prior_to_date)
        context['sub_to_prune'] = request.POST['sub_to_prune']

        return render(request, 'recadm/prune_database_by_date.html',
                      MiscMethods.add_pagination_info(MiscMethods.add_header_info(context), administrations))

    elif 'verified' in request.POST:
        prune_prior_to_date = datetime.strptime(request.POST['prune_prior_to_date'], '%Y-%m-%d %H:%M:%S')

        usages = Usage.objects.filter(
            user=request.user, sub=request.POST['sub_to_prune'], timestamp__lte=prune_prior_to_date).delete()

        context['user_message'] = str(len(usages)) + " entries prior to " + request.POST['prune_prior_to_date'] + \
            " have been deleted."
        context['verified'] = True

    else:
        context['all_subs'] = Substance.objects.all()
        context['error_message'] = "You did not verify deleting the database entries for pruning!"

    return render(request, 'recadm/prune_database_by_date.html', MiscMethods.add_header_info(context))


@login_required
def consolidate_database(request):
    """
    Provides the capability for consolidating entries within a specified time-
    span into single entries, in order to keep the number of entries to a more
    reasonable number and avoid too many duplicated records within short
    intervals.

    :param request:
    :return:
    """

    consolidation_debugging = True
    context = {}
    wiped_entries = []
    new_entries = []

    if request.method != 'POST':
        # initial landing page; still need to select substance and interval
        context['all_subs'] = Substance.objects.all()
        context['mins'] = range(0, 60)
        context['hrs'] = range(0, 24)

    else:
        # validate the selection

        max_delta = timedelta(seconds=int(request.POST['hours']) * 60**2 + int(request.POST['minutes']) * 60)
        applicable_usages = Usage.objects.filter(
            user=request.user, sub=request.POST['sub_to_consolidate'], valid_entry=True).order_by('-timestamp')

        for cntr in range(0, len(applicable_usages)):
            if cntr > 0 and cntr < len(applicable_usages) - 1:
                # here we're going to have to test for both cases and the tertiary case of consolidating 3 entries

                if (applicable_usages[cntr - 1].timestamp - applicable_usages[cntr + 1].timestamp) <= max_delta * 2:
                    # consolidate the three
                    new_usage = Usage()

                    new_usage.user = applicable_usages[cntr - 1].user
                    new_usage.sub = applicable_usages[cntr - 1].sub
                    new_usage.dosage = (applicable_usages[cntr - 1].dosage + applicable_usages[cntr].dosage +
                                        applicable_usages[cntr + 1].dosage)

                    # tmp_offset = applicable_usages[cntr - 1].timestamp - applicable_usages[cntr + 1].timestamp
                    new_usage.timestamp = applicable_usages[cntr].timestamp

                    new_usage.notes = "Consolidated entry"  # should be compiled from the previous usages' notes & a
                                                            # note regarding the consolidation
                    new_usage.valid_entry = True

                    if consolidation_debugging:
                        # print what we'd do
                        print("\nCondition 1:\nSaving: " + str(new_usage))
                        print("Marking invalid: " + str(applicable_usages[cntr - 1]) + "\n" +
                              str(applicable_usages[cntr]) + "\n" + str(applicable_usages[cntr + 1]))
                    else:
                        mark_invalid(applicable_usages[cntr - 1], applicable_usages[cntr], applicable_usages[cntr + 1])

                        new_usage.save()

                    wiped_entries.append(applicable_usages[cntr - 1])
                    wiped_entries.append(applicable_usages[cntr])
                    wiped_entries.append(applicable_usages[cntr - 1])

                    new_entries.append(new_usage)

                    cntr += 1

                elif (applicable_usages[cntr].timestamp - applicable_usages[cntr + 1].timestamp) <= max_delta:
                    # CHECK IF DEBUGGING AND DON'T SAVE CHANGES IF SO
                    if consolidation_debugging:
                        print("\nCondition 1b:\nSaving: " + str(new_usage))
                        print("Marking invalid: " + str(applicable_usages[cntr]) + "\n" +
                              str(applicable_usages[cntr + 1]))
                    else:
                        new_usage = consolidate_two(applicable_usages[cntr], applicable_usages[cntr + 1])

                        mark_invalid(applicable_usages[cntr], applicable_usages[cntr + 1], None)
                        new_usage.save()

                    wiped_entries.append(applicable_usages[cntr])
                    wiped_entries.append(applicable_usages[cntr + 1])

                    new_entries.append(new_usage)

                    cntr += 1

                else:
                    if consolidation_debugging:
                        print("Nothing to consolidate here")

            elif cntr == 0:
                # check the two and consolidate if necessary
                if applicable_usages[cntr].timestamp - applicable_usages[cntr + 1].timestamp <= max_delta:
                    new_usage = consolidate_two(applicable_usages[cntr], applicable_usages[cntr + 1])

                    if consolidation_debugging:
                        print("\nCondition 3:\nSaving: " + str(new_usage))
                        print("Marking invalid: " + str(applicable_usages[cntr]) + "\n" +
                              str(applicable_usages[cntr + 1]))
                    else:
                        mark_invalid(applicable_usages[cntr], applicable_usages[cntr + 1], None)
                        new_usage.save()

                    wiped_entries.append(applicable_usages[cntr])
                    wiped_entries.append(applicable_usages[cntr + 1])

                    new_entries.append(new_usage)

                    cntr += 1

            else:
                # no idea wtf happened here
                print("\nSomething unexpected happened here!")

        if consolidation_debugging:
            print("\nWiped: " + str(wiped_entries))
            print("New: " + str(new_entries))

        context['wiped_entries'] = wiped_entries
        context['new_entries'] = new_entries

    return render(request, 'recadm/consolidate_database.html', MiscMethods.add_header_info(context))


def consolidate_two(first_usage, second_usage):
    """
    Method creates a new usage based on the applicable fields being averaged
    from the two passed Usages and returns it.

    :param first_usage:
    :param second_usage:
    :return:
    """

    consolidation_debugging = True

    new_usage = Usage()

    new_usage.user = first_usage.user
    new_usage.sub = first_usage.sub
    new_usage.dosage = (first_usage.dosage + second_usage.dosage)
    tmp_offset = first_usage.timestamp - second_usage.timestamp
    new_usage.timestamp = second_usage.timestamp + (tmp_offset / 2)

    if consolidation_debugging:
        print("\nTS1: " + str(first_usage.timestamp))
        print("TS2: " + str(second_usage.timestamp))
        print("New TS: " + str(new_usage.timestamp))

    new_usage.notes = "Consolidated entry"  # this should later be turned into that plus whatever will fit of the
                                            # first and second entry's notes; I'm just too lazy right now
    new_usage.valid_entry = True

    return new_usage


def mark_invalid(first_usage, second_usage, third_usage):
    """
    Method takes two (plus None), or three Usages, then marks them as no longer
    valid and saves the new records back to the database.

    :param first_usage:
    :param second_usage:
    :param third_usage:
    :return:
    """
    first_usage.valid_entry = False
    first_usage.save()

    second_usage.valid_entry = False
    second_usage.save()

    if third_usage is not None:
        third_usage.valid_entry = False
        third_usage.save()

    return
