from django.shortcuts import render
from django.views import generic

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
        for use in usages:
            total_administered += use.dosage

        usage_average = total_administered / usage_count

        # timespan & average calculation
        timespans = []
        prev_time = None
        for use in usages:
            if prev_time is not None:
                timespans.append(use.timestamp - prev_time)
                prev_time = use.timestamp

        total_span = 0
        for span in timespans:
            total_span += span

        average_span = total_span / (usage_count - 1)

        return add_header_info({'usages': usages, 'usage_count': usage_count, 'usage_average': usage_average,
                                'usage_total': total_administered,
                                'sub_name': Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name,
                                'timespans': timespans, 'average_span': average_span})


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
