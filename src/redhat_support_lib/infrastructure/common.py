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
from redhat_support_lib.utils.parsehelper import ParseHelper
from redhat_support_lib.infrastructure import contextmanager

class Base(object):
    ''' Returns the proxy to connections pool '''
    def _getProxy(self):
        return contextmanager.get('proxy')

    def __getattr__(self, item):
        return self.superclass.__getattribute__(item)

    def toXml(self):
        '''
        A utility method to print this object's superclass as XML.
        The superclass property should be a member of redhat_support_lib.xml.params.
        '''
        return ParseHelper.toXml(self.superclass)
