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

from redhat_support_lib.utils.reflectionhelper import ReflectionHelper
from redhat_support_lib.xml import params, report
import StringIO
import sys


class ParseHelper(object):
    '''Provides parsing capabilities'''

    @classmethod
    def toXml(self, entity):
        '''Parse entity to corresponding XML representation'''

        if ReflectionHelper.isModuleMember(
                    sys.modules['redhat_support_lib.infrastructure.brokers'],
                    type(entity)) and hasattr(entity, 'superclass'):
            entity = entity.superclass

        type_name = type(entity).__name__.lower()
        output = StringIO.StringIO()
        output.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        entity.export(output, 0, name_=self.getXmlTypeInstance(type_name),
                      namespacedef_='xmlns:tns="http://www.redhat.com/gss/strata"')
        return output.getvalue()

    @classmethod
    def getXmlWrapperType(self, type_name):
        tn = type_name.lower()
        for k, v in params._rootClassMap.items():
            if v.__name__.lower() == tn or k.lower() == tn:
                return v.__name__
        return type_name

    @classmethod
    def getXmlTypeInstance(self, type_name):
        tn = type_name.lower()
        for k, v in params._rootClassMap.items():
            if v.__name__.lower() == tn:
                return k
        return type_name

    @classmethod
    def getXmlType(self, type_name):
        if type_name and type_name != '':
            tn = type_name.lower()
            items = params._rootClassMap.items()
            for k, v in items:
                if v.__name__.lower() == tn or k.lower() == tn:
                    return v
        return None

    @classmethod
    def getSingularXmlTypeInstance(self, type_name):
        instance = self.getXmlTypeInstance(type_name)
        if instance.endswith('s'):
            return instance[0 : len(instance) - 1]
        return instance

    @classmethod
    def toType(self, fromItem, toType):
        '''Encapsulates the entity with the broker instance.'''
        return toType(fromItem)

    @classmethod
    def toCollection(self, toType, fromItems=[]):
        '''Encapsulates the entities collection with the broker 
           instance collection.'''
        new_coll = []
        for item in fromItems:
            new_coll.append(self.toType(item, toType))
        return new_coll

    @classmethod
    def toSubType(self, fromItem, toType, parent):
        '''Encapsulates the sub-entity with the broker instance.'''
        return toType(parent, fromItem)

    @classmethod
    def toSubTypeFromCollection(self, toType, parent, fromItems=[]):
        '''Encapsulates the sub-entity collection element with the broker 
           instance.'''
        if fromItems is not None and len(fromItems) > 0:
            return toType(parent, fromItems[0])
        else:
            None

    @classmethod
    def toTypeFromCollection(self, toType, fromItems=[]):
        '''Encapsulates the entity collection element with the broker 
           instance.'''
        # return toType(fromItems[0]) if(fromItems is not None and len(fromItems) > 0) else None
        if fromItems is not None and len(fromItems) > 0:
            return toType(fromItems[0])
        else:
            None

    @classmethod
    def toSubCollection(self, toType, parent, fromItems=[]):
        '''Encapsulates the sub-entities collection with the broker instance 
           collection.'''
        new_coll = []
        for fromItem in fromItems:
            new_coll.append(self.toSubType(fromItem, toType, parent))
        return new_coll


class ReportParseHelper(ParseHelper):

    @classmethod
    def toXml(self, entity):
        '''Parse entity to corresponding XML representation'''

        if ReflectionHelper.isModuleMember(
                    sys.modules['redhat_support_lib.infrastructure.brokers'],
                    type(entity)) and hasattr(entity, 'superclass'):
            entity = entity.superclass

        type_name = type(entity).__name__.lower()
        output = StringIO.StringIO()
        output.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        # rs/problems can't handle namespaced XML need to nil it out.
        entity.export(output,
                      0,
                      name_=self.getXmlTypeInstance(type_name),
                      namespace_='',  # Set to null.
                      namespacedef_='xmlns="http://www.redhat.com/gss/strata"')
        return output.getvalue()

    @classmethod
    def getXmlWrapperType(self, type_name):
        tn = type_name.lower()
        for k, v in report._rootClassMap.items():
            if v.__name__.lower() == tn or k.lower() == tn:
                return v.__name__
        return type_name

    @classmethod
    def getXmlTypeInstance(self, type_name):
        tn = type_name.lower()
        for k, v in report._rootClassMap.items():
            if v.__name__.lower() == tn:
                return k
        return type_name

    @classmethod
    def getXmlType(self, type_name):
        if type_name and type_name != '':
            tn = type_name.lower()
            items = report._rootClassMap.items()
            for k, v in items:
                if v.__name__.lower() == tn or k.lower() == tn:
                    return v
        return None
