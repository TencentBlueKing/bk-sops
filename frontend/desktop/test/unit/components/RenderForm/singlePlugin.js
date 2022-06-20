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

export default [{
    "variableKey": "bk_timing",
    "tag_code": "bk_timing",
    "type": "input",
    "attrs": {
        "name": "定时时间",
        "placeholder": "秒(s) 或 时间(%Y-%m-%d %H:%M:%S)",
        "hookable": true,
        "validation": [
            {
                type: "custom",
                args (value) {
                    const result = {
                        result: false,
                        error_message: "请填写秒(s)且不超过8位数或时间(%Y-%m-%d %H:%M:%S)"
                    }
                    const number_regex = /^\d{1,8}$/;
                    if (number_regex.test(value)) {
                        result.result = true;
                    }

                    const date_time_regex = /^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|(29-02-((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|((0[469]|11)-(0?[1-9]|[12]\d|30))|(0[2])-(0[1-9]|[1]\d|2[0-8])) ((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$/;
                    if (date_time_regex.test(value)) {
                        result.result = true;
                    }

                    return result;
                }
            }
        ]
    }
}]
