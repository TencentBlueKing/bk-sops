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
    $.atoms.select = [
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
