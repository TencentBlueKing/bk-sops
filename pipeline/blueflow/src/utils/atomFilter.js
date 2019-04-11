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
import tools from './tools.js'

const atomFilter = {
    formFilter (tag_code, config) {
        let formConfig
        if (tag_code && config){
            config.some(item => {
                if (item.tag_code === tag_code) {
                    formConfig = item
                    return true
                }
                /**
                 * combine类型的tag勾选为为统一勾选，子tag没有勾选选项，暂时注释
                 */
                // if (item.type === 'combine') {
                //     debugger
                //     formConfig = this.formFilter(tag_code, item.attrs.children)
                //     return true
                // }
            })
        }
        return formConfig
    },
    getFormItemDefaultValue (config) {
        let value = {}
        config.forEach(item => {
            if (item.type === 'combine') {
                value[item.tag_code] = this.getFormItemDefaultValue(item.attrs.children)
            } else {
                let val

                if ('value' in item.attrs) {
                    val = tools.deepClone(item.attrs.value)
                } else if ('default' in item.attrs) {
                    val = tools.deepClone(item.attrs.default)
                } else {
                    switch (item.type) {
                        case 'input':
                        case 'textarea':
                        case 'radio':
                        case 'text':
                        case 'datetime':
                        case 'password':
                            val = ''
                            break
                        case 'checkbox':
                        case 'datatable':
                        case 'tree':
                        case 'upload':
                            val = []
                            break
                        case 'select':
                            val = item.attrs.multiple ? [] : ''
                            break
                        case 'int':
                            val = 0
                            break
                        case 'ip_selector':
                            val = {
                                selectors: [],
                                ip: [],
                                topo: [],
                                filters: [],
                                excludes: []
                            }
                            break
                        default:
                            val = ''

                    }
                }

                value[item.tag_code] = val
            }
        })

        return value
    }
}

export default atomFilter