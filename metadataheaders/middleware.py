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


from swift.common.swob import wsgify
from swift.common.utils import split_path
from swift.proxy.controllers.base import get_container_info, get_object_info


class MetadataHeadersMiddleware(object):
    def __init__(self, app, conf, *args, **kwargs):
        self.app = app

        header_container_metadata = conf.get('header_container_metadata', '')
        self.header_container_metadata = [
            name.strip()
            for name in header_container_metadata.split(',')
            if name.strip()]

        header_object_metadata = conf.get('header_object_metadata', '')
        self.header_object_metadata = [
            name.strip()
            for name in header_object_metadata.split(',')
            if name.strip()]

    @wsgify
    def __call__(self, request):
        try:
            (version, account, container, objname) = split_path(
                request.path_info, 1, 4, True)
        except ValueError:
            return self.app

        if container and self.header_container_metadata:
            container_info = get_container_info(request.environ, self.app)
            for key in self.header_container_metadata:
                value = container_info.get('meta', {}).get(key)
                if value:
                    keyname = 'X-CONTAINER-METADATA-%s' % key.upper() 
                    request.headers[keyname] = value

        if objname and self.header_object_metadata:
            object_info = get_object_info(request.environ, self.app)
            for key in self.header_object_metadata:
                value = object_info.get('meta', {}).get(key)
                if value:
                    keyname = 'X-OBJECT-METADATA-%s' % key 
                    request.headers[keyname] = value

        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def metadata_header_filter(app):
        return MetadataHeadersMiddleware(app, conf)
    return metadata_header_filter
