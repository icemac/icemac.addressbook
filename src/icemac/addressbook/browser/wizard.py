# Copyright (c) 2011-2014 Michael Howitz
# See also LICENSE.txt
"""Base classes and functions for wizards."""

import z3c.form.field
import z3c.wizard.step
import z3c.wizard.wizard


class Step(z3c.wizard.step.Step):
    """Customized wizard step which (easier to use)."""

    @property
    def fields(self):
        return z3c.form.field.Fields(self.interface)


class Wizard(z3c.wizard.wizard.Wizard):
    """Base (customizable) wizard."""
