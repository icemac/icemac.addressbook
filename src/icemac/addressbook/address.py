from icemac.addressbook.i18n import _
import grokcore.component
import icemac.addressbook.entities
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import persistent
import six
import zope.container.contained
import zope.globalrequest
import zope.interface
import zope.schema.fieldproperty


@zope.interface.implementer(
    icemac.addressbook.interfaces.IPostalAddress,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
)
class PostalAddress(persistent.Persistent,
                    zope.container.contained.Contained):
    """A postal address."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IPostalAddress)


# postal address entity, default_attrib is the name of the attribute
# on IPerson which contains the default postal address.
postal_address_entity = icemac.addressbook.entities.create_entity(
    _(u'postal address'), icemac.addressbook.interfaces.IPostalAddress,
    PostalAddress, default_attrib='default_postal_address')


@zope.component.adapter(icemac.addressbook.interfaces.IPostalAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def postal_address_title(address):
    """Title of a postal address."""
    title = _('none')
    values = [icemac.addressbook.interfaces.ITitle(getattr(address, x))
              for x in ('address_prefix', 'street', 'zip', 'city', 'country')
              if getattr(address, x)]
    if values:
        request = zope.globalrequest.getRequest()
        title = ', '.join(
            icemac.addressbook.utils.translate(val, request)
            for val in values)
    return title


@zope.interface.implementer(
    icemac.addressbook.interfaces.IEMailAddress,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
)
class EMailAddress(persistent.Persistent,
                   zope.container.contained.Contained):
    """An e-mail address."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IEMailAddress)


# e-mail address entity, default_attrib is the name of the attribute
# on IPerson which contains the default e-mail address.
e_mail_address_entity = icemac.addressbook.entities.create_entity(
    _(u'e-mail address'), icemac.addressbook.interfaces.IEMailAddress,
    EMailAddress, default_attrib='default_email_address')


@zope.component.adapter(icemac.addressbook.interfaces.IEMailAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def email_address_title(email):
    """Title of an e-mail address."""
    title = _('none')
    if email.email:
        title = email.email
    return title


@grokcore.component.adapter(icemac.addressbook.interfaces.IPerson)
@grokcore.component.implementer(icemac.addressbook.interfaces.IEMailAddress)
def email_address_of_person(person):
    email_entity = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IEMailAddress)
    return getattr(person, email_entity.tagged_values['default_attrib'])


@zope.interface.implementer(
    icemac.addressbook.interfaces.IHomePageAddress,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
)
class HomePageAddress(persistent.Persistent,
                      zope.container.contained.Contained):
    """A home page address."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IHomePageAddress)


# home page address entity, default_attrib is the name of the attribute
# on IPerson which contains the default home page address.
home_page_address_entity = icemac.addressbook.entities.create_entity(
    _(u'home page address'), icemac.addressbook.interfaces.IHomePageAddress,
    HomePageAddress, default_attrib='default_home_page_address')


@zope.component.adapter(icemac.addressbook.interfaces.IHomePageAddress)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def home_page_address_title(hp):
    """Title of a home page address."""
    title = _('none')
    if hp.url:
        title = six.text_type(hp.url)
    return title


@zope.interface.implementer(
    icemac.addressbook.interfaces.IPhoneNumber,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
)
class PhoneNumber(persistent.Persistent,
                  zope.container.contained.Contained):
    """A phone number."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IPhoneNumber)


# phone number entity, default_attrib is the name of the attribute
# on IPerson which contains the default phone number.
phone_number_entity = icemac.addressbook.entities.create_entity(
    _(u'phone number'), icemac.addressbook.interfaces.IPhoneNumber,
    PhoneNumber, default_attrib='default_phone_number')


@zope.component.adapter(icemac.addressbook.interfaces.IPhoneNumber)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def phone_number_title(tel):
    """Title of a phone number."""
    title = _('none')
    if tel.number:
        title = tel.number
    return title


def normalize_phone_number(number, country_code):
    """Normalize a phone number to E.123 notation (but without spaces).

    See: http://de.wikipedia.org/wiki/E.123

    """
    digits = ''.join(x for x in number if x.isdigit())
    if digits.startswith('00'):
        # old writing of numbers abroad
        return digits.replace('00', '+', 1)
    if not country_code:
        # without country_code no further normalization is possible
        return digits
    if digits.startswith('0'):
        # normalize numbers without country code
        return digits.replace('0', country_code, 1)
    return '+' + digits


def default_attrib_name_to_entity(default_attrib_name):
    """Convert name of a default attrib to the entity where it is defined on"""
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities).getEntities(sorted=False)
    for candidate in entities:
        candidate_default_attrib = candidate.tagged_values.get(
            'default_attrib')
        if candidate_default_attrib == default_attrib_name:
            return candidate
    raise ValueError("Unknown default_attrib_name: %r" % default_attrib_name)
