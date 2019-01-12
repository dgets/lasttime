from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User

from .models import NavInfo, HeaderInfo
from .forms import NewUserForm


class IndexView(generic.ListView):
    model = HeaderInfo
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        page_data = {}

        return add_header_info(page_data)


def create_user_interface(request):
    """
    Method is utilized for the user creation page.

    :param request:
    :return:
    """

    if request.method == "POST":
        context = {}

        user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()     # this will need to be in an error handling block at some point here

        context['username'] = user.username

        return render(request, 'home/user_created.html', add_header_info(context))
    else:
        create_user_form = NewUserForm()

        return render(request, 'home/create_user.html', add_header_info({'create_user_form': create_user_form}))


def add_header_info(page_data):
    """
    Method takes whatever (presumably context) dict that is passed to it and
    adds the 'NavInfo' and 'HeaderInfo' keys to it, pointing to the
    applicable data for the header & footer schitt.

    :param page_data:
    :return: new context (dict)
    """

    page_data['header_info'] = HeaderInfo.objects.first()
    page_data['links'] = NavInfo.objects.all()

    return page_data
