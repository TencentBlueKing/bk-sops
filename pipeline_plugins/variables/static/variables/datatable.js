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
    $.atoms.datatable = [
        {
            tag_code: "datatable_meta",
            type: "combine",
            attrs: {
                name: gettext("表格"),
                hookable: true,
                children: [
                    {
                        tag_code: "columns_text",
                        type: "textarea",
                        attrs: {
                            name: gettext("列配置"),
                            hookable: true,
                            placeholder: gettext('请输入列配置，格式为 [{"tag_code": "name1", "type": "input", "attrs": {"name": "列1"}}...], 更多配置请参考《Tag 使用和开发说明》文档中 datatable 说明'),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "default_text",
                        type: "textarea",
                        attrs: {
                            name: gettext("默认值"),
                            hookable: true,
                            placeholder: gettext('请输入默认值，可为空，格式为 [{"name1": "value1", "name2": "value2"}...]，每一项字典的 key 请和列配置 tag_code 对应')
                        }
                    }
                ]
            }

        },
        {
            tag_code: "datatable",
            meta_transform: function (variable) {
                let metaConfig = variable.value;
                let columns = [];
                let default_val = [];
                let empty_text = '';

                try {
                    columns = JSON.parse(metaConfig.columns_text);
                } catch (err) {
                    columns = [];
                    empty_text = gettext('表格列配置不是合法的 JSON 格式，请检查变量配置');
                }
                if (!(columns instanceof Array)) {
                    columns = [];
                    empty_text = gettext('表格列配置解析后不是列表格式，请检查变量配置');
                }

                if (metaConfig.default_text !== '') {
                    try {
                        default_val = JSON.parse(metaConfig.default_text);
                    } catch (err) {
                        default_val = [];
                        empty_text = gettext('表格默认值不是合法的 JSON 格式，请检查变量配置');
                    }
                    if (!(default_val instanceof Array)) {
                        default_val = [];
                        empty_text = gettext('表格默认值解析后不是列表格式，请检查变量配置');
                    }
                }

                return {
                    tag_code: this.tag_code,
                    type: "datatable",
                    attrs: {
                        name: gettext("表格"),
                        hookable: false,
                        columns: columns,
                        value: default_val,
                        empty_text: empty_text,
                        editable: true,
                        table_buttons: [
                            {
                                type: "add_row",
                                text: gettext("添加"),
                                callback: function(){
                                    this.add_row()
                                }
                            },
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
                        remote_data_init: function (data) {
                            return data
                        },
                        validation: [
                            {
                                type: "required"
                            }
                        ]
                    }
                }
            }
        }
    ]
})();
