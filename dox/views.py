from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import MainHelpTopic, MainHelpTopicDetail, SpecificViewHelpTopic, SpecificViewTopicDetail
from home.models import HeaderInfo, NavInfo

from lasttime.myglobals import MiscMethods

# just put two and two together here and realized that I really don't want
# these particular views restricted to just logged in users; derp!


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

    return render(request, 'dox/index.html', MiscMethods.add_header_info({'topics': topics_set,}))


def detail(request, topic_id):
    """
    Displays the detailed information for whatever link was selected in the
    index view, above.

    :param request:
    :param topic_id:
    :return:
    """

    topic_info = {}
    topic_info['primary'] = MainHelpTopic.objects.get(id=topic_id)
    topic_info['supporting'] = MainHelpTopicDetail.objects.filter(topic=topic_id)

    return render(request, 'dox/detail.html', MiscMethods.add_header_info(topic_info))

