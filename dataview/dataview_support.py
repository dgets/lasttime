from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from lasttime.myglobals import MiscMethods, Const

import datetime
from pytz import timezone
import json

from recadm.forms import Usage
from subadd.forms import Substance
from home.models import NavInfo, HeaderInfo


def get_weed_stats(usages, active_half_life):
    """
    We're working with weed, let's give this a shot based on the information
    available at
    https://www.mayocliniclabs.com/test-info/drug-book/marijuana.html FWIW
    we're just going to base our projection on the average of the last 2 weeks
    of usage.

    :param usages:
    :param active_half_life:
    :return:
    """

    weeks_averaged = 2
    relevant_dt = MiscMethods.localize_timestamp(datetime.datetime.now())
    elimination_data = {'full': float(active_half_life) * 5.7,
                        'detectable': None,
                        'relevant_since': relevant_dt - datetime.timedelta(weeks=weeks_averaged),
                        'last_usage': usages.first(), 'uses': len(usages)}

    # localize the following?
    last_usage_dt = elimination_data['last_usage'].timestamp
    uses_dt = elimination_data['uses'].timestamp

    if MiscMethods.is_localization_needed(last_usage_dt):
        last_usage_dt = MiscMethods.localize_timestamp(last_usage_dt)
    if MiscMethods.is_localization_needed(uses_dt):
        uses_dt = MiscMethods.localize_timestamp(uses_dt)

    # note that half-life durations here (not flat day count) are calculated @ 5.7 * half-life, as in the
    # standard non-lipid-soluble substances; detectable metabolites will be out of the system sooner (hence
    # the less precise flat day count)
    if elimination_data['uses'] <= weeks_averaged:
        # single use: detectable for a standard half-life duration
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full']))
        elimination_data['detectable'] = last_usage_dt + datetime.timedelta(days=3)

    elif elimination_data['uses'] <= (weeks_averaged * 4):
        # moderate use: detectable for standard half-life * 5/3, _or_ 5 days
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full'] * (5 / 3)))
        elimination_data['detectable'] = last_usage_dt + datetime.timedelta(days=5)

    elif elimination_data['uses'] <= (weeks_averaged * 7):
        # heavy use: detectable for standard half-life * 10/3, _or_ 10 days
        elimination_data['full'] = last_usage_dt + datetime.timedelta(hours=int(elimination_data['full'] * (10 / 3)))
        elimination_data['detectable'] = uses_dt + datetime.timedelta(days=10)

    else:
        # chronic heavy use: detectable for standard half-life * 10, _or_ 30 days
        elimination_data['full'] = uses_dt + datetime.timedelta(hours=(elimination_data['full'] * 10))
        elimination_data['detectable'] = uses_dt + datetime.timedelta(days=30)

    return elimination_data


def get_interval_stats(usages):
    """
    Method takes the appropriate Usage objects, compiles the spans between
    them, determines the longest, shortest, and total of the timespans, along
    with the average, and returns them in a dict.

    Dict keys consist of timespans, total, longest, shortest, average

    :param usages:
    :return:
    """

    # NOTE: with the current functionality in this particular method, we shouldn't need to worry about having to
    # localize anything; it makes no difference to the relevance of the intervals, especially as they're not mapped
    # to any particular dates on the graph or anything

    prev_time = None
    interval_data = {'timespans': [],
                     'total': datetime.timedelta(0),
                     'longest': datetime.timedelta(0),
                     'shortest': datetime.timedelta.max,
                     'average': None,}

    for use in usages:
        if prev_time is not None:
            # current_delta = datetime.timedelta
            current_delta = use.timestamp - prev_time
            interval_data['timespans'].append(round_timedelta(current_delta, datetime.timedelta(seconds=1)))

        prev_time = use.timestamp

    for span in interval_data['timespans']:
        if interval_data['longest'] < span:
            interval_data['longest'] = span

        if interval_data['shortest'] > span:
            interval_data['shortest'] = span

        interval_data['total'] += span

    # errors here if there are 0 or 1 usages, obviously
    interval_data['average'] = round_timedelta((interval_data['total'] / (len(usages) - 1)),
                                               datetime.timedelta(seconds=1))

    return interval_data


def round_timedelta(td, period):
    """
    Rounds the given timedelta by the given timedelta period.

    NOTE: Stolen shamelessly from
    https://stackoverflow.com/questions/42299312/rounding-a-timedelta-to-the-nearest-15-minutes

    :param td: `timedelta` to round
    :param period: `timedelta` period to round by.
    :return:
    """

    period_seconds = period.total_seconds()
    half_period_seconds = period_seconds / 2
    remainder = td.total_seconds() % period_seconds

    if remainder >= half_period_seconds:
        return datetime.timedelta(seconds=td.total_seconds() + (period_seconds - remainder))
    else:
        return datetime.timedelta(seconds=td.total_seconds() - remainder)


def get_usage_stats(usages):
    """
    Method utilizes the Usage records to calculate highest/lowest/average
    dosages, total amount, and times administered, then returning them in a
    dict.

    Dict keys consist of: total, highest, lowest, average, count

    :param usages: the records that we're looking at
    :return:
    """

    # TODO: add the dates at which each of the highest & lowest were admined

    # average & total calculation
    administration_stats = {'total': 0,
                            'highest': 0,
                            'lowest': None,
                            'average': None,
                            'count': len(usages)}

    for use in usages:
        administration_stats['total'] += use.dosage

        # rounding things to 3 decimal places for a nicer display experience
        if use.dosage > administration_stats['highest']:
            administration_stats['highest'] = round(use.dosage, 3)

        if administration_stats['lowest'] is None or use.dosage < administration_stats['lowest']:
            administration_stats['lowest'] = round(use.dosage, 3)

    administration_stats['average'] = round((administration_stats['total'] / administration_stats['count']), 3)

    return administration_stats


# def round_timedelta_to_15min_floor(span):
#     """
#     Method takes the timedelta passed and rounds it down to the closest 15min
#     interval.
#
#     :param span: datetime.timedelta
#     :return:
#     """
#
#     fifteen_min = datetime.timedelta(minutes=15)
#     dingleberry = span.total_seconds() % fifteen_min.seconds
#
#     return span - datetime.timedelta(seconds=dingleberry)


def get_graph_normalization_divisor(max_qty, graph_max_boundary):
    """
    Method takes the maximum quantity (dimensionless), along with the maximum
    dimension on the quantity axis, and returns the scale to divide by in
    order to make things fit properly in the graph.

    :param max_qty:
    :param graph_max_boundary:
    :return:
    """

    scale_factor = 1
    if max_qty <= (graph_max_boundary / 2) or max_qty > graph_max_boundary:
        scale_factor = graph_max_boundary / max_qty

    return scale_factor


def check_dose_range_sanity(dose_list):
    """
    Method determines whether or not any of the dosages passed in the dose_list
    parameter are an order of magnitude greater than any of the others; if so,
    they are chopped at 10x the lowest dosage.

    TODO: Check to see if this would be better implemented as the method below

    :param dose_list:
    :return:
    """

    low_dose = 10000
    high_dose = 0
    constrained_list = []

    for dose in dose_list:
        if low_dose > dose:
            low_dose = dose
        if high_dose < dose:
            high_dose = dose

    if high_dose >= (low_dose * 10):
        # an order of magnitude or more range breaks the graphs
        for dose in dose_list:
            if dose > (low_dose * 10):
                constrained_list.append(low_dose * 10)
                # print("Chopping " + str(dose) + " to " + str(low_dose * 10))
            else:
                constrained_list.append(dose)

        return constrained_list
    else:
        return dose_list


def check_for_extremes_from_average(qty_list):
    """
    Method determines whether or not any of the quantities passed in the
    'qty_list' parameter are over 2 times the average quantity; if
    so, they are constrained at this value and returned (or returned
    unscathed if not).

    :param qty_list:
    :return:
    """

    cntr = 0
    average = 0

    # determine list average
    for qty in qty_list:
        average += qty

    average = average / len(qty_list)

    # constrain list to average x multiplier
    for qty in qty_list:
        if qty > (average * 2):
            qty_list[cntr] = average * 2

        cntr += 1

    # list was modified in place, so we can just return it
    return qty_list
