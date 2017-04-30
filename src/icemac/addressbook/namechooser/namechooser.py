import BTrees.Length
import icemac.addressbook.namechooser.interfaces
import persistent
import zope.component
import zope.container.contained
import zope.interface


class NameSuffix(persistent.Persistent, zope.container.contained.Contained):
    """Storage for name suffix."""

    zope.interface.implements(
        icemac.addressbook.namechooser.interfaces.INameSuffix)
    zope.component.adapts(
        icemac.addressbook.namechooser.interfaces.IDontReuseNames)

    def __init__(self):
        self._suffix = BTrees.Length.Length(0)

    def __iadd__(self, value):
        self._suffix.change(value)
        return self

    def __unicode__(self):
        return unicode(self._suffix.value)


name_suffix = zope.annotation.factory(
    NameSuffix, key='icemac.namechooser.DontReuseNames.NameSuffix')


class DontReuseNames(zope.container.contained.NameChooser):
    """NameChooser assuring that the chosen names are unique forever.

    It assures this by storing the last chosen suffix in an annotation on
    the container object.

    When a containers provides
    ``icemac.addressbook.namechooser.interfaces.IDontReuseNames`` this name
    chooser is used. (It also needs to provide
    ``zope.annotation.interfaces.IAttributeAnnotatable`` as the information
    gets stored in an annotation.)
    """

    zope.component.adapts(
        icemac.addressbook.namechooser.interfaces.IDontReuseNames)

    def chooseName(self, name, obj):
        # remove characters that checkName does not allow
        name = unicode(name.replace('/', '-').lstrip('+@'))

        if not name:
            name = unicode(obj.__class__.__name__)

        prefix, dot, extension = name.rpartition('.')
        if prefix:
            extension = dot + extension
        else:
            # There is no dot in the name, so
            prefix = extension
            extension = u''

        name_suffix = self.name_suffix
        while True:
            name_suffix += 1
            chosen_name = u'{prefix}-{suffix}{extension}'.format(
                prefix=prefix, suffix=name_suffix, extension=extension)
            if not self.name_in_use(chosen_name):
                break

        # Make sure the name is valid.  We may have started with something bad.
        self.checkName(chosen_name, obj)

        return chosen_name

    def name_in_use(self, name):
        return name in self.context

    @property
    def name_suffix(self):
        return icemac.addressbook.namechooser.interfaces.INameSuffix(
            self.context)
