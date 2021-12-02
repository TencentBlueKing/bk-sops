# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import tempfile

from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
from django.template.context import _builtin_context_processors
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from mako import exceptions as mako_exceptions
from mako.lookup import TemplateLookup as MakoTemplateLookup
from mako.template import Template as MakoTemplate


class MakoTemplates(BaseEngine):
    app_dirname = settings.MAKO_DIR_NAME

    def __init__(self, params):
        params = params.copy()
        options = params.pop("OPTIONS").copy()
        super(MakoTemplates, self).__init__(params)

        # Defaut values for initializing the MakoTemplateLookup class
        # You can define them in the backend OPTIONS dict.
        options.setdefault("directories", self.template_dirs)
        options.setdefault("module_directory", tempfile.gettempdir())
        options.setdefault("input_encoding", "utf-8")
        options.setdefault("output_encoding", "utf-8")
        options.setdefault("encoding_errors", "replace")
        options.setdefault("collection_size", 500)
        options.setdefault(
            "default_filters",
            settings.MAKO_DEFAULT_FILTERS
            if hasattr(settings, "MAKO_DEFAULT_FILTERS")
            else [],
        )

        # Use context processors like Django
        context_processors = options.pop("context_processors", [])
        self.context_processors = context_processors

        # Use the mako template lookup class to find templates
        self.lookup = MakoTemplateLookup(**options)

    @cached_property
    def template_context_processors(self):
        context_processors = _builtin_context_processors
        context_processors += tuple(self.context_processors)
        return tuple(import_string(path) for path in set(context_processors))

    def from_string(self, template_code):
        try:
            return Template(MakoTemplate(template_code, lookup=self.lookup), [])
        except mako_exceptions.SyntaxException as err:
            raise TemplateSyntaxError(err.args)

    def get_template(self, template_name):
        try:
            return Template(
                self.lookup.get_template(template_name),
                self.template_context_processors,
            )
        except mako_exceptions.TemplateLookupException as err:
            raise TemplateDoesNotExist(err.args)
        except mako_exceptions.CompileException as err:
            raise TemplateSyntaxError(err.args)


class Template(object):
    def __init__(self, template, context_processors):
        self.template = template
        self.context_processors = context_processors

    def render(self, context=None, request=None):
        if context is None:
            context = {}

        if request is not None:
            for processor in self.context_processors:
                try:
                    context.update(processor(request))
                except Exception:  # pylint: disable=broad-except
                    pass

            context["request"] = request
            context["csrf_input"] = csrf_input_lazy(request)
            context["csrf_token"] = csrf_token_lazy(request)

        return self.template.render_unicode(**context)
