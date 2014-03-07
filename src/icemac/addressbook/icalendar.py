from __future__ import absolute_import
import icalendar
import pkg_resources


def Calendar(**kw):
    """Factory to create an icalendar.Calendar with address book defaults."""
    calendar = icalendar.Calendar()
    calendar.add(
        'prodid', '-//icemac.addressbook//%s//EN' %
        pkg_resources.get_distribution('icemac.addressbook').version)
    calendar.add('version', '2.0')
    calendar.add('calscale', 'GREGORIAN')
    for key, value in kw.items():
        calendar.add(key, value)
    return calendar


def set_download_request_headers(request, filename_base):
    """Set the needed headers on the request to download an iCalendar file.

    filename_base ... filename without extension.

    """
    request.response.setHeader('Content-Type', 'text/calendar')
    request.response.setHeader('Content-Disposition',
                               'attachment; filename=%s.ics' % filename_base)
