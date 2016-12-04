from ..errormessage import render_error
from icemac.addressbook.person import person_entity
from zope.i18n import translate


def test_errormessage__render_error__1(zcmlS):
    """It is able to render an error which does not belong to a field."""
    message = render_error(
        person_entity, field_name='', exc=RuntimeError('General Error!'))
    assert ('Unexpected error occurred: RuntimeError: General Error!' ==
            translate(message))
