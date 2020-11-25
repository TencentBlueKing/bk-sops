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
    $.atoms.bk_http_request = [
        {
            tag_code: "bk_http_request_method",
            type: "select",
            attrs: {
                name: gettext("请求方式"),
                hookable: true,
                items: [
                    { text: "GET", value: "GET" },
                    { text: "POST", value: "POST" },
                    { text: "PUT", value: "PUT" },
                    { text: "DELETE", value: "DELETE" },
                    { text: "PATCH", value: "PATCH" },
                    { text: "HEAD", value: "HEAD" },
                    { text: "CONNECT", value: "CONNECT" },
                    { text: "OPTIONS", value: "OPTIONS" },
                    { text: "TRACE", value: "TRACE" },
                ],
                default: "GET"
            },
        },
        {
            tag_code: "bk_http_request_url",
            type: "input",
            attrs: {
                name: "URL",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    },
                    {
                        type: "custom",
                        args: function (value) {
                            var result = {
                                result: true,
                                error_message: ""
                            }
                            var strRegex = '^https?:\/\/[-a-z0-9_.:]+\/?[-a-z0-9_:@&?=+,.!/~*%$]*';
                            var re = new RegExp(strRegex, 'i')
                            if (!re.test(value)) {
                                result.result = false
                                result.error_message = gettext("请输入正确的 URL")
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "bk_http_request_header",
            type: "datatable",
            attrs: {
                name: "Header",
                hookable: true,
                add_btn: true,
                empty_text: gettext("请求头，一行填写一个头部的信息"),
                columns: [
                    {
                        tag_code: "name",
                        type: "textarea",
                        attrs: {
                            name: "Header",
                        }
                    },
                    {
                        tag_code: "value",
                        type: "textarea",
                        attrs: {
                            name: "Value",
                        }
                    },
                ]
            }
        },
        {
            tag_code: "bk_http_request_body",
            type: "textarea",
            attrs: {
                name: "Body",
                hookable: true
            }
        },
        {
            tag_code: "bk_http_timeout",
            type: "int",
            attrs: {
                name: gettext("超时时间"),
                hookable: true,
                placeholder: gettext("请求超时时间"),
                min: 0,
                max: 10,
                default: 0
            }
        },
        {
            tag_code: "bk_http_success_exp",
            type: "textarea",
            attrs: {
                name: gettext("成功条件"),
                hookable: true,
                placeholder: gettext("根据返回的 JSON 的数据来控制节点的成功或失败，使用 resp 引用返回的 JSON 对象，例 resp.result==True")
            }
        }
    ]
})();
