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
    $.atoms.job_execute_task = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                disabled: $.context.project.from_cmdb,
                value: $.context.project.from_cmdb ? $.context.project.bk_biz_id : '',
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_task_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: function () {
                    url = $.context.project.from_cmdb ? $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + $.context.project.bk_biz_id + '/' : '';
                    return url;
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
                        cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                        if (cc_id !== '') {
                            this.remote_url = $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + cc_id + '/';
                            this.remoteMethod();
                        }
                    }
                },
                {
                    source: "biz_cc_id",
                    type: "change",
                    action: function (value) {
                        this._set_value('');
                        if (value === '') {
                            return;
                        }
                        this.remote_url = $.context.site_url + 'pipeline/job_get_job_tasks_by_biz/' + value + '/';
                        this.remoteMethod();
                    }
                }
            ]
        },
        {
            tag_code: "job_global_var",
            type: "datatable",
            attrs: {
                name: gettext("全局变量"),
                hookable: true,
                empty_text: gettext("没选中作业模板或当前作业模板全局变量为空"),
                columns: [
                    {
                        tag_code: "name",
                        type: "text",
                        attrs: {
                            name: gettext("参数名称"),
                        }
                    },
                    {
                        tag_code: "type",
                        type: "text",
                        attrs: {
                            name: gettext("参数类型"),
                            hidden: true,
                        }
                    },
                    {
                        tag_code: "value",
                        type: "textarea",
                        attrs: {
                            name: gettext("参数值"),
                            editable: true
                        }
                    },
                    {
                        tag_code: "description",
                        type: "text",
                        attrs: {
                            name: gettext("描述")
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_task_id",
                    type: "change",
                    action: function (value) {
                        var $this = this;
                        this.changeHook(false);
                        if (value === '') {
                            this._set_value([]);
                            return;
                        }
                        this.set_loading(true);
                        cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id').value;
                        $.ajax({
                            url: $.context.site_url + 'pipeline/job_get_job_detail_by_biz/' + cc_id + '/' + value + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                $this._set_value(resp.data.global_var);
                                $this.set_loading(false);
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                            },
                            error: function () {
                                $this._set_value([]);
                                $this.set_loading(false);
                                show_msg('request job detail error', 'error');
                            }
                        });
                    }
                }
            ]
        }
    ]
})();