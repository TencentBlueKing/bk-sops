# -*- coding: utf-8 -*-
import io
import os
import sys
import shutil
from os import path

import django
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.conf import settings

import blueapps
PY_VER = sys.version


class Command(TemplateCommand):
    help = u"基于蓝鲸开发框架初始化小程序开发样例"

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs='?', default='./',
                            help='Optional destination directory')

    def handle(self, **options):
        target = options.pop('directory')

        # if some directory is given, make sure it's nicely expanded
        top_dir = path.abspath(path.expanduser(target))
        if not path.exists(top_dir):
            raise CommandError("Destination directory '%s' does not "
                               "exist, please init first." % top_dir)
        if not path.exists(path.join(top_dir, 'manage.py')):
            raise CommandError("Current directory '%s' is not "
                               "a django project dir, please init first. "
                               "(bk-admin init ${app_code})" %
                               top_dir)

        base_subdir = 'wxapp_template'

        append_file_tuple = (('', 'requirements.txt'),)

        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        template_dir = path.join(blueapps.__path__[0], 'conf', base_subdir)
        run_ver = None
        if PY_VER[0] == '2':
            conf_file = open(path.join(os.getcwd(), 'config', '__init__.py'))
        else:
            conf_file = open(path.join(os.getcwd(), 'config', '__init__.py'), encoding='utf-8')
        for line in conf_file.readlines():
            if line.startswith('RUN_VER'):
                run_ver = line[11:-2]
        conf_file.close()

        if run_ver != u'ieod':
            self.stderr.write(
                "Error: Currently only ieod version is supported. "
                "Your version is %s" % run_ver
            )
            sys.exit(-1)

        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            relative_dir = root[prefix_length:]

            target_dir = path.join(top_dir, relative_dir)
            if not path.exists(target_dir):
                os.mkdir(target_dir)

            flag = root.endswith('sites')
            for dirname in dirs[:]:
                if (
                        dirname.startswith('.') or
                        dirname == '__pycache__' or
                        (flag and dirname != run_ver)
                ):
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class', '.json')):
                    # Ignore some files as they cause various breakages.
                    if filename != u'app.json':
                        continue
                old_path = path.join(root, filename)
                new_path = path.join(top_dir, relative_dir, filename)
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[:-len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                with io.open(old_path, 'rb') as template_file:
                    content = template_file.read()
                w_mode = 'wb'
                for _root, _filename in append_file_tuple:
                    if _root == relative_dir and _filename == filename:
                        w_mode = 'ab'
                with io.open(new_path, w_mode) as new_file:
                    new_file.write(content)

                try:
                    shutil.copymode(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path, self.style.NOTICE)