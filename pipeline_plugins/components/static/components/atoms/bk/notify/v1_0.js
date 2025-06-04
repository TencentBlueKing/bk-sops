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
    $.atoms.bk_notify = [
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
            tag_code: "bk_notify_type",
            type: "checkbox",
            attrs: {
                name: gettext("通知方式"),
                hookable: true,
                items: [],
                default: [],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                _tag_init: function () {
                    let self = this;
                    let url = $.context.get('site_url') + 'core/api/get_msg_types/?only_cmsi=1';
                    $.ajax({
                        url: url,
                        type: 'GET',
                        dataType: 'json',
                        success: function (resp) {
                            if (!resp.result) {
                                show_msg(resp.message, 'error');
                            } else {
                                let data = resp.data.filter(function (item) {
                                    return item.is_active
                                });
                                let items = data.map(function (item) {
                                    return {"name": item.label, "value": item.type}
                                });
                                if (items.length > 0) {
                                    self.items = items;
                                }
                            }
                        },
                        error: function (resp) {
                            show_msg(resp.message, 'error');
                        }
                    })
                }
            }
        },
        {
            tag_code: "bk_receiver_info",
            type: "combine",
            attrs: {
                name: gettext("通知分组"),
                hookable: true,
                children: [
                    {
                        tag_code: "bk_receiver_group",
                        type: "checkbox",
                        attrs: {
                            name: gettext("固定分组"),
                            items: [
                                {name: gettext("运维人员"), value: "Maintainers"},
                                {name: gettext("产品人员"), value: "ProductPm"},
                                {name: gettext("开发人员"), value: "Developer"},
                                {name: gettext("测试人员"), value: "Tester"},
                            ],
                            default: ["Maintainers"],
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        var self = this;
                                        self.get_parent && self.get_parent().get_child('bk_more_receiver').validate()
                                        return {
                                            result: true,
                                            error_message: ""
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "bk_staff_group",
                        type: "select",
                        attrs: {
                            name: gettext("项目人员分组"),
                            placeholder: gettext("请选择项目人员分组"),
                            multiple: true,
                            remote: true,
                            remote_url: function () {
                                return $.context.canSelectBiz() ? '' : $.context.get('site_url') + 'pipeline/get_staff_groups/' + $.context.getProjectId() + '/'
                            },
                            remote_data_init: function (resp) {
                                return resp.data
                            },
                            disabled: $.context.canSelectBiz(),
                        }
                    },
                    {
                        tag_code: "bk_more_receiver",
                        type: "input",
                        attrs: {
                            name: gettext("附加人员"),
                            placeholder: gettext("填写用户名，多个用英文逗号 `,` 分隔"),
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value, parent_data) {
                                        var result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        if (
                                            parent_data.hasOwnProperty('bk_receiver_group') &&
                                            !(parent_data.bk_receiver_group.length > 0) &&
                                            !value && parent_data.hasOwnProperty('bk_staff_group') &&
                                            !(parent_data.bk_staff_group.length > 0)
                                        ) {
                                            result.result = false;
                                            result.error_message = gettext("固定分组、项目人员分组和附加人员不可同时为空");
                                        }
                                        return result;
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            tag_code: "notify",
            type: "radio",
            attrs: {
                name: gettext("通知执行人"),
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
                ],
                default: false,
                hookable: true,
            }
            },
        {
            tag_code: "bk_notify_title",
            type: "input",
            attrs: {
                name: gettext("通知主题"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "bk_notify_content",
            type: "textarea",
            attrs: {
                name: gettext("通知内容"),
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
