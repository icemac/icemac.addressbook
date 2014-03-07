import zope.interface


class IBirthDate(zope.interface.Interface):
    """Person's birthdate data."""

    icalendar_event = zope.interface.Attribute(
        'Birthdate as icalendar.Event or `None`')
