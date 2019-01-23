from enum import Enum


class Dosage(Enum):
    """
    Different dosage units
    """

    mcg = 1
    mg = 2
    ml = 3
    tsp = 4
    floz = 5


class TimeSpan(Enum):
    """
    Different time span variants
    """

    min = 1
    hr = 2
    day = 3


class MiscMethods:
    """
    Different generic methods for usage from different views.py
    """

    @staticmethod
    def add_pagination_info(prev_context, pagination_object):
        """
        Method takes the previous context, appends properly named variables to
        the aforementioned context for the template's pagination capability,
        and returns it.  Attributes for the pagination context are taken from
        the second parameter, which can be any dataset containing the fields
        for .has_previous, .previous_page_number, .number, .num_pages,
        .next_page_number, and .has_next.

        :param prev_context:
        :param pagination_object:
        :return:
        """

        prev_context['has_previous'] = pagination_object.has_previous
        prev_context['previous_page_number'] = pagination_object.previous_page_number
        prev_context['page_number'] = pagination_object.number
        prev_context['num_pages'] = pagination_object.num_pages
        prev_context['next_page_number'] = pagination_object.next_page_number
        prev_context['has_next'] = pagination_object.has_next

        return prev_context
