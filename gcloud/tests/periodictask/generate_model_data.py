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
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.models import Snapshot, PipelineTemplate, PipelineInstance, TreeInfo

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.function.models import FunctionTask
from gcloud.periodictask.models import PeriodicTask

from gcloud.core.models import Project
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


class GenerateBaseTestData:
    def __init__(self):
        self.project = None
        self.snapshot = None
        self.pipeline_template = None

    def set_and_get_data(self):
        self.project = Project.objects.create(
            name="xxxxx",
            time_zone="Asia/Shanghai",
            creator="admin"
        )
        self.snapshot = Snapshot.objects.create(
            md5sum="474e569c553cd05d92384cbc4dc45a6e",
            data={
                "activities": {
                    "node11f307055fdd3a1425906e20b371": {
                        "component": {
                            "code": "sleep_timer",
                            "data": {
                                "bk_timing": {
                                    "hook": False,
                                    "need_render": True,
                                    "value": "1"
                                },
                                "force_check": {
                                    "hook": False,
                                    "need_render": True,
                                    "value": True
                                }
                            },
                            "version": "legacy"
                        },
                        "error_ignorable": False,
                        "id": "node11f307055fdd3a1425906e20b371",
                        "incoming": [
                            "line586008cec072e27e852023206507"
                        ],
                        "loop": None,
                        "name": "定时",
                        "optional": True,
                        "outgoing": "line20a513ec6a92401e318dc7f109b5",
                        "stage_name": "",
                        "type": "ServiceActivity",
                        "retryable": True,
                        "skippable": True,
                        "auto_retry": {
                            "enable": False,
                            "interval": 0,
                            "times": 1
                        },
                        "timeout_config": {
                            "enable": False,
                            "seconds": 10,
                            "action": "forced_fail"
                        },
                        "labels": []
                    }
                },
                "constants": {},
                "end_event": {
                    "id": "node25b0b0bdc5278890d92a44b23e35",
                    "incoming": [
                        "line20a513ec6a92401e318dc7f109b5"
                    ],
                    "name": "",
                    "outgoing": "",
                    "type": "EmptyEndEvent",
                    "labels": []
                },
                "flows": {
                    "line586008cec072e27e852023206507": {
                        "id": "line586008cec072e27e852023206507",
                        "is_default": False,
                        "source": "nodee8a470688987b1c1be94bb840664",
                        "target": "node11f307055fdd3a1425906e20b371"
                    },
                    "line20a513ec6a92401e318dc7f109b5": {
                        "id": "line20a513ec6a92401e318dc7f109b5",
                        "is_default": False,
                        "source": "node11f307055fdd3a1425906e20b371",
                        "target": "node25b0b0bdc5278890d92a44b23e35"
                    }
                },
                "gateways": {},
                "line": [
                    {
                        "id": "line586008cec072e27e852023206507",
                        "source": {
                            "arrow": "Right",
                            "id": "nodee8a470688987b1c1be94bb840664"
                        },
                        "target": {
                            "arrow": "Left",
                            "id": "node11f307055fdd3a1425906e20b371"
                        }
                    },
                    {
                        "id": "line20a513ec6a92401e318dc7f109b5",
                        "source": {
                            "arrow": "Right",
                            "id": "node11f307055fdd3a1425906e20b371"
                        },
                        "target": {
                            "arrow": "Left",
                            "id": "node25b0b0bdc5278890d92a44b23e35"
                        }
                    }
                ],
                "location": [
                    {
                        "id": "nodee8a470688987b1c1be94bb840664",
                        "type": "startpoint",
                        "x": 40,
                        "y": 150
                    },
                    {
                        "id": "node11f307055fdd3a1425906e20b371",
                        "type": "tasknode",
                        "name": "定时",
                        "stage_name": "",
                        "x": 240,
                        "y": 140,
                        "group": "蓝鲸服务(BK)",
                        "icon": ""
                    },
                    {
                        "id": "node25b0b0bdc5278890d92a44b23e35",
                        "type": "endpoint",
                        "x": 540,
                        "y": 150
                    }
                ],
                "outputs": [],
                "start_event": {
                    "id": "nodee8a470688987b1c1be94bb840664",
                    "incoming": "",
                    "name": "",
                    "outgoing": "line586008cec072e27e852023206507",
                    "type": "EmptyStartEvent",
                    "labels": []
                }
            }
        )

        self.pipeline_template = PipelineTemplate.objects.create(
            name="xxx模板",
            creator="admin",
            template_id="nea6e1d7385e3c329944e5cf1e277d47",
            snapshot=Snapshot.objects.first()
        )

    def destory_data(self):
        Project.objects.all().delete()


class GeneratePeriodicTaskTestData(GenerateBaseTestData):
    def __init__(self):
        super().__init__()
        self.task_template = None

    def set_and_get_data(self):
        super().set_and_get_data()
        self.task_template = TaskTemplate.objects.create(
            project=Project.objects.first(),
            pipeline_template=PipelineTemplate.objects.first()
        )
        return self.project, self.task_template, self.snapshot.data

    def destory_data(self):
        super().destory_data()
        PipelinePeriodicTask.objects.all().delete()
        TaskTemplate.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        Snapshot.objects.all().delete()
        PeriodicTask.objects.all().delete()


class GenerateTemplateTestData(GenerateBaseTestData):
    def __init__(self):
        super().__init__()

    def set_and_get_data(self):
        super().set_and_get_data()
        return self.project, self.pipeline_template

    def destroy_data(self):
        super().destory_data()
        TaskTemplate.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        Snapshot.objects.all().delete()
        TaskTemplate.objects.all().delete()


class GenerateAppMakerTestData(GeneratePeriodicTaskTestData):
    def __init__(self):
        super().__init__()

    def set_and_get_data(self):
        super().set_and_get_data()
        return self.project, self.task_template

    def destory_data(self):
        super().destory_data()
        AppMaker.objects.all().delete()


class GenerateFunctionTaskTestData(GenerateBaseTestData):
    def __init__(self):
        super().__init__()
        self.tree_info = None
        self.pipeline_instance = None
        self.taskflow_instance = None

    def set_and_get_data(self):
        super().set_and_get_data()
        self.tree_info = TreeInfo.objects.create(
            data=Snapshot.objects.first().data
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id="nccbb7857572372f9b49fe2c05xxxxxx",
            template=PipelineTemplate.objects.first(),
            name="new20221115095047_周期执行_202211150955xx",
            creator="admin",
            executor="admin",
            snapshot=Snapshot.objects.first(),
            execution_snapshot=Snapshot.objects.first(),
            tree_info=TreeInfo.objects.first()
        )
        self.taskflow_instance = TaskFlowInstance.objects.create(
            project=Project.objects.first(),
            pipeline_instance=PipelineInstance.objects.first(),
            category="Default",
            template_id=1,
            create_info=1,
            current_flow="finished"
        )
        return self.taskflow_instance

    def destory_data(self):
        super().destory_data()
        FunctionTask.objects.all().delete()
        TreeInfo.objects.all().delete()
        PipelineInstance.objects.all().delete()
        TaskFlowInstance.objects.all().delete()
        TaskTemplate.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        Snapshot.objects.all().delete()


class GenerateTaskFlowTestData(GenerateBaseTestData):
    def __init__(self):
        super().__init__()
        self.tree_info = None
        self.pipeline_instance = None
        self.task_template = None

    def set_and_get_data(self):
        super().set_and_get_data()
        self.tree_info = TreeInfo.objects.create(
            data=Snapshot.objects.first().data
        )
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id="nccbb7857572372f9b49fe2c05xxxxxx",
            template=PipelineTemplate.objects.first(),
            name="new20221115095047_周期执行_202211150955xx",
            creator="admin",
            executor="admin",
            snapshot=Snapshot.objects.first(),
            execution_snapshot=Snapshot.objects.first(),
            tree_info=TreeInfo.objects.first()
        )
        self.task_template = TaskTemplate.objects.create(
            project=Project.objects.first(),
            pipeline_template=PipelineTemplate.objects.first()
        )

        return self.project, self.pipeline_instance

    def destory_data(self):
        super().destory_data()
        TreeInfo.objects.all().delete()
        PipelineInstance.objects.all().delete()
        TaskFlowInstance.objects.all().delete()
        TaskTemplate.objects.all().delete()
        PipelineTemplate.objects.all().delete()
        Snapshot.objects.all().delete()
