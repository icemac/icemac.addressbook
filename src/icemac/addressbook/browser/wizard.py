"""Base classes and functions for wizards."""

import icemac.addressbook.browser.resource
import z3c.form.field
import z3c.wizard.step


class Step(z3c.wizard.step.Step):
    """Customized wizard step which (easier to use)."""

    def update(self):
        icemac.addressbook.browser.resource.form_css.need()
        super(Step, self).update()

    @property
    def fields(self):
        return z3c.form.field.Fields(self.interface)
