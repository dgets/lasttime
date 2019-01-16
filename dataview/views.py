from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import datetime
import json

from recadm.forms import Usage
from subadd.forms import Substance
from home.models import NavInfo, HeaderInfo


class IndexView(LoginRequiredMixin, generic.ListView):
    """
    I may be over simplifying things here, since I'm learning how to use
    generic/class-based views while implementing these features, but the
    general idea for this class is to provide a list of links to
    the SubAdminDetailsView class/view, each of which represents a particular
    [unique] substance's administration details.
    """

    model = Substance  # ListView needs to know
    template_name = 'dataview/index.html'   # to avoid default
    # paginate_by = 15
    context_object_name = 'relevant_subs'  # overrides default of 'usage_list'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['sub'] = Substance.objects.all()[:5]

        return add_header_info(context)


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
        usages = Usage.objects.filter(sub=self.kwargs['pk'], user=self.request.user)

        # calculate usage statistics
        usage_data = get_usage_stats(usages)

        # timespan & average calculation
        span_data = get_interval_stats(usages)

        scale_factor = get_graph_normalization_divisor(span_data['longest'].total_seconds(), 600)

        return add_header_info({'usages': usages, 'usage_count': usage_data['count'],
                                'usage_average': usage_data['average'], 'usage_high': usage_data['highest'],
                                'usage_low': usage_data['lowest'], 'usage_total': usage_data['total'],
                                'sub_dosage_units': usages[0].sub.units,
                                'sub_name': Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name,
                                'sub_id': self.kwargs['pk'], 'longest_span': span_data['longest'],
                                'shortest_span': span_data['shortest'], 'timespans': span_data['timespans'],
                                'scale_factor': scale_factor, 'average_span': span_data['average'],})


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

    # print('sub:' + str(substance) + ', elimination_data: ' + str(elimination_data))
    context = {'sub': substance, 'elimination_target': elimination_data['full'],
               'undetectable_target': elimination_data['detectable'],
               'last_usage': elimination_data['last_usage'].timestamp}

    return render(request, 'dataview/halflife.html', add_header_info(context))


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
    usages = Usage.objects.filter(sub=sub_id, user=request.user)[:20]

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

    return HttpResponse(json.dumps({'scale_factor': float(scale_factor), 'dosages': dosage_graph_data}),
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

    usages = Usage.objects.filter(sub=sub_id, user=request.user)[:20]

    timespans = []
    prev_time = None
    max_span = datetime.timedelta(0)
    for use in usages:
        if prev_time is not None:
            current_delta = datetime.timedelta
            current_delta = use.timestamp - prev_time
            current_delta = round_timedelta_to_15min_floor(current_delta)
            timespans.append(current_delta.total_seconds())

            if current_delta > max_span:
                max_span = current_delta

        prev_time = use.timestamp

    scale_factor = get_graph_normalization_divisor(max_span.total_seconds(), 300)
    # convert this to minutes
    for cntr in range(0, len(timespans)):
        timespans[cntr] = timespans[cntr] / (60 ** 2)

    return HttpResponse(json.dumps({'scale_factor': scale_factor, 'timespans': timespans}),
                        content_type='application/json')


def get_weed_stats(usages, active_half_life):
    # we're working with weed, let's give this a shot based on the information available at
    # https://www.mayocliniI sure hope auto-save was keeping upclabs.com/test-info/drug-book/marijuana.html
    # FWIW we're just going to base our projection on the average of the last 2 weeks of usage

    weeks_averaged = 2
    elimination_data = {'full': float(active_half_life) * 5.7,
                        'detectable': None,
                        'relevant_since': datetime.datetime.now() - datetime.timedelta(weeks=weeks_averaged),
                        'last_usage': usages.first(), 'uses': len(usages)}

    # note that half-life durations here (not flat day count) are calculated @ 5.7 * half-life, as in the
    # standard non-lipid-soluble substances; detectable metabolites will be out of the system sooner (hence
    # the less precise flat day count)
    if elimination_data['uses'] <= weeks_averaged:
        # single use: detectable for a standard half-life duration
        elimination_data['full'] = elimination_data['last_usage'].timestamp + \
                                   datetime.timedelta(hours=int(elimination_data['full']))
        elimination_data['detectable'] = elimination_data['last_usage'].timestamp + datetime.timedelta(days=3)

    elif elimination_data['uses'] <= (weeks_averaged * 4):
        # moderate use: detectable for standard half-life * 5/3, _or_ 5 days
        elimination_data['full'] = elimination_data['last_usage'].timestamp + \
                                   datetime.timedelta(hours=int(elimination_data['full'] * (5 / 3)))
        elimination_data['detectable'] = elimination_data['last_usage'].timestamp + datetime.timedelta(days=5)

    elif elimination_data['uses'] <= (weeks_averaged * 7):
        # heavy use: detectable for standard half-life * 10/3, _or_ 10 days
        elimination_data['full'] = elimination_data['last_usage'].timestamp + \
                                   datetime.timedelta(hours=int(elimination_data['full'] * (10 / 3)))
        elimination_data['detectable'] = elimination_data['uses'].timestamp + datetime.timedelta(days=10)

    else:
        # chronic heavy use: detectable for standard half-life * 10, _or_ 30 days
        elimination_data['full'] = elimination_data['uses'].timestamp + \
                                   datetime.timedelta(hours=(elimination_data['full'] * 10))
        elimination_data['detectable'] = elimination_data['uses'].timestamp + datetime.timedelta(days=30)

    print(str(elimination_data))
    return elimination_data


def get_interval_stats(usages):
    """
    Method takes the appropriate Usage objects, compiles the spans between them
    (currently rounded to 15 min intervals), determines the longest, shortest,
    and total of the timespans, along with the average, and returns them in a
    dict.

    :param usages:
    :return:
    """

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
            current_delta = round_timedelta_to_15min_floor(current_delta)
            interval_data['timespans'].append(current_delta)

        prev_time = use.timestamp

    for span in interval_data['timespans']:
        if interval_data['longest'] < span:
            interval_data['longest'] = span

        if interval_data['shortest'] > span:
            interval_data['shortest'] = span

        interval_data['total'] += span

    # errors here if there are 0 or 1 usages, obviously
    interval_data['average'] = round_timedelta_to_15min_floor(interval_data['total'] / (len(usages) - 1))

    return interval_data


def get_usage_stats(usages):
    """
    Method utilizes the Usage records to calculate highest/lowest/average
    dosages, total amount, and times administered, then returning them in a
    dict.

    :param usages: the records that we're looking at
    :return:
    """

    # average & total calculation
    administration_stats = {'total': 0,
                            'highest': 0,
                            'lowest': None,
                            'average': None,
                            'count': len(usages)}

    for use in usages:
        administration_stats['total'] += use.dosage

        if use.dosage > administration_stats['highest']:
            administration_stats['highest'] = use.dosage

        if administration_stats['lowest'] is None or use.dosage < administration_stats['lowest']:
            administration_stats['lowest'] = use.dosage

    administration_stats['average'] = administration_stats['total'] / administration_stats['count']

    return administration_stats


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


def round_timedelta_to_15min_floor(span):
    """
    Method takes the timedelta passed and rounds it down to the closest 15min
    interval.

    :param span: datetime.timedelta
    :return:
    """

    fifteen_min = datetime.timedelta(minutes=15)
    dingleberry = span.total_seconds() % fifteen_min.seconds

    return span - datetime.timedelta(seconds=dingleberry)


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
