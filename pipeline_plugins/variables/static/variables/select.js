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
(function () {
    $.atoms.select = [
        {
            tag_code: "select_meta",
            type: "combine",
            attrs: {
                name: gettext("下拉框"),
                hookable: true,
                children: [
                    {
                        tag_code: "datasource",
                        type: "radio",
                        attrs: {
                            name: gettext("数据源"),
                            hookable: true,
                            items: [{name: gettext("自定义"), value: "0"}, {name: gettext("远程数据源"), value: "1"}],
                            value: "0",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "items_text",
                        type: "textarea",
                        attrs: {
                            name: gettext("选项"),
                            hookable: true,
                            placeholder: gettext('请输入数据源信息，自定义数据源格式为 [{"text": "", "value": ""}...]，若是远程数据源则填写返回该格式数据的 URL'),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "type",
                        type: "radio",
                        attrs: {
                            name: gettext("类型"),
                            hookable: true,
                            items: [{name: gettext("单选"), value: "0"}, {name: gettext("多选"), value: "1"}],
                            value: "0",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "default",
                        type: "textarea",
                        attrs: {
                            name: gettext("默认值"),
                            placeholder: gettext("请输入下拉框的默认值，单选为 value 的格式，多选为 value,value,... 的格式"),
                            hookable: true,
                        }
                    }
                ]
            }

        },
        {
            tag_code: "select",
            meta_transform: function (variable) {
                let metaConfig = variable.value;
                let remote = false;
                let remote_url = "";
                let items = [];
                let placeholder = '';
                if (metaConfig.datasource === "1") {
                    remote_url = metaConfig.items_text;
                    remote = true;
                } else {
                    try {
                        items = JSON.parse(metaConfig.items_text);
                    } catch (err) {
                        items = [];
                        placeholder = gettext('非法下拉框数据源，请检查您的配置');
                    }
                    if (!(items instanceof Array)) {
                        items = [];
                        placeholder = gettext('非法下拉框数据源，请检查您的配置');
                    }
                }

                let multiple = false;
                let default_val = metaConfig.default || '';

                if (metaConfig.type === "1") {
                    multiple = true;
                    default_val = [];
                    if (metaConfig.default) {
                        let vals = metaConfig.default.split(',');
                        for (let i in vals) {
                            default_val.push(vals[i].trim());
                        }
                    }
                }
                return {
                    tag_code: this.tag_code,
                    type: "select",
                    attrs: {
                        name: gettext("下拉框"),
                        hookable: false,
                        items: items,
                        multiple: multiple,
                        value: default_val,
                        remote: remote,
                        remote_url: remote_url,
                        placeholder: placeholder,
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
