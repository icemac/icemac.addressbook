from z3c.form.i18n import MessageFactory as _
import icemac.addressbook.browser.base


class Redirect(icemac.addressbook.browser.base.BaseView):
    """Redirect back to person list"""

    def __call__(self):
        self.send_flash(_('Data successfully updated.'))
        self.request.response.redirect(
            self.url(self.context, 'person-list.html'))
