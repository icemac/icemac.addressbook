from icemac.addressbook.i18n import _
from js.cookieconsent import cookieconsent
import json
import os
import zope.i18n
import zope.viewlet.viewlet


class CookieConsentViewlet(zope.viewlet.viewlet.ViewletBase):
    """Configure and render the cookieconsent dialog."""

    def _t(self, message_id):
        return zope.i18n.translate(message_id, context=self.request)

    def update(self):
        cookieconsent.need()
        self.config = {
            "palette": {
                "popup": {
                    "background": "#383b75"
                },
                "button": {
                    "background": "#f1d600"
                }
            },
            "theme": "classic",
            "position": "bottom-right",
            "content": {
                "message": self._t(
                    _("This web application uses a session cookie to"
                      " store the log-in status. It gets deleted when"
                      " closing the browser.")),
                "dismiss": self._t(_("I understand!")),
                "href": None,
                "link": None,
            }
        }
        url = os.environ.get('AB_LINK_DATAPROTECTION_URL', None)
        if url:
            self.config['content']['href'] = url
            self.config['content']['link'] = self._t(_("Read more."))

    def render(self):
        return u'''\
            <script>
                window.addEventListener("load", function(){
                window.cookieconsent.initialise(%s)});
            </script>''' % json.dumps(self.config)
