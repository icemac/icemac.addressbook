===========================
Manual package installation
===========================

Follow these steps if you want to install the pre-packaged address book
manually.

.. note::

    ``icemac.addressbook`` cannot be installed using ``easy_install`` or
    ``pip``, you have to follow these simple steps.

.. warning::

    This installation method is deprecated and will be removed in the next
    major version of ``icemac.addressbook``.

    Switch to :ref:`package-installation` now as described in
    :ref:`upgrade-to-guided-installation`.


Neither you need any root privileges nor it installs anything outside its directory.

#. Create a `virtualenv` using::

   $ virtualenv-2.7 addressbook

#. Download the source distribution (`*.tar.gz`) from PyPI_.

#. Extract the downloaded file into `addressbook` directory created in step 1.

#. Switch to the extracted directory using ``cd``.

#. Run ``install.py`` using the Python binary of the `virtualenv`::

   $ ../bin/python2.7 install.py

#. Answer the questions about admin user name, password and so on.

#. :ref:`runthetests`

#. :ref:`runtheapplication`

.. _PyPI : https://pypi.org/project/icemac.addressbook/#files
