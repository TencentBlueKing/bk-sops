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
module.exports = {
    root: true,
    parserOptions: {
        parser: "babel-eslint",
        ecmaVersion: 2017,
        sourceType: 'module'
    },
    env: {
        browser: true,
    },
    rules: {
        "no-debugger": process.env.NODE_ENV === "production" ? 2 : 0,
        "arrow-parens": 0,
        "no-empty": "error",
        "no-extra-semi": "error",
        "semi": ["error", "never"],
        "generator-star-spacing": 0,
        "no-unused-vars": 0,
        "indent": ["error", 4, {
            "SwitchCase": 1
        }],
        "space-before-function-paren": ["error", {
            "anonymous": "always", 
            "named": "always",
            "asyncArrow": "always" 
        }],
        "no-trailing-spaces": ["error", {
            "skipBlankLines": true 
        }],
        "comma-dangle": ["error", "never"],
        "key-spacing": ["error", {
            "beforeColon": false 
        }],
        "keyword-spacing": ["error", {
            "before": true, 
            "after": true
        }],
        "space-infix-ops": "error",
        "spaced-comment": ["error", "always"],
    },
    extends: [
        "plugin:vue/essential"
    ]
}