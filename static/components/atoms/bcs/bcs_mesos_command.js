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
    $.atoms.bcs_mesos_command = [
        {
            "tag_code": "bcs_command_data",
            "type": "combine",
            attrs: {
                "name": gettext("Command配置"),
                hookable: true,
                children: [
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("BCS项目ID"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                        },
                        "events": [],
                        "methods": {
                            _tag_init: function () {
                                this.emit_event(this.tagCode, "change", this.value)
                            }
                        },
                        "tag_code": "bcs_command_project_id"
                    },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("对象类型"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                                {
                                    "text": "Deployment",
                                    "value": "Deployment"
                                },
                                {
                                    "text": "Application",
                                    "value": "Application"
                                }
                            ],
                            "remote": false,
                            "remote_url": "",
                            "remote_data_init": function (e) { return e },
                            "placeholder": gettext("请选择对象类型"),
                        },
                        "events": [],
                        "methods": {
                            _tag_init: function () {
                                this.emit_event(this.tagCode, "change", this.value)
                            }
                        },
                        "tag_code": "bcs_command_obj_type"
                    },
                    // {
                    //     "type": "select",
                    //     "attrs": {
                    //         "name": gettext("所属命名空间"),
                    //         "default": "",
                    //         "value": "",
                    //         "validation": [
                    //             {
                    //                 type: "required"
                    //             }
                    //         ],
                    //         "items": [
                    //         ],
                    //         "remote": false,
                    //         "remote_url": "",
                    //         "remote_data_init": function (e) { return e },
                    //         "placeholder": gettext("请选择命名空间"),
                    //     },
                    //     "events": [],
                    //     "methods": {},
                    //     "tag_code": "bcs_command_namespace"
                    // },
                    {
                        "type": "select",
                        "attrs": {
                            "name": gettext("应用实例"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "items": [
                            ],
                            "remote": true,
                            "remote_url": function () {
                                var project_id = this.get_parent().get_child('bcs_command_project_id').value
                                if (!project_id) {
                                    return ''
                                }
                                var category = this.get_parent().get_child('bcs_command_obj_type').value
                                return this.instances_url($.context.getBkBizId(), project_id, category)
                            },
                            "remote_data_init": function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data
                            },
                            "placeholder": gettext("请选择应用实例"),
                        },
                        "events": [
                            {
                                source: "bcs_command_project_id",
                                type: "change",
                                action: function (value) {
                                    if (!value) {
                                        return
                                    }
                                    var category = this.get_parent().get_child('bcs_command_obj_type').value
                                    this.remote_url = this.instances_url($.context.getBkBizId(), value, category)
                                    this.remoteMethod()
                                }
                            },
                            {
                                source: "bcs_command_obj_type",
                                type: "change",
                                action: function (value) {
                                    if (!value) {
                                        return
                                    }
                                    var project_id = this.get_parent().get_child('bcs_command_project_id').value
                                    this.remote_url = this.instances_url($.context.getBkBizId(), project_id, value)
                                    this.remoteMethod()
                                }
                            }
                        ],
                        "methods": {
                            instances_url: function (bk_biz_id, project_id, category) {
                                url = $.context.get('site_url') + 'pipeline/bcs_get_instances/'
                                url += '?project_id=' + project_id + '&bk_biz_id=' + bk_biz_id + '&category=' + category
                                return url
                            }
                        },
                        "tag_code": "bcs_command_app"
                    },
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("命令"),
                            "default": "",
                            "value": "",
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                            "placeholder": gettext("请填写命令，例: ps"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_cmd"
                    },
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("命令参数"),
                            "default": "",
                            "value": "",
                            "placeholder": gettext("请填写命令参数，例: -a"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_param"
                    },
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("用户"),
                            "default": "",
                            "value": "",
                            "placeholder": gettext("请填写用户身份，不填则默认为 root"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_user"
                    },
                    {
                        "type": "input",
                        "attrs": {
                            "name": gettext("工作目录"),
                            "default": "",
                            "value": "",
                            "placeholder": gettext("请填写工作目录"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_work_dir"
                    },
                    {
                        "type": "radio",
                        "attrs": {
                            "name": gettext("拥有特权"),
                            "default": false,
                            "items": [
                                {
                                    "name": "是",
                                    "value": true
                                },
                                {
                                    "name": "否",
                                    "value": false
                                }
                            ],
                            "disabled": false,
                            "validation": [
                                {
                                    type: "required"
                                }
                            ],
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_has_privilege"
                    },
                    {
                        "type": "int",
                        "attrs": {
                            "name": gettext("任务信息保存时间"),
                            "default": "",
                            "value": "",
                            "placeholder": gettext("默认为24607分钟"),
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_command_task_ttl"
                    },
                    {
                        "type": "datatable",
                        "attrs": {
                            "name": gettext("环境变量"),
                            "hookable": false,
                            "default": "",
                            "columns": [
                                {
                                    "tag_code": "key",
                                    "type": "input",
                                    "attrs": {
                                        "name": "Key"
                                    }
                                },
                                {
                                    "tag_code": "value",
                                    "type": "input",
                                    "attrs": {
                                        "name": "Value"
                                    }
                                }
                            ],
                            "editable": true,
                            "value": [],
                            "add_btn": true,
                            "empty_text": "无数据",
                            "remote_url": "",
                            "remote_data_init": function (e) { return e },
                            "table_buttons": []
                        },
                        "events": [],
                        "methods": {},
                        "tag_code": "bcs_rollingupdate_vars"
                    }
                ]
            },
            "events": [],
        }
    ]
})();