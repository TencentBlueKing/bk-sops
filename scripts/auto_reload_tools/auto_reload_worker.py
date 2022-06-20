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

# worker 自动重启补丁，改造 djcelery 命令行启动方式，增加监听指定文件变化，并自动重启worker的功能。

from __future__ import absolute_import, unicode_literals

import os
import sys
import subprocess
import threading
import time

import djcelery
from celery.bin import celery
from djcelery.app import app
from djcelery.management.base import CeleryCommand

from config import BASE_DIR
from scripts.auto_reload_tools.common import get_files_list

USE_AUTO_RELOAD = os.environ.get("USE_AUTO_PATCH")

base = celery.CeleryCommand(app=app)

_mtimes = {}

# django 扫描的文件列表, 支持多个文件夹进行监听
STATIC_DIRS = [os.path.join(BASE_DIR, "pipeline_plugins//components//collections")]

# 执行监听的后缀名
FILE_SUFFIX = "py"

_win = sys.platform == "win32"
# 文件退出码
TASK_FILE_MODIFIED = 1

# 定时扫描间隔
FILE_SCANNING_INTERVAL = 1


def code_changed():
    global _mtimes, _win
    for filename in get_files_list(STATIC_DIRS, FILE_SUFFIX):
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes:
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes[filename]:
            return TASK_FILE_MODIFIED
    return False


def restart_with_reloader(argv):
    args = [sys.executable] + argv
    while True:
        new_environ = os.environ.copy()
        new_environ["RUN_MAIN_CELERY"] = "true"
        exit_code = subprocess.call(args, env=new_environ)
        if exit_code != 3:
            return exit_code


def execute_from_commandline(argv):
    base.execute_from_commandline(["{0[0]} {0[1]}".format(argv)] + argv[2:],)


class Command(CeleryCommand):
    """The celery command."""

    help = "celery commands, see celery help"
    options = CeleryCommand.options + base.get_options() + base.preload_options

    def run_from_argv(self, argv):
        if os.environ.get("RUN_MAIN_CELERY") == "true":
            argv = self.handle_default_options(argv)
            f = threading.Thread(target=execute_from_commandline, args=(argv,))
            f.daemon = True
            f.start()
            while True:
                change = code_changed()
                if change == TASK_FILE_MODIFIED:
                    sys.exit(3)
                time.sleep(FILE_SCANNING_INTERVAL)
        else:
            try:
                exit_code = restart_with_reloader(argv)
                if exit_code < 0:
                    os.kill(os.getpid(), -exit_code)
                else:
                    sys.exit(exit_code)
            except KeyboardInterrupt:
                pass


def patch_worker_autoreload():
    # 只有本地配置了环境变量的情况下才会打补丁
    if USE_AUTO_RELOAD == "True":
        djcelery.management.commands.celery.Command = Command
