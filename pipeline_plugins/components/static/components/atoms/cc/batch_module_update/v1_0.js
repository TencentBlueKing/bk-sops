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
    $.atoms.cc_batch_module_update = [
        {
            tag_code: "cc_tag_method",
            type: "radio",
            attrs: {
                name: gettext("填参方式"),
                hookable: false,
                default: "custom",
                items: [
                    {value: "custom", name: gettext("手动填写")},
                    {value: "template", name: gettext("单行自动扩展")},
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "cc_tag_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value);
                    }
                },
            ],
        },
        {
            tag_code: "cc_module_update_data",
            type: "datatable",
            attrs: {
                pagination: true,
                name: gettext("拓扑模块属性修改"),
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
                remote_url: function () {
                    const url = $.context.get("site_url") + "pipeline/cc_get_editable_module_attribute/" + $.context.getBkBizId() + "/";
                    return url
                },
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    const data = [];

                    resp.data.forEach(function (column) {
                        data.push({
                            "tag_code": column.bk_property_id,
                            "type": "input",
                            "attrs": {
                                "name": column.bk_property_name,
                                "editable": true
                            }
                        });
                    });
                    data.unshift({
                        "tag_code": "cc_module_select_text",
                        "type": "input",
                        "attrs": {
                            "name": gettext("模块拓扑"),
                            "placeholder": "集群A>模块B",
                            "width": "120px",
                            "editable": true
                        }
                    });
                    data.forEach(function (column) {
                        column.type = 'input'
                    });
                    return data;
                },
                add_btn: true,
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "cc_template_break_line",
            type: "input",
            attrs: {
                name: gettext("自动扩展分隔符"),
                placeholder: gettext("可为空，单行自动扩展模式下每一行的换行符，默认使用 ,"),
                hookable: true
            },
            events: [
                {
                    source: "cc_tag_method",
                    type: "change",
                    action: function (value) {
                        var self = this;
                        if (value === "template") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ],
        },
    ]
})();
