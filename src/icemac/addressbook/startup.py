from __future__ import print_function
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
import code
import fanstatic
import os
import sys
import zdaemon.zdctl
import zope.app.debug
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


def interactive_debug_prompt(zope_conf='zope.conf'):  # pragma: no cover
    db = zope.app.wsgi.config(zope_conf)
    debugger = zope.app.debug.Debugger.fromDatabase(db)
    # Invoke an interactive interpreter shell
    banner = ("Welcome to the interactive debug prompt.\n"
              "The 'root' variable contains the ZODB root folder.\n"
              "The 'app' variable contains the Debugger, 'app.publish(path)' "
              "simulates a request.")
    code.interact(banner=banner, local={
        'debugger': debugger, 'app': debugger, 'root': debugger.root()})


class ControllerCommands(zdaemon.zdctl.ZDCmd):  # pragma: no cover

    def do_debug(self, rest):
        interactive_debug_prompt()

    def help_debug(self):
        print("debug -- Initialize the application, providing a debugger")
        print("         object at an interactive Python prompt.")


def zdaemon_controller(zdaemon_conf='zdaemon.conf'):  # pragma: no cover
    args = ['-C', zdaemon_conf] + sys.argv[1:]
    zdaemon.zdctl.main(args, options=None, cmdclass=ControllerCommands)
