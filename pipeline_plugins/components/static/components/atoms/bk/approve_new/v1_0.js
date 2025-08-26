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
    $.atoms.bk_approve = [
        {
            tag_code: "bk_verifier",
            type: "member_selector",
            attrs: {
                name: gettext("审核人"),
                hookable: true,
                placeholder: gettext("多个审核人，请用英文`,`分隔"),
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "bk_approve_title",
            type: "input",
            attrs: {
                name: gettext("审核标题"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "bk_approve_content",
            type: "textarea",
            attrs: {
                name: gettext("审核内容"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
