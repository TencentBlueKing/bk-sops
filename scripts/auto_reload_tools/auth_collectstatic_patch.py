# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


# django 自动重启补丁，在django原来的技术上添加对静态资源发生变化自动执行 collectstatic 并重启的能力。
# 使之更加符合 标准运维 插件开发的工作需求，提升插件开发效率


import os
import sys
import time
from itertools import chain

from django.apps import apps
from django.contrib.staticfiles.management.commands.collectstatic import Command
from django.utils import autoreload
from django.utils.autoreload import (
    FILE_MODIFIED,
    I18N_MODIFIED,
    RUN_RELOADER,
    USE_INOTIFY,
    _error_files,
    ensure_echo_on,
    gen_filenames,
    inotify_code_changed,
    reset_translations,
)

from config import BASE_DIR
from scripts.auto_reload_tools.common import get_files_list

_mtimes = autoreload._mtimes
_win = autoreload._win

USE_AUTO_RELOAD = os.environ.get("USE_AUTO_PATCH")

# django 扫描的文件列表, 支持多个文件夹进行监听
STATIC_DIRS = [os.path.join(BASE_DIR, "pipeline_plugins//components//static")]

# 执行监听的后缀名
FILE_SUFFIX = "js"


# 调用django collectstatic 的逻辑
def auto_collectstatic():
    c = Command()
    options = {
        "verbosity": 1,
        "settings": None,
        "pythonpath": None,
        "traceback": False,
        "no_color": False,
        "interactive": False,
        "post_process": True,
        "ignore_patterns": [],
        "dry_run": False,
        "clear": False,
        "link": False,
        "use_default_ignore_patterns": True,
    }
    c.interactive = options["interactive"]
    c.verbosity = options["verbosity"]
    c.symlink = options["link"]
    c.clear = options["clear"]
    c.dry_run = options["dry_run"]
    ignore_patterns = options["ignore_patterns"]
    if options["use_default_ignore_patterns"]:
        ignore_patterns += apps.get_app_config("staticfiles").ignore_patterns
    c.ignore_patterns = list(set(ignore_patterns))
    c.post_process = options["post_process"]
    c.collect()


def code_changed():
    global _mtimes, _win  # noqa: F824
    file_list = get_files_list(STATIC_DIRS, FILE_SUFFIX)
    for filename in chain(gen_filenames(), file_list):
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes:
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes[filename]:
            _mtimes = {}
            try:
                del _error_files[_error_files.index(filename)]
            except ValueError:
                pass
            return I18N_MODIFIED if filename.endswith(".mo") else FILE_MODIFIED
    return False


def reloader_thread():
    ensure_echo_on()
    if USE_INOTIFY:
        fn = inotify_code_changed
    else:
        fn = code_changed
    while RUN_RELOADER:
        change = fn()
        if change == FILE_MODIFIED:
            auto_collectstatic()
            sys.exit(3)  # force reload
        elif change == I18N_MODIFIED:
            reset_translations()
        time.sleep(1)


def patch_django_autoreload():
    # 只有本地配置了环境变量的情况下才会打补丁
    if USE_AUTO_RELOAD == "True":
        autoreload.code_changed = code_changed
        autoreload.reloader_thread = reloader_thread
