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
import sys
import base64
import mimetypes
import os
import socket
import time
import urllib
import urlparse
import logging

from httplib import HTTPConnection, BadStatusLine
from M2Crypto import SSL
from M2Crypto.httpslib import HTTPSConnection
from redhat_support_lib.web.proxyhttpsconnection import RSLProxyHTTPSConnection
from redhat_support_lib.infrastructure.errors import RequestError


logger = logging.getLogger("redhat_support_lib.web.connection")


class Connection(object):
    '''
    The strata api connection proxy
    '''
    def __init__(self,
                 url,
                 username,
                 password,
                 manager,
                 key_file=None,
                 cert_file=None,
                 strict=None,
                 # timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 timeout=None,
                 proxy_url=None,
                 proxy_user=None,
                 proxy_pass=None,
                 debug=False,
                 noverify=False,
                 ssl_ca=None):

        self.url = url
        self.username = username
        self.password = password
        self.key_file = key_file
        self.cert_file = cert_file
        self.strict = strict
        self.timeout = timeout
        self.proxy_url = proxy_url
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.debug = debug
        self.noverify = noverify
        self.ssl_ca = ssl_ca

        u = self.__parse_url(url)
        self.url_schema = u[0]
        self.url_host = u[1]
        self.url_port = u[2]
        self.handlerprefix = ''

        if proxy_url:
            purl = self.__parse_url(proxy_url)
            self.proxy_host = purl[1]
            self.proxy_port = purl[2]

        self.__connection = self.__createConnection()
        self.__connection.set_debuglevel(int(debug))
        self.__manager = manager
        self.__id = id(self)

    def get_id(self):
        return self.__id

    def getConnection(self):
        return self.__connection

    def getDefaultHeaders(self):
        return self.__headers.copy()

    def doRequest(self, method, url, body=urllib.urlencode({}), headers={}):
        attempts = 0
        while True:
            try:
                self.__connection.request(method,
                                          self.handlerprefix + url,
                                          body,
                                          self.getHeaders(headers))
                return self.__connection.getresponse()
            except BadStatusLine:
                if attempts == 0:
                    # Try to reset the connection, HTTPS proxying on RHEL5
                    # will trigger this a lot as M2Crypto doesn't support
                    # SSL/TLS Proxy Keep-Alive.
                    # Transient issues may also trigger this on other setups.
                    self.resetConnection()
                    attempts += 1
                    logging.debug(_('Connection socket closed, reconnecting.'))
                else:
                    raise

    def doUpload(self, url, fileName, fileChunk=None, description=None):
        '''Wrapper for _doUpload to handle connection retries'''
        attempts = 0
        while True:
            try:
                self._doUpload(url, fileName, fileChunk, description)
                return self.__connection.getresponse()
            except BadStatusLine:
                if attempts == 0:
                    # Like doRequest, we may need to reset the connection.
                    self.resetConnection()
                    attempts += 1
                    logging.debug(_('Connection socket closed, reconnecting.'))
                else:
                    raise

    def _doUpload(self, url, fileName, fileChunk=None, description=None):
        '''
        Do an upload of a single file to the given URL.
        Keyword arguments:
            url -- The URL to upload to.
            fileName -- An open file handle whose content needs to be sent.
            fileChunk -- Dict describing the chunk of fileName to be sent.
            description -- Optional description of the file.
        '''
        boundary = '----------%x' % time.time()
        fh = None
        try:
            try:
                fh = open(fileName, 'rb')
                fileSize = os.path.getsize(fileName)
                # Loop used for uploading all the chunks of split attachments
                while True:
                    # Compose the head of the form.
                    headFormAry = []
                    if description:
                        headFormAry.append('--' + boundary)
                        headFormAry.append(\
                            'Content-Disposition: form-data; name="description"')
                        headFormAry.append('')
                        headFormAry.append(str(description))
                    headFormAry.append('--' + boundary)
                    if fileChunk:
                        chunkName = ("%s.%03d" % (os.path.basename(fileName),
                                                  fileChunk['num']))
                        fileChunk['names'].append(chunkName)
                        header_filename = chunkName
                    else:
                        header_filename = os.path.basename(fileName)
                    headFormAry.append(\
                        'Content-Disposition: form-data; name="%s"; filename="%s"'\
                        % ('file', header_filename))
                    headFormAry.append('Content-Type: %s' % \
                                       (mimetypes.guess_type(fileName)[0] or \
                                        'application/octet-stream'))
                    headFormAry.append('')
                    headFormAry.append('')
                    headForm = '\r\n'.join(headFormAry)

                    # Compose the tail
                    tailFormAry = []
                    tailFormAry.append('')
                    tailFormAry.append('--' + boundary + '--')
                    tailFormAry.append('')
                    tailForm = '\r\n'.join(tailFormAry)

                    totalLength = len(headForm) + len(tailForm)
                    if fileChunk:
                        totalLength += fileChunk['size']
                    else:
                        totalLength += fileSize

                    # Start sending.
                    if self.proxy_url:
                        self.__connection.putrequest(method='POST',
                                                     url=self.url + url,
                                                     skip_host=1,
                                                     skip_accept_encoding=1)
                    else:
                        self.__connection.putrequest(method='POST',
                                                     url=url,
                                                     skip_host=0,
                                                     skip_accept_encoding=1)

                    hdrDict = self.getHeaders({'Content-Length': str(totalLength),
                    'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                                               'Accept': 'text/plain'})
                    for key, value in hdrDict.items():
                        self.__connection.putheader(key, value)
                    self.__connection.endheaders()
                    self.__connection.send(headForm)
                    if fileChunk:
                        self.__connection.send(fh.read(fileChunk['size']))
                        self.__connection.send(tailForm)
                        if fh.tell() >= fileSize:
                            break
                        else:
                            response = self.__connection.getresponse()
                            response.read()
                            if response.status >= 400:
                                logger.debug("HTTP status(%s) HTTP reason(%s) "
                                             "HTTP response(%s)" %
                                             (response.status, response.reason,
                                              response.read()))
                                raise RequestError(response.status,
                                                   response.reason,
                                                   response.read())
                        fileChunk['num'] += 1
                    else:
                        self.__connection.send(fh.read())
                        self.__connection.send(tailForm)
                        break
            except:
                raise
        finally:
            if fh:
                fh.close()

    def getHeaders(self, headers):
        extended_headers = self.getDefaultHeaders()
        for k in headers.keys():
            if (headers[k] is None and
                extended_headers.has_key(k)):
                extended_headers.pop(k)
            else:
                extended_headers[k] = headers[k]
        return extended_headers

    def setDebugLevel(self, level):
        self.__connection.set_debuglevel(level)

    def setTunnel(self, host, port=None, headers=None):
        self.__connection.set_tunnel(host, port, headers)

    def close(self):
        self.__connection.close()
# FIXME: create connection watchdog to close it on
# idle-ttl expiration, rather than after the call
        if (self.__manager is not None):
            self.__manager._freeResource(self)

    def state(self):
        return self.__connection.__state

    def __parse_url(self, url):
        if not url.startswith('http'):
            url = "https://" + url
        parse = urlparse.urlparse(url)
        hostport = parse[1].rsplit(':')
        ret = [parse[0]]
        if len(hostport) == 2:
            ret.append(hostport[0])
            try:
                ret.append(int(hostport[1]))
            except ValueError:
                ret.append(None)
        else:
            ret.append(parse[1])
            ret.append(None)
        return ret

    def __createConnection(self):

        def makeHTTPSConnection():
            hdr = {}
            conn = None
            context = SSL.Context()

            if self.noverify:
                # User has asked to ignore the results of certificate validity
                # checks, needed for people that use transparent SSL proxies.
                context.set_verify(SSL.verify_none, 9)
            else:
                context.set_verify(SSL.verify_peer, 9)

            if os.access('/etc/pki/tls/certs/ca-bundle.crt', os.R_OK):
                context.load_verify_locations(
                                            '/etc/pki/tls/certs/ca-bundle.crt')

            if self.ssl_ca and os.access(self.ssl_ca, os.R_OK):
                context.load_verify_locations(self.ssl_ca)

            if self.proxy_url:
                conn = RSLProxyHTTPSConnection(self.proxy_host,
                                                self.proxy_port, self.strict,
                                                self.proxy_user,
                                                self.proxy_pass,
                                                ssl_context=context)
                if self.url_port != None:
                    self.handlerprefix = "https://%s:%s" % (self.url_host,
                                                            self.url_port)
                else:
                    self.handlerprefix = "https://%s" % (self.url_host)

            else:
                conn = HTTPSConnection(self.url_host, self.url_port,
                                       self.strict, ssl_context=context)

            return (conn, hdr)

        def makeHTTPConnection():
            hdr = {}
            conn = None

            if self.proxy_url:
                conn = HTTPConnection(self.proxy_host, self.proxy_port,
                                      self.strict)
                if self.url_port != None:
                    self.handlerprefix = "https://%s:%s" % (self.url_host,
                                                            self.url_port)
                else:
                    self.handlerprefix = "https://%s" % (self.url_host)
                hdr['Proxy-Connection'] = 'Keep-Alive'
                if self.proxy_user and self.proxy_pass:
                    auth = base64.encodestring("%s:%s" % (self.proxy_user,
                                                    self.proxy_pass)).strip()
                    hdr['Proxy-authorization'] = "Basic %s" % auth
            else:
                conn = HTTPConnection(self.url_host, self.url_port,
                                      self.strict)

            return (conn, hdr)

        conn = None
        hdr = {}

        if self.url_schema == 'http':
            (conn, hdr) = makeHTTPConnection()
        else:
            (conn, hdr) = makeHTTPSConnection()

        # Create the default set of headers
        self.__headers = self.__createHeaders(hdr)
        return conn

    def __createHeaders(self, defaultheaders):
        auth = base64.encodestring("%s:%s" % (self.username,
                                              self.password)).strip()
        hdrs = {"Accept": "application/xml",
                "Content-Type": "application/xml",
                'Host': self.url_host,
                "Authorization": "Basic %s" % auth}
        hdrs.update(defaultheaders)
        return hdrs

    def resetConnection(self):
        self.close()
        self.__connection == self.__createConnection()

    id = property(get_id, None, None, None)
