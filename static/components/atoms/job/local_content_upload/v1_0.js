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
    $.atoms.job_local_content_upload = [
        {
            tag_code: "local_name",
            type: "input",
            attrs: {
                name: gettext("生成文件名[后缀]"),
                placeholder: gettext("输入生成文件名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "local_content",
            type: "textarea",
            attrs: {
                name: gettext("文本内容"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_ip_list",
            type: "textarea",
            attrs: {
                name: gettext("目标IP"),
                placeholder: gettext("输入IP, 多个用英文逗号 `,` 或换行分隔"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "file_account",
            type: "input",
            attrs: {
                name: gettext("目标账户"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "file_path",
            type: "input",
            attrs: {
                name: gettext("目标路径"),
                placeholder: gettext("输入目标路径"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_across_biz",
            type: "radio",
            attrs: {
                name: gettext("是否允许跨业务"),
                hookable: true,
                items: [
                    { value: true, name: gettext("是") },
                    { value: false, name: gettext("否") },
                ],
                default: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
    ]
})();
