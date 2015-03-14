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

'''
The main interface through which you should interact with the Strata API.
'''
from redhat_support_lib.infrastructure import contextmanager
from redhat_support_lib.infrastructure.connectionspool import ConnectionsPool
from redhat_support_lib.infrastructure.proxy import Proxy
from redhat_support_lib.infrastructure.contextmanager import Mode
from redhat_support_lib.infrastructure.brokers import solutions
from redhat_support_lib.infrastructure.brokers import articles
from redhat_support_lib.infrastructure.brokers import cases
from redhat_support_lib.infrastructure.brokers import groups
from redhat_support_lib.infrastructure.brokers import users
from redhat_support_lib.infrastructure.brokers import comments
from redhat_support_lib.infrastructure.brokers import attachments
from redhat_support_lib.infrastructure.brokers import problems
from redhat_support_lib.infrastructure.brokers import entitlements
from redhat_support_lib.infrastructure.brokers import products
from redhat_support_lib.infrastructure.brokers import values
from redhat_support_lib.infrastructure.brokers import InstanceMaker
from redhat_support_lib.infrastructure.brokers import symptoms
from redhat_support_lib.infrastructure.brokers import search
from redhat_support_lib.utils import reporthelper
import redhat_support_lib.utils.confighelper as confighelper
from redhat_support_lib.xml import report
import redhat_support_lib.version as version
import logging


__author__ = 'Keith Robertson <kroberts@redhat.com>'

STREAM_LOG_FORMAT = '%(levelname)s: %(message)s'
USER_AGENT = 'redhat-support-lib-%s' % (version.version)

logger = logging.getLogger("redhat_support_lib.infrastructure.proxy")


class API(object):
    def __init__(self,
                 username,
                 password,
                 url='https://api.access.redhat.com',
                 key_file=None,
                 cert_file=None,
                 proxy_url=None,
                 proxy_user=None,
                 proxy_pass=None,
                 ftp_host='dropbox.redhat.com',
                 ftp_port=21,
                 ftp_user=None,
                 ftp_pass=None,
                 ftp_dir="/incoming",
                 timeout=None,
                 userAgent=None,
                 no_verify_ssl=False,
                 ssl_ca=None):

        """
        Initialize an instance of the Red Hat Support Library

        :param username: User name for Red Hat Customer Portal
        :type username: string
        :param password: Password for Red Hat Customer Portal
        :type password: string
        :param url:
            Strata REST URL (by default this is https://api.access.redhat.com)

        :type url: string
        :param key_file:
            SSL key location for SSL authentication (not implemented)

        :type key_file: string
        :param cert_file:
            SSL certificate location for SSL authentication (not implemented)

        :type cert_file: string
        :param proxy_url: URL for HTTP/HTTPS proxy server (optional)
        :type proxy_url: string
        :param proxy_user: User name for HTTP/HTTPS proxy server (optional)
        :type proxy_user: string
        :param proxy_pass: Password for HTTP/HTTPS proxy server (optional)
        :type proxy_pass: string
        :param timeout: Request timeout (optional)
        :type timeout: string
        :param userAgent: User agent to set for API communications (optional)
        :type userAgent: string
        :param no_verify_ssl: If True, don't verify server identity (optional)
        :type no_verify_ssl: boolean
        :param ssl_ca: Path to an alternative certificate authority to trust
        :type ssl_ca: string/filepath
        :returns: Strata API object
        """

        # Make sure logger is initialized
        if len(logging.getLogger().handlers) == 0:
            logging.basicConfig(level=logging.CRITICAL)
        httpdebug = False
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            httpdebug = True

        self._ua = None
        if userAgent:
            ua = {'User-Agent': userAgent}
        else:
            ua = {'User-Agent': USER_AGENT}
        config = confighelper.get_config_helper()
        config.username = username
        config.password = password
        config.url = url
        config.key_file = key_file
        config.cert_file = cert_file
        config.proxy_url = proxy_url
        config.proxy_user = proxy_user
        config.proxy_pass = proxy_pass
        config.ftp_host = ftp_host
        config.ftp_port = ftp_port
        config.ftp_user = ftp_user
        config.ftp_pass = ftp_pass
        config.ftp_dir = ftp_dir
        config.timeout = timeout
        config.userAgent = ua
        config.http_debug = httpdebug
        config.no_verify_ssl = no_verify_ssl
        config.ssl_ca = ssl_ca
        self.config = config

        contextmanager.add('proxy',
                           Proxy(ConnectionsPool(url=config.url,
                                                 key_file=config.key_file,
                                                 cert_file=config.cert_file,
                                                 timeout=config.timeout,
                                                 username=config.username,
                                                 password=config.password,
                                                 proxy_url=config.proxy_url,
                                                 proxy_user=config.proxy_user,
                                                 proxy_pass=config.proxy_pass,
                                                 debug=config.http_debug,
                                                 noverify=config.no_verify_ssl,
                                                 ssl_ca=config.ssl_ca),
                                 config.userAgent),
                           Mode.R)

        # Initialize the container classes.
        self.solutions = solutions()
        self.articles = articles()
        self.cases = cases()
        self.groups = groups()
        self.users = users()
        self.comments = comments()
        self.attachments = attachments()
        self.problems = problems()
        self.entitlements = entitlements()
        self.products = products()
        self.symptoms = symptoms()
        self.values = values()
        self.search = search()
        self.im = InstanceMaker()

    def disconnect(self):
        ''' terminates server connection/s '''
        contextmanager._remove('proxy', force=True)

    @classmethod
    def make_report(cls,
                    path,
                    custom=None,
                    max_file_size=reporthelper.MAX_FILE_SIZE_BYTES,
                    report_dir=None):
        '''
        A Report file is made from a path which can either be a single file or
        a directory.  The name and content params allow for customer name/value
        entry into xml.  Typical use is to only use the path name.

        :param path: the file or folder from which a report should be made
        :type path: string
        :param custom:
            A dictionary of bindings.  Key will be name and value will
            binding's value.

        :type custom: dict
        :param max_file_size:
            The max size (in bytes) of a file which should be included in
            content.xml.

        :type max_file_size: int
        :param report_dir:
            Path to save the generated report to, a subdirectory will be
            created by :func:`tempfile.mkdtemp`.  This value will be /tmp
            by default.

        :type report_dir: string

        Example:

            .. code-block:: python

                api.make_report("/var/spool/abrt/ccpp-2013-03-15-15:26:39-2202")

        :returns:
            The path to an XML file or a TGZ depending on the size of 'path'

        :rtype: string'''
        return reporthelper.make_report(path,
                                        custom,
                                        max_file_size,
                                        report_dir)

    @classmethod
    def process_report_file(cls,
                            path):
        '''
        A utility function which returns a redhat_support_lib.xml.report object
        given a report file's content.xml.  The report object can then be
        inspected to see what was in the content.xml.

        :param path: A path to a report file's content.xml
        :type path: string

        :returns: A redhat_support_lib.xml.report object
        '''
        return report.parse(path, False)
