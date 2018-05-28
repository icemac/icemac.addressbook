import pytz
import zope.component
import zope.preference.interfaces


def get_preference_group(id):
    return zope.component.getUtility(
        zope.preference.interfaces.IPreferenceGroup, name=id)


def get_time_zone_name():
    """User selected time zone name."""
    return get_preference_group('ab.timeZone').time_zone


def get_time_zone():
    """User selected time zone object."""
    return pytz.timezone(get_time_zone_name())
