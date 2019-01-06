from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
import datetime
import json

from recadm.forms import Usage
from subadd.forms import Substance
from home.models import NavInfo, HeaderInfo


class IndexView(generic.ListView):
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

    # def get_queryset(self):
    #     """
    #     Return the last five (or fewer) unique substance administration links
    #     for viewing the record details of.
    #
    #     :return: Substance queryset
    #     """
    #
    #     return Substance.objects.all()[:5]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context['sub'] = Substance.objects.all()[:5]

        return add_header_info(context)


class SubAdminDataView(generic.DetailView):
    """
    Again, if I'm misunderstanding concepts about class/generic view
    implementation, this may have to be revised, but the idea behind this view/
    class is to provide a view of the data (averages, then eventually plasma
    drop-off graphing, etc) regarding the history of administrations of the
    particular substance in question.
    """

    model = Usage   # should've said all generic views need to know
    template_name = 'dataview/data_summary.html'  # needed to avoid using the default

    # TODO: add calculation of the amount of time between dosages (plus avg)

    def get_context_data(self, **kwargs):
        usages = Usage.objects.filter(sub=self.kwargs['pk'])
        usage_count = len(usages)

        # average & total calculation
        total_administered = 0
        highest_administered = 0
        lowest_administered = None
        for use in usages:
            total_administered += use.dosage

            if use.dosage > highest_administered:
                highest_administered = use.dosage

            if lowest_administered is None or use.dosage < lowest_administered:
                lowest_administered = use.dosage

        usage_average = total_administered / usage_count

        # timespan & average calculation
        timespans = []
        prev_time = None    # would we (perhaps optionally) want timezone.now()?
        for use in usages:
            if prev_time is not None:
                current_delta = datetime.timedelta
                current_delta = use.timestamp - prev_time
                current_delta = round_timedelta_to_15min_floor(current_delta)
                timespans.append(current_delta)

            prev_time = use.timestamp

        total_span = datetime.timedelta(0)
        for span in timespans:
            total_span += span

        average_span = round_timedelta_to_15min_floor(total_span / (usage_count - 1))

        return add_header_info({'usages': usages, 'usage_count': usage_count, 'usage_average': usage_average,
                                'usage_high': highest_administered, 'usage_low': lowest_administered,
                                'usage_total': total_administered,
                                'sub_name': Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name,
                                'timespans': timespans, 'average_span': average_span})


def dump_graph_data(request, sub_id):
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
    :return:
    """

    usage_graph_data = {}
    # usage_sub_id = request.POST['sub']
    usages = Usage.objects.filter(sub=sub_id)[:20]   # pk or usage_sub_id?

    for use in usages:
        usage_graph_data[str(use.timestamp)] = float(use.dosage)
        # TODO: find a workaround for this only working with integers
        # later on we can look at using use.notes as hover-over text for each
        # graph bar, or something of the like

    return HttpResponse(json.dumps(usage_graph_data), content_type='application/json')


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
