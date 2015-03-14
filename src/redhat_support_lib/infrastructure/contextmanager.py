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

from redhat_support_lib.infrastructure.errors import ImmutableError
import threading

cache = {}
lock = threading.RLock()


class __Item(object):
    def __init__(self, val, mode):
        self.__val = val
        self.__mode = mode

    def get_val(self):
        return self.__val

    def get_mode(self):
        return self.__mode

    val = property(get_val, None, None, None)
    mode = property(get_mode, None, None, None)


class Mode(object):
    RW, R = range(2)

    def __init__(self, Type):
        self.value = Type

    def __str__(self):
        if self.value == Mode.RW:
            return 'ReadWrite'
        if self.value == Mode.R:
            return 'Read'

    def __eq__(self, y):
        return self.value == y.value


def add(key, val, mode=Mode.RW):
    '''
    stores the value in cache

    Keyword arguments:
    key    -- is the cache key
    val    -- is the cache value
    mode   -- is the access mode [r|rw]
    '''
    try:
        lock.acquire(True)
        if mode is Mode.R and cache.has_key(key):
            raise ImmutableError(key)
        else:
            cache[key] = __Item(val, mode)
    finally:
        lock.release()


def get(key, remove=False):
    '''
    retrieves the value from the cache

    Keyword arguments:
    key     --  is the cache key
    remove  --  removes the value from cache [true|false]
    '''
    try:
        lock.acquire(True)
        if cache.has_key(key):
            if  remove:
                item = cache[key]
                if item.mode is Mode.RW:
                    item = cache.pop(key)
                    return item.val
                else:
                    raise ImmutableError(key)
            else:
                return cache[key].val
        return None
    finally:
        lock.release()


def _remove(key, force=False):
    '''
    removes the value from cache

    Keyword arguments:
    key   --   is the cache key
    force --   force remove regardless cache mode
    '''
    try:
        lock.acquire(True)
        if cache.has_key(key):
            item = cache[key]
            if (item.mode is Mode.RW) or force:
                cache.pop(key)
            else:
                raise ImmutableError(key)
    finally:
        lock.release()
