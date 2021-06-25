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
    $.atoms.format_support_datetime = [
        {
            tag_code: "format_support_datetime",
            type: "combine",
            attrs: {
                name: gettext("日期时间"),
                hookable: true,
                children: [
                    {
                        tag_code: "datetime",
                        type: "datetime",
                        attrs: {
                            name: gettext("时间"),
                            placeholder: gettext("请选择时间"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                    },
                    {
                        tag_code: "datetime_format",
                        type: "input",
                        attrs: {
                            name: gettext("时间格式"),
                            hookable: true,
                            placeholder: gettext("自定义时间格式，默认为`%Y-%m-%d %H:%M:%S`"),
                            default: "%Y-%m-%d %H:%M:%S",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                ],
            }
        },
    ]
})();
