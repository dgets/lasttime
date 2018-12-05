from django.shortcuts import render
from django.views import generic

from recadm.forms import Usage
from subadd.forms import Substance

# Create your views here.


class IndexView(generic.ListView):
    """
    I may be over simplifying things here, since I'm learning how to use
    generic/class-based views while implementing these features, but the
    general idea for this class is to provide a list of links to
    the SubAdminDetailsView class/view, each of which represents a particular
    [unique] substance's administration details.
    """

    template_name = 'dataview/index.html'   # to avoid default
    context_object_name = 'relevant_subs'  # overrides default of 'usage_list'
    model = Substance   # ListView needs to know

    def get_queryset(self):
        """
        Return the last five (or fewer) unique substance administration links
        for viewing the record details of.

        :return: Substance queryset
        """

        return Substance.objects.all()[:5]


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

        return {'usages': usages, 'usage_count': usage_count, 'usage_average': usage_average,
                'usage_total': total_administered,
                'sub_name': Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name, 'timespans': timespans,
                'average_span': average_span}

