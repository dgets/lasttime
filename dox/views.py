from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import MainHelpTopic, MainHelpTopicDetail, SpecificViewHelpTopic, SpecificViewTopicDetail
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

    return render(request, 'dox/index.html', add_header_info({'topics': topics_set,}))


@login_required
def detail(request):
    """
    Displays the detailed information for whatever link was selected in the
    index view, above.

    :param request:
    :return:
    """




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
