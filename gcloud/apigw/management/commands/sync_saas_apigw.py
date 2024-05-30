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

import os
import traceback

from django.core.management import call_command
from django.core.management.base import BaseCommand

import env


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--stage", default=["stage", "prod"], nargs="+", help="release stages")

    def handle(self, *args, **kwargs):
        if not env.IS_PAAS_V3:
            print("[bk-sops]current version is not open v3,skip sync_saas_apigw")
            return
        stage = kwargs.get("stage")
        definition_file_path = os.path.join(__file__.rsplit("/", 1)[0], "data/api-definition.yml")
        resources_file_path = os.path.join(__file__.rsplit("/", 1)[0], "data/api-resources.yml")

        print("[bk-sops]call sync_apigw_config with definition: %s" % definition_file_path)
        call_command("sync_apigw_config", file=definition_file_path)

        print("[bk-sops]call sync_apigw_stage with definition: %s" % definition_file_path)
        call_command("sync_apigw_stage", file=definition_file_path)

        print("[bk-sops]call sync_apigw_resources with resources: %s" % resources_file_path)
        call_command("sync_apigw_resources", file=resources_file_path)

        print("[bk-sops]call sync_resource_docs_by_archive with definition: %s" % definition_file_path)
        call_command("sync_resource_docs_by_archive", file=definition_file_path)

        print("[bk-sops]call create_version_and_release_apigw with definition: %s" % definition_file_path)
        call_command("create_version_and_release_apigw", "--generate-sdks", file=definition_file_path, stage=stage)

        print("[bk-sops]call fetch_apigw_public_key")
        call_command("fetch_apigw_public_key")

        print("[bk-sops]call fetch_esb_public_key")
        try:
            call_command("fetch_esb_public_key")
        except Exception:
            print("[bk-sops]this env has not bk-sops esb api,skip fetch_esb_public_key ")
            traceback.print_exc()
