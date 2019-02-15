from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import NavInfo, HeaderInfo
from .forms import NewUserForm
from lasttime.myglobals import Const, MiscMethods


class IndexView(generic.ListView):
    """
    Just a simple page giving links for logging in or creating a new user.
    """

    model = HeaderInfo
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        page_data = {}

        return MiscMethods.add_header_info(page_data)


def create_user_interface(request):
    """
    Method is utilized for the user creation page.

    :param request:
    :return:
    """

    if request.method == "POST":
        context = {}

        try:
            user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.tz = Const.Time_Zone   # obviously this will need to be changed when we add user TZ selection
            user.save()     # this will need to be in an error handling block at some point here
        except Exception as ex:
            create_user_form = NewUserForm
            return render(request, 'home/create_user.html', MiscMethods.add_header_info({'create_user_form':
                                                                                             create_user_form,
                                                                                         'error_message':
                                                                                             "Error saving: " +
                                                                                             str(ex),}))

        context['username'] = user.username

        return render(request, 'home/user_created.html', MiscMethods.add_header_info(context))
    else:
        create_user_form = NewUserForm()

        return render(request, 'home/create_user.html', MiscMethods.add_header_info({'create_user_form':
                                                                                     create_user_form}))

