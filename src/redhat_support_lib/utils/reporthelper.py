#!/usr/bin/python
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
from redhat_support_lib.xml import report as report
import StringIO
import datetime
import dateutil.tz as tz
import logging
import os
import platform
import re as re
import shutil
import subprocess
import sys
import tarfile
import tempfile

logger = logging.getLogger("redhat_support_lib.utils.reporthelper")

__author__ = 'Tim Walsh tdwalsh@redhat.com'
__author__ = 'Keith Robertson kroberts@redhat.com'

# specify the max size of a file that can
# be included by value in the xml file
# before it is included as a href
MAX_FILE_SIZE_BYTES = 300000


def rpm_for_file(fileName):
    """
    Find the rpm name that provides a specific file.

    fileName -- Find the rpm package that supplies this file.

    Equivalent to

    rpm -qf /etc/passwd

    setup-2.8.48-1.fc17
    """
    rpmName = None
    try:
        import rpm
        ts = rpm.TransactionSet()
        # loop headers to build package name
        fileName = os.path.abspath(fileName)
        origFileName = fileName
        while not rpmName:
            headers = ts.dbMatch('basenames', fileName)
            for h in headers:
                rpmName = "%s-%s-%s" % (h['name'], h['version'], h['release'])
                break
            fileName = os.path.dirname(fileName)
            if (len(fileName) <= 1):
                # just in case short circuit
                break
        if not ts.dbMatch('basenames', origFileName):
            return None
    except ImportError:
        pass
    return rpmName


def get_file_type(fileName):
    try:
        proc = subprocess.Popen(['file', '-bi', '--', fileName],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            return str(stdout).rstrip()
        else:
            logger.debug(stderr)
            raise Exception
    except  Exception, e:
        logger.debug('Problem determing file type of %s. Exception: %s' % \
                      (fileName, e))
        return 'application/octet-stream; charset=binary'


def contains_invalid_xml_chars(fileName):
    # BZ967510 - check for certain control chars which are invalid XML
    illegal_xml_chars = \
        re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

    f = open(fileName, 'rb')
    count = os.path.getsize(fileName)
    try:
        while count > 0:
            content = f.read(4096)
            if content is None:
                raise Exception("Problem encountered reading %s" % (fileName))
            count = count - len(content)
            if re.search(illegal_xml_chars, content):
                return True
    finally:
        f.close()

    return False


def _process_file(fileName,
                  report_obj,
                  tar_refs=None,
                  max_file_size=MAX_FILE_SIZE_BYTES,
                  name=None):
    """
    Process a specific fileName as either a value in xml fileName
    or entry in tar fileName
    """
    if not name:
        name = os.path.basename(fileName)
    mtype = get_file_type(fileName)
    if os.path.getsize(fileName) > max_file_size or \
       str(mtype).rfind('charset=binary') >= 0 or \
       contains_invalid_xml_chars(fileName):
        tar_refs.append(fileName)
        report_obj.add_binding(report.binding(name=name,
                                              fileName=fileName,
                                              type_=mtype,
                                              href='content/%s' % \
                                              (os.path.basename(fileName))))
    else:
        # read content from fileName and place into xml
        f = open(fileName, 'rb')
        try:
            content = f.read()
        finally:
            f.close

        # BZ967510 - handle &#.*; chars and nested CDATA sections
        if re.search('[&;<>]', content):
            content = content.replace(']]>',']]]]><![CDATA[>')
            content = u'<![CDATA[%s]]>' % (content.decode('utf-8'))
        try:
            report_obj.add_binding(report.binding(name=name,
                                                  fileName=fileName,
                                                  type_=mtype,
                                                  valueOf_=content))
        except Exception, e:
            print e


def _add_sys_info(report_obj,
                  fileName):
    """
    Add the system specific info to the report object.  Handles the  case where
    these objects are already included via ABRT, in which case the ABRT information
    will not be overwritten.
     report_obj -- The redhat_support_lib.xml.report to which binding should be added.
     fileName   -- The original file or directory supplied by the user.  This will be
                   queried to determine package information.

    Information added:
     - Kernel version
     - Package info
     - Hostname
     - OS Arch
     - OS Release
    """
    info = {'kernel': True,
            'package': True,
            'hostname': True,
            'architecture': True,
            'os_release': True}
    # Step 1: See what is already there.
    bAry = report_obj.get_binding()
    for b in bAry:
        if b.get_name() in info:
            info[b.get_name()] = False

    if info['kernel']:
        report_obj.add_binding(report.binding(name='kernel',
                                              valueOf_=platform.release()))
    if info['package']:
        report_obj.add_binding(report.binding(name='package',
                                              valueOf_=rpm_for_file(fileName)))
    if info['hostname']:
        report_obj.add_binding(report.binding(name='hostname',
                                              valueOf_=platform.node()))
    if info['architecture']:
        report_obj.add_binding(report.binding(name='architecture',
                                              valueOf_=platform.processor()))
    if info['os_release']:
        report_obj.add_binding(report.binding(name='os_release',
                                    valueOf_=str(' ').join(platform.dist())))


def _add_custom(report_obj,
                custom):
    '''
    Add any custom bindings to the content.xml

    report_obj -- The redhat_support_lib.xml.report to which binding should be added.
    custom     -- A dictionary of bindings.  Key will be name and value will
    binding's value.

    e.g.
    <binding name='uid'>500</binding>
    '''
    for i in custom:
        report_obj.add_binding(report.binding(name=i,
                                              valueOf_=custom[i]))


def _write_report_file(report_obj,
                       temp_dir,
                       tar_refs=None):
    '''
     report_obj -- The redhat_support_lib.xml.report to which binding should be added.
     temp_dir   -- A valid directory into which a report file will be placed.
     tar_refs   -- An array of files to be added to the tar.bz2
    '''
    out = None
    content_xml = None
    out_file = None
    try:
        try:
            # Marshal everything into a tar or XML file.
            content_xml = StringIO.StringIO()
            content_xml.write('<?xml version="1.0" ?>' + os.linesep)
            report_obj.export(content_xml,
                              0,
                              namespace_='',
                              namespacedef_='xmlns="http://www.redhat.com/gss/strata"')

            if len(tar_refs) > 0:
                out_file = os.path.join(temp_dir,
                                        'report-%s.tar.bz2' % \
                                        (datetime.datetime.now(
                                tz=tz.tzutc()).strftime("%Y%m%d%H%M%S")))
                out = tarfile.open(out_file, 'w:bz2')
                # Add the descriptor
                info = tarfile.TarInfo(name='content.xml')
                content_xml.seek(0)
                info.size = len(content_xml.buf)
                info.mtime = os.stat(out_file).st_mtime
                out.addfile(tarinfo=info, fileobj=content_xml)
                # Add the files.
                for i in tar_refs:
                    logger.debug('adding %s as %s to %s' % (i,
                                        'content/%s' % (os.path.basename(i)),
                                                                  out_file))
                    out.add(i, arcname='content/%s' % (os.path.basename(i)))
            else:
                out_file = os.path.join(temp_dir,
                                        'report-%s.xml' % \
                                        (datetime.datetime.now(\
                                    tz=tz.tzutc()).strftime("%Y%m%d%H%M%S")))
                out = open(out_file, 'wb')
                out.write(content_xml.getvalue())

        except Exception, e:
            logger.exception(e)
            try:
                logger.debug(
                    "Cleaning up temp directory %s from failed create." % \
                    (temp_dir))
                shutil.rmtree(temp_dir)
            except Exception, e:
                # Nothing to see here move along please
                pass
            raise Exception('Unable to create report file in %s.' % (temp_dir))
    finally:
        if out:
            out.close()
        if content_xml:
            content_xml.close()
    return out_file


def make_report(path=None,
                custom=None,
                max_file_size=MAX_FILE_SIZE_BYTES,
                report_dir=None):
    """
    Make a report.

    A Report is made from a path.  The name and content params allow for customer name/value entry
    into xml.  Typical use is to only use the path name.

    path          -- the file or folder from which a report should be made
    custom        -- A dictionary of bindings.  Key will be name and value will
                     binding's value.
    max_file_size -- The max size (in bytes) of a file  which should be included in content.xml.
    report_dir    -- By default, the generated report file will be placed in a temporary directory
                     created by mkdtemp.  This usually resolves to /tmp; however, if there isn't
                     enough space there you can specify an alternate base dir for temp files.

    Usage:
        Generate report xml with simple name/value binding:
        make_report("kernel", "2.6.32-71.el6.x86_64")

        Generate report xml with a path to process ( /var/spool/abrt/ccpp-2012-07-10-21:30:32-1920 )
        make_report(path="/var/spool/abrt/ccpp-2012-07-10-21:30:32-1920")

    return The path to an XML file or a TGZ depending on the size of 'path'
    """
    tar_refs = []
    temp_dir = None
    rpt = report.report()
    # check path to be included in report
    try:
        # Try to make the temporary directory first.
        temp_dir = tempfile.mkdtemp(dir=report_dir)

        if os.path.isfile(path):
            _process_file(fileName=path,
                          report_obj=rpt,
                          tar_refs=tar_refs,
                          max_file_size=MAX_FILE_SIZE_BYTES,
                          name='description')
        elif os.path.isdir(path):
            p = os.walk(path)
            for root_name, dir_name, file_names in p:
                # process files
                for fn in file_names:
                    _process_file(os.path.join(root_name, fn),
                                  rpt,
                                  tar_refs)
        else:
            # Fail fast.  It is either a file, dir, or none
            raise ValueError('Please supply a valid file or directory to process.')
    except Exception, e:
        logger.debug(e)
        raise Exception('Unable to generate report file.')

    _add_sys_info(rpt, path)
    if custom:
        _add_custom(rpt, custom)
    return _write_report_file(rpt,
                              temp_dir,
                              tar_refs)


if __name__ == '__main__':
    # /var/spool/abrt/ccpp-2012-08-16-11:35:40-5397
    if len(sys.argv) == 2:
        file_name = make_report(path=sys.argv[1])
        print('File is %s' % (file_name))
    else:
        print "Usage: %s /path/to/file-or-dir" % (sys.argv[0])
