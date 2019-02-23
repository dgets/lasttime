from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from lasttime.myglobals import MiscMethods, Const

import datetime
from pytz import timezone
import json

from recadm.forms import Usage
from subadd.forms import Substance
from home.models import NavInfo, HeaderInfo
from . import dataview_support

@login_required
def index(request):
    all_subs = Substance.objects.all()
    filtered_subs = []
    context = {}

    for sub in all_subs:
        if Usage.objects.filter(sub=sub.pk, user=request.user).exists():
            print("Adding " + str(sub))
            filtered_subs.append(sub)

    print("Filtered subs: " + str(filtered_subs))

    paginator = Paginator(filtered_subs, 15)  # 15 admins per page

    page = request.GET.get('page')
    subs = paginator.get_page(page)

    print("subs: " + str(subs))

    context = {'relevant_subs': subs}

    return render(request, 'dataview/index.html', MiscMethods.add_pagination_info(MiscMethods.add_header_info(context),
                                                                                  subs))


class SubAdminDataView(LoginRequiredMixin, generic.DetailView):
    """
    Again, if I'm misunderstanding concepts about class/generic view
    implementation, this may have to be revised, but the idea behind this view/
    class is to provide a view of the data (averages, then eventually plasma
    drop-off graphing, etc) regarding the history of administrations of the
    particular substance in question.  It breaks down a lot of the specifics
    in order to be fed to the D3.js graphing system that is utilized in the
    applicable template.
    """

    model = Usage   # should've said all generic views need to know
    template_name = 'dataview/data_summary.html'  # needed to avoid using the default

    def get_context_data(self, **kwargs):
        usages = Usage.objects.filter(sub=self.kwargs['pk'], user=self.request.user).order_by("timestamp")
        print("pk is: " + str(self.kwargs['pk']))

        # though it duplicates things, the following conditional just checks for errors that will screw up the graphing
        too_few_usages_error = False
        if len(usages) < 2:
            too_few_usages_error = True
        else:
            zero_interval_error = False
            prev_timestamp = None
            for use in usages:
                if prev_timestamp is not None and use.timestamp == prev_timestamp:
                    zero_interval_error = True

                prev_timestamp = use.timestamp

        if too_few_usages_error:
            return MiscMethods.add_header_info({'error_message': "Not enough usages to calculate statistics properly"})

        elif zero_interval_error:
            return MiscMethods.add_header_info({'error_message':
                                                "Zero intervals between datasets causing calculation errors"})

        else:
            # now we get to actually gathering/calculating stats
            # calculate usage statistics
            usage_data = dataview_support.get_usage_stats(usages)

            # timespan & average calculation
            span_data = dataview_support.get_interval_stats(usages)

            # having issues with this with <2 (or maybe it's <3) usages recorded; not stopping to fix it the right way
            # just yet here; next time work is done with this try to get to the bottom of it
            scale_factor = 1    # get_graph_normalization_divisor(span_data['longest'].total_seconds(), 600)

            return MiscMethods.add_header_info({'usages': usages, 'usage_count': usage_data['count'],
                                                'usage_average': usage_data['average'],
                                                'usage_high': usage_data['highest'],
                                                'usage_low': usage_data['lowest'], 'usage_total': usage_data['total'],
                                                'sub_dosage_units': usages[0].sub.units,
                                                'sub_name':
                                                    Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name,
                                                'sub_id': self.kwargs['pk'], 'longest_span': span_data['longest'],
                                                'shortest_span': span_data['shortest'],
                                                'timespans': span_data['timespans'],
                                                'scale_factor': scale_factor, 'average_span': span_data['average'],})


@login_required
def day_constrained_summary(request, sub_id):
    """
    This method will just handle displaying a per-day constrained view of the
    dosages administered to this user per-sub, for now.  More functionality
    including variable time constraints will be added in the future.

    :param request:
    :param sub_id:
    :return:
    """

    usages = Usage.objects.filter(sub=sub_id, user=request.user).order_by("timestamp")
    sub_data = Substance.objects.filter(id=sub_id)

    # not going to bother with testing if there are too few usages for now; if
    # there weren't enough this should've prevented the user from getting this
    # far in the first place

    OneDay = datetime.timedelta(days=1)
    usage_data = {}
    # prev_date = None
    admins_start = MiscMethods.localize_timestamp(datetime.datetime.max - OneDay)
    admins_end = MiscMethods.localize_timestamp(datetime.datetime.min + OneDay)

    for use in usages:
        if MiscMethods.is_localization_needed(use.timestamp):
            local_datetime = MiscMethods.localize_timestamp(use.timestamp)
        else:
            local_datetime = use.timestamp

        if not str(local_datetime.date()) in usage_data:
            usage_data[str(local_datetime.date())] = float(use.dosage)
            print("Creating " + str(local_datetime) + " to " + str(local_datetime.date()) + " @ " + str(use.dosage))

            # get our tabulated duration information
            if local_datetime < admins_start:
                admins_start = local_datetime
            if local_datetime > admins_end:
                admins_end = local_datetime
        else:
            usage_data[str(local_datetime.date())] += float(use.dosage)
            print("Adding " + str(local_datetime) + " to " + str(local_datetime.date()) + " @ " + str(use.dosage))

        # prev_date = local_datetime.date()

    total_span = admins_end - admins_start

    max_dosage = 0
    min_dosage = 100000     # since Decimal.max isn't working, this should be big enough here
    cntr = 0
    total_dosed = 0
    for constrained_usage in usage_data:
        # get our max/min dosage information
        if usage_data[constrained_usage] > max_dosage:
            max_dosage = usage_data[constrained_usage]
        if usage_data[constrained_usage] < min_dosage:
            min_dosage = usage_data[constrained_usage]

        # for calculating average/total information
        cntr += 1
        total_dosed += usage_data[constrained_usage]

    average_dosed = total_dosed / cntr

    print("usage_data: " + str(usage_data))

    return render(request, 'dataview/constrained_dosage_summary.html',
                  MiscMethods.add_header_info({'usage_data': str(usage_data), 'sub_id': sub_id,
                                               'highest_dose': max_dosage, 'lowest_dose': min_dosage,
                                               'avg_dose': average_dosed, 'admins_start': admins_start,
                                               'admins_end': admins_end, 'duration': total_span,
                                               'sub_name': sub_data[0].common_name,}))


@login_required
def extrapolate_halflife_data(request, sub_id):
    """
    This method has a little more beef to it than most.  First it determines
    whether or not the substance passed is lipid soluble or not.  If it is,
    then it tries to determine whether or not it's talking about THC.  If so,
    it utilizes an algorithm based on the Mayo Clinic labs' standards for the
    detectability of THC in urine to determine the detectable half-life
    duration.  If the substance is lipid soluble but not THC, we return an
    error message due to not having enough specific data to work with that
    just yet.  If it's only water/plasma soluble, we calculate solely the
    standard elimination projection (which is done for THC, as well), which is
    based on the 5.7 * half-life projection that I was quoted by one of my
    health care professionals.

    :param request:
    :param sub_id:
    :return:
    """

    # TODO: modularize the lipid_soluble weed block below
    substance = Substance.objects.get(id=sub_id)
    context = {}
    elimination_data = {'full': None, 'detectable': None, 'relevant_since': None,
                        'last_usage':
                            Usage.objects.filter(sub=sub_id, user=request.user).order_by('-timestamp').first(),
                        'uses': 0}

    if substance.lipid_solubility and ('marijuana' in substance.common_name or 'weed' in substance.common_name):
        #process the information for the tweeds
        elimination_data = get_weed_stats(Usage.objects.filter(sub=sub_id, user=request.user).order_by('-timestamp'),
                                          substance.active_half_life)

    elif substance.lipid_solubility:
        # we can't process this yet
        context['error_message'] = \
            "We are not able to process half-life extrapolation for non-THC lipid soluble metabolites yet, sorry!"
    else:
        # last_usage = Usage.objects.filter(sub=sub_id, user=request.user).order_by('-timestamp').first()

        elimination_data['full'] = elimination_data['last_usage'].timestamp + \
                                   datetime.timedelta(hours=int(float(substance.half_life) * 5.7))
        elimination_data['detectable'] = elimination_data['full']

        # check if localization is needed
        if MiscMethods.is_localization_needed(elimination_data['full']):
            elimination_data['full'] = MiscMethods.localize_timestamp(elimination_data['full'])
        if MiscMethods.is_localization_needed(elimination_data['detectable']):
            elimination_data['detectable'] = MiscMethods.localize_timestamp(elimination_data['detectable'])
        if MiscMethods.is_localization_needed(elimination_data['last_usage'].timestamp):
            elimination_data['last_usage'] = MiscMethods.localize_timestamp(elimination_data['last_usage'].timestamp)

    context = {'sub': substance, 'elimination_target': elimination_data['full'],
               'undetectable_target': elimination_data['detectable'],
               'last_usage': elimination_data['last_usage'].timestamp}

    return render(request, 'dataview/halflife.html', MiscMethods.add_header_info(context))


@login_required
def dump_constrained_dose_graph_data(request, sub_id):
    """
    Much like the original 2 'dump' routines that come after this one, this
    method is used to return usage data in a JSON format that the D3.js
    graphing library will handle more easily.  This particular view will put
    a day-constraint (by default-- we'll expand the potential in this as we
    go) on the data, so that per-diem usage totals can be seen instead of the
    details for each individual administration.

    :param request:
    :param sub_id:
    :return:
    """

    usages = Usage.objects.filter(sub=sub_id, user=request.user).order_by("timestamp")

    # not going to bother with testing if there are too few usages for now; if
    # there weren't enough this should've prevented the user from getting this
    # far in the first place

    OneDay = datetime.timedelta(days=1)
    day_dosages = []
    current_dt = None
    tmp_dt = None
    cntr = -1

    # localize timezone?
    # if MiscMethods.is_localization_needed(current_dt):
    #    current_dt = MiscMethods.localize_timestamp(current_dt).date()

    for use in usages:
        current_dt = use.timestamp.date()

        # here we'll enter the blank entries for days where no administrations were recorded
        while tmp_dt is not None and (use.timestamp.date() - tmp_dt) > OneDay:
            # we need a more exact calculation above, maybe?
            tmp_dt = tmp_dt + OneDay
            # usage_data[str(tmp_dt)] = 0.0
            day_dosages.append(0.0)
            cntr += 1
            # print("Adding " + str(tmp_dt) + ": 0.0")

        if current_dt != tmp_dt:
            day_dosages.append(float(use.dosage))
            cntr += 1
            # print("Appending " + str(use.dosage))
        else:
            day_dosages[cntr] += float(use.dosage)
            # print("Adding " + str(use.dosage) + " to " + str(day_dosages[cntr]) + " already at day_dosages[" +
            #      str(cntr) + "]")

        tmp_dt = current_dt
        # what about localization here?
        # if MiscMethods.is_localization_needed(use.timestamp):
        #     tmp_dt = MiscMethods.localize_timestamp(use.timestamp).date()
        # else:
        #     tmp_dt = use.timestamp.date()

    return HttpResponse(json.dumps({'scale_factor': 1, 'dosages': day_dosages}), content_type='application/json')


@login_required
def dump_dose_graph_data(request, sub_id):
    """
    This view is a little more interesting than the different flavors of the
    same that we've been working with so far.  This one is going to take our
    request parameters and use them to determine what subset of administration
    data to pull out into a JSON string and then return that (alone, not
    embedded in any HTML or template) to feed to the D3 library for graphing.

    Until we've gotten the basics working here we're going to limit the
    number of administrations graphed to 20; afterwards we'll add options to
    the above dataview in order to select how much we're going to graph.

    :param request:
    :param sub_id:
    :return:
    """

    dosage_graph_data = []
    usages = Usage.objects.filter(sub=sub_id, user=request.user).order_by("timestamp")

    max_dosage = 0
    for use in usages:
        # later on we can look at using use.notes as hover-over text for each
        # graph bar, or something of the like
        # dosage_graph_data.append(float(use.dosage))

        if max_dosage < use.dosage:
            max_dosage = use.dosage

    scale_factor = dataview_support.get_graph_normalization_divisor(max_dosage, 300)

    # okay, yeah the 2 for loops is gross, but my brain is fried and I want to
    # finish this quick; I'll fix it later
    # TODO: fix the gross 2 for loops issue
    for use in usages:
        dosage_graph_data.append(float(use.dosage))

    return HttpResponse(json.dumps({'scale_factor': 1, 'dosages': dosage_graph_data}),
                        content_type='application/json')


@login_required
def dump_interval_graph_data(request, sub_id):
    """
    View does the same as the above one, except for the intervals between
    administrations data subset.

    :param request:
    :param sub_id:
    :return:
    """

    usages = Usage.objects.filter(sub=sub_id, user=request.user).order_by("timestamp")

    timespans = []
    prev_time = None
    tmp_dt = None
    max_span = datetime.timedelta(0)
    for use in usages:
        # localization needed?
        if MiscMethods.is_localization_needed(use.timestamp):
            tmp_dt = MiscMethods.localize_timestamp(use.timestamp)
        else:
            tmp_dt = use.timestamp

        if prev_time is not None:
            current_delta = datetime.timedelta
            current_delta = tmp_dt - prev_time
            timespans.append(int(current_delta.total_seconds() / 3600))

            if current_delta > max_span:
                max_span = current_delta

        prev_time = tmp_dt

    scale_factor = 1    # get_graph_normalization_divisor(max_span.total_seconds(), 72)
    # convert this to minutes
    for cntr in range(0, len(timespans)):
        timespans[cntr] = timespans[cntr]

    return HttpResponse(json.dumps({'scale_factor': scale_factor, 'timespans': timespans}),
                        content_type='application/json')
