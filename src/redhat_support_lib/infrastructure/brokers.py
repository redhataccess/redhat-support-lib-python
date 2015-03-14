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
Module that brokers the RESTful methods.
'''
from redhat_support_lib.infrastructure.common import Base
from redhat_support_lib.infrastructure.errors import ConnectionError, \
    RequestError
from redhat_support_lib.utils.filterhelper import FilterHelper
from redhat_support_lib.utils.parsehelper import ParseHelper, ReportParseHelper
from redhat_support_lib.utils.searchhelper import SearchHelper
from redhat_support_lib.utils.urlhelper import UrlHelper
from redhat_support_lib.xml import params, report
from urllib import quote
from urlparse import urlparse
from xml.sax.saxutils import escape
import redhat_support_lib.utils.ftphelper as FtpHelper
import redhat_support_lib.utils.confighelper as confighelper
import logging
import mimetypes
import os.path
import socket
import sys
from email.Header import decode_header


logger = logging.getLogger("redhat_support_lib.infrastructure.brokers")

__author__ = 'Keith Robertson <kroberts@redhat.com>'


class solution(params.solution, Base):
    def __init__(self, solution):
        self.superclass = solution

    def __new__(cls, solution):
        if solution is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(solution)
        return obj


    @classmethod
    def fromProps(cls,
                  createdBy=None,
                  title=None,
                  summary=None,
                  kcsState=None,
                  resolution=None,
                  **kwargs):

        issue = kwargs.get('issue', None)
        if issue is not None:
            issue = params.issueType(issue, None)

        resolution = kwargs.get('resolution', None)
        if resolution is not None:
            resolution = params.resolutionType(resolution, None)

        environment = kwargs.get('environment', None)
        if environment is not None:
            environment = params.environmentType(environment, None)

        rootCause = kwargs.get('rootCause', None)
        if rootCause is not None:
            rootCause = params.rootCauseType(rootCause, None)

        internalDiagnosticSteps = kwargs.get('internalDiagnosticSteps', None)
        if internalDiagnosticSteps is not None:
            internalDiagnosticSteps = params.internalDiagnosticStepsType(internalDiagnosticSteps, None)

        tags = kwargs.get('tags', None)
        if tags is not None:
            tags = params.tagType(tags, None)

        duplicateOf = kwargs.get('duplicateOf', None)
        if duplicateOf is not None:
            duplicateOf = params.duplicateOfType(None, duplicateOf)

        psol = params.solution(createdBy=createdBy, title=title,
                               summary=summary, kcsState=kcsState,
                               resolution=resolution, **kwargs)

        return cls(psol)

    def set_issue(self, issue):
        issue = params.issueType(issue, None)
        super(solution, self).set_issue(issue)

    def set_resolution(self, resolution):
        resolution = params.resolutionType(resolution, None)
        super(solution, self).set_resolution(resolution)

    def set_environment(self, environment):
        environment = params.environmentType(environment, None)
        super(solution, self).set_environment(environment)

    def set_rootCause(self, rootCause):
        rootCause = params.rootCauseType(rootCause, None)
        super(solution, self).set_rootCause(rootCause)

    def set_internalDiagnosticSteps(self, internalDiagnosticSteps):
        internalDiagnosticSteps = params.internalDiagnosticStepsType(internalDiagnosticSteps, None)
        super(solution, self).set_internalDiagnosticSteps(internalDiagnosticSteps)

    def set_tag(self, tag):
        tag = params.tagType(tag, None)
        super(solution, self).set_tag(tag)

    def set_duplicateOf(self, duplicateOf):
        duplicateOf = params.duplicateOfType(None, duplicateOf)
        super(solution, self).set_duplicateOf(duplicateOf)

    def update(self):
        '''
        Update this solution. This solution *must* have an ID.

        .. IMPORTANT::
           The solution must already exist on the Red Hat Customer Portal, if
           you are adding a new solution you should use
           :func:`solutions.add` instead

        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/solutions'
        if self.get_id() is not None:
            self._getProxy().update(url=UrlHelper.append(url, self.superclass.get_id()),
                                    body=ParseHelper.toXml(self.superclass))
        else:
            raise RequestError('ID cannot be None on update')


class solutions(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def add(self, sol):
        '''

        Add a new solution

        :param sol: Solution to be added to Customer Portal
        :type sol: solution
        :rtype: solution
        :returns: The solution ID and view_uri will be set if successful.
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/solutions'
        doc, headers = self._getProxy().add(url=url,
                                            body=ParseHelper.toXml(sol))

        d = {}
        d.update(headers)
        view_uri = d['view-uri']
        parsed = urlparse(view_uri)
        sol.set_id(os.path.basename(parsed[2]))
        sol.set_view_uri(view_uri)
        return sol


    def get(self, solutionID=None):
        '''
        Queries the API for the given solution ID.

        :param solutionID: Solution ID to be queried from the API
        :type solutionID: Integer
        :rtype: solution
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/solutions'
        doc, headers = self._getProxy().get(url=UrlHelper.append(url, solutionID))
        sol = solution(doc)
        logger.debug("REST Response:%s" % sol.toXml())
        return sol

    def list(self, keywords=None, **kwargs):
        '''
        Queries the solutions RESTful interface with a given set of keywords.

        :param keywords: Search string
        :type keywords: string
        :param searchopts: search options/query filters passed to the API
        :type searchopts: dict
        :param kwargs:
            Additional options passed to FilterHelper

            Example:

            .. code-block:: python

                solutions.list('RHEV', authorSSOName="anonymous")

        :type kwargs: dict
        :returns: A list of solution objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/solutions'

        # extract searchopts from kwargs, return empty dict if not present
        searchopts = kwargs.pop('searchopts', {})
        searchopts['keyword'] = keywords

        doc, headers = self._getProxy().get(url=SearchHelper.appendQuery(url, searchopts))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(solution,
                                        FilterHelper.filter(doc.get_solution(), kwargs))


class article(params.article, Base):
    def __init__(self, article):
        self.superclass = article

    def __new__(cls, article):
        if article is None: return None
        obj = object.__new__(cls)
        obj.__init__(article)
        return obj


    @classmethod
    def fromProps(cls, createdBy=None, title=None, summary=None, kcsState=None, body=None, **kwargs):

        issue = kwargs.get('issue', None)
        if kwargs.get('issue', None):
            issue = params.issueType(issue, None)

        resolution = kwargs.get('resolution', None)
        if resolution is not None:
            resolution = params.resolutionType(resolution, None)

        environment = kwargs.get('environment', None)
        if environment is not None:
            environment = params.environmentType(environment, None)

        rootCause = kwargs.get('rootCause', None)
        if rootCause is not None:
            rootCause = params.rootCauseType(rootCause, None)

        internalDiagnosticSteps = kwargs.get('internalDiagnosticSteps', None)
        if internalDiagnosticSteps is not None:
            internalDiagnosticSteps = params.internalDiagnosticStepsType(internalDiagnosticSteps, None)

        tag = kwargs.get('tag', None)
        if tag is not None:
            tag = params.tagType(tag, None)

        duplicateOf = kwargs.get('duplicateOf', None)
        if duplicateOf is not None:
            duplicateOf = params.duplicateOfType(None, duplicateOf)

        psol = params.article(createdBy=createdBy, title=title,
                              summary=summary, kcsState=kcsState,
                              body=body, **kwargs)
        return cls(psol)

    def set_issue(self, issue):
        issue = params.issueType(issue, None)
        params.article.set_issue(self, issue)

    def set_resolution(self, resolution):
        resolution = params.resolutionType(resolution, None)
        params.article.set_resolution(self, resolution)

    def set_environment(self, environment):
        environment = params.environmentType(environment, None)
        params.article.set_environment(self, environment)

    def set_rootCause(self, rootCause):
        rootCause = params.rootCauseType(rootCause, None)
        params.article.set_rootCause(self, rootCause)

    def set_internalDiagnosticSteps(self, internalDiagnosticSteps):
        internalDiagnosticSteps = params.internalDiagnosticStepsType(internalDiagnosticSteps, None)
        params.article.set_internalDiagnosticSteps(self, internalDiagnosticSteps)

    def add_tag(self, tag):
        tag = params.tagType(tag, None)
        params.article.add_tag(self, tag)

    def add_duplicateOf(self, duplicateOf):
        duplicateOf = params.duplicateOfType(None, duplicateOf)
        params.article.add_duplicateOf(self, duplicateOf)

# # No such animal as delete.
#    def delete(self):
#        '''
#
#        '''
#        url = '/rs/articles'
#        sol = self._getProxy().delete(url=UrlHelper.append(url, self.get_id()))
#        print "----%s---" % sol


    def update(self):
        '''
        Update this article. This article *must* have an ID.

        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/articles'
        if self.get_id() is not None:
            self._getProxy().update(url=UrlHelper.append(url, self.superclass.get_id()),
                                    body=ParseHelper.toXml(self.superclass))
        else:
            raise RequestError('ID cannot be None on update')


class articles(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def add(self, art):
        '''
        Add a new article

        :param art: Article to be added to Customer Portal
        :type art: article
        :rtype: article
        :returns: The article ID and view_uri will be set if successful.
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/articles'
        doc, headers = self._getProxy().add(url=url,
                                      body=ParseHelper.toXml(art))
        d = {}
        d.update(headers)
        view_uri = d['view-uri']
        parsed = urlparse(view_uri)
        art.set_id(os.path.basename(parsed[2]))
        art.set_view_uri(view_uri)
        return art

    def get(self, articleID=None):
        '''
        Queries the API for the given article ID.

        :param articleID: Article ID to be queried from the API
        :type articleID: Integer
        :rtype: article
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/articles'

        doc, headers = self._getProxy().get(url=UrlHelper.append(url, articleID))
        art = article(doc)
        logger.debug("REST Response:%s" % art.toXml())
        return art

    def list(self, keywords=None, **kwargs):
        '''
        Queries the articles RESTful interface with a given set of keywords.

        :param keywords: Search string
        :type keywords: string
        :param searchopts: search options/query filters passed to the API
        :type searchopts: dict
        :param kwargs:
            Additional options passed to FilterHelper

            Example:

            .. code-block:: python

                articles.list('RHEV', authorSSOName="anonymous")

        :returns: A list of solution objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/articles'

        doc, headers = self._getProxy().get(url=SearchHelper.appendQuery(url, {'keyword':keywords}))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(article,
                                        FilterHelper.filter(doc.get_article(), kwargs))


class comment(params.comment, Base):
    def __init__(self, comment):
        self.superclass = comment

    def __new__(cls, comment):
        if comment is None: return None
        obj = object.__new__(cls)
        obj.__init__(comment)
        return obj

    @classmethod
    def fromProps(cls, caseNumber=None, text=None,
                  public=True, **kwargs):
        comment = params.comment(caseNumber=caseNumber,
                                 text=text,
                                 public=public,
                                 **kwargs)
        return cls(comment)


    def update(self):
        '''
        Update this comment. This comment must have both an comment ID and a case ID.
        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/cases/{caseNumber}/comments/{commentID}'


        if self.get_id() is not None and self.get_id() is not None:
            url = UrlHelper.replace(url,
                                    {'{caseNumber}': self.get_caseNumber(),
                                     '{commentID}': self.get_id()})
            self._getProxy().update(url,
                                    body=ParseHelper.toXml(self))
        else:
            raise RequestError('ID cannot be None on update')



class comments(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def add(self, cmnt):
        '''
        Add a new comment

        :param cmnt: The comment to be added
        :type cmnt: comment
        :returns: Comment object with ID and view_uri populated
        :rtype: comment
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/comments'

        url = UrlHelper.replace(url, {'{caseNumber}': cmnt.get_caseNumber()})

        doc, headers = self._getProxy().add(url=url,
                                            body=ParseHelper.toXml(cmnt))
        d = {}
        d.update(headers)
        view_uri = d['view_uri']
        parsed = urlparse(view_uri)
        cmnt.set_caseNumber(os.path.basename(parsed[2]))
        cmnt.set_id(parsed[5])
        return cmnt

    def get(self, caseNumber=None, commentID=None):
        '''
        Queries the API for the given solution ID.

        :param caseNumber: Case number to retrieve the comment from.
        :type caseNumber: string
        :param commentID: ID string of the comment to retrieve
        :type commentID: string
        :returns: Comment matching specified case number and comment ID
        :rtype: comment
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/comments/{commentID}'

        url = UrlHelper.replace(url,
                                {'{caseNumber}': caseNumber,
                                 '{commentID}': commentID})

        doc, headers = self._getProxy().get(url)
        com = comment(doc)
        logger.debug("REST Response:%s" % com.toXml())
        return com

    def list(self, caseNumber=None, startDate=None, endDate=None, **kwargs):
        '''
        Gets all of the comments for a given case number.  You can then
        search/filter the returned comments using any of the properties
        of a 'comment'

        :param caseNumber: Case number to retrieve the comment from.
        :type caseNumber: string
        :param startDate: Date to list comments from
        :type startDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param endDate: Date to list comments until
        :type endDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param kwargs:
            Additional options passed to FilterHelper to filter results based
            on additional criteria.

            Example:

            .. code-block:: python

                comments.list('00595293', createdBy="AnonymousUser")

        :type kwargs: dict
        :returns: A list of comment objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/comments'

        url = UrlHelper.replace(url,
                                {'{caseNumber}': caseNumber})

        doc, headers = self._getProxy().get(SearchHelper.appendQuery(url,
                                                                     {'startDate':startDate,
                                                                      'endDate':endDate}))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(comment,
                                        FilterHelper.filter(doc.get_comment(), kwargs))

class attachment(params.attachment, Base):
    def __init__(self, attachment):
        self.superclass = attachment

    def __new__(cls, attachment):
        if attachment is None: return None
        obj = object.__new__(cls)
        obj.__init__(attachment)
        return obj

    @classmethod
    def fromProps(cls, caseNumber=None, public=True,
                  fileName=None, description=None, **kwargs):

        attachmnt = params.attachment(caseNumber=caseNumber, private=not public,
                                      fileName=fileName, description=description,
                                      **kwargs)

        return cls(attachmnt)


class attachments(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def add(self, caseNumber=None, public=True, fileName=None,
            fileChunk=None, description=None, useFtp=False):
        '''
        Add a new attachment

        :param caseNumber: The case number to add the attachment to
        :type caseNumber: string
        :param public: If the attachment is public, or Red Hat only
        :type public: boolean
        :param fileName: Path to the file to be uploaded
        :type fileName: string
        :param description:
            Description of the attachment uploaded, for example "sosreport from
            host database01"

        :type description: string
        :returns: The attachment object with the attachment UUID populated
        :rtype: attachment
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/attachments'
        amnt = None
        config = confighelper.get_config_helper()

        exceeds_max_size = (not fileChunk and os.path.getsize(fileName) > config.attachment_max_size)
        if useFtp or exceeds_max_size:
            amnt = FtpHelper.ftp_attachment(fileName, caseNumber, fileChunk)
            if exceeds_max_size and not useFtp:
                # if useFtp is True, no need to display this comment in the case
                filebaseName = os.path.basename(fileName)
                cmntText = ('[RHST] The file %s exceeds the byte limit to attach a file '
                            'to a case; therefore the file was uploaded to %s as %s-%s'
                            % (filebaseName, config.ftp_host, caseNumber, filebaseName))
                cmnt = InstanceMaker.makeComment(caseNumber=caseNumber,
                                                 text=cmntText)
                casecomment = comments()
                casecomment.add(cmnt)
        else:
            url = UrlHelper.replace(url, {'{caseNumber}': caseNumber})

            doc = self._getProxy().upload(SearchHelper.appendQuery(url, {'private':not public}),
                                          fileName,
                                          fileChunk,
                                          description)[0]
            amnt = attachment(doc)
            amnt.set_private(not public)
            amnt.set_mimeType(mimetypes.guess_type(fileName)[0] or
                              'application/octet-stream')
            logger.debug("REST Response:%s" % amnt.toXml())
        return amnt

    def delete(self, caseNumber=None, attachmentUUID=None):
        '''
        Removes the attachment from the case.

        :param caseNumber: The case number to delete the attachment from
        :type caseNumber: string
        :param attachmentUUID: UUID of the attachment to be deleted
        :type attachmentUUID: string (UUID)
        :returns: True if successful
        :rtype: boolean
        :raises:
            Exception if there was a connection related issue, an issue parsing
            headers, or the attachment deletion failed.
        '''
        url = '/rs/cases/{caseNumber}/attachments/{attachmentUUID}'

        url = UrlHelper.replace(url,
                                {'{caseNumber}': caseNumber,
                                 '{attachmentUUID}': attachmentUUID})

        doc, headers = self._getProxy().delete(url)
        return True

    def get(self, caseNumber=None, attachmentUUID=None, fileName=None, attachmentLength=None, destDir=None):
        '''
        Queries the API for the given attachment.

        :param caseNumber: The case number to retrieve the attachment from
        :type caseNumber: string
        :param attachmentUUID: UUID of the attachment to be retrieved
        :type attachmentUUID: string (UUID)
        :param fileName: Path to the file to be retrieved
        :type fileName: string
        :param attachmentLength: Length of the attachment to be retrieved
        :type attachmentLength: integer
        :param destDir: The directory which the attachment should be saved in
        :type destDir: string
        :returns: The full path to the downloaded file
        :rtype: string
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/attachments/{attachmentUUID}'

        # Pre-checks for proper input
        if not caseNumber or not attachmentUUID:
            raise Exception('caseNumber(%s) attachmentUUID(%s) cannot be empty.' %
                            (caseNumber, attachmentUUID))
        # Join the path
        if destDir and not os.path.isdir(destDir):
            raise Exception("destDir(%s) is not a valid directory" % destDir)

        # BZ967496 - ensure fileName doesn't contain directory separators
        if fileName and os.path.dirname(fileName):
            raise Exception("fileName(%s) contains directory info (%s)."
                            "  Use the destDir parameter for specifying directory info." %
                            (fileName, os.path.dirname(fileName)))

        url = UrlHelper.replace(url,
                                {'{caseNumber}': caseNumber,
                                 '{attachmentUUID}': attachmentUUID})
        conn = None
        fh = None
        try:
            try:
                logger.debug('Downloading attachment...')
                conn = self._getProxy().getConnectionsPool().getConnection()
                response = conn.doRequest(method='GET', url=url)
                if response.status < 400:
                    if not fileName:
                        contDispArr = response.msg.dict['content-disposition'].split("\"")
                        fileName = decode_header(contDispArr[1])[0][0]
                    # Join the path
                    if destDir:
                        fileName = os.path.join(destDir, fileName)
                    fh = open(fileName, 'wb')
                    buf = response.read(8192)
                    downloadedBytes = len(buf)
                    while len(buf) > 0:
                        if attachmentLength:
                            percent = str(int(downloadedBytes * 100 / attachmentLength))
                            sys.stdout.write("%s%3s%%" % ("\b\b\b\b", percent))
                            sys.stdout.flush()
                        fh.write(buf)
                        buf = response.read(8192)
                        downloadedBytes += len(buf)
                    if attachmentLength:
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                    logger.debug('Successfully downloaded %s.' % fileName)
                else:
                    logger.debug("unable to download %s as %s. Reason: %s" %
                                  (url, fileName, response.reason))
                    raise RequestError(response.status, response.reason, None)
            except socket.error, se:
                logger.debug('Socket error: msg(%s)' % (se))
                raise ConnectionError, str(se)
            except IOError, ioe:
                logger.debug('I/O error: errno(%s) strerror(%s)' % (ioe.errno, ioe.strerror))
                raise
            except Exception, e:
                logger.debug('Unexpected exception: msg(%s)' % (str(e)))
                raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            if fh:
                try:
                    fh.close()
                except Exception:
                    pass

        return fileName


    def list(self, caseNumber=None, startDate=None, endDate=None, **kwargs):
        '''
        Gets all of the attachments for a given case number.  You can then
        search/filter the returned comments using any of the properties
        of a 'attachment'

        :param caseNumber: Case number to list the attachments from
        :type caseNumber: string
        :param startDate: Date to list attachments from
        :type startDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param endDate: Date to list attachments until
        :type endDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param kwargs:
            Additional options passed to FilterHelper to filter results based
            on additional criteria.

            Example:

            .. code-block:: python

                attachments.list('00595293', createdBy="AnonymousUser")

        :type kwargs: dict
        :returns: A list of attachment objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/attachments'

        url = UrlHelper.replace(url,
                                {'{caseNumber}': caseNumber})

        doc, headers = self._getProxy().get(SearchHelper.appendQuery(url,
                                                                     {'startDate':startDate,
                                                                      'endDate':endDate}))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(attachment,
                                        FilterHelper.filter(doc.get_attachment(), kwargs))


class entitlement(params.entitlement, Base):
    def __init__(self, entitlement):
        self.superclass = entitlement

    def __new__(cls, entitlement):
        if entitlement is None: return None
        obj = object.__new__(cls)
        obj.__init__(entitlement)
        return obj

    @classmethod
    def fromProps(cls, name=None, **kwargs):

        entitlement = params.entitlement(name=name, **kwargs)
        return cls(entitlement)

class entitlements(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def list(self, activeOnly=True, product=None, **kwargs):
        '''
        Queries the entitlements RESTful interface with a given set of
        keywords.

        :param activeOnly: Limit results to only active entitlements
        :type activeOnly: boolean
        :param product: Product to limit results to
        :type product: string
        :param kwargs:
            Additional options passed to FilterHelper to filter results based
            on additional criteria.

            Example:

            .. code-block:: python

                entitlements.list(supportLevel='SUPPORTED')

        :type kwargs: dict
        :returns: A list of entitlement objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/entitlements'
        # Strata is inverted in several respects, the option for filtering inactive entitlements being one.
        showAll = not activeOnly
        doc, headers = self._getProxy().get(url=SearchHelper.appendQuery(url,
                                                                         {"showAll":showAll, "product": product}))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(entitlement,
                                        FilterHelper.filter(doc.get_entitlement(), kwargs))


class case(params.case, Base):
    def __init__(self, case):
        self.superclass = case

    def __new__(cls, case):
        if case is None: return None
        obj = object.__new__(cls)
        obj.__init__(case)
        return obj

    @classmethod
    def fromProps(cls, summary=None, product=None, version=None, **kwargs):
        case = params.case(summary=summary, product=product, version=version, **kwargs)
#
        return cls(case)

    def update(self):
        '''
        Update this case. This case *must* have an case number.

        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases'
        if self.get_caseNumber() is not None:
            self._getProxy().update(url=UrlHelper.append(url, self.get_caseNumber()),
                                    body=ParseHelper.toXml(self.superclass))
        else:
            raise RequestError('ID cannot be None on update')

    def get_comments(self):
        '''
        Retrieve a list of comments related to the case object

        :returns: A list of comment objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        try:
            return ParseHelper.toCollection(comment,
                                        params.case.get_comments(self).comment)
        except AttributeError:
            # AttributeErrors happen if the API forgets to include the XML
            # Stanza for comments, send a empty list back.
            return []

    def get_attachments(self):
        '''
        Retrieve a list of attachments, related to the case object

        :returns: A list of attachment objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases/{caseNumber}/attachments'
        url = UrlHelper.replace(url, {'{caseNumber}': quote(self.get_caseNumber())})
        doc, headers = self._getProxy().get(url)
        return ParseHelper.toCollection(attachment, doc.get_attachment())

    def get_recommendations(self):
        '''
        Retrieve a list of recommendations related to the case object

        :returns: A list of recommendation objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        try:
            return ParseHelper.toCollection(recommendation,
                        params.case.get_recommendations(self).recommendation)
        except AttributeError:
            # AttributeErrors happen if the API forgets to include the XML
            # Stanza for recommendations, send a empty list back.
            return []

    def get_entitlement(self):
        return entitlement(params.case.get_entitlement(self))


class cases(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def add(self, cs):
        '''
        Add a new case

        :param cs: case object to be submitted to the Customer Portal
        :type cs: case
        :returns:
            The same case object with the case number and associated fields
            populated.

        :rtype: case
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''

        url = '/rs/cases'
        doc, headers = self._getProxy().add(url=url,
                                            body=ParseHelper.toXml(cs))
        d = {}
        d.update(headers)
        view_uri = d['view_uri']
        parsed = urlparse(view_uri)
        cs.set_caseNumber(os.path.basename(parsed[2]))
        cs.set_view_uri(view_uri)
        return cs

    def get(self, caseNumber=None):
        '''
        Queries the API for the given case number.

        :param caseNumber: Case Number of case to retrieve from the API
        :type caseNumber: string
        :returns: The case object for the relevant caseNumber provided
        :rtype: case
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases'

        doc, headers = self._getProxy().get(url=UrlHelper.append(url, caseNumber))
        cs = case(doc)
        logger.debug("REST Response:%s" % cs.toXml())
        return cs

    def list(self, keywords=None, includeClosed=False, detail=False,
             group=None, startDate=None, endDate=None, **kwargs):
        '''
        Queries the cases RESTful interface with a given set of keywords.

        :param keywords: Keywords to search cases on (space seperated)
        :type keywords: string
        :param detail:
        :type detail: boolean
        :param group: Case group to search for cases in
        :param startDate: Date to start listing cases from
        :type startDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param endDate: Date to list cases until
        :type endDate:
            ISO 8601 formatted string, either YYYY-MM-DDThh:mm:ss or YYYY-MM-DD
        :param searchopts: search options/query filters passed to the API
        :type searchopts: dict
        :param kwargs:
            Additional options passed to FilterHelper to filter results based
            on additional criteria.

            Example:

            .. code-block:: python

                cases.list(status="Closed")

        :type kwargs: dict
        :returns: A list of case objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/cases'

        # extract searchopts from kwargs, return empty dict if not present
        searchopts = kwargs.pop('searchopts', {})

        # Because cases.list handled search options better previously,
        # overwrite (if somehow needed) with what we captured in named
        # arguments with dict.update
        searchopts.update({'query': keywords,
                           'includeClosed': includeClosed,
                           'group': group,
                           'startDate': startDate,
                           'endDate': endDate})

        doc, headers = self._getProxy().get(url=SearchHelper.appendQuery(url,
                                                                   searchopts))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(case,
                                        FilterHelper.filter(doc.get_case(),
                                                            kwargs))

    def filter(self, case_filter):
        '''
        Filter case results.

        :param case_filter: a filter object to be submitted
        :type cs: caseFilter
        :returns:
             A list of case objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''

        url = '/rs/cases/filter'
        doc, headers = self._getProxy().add(url=url,
                                    body=ParseHelper.toXml(case_filter))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(case,
                                        FilterHelper.filter(doc.get_case()))


class symptom(params.symptom, Base):
    def __init__(self, symptom):
        self.superclass = symptom

    def __new__(cls, symptom):
        if symptom is None: return None
        obj = object.__new__(cls)
        obj.__init__(symptom)
        return obj

    @classmethod
    def fromProps(cls, caseNumber=None, category=None, 
                  data=None, description=None,
                  location=None, summary=None,
                  uri=None, **kwargs):

        symptom = params.symptom(caseNumber=caseNumber, category=category,
                                 data=data, description=description,
                                 location=location, summary=summary,
                                 uri=uri, **kwargs)
        return cls(symptom)


class extractedSymptom(params.extractedSymptom, Base):
    def __init__(self, extractedSymptom):
        self.superclass = extractedSymptom

    def __new__(cls, extractedSymptom):
        if extractedSymptom is None: return None
        obj = object.__new__(cls)
        obj.__init__(extractedSymptom)
        return obj

    @classmethod
    def fromProps(cls, label=None, createdBy=None, createdDate=None, lastModifiedBy=None,
                  lastModifiedDate=None, linked=None, linkedBy=None, linkedAt=None,
                  type_=None, category=None, occurrences=None, verbatim=None, fields=None,
                  beginIndex=None, endIndex=None, summary=None, signature=None, timestamp=None):

        symptom = params.extractedSymptom(label=label, createdBy=createdBy, createdDate=createdDate,
                                          lastModifiedBy=lastModifiedBy, lastModifiedDate=lastModifiedDate,
                                          linked=linked, linkedBy=linkedBy, linkedAt=linkedAt,
                                          type_=type_, category=category, occurrences=occurrences,
                                          verbatim=verbatim, fields=fields, beginIndex=beginIndex,
                                          endIndex=endIndex, summary=summary, signature=signature,
                                          timestamp=timestamp)
        return cls(extractedSymptom)


class symptoms(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self


    def add(self, sym):
        url = '/rs/symptoms'
        doc, headers = self._getProxy().add(url=url,
                                            body=ParseHelper.toXml(sym))
        d = {}
        d.update(headers)
        sym.set_location(d['location'])
        return sym


    def extractFromStr(self,
                       content=None):
        '''
        Queries the symptom extractor RESTful interface with a given string.

        :param content:
            The text that you wish to be analyzed by the diagnostics engine

        :type content: string
        :returns: A list of extractedSymptom objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/symptoms/extractor'

        doc, headers = self._getProxy().action(url,
                                               body=escape(content),
                                               headers={'Content-Type': 'text/plain'})

        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(extractedSymptom, doc.get_extractedSymptom())

    def extractFromFile(self, fileName=None):
        '''
        Queries the symptom extractor RESTful interface with a given string.

        :param fileName:
            The path of the file that you wish to be analyzed
            by the diagnostics engine

        :type fileName: file
        :returns: A list of extractedSymptom objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers

            socket.error or IOError for issues when reading the specified file.
        '''
        url = '/rs/symptoms/extractor'
        fh = None
        doc = None
        try:
            try:
                fh = open(fileName, 'rb')
                doc, headers = self._getProxy().action(url,
                                                       fh.read(),
                                                       {'Content-Type': 'text/plain'})
            except socket.error, se:
                logger.debug('Socket error: msg(%s)' % (se))
                raise ConnectionError, str(se)
            except IOError, ioe:
                logger.debug('I/O error: errno(%s) strerror(%s)' % (ioe.errno, ioe.strerror))
                raise
            except Exception, e:
                logger.debug('Unexpected exception: msg(%s)' % (str(e)))
                raise
        finally:
            if fh:
                fh.close()

        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(extractedSymptom, doc.get_extractedSymptom())


class problem(params.problem, Base):
    def __init__(self, problem):
        self.superclass = problem

    def __new__(cls, problem):
        if problem is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(problem)
        return obj

    @classmethod
    def fromProps(cls, source=None, link=None, explainSbr=None):

        problem = params.problem(source=source, link=link, explainSbr=explainSbr)
        return cls(problem)


class problems(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def diagnoseStr(self,
                    content=None):
        '''
        Queries the problems RESTful interface with a given string.

        :param content:
            The text that you wish to be analyzed by the diagnostics engine

        :type content: string
        :returns: A list of problem objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/problems'


        rpt = report.report()

        rpt.add_binding(report.binding(type_='text',
                                       name='summary',
                                       valueOf_=escape(content)))
        doc, headers = self._getProxy().action(url,
                                               body=ReportParseHelper.toXml(rpt))

        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(problem, doc.get_problem())

    def diagnoseFile(self, fileName=None):
        '''
        Queries the problems RESTful interface with a given file.

        :param fileName:
            The path of the file that you wish to be analyzed
            by the diagnostics engine

        :type fileName: file
        :returns: A list of problem objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers

            socket.error or IOError for issues when reading the specified file.
        '''
        url = '/rs/problems'
        fh = None
        try:
            try:
                fh = open(fileName, 'rb')
                doc, headers = self._getProxy().action(url,
                                                   fh.read())
            except socket.error, se:
                logger.debug('Socket error: msg(%s)' % (se))
                raise ConnectionError, str(se)
            except IOError, ioe:
                logger.debug('I/O error: errno(%s) strerror(%s)' % (ioe.errno, ioe.strerror))
                raise
            except Exception, e:
                logger.debug('Unexpected exception: msg(%s)' % (str(e)))
                raise
        finally:
            if fh:
                fh.close()

        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(problem, doc.get_problem())

    def diagnoseCase(self, diagcase=None):
        '''
        Queries the problems RESTful interface with a given file.

        :param diagcase:
            The case to be evaluated by the

        :type diagcase: case object
        :returns: A list of recommendation objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers

            socket.error or IOError for issues when reading the specified file.
        '''
        url = '/rs/problems'
        try:
            doc, headers = self._getProxy().action(url,
                        diagcase.toXml(),
                        headers={'Accept':
                                   'application/vnd.redhat.xml.suggestions'})
        except socket.error, se:
            logger.debug('Socket error: msg(%s)' % (se))
            raise ConnectionError, str(se)
        except IOError, ioe:
            logger.debug('I/O error: errno(%s) strerror(%s)' % (ioe.errno, ioe.strerror))
            raise
        except Exception, e:
            logger.debug('Unexpected exception: msg(%s)' % (str(e)))
            raise

        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(recommendation,
                                        doc.get_recommendation())


class product(params.product, Base):
    def __init__(self, product):
        self.superclass = product

    def __new__(cls, product):
        if product is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(product)
        return obj

    @classmethod
    def fromProps(cls, code=None, name=None):
        product = params.product(code, name)
        return cls(product)

    def get_versions(self):
        url = '/rs/products/{prodName}/versions'
        url = UrlHelper.replace(url, {'{prodName}': quote(self.get_name())})
        doc, headers = self._getProxy().get(url)
        return doc.get_version()


class products(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def list(self, **kwargs):
        '''
        Queries the products RESTful interface with a given set of keywords.

        :param kwargs:
            Properties to be passed to FilterHelper to filter results based
            on additional criteria.

            Example:

            .. code-block:: python

                products.list(name="Fuse ESB")

        :type kwargs: dict
        :returns: A list of product objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/products'
        doc, headers = self._getProxy().get(url)
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(product,
                                        FilterHelper.filter(doc.get_product(), kwargs))


class recommendation(params.recommendation, Base):
    def __init__(self, recommendation):
        self.superclass = recommendation

    def __new__(cls, recommendation):
        if recommendation is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(recommendation)
        return obj

    @classmethod
    def fromProps(cls, **kwargs):

        prec = params.recommendation(**kwargs)
        return cls(prec)


class group(params.group, Base):
    def __init__(self, group):
        self.superclass = group

    def __new__(cls, group):
        if group is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(group)
        return obj

    @classmethod
    def fromProps(cls, number=None, name=None, uri=None, isPrivate=None):
        group = params.group(number=number, name=name, uri=uri,
                             isPrivate=isPrivate)
        return cls(group)


class groups(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def list(self):
        '''
        Queries the groups RESTful interface for a list of case groups.

        :returns: A list of group objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/groups'
        doc, headers = self._getProxy().get(url)
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(group,
                                        FilterHelper.filter(doc.get_group()))

    def get(self, groupNumber=None):
        '''
        Queries the API for the given group number.
        '''
        url = '/rs/groups'
        doc, headers = self._getProxy().get(url=UrlHelper.append(url, groupNumber))
        g = group(doc)
        logger.debug("REST Response:%s" % g.toXml())
        return g


class user(params.user, Base):
    def __init__(self, user):
        self.superclass = user

    def __new__(cls, user):
        if user is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(user)
        return obj

    @classmethod
    def fromProps(cls, firstName=None, lastName=None, orgAdmin=None,
                  hasChat=None, sessionId=None, isInternal=None,
                  canAddAttachments=None):
        user = params.user(firstName=firstName, lastName=lastName,
                           orgAdmin=orgAdmin, hasChat=hasChat,
                           sessionId=sessionId, isInternal=isInternal,
                           canAddAttachments=canAddAttachments)
        return cls(user)


class users(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def get(self, userName=None):
        '''
        Queries the API for the given user name.
        '''
        url = '/rs/users'
        doc, headers = self._getProxy().get("%s?ssoUserName=%s" % (url, userName))
        u = user(doc)
        logger.debug("REST Response:%s" % u.toXml())
        return u


class caseFilter(params.caseFilter, Base):
    def __init__(self, caseFilter):
        self.superclass = caseFilter

    def __new__(cls, caseFilter):
        if caseFilter is None:
            return None
        obj = object.__new__(cls)
        obj.__init__(caseFilter)
        return obj

    @classmethod
    def fromProps(cls, endDate=None, accountNumber=None,
                  includeClosed=None, groupNumbers=None,
                  includePrivate=None, keyword=None,
                  count=None, start=None, onlyUngrouped=None,
                  ownerSSOName=None, product=None, severity=None,
                  sortField=None, sortOrder=None, startDate=None,
                  status=None, type_=None, associateSSOName=None, view=None):

        if groupNumbers:
            groupNumbers = params.groupNumbers(groupNumbers)

        filt = params.caseFilter(endDate=endDate,
                  accountNumber=accountNumber,
                  includeClosed=includeClosed,
                  groupNumbers=groupNumbers,
                  includePrivate=includePrivate, keyword=keyword,
                  count=count, start=start, onlyUngrouped=onlyUngrouped,
                  ownerSSOName=ownerSSOName, product=product,
                  severity=severity, sortField=sortField,
                  sortOrder=sortOrder, startDate=startDate,
                  status=status, type_=type_, associateSSOName=associateSSOName,
                  view=view)
        return cls(filt)


class values(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def getType(self, **kwargs):
        '''
        Queries the API for available case type values.
        RESTful method: https://api.access.redhat.com/rs/values/case/types

        Keyword arguments:
        returns   -- A list of case type values.
        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/values/case/types'

        doc, headers = self._getProxy().get(url)
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        type_values = list(value.get_name() for value in doc.get_value())
        return type_values

    def getSeverity(self, **kwargs):
        '''
        Queries the API for available case severity values.
        RESTful method: https://api.access.redhat.com/rs/values/case/severity

        Keyword arguments:
        returns   -- A list of case severity values.
        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/values/case/severity'

        doc, headers = self._getProxy().get(url)
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        severity_values = list(value.get_name() for value in doc.get_value())
        return severity_values

    def getStatus(self, **kwargs):
        '''
        Queries the API for available case status values.
        RESTful method: https://api.access.redhat.com/rs/values/case/status

        Keyword arguments:
        returns   -- A list of case status values.
        raises   -- An exception if there was a connection related issue.
        '''
        url = '/rs/values/case/status'

        doc, headers = self._getProxy().get(url)
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        severity_values = list(value.get_name() for value in doc.get_value())
        return severity_values


class searchResult(params.searchResult, Base):
    def __init__(self, searchResult):
        self.superclass = searchResult

    def __new__(cls, searchResult):
        if searchResult is None: return None
        obj = object.__new__(cls)
        obj.__init__(searchResult)
        return obj

    @classmethod
    def fromProps(cls, **kwargs):

        symptom = params.searchResult(**kwargs)
        return cls(searchResult)

class search(Base):
    def __init__(self):
        """Constructor."""
        # Assign self to superclass for the broker classes that are aggregates of the specific type.
        # Without this assignment you'll get a nice and confusing recursion stacktrace if
        # a wayward programmer attempts to call a non-existent method on this class.
        self.superclass = self

    def search(self, keywords=None, **kwargs):
        '''
        Queries the search RESTful interface with a given set of keywords.

        :param keywords: Search string
        :type keywords: string
        :param searchopts: search options/query filters passed to the API
        :type searchopts: dict
        :param kwargs:
            Additional options passed to FilterHelper

            Example:

            .. code-block:: python

                api.search.search('RHEV', authorSSOName="anonymous")

        :returns: A list of searchResult objects
        :rtype: list
        :raises:
            Exception if there was a connection related issue or an
            issue parsing headers
        '''
        url = '/rs/search'

        doc, headers = self._getProxy().get(url=SearchHelper.appendQuery(url, {'keyword':keywords}))
        logger.debug("REST Response:\n%s" % ParseHelper.toXml(doc))
        return ParseHelper.toCollection(searchResult,
                                        FilterHelper.filter(doc.get_searchResult(), kwargs))


class InstanceMaker(object):
    '''
    Utility class to make single instances of case, solution, article, entitlement, and comment.
    This is useful so that you only need import API and not all of the helper classes used by
    API to get the job done.
    '''
    @classmethod
    def makeCase(self, summary=None, product=None, version=None, **kwargs):
        return case.fromProps(summary=summary, product=product, version=version, **kwargs)

    @classmethod
    def makeSolution(self, createdBy=None, title=None,
                     summary=None, kcsState=None,
                     resolution=None, **kwargs):
        return solution.fromProps(createdBy=createdBy, title=title,
                                  summary=summary, kcsState=kcsState,
                                  resolution=resolution, **kwargs)

    @classmethod
    def makeArticle(self, createdBy=None, title=None,
                    summary=None, kcsState=None,
                    body=None, **kwargs):
        return article.fromProps(createdBy=createdBy, title=title,
                              summary=summary, kcsState=kcsState,
                              body=body, **kwargs)

    @classmethod
    def makeEntitlement(self, name=None, **kwargs):
        return entitlement.fromProps(name=name, **kwargs)

    @classmethod
    def makeComment(self, caseNumber=None, text=None,
                    public=True, **kwargs):
        return comment.fromProps(caseNumber=caseNumber,
                                 text=text,
                                 public=public,
                                 **kwargs)

    @classmethod
    def makeAttachment(self, caseNumber=None, public=True,
                       fileName=None, description=None, **kwargs):
        return attachment.fromProps(caseNumber=caseNumber, private=not public,
                                      fileName=fileName, description=description,
                                      **kwargs)
    @classmethod
    def makeSymptom(self, caseNumber=None, category=None,
                    data=None, description=None,
                    location=None, summary=None,
                    uri=None, **kwargs):
        return symptom.fromProps(caseNumber=caseNumber, category=category,
                                 data=data, description=description,
                                 location=location, summary=summary,
                                 uri=uri, **kwargs)

    @classmethod
    def makeCaseFilter(cls, endDate=None, accountNumber=None,
                       includeClosed=None, groupNumbers=None,
                       includePrivate=None, keyword=None,
                       count=None, start=None, onlyUngrouped=None,
                       ownerSSOName=None, product=None, severity=None,
                       sortField=None, sortOrder=None, startDate=None,
                       status=None, type_=None, associateSSOName=None,
                       view=None):
        return caseFilter.fromProps(endDate=endDate,
                                    accountNumber=accountNumber,
                                    includeClosed=includeClosed,
                                    groupNumbers=groupNumbers,
                                    includePrivate=includePrivate,
                                    keyword=keyword,
                                    count=count, start=start,
                                    onlyUngrouped=onlyUngrouped,
                                    ownerSSOName=ownerSSOName,
                                    product=product,
                                    severity=severity,
                                    sortField=sortField,
                                    sortOrder=sortOrder,
                                    startDate=startDate,
                                    status=status,
                                    type_=type_,
                                    associateSSOName=associateSSOName,
                                    view=view)

