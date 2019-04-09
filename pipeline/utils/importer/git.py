# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import urlparse
import urllib2

from pipeline.utils.importer.base import NonstandardModuleImporter

logger = logging.getLogger(__name__)


class GitRepoModuleImporter(NonstandardModuleImporter):

    def __init__(self, modules, repo_raw_url, branch, use_cache=True):
        super(GitRepoModuleImporter, self).__init__(modules=modules)
        self.repo_raw_url = repo_raw_url if repo_raw_url.endswith('/') else '%s/' % repo_raw_url
        self.branch = branch
        self.use_cache = use_cache
        self.file_cache = {}
        self.error_cache = {}

    def is_package(self, fullname):
        try:
            self._fetch_repo_file(self._file_url(fullname, is_pkg=True))
        except IOError:
            return False

        return True

    def get_code(self, fullname):
        return compile(self.get_source(fullname), self.get_file(fullname), 'exec')

    def get_source(self, fullname):
        try:
            return self._fetch_repo_file(self._file_url(fullname, is_pkg=self.is_package(fullname)))
        except IOError:
            raise ImportError('Can not find {module} in {repo}/{branch}'.format(module=fullname,
                                                                                repo=self.repo_raw_url,
                                                                                branch=self.branch))

    def get_path(self, fullname):
        return [self._file_url(fullname, is_pkg=True).rpartition('/')[0]]

    def get_file(self, fullname):
        return self._file_url(fullname, is_pkg=self.is_package(fullname))

    def _file_url(self, fullname, is_pkg=False):
        base_url = '%s/' % urlparse.urljoin(self.repo_raw_url, self.branch)
        path = fullname.replace('.', '/')
        file_name = '%s/__init__.py' % path if is_pkg else '%s.py' % path
        return urlparse.urljoin(base_url, file_name)

    def _fetch_repo_file(self, file_url):
        logger.info('Try to fetch git file: {file_url}'.format(file_url=file_url))
        if self.use_cache:

            if file_url in self.file_cache:
                logger.info('Content in cache for git file: {file_url} found'.format(file_url=file_url))
                return self.file_cache[file_url]

            if file_url in self.error_cache:
                logger.info('Error in cache for git file: {file_url} found'.format(file_url=file_url))
                raise self.error_cache[file_url]

            try:
                file_content = urllib2.urlopen(file_url).read()
            except IOError as e:
                logger.info('Error cached for git file: {file_url}'.format(file_url=file_url))
                self.error_cache[file_url] = e
                raise e

            self.file_cache[file_url] = file_content
            logger.info('Content cached for git file: {file_url}'.format(file_url=file_url))
            return file_content

        return urllib2.urlopen(file_url).read()
