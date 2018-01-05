from icemac.addressbook.i18n import _
import z3c.authviewlet.auth
import icemac.addressbook.browser.base


class FlashedHTTPAuthenticationLogout(
        z3c.authviewlet.auth.HTTPAuthenticationLogout,
        icemac.addressbook.browser.base.FlashView):
    """HTTPAuthenticationLogout enriched by flash messages."""

    title = _('logout')

    def logout(self, nextURL=None):
        result = super(FlashedHTTPAuthenticationLogout, self).logout(nextURL)
        self.send_flash(_('You have been logged out successfully.'))
        return result


class LogoutRedirectPagelet(
        z3c.authviewlet.auth.LogoutRedirectPagelet,
        icemac.addressbook.browser.base.FlashView):
    """Pagelet to display logout redirect."""

    title = _('redirect')


class LogoutSuccessPagelet(
        z3c.authviewlet.auth.LogoutSuccessPagelet,
        icemac.addressbook.browser.base.FlashView):
    """Pagelet to display logout success."""

    title = _('successful')
