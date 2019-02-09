from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from lasttime.myglobals import MiscMethods

from .forms import Substance, SubstanceForm


@login_required
def index(request):
    """
    View provides a listing of all substances in the database; passes the
    information on to the index template for rendering.

    :param request:
    :return:
    """

    all_subs = Substance.objects.all()
    paginator = Paginator(all_subs, 15)  # 15 admins per page

    page = request.GET.get('page')
    subs = paginator.get_page(page)

    context = {
        'all_subs': subs,
    }

    return render(request, 'subadd/index.html', MiscMethods.add_pagination_info(MiscMethods.add_header_info(context),
                                                                                subs))


@login_required
def add(request):
    """
    View provides an empty form with the relevant fields (see forms.py) needing
    to be filled out by the user in order to record a new substance.  Passes
    the form off to add.html for rendering.

    :param request:
    :return:
    """

    add_sub_form = SubstanceForm()

    return render(request, 'subadd/add.html', MiscMethods.add_header_info({'substance': None,
                                                                           'add_sub_form': add_sub_form}))


@login_required
def addentry(request):
    """
    Another version of the above substance data entry form, this one is for
    usage when there was an error in validation or submission and processing
    of the previous form; this one comes pre-filled with whatever data the
    user had previously submitted.  Hands things off to addentry template,
    if there is an issue in saving the database record from the previous
    entry, otherwise it stuffs everything in the database where it needs to
    go and sends the user back to the index template in order to see the
    substances summary so that they can verify that their addition has been
    added.

    :param request:
    :return:
    """

    try:
        substance = Substance(common_name=request.POST['common_name'],
                              sci_name=request.POST['sci_name'],
                              half_life=request.POST['half_life'],
                              active_half_life=request.POST['active_half_life'],
                              lipid_solubility=request.POST.get('lipid_solubility', False),
                              units=request.POST['units'])

        # we'll need to do validation here, of course

    except:
        context = {}
        context['error_message'] = "Please navigate to addentry (here) only from the links."

        return render(request, 'subadd/add.html', MiscMethods.add_header_info(context))


    try:
        substance.save()
    except Exception as ex:
        context = {}
        context['error_message'] = "Unable to save record to database (" + str(ex) + ")!"
        context['substance'] = substance

        return render(request, 'subadd/add.html', context)

    return render(request, 'subadd/index.html', MiscMethods.add_header_info({'all_subs': Substance.objects.all()}))


@login_required
def detail(request, substance_id):
    """
    View provides details on any particular substance record.  Hands things
    off to the detail template for rendering.

    :param request:
    :param substance_id:
    :return:
    """

    try:
        substance = get_object_or_404(Substance, pk=substance_id)
    except Substance.DoesNotExist:
        raise Http404("Substance does not exist :|")

    return render(request, 'subadd/detail.html', MiscMethods.add_header_info({'substance': substance}))

