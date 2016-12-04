from icemac.addressbook.i18n import _
import z3c.authviewlet.auth
import icemac.addressbook.browser.base


class FlashedHTTPAuthenticationLogout(
        z3c.authviewlet.auth.HTTPAuthenticationLogout,
        icemac.addressbook.browser.base.FlashView):
    """HTTPAuthenticationLogout enriched by flash messages."""

    def logout(self, nextURL=None):
        result = super(FlashedHTTPAuthenticationLogout, self).logout(nextURL)
        self.send_flash(_('You have been logged out successfully.'))
        return result
