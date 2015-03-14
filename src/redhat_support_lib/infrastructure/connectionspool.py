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

from Queue import Queue
from redhat_support_lib.web.connection import Connection
import socket
import threading


class ConnectionsPool(object):
    '''
    ConnectionsManager used to manage pool of web connections
    '''
    def __init__(self,
                 url,
                 username,
                 password,
                 key_file=None,
                 cert_file=None,
                 strict=None,
                 # timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 timeout=getattr(socket, '_GLOBAL_DEFAULT_TIMEOUT', object()),
                 count=20,
                 proxy_url=None,
                 proxy_user=None,
                 proxy_pass=None,
                 debug=False,
                 noverify=False,
                 ssl_ca=None):

        self.__free_connections = Queue(0)
        self.__busy_connections = {}

        # self.__plock = thread.allocate_lock()
        # No plock in threading...Is this a problem??
        self.__rlock = threading.RLock()

        self.__url = url

        for _ in range(count):
            self.__free_connections.put(item=Connection(url=url,
                                                        username=username,
                                                        password=password,
                                                        manager=self,
                                                        key_file=key_file,
                                                        cert_file=cert_file,
                                                        strict=strict,
                                                        timeout=timeout,
                                                        proxy_url=proxy_url,
                                                        proxy_user=proxy_user,
                                                        proxy_pass=proxy_pass,
                                                        debug=debug,
                                                        noverify=noverify,
                                                        ssl_ca=ssl_ca))

    def getConnection(self, get_ttl=100):
        try:
            # Can we replace plock with rlock??
            self.__rlock.acquire(True)
            conn = self.__free_connections.get(block=True, timeout=get_ttl)
            self.__busy_connections[conn.get_id()] = conn
            return conn
        finally:
            self.__rlock.release()
#        except Empty, e:
#                self.__extendQueue()
#                return self.getConnection(get_ttl)

#    def __extendQueue(self):
# TODO: add more connections if needed
#        continue

    def _freeResource(self, conn):
        try:
            self.__rlock.acquire(True)
            conn = self.__busy_connections.pop(conn.get_id())
            self.__free_connections.put_nowait(conn)
        finally:
            self.__rlock.release()

    def get_url(self):
        return self.__url
