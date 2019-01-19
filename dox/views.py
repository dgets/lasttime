from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import MainHelpTopic, MainHelpTopicDetails, SpecificViewHelpTopic, SpecificViewTopicDetails
from home.models import HeaderInfo, NavInfo

@login_required
def index(request):
    """
    View displays the topics links for everything available, paginated if
    necessary.

    :param request:
    :return:
    """
    topics = MainHelpTopic.objects.all()
    paginator = Paginator(topics, 15)
    page = request.GET.get('page')
    topics_set = paginator.get_page(page)

    return add_header_info({'topics': topics_set,})


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
