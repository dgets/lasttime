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

    template_name = 'dataview/index.html'
    context_object_name = 'latest_relevant_admins'

    def get_queryset(self):
        """
        Return the last five (or fewer) unique substance administration links
        for viewing the record details of.

        :return:
        """


class SubAdminDetailsView(generic.DetailView):
    """
    Again, if I'm misunderstanding concepts about class/generic view
    implementation, this may have to be revised, but the idea behind this view/
    class is to provide a view of the data (averages, then eventually plasma
    drop-off graphing, etc) regarding the history of administrations of the
    particular substance in question.
    """

    model = Usage
    template_name = 'dataview/details.html'

