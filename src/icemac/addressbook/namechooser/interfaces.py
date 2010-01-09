# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import zope.interface

class IDontReuseNames(zope.interface.Interface):
    """Marker interface for container those names are never reused.

    Even when contained objects get deleted their names are _not_ reused.
    """

class INameSuffix(zope.interface.Interface):
    """Suffix to make name in container unique."""

    def __iadd__(value):
        "Increment the suffix by `value`."

    def __unicode__():
        "Convert suffix to unicode."
