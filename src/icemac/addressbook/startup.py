from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
import code
import os
import sys
import zdaemon.zdctl
import zope.app.debug
import zope.app.wsgi
import zope.app.wsgi.interfaces
zope.event


def application_factory(global_conf, conf='zope.conf', db=None,
                        requestFactory=HTTPPublicationRequestFactory,
                        handle_errors=True):
    """Application Factory, mainly copyied from
       zope.app.wsgi.getWSGIApplication, but added the ability to do the set up
       done in zope.conf from outside.

    """
    if db is None:
        zope_conf = os.path.join(global_conf['here'], conf)
        db = zope.app.wsgi.config(zope_conf)
    application = zope.app.wsgi.WSGIPublisherApplication(
        db, requestFactory, handle_errors)

    # Create the application, notify subscribers.
    zope.event.notify(
        zope.app.wsgi.interfaces.WSGIPublisherApplicationCreated(application))

    return application


def interactive_debug_prompt(zope_conf='zope.conf'):
    db = zope.app.wsgi.config(zope_conf)
    debugger = zope.app.debug.Debugger.fromDatabase(db)
    # Invoke an interactive interpreter shell
    banner = ("Welcome to the interactive debug prompt.\n"
              "The 'root' variable contains the ZODB root folder.\n"
              "The 'app' variable contains the Debugger, 'app.publish(path)' "
              "simulates a request.")
    code.interact(banner=banner, local={'debugger': debugger,
                                        'app':      debugger,
                                        'root':     debugger.root()})


class ControllerCommands(zdaemon.zdctl.ZDCmd):

    def do_debug(self, rest):
        interactive_debug_prompt()

    def help_debug(self):
        print "debug -- Initialize the application, providing a debugger"
        print "         object at an interactive Python prompt."


def zdaemon_controller(zdaemon_conf='zdaemon.conf'):
    args = ['-C', zdaemon_conf] + sys.argv[1:]
    zdaemon.zdctl.main(args, options=None, cmdclass=ControllerCommands)


def zdaemon_controller_debug_ajax():
    zdaemon_controller('zdaemon-debug-ajax.conf')


def zdaemon_controller_debug_pdb():
    zdaemon_controller('zdaemon-debug-pdb.conf')
