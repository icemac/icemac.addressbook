from __future__ import print_function
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
import fanstatic
import os
import zope.app.wsgi
import zope.app.wsgi.interfaces
import zope.event

IGNORED = None
HANDLE_ERRORS = bool(int(os.environ.get('HANDLE_ERRORS', 1)))


def zope_application_factory(
        global_conf=None, requestFactory=HTTPPublicationRequestFactory):
    """Create a Zope application."""
    if global_conf is None:
        db = None
    else:  # pragma: no cover (not testable)
        zope_conf = os.path.join(global_conf['here'], 'zope.conf')
        db = zope.app.wsgi.config(zope_conf)
    application = zope.app.wsgi.WSGIPublisherApplication(
        db, factory=requestFactory, handle_errors=HANDLE_ERRORS)
    return application


def application_factory(global_conf=None, zope_application=None):
    """Create an address book application with all WSGI middle wares.

    The concept and initial implementation came from
    `zope.app.wsgi.getWSGIApplication`.

    """
    if zope_application is None:  # pragma: no cover (not testable)
        zope_application = zope_application_factory(global_conf)
    application = fanstatic.make_fanstatic(
        zope_application, IGNORED, bottom=True, versioning=True,
        recompute_hashes=False)

    # Create the application, notify subscribers.
    zope.event.notify(
        zope.app.wsgi.interfaces.WSGIPublisherApplicationCreated(application))

    return application
