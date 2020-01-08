# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
from importlib import import_module
from collections import OrderedDict
from os import path

from six.moves import input

from django.core.management.base import CommandError

import blueapps
from blueapps.contrib.bk_commands.management.templates import \
    BlueTemplateCommand

platform_esb_minimum_version_map = OrderedDict(
    [('ieod', '0.0.39'),
     ('clouds', '0.0.42'),
     ('qcloud', '0.1.14'),
     ('tencent', '0.0.21'),
     ('open', '')]
)

platform_secret_key_length_map = {
    'ieod': 50,
    'clouds': 50,
    'qcloud': 50,
    'tencent': 50,
    'open': 36
}


class Command(BlueTemplateCommand):
    help = ('Creates a Django project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')
    missing_args_message = 'You must provide a project name.'

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the application or project.')
        parser.add_argument('directory', nargs='?',
                            help='Optional destination directory')
        parser.add_argument('--template',
                            help='The path or URL to load the template from.')
        parser.add_argument(
            '--secret_key',
            dest='secret_key',
            help='App secret of the application, you can also enter later.'
        )
        parser.add_argument(
            '--run_ver',
            dest='run_ver',
            choices=list(platform_esb_minimum_version_map.keys()),
            help='App run_ver of the application, you can also enter later.'
        )
        parser.add_argument(
            '--extension', '-e', dest='extensions',
            action='append', default=['py', 'txt'],
            help='The file extension(s) to render (default: "py,txt"). '
                 'Separate multiple extensions with commas, or use '
                 '-e multiple times.'
        )
        parser.add_argument(
            '--name', '-n', dest='files',
            action='append', default=[],
            help='The file name(s) to render. Separate multiple extensions '
                 'with commas, or use -n multiple times.'
        )

    def handle(self, **options):
        app_code, target = options.pop('name'), options.pop('directory')
        self.validate_name(app_code, 'project')

        # Check that the project_name cannot be imported.
        try:
            import_module(app_code)
        except ImportError:
            pass
        else:
            raise CommandError('%r conflicts with the name of an existing '
                               'Python module and cannot be used as a '
                               'project name. Please try another name.' %
                               app_code)

        run_ver = blueapps.get_run_ver() or options.get('run_ver')
        # Create a random SECRET_KEY to put it in the main settings.
        if not options.get('secret_key'):
            secret_key = input('secret_key: ').strip()
            if not run_ver:
                run_ver = self.confirm_run_ver()
            if not secret_key or len(secret_key) != \
                    platform_secret_key_length_map[run_ver]:
                raise CommandError("secret_key is necessary and "
                                   "it's length is %s" %
                                   platform_secret_key_length_map[run_ver])
            options['secret_key'] = secret_key
        options['run_ver'] = run_ver
        options['app_code'] = app_code
        options['blueapps_version'] = blueapps.__version__
        options[
            'esb_sdk_minimum_version'] = platform_esb_minimum_version_map.get(
            run_ver)
        project_name = 'trunk'
        super(Command, self).handle('project', project_name, target,
                                    **options)

        # 根据版本确定requirements.txt
        if target is None:
            top_dir = path.join(os.getcwd(), project_name)
        else:
            top_dir = os.path.abspath(path.expanduser(target))
        # open版本的requirements-open.txt路径
        open_requirements_file = os.path.join(top_dir, 'requirements-open.txt')
        # v3版本的requirements-v3.txt路径
        v3_requirements_file = os.path.join(top_dir, 'requirements-v3.txt')
        # 最终的requirements.txt路径
        requirements_file = os.path.join(top_dir, 'requirements.txt')
        # open保留requirements-open.txt,并重命名为requirements.txt
        if run_ver == 'open':
            os.remove(v3_requirements_file)
            os.rename(open_requirements_file, requirements_file)
        # v3(ieod,qcloud,clouds,tencent)保留requirements-v3.txt,并重命名为requirements.txt
        else:
            os.remove(open_requirements_file)
            os.rename(v3_requirements_file, requirements_file)

    def confirm_run_ver(self):
        run_ver_choice = list(platform_esb_minimum_version_map.keys())
        choice = self.choice_input(
            'Please select a run version:', run_ver_choice)
        return run_ver_choice[choice - 1]

    def choice_input(self, question, choices):
        self.stdout.write(question)
        for i, choice in enumerate(choices):
            self.stdout.write(' %s -> %s' % (i + 1, choice))
        result = input('Select an option: ').strip()
        while True:
            try:
                value = int(result)
                if 0 < value <= len(choices):
                    return value
            except ValueError:
                pass
            result = input('Please select a valid option: ')
