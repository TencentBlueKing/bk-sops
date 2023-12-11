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
    $.atoms.cc_batch_update_host = [
        {
            tag_code: "cc_host_update_method",
            type: "radio",
            attrs: {
                name: gettext("填参方式"),
                hookable: false,
                items: [
                    {value: "manual", name: gettext("手动填写")},
                    {value: "auto", name: gettext("单行自动扩展")}
                ],
                default: "auto",
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "cc_host_update_method",
                    type: "init",
                    action: function () {
                        this.emit_event(this.tagCode, "change", this.value)
                    }
                }
            ]
        },
        {
            tag_code: "cc_host_property_custom",
            type: "datatable",
            attrs: {
                pagination: true,
                name: gettext("主机属性修改"),
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    const resp_data = resp.data;
                    const data = [
                        {
                            tag_code: "bk_host_innerip",
                            type: 'textarea',
                            attrs: {
                                name: gettext("内网IP"),
                                editable: true,
                                validation: [
                                    {
                                        type: "required"
                                    }
                                ]
                            }
                        }
                    ];
                    resp_data.forEach(function (column) {
                        column.type = 'textarea';
                        data.push({
                            tag_code: column.bk_property_id,
                            type: 'textarea',
                            attrs: {
                                name: column.bk_property_name,
                                editable: true
                            }
                        });
                    });
                    return data;
                },
                add_btn: true,
                hookable: true,
                table_buttons: [
                    {
                        type: "export",
                        text: gettext("导出"),
                        callback: function() {
                            this.export2Excel()
                        }
                    },
                    {
                        type: "import",
                        text: gettext("导入")
                    }
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            events: [
                {
                    source: "cc_host_property_custom",
                    type: "init",
                    action: function (value) {
                        this.remote_url = $.context.inCommonTemplate() ? '' : $.context.get('site_url') + 'pipeline/cc_input_host_property/' + $.context.getBkBizId() + '/';
                        this.remoteMethod();
                    }
                }
            ],
        },
        {
            tag_code: "cc_auto_separator",
            type: "textarea",
            attrs: {
                name: gettext("自动扩展分隔符"),
                hookable: true,
                placeholder: gettext("单行自动扩展模式下每一行的换行符，默认使用 ,"),
                default: ","
            },
            events: [
                {
                    source: "cc_host_update_method",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === "auto") {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
            ]
        },
    ]
})();
