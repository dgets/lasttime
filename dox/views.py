from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import MainHelpTopic, MainHelpTopicDetails, SpecificViewHelpTopic, SpecificViewTopicDetails

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

