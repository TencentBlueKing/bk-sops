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
export const checkDataType = (data) => {
    const typeString = Object.prototype.toString.call(data)
    return typeString.slice(8, -1)
}

export const getDefaultValueFormat = (scheme) => {
    let valueFormat
    switch (scheme.type) {
        case 'input':
        case 'textarea':
        case 'radio':
        case 'text':
        case 'datetime':
        case 'memberSelector':
        case 'logDisplay':
        case 'code_editor':
        case 'section':
            valueFormat = {
                type: ['String', 'Number', 'Boolean'],
                value: ''
            }
            break
        case 'checkbox':
        case 'datatable':
        case 'tree':
        case 'upload':
        case 'cascader':
            valueFormat = {
                type: 'Array',
                value: []
            }
            break
        case 'select': // 文本值下拉框数据类型可能为对象
            if (scheme.attrs.multiple) {
                valueFormat = {
                    type: ['Array', 'Object'],
                    value: []
                }
            } else {
                valueFormat = {
                    type: ['String', 'Number', 'Boolean', 'Object'],
                    value: ''
                }
            }
            break
        case 'time':
            if (scheme.attrs.isRange) {
                valueFormat = {
                    type: 'Array',
                    value: ['00:00:00', '23:59:59']
                }
            } else {
                valueFormat = {
                    type: 'String',
                    value: ''
                }
            }
            break
        case 'int':
            valueFormat = {
                type: 'Number',
                value: 0
            }
            break
        case 'ip_selector':
            valueFormat = {
                type: 'Object',
                value: {
                    static_ip_table_config: [],
                    selectors: [],
                    ip: [],
                    topo: [],
                    group: [],
                    filters: [],
                    excludes: []
                }
            }
            break
        case 'set_allocation':
            valueFormat = {
                type: 'Object',
                value: {
                    config: {
                        set_count: 1,
                        set_template_id: '',
                        host_resources: [],
                        module_detail: []
                    },
                    data: [],
                    separator: ','
                }
            }
            break
        case 'host_allocation':
            valueFormat = {
                type: 'Object',
                value: {
                    config: {
                        host_count: 0,
                        host_screen_value: '',
                        host_resources: [],
                        host_filter_detail: []
                    },
                    data: [],
                    separator: ','
                }
            }
            break
        case 'password':
            valueFormat = {
                type: ['String', 'Object'],
                value: {
                    type: 'password_value',
                    tag: 'value',
                    value: ''
                }
            }
            break
        default:
            valueFormat = {
                type: 'String',
                value: ''
            }
    }
    return valueFormat
}
