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


# class IndexView(LoginRequiredMixin, generic.ListView):
#     """
#     I may be over simplifying things here, since I'm learning how to use
#     generic/class-based views while implementing these features, but the
#     general idea for this class is to provide a list of links to
#     the SubAdminDetailsView class/view, each of which represents a particular
#     [unique] substance's administration details.
#     """
#
#     model = Substance  # ListView needs to know
#     template_name = 'dataview/index.html'   # to avoid default
#     paginate_by = 15
#     context_object_name = 'relevant_subs'  # overrides default of 'usage_list'
#
#     def get_context_data(self, **kwargs):
#         context = super(IndexView, self).get_context_data(**kwargs)
#
#         # how do I hand off the lifting to the database here?
#         subs = Substance.objects.all()
#         context['subs'] = []
#         for sub in subs:
#             if Usage.objects.filter(sub=sub.pk, user=self.request.user).exists():
#                 context['subs'].append(sub)
#
#         return MiscMethods.add_header_info(context)


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
            usage_data = get_usage_stats(usages)

            # timespan & average calculation
            span_data = get_interval_stats(usages)

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
def constrained_summary(request, sub_id):
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

    usage_data = {}
    admins_start = MiscMethods.localize_timestamp(datetime.datetime.max - datetime.timedelta(days=1))
    admins_end = MiscMethods.localize_timestamp(datetime.datetime.min + datetime.timedelta(days=1))
    for use in usages:
        # if use.timestamp.tzinfo is None or use.timestamp.tzinfo.utcoffset(use.timestamp) is None:
        #     local_datetime = MiscMethods.localize_timestamp(use.timestamp)
        # else:
        #     local_datetime = use.timestamp
        if MiscMethods.is_localization_needed(use.timestamp):
            local_datetime = MiscMethods.localize_timestamp(use.timestamp)
        else:
            local_datetime = use.timestamp

        if not str(local_datetime.date()) in usage_data:
            usage_data[str(local_datetime.date())] = float(use.dosage)

            # get our tabulated duration information
            if local_datetime < admins_start:
                admins_start = local_datetime
            if local_datetime > admins_end:
                admins_end = local_datetime
        else:
            usage_data[str(local_datetime.date())] += float(use.dosage)

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

    day_dosages = []
    current_dt = datetime.datetime.now()
    tmp_dt = None
    cntr = -1

    # localize timezone?
    if MiscMethods.is_localization_needed(current_dt):
        current_dt = MiscMethods.localize_timestamp(current_dt).date()

    for use in usages:
        # print("Currently working with use: " + str(use))

        # what about localization here?
        if MiscMethods.is_localization_needed(use.timestamp):
            tmp_dt = MiscMethods.localize_timestamp(use.timestamp).date()
        else:
            tmp_dt = use.timestamp.date()

        # print("timestamp date: " + str(use.timestamp.date()))
        if current_dt != tmp_dt:
            current_dt = use.timestamp.date()

            day_dosages.append(float(use.dosage))
            cntr += 1

        else:
            day_dosages[cntr] += float(use.dosage)

        # print("filing under: " + str(current_dt))

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

    scale_factor = get_graph_normalization_divisor(max_dosage, 300)

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


def get_weed_stats(usages, active_half_life):
    """
    We're working with weed, let's give this a shot based on the information
    available at
    https://www.mayocliniclabs.com/test-info/drug-book/marijuana.html FWIW
    we're just going to base our projection on the average of the last 2 weeks
    of usage.

    :param usages:
    :param active_half_life:
    :return:
    """


    weeks_averaged = 2
    relevant_dt = MiscMethods.localize_timestamp(datetime.datetime.now())
    elimination_data = {'full': float(active_half_life) * 5.7,
                        'detectable': None,
                        'relevant_since': relevant_dt - datetime.timedelta(weeks=weeks_averaged),
                        'last_usage': usages.first(), 'uses': len(usages)}

    # localize the following?
    last_usage_dt = elimination_data['last_usage'].timestamp
    uses_dt = elimination_data['uses'].timestamp

    if MiscMethods.is_localization_needed(last_usage_dt):
        last_usage_dt = MiscMethods.localize_timestamp(last_usage_dt)
    if MiscMethods.is_localization_needed(uses_dt):
        uses_dt = MiscMethods.localize_timestamp(uses_dt)

    # note that half-life durations here (not flat day count) are calculated @ 5.7 * half-life, as in the
    # standard non-lipid-soluble substances; detectable metabolites will be out of the system sooner (hence
    # the less precise flat day count)
    if elimination_data['uses'] <= weeks_averaged:
        # single use: detectable for a standard half-life duration
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full']))
        elimination_data['detectable'] = last_usage_dt + datetime.timedelta(days=3)

    elif elimination_data['uses'] <= (weeks_averaged * 4):
        # moderate use: detectable for standard half-life * 5/3, _or_ 5 days
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full'] * (5 / 3)))
        elimination_data['detectable'] = last_usage_dt + datetime.timedelta(days=5)

    elif elimination_data['uses'] <= (weeks_averaged * 7):
        # heavy use: detectable for standard half-life * 10/3, _or_ 10 days
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full'] * (10 / 3)))
        elimination_data['detectable'] = uses_dt + datetime.timedelta(days=10)

    else:
        # chronic heavy use: detectable for standard half-life * 10, _or_ 30 days
        elimination_data['full'] = uses_dt + datetime.timedelta(hours=(elimination_data['full'] * 10))
        elimination_data['detectable'] = uses_dt + datetime.timedelta(days=30)

    return elimination_data


def get_interval_stats(usages):
    """
    Method takes the appropriate Usage objects, compiles the spans between
    them, determines the longest, shortest, and total of the timespans, along
    with the average, and returns them in a dict.

    :param usages:
    :return:
    """

    # NOTE: with the current functionality in this particular method, we shouldn't need to worry about having to
    # localize anything; it makes no difference to the relevance of the intervals, especially as they're not mapped
    # to any particular dates on the graph or anything

    prev_time = None
    interval_data = {'timespans': [],
                     'total': datetime.timedelta(0),
                     'longest': datetime.timedelta(0),
                     'shortest': datetime.timedelta.max,
                     'average': None,}

    for use in usages:
        if prev_time is not None:
            current_delta = datetime.timedelta
            current_delta = use.timestamp - prev_time
            interval_data['timespans'].append(round_timedelta(current_delta, datetime.timedelta(seconds=1)))

        prev_time = use.timestamp

    for span in interval_data['timespans']:
        if interval_data['longest'] < span:
            interval_data['longest'] = span

        if interval_data['shortest'] > span:
            interval_data['shortest'] = span

        interval_data['total'] += span

    # errors here if there are 0 or 1 usages, obviously
    interval_data['average'] = round_timedelta((interval_data['total'] / (len(usages) - 1)),
                                               datetime.timedelta(seconds=1))

    return interval_data


def round_timedelta(td, period):
    """
    Rounds the given timedelta by the given timedelta period.

    NOTE: Stolen shamelessly from
    https://stackoverflow.com/questions/42299312/rounding-a-timedelta-to-the-nearest-15-minutes

    :param td: `timedelta` to round
    :param period: `timedelta` period to round by.
    :return:
    """

    period_seconds = period.total_seconds()
    half_period_seconds = period_seconds / 2
    remainder = td.total_seconds() % period_seconds

    if remainder >= half_period_seconds:
        return datetime.timedelta(seconds=td.total_seconds() + (period_seconds - remainder))
    else:
        return datetime.timedelta(seconds=td.total_seconds() - remainder)


def get_usage_stats(usages):
    """
    Method utilizes the Usage records to calculate highest/lowest/average
    dosages, total amount, and times administered, then returning them in a
    dict.

    :param usages: the records that we're looking at
    :return:
    """

    # TODO: add the dates at which each of the highest & lowest were admined

    # average & total calculation
    administration_stats = {'total': 0,
                            'highest': 0,
                            'lowest': None,
                            'average': None,
                            'count': len(usages)}

    for use in usages:
        administration_stats['total'] += use.dosage

        # rounding things to 3 decimal places for a nicer display experience
        if use.dosage > administration_stats['highest']:
            administration_stats['highest'] = round(use.dosage, 3)

        if administration_stats['lowest'] is None or use.dosage < administration_stats['lowest']:
            administration_stats['lowest'] = round(use.dosage, 3)

    administration_stats['average'] = round((administration_stats['total'] / administration_stats['count']), 3)

    return administration_stats


# def round_timedelta_to_15min_floor(span):
#     """
#     Method takes the timedelta passed and rounds it down to the closest 15min
#     interval.
#
#     :param span: datetime.timedelta
#     :return:
#     """
#
#     fifteen_min = datetime.timedelta(minutes=15)
#     dingleberry = span.total_seconds() % fifteen_min.seconds
#
#     return span - datetime.timedelta(seconds=dingleberry)


def get_graph_normalization_divisor(max_qty, graph_max_boundary):
    """
    Method takes the maximum quantity (dimensionless), along with the maximum
    dimension on the quantity axis, and returns the scale to divide by in
    order to make things fit properly in the graph.

    :param max_qty:
    :param graph_max_boundary:
    :return:
    """

    scale_factor = 1
    if max_qty <= (graph_max_boundary / 2) or max_qty > graph_max_boundary:
        scale_factor = graph_max_boundary / max_qty

    return scale_factor
