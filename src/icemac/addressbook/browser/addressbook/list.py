# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.interfaces

class PersonList(object):

    def values(self):
        return sorted(self.context.values(),
                      key=lambda x: icemac.addressbook.interfaces.ITitle(x))
