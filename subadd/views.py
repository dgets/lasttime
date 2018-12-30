from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .forms import Substance, SubstanceForm

from home.models import NavInfo, HeaderInfo


def index(request):
    """
    View provides a listing of all substances in the database; passes the
    information on to the index template for rendering.

    :param request:
    :return:
    """

    all_subs = Substance.objects.all()
    context = {
        'all_subs': all_subs,
    }

    return render(request, 'subadd/index.html', add_header_info(context))


def add(request):
    """
    View provides an empty form with the relevant fields (see forms.py) needing
    to be filled out by the user in order to record a new substance.  Passes
    the form off to add.html for rendering.

    :param request:
    :return:
    """

    add_sub_form = SubstanceForm()

    return render(request, 'subadd/add.html', add_header_info({'substance': None, 'add_sub_form': add_sub_form}))


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

    substance = Substance(common_name = request.POST['common_name'],
        sci_name = request.POST['scientific_name'],
        half_life = request.POST['half_life'],
        active_half_life = request.POST['detectable_half_life'],
        lipid_solubility = request.POST.get('fat_soluble', False))

    # we'll need to do validation here, of course

    try:
        substance.save()
    except:
        error_message = "Unable to save record to database (unknown reason)!"
        return render(request, 'subadd/addentry.html', substance)

    return render(request, 'subadd/index.html', add_header_info({'all_subs':
                  Substance.objects.all()}))


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

    return render(request, 'subadd/detail.html', add_header_info({'substance': substance}))


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
