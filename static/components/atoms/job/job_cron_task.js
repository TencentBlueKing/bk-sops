/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.job_cron_task = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                allowCreate: true,
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                disabled: !$.context.canSelectBiz(),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                _tag_init: function () {
                    if (this.value) {
                        return
                    }
                    this._set_value($.context.getBkBizId())
                }
            }
        },
        {
            tag_code: "job_cron_job_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_job_tasks_by_biz/' + $.context.getBkBizId() + '/'
                    return url
                },
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "biz_cc_id",
                    type: "init",
                    action: function () {
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        if (cc_id !== '') {
                            this.remote_url = $.context.get('site_url') + 'pipeline/job_get_job_tasks_by_biz/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        if ($.context.canSelectBiz()) {
                            this._set_value('');
                        }
                        if (value === '') {
                            return;
                        }
                        this.remote_url = $.context.get('site_url') + 'pipeline/job_get_job_tasks_by_biz/' + value + '/';
                        this.remoteMethod();
                    }
                }
            ]
        },
        {
            tag_code: "job_cron_name",
            type: "input",
            attrs: {
                name: gettext("定时作业名称"),
                hookable: false,
                placeholder: gettext("请填写定时作业名称"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "job_cron_job_id",
                    type: "change",
                    action: function (value) {
                        if (!value) {
                            return
                        }
                        var $this = this;
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        $.ajax({
                            url: $.context.get('site_url') + 'pipeline/job_get_job_tasks_by_biz/' + cc_id + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                let text = resp.data.filter((item) => {
                                    return item.value === value
                                })[0]['text'];
                                $this._set_value(text + '_' + (new Date()).getTime());
                            },
                            error: function () {
                                $this._set_value('');
                            }
                        });
                    }
                }
            ]
        },
        {
            tag_code: "job_cron_expression",
            type: "textarea",
            attrs: {
                name: gettext("定时规则"),
                hookable: true,
                placeholder: gettext("Crontab定时规则，请参考JOB平台定时任务Crontab规则"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_cron_status",
            type: "radio",
            attrs: {
                name: gettext("定时作业状态"),
                hookable: true,
                items: [
                    {value: 2, name: gettext("暂停")},
                    {value: 1, name: gettext("启动")},
                ],
                default: 2,
                validation: [
                    {
                        type: "required"
                    }
                ],
            }
        }
    ]
})();
