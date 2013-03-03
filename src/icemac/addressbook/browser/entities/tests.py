import icemac.addressbook.testing
import transaction


class TestFieldOrder(icemac.addressbook.testing.SeleniumTestCase):

    def test_field_movement(self):
        self.login('mgr')
        sel = self.selenium
        sel.open('/ab/++attribute++entities/icemac.addressbook.person.Person')

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
