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
(function () {
    $.atoms.job_crontab_task = [
        {
            tag_code: "job_task_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + $.context.biz_cc_id + '/',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_cron_name",
            type: "input",
            attrs: {
                name: gettext("作业名称"),
                placeholder: gettext("为空则自动生成：作业名_时间戳"),
                hookable: true
            }
        },
        {
            tag_code: "job_cron_expression",
            type: "input",
            attrs: {
                name: gettext("定时表达式"),
                placeholder: gettext("0 0/5 * * * ?"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "cron_status",
            type: "radio",
            attrs: {
                name: gettext("任务状态"),
                hookable: true,
                items: [
                    {"name": gettext("关闭"), "value": "2"},
                    {"name": gettext("启动"), "value": "1"},
                ],
                default: "2",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();
