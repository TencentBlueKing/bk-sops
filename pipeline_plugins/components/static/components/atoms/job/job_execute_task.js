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
    $.atoms.job_execute_task = [
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
            tag_code: "job_task_id",
            type: "select",
            attrs: {
                name: gettext("作业模板"),
                hookable: false,
                remote: true,
                remote_url: function () {
                    const url = $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/job_get_job_tasks_by_biz/' + $.context.getBkBizId() + '/';
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
                ],
                cols: 10
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
            tag_code: "button_refresh",
            type: "button",
            attrs: {
                hookable: false,
                type: "primary",
                title: '刷新',
                size: "normal",
                cols: 1,
                formViewHidden: true
            }
        },
        {
            tag_code: "job_global_var",
            type: "datatable",
            attrs: {
                name: gettext("全局变量"),
                hookable: true,
                deleteable: false,
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
                        type: "category",
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
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        $.ajax({
                            url: $.context.get('site_url') + 'pipeline/job_get_job_detail_by_biz/' + cc_id + '/' + value + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                } else {
                                    $this._set_value(resp.data.global_var)
                                }

                                $this.set_loading(false);
                            },
                            error: function () {
                                $this._set_value([]);
                                $this.set_loading(false);
                                show_msg('request job detail error', 'error');
                            }
                        });
                    }
                },
                {
                    source: "button_refresh",
                    type: "click",
                    action: function (value) {
                        const job_id = this.get_parent().get_child("job_task_id").value;
                        var $this = this;
                        this.changeHook(false);
                        if (job_id === '') {
                            this._set_value([]);
                            return;
                        }
                        this.set_loading(true);
                        const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                        $.ajax({
                            url: $.context.get('site_url') + 'pipeline/job_get_job_detail_by_biz/' + cc_id + '/' + job_id + '/',
                            type: 'GET',
                            dataType: 'json',
                            success: function (resp) {
                                var global_var = $this._get_value()
                                if (global_var) {
                                    var new_global_var = resp.data.global_var.map(function (item) {
                                        var target = global_var.find(function (old_item) {
                                            return old_item.name === item.name;
                                        });
                                        if (target) {
                                            item.value = target.value;
                                        }
                                        return item;
                                    })
                                    $this._set_value(new_global_var);
                                }
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
        },
        {
            tag_code: "ip_is_exist",
            type: "radio",
            attrs: {
                name: gettext("IP 存在性校验"),
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
                ],
                default: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
