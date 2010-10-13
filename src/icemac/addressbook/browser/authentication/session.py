from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import z3c.authviewlet.session
import zope.pluggableauth.plugins.session


class FlashedSessionCredentialsPlugin(
    zope.pluggableauth.plugins.session.SessionCredentialsPlugin,
    icemac.addressbook.browser.base.FlashView):
    """SessionCredentialsPlugin with support for flash messages."""

    def challenge(self, request):
        result = super(FlashedSessionCredentialsPlugin, self).challenge(request)
        if result:
            self.send_flash(
                _('To log-in enter your username and password and submit the '
                  'form.'))
        return result


class FlashedSessionCredentialsLoginForm(
    z3c.authviewlet.session.SessionCredentialsLoginForm,
    icemac.addressbook.browser.base.FlashView):
    """SessionCredentialsLoginForm with flash messages."""

    def update(self):
        super(FlashedSessionCredentialsLoginForm, self).update()
        if str(self.request.response.getStatus()).startswith('3'):
            self.send_flash(_('You have been logged-in successfully.'))
        elif 'SUBMIT' in self.request:
            self.send_flash(
                _('Login failed. Username and/or password might be wrong.'))
