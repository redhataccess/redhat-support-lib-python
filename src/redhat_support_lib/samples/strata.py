'''
Created on Apr 13, 2012

@author: Keith Robertson
'''
from redhat_support_lib.api import API

__author__ = 'Keith Robertson <kroberts@redhat.com>'


def sampleSolutionSearch(api):
    '''
    Search for solutions with the given keyword(s) and apply a post-get-filter to
    the returned list. In this case we're post-get-filtering on the author.  Why post-get-filter?
    The RESTful API doesn't (and shouldn't) filter on every property
    in a solution.
    Note: All properties of a solution are available as filterable arguments.  The
    list method takes a **kwargs; hence, you simply need to supply the property
    and the value you're looking for.
    ex. api.solutions.list('RHEV',authorSSOName='rhn-support-vvijayan', kcsState='wip',
                            anotherPropertyHere='anotherValueHere',..., etc.)
    '''
    solAry = api.solutions.list('RHEV', authorSSOName='rhn-support-vvijayan')
    print "---- Printing Filtered Results---"
    for sol in solAry:
        sol.toXml()


def sampleCaseSearch(api):
    '''
    Search for cases with the given keyword(s) and apply a filter to
    the returned list. In this case we're filtering on the owner.  Why filter?
    The RESTful API doesn't (and shouldn't) filter on every property
    in a solution.
    Note: All properties of a solution are available as filterable arguments.  The
    list method takes a **kwargs; hence, you simply need to supply the property
    and the value you're looking for.
    ex. api.cases.list('RHEV',owner='Hannah Miles', accountNumber='1317732',
                            anotherPropertyHere='anotherValueHere',..., etc.)
    '''
    solAry = api.cases.list(startDate='2011-01-01',
                            status='Pending Closure')

    print "---- Printing Filtered Results---"
    for sol in solAry:
        sol.toXml()


def sampleCaseGet(api):
    '''
    Get a specific case and print it's details.
    '''
    cs = api.cases.get('00595293')
    print "---- Printing Case GET result---"
    # This will print everything ... including case comments
    cs.toXml()

    print "---- Printing comments individually---"
    commentAry = cs.get_comments()
    n = 1
    for c in commentAry:
        print "--- Comment number %s" % n
        c.toXml()
        n = n + 1

    print "---- Printing solutions individually---"
    solAry = cs.get_solutions()
    for s in solAry:
        s.toXml()


    print "---- Printing entitlement---"
    e = cs.get_entitlement()
    if e is not None:
        e.toXml()


def sampleCaseCreate(api):
    '''
    Create a case and print the returned URI.
    '''
    # Step 1: You need to create a case bean.  This is an object
    # that has all of the attributes of the case that you want
    # to create.
    case = api.im.makeCase(summary="Summary field: Python Bindings Test",
                           description="Description field:  Python Bindings Test",
                           product="Red Hat Enterprise Linux",
                           version="6.0",
                           entitlement=api.im.makeEntitlement(name='1redhatlogin 1redhatlogin'))
    print "--- Print the XML before we send it---"
    case.toXml()

    # Step 2: Send your case bean to the RESTful API.  The strata-sdk code
    # will handle the marshalling and unmarshalling of the data to XML for you.
    retVal = api.cases.add(case)

    # Step 3: Investigate the return response.  Did we get a URI back?
    print "--- Print the Case number and URI of the newly created case ---"
    if retVal is not None:
        print "Case Number(%s) URI(%s)" % (retVal.get_caseNumber(), retVal.get_uri())


def sampleCaseUpdate(api):
    # Step 1: Make a case.
    # - You must provide the case number.
    # - After the case number, all properties are available for updating.  In this
    # example I'm only updating the type.
    case = api.im.makeCase(caseNumber='00642424', type_='Other')

    # Step 2: On the case bean ... call update.
    case.update()


def sampleCommentGet(api):
    '''
    Get a specific comment from a specific case.
    '''
    comment = api.comments.get('00595293', 'a0aA00000079RwcIAE')
    # print the comment.
    comment.toXml()


def sampleCommentSearch(api):
    '''
    Get all comments from a given case an filter them on some property
    intrinsic to a comment.
    '''
    comAry = api.comments.list('00595293',
                               createdBy='Vaddarapu, Anand')

    print "---- Printing Filtered Results---"
    for com in comAry:
        com.toXml()


def sampleCommentCreate(api):
    '''
    Add a comment to a case and print the returned URI.
    '''
    com = api.im.makeComment(caseNumber='00642424',
                             public=False,
                             # draft=True,
                             text='Test comment 5.')
    retVal = api.comments.add(com)
    print "--- Print the comment ID and URI of the newly created comment ---"
    if retVal is not None:
        print "Comment ID(%s) URI(%s)" % (retVal.get_id(), retVal.get_uri())


def sampleCommentUpdate(api):
    '''
    Updating a comment can only be done if the comment is in draft state.
    '''
    com = api.im.makeComment(caseNumber='00642424',
                       id='a0aZ00000009bKaIAI',
                       draft=False,
                       text='Updated text.')
    com.update()

    pass

#
# Main starts here.
#
if __name__ == '__main__':
    api = API(username='rhn-support-yourname',
              password='password',
              url='https://api.access.gss.devlab.phx1.redhat.com')


    # sampleSolutionSearch(api)
    # sampleCaseSearch(api)
    # sampleCaseGet(api)
    # sampleCaseCreate(api)
    # sampleCaseUpdate(api)
    # sampleCommentGet(api)
    # sampleCommentCreate(api)
    sampleCommentUpdate(api)
    pass
