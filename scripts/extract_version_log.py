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

import sys
import yaml
from pathlib import Path
from datetime import datetime


def extract_logs(log_yaml, version_logs):
    logs = yaml.load(log_yaml)
    logs.pop("i18n", None)

    for section, contents in logs.items():
        if contents:
            version_logs.setdefault(section, []).extend(contents)

    return version_logs


if __name__ == "__main__":

    version = sys.argv[1]

    version_logs = {}

    # extract version log
    for fpath in Path("dev_log/dev").glob("*.yaml"):
        with open(fpath) as log_file:
            extract_logs(log_file, version_logs)

    for fpath in Path("dev_log/dev").glob("*.yml"):
        with open(fpath) as log_file:
            extract_logs(log_file, version_logs)

    # write version log
    with open("docs/release.md") as f:
        lines = f.readlines()

    logs_text = ""
    for section, content in version_logs.items():
        logs_text = "{logs}\n- {section}".format(logs=logs_text, section=section)
        for line in content:
            logs_text = "{logs}\n  - {line}".format(logs=logs_text, line=line)

    lines[1] = "\n## {version}\n{logs}\n\n".format(version=version, logs=logs_text)

    # write version logs to release
    with open("docs/release.md", "w") as f:
        for line in lines:
            f.write(line)

    # create version log file
    with open(
        "version_log/version_logs_md/V{version}_{date}.md".format(
            version=version, date=datetime.now().strftime("%Y-%m-%d")
        ),
        "w",
    ) as f:
        logs_text = logs_text.replace("- feature", "## feature")
        logs_text = logs_text.replace("- improvement", "## improvement")
        logs_text = logs_text.replace("- bugfix", "## bugfix")
        f.write(logs_text)
