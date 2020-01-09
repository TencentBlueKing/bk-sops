/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
[
    {
        tag_code: "job_id",
        type: "input",
        attrs: {
            name: gettext("JOB 任务 ID"),
            disabled: true,
            value: $.context.getOuput("job_inst_id")
        }
    },
    {
        tag_code: "job_url",
        type: "input",
        attrs: {
            name: gettext("JOB 任务链接"),
            disabled: true,
            value: $.context.getOuput("job_inst_url")
        }
    },
    {
        tag_code: "node_status",
        type: "input",
        attrs: {
            name: gettext("任务状态展示"),
            disabled: true,
            value: $.context.getNodeStatus()
        }
    }
]