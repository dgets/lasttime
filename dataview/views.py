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
    # context['sub_data'] = Substance.objects.filter(pk=pk)

    # def get_queryset(self):
    #     return Usage.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        # page_data = super().get_context_data(**kwargs)
        usages = Usage.objects.filter(sub=self.kwargs['pk'])
        usage_count = len(usages)

        total_administered = 0
        for use in usages:
            total_administered += use.dosage

        usage_average = total_administered / usage_count

        return {'usages': usages, 'usage_count': usage_count, 'usage_average': usage_average,
                'usage_total': total_administered,
                'sub_name': Substance.objects.filter(pk=self.kwargs['pk'])[0].common_name,}


# def add_header_info(previous_context):

