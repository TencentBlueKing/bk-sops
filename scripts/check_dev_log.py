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

import os
import yaml


DEV_LOG_TITLE = {"feature", "improvement", "bugfix"}


def check_dev_log(dir_path):
    absolute_dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir_path)
    assert os.path.isdir(absolute_dir_path), f"检查版本日志文件夹出错：文件夹{absolute_dir_path}不存在"
    for yaml_file in os.listdir(absolute_dir_path):
        with open(os.path.join(absolute_dir_path, yaml_file)) as data:
            dev_log = yaml.load(data, yaml.FullLoader)
            assert isinstance(dev_log, dict), f"{yaml_file}格式出错：版本日志需要符合yaml字典格式"
            assert all([isinstance(logs, list) for logs in dev_log.values()]), f"{yaml_file}格式出错：每个标题下版本日志需要是列表形式"
            assert all(
                [title in DEV_LOG_TITLE for title in dev_log.keys()]
            ), f"{yaml_file}格式出错: 版本日志标题需要满足{DEV_LOG_TITLE}中的一个"


if __name__ == "__main__":
    try:
        check_dev_log("dev_log/dev")
    except Exception as e:
        print(e)
        exit(1)
    exit(0)
