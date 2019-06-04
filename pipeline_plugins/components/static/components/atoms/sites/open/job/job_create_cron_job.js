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
(function(){
    $.atoms.job_create_cron_job = [
        {
            tag_code: "job_task_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + $.context.biz_cc_id + '/',
                remote_data_init: function (resp) {
                    g_tasks = resp.data;
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
            tag_code: "cron_name",
            type: "input",
            attrs: {
                name: gettext("定时作业名称"),
                hookable: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "job_task_id",
                    type: "change",
                    action: function (value) {
                        $this = this;

                        g_tasks.forEach(function(el, index) {
                            if (value === el.value) {
                                $this._set_value(el.text + '_' + (new Date()).getTime());
                                return;
                            }
                        });

                    }
                }
            ]
        },
        {
            tag_code: "cron_status",
            type: "radio",
            attrs: {
                name: gettext("定时作业状态"),
                hookable: false,
                items: [
                    {value: "1", name: "启动"},
                    {value: "2", name: "暂停"}
                ],
                default: "2"
            }
        },
        {
            tag_code: "cron_expression",
            type: "textarea",
            attrs: {
                name: gettext("定时规则"),
                hookable: false,
                placeholder: gettext("定时规则，填写：秒 分 时 日 月 周 年（可选），如: 0 0/5 * * * ? 表示每5分钟执行一次，0 0 12 * * ? 2015表示2015年每天中午12点触发"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }

    ]
})();

