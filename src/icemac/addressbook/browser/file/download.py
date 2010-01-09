# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import zope.interface
import zope.publisher.interfaces.http
import zope.security.proxy


class Download(object):

    def __call__(self):
        mime_type = self.context.mimeType
        if not mime_type:
            mime_type = 'application/octet-stream'
        self.request.response.setHeader('Content-Type', mime_type)

        self.request.response.setHeader('Content-Length', self.context.size)

        file_name = self.context.name.replace(' ', '_')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename=%s' % file_name)

        return DownloadResult(self.context)


class DownloadResult(object):
    """Result object for a download request."""

    zope.interface.implements(zope.publisher.interfaces.http.IResult)

    def __init__(self, context):
        self._iter = bodyIterator(
            zope.security.proxy.removeSecurityProxy(context.openDetached()))

    def __iter__(self):
        return self._iter


CHUNK_SIZE = 64 * 1024

def bodyIterator(f):
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            f.close()
            raise StopIteration()
        yield chunk
