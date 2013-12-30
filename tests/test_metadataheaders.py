# Copyright (C) 2013 eNovance SAS <licensing@enovance.com>
#
# Author: Christian Schwede <christian.schwede@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import unittest

from swift.common.swob import Request

from metadataheaders import middleware as metadataheaders


class FakeCache(object):
    def __init__(self, val=None):
        if val:
            self.val = val
        else:
            self.val = {}

    def get(self, key, *args):
        return self.val.get(key)

    def set(self, *args, **kwargs):
        pass


class FakeApp(object):
    def __init__(self, headers=None):
        if headers:
            self.headers = headers
        else:
            self.headers = {}

    def __call__(self, env, start_response):
        start_response('200 OK', self.headers)

        return []


class TestMetadataHeaders(unittest.TestCase):
    def setUp(self, *_args, **_kwargs):
        self.app = metadataheaders.MetadataHeadersMiddleware(FakeApp(),
            {'header_container_metadata': 'entry1, entry2',
             'header_object_metadata': 'entry4, entry5'})
        
        self.cache = FakeCache({
            'container/a/c': {'meta': {
                    'entry1': 'sample1',
                    'entry2': 'sample2',
                    'entry3': 'sample3',
                }}})

    def test_get_container(self):
        req = Request.blank('/v1/a/c', environ={
            'REQUEST_METHOD': 'GET', 'swift.cache': self.cache})
        res = req.get_response(self.app)
        self.assertEquals(res.status_int, 200)

        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY1'), 'sample1')
        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY2'), 'sample2')
        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY3'), None)
 
    def test_get_object(self):
        req = Request.blank('/v1/a/c/o', environ={
            'REQUEST_METHOD': 'GET', 'swift.cache': self.cache,
            'swift.object/a/c/o': {'meta': {
                'entry4': 'sample4',
                'entry5': 'sample5',
                'entry6': 'sample6',
            }},
        })
        res = req.get_response(self.app)
        self.assertEquals(res.status_int, 200)

        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY1'), 'sample1')
        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY2'), 'sample2')
        self.assertEquals(res.environ.get(
            'HTTP_X_CONTAINER_METADATA_ENTRY3'), None)
 
        self.assertEquals(res.environ.get(
            'HTTP_X_OBJECT_METADATA_ENTRY4'), 'sample4')
        self.assertEquals(res.environ.get(
            'HTTP_X_OBJECT_METADATA_ENTRY5'), 'sample5')
        self.assertEquals(res.environ.get(
            'HTTP_X_OBJECT_METADATA_ENTRY6'), None)

