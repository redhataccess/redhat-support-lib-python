#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from redhat_support_lib.infrastructure.errors import RequestError, \
    ConnectionError
from redhat_support_lib.xml import params
from urlparse import urlparse
import logging
import os
import socket

logger = logging.getLogger("redhat_support_lib.infrastructure.proxy")

class Proxy(object):
    '''
    The proxy to web connection
    '''
    def __init__(self, connections_pool, headers={}):
        """Constructor."""
        self.__connections_pool = connections_pool
        self.headers = headers

    def getConnectionsPool(self):
        return self.__connections_pool

    def get(self, url, headers={}):
        '''
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        return self.request(method='GET', url=url, headers=headers)

    def delete(self, url, body=None, headers={}):
        '''
        Returns a 2 tuple consisting of the response body and the returned
        HTTP headers for inspection.
        '''
        return self.request('DELETE', url, body, headers)

    def update(self, url, body=None, headers={}):
        '''
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        return self.request('PUT', url, body, headers)

    def add(self, url, body=None, headers={}):
        '''
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        return self.request('POST', url, body, headers)

    def action(self, url, body=None, headers={}):
        '''
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        return self.request('POST', url, body, headers)

    def upload(self, url, fileName, fileChunk=None, description=None):
        '''
        Upload a file.
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        conn = self.getConnectionsPool().getConnection()
        try:
            try:
                response = conn.doUpload(url, fileName, fileChunk, description)
                logger.debug("HTTP response status(%s) " % response.status)
                if response.status < 400:
                    res = response.read()
                    logger.debug("response data for %s\n(%s)" % (url, res))

                    headers = response.getheaders()
                    d = {}
                    d.update(headers)
                    uri = d['location']
                    parsed = urlparse(uri)
                    uuid = (os.path.basename(parsed[2]))
                    caseNumber = os.path.basename(os.path.dirname(os.path.dirname(parsed[2])))
                    doc = params.attachment(caseNumber=caseNumber,
                                            uuid=uuid,
                                            uri=uri,
                                            fileName=fileName,
                                            description=description)
                    return (doc , headers)
                else:
                    logger.debug("HTTP status(%s) HTTP reason(%s) HTTP response(%s)" % (response.status, response.reason, response.read()))
                    raise RequestError(response.status, response.reason, response.read())
            except socket.error, e:
                raise ConnectionError, str(e)
        finally:
            conn.close()

    def request(self, method, url, body=None, headers={}):
        '''
        Returns a 2 tuple consisting of the response body as strata.xml.params.* object and the returned
        HTTP headers for inspection.
        '''
        logger.debug("Proxy.request: method(%s) url(%s) body(%s) headers(%s)" % (method, url, body, headers))
        return self.__doRequest(method, \
                                url, \
                                body=body, \
                                headers=headers, \
                                conn=self.getConnectionsPool().getConnection())

    def __doRequest(self, method, url, conn, body=None, headers={}):
        try:
            try:
                headers.update(self.headers)
                response = conn.doRequest(method=method, url=url, body=body,
                                          headers=headers)
                logger.debug("HTTP response status(%s) " % response.status)
                if response.status < 400:
                    res = response.read()
                    logger.debug("XML response data for %s\n(%s)" % (url, res))
                    doc = None
                    if res is not None and res is not '' and res.strip() is not '':
                        doc = params.parseString(res)
                    return (doc , response.getheaders())
                else:
                    logger.debug("HTTP status(%s) HTTP reason(%s) HTTP response(%s)" % (response.status, response.reason, response.read()))
                    raise RequestError(response.status, response.reason, response.read())
            except socket.error, e:
                raise ConnectionError, str(e)
        finally:
            conn.close()

    def get_url(self):
        return self.getConnectionsPool().get_url()

    @staticmethod
    def instance(connections_pool):
        Proxy(connections_pool)
