========
Features
========

General
=======

- multi-client capability

- user and role management

- Completely translated into German, and easily translatable into
  other languages.

- Optimized for the following browsers: Firefox, Safari.

- Calendar via `icemac.ab.calendar`_.

.. _`icemac.ab.calendar` : https://pypi.org/project/icemac.ab.calendar

Data
====

- store data of persons including postal address, phone number, e-mail address,
  home page address and files

- add custom data fields to persons and addresses in the master data area of
  the web user interface

- change the order of the fields of persons and addresses

- assign keywords to persons

- import data from XLS (Excel) or CSV files (via `icemac.ab.importer`_ resp.
  `icemac.ab.importxls`_)

.. _`icemac.ab.importer` : https://pypi.org/project/icemac.ab.importer)
.. _`icemac.ab.importxls` : https://pypi.org/project/icemac.ab.importxls)

Search & Export
===============

- search for persons by keywords and names

- export persons found using a search as XLS file

- export iCal calender file of the birth dates of persons

- update a single field of multiple persons as returned by a search
  (multi-update)

Technical
=========

- 100 % test coverage of the program code including all possible program
  execution branches

- The data storage is an object database (ZODB); so no additional database is
  required.
