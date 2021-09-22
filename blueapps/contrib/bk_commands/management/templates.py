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

import errno
import os
import shutil
from os import path

import django
from django.core.management import CommandError
from django.core.management.templates import TemplateCommand
from django.core.management.utils import handle_extensions
from django.template import Context, Engine
from django.utils.version import get_docs_version

import blueapps


class BlueTemplateCommand(TemplateCommand):
    def handle_template(self, template, subdir):
        if template is None:
            return path.join(blueapps.__path__[0], "conf", subdir)

        else:
            return super(BlueTemplateCommand, self).handle_template(template, subdir)

    def handle(self, app_or_project, name, target=None, **options):
        self.app_or_project = app_or_project
        self.paths_to_remove = []
        self.verbosity = options["verbosity"]

        self.validate_name(name, app_or_project)
        # if some directory is given, make sure it's nicely expanded
        top_dir = self.get_top_dir(target, name)

        extensions = tuple(handle_extensions(options["extensions"]))
        extra_files = ["csrftoken.js"]
        for file in options["files"]:
            extra_files.extend(map(lambda x: x.strip(), file.split(",")))
        if self.verbosity >= 2:
            self.stdout.write(
                "Rendering %s template files with "
                "extensions: %s\n" % (app_or_project, ", ".join(extensions))
            )
            self.stdout.write(
                "Rendering %s template files with "
                "filenames: %s\n" % (app_or_project, ", ".join(extra_files))
            )

        base_name = "%s_name" % app_or_project
        base_subdir = "%s_template" % app_or_project
        base_directory = "%s_directory" % app_or_project

        context = Context(
            dict(
                options,
                **{
                    base_name: name,
                    base_directory: top_dir,
                    "docs_version": get_docs_version(),
                    "django_version": django.__version__,
                }
            ),
            autoescape=False,
        )

        # Setup a stub settings environment for template rendering
        from django.conf import settings

        if not settings.configured:
            settings.configure()

        template_dir = self.handle_template(options["template"], base_subdir)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = path.join(top_dir, relative_dir)
                if not path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if dirname.startswith(".") or dirname == "__pycache__":
                    dirs.remove(dirname)
                # 处理多版本差异，将只对指定版本初始化
                if "run_ver" in options and os.path.basename(root) == "sites":
                    if dirname != options["run_ver"]:
                        dirs.remove(dirname)
            self.remove_or_write_file(files, root, top_dir, relative_dir,
                                      base_name, name, extensions, extra_files, context)

        if self.paths_to_remove:
            if self.verbosity >= 2:
                self.stdout.write("Cleaning up temporary files.\n")
            for path_to_remove in self.paths_to_remove:
                if path.isfile(path_to_remove):
                    os.remove(path_to_remove)
                else:
                    shutil.rmtree(path_to_remove)

    def remove_or_write_file(self, files, root, top_dir, relative_dir,
                             base_name, name, extensions, extra_files,
                             context):
        for filename in files:
            if filename.endswith((".pyo", ".pyc", ".py.class")):
                # Ignore some files as they cause various breakages.
                continue
            old_path = path.join(root, filename)
            new_path = path.join(
                top_dir, relative_dir, filename.replace(base_name, name)
            )
            if path.exists(new_path):
                raise CommandError(
                    "%s already exists, overlaying a "
                    "project or app into an existing "
                    "directory won't replace conflicting "
                    "files" % new_path
                )

            # Only render the Python files, as we don't want to
            # accidentally render Django templates files
            with open(old_path, "rb") as template_file:
                content = template_file.read()
            if filename.endswith(extensions) or filename in extra_files:
                content = content.decode("utf-8")
                template = Engine().from_string(content)
                content = template.render(context)
                content = content.encode("utf-8")
            with open(new_path, "wb") as new_file:
                new_file.write(content)

            if self.verbosity >= 2:
                self.stdout.write("Creating %s\n" % new_path)
            try:
                shutil.copymode(old_path, new_path)
                self.make_writeable(new_path)
            except OSError:
                self.stderr.write(
                    "Notice: Couldn't set permission bits on %s. You're "
                    "probably using an uncommon filesystem setup. No "
                    "problem." % new_path,
                    self.style.NOTICE,
                )

    @staticmethod
    def get_top_dir(target, name):
        if target is None:
            top_dir = path.join(os.getcwd(), name)
            try:
                os.makedirs(top_dir)
            except OSError as err:
                if err.errno == errno.EEXIST:
                    message = "'%s' already exists" % top_dir
                else:
                    message = err
                raise CommandError(message)
        else:
            top_dir = os.path.abspath(path.expanduser(target))
            if not os.path.exists(top_dir):
                raise CommandError(
                    "Destination directory '%s' does not "
                    "exist, please create it first." % top_dir
                )
        return top_dir
