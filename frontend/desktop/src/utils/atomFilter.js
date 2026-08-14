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
import tools from './tools.js'

const atomFilter = {
    formFilter (tag_code, config) {
        let formConfig
        if (tag_code && config) {
            config.some((item) => {
                if (item.tag_code === tag_code) {
                    formConfig = item
                    return true
                }
                return false
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
        const value = {}
        config.forEach((item) => {
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
                        case 'member_selector':
                        case 'log_display':
                        case 'code_editor':
                        case 'section':
                            val = ''
                            break
                        case 'checkbox':
                        case 'datatable':
                        case 'tree':
                        case 'upload':
                        case 'cascader':
                            val = []
                            break
                        case 'select':
                            val = item.attrs.multiple ? [] : ''
                            break
                        case 'time':
                            val = item.attrs.isRange ? ['00:00:00', '23:59:59'] : ''
                            break
                        case 'int':
                            val = 0
                            break
                        case 'ip_selector':
                            val = {
                                selectors: [],
                                ip: [],
                                topo: [],
                                group: [],
                                filters: [],
                                excludes: [],
                                with_cloud_id: false
                            }
                            break
                        case 'set_allocation':
                            val = {
                                config: {
                                    set_count: 0,
                                    set_template_id: '',
                                    host_resources: [],
                                    module_detail: []
                                },
                                data: [],
                                separator: ','
                            }
                            break
                        case 'host_allocation':
                            val = {
                                config: {
                                    host_count: 0,
                                    host_screen_value: '',
                                    host_resources: [],
                                    host_filter_detail: []
                                },
                                data: [],
                                separator: ','
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
    },
    /**
     * 通过变量配置项获取需要加载标准插件的相关参数
     * @param {Object} variable 变量配置项
     *
     * @return {String} name 标准插件文件名称
     * @return {String} atom 标准插件注册在 $.atoms 上的名称
     * @return {String} tagCode 标准插件中的某一项表单tagCode
     * @return {String} classify 标准插件分类：变量、组件
     */
    getVariableArgs (variable) {
        const { source_tag, custom_type } = variable
        let name = ''
        let atom = ''
        let tagCode = ''
        let classify = ''
        if (custom_type) {
            name = custom_type
            atom = source_tag ? source_tag.split('.')[0] : custom_type // 兼容旧数据自定义变量source_tag为空
            tagCode = source_tag ? source_tag.split('.')[1] : custom_type
            classify = 'variable'
        } else {
            [name, tagCode] = source_tag.split('.')
            atom = name
            classify = 'component'
        }
        return { name, atom, tagCode, classify }
    },
    /**
     * 获取变量的实际表单类型
     * 自定义变量（custom_type）直接返回；勾选生成的 component_inputs 变量 custom_type 为空，
     * 需从 form_schema.type 取原始表单类型（如 input/textarea），用于正则校验等场景
     * @param {Object} variable 变量对象，含 custom_type / source_type / form_schema 字段
     * @returns {String} 表单类型
     */
    getEffectiveFormType (variable) {
        const { custom_type, source_type, form_schema } = variable || {}
        if (source_type === 'component_inputs' && form_schema?.type) {
            return form_schema.type
        }
        return custom_type
    },
    /**
     * 判断 atom 配置文件是否存在
     * @param {String} atomType 插件类型
     * @param {String} version 插件版本
     * @param {Object} atomFormConfig 所有配置
     */
    isConfigExists (atomType, version, atomFormConfig) {
        return atomFormConfig[atomType] && atomFormConfig[atomType][version]
    },
    /**
     * 参数填写/执行页面中，为保证每个表单 tag_code 唯一，原表单 tag_code 会被替换为全局变量 key，
     * 标准插件配置项里的 events.source 需要同步替换，否则跨表单项联动
     * （如：下拉框选项随单选按钮变化）的事件无法命中，选项停留在初始值
     *
     * 处理两类事件：
     * 1. 自引用：source 为当前表单项自身 tag_code，替换为 ${tag_code}（保持原逻辑）
     * 2. 跨表单项：source 为同插件其他表单项 tag_code，找到对应全局变量后替换为变量 key
     *
     * @param {Object} formConfig 单个表单项配置项
     * @param {String} tagCode 表单项原始 tag_code（变量 source_tag 的后段）
     * @param {Array} variables 全局变量列表（与当前表单项处于同一渲染上下文中）
     * @param {Object} currentVariable 当前表单项对应的全局变量
     */
    remapEventsSource (formConfig, tagCode, variables, currentVariable) {
        if (!formConfig || !formConfig.hasOwnProperty('events')) return
        formConfig.events.forEach(e => {
            if (!e || !e.source) return
            // 自引用：source 为当前表单项自身 tag_code
            if (e.source === tagCode) {
                e.source = '${' + e.source + '}'
                return
            }
            // 跨表单项联动：source 指向同插件其他表单项，查找对应全局变量并替换为变量 key
            const sourceVariable = variables.find(item => {
                if (!item || item === currentVariable || !item.source_tag) return false
                let sourceTagCode = ''
                try {
                    // 解析候选变量的原始tag_code与e.source比对
                    sourceTagCode = atomFilter.getVariableArgs(item).tagCode
                } catch (err) {
                    return false
                }
                // 表单的 tag_code 已被替换成全局变量key，而 events.source 里存的还是原始 tag_code
                if (sourceTagCode !== e.source) return false
                // 优先限定为同一节点来源，避免同插件多节点重复勾选时错配
                const nodesA = Object.keys((currentVariable && currentVariable.source_info) || {})
                const nodesB = Object.keys(item.source_info || {})
                if (nodesA.length && nodesB.length) {
                    return nodesA.some(nodeId => nodesB.includes(nodeId))
                }
                return true
            })
            if (sourceVariable) {
                e.source = sourceVariable.key
            }
        })
    }
}

export default atomFilter
