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
    $.atoms.nodeman_create_task = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
                remote_data_init: function (resp) {
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
            tag_code: "nodeman_bk_cloud_id",
            type: "input",
            attrs: {
                name: gettext("云区域ID"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_node_type",
            type: "radio",
            attrs: {
                name: gettext("节点类型"),
                hookable: true,
                items: [
                    {value: "AGENT", name: gettext("直连区域AGENT")},
                    {value: "PROXY", name: gettext("PROXY")},
                    {value: "PAGENT", name: gettext("非直连区域AGENT")}
                ],
                default: "AGENT",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_op_type",
                type: "select",
                attrs: {
                    name: gettext("操作类型"),
                    items: [
                        {value: "INSTALL", text: gettext("安裝")},
                        {value: "REINSTALL", text: gettext("重新安装")},
                        {value: "UNINSTALL", text: gettext("卸载")},
                        {value: "REMOVE", text: gettext("移除")},
                        {value: "UPGRADE", text: gettext("升级")},
                    ],
                    default: "INSTALL",
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
        },
        {
            tag_code: "nodeman_hosts",
            type: "datatable",
            attrs: {
                name: gettext("主机"),
                editable: true,
                add_btn: true,
                columns: [
                    {
                        tag_code: "conn_ips",
                        type: "textarea",
                        attrs: {
                            name: gettext("通信IP"),
                            placeholder: gettext("多个用,隔开"),
                            width: '100px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "login_ip",
                        type: "textarea",
                        attrs: {
                            name: gettext("登录IP"),
                            placeholder: gettext("可为空，适配复杂网络时填写"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "data_ip",
                        type: "textarea",
                        attrs: {
                            name: gettext("数据IP"),
                            placeholder: gettext("可为空，适配复杂网络时填写"),
                            width: '100px',
                            editable: true,

                        }
                    },
                    {
                        tag_code: "cascade_ip",
                        type: "textarea",
                        attrs: {
                            name: gettext("级联IP"),
                            placeholder: gettext("可为空，节点类型是 PROXY 时必填"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "os_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作系统类型"),
                            width: '100px',
                            items: [
                                {value: "LINUX", text: gettext("LINUX")},
                                {value: "WINDOWS", text: gettext("WINDOWS")},
                                {value: "AIX", text: gettext("AIX")}
                            ],
                            default: "LINUX",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "has_cygwin",
                        type: "select",
                        attrs: {
                            name: gettext("是否安装cygwin"),
                            items: [
                                {value: true, text: gettext("是")},
                                {value: false, text: gettext("否")},
                            ],
                            width: '100px',
                            default: false,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "port",
                        type: "input",
                        attrs: {
                            name: gettext("端口号"),
                            width: '100px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "account",
                        type: "input",
                        attrs: {
                            name: gettext("登录账号"),
                            width: '100px',
                            editable: true
                        }
                    },
                    {
                        tag_code: "auth_type",
                        type: "select",
                        attrs: {
                            name: gettext("认证方式"),
                            width: '100px',
                            items: [
                                {value: "PASSWORD", text: gettext("PASSWORD")},
                                {value: "KEY", text: gettext("KEY")}
                            ],
                            default: "PASSWORD",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "auth_key",
                        type: "input",
                        attrs: {
                            name: gettext("认证密钥"),
                            width: '100px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    }
                ],
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
