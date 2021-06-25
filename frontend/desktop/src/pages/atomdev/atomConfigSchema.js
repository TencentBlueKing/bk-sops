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
import Ajv from 'ajv'
import importTag from './importTag'

const { components } = importTag()
const tagNames = Object.keys(components).map(item => item.slice(3).replace(/[A-Z]/g, match => `_${match.toLowerCase()}`)
    .slice(1)
)

const NAME_REG = '^[a-zA-Z_][a-zA-Z0-9_]*'

export const atomFormItemSchema = {
    $id: '/AtomFormItem',
    title: '标准插件单个表单项配置',
    type: 'object',
    properties: {
        tag_code: {
            type: 'string',
            pattern: NAME_REG
        },
        type: {
            type: 'string',
            enum: ['combine', ...tagNames]
        },
        attrs: {
            type: 'object',
            properties: {
                name: {
                    type: 'string'
                }
            },
            required: ['name']
        },
        events: {
            type: 'array'
        },
        methods: {
            type: 'object'
        }
    },
    required: ['tag_code', 'type', 'attrs']
}

const ajv = new Ajv()

export default ajv.compile(atomFormItemSchema)
