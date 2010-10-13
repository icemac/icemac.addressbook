from icemac.addressbook.i18n import _
import z3c.authviewlet.auth
import z3c.flashmessage.interfaces
import zope.component
import icemac.addressbook.browser.base


class FlashedHTTPAuthenticationLogout(
    z3c.authviewlet.auth.HTTPAuthenticationLogout,
    icemac.addressbook.browser.base.FlashView):
    """HTTPAuthenticationLogout enriched by flash messages."""

    def logout(self, nextURL=None):
        result = super(FlashedHTTPAuthenticationLogout, self).logout(nextURL)
        if result:
            self.send_flash(_('You have been logged out successfully.'))
        return result

