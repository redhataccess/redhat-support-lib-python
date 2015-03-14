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

import inspect
import threading


class ReflectionHelper(object):
    cache = {}
    __rlock = threading.RLock()
    '''Provides reflection capabilities'''
    @staticmethod
    def getClasses(module, byName=False):
        '''
        Retrieves module members

        Keyword Arguments:
        module  -- the name of the module for lookup
        '''
        known_wrapper_types = {}
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if byName is True:
                known_wrapper_types[name.lower()] = name
            else:
                known_wrapper_types[name.lower()] = obj

        return known_wrapper_types

    @staticmethod
    def getClassNames(module):
        '''
        Retrieves module member's names key:val pairs

        Keyword Arguments:
        module -- the name of the module for lookup
        '''
        return ReflectionHelper.getClasses(module, True)

    @staticmethod
    def isModuleMember(module, typ, invalidate=False):
        '''
        Checks if specific type exist in given module

        Keyword Arguments:
        module     -- the name of the module for lookup
        typ        -- the type to check
        invalidate -- force cache invalidation
        '''
        try:
            ReflectionHelper.__rlock.acquire(True)
            if invalidate or (module not in ReflectionHelper.cache.keys() or \
               (len(inspect.getmembers(module, inspect.isclass)) >
                len(ReflectionHelper.cache[module]))):
                ReflectionHelper.cache[module] = \
                    ReflectionHelper.getClasses(module)
            if ReflectionHelper.cache[module].has_key(typ.__name__.lower()) and \
               ReflectionHelper.cache[module][typ.__name__.lower()] == typ:
                return True
            return False
        finally:
            ReflectionHelper.__rlock.release()
