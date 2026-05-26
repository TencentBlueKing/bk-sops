/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

(function () {

    function validate_not_empty(self, value, allow_op_type, description) {
        let result = {
            result: true,
            error_message: ""
        };

        if (!self.get_parent) {
            return result;
        }

        let op_type = self.get_parent().get_parent().get_child('nodemgr_operation_type');
        if (op_type && op_type.value === allow_op_type) {
            if (value === '') {
                result.result = false;
                result.error_message = gettext(description);
            }
        }

        return result;
    }

    $.atoms.nodemgr_operate_plugin = [
        {
            tag_code: "nodemgr_biz_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                allowCreate: true,
                hookable: true,
                remote: true,
                remote_url: $.context.get("site_url") + "pipeline/cc_get_business_list/",
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
            },
        },
        {
            tag_code: "nodemgr_op_info",
            type: "combine",
            attrs: {
                name: gettext("操作类型"),
                hookable: true,
                children: [
                    {
                        tag_code: "nodemgr_operation_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作类型"),
                            hookable: true,
                            items: [
                                {value: "install", text: gettext("安装")},
                                {value: "uninstall", text: gettext("卸载")}
                            ],
                            default: "install",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "init",
                                action: function (value) {
                                    // 统一以 change 事件抛出
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_install",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "plugin_name",
                                    type: "select",
                                    attrs: {
                                        name: gettext("插件名称"),
                                        placeholder: gettext("请选择插件"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_plugin/" + $.context.getBkBizId() + "/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '插件名称不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "plugin_version",
                                    type: "select",
                                    attrs: {
                                        name: gettext("插件版本"),
                                        placeholder: gettext("请选择插件版本"),
                                        remote: true,
                                        items: [],
                                        remote_url: "",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '插件版本不可为空');
                                                }
                                            }
                                        ],
                                    },
                                    events: [
                                        {
                                            source: "plugin_name",
                                            type: "change",
                                            action: function (value) {
                                                var items = this.get_parent().get_child("plugin_name").items;
                                                for (var i = 0; i < items.length; i++) {
                                                    var data = items[i].data;
                                                    if (data.name === value) {
                                                        this.remote_url = $.context.get("site_url") + "pipeline/nodemgr_get_plugin_version/" + data.pkg_name + "/";
                                                        this.remoteMethod();
                                                        break;  
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "install") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_uninstall",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'uninstall', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'uninstall', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "plugin_name",
                                    type: "select",
                                    attrs: {
                                        name: gettext("插件名称"),
                                        placeholder: gettext("请选择插件"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_plugin/" + $.context.getBkBizId() + "/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '插件名称不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "uninstall") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }
    ]
})();
