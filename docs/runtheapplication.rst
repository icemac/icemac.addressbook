.. _runtheapplication:

===================
Run the application
===================

Running the application is quite independent from your chosen installation
method.

The application is started and controlled by Supervisor_.
During the installation a `crontab` entry is generated which starts Supervisor_
at reboot of the machine the address book was installed on.

To start Supervisor and all application processes by hand call::

  $ bin/svd

To see which application processes are running call::

  $ bin/svctl status

To stop the application and Supervisor call::

  $ bin/svctl shutdown

The next step is to :ref:`loginintotheapplication`.

.. _Supervisor : http://www.supervisord.org
