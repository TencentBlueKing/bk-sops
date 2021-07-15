/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
 (function () {
    $.atoms.cc_batch_transfer_host_module = [
        {
            tag_code: "cc_module_select_method",
            type: "radio",
            attrs: {
                name: gettext("填参方式"),
                hookable: false,
                items: [
                    { value: "manual", name: gettext("手动填写") },
                    { value: "auto", name: gettext("单行自动扩展") },
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
                    source: "cc_module_select_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                },
            ]
        },
        {
            tag_code: "cc_host_transfer_detail",
            type: "datatable",
            attrs: {
                pagination: true,
                name: gettext("主机所属模块修改详情"),
                table_buttons: [
                    {
                        type: "export",
                        text: gettext("导出"),
                        callback: function () {
                            this.export2Excel()
                        }
                    },
                    {
                        type: "import",
                        text: gettext("导入")
                    }
                ],
                columns: [
                    {
                        tag_code: "cc_transfer_host_ip",
                        type: "input",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("必填项"),
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "cc_transfer_host_target_module",
                        type: "input",
                        attrs: {
                            name: gettext("目标模块"),
                            placeholder: gettext("集群A>模块B"),
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    }
                ],
                add_btn: true,
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [],
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
            tag_code: "cc_transfer_host_template_break_line",
            type: "input",
            attrs: {
                name: gettext("自动扩展分隔符"),
                placeholder: gettext("可为空，单行自动扩展模式下每一行的换行符，默认使用 ,"),
                hookable: true
            },
            events: [
                {
                    source: "cc_module_select_method",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "auto") {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                }
            ],
        },

    ]
})();
