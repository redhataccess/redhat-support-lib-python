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

from M2Crypto import httpslib

class RSLProxyHTTPSConnection(httpslib.ProxyHTTPSConnection):
    # There are tweaks we need to do for ProxyHTTPSconnection to ensure
    # success.


    def _get_connect_msg(self):
        """ Return an HTTP CONNECT request to send to the proxy. """
        port = int(self._real_port)
        msg = "CONNECT %s:%d HTTP/1.1\r\n" % (self._real_host, port)
        msg = msg + "Host: %s:%d\r\n" % (self._real_host, port)
        if self._proxy_UA:
            msg = msg + "%s: %s\r\n" % (self._UA_HEADER, self._proxy_UA)
        if self._proxy_auth:
            msg = msg + "%s: %s\r\n" % (self._AUTH_HEADER, self._proxy_auth)
        msg = msg + "\r\n"
        return msg
