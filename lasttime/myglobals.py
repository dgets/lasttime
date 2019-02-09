from enum import Enum
from datetime import datetime
from pytz import timezone

class Const:
    """
    Just constant data here
    """
    Debugging = {
        'dataview': True,
    }
    Time_Zone = 'US/Central'

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
        prev_context['num_pages'] = pagination_object.paginator.num_pages
        prev_context['next_page_number'] = pagination_object.next_page_number
        prev_context['has_next'] = pagination_object.has_next

        return prev_context

    @staticmethod
    def chk_debug_print(area, debug_message):
        """
        Checks to see if we're in debugging mode and, if so, prints the message
        to the console/terminal window.

        :param area:
        :param debug_message:
        :return:
        """

        if Const.Debugging[area]:
            print("DEBUG:\t" + debug_message)

    @staticmethod
    def localize_timestamp(ts):
        """
        Takes whatever timestamp it is handed and changes it to a localized one;
        right now it's going to set everything to US/Central, but as the bit in
        the user records starts working correctly as far as saving a default TZ
        per-user, we'll add another parameter here and handle it for whatever TZ
        that they're in.

        :param ts:
        :return:
        """

        central_tz = timezone(Const.Time_Zone)
        timestamp = central_tz.localize(ts)

        return timestamp

    @staticmethod
    def str_to_datetime(datetime_string):
        """
        Simply a wrapper to convert a properly formatted string back into a
        datetime object for localization or whatever is needed; NOTE, as above,
        this is only being utilized for US/Central right now and will require
        additional work as timezones are implemented per-user.

        :param datetime_string:
        :return:
        """

        return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def is_localization_needed(datetime_in_question):
        """
        Just determines whether or not a datetime object has already been
        localized; returns true if localization is needed.

        :param datetime_in_question:
        :return:
        """

        if datetime_in_question.tzinfo is None or datetime_in_question.tzinfo.utcoffset(datetime_in_question) is None:
            # localization is needed for this one
            return True
        else:
            return False
