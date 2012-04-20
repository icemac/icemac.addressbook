import icemac.addressbook.testing
import transaction


class TestFieldOrder(icemac.addressbook.testing.SeleniumTestCase):

    def setUp(self):
        super(TestFieldOrder, self).setUp()
        ab = self.layer['addressbook']
        icemac.addressbook.testing.create_user(
            ab, ab, u'Selenium', u'Tester', u'sel@example.com', '12345678',
            ['Administrator'])
        transaction.commit()

    def test_field_movement(self):
        sel = self.selenium
        sel.open('http://%s/++skin++AddressBook/ab' % self.selenium.server)
        # Login
        sel.type("login", "sel@example.com")
        sel.type("password", "12345678")
        sel.clickAndWait("SUBMIT")
        # Open Masterdata
        sel.clickAndWait("//ul[@id='main-menu']/li[4]/a/span")
        sel.assertLocation(r'regexp:@@masterdata\.html$')
        # Go to entities
        sel.clickAndWait("//div[@id='content']/ul/li[3]/a/span")
        sel.assertLocation(r'regexp:\+\+attribute\+\+entities$')
        # Open fields of person entity
        sel.clickAndWait("//div[@id='content']/table/tbody/tr[2]/td[4]/a")
        sel.assertLocation(r'regexp:icemac\.addressbook\.person\.Person$')

        # Keywords-Field has a language depenend title, we store it here for
        # the assertion of the movement later on
        fieldtitle = sel.getText("//tr[4]/td[1]")

        # The Drag'n'drop commands of selenium don't work so we have to
        # emulate them:
        sel.mouseDownAt("//tr[4]/td[1]", "5,5")
        sel.mouseMoveAt("//tr[2]/td[1]", "5,5")
        sel.mouseUpAt("//tr[1]/td[1]", "5,5")
        # The dragged field is stored in the table below the field it was
        # dragged to.
        sel.clickAndWait("entity-fields-save")

        # After saving the position after drag'n'drop was stored.
        self.assertEqual(fieldtitle, sel.getText("//tr[2]/td[1]"))
