from django.shortcuts import render
from django.views import generic

from .models import NavInfo, HeaderInfo


class IndexView(generic.ListView):
    model = HeaderInfo
    template_name = 'home/index.html'

    def get_context_data(self):
        page_data = {}

        return add_header_info(page_data)


def add_header_info(page_data):
    """
    Method takes whatever (presumably context) dict that is passed to it and
    adds the 'NavInfo' and 'HeaderInfo' keys to it, pointing to the
    applicable data for the header & footer schitt.

    :param previous_context:
    :return: new context (dict)
    """

    previous_context['header_info'] = HeaderInfo.objects.first()
    previous_context['links'] = NavInfo.objects.all()

    return previous_context
