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

export default [
    {
        variableKey: "bk_receiver_info",
        tag_code: "bk_receiver_info",
        type: "combine",
        attrs: {
            name: "通知分组",
            hookable: true,
            children: [
                {
                    tag_code: "bk_receiver_group",
                    type: "checkbox",
                    attrs: {
                        name: "通知分组",
                        items: [
                            {name: "运维人员", value: "Maintainers"},
                            {name: "产品人员", value: "ProductPm"},
                            {name: "开发人员", value: "Developer"},
                            {name: "测试人员", value: "Tester"},
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
                    tag_code: "bk_more_receiver",
                    type: "input",
                    attrs: {
                        name: "附加人员",
                        placeholder: "填写用户名，多个用英文逗号 `,` 分隔",
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
                                        !value
                                    ) {
                                        result.result = false;
                                        result.error_message = "通知分组与附加人员不可同时为空"
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
        variableKey: "bk_notify_title",
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
    }
]
