# -*- coding: utf-8 -*-
import io
import re
import json
import os
import sys
import shutil
from os import path
from codecs import open

import django
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.conf import settings

import blueapps
PY_VER = sys.version


class Command(TemplateCommand):
    help = u"基于蓝鲸开发框架初始化开发样例"

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs='?', default='./',
                            help='Optional destination directory')

    def handle(self, **options):
        target = options.pop('directory')

        # 先获取原内容
        old_file = open('config/default.py', encoding='utf-8')

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

        base_subdir = 'example_template'

        append_file_tuple = (('', 'requirements.txt'),)

        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        template_dir = path.join(blueapps.__path__[0], 'conf', base_subdir)
        run_ver = None
        conf_file = open(path.join(os.getcwd(), 'config', '__init__.py'), encoding='utf-8')
        for line in conf_file.readlines():
            if line.startswith('RUN_VER'):
                run_ver = re.search("\'(.+)\'", line).group(1)
        conf_file.close()

        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            relative_dir = root[prefix_length:]

            target_dir = path.join(top_dir, relative_dir)
            if not path.exists(target_dir):
                os.mkdir(target_dir)

            flag = root.endswith('sites')
            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__' or (flag and dirname != run_ver):
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class', '.json')):
                    # Ignore some files as they cause various breakages.
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

        # 处理open版本导入的blueking与其他版本不同的情况
        test_component_base = path.join(top_dir, 'blueapps_example', 'test_component')
        test_app_tags_base = path.join(top_dir, 'blueapps_example', 'test_app_tags')
        if run_ver == 'open':
            os.remove(path.join(test_component_base, 'views.py'))
            shutil.move(path.join(test_component_base, 'views_open.py'), path.join(test_component_base, 'views.py'))
            os.remove(path.join(test_app_tags_base, 'views.py'))
            shutil.move(path.join(test_app_tags_base, 'views_open.py'), path.join(test_app_tags_base, 'views.py'))
        else:
            os.remove(path.join(test_component_base, 'views_open.py'))
            os.remove(path.join(test_app_tags_base, 'views_open.py'))
        # 将静态文件夹移到项目根目录的static文件夹中
        shutil.move(path.join(top_dir, 'blueapps_example', 'static', 'blueapps_example'),
                    path.join(top_dir, 'static'))
        shutil.rmtree(path.join(top_dir, 'blueapps_example', 'static'))

        # 修改文件
        modify_default_file(old_file)


# 获取原先的 default 文件并对其进行追加和覆盖
def modify_default_file(old_file_object):
    # 打开覆盖前的文件和替换的 json 文件
    with open("%s/conf/example_template/config/default.json" % blueapps.__path__[0], 'r') as json_file:
        with old_file_object as old_file:
            # 获取 json 数据内容
            result_content = old_file.read()
            json_dict = json.load(json_file)
            # 根据 key 进行替换会追加内容
            for replace_property in json_dict:
                # 获得 key 值
                propertys = json_dict.get(replace_property)
                # 寻找 key 值所在位置
                start_index = result_content.find(str(replace_property))
                # 获得 key 的 content 内容
                content = propertys.get('content')
                # mode 为 add 追加内容
                if propertys.get('mode') == 'add':
                    end_index = result_content.find(')', start_index) - 1
                    temp_content = result_content[start_index:end_index].strip()
                    # 检查最后一个是不是,结尾
                    if temp_content[-1] == ',' or temp_content[-1] == '(':
                        temp_content += '\n'
                    else:
                        temp_content += ',\n'
                    # 内容替换 content 需要进行 str 方法转换
                    result_content = ''.join(
                        [result_content[:start_index], temp_content,
                         str(content),
                         result_content[end_index:]])
                # mode 为 cover 进行覆盖内容
                elif propertys.get('mode') == 'cover':
                    end_index = result_content.find('False', start_index)
                    # 即最后一个是 True 不需要做任何覆盖
                    if end_index == -1:
                        continue
                    # 需要位移 start_index 防止覆盖变量名称
                    start_index += len(replace_property)
                    # 内容覆盖
                    result_content = ''.join(
                        [result_content[:start_index], str(content),
                         result_content[end_index + 5:]])
                else:
                    # 其他情况
                    break
            with open('config/default.py', 'w', encoding='utf-8') as default_file:
                default_file.write(result_content)
