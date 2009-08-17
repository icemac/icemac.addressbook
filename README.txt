==================
icemac.addressbook
==================

*Purpose:* Store, search and export addresses and phone numbers using
a web application.

*Status:* working prototype (preview of the real application)

.. contents::

Features
========

- store data of persons including (postal address, e-mail address,
  home page address, phone number and files)

- assign keywords to persons

- search for persons by keyword

- export persons found using a search as XLS file

- multi-client capability

- user and role management

- really good test coverage (> 98 %)

User management
===============

Roles
-----

Access to the address book is only granted after authentication. There
are three roles to authorize a user:

- visitor: visit all person's data, search and export, change own
  password

- editor: permissions of visitor + edit all person's data, change own
  log-in name

- administrator: permissions of editor + create and change address
  book and users

Create new users
----------------

Users are persons from the addressbook augmented by log-in
information.

To create the first new user inside an addressbook the adminstrator
(who was created in Install_) has to log-in and then do the following:

  1. create a new person with an e-mail address using `Add person`.

  2. create a new user using `Master data --> Users --> Add user`.

The newly created user has now a log-in (e-mail address) for the
addressbook the person belonges to.