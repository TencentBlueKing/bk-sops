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
    $.atoms.job_fast_execute_sql = [
        {
            tag_code: "job_sql_script_source",
            type: "radio",
            attrs: {
                name: gettext("脚本来源"),
                hookable: false,
                items: [
                    {value: "manual", name: gettext("手工录入")},
                    {value: "general", name: gettext("业务脚本")},
                ],
                default: "manual",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "job_sql_script_source",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "job_sql_content",
            type: "textarea",
            attrs: {
                name: gettext("脚本内容"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let self = this
                            let result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_sql_script_source')) {
                                if (self.get_parent().get_child('job_sql_script_source').value === "manual" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请输入脚本内容");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请输入脚本内容");
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_sql_script_source",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "manual") {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_sql_script_id",
            type: "select",
            attrs: {
                name: gettext("脚本列表"),
                placeholder: gettext("请选择作业平台上的SQL脚本"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/job_get_script_list/' + $.context.biz_cc_id + '/?type=general&script_type=6',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let self = this
                            let result = {
                                result: true,
                                error_message: ""
                            }
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_sql_script_source')) {
                                if (self.get_parent().get_child('job_sql_script_source').value === "general" && !value) {
                                    result.result = false;
                                    result.error_message = gettext("请选择脚本");
                                }
                            } else if (!value) {
                                result.result = false;
                                result.error_message = gettext("请选择脚本");
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_sql_script_source",
                    type: "change",
                    action: function (value) {
                        let self = this
                        if (value === "general") {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                }
            ]
        },
        {
            tag_code: "job_script_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒，为空时使用 JOB 默认值"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            let result = {
                                result: true,
                                error_message: ""
                            }
                            if (value && !Number(value)) {
                                result.result = false;
                                result.error_message = gettext("请输入数字");
                            }
                            return result;
                        }
                    }
                ]
            }
        },
        {
            tag_code: "job_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标IP"),
                placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行符分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_db_account",
            type: "select",
            attrs: {
                name: gettext("DB账户"),
                placeholder: gettext("请选择蓝鲸作业平台上已注册并授权的DB账号"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/job_get_own_db_account_list/' + $.context.biz_cc_id + '/',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required",
                    }
                ]
            },
        },
    ]
})();
