# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import traceback
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import (
    handle_api_error,
)

from gcloud.conf import settings
from pipeline_plugins.components.utils import bcs_client


logger = logging.getLogger('celery')

__group_name__ = _(u"容器管理平台(BCS)")

bcs_handle_api_error = partial(handle_api_error, __group_name__)

BCS_INSTANTCE_STATUS_RUNNING = 'running'
BCS_TASK_STATUS_FINISH = 'finish'
BCS_TASK_STATUS_FAILED = 'failed'
BCS_COMMAND_EXIT_SUCCESS = 0

BCS_MAX_SCHEDULE_TIMES = 120


class BcsMesosCreateService(Service):

    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def inputs_format(self):
        return []

    def outputs_format(self):
        return [
            self.OutputItem(name='version id',
                            key='version_id',
                            type='int',
                            schema=IntItemSchema(description='')),
            self.OutputItem(name='template id',
                            key='template_id',
                            type='int',
                            schema=IntItemSchema(description='')),
            self.OutputItem(name='instance id list',
                            key='instance_id_list',
                            type='list',
                            schema=ArrayItemSchema(
                                description='',
                                item_schema=IntItemSchema(description=''))),
        ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        bk_biz_id = parent_data.inputs.bk_biz_id
        project_id = data.inputs.bcs_create_project_id
        bcs_create_set = data.inputs.bcs_create_set
        bcs_create_vars = data.inputs.bcs_create_vars

        # assemble cluster_ns_info
        cluster_ns_info = {
            bcs_create_set: {}
        }
        for var in bcs_create_vars:
            cluster_ns_info[bcs_create_set].setdefault(
                var['namespace_name'],
                {}
            ).update({var['key']: var['value']})

        bcs_create_muster_ver = data.inputs.bcs_create_muster_ver
        version_id, show_version_id = bcs_create_muster_ver.split('_', 1)
        version_id = int(version_id)
        show_version_id = int(show_version_id)

        obj_type = data.inputs.bcs_create_obj_type
        templates = data.inputs.bcs_create_template
        # assemble instance_entity
        instance_entity = {
            obj_type: []
        }
        for tmpl in templates:
            tid, name = tmpl.split('_', 1)
            instance_entity[obj_type].append({
                'id': int(tid),
                'name': name
            })

        bcs_kwargs = dict(
            bk_biz_id=bk_biz_id,
            project_id=project_id,
            cluster_ns_info=cluster_ns_info,
            version_id=version_id,
            show_version_id=show_version_id,
            instance_entity=instance_entity
        )
        client = bcs_client.BCSClient()
        bcs_result = client.create_instance(**bcs_kwargs)

        if not bcs_result['result']:
            message = bcs_handle_api_error('bcs.create_instance', bcs_kwargs, bcs_result)
            self.logger.error(message)
            self.outputs.ex_data = message
            return False

        self.outputs.version_id = bcs_result['data']['version_id']
        self.outputs.template_id = bcs_result['data']['template_id']
        self.outputs.instance_id_list = bcs_result['data']['inst_id_list']

        return True

    def schedule(self, data, parent_data, callback_data=None):
        statuses = []
        client = bcs_client.BCSClient()

        for instance_id in data.outputs.instance_id_list:
            bcs_kwargs = dict(
                bk_biz_id=parent_data.inputs.bk_biz_id,
                project_id=data.inputs.bk_biz_id,
                instance_id=instance_id
            )
            bcs_result = client.get_instance_status(**bcs_kwargs)
            if not bcs_result['result']:
                self.logger.error(bcs_handle_api_error('bcs.get_instance_status', bcs_kwargs, bcs_result))
                return True
            statuses.append(bcs_result['data']['status'])

        if all([s == BCS_INSTANTCE_STATUS_RUNNING for s in statuses]):
            self.finish_schedule()

        if data.get_one_of_outputs('schedule_count') is None:
            data.outpus.schedule_count = 0

        data.outpus.schedule_count += 1

        if data.outpus.schedule_count >= BCS_MAX_SCHEDULE_TIMES:
            data.outpus.ex_data = 'bcs instance status wait timeout'
            return False

        return True


class BcsMesosCreateComponent(Component):
    name = _(u'Mesos Create')
    code = 'bcs_mesos_create'
    bound_service = BcsMesosCreateService
    form = '%scomponents/atoms/bcs/bcs_mesos_create.js' % settings.STATIC_URL


class BcsMesosRollingUpdateService(Service):

    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def inputs_format(self):
        return []

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        bk_biz_id = parent_data.inputs.bk_biz_id
        project_id = data.inputs.bcs_create_project_id
        instance_id = data.inputs.bcs_rollingupdate_app
        instance_num = data.inputs.bcs_rollingupdate_inst_num
        version_id = int(data.inputs.bcs_rollingupdate_app_ver)
        user_vars = data.inputs.bcs_rollingupdate_vars

        # assemble varaibles
        variable = {var['key']: var['value'] for var in user_vars}

        bcs_kwargs = dict(
            bk_biz_id=bk_biz_id,
            project_id=project_id,
            instance_id=instance_id,
            instance_num=instance_num,
            version_id=version_id,
            variable=variable
        )
        client = bcs_client.BCSClient()
        bcs_result = client.update_instance(**bcs_kwargs)

        if not bcs_result['result']:
            message = bcs_handle_api_error('bcs.update_instance', bcs_kwargs, bcs_result)
            self.logger.error(message)
            self.outputs.ex_data = message
            return False

        self.outputs.instance_id = instance_id
        return True

    def schedule(self, data, parent_data, callback_data=None):
        client = bcs_client.BCSClient()

        bcs_kwargs = dict(
            bk_biz_id=parent_data.inputs.bk_biz_id,
            project_id=data.inputs.bk_biz_id,
            instance_id=data.outputs.instance_id
        )
        bcs_result = client.get_instance_status(**bcs_kwargs)
        if not bcs_result['result']:
            self.logger.error(bcs_handle_api_error('bcs.get_instance_status', bcs_kwargs, bcs_result))
            return True

        if bcs_result['data']['status'] == BCS_INSTANTCE_STATUS_RUNNING:
            self.finish_schedule()

        if data.get_one_of_outputs('schedule_count') is None:
            data.outpus.schedule_count = 0

        data.outpus.schedule_count += 1

        if data.outpus.schedule_count >= BCS_MAX_SCHEDULE_TIMES:
            data.outpus.ex_data = 'bcs instance status wait timeout'
            return False

        return True


class BcsMesosCreateComponent(Component):
    name = _(u'Mesos Rollingupdate')
    code = 'bcs_mesos_rollingupdate'
    bound_service = BcsMesosRollingUpdateService
    form = '%scomponents/atoms/bcs/bcs_mesos_rollingupdate.js' % settings.STATIC_URL


class BcsMesosCommandService(Service):

    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def inputs_format(self):
        return []

    def outputs_format(self):
        return [
            self.OutputItem(name='task id',
                            key='task_id',
                            type='int',
                            schema=IntItemSchema(description='')),
        ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        bk_biz_id = parent_data.inputs.bk_biz_id
        project_id = data.inputs.bcs_create_project_id
        instance_id = data.inputs.bcs_command_app
        username = data.inputs.bcs_command_user.strip()
        work_dir = data.inputs.bcs_command_work_dir.strip()
        reserve_time = data.inputs.bcs_command_task_ttl
        privileged = data.inputs.bcs_command_has_privilege
        user_vars = data.inputs.bcs_rollingupdate_vars

        # env assemble
        env = ['{key}={value}'.format(var['key'], var['value']) for var in user_vars]

        # command assemble
        command_base = data.inputs.bcs_command_cmd.strip()
        command_param = data.inputs.bcs_command_param.strip()
        command = [command_base]
        command.extend(command_param.split(' '))

        bcs_kwargs = dict(
            bk_biz_id=bk_biz_id,
            project_id=project_id,
            instance_id=instance_id,
            command=command,
            username=username,
            work_dir=work_dir,
            privileged=privileged,
            reserve_time=reserve_time,
            env=env
        )
        client = bcs_client.BCSClient()
        bcs_result = client.send_command(**bcs_kwargs)

        if not bcs_result['result']:
            message = bcs_handle_api_error('bcs.send_command', bcs_kwargs, bcs_result)
            self.logger.error(message)
            self.outputs.ex_data = message
            return False

        data.outputs.task_id = bcs_result['data']['task_id']
        return True

    def schedule(self, data, parent_data, callback_data=None):

        client = bcs_client.BCSClient()
        bcs_kwargs = dict()
        bcs_result = client.get_command_status(
            bk_biz_id=parent_data.inputs.bk_biz_id,
            project_id=data.inputs.project_id,
            task_id=data.outputs.task_id
        )

        if not bcs_result['result']:
            self.logger.error(bcs_handle_api_error('bcs.get_command_status', bcs_kwargs, bcs_result))
            return True

        statuses = set()
        exitcodes = set()

        for task_group in bcs_result['data']['taskgroups']:
            for task in task_group['tasks']:
                statuses.add(task['status'])
                exitcodes.add(task['commInspect']['exitCode'])

        if BCS_TASK_STATUS_FAILED in statuses:
            data.outputs.ex_data = 'bcs command task failed'
            return False

        if statuses == {BCS_TASK_STATUS_FINISH} and exitcodes == {0}:
            self.finish_schedule()
            return True

        return True


class BcsMesosCreateComponent(Component):
    name = _(u'Mesos Command')
    code = 'bcs_mesos_command'
    bound_service = BcsMesosCommandService
    form = '%scomponents/atoms/bcs/bcs_mesos_command.js' % settings.STATIC_URL
