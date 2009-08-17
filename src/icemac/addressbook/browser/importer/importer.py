# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.address
import icemac.addressbook.browser.file.file
import icemac.addressbook.browser.table
import icemac.addressbook.file.interfaces
import icemac.addressbook.importer.interfaces
import icemac.addressbook.importer.readers.base
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.sources
import persistent.mapping
import xml.sax.saxutils
import z3c.form.button
import z3c.form.datamanager
import z3c.form.field
import z3c.form.interfaces
import z3c.formui.form
import z3c.wizard.wizard
import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import zope.component
import zope.event
import zope.interface
import zope.lifecycleevent
import zope.schema
import zope.security.proxy
import zope.session.interfaces
import zope.traversing.api
import zope.traversing.browser.absoluteurl


class Overview(icemac.addressbook.browser.table.PageletTable):

    no_rows_message = _(
        u'No import files uploaded, yet.')

    def setUpColumns(self):
        return [
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TitleLinkColumn,
                'file', weight=1),
            z3c.table.column.addColumn(
                self, z3c.table.column.GetAttrColumn, 'mimeType', weight=2,
                header=_(u'MIME type'), attrName='mimeType'),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.TruncatedContentColumn,
                'notes', weight=3,
                header=_(u'Notes'), attrName='notes', length=50),
#             z3c.table.column.addColumn(
#                 self, z3c.table.column.CreatedColumn,
#                 'created', weight=4),
#             z3c.table.column.addColumn(
#                 self, z3c.table.column.ModifiedColumn,
#                 'created', weight=5),
            z3c.table.column.addColumn(
                self, icemac.addressbook.browser.table.DeleteLinkColumn,
                'delete', weigth=6),
            z3c.table.column.addColumn(
                self, z3c.table.column.LinkColumn, 'import', weight=200,
                header=_(u''), linkContent=_(u'Import'),
                linkName='@@import'),
            ]

    @property
    def values(self):
        return self.context.values()


class ImportWizard(z3c.wizard.wizard.Wizard):

    label = _(u'Import Wizard')

    def setUpSteps(self):
        return [
            z3c.wizard.step.addStep(self, 'editFile', weight=1),
            z3c.wizard.step.addStep(self, 'reader', weight=2),
            z3c.wizard.step.addStep(self, 'map', weight=3),
            z3c.wizard.step.addStep(self, 'review', weight=4),
            z3c.wizard.step.addStep(self, 'complete', weight=5),
            ]


class FileSession(persistent.mapping.PersistentMapping):
    "Session of an import file."

    file = None


@zope.component.adapter(FileSession)
@zope.interface.implementer(icemac.addressbook.importer.interfaces.IImportFile)
def file_session_to_import_file(file_session):
    """Get the import file of its session."""
    return file_session.file


def get_file_session(file, request):
    "Get the session associated with the file."
    session = zope.session.interfaces.ISession(request)[
        icemac.addressbook.interfaces.PACKAGE_ID]
    key = 'import_%s' % file.__name__
    file_session = session.get(key, None)
    if file_session is None:
        file_session = FileSession()
        file_session.file = zope.security.proxy.removeSecurityProxy(file)
        session[key] = file_session
    return file_session


class Step(z3c.wizard.step.Step):

    @property
    def fields(self):
        return z3c.form.field.Fields(self.interface)


class EditFile(Step):

    interface = icemac.addressbook.file.interfaces.IFile
    label = _(u'Edit import file')

    @property
    def available(self):
        return get_file_session(self.context,
                                self.request).get('edit_file_available', False)

    def applyChanges(self, data):
        super(EditFile, self).applyChanges(data)
        icemac.addressbook.browser.file.file.update_blob(
            self.widgets['data'], self.context)


class IReadersList(zope.interface.Interface):
    "A list of import readers which are able to read the file."

    reader = zope.schema.Choice(
        title=_(u'Import file reader'),
        source=icemac.addressbook.importer.readers.base.Source())


class FileSessionStorageStep(Step):
    "Step which stores its data in file's session."

    def getContent(self):
        return get_file_session(self.context, self.request)


class ChooseReader(FileSessionStorageStep):

    interface = IReadersList
    label = _(u'Choose reader')

    def update(self):
        super(ChooseReader, self).update()
        # XXX delete session contents, wenn file nicht identisch

    @property
    def showBackButton(self):
        """Back button condition."""
        return True

    def doBack(self, action):
        """Process back action and return True on sucess."""
        self.getContent()['edit_file_available'] = True
        return super(ChooseReader, self).doBack(action)



person_mapping = dict(interface=icemac.addressbook.interfaces.IPerson,
                      title=u'person',
                      prefix='person',
                      class_=icemac.addressbook.person.Person)
import_mapping =  (person_mapping,) + icemac.addressbook.address.address_mapping


def getImportMappingRowForPrefix(prefix):
    for row in import_mapping:
        if prefix == row['prefix']:
            return row


def getImportMappingRowForInterface(interface):
    for row in import_mapping:
        if interface == row['interface']:
            return row


class ImportFields(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    "Where to put the imported data in the addressbook."

    def getValues(self, context):
        return xrange(len(get_reader(context).getFieldNames()))

    def getTitle(self, context, value):
        reader = get_reader(context)
        field_name = reader.getFieldNames()[value]
        samples = u', '.join(x for x in reader.getFieldSamples(field_name) if x)
        title = field_name
        if samples:
            title = '%s (%s)' % (field_name, samples)
        return title

import_fields = ImportFields()


def get_reader(session):
    reader_name = session['reader']
    reader = zope.component.getAdapter(
        None,
        icemac.addressbook.importer.interfaces.IImportFileReader,
        name=reader_name)
    file = zope.security.proxy.removeSecurityProxy(session.file.openDetached())
    return reader.open(file)


class ImportObjectBuilder(object):
    """Build the objects the user wants to import."""

    def __init__(self, user_data, address_book):
        """Expects a mapping between name of the field in the address book and
        (pseudo) field index in import file and
        .

        Example: person.first_name --> field_0
                 homepage.notes --> field_11

        Stores the address book field names in dictionaries on
        attributes mapping to the index in the import file.

        address_book ... address book to create the objects in.

        """
        self.address_book = address_book
        for row in import_mapping:
            setattr(self, row['prefix'], {})
        for field_desc, index in user_data.iteritems():
            if index is None:
                continue # field was not selected for import
            prefix, field_name = field_desc.split('.')
            getattr(self, prefix)[field_name] = index

    def create(self, data):
        """Create an object for data.

        data ... import data row, mapping between field index and value."""
        self.errors = set()
        person = self._create('person', self.address_book, data)
        self._validate(person_mapping['interface'], person)
        for address in icemac.addressbook.address.address_mapping:
            obj = self._create(address['prefix'], person, data)
            # set the created address as default address of its kind
            setattr(person, 'default_'+address['prefix'], obj)
            self._validate(address['interface'], obj)
        return person, sorted(list(self.errors))

    def _create(self, prefix, parent, data):
        # map address book field name to value
        row = getImportMappingRowForPrefix(prefix)
        obj = row['class_']()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

        for field_name, index in getattr(self, prefix).iteritems():
            try:
                setattr(obj, field_name, data[index])
            except zope.interface.Invalid, e:
                self.errors.add(
                    self._render_error(row['interface'], field_name, e))

        icemac.addressbook.utils.add(parent, obj)
        return obj

    def _validate(self, interface, obj):
        for field_name, exc in zope.schema.getValidationErrors(interface, obj):
            self.errors.add(self._render_error(interface, field_name, exc))

    def _render_error(self, interface, field_name, exc):
        obj_title = getImportMappingRowForInterface(interface)['title']
        message = exc.doc()
        if field_name is not None:
            field = interface[field_name]
            field_name = field.title
            if (isinstance(field, zope.schema.Choice) and
                isinstance(exc, zope.schema.interfaces.ConstraintNotSatisfied)):
                message = _(u'Value %s not allowed. Allowed values: %s') % (
                    exc.args[0],
                    ', '.join(str(x)
                              for x in field.source.factory.getValues()))
        return '%s - %s: %s' % (obj_title, field_name, message)


@zope.interface.implementer(icemac.addressbook.interfaces.IAddressBook)
@zope.component.adapter(icemac.addressbook.importer.interfaces.IImportFile)
def importfile_to_addressbook(import_file):
    "Adapt import file to address book."
    return import_file.__parent__.__parent__


def delete_imported_data(self):
    """Delete previously imported data."""
    addressbook = icemac.addressbook.interfaces.IAddressBook(self.context)
    session = self.getContent()
    for id in session.get('imported', []):
        del addressbook[id]
    session['imported'] = []


class FieldsGroup(z3c.form.group.Group):

    def __init__(self, context, request, parent, interface, label, prefix):
        super(FieldsGroup, self).__init__(context, request, parent)
        self.label = label
        self.prefix = prefix
        fields = []
        for field_name in zope.schema.getFieldNamesInOrder(interface):
            field = interface[field_name]
            choice = zope.schema.Choice(
                title=field.title, description=field.description,
                required=False, source=import_fields)
            choice.__name__ = field_name
            fields.append(choice)
        self.fields = z3c.form.field.Fields(*fields, **dict(prefix=prefix))



class MapFields(z3c.form.group.GroupForm, FileSessionStorageStep):
    "Map the fields in the import file to fields in the addressbook."

    label = _(u'Map fields')

    def __init__(self, *args, **kw):
        super(MapFields, self).__init__(*args, **kw)
        session = self.getContent()
        request = self.request
        self.groups = [FieldsGroup(session, request, self, row['interface'],
                                   row['title'], row['prefix'])
                       for row in import_mapping]

    @property
    def fields(self):
        return z3c.form.field.Fields()

    def update(self):
        super(MapFields, self).update()
        FileSessionStorageStep.update(self)
        if not self.nextURL:
            # no redirect to next step, make sure no imported data exists
            delete_imported_data(self)

    def applyChanges(self, data):
        super(MapFields, self).applyChanges(data)
        import_object_builder = ImportObjectBuilder(
            data, icemac.addressbook.interfaces.IAddressBook(self.context))
        session = self.getContent()
        reader = get_reader(session)
        imported = session['imported'] = []
        import_errors = session['import_errors'] = {}
        session['found_errors'] = False
        for data_row in reader:
            obj, errors = import_object_builder.create(data_row)
            imported.append(obj.__name__)
            import_errors[obj.__name__] = errors
            if errors:
                session['found_errors'] = True


class ReviewFields(zope.interface.Interface):

    keep = zope.schema.Choice(title=_(u'Keep imported data?'),
                              source=icemac.addressbook.sources.yes_no_source)


class ImportedTable(icemac.addressbook.browser.table.Table):

    cssClassEven = u'table-even-row'
    cssClassOdd = u'table-odd-row'
    sortOn = None

    def setUpColumns(self):
        cols = []
        weight = 0
        for row in import_mapping:
            fields = zope.schema.getFieldsInOrder(row['interface'])
            first = True
            for field_name, field in fields:
                weight += 1
                if first:
                    header = '<i>%s</i><br />%s' % (
                        row['title'], field.title)
                    first = False
                else:
                    header = '<br />%s' % field.title
                cols.append(self._create_col(
                        row['prefix'], field_name, weight, header))
        return cols

    def renderRow(self, row, cssClass=None):
        rendered_row = super(ImportedTable, self).renderRow(row, cssClass)
        if not row:
            return rendered_row
        return u'\n'.join((rendered_row,
                           self._renderErrors(row[0][0], cssClass)))

    def _create_col(self, prefix, field_name, weight, header):
        "Create a single column according to `prefix` and `field_name`."
        kwargs = {}
        if prefix == 'person':
            column = icemac.addressbook.browser.table.GetAttrColumn
            if field_name == 'keywords':
                column = icemac.addressbook.browser.table.IterableGetAttrColumn
        else:
            column = icemac.addressbook.browser.table.AttrGetAttrColumn
            kwargs['masterAttrName'] = 'default_' + prefix
            if field_name == 'country':
                column = (
                    icemac.addressbook.browser.table.CountryAttrGetAttrColumn)

        return z3c.table.column.addColumn(
            self, column, field_name, weight=weight, header=header,
            attrName=field_name, **kwargs)

    def _renderErrors(self, item, cssClass):
        errors = self.session['import_errors'][item.__name__]
        result = []
        if errors:
            result.extend([u'<tr class="%s">' % cssClass,
                           u'<td colspan="%s">' % len(self.columns),
                           _(u'Errors:'),
                           u'<ul class="errors">'])
            for error in errors:
                result.append(
                    u'<li>%s</li>' % xml.sax.saxutils.escape(unicode(error)))
            result.extend([u'</ul>',
                           u'</td>',
                           u'</tr>'])
        return u'\n'.join(result)



    @property
    def session(self):
        return get_file_session(self.context, self.request)

    @property
    def values(self):
        addressbook = icemac.addressbook.interfaces.IAddressBook(self.context)
        for id in self.session.get('imported', []):
            yield addressbook[id]


class Review(FileSessionStorageStep):

    no_rows_message = _(u'No rows where imported.')
    interface = ReviewFields
    label = _(u'Review imported data')

    def renderImportedTable(self):
        table = ImportedTable(self.context, self.request)
        table.update()
        return table.render()

    def render(self):
        result = super(Review, self).render()
        if self.found_errors:
            # make sure data conatining errors is not stored
            delete_imported_data(self)
        return result

    def applyChanges(self, data):
        super(Review, self).applyChanges(data)
        if not data['keep']:
            delete_imported_data(self)
        return True

    @property
    def found_errors(self):
        """Tells whether there were import errors."""
        return self.getContent().get('found_errors', False)

    @property
    def showNextButton(self):
        """Next button condition."""
        return not self.found_errors


class Complete(z3c.wizard.step.Step):

    label = _(u'Complete')

    def applyChanges(self, data):
        super(Complete, self).applyChanges(data)
        self.wizard.nextURL = zope.traversing.browser.absoluteurl.absoluteURL(
            zope.traversing.api.getParent(self.context), self.request)
