# -*- coding: utf-8 -*-

#
# Copyright (c) 2012 Red Hat, Inc.
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

__author__ = 'Spenser Shumaker <sshumake@redhat.com>'
_config_helper = None


class EmptyValueError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class ConfigHelper(object):

    def __init__(self,
                 username=None,
                 password=None,
                 url=None,
                 key_file=None,
                 cert_file=None,
                 proxy_url=None,
                 proxy_user=None,
                 proxy_pass=None,
                 ftp_host='dropbox.redhat.com',
                 ftp_port=None,
                 ftp_user=None,
                 ftp_pass=None,
                 ftp_dir='/incoming',
                 timeout=None,
                 userAgent=None,
                 http_debug=False,
                 no_verify_ssl=False,
                 ssl_ca=None):
        self.username = username
        self.password = password
        self.url = url
        self.key_file = key_file
        self.cert_file = cert_file
        self.proxy_url = proxy_url
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.ftp_host = ftp_host
        self.ftp_port = ftp_port
        self.ftp_user = ftp_user
        self.ftp_pass = ftp_pass
        self.ftp_dir = ftp_dir
        self.timeout = timeout
        self.userAgent = userAgent
        self.http_debug = http_debug
        self.attachment_max_size = 1 * 1024 * 1024 * 1024 # 1GB
        self.no_verify_ssl = no_verify_ssl
        self.ssl_ca = ssl_ca


def get_config_helper():
    '''
    A helper method to get the configuration object.
    '''
    # Tell python we want the *global* version and not a
    # function local version. Sheesh. :(
    global _config_helper
    if not _config_helper:
        _config_helper = ConfigHelper()
    return _config_helper

