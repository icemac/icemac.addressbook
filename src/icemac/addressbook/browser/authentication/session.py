from icemac.addressbook.i18n import _
import datetime
import icemac.addressbook.browser.base
import pytz
import z3c.authviewlet.session
import zope.pluggableauth.plugins.session


class FlashedSessionCredentialsPlugin(
        zope.pluggableauth.plugins.session.SessionCredentialsPlugin,
        icemac.addressbook.browser.base.FlashView):
    """SessionCredentialsPlugin with support for flash messages."""

    def challenge(self, request):
        result = super(FlashedSessionCredentialsPlugin,
                       self).challenge(request)
        self.send_flash(
            _('To log-in enter your username and password and submit the '
              'form.'))
        return result


class FlashedSessionCredentialsLoginForm(
        z3c.authviewlet.session.SessionCredentialsLoginForm,
        icemac.addressbook.browser.base.FlashView):
    """SessionCredentialsLoginForm with flash messages."""

    title = _('Login')

    def update(self):
        super(FlashedSessionCredentialsLoginForm, self).update()
        if str(self.request.response.getStatus()).startswith('3'):
            self.send_flash(_('You have been logged-in successfully.'))
            principals = zope.component.getUtility(
                zope.pluggableauth.interfaces.IAuthenticatorPlugin,
                name=u'icemac.addressbook.principals')
            principal = principals.get(self.request.principal.id)
            principal.last_login = pytz.utc.localize(
                datetime.datetime.utcnow())
        elif 'SUBMIT' in self.request:
            self.send_flash(
                _('Login failed. Username and/or password might be wrong.'))
