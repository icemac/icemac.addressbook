==================
icemac.addressbook
==================

*Purpose:* Store, search and export addresses and phone numbers using
a web application.

*Status:* version used in production but still missing some functionality
(See `To do`_)

.. contents::

========
Features
========

General
=======

- multi-client capability

- user and role management

- Completely translated into German, and easily translateable into
  other languages.

- Optimized for the following browsers: Firefox, Safari. IE works but might
  look ugly. (Mobile version of Safari has some glitches.)

Data
====

- store data of persons including postal address, e-mail address,
  home page address, phone number and files

- add data fields to persons and addresses using the user interface

- ability to change the oder of the fields of persons and adresses

- assign keywords to persons

- import data from XLS (Excel) or CSV files

Search & Export
===============

- search for persons by keywords and names

- export persons found using a search as XLS file

- update a single field of multiple persons as returned by a search
  (multi-update)

Technical
=========

- really good test coverage of program code (> 98 %)

- data storage is an object database (ZODB) so no additional database is
  required

===========
Screenshots
===========

See SourceForge_.

.. _SourceForge : https://sourceforge.net/projects/icemac/#screenshots

=======
Hacking
=======

Fork me on: https://bitbucket.org/icemac/icemac.addressbook

.. image:: https://secure.travis-ci.org/icemac/icemac.addressbook.png
   :target: https://travis-ci.org/icemac/icemac.addressbook

See `Source installation`_, too.