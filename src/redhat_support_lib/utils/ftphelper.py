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
import redhat_support_lib.utils.confighelper as confighelper
import redhat_support_lib.utils.reporthelper as reporthelper
from redhat_support_lib.web.connection import Connection
from ftplib import FTP
import base64
import tempfile
import datetime
import gzip
import logging
import os.path
import shutil
import sys

logger = logging.getLogger("redhat_support_lib.utils.ftphelper")

__author__ = 'Spenser Shumaker sshumake@redhat.com'
__author__ = 'Keith Robertson kroberts@redhat.com'


def ftp_attachment(fileName=None, caseNumber=None, fileChunk=None):

    config = confighelper.get_config_helper()

    if not fileName:
        raise Exception('ftp_file(%s) cannot be empty.' % fileName)
    logger.debug("Creating connection to FTP server %s" % config.ftp_host)
    if not caseNumber:
        caseNumber = 'RHST-upload'

    conn = None
    ftp = None
    fh = None
    # add http to host because if it is not prefixed it defaults to https
    try:
        if config.proxy_url != None:
            conn = Connection(url="http://" + config.ftp_host,
                                         manager=None,
                                         key_file=config.key_file,
                                         cert_file=config.cert_file,
                                         timeout=config.timeout,
                                         username=config.ftp_user,
                                         password=config.ftp_pass,
                                         proxy_url=config.proxy_url,
                                         proxy_user=config.proxy_user,
                                         proxy_pass=config.proxy_pass,
                                         debug=config.http_debug)
            httpconnection = conn.getConnection()

            hdr = {'Host': config.ftp_host,
                   'Proxy-Connection': 'Keep-Alive',
                   'Accept': 'application/xml'}
            if config.proxy_user and config.proxy_pass:
                auth = base64.encodestring("%s:%s" % \
                                           (config.proxy_user,
                                            config.proxy_pass)).strip()
                hdr['Proxy-authorization'] = "Basic %s" % auth
            # Critical step.  Proxy must know where to go.
            if sys.version_info[:2] == (2, 6):
                httpconnection._set_tunnel(config.ftp_host,
                                config.ftp_port,
                                hdr)
            else:
                httpconnection.set_tunnel(config.ftp_host,
                                config.ftp_port,
                                hdr)
            httpconnection.connect()

            ftp = FTP()
            ftp.host = config.ftp_host
            ftp.sock = httpconnection.sock
            ftp.af = ftp.sock.family
            ftp.file = ftp.sock.makefile('rb')
            ftp.welcome = ftp.getresp()
            ftp.login(user=config.ftp_user, passwd=config.ftp_pass)
        else:
            ftp = FTP(host=config.ftp_host, user=config.ftp_user,
                                            passwd=config.ftp_pass)
            ftp.login()
        if config.ftp_dir:
            ftp.cwd(config.ftp_dir)
        fh = open(fileName, 'rb')
        if fileChunk:
            fileSize = os.path.getsize(fileName)
            while fh.tell() < fileSize:
                chunkName = ("%s-%s.%03d" % (caseNumber,
                              os.path.basename(fileName), fileChunk['num']))
                fileChunk['names'].append(chunkName)
                logger.debug("Sending file %s over FTP" % chunkName)
                resp = _ftp_storbinary_chunk(ftp, 'STOR %s' % chunkName, fh,
                                             fileChunk['size'])
                if _ftp_error_return_code(resp):
                    raise Exception(resp)
                fileChunk['num'] += 1
        else:
            logger.debug("Sending file %s over FTP" % fileName)
            resp = ftp.storbinary('STOR %s-%s' % 
                                 (caseNumber, os.path.basename(fileName)), fh)
            if _ftp_error_return_code(resp):
                raise Exception(resp)
    finally:
        if fh: fh.close()
        if config.proxy_url != None:
            if conn: conn.close()
        else:
            if ftp: ftp.close()
    return resp


def _ftp_storbinary_chunk(ftpobj, cmd, fp, chunksize):
    """Replacement for ftplib.storbinary that sends only a single file chunk,
    representing a separate file on dropbox, then closes the connection
    """
    ftpobj.voidcmd('TYPE I')
    conn = ftpobj.transfercmd(cmd)
    conn.sendall(fp.read(chunksize))
    conn.close()
    return ftpobj.voidresp()


def _ftp_error_return_code(code):
    # True if FTP return code is 4xx or 5xx signifying an error
    if code[0] in '45':
        return True
    return False


def compress_attachment(fileName):
    try:
        try:
            tmp_dir = tempfile.mkdtemp()
            gzipName = "%s/%s.gz" % (tmp_dir, os.path.basename(fileName))
            gzf = gzip.open(gzipName, 'w+')
            f = open(fileName, 'rb')
            gzf.writelines(f)
        except Exception, e:
            err = ("Failed.\nERROR: unable to compress attachment.  Reason: %s" % e)
            print err
            logger.log(logging.ERROR, err)
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
            return None
        return gzipName
    finally:
        f.close()
        gzf.close()


def is_compressed_file(fileName):
    file_type = reporthelper.get_file_type(fileName)
    for compressed_type in ['zip', 'x-xz', 'x-rar']:
        if compressed_type in file_type:
            return True
    return False

