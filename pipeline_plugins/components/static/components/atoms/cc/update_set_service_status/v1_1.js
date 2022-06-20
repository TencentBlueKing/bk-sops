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
    $.atoms.cc_update_set_service_status = [
        {
            tag_code: "set_select_method",
            type: "radio",
            attrs: {
                name: gettext("传参形式"),
                hookable: false,
                items: [
                    {value: "name", name: gettext("Set名称")},
                    {value: "id", name: gettext("Set ID")},
                    {value: "custom", name: gettext("自定义")},
                ],
                default: "name",
                validation: [
                    {
                        type: "required"
                    }
                ],
            },
            events: [
                {
                    source: "set_select_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "set_attr_id",
            type: "input",
            attrs: {
                name: gettext("集群属性ID"),
                placeholder: gettext("用英文','分割，集群范围中填写的值会在此处填写的属性 ID 的值上进行过滤"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var result = {
                                result: true,
                                error_message: ""
                            };
                            var self = this;
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('set_select_method').value === "custom" && value.length===0 ) {
                                result.result = false;
                                result.error_message = gettext("传参形式为自定义时必填");
                            }

                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "set_select_method",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "custom") {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                }
            ],
        },
        {
            tag_code: "set_list",
            type: "textarea",
            attrs: {
                name: gettext("集群范围"),
                placeholder: gettext("多个集群使用英文','分割"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "set_status",
            type: "select",
            attrs: {
                name: gettext("服务状态"),
                allowCreate: true,
                placeholder: gettext('请选择'),
                hookable: true,
                remote: true,
                remote_url: $.context.get('site_url') + 'pipeline/cc_search_status_options/' + $.context.getBkBizId() + '/',
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
        },
    ]

})();
