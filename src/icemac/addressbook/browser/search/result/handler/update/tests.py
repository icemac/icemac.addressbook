import icemac.addressbook.browser.testing
import icemac.addressbook.testing
import unittest


class TestOnlyAdminIsAllowedToUseUpdate(unittest.TestCase):

    def test_editor_is_not_able_to_see_update_search_result_handler(self):
        self.fail('nyi')

    def test_editor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.fail('nyi')

    def test_visitor_is_not_able_to_see_update_search_result_handler(self):
        self.fail('nyi')

    def test_visitor_is_not_able_to_access_update_search_result_handler(self):
        # even though he knows the url
        self.fail('nyi')


class Test_update_persons(unittest.TestCase):
    """Testing .base.update_persons."""

    def test_update_persons_updates_only_specified_field(self):
        from icemac.addressbook.person import Person, person_entity
        from .base import update_persons
        person1 = Person()
        person1.notes = u'p1'
        person2 = Person()
        person2.notes = u'p2'
        update_persons((person1, person2), person_entity,
                       person_entity.getRawField('notes'), lambda a,b: a+b,
                       u'bar')
        self.assertEqual('p1bar', person1.notes)
        self.assertEqual('p2bar', person2.notes)
        # no other attributes are in vars as they are not changed (only the
        # private container attributes are additionally here).
        self.assertEqual(
            ['notes', '_BTreeContainer__len', '_SampleContainer__data'],
            vars(person1).keys())


def test_suite():
    suite = icemac.addressbook.testing.DocFileSuite(
        "update.txt",
        package="icemac.addressbook.browser.search.result.handler.update",
        layer=icemac.addressbook.browser.testing.WSGI_SEARCH_LAYER
        )
    suite.addTest(unittest.makeSuite(TestOnlyAdminIsAllowedToUseUpdate))
    suite.addTest(unittest.makeSuite(Test_update_persons))
    return suite
