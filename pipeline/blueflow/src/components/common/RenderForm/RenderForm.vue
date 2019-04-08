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
<template>
    <div class="render-form">
        <component
            :is="atom.type === 'combine' ? 'FormGroup' : 'FormItem'"
            v-for="(atom, index) in scheme"
            :key="`${atom.tag_code}_${index}`"
            :scheme="atom"
            :option="option"
            :value="getFormValue(atom)"
            :hook="hooked[atom.tag_code]"
            @change="updateForm"
            @onHook="updateHook">
        </component>
    </div>
</template>
<script>
/**
 * 标准插件表单渲染函数
 * param {Array} scheme 标准插件表单配置项
 * param {Object} formOption 表单 UI 选项(label、checkbox、groupName)
 * param {Object} formData 表单值
 * param {Object} hooked 表单是否勾选
 */
import '@/utils/i18n.js'
import tools from '@/utils/tools.js'
import FormGroup from './FormGroup.vue'
import FormItem from './FormItem.vue'

const DEFAUTL_OPTION = {
    showHook: false, // 是否可以勾选
    showGroup: false, // 是否显示 combine 类型标准插件名称
    showLabel: false, // 是否显示标准插件名称
    formEdit: true, // 是否可编辑
    formMode: true // 是否为表单模式（查看参数时，input、textarea等不需要用表单展示）
}

export default {
    name: 'RenderForm',
    components: {
        FormGroup,
        FormItem
    },
    model: {
        prop: 'formData',
        event: 'change'
    },
    data () {
        return {
            value: tools.deepClone(this.formData)
        }
    },
    props: {
        scheme: {
            type: Array,
            default () {
                return []
            }
        },
        formOption: {
            type: Object,
            default () {
                return {
                    ...DEFAUTL_OPTION
                }
            }
        },
        formData: {
            type: Object,
            default () {
                return {}
            }
        },
        hooked: {
            type: Object,
            default () {
                return {}
            }
        }
    },
    computed: {
        option () {
            return Object.assign({}, DEFAUTL_OPTION, this.formOption)
        }
    },
    watch: {
        scheme: {
            handler: function (val) {
                this.setDefaultValue(val, this.formData)
            },
            deep: true
        },
        formData: {
            handler: function (val) {
                this.value = tools.deepClone(val)
            },
            deep: true
        }
    },
    created () {
        this.setDefaultValue(this.scheme, this.formData)
    },
    methods: {
        /**
         * 设置表单默认值
         * 若传入的 formData 不包含表单项的值，取值顺序为：标准插件配置项 value 字段 -> 标准插件配置项 default 字段 -> tag 类型默认值
         * @param {Array} scheme 表单配置项
         * @param {Object} data 表单值
         */
        setDefaultValue (scheme, data) {
            if (!scheme || !Array.isArray(scheme)) return

            scheme.forEach(item => {
                const key = item.tag_code

                if (item.type === 'combine') {
                    if (!this.hooked || !this.hooked[item.tag_code]) {
                        if (!(key in data)) {
                            this.$set(data, key, {})
                            this.$set(this.value, key, {})
                        }
                        this.setDefaultValue (item.attrs.children, data[key])
                    }
                } else {
                    if (!(key in data)) {
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
                        this.$set(data, key, val)
                    }
                }
            })
        },
        getFormValue (atom) {
            return this.value[atom.tag_code]
        },
        updateForm (fieldArr, val) {
            const field = fieldArr.slice(-1)[0]
            let fieldDataObj = this.value
            fieldArr.slice(0, -1).forEach(item => {
                if (item in fieldDataObj) {
                    fieldDataObj = fieldDataObj[item]
                } else {
                    this.$set(fieldDataObj, item, {})
                }
            })

            this.$set(fieldDataObj, field, val)
            this.$emit('change', this.value)
        },
        updateHook (field, val) {
            this.$emit('onHookChange', field, val)
        },
        /**
         * 获取 combine 类型组件的子组件实例
         * @param {String} tagCode 标准插件 tag_code，值空时，返回全部子组件
         */
        get_child (tagCode) {
            let childComponent
            if (typeof tagCode === 'string' && tagCode !== '') {
                this.$children.some(item => {
                    if (item.scheme && item.scheme.tag_code === tagCode) {
                        childComponent = item.$children[0]
                        return true
                    }
                })
            } else {
                childComponent = this.$children
            }

            return childComponent
        },
        /**
         * 表单校验函数
         * @TODO: 改写为 promise 异步机制
         */
        validate () {
            let isValid = true
            this.$children.forEach(childComp => {
                const singleItemValid = childComp.validate()

                if (isValid) {
                    isValid = singleItemValid
                }
            })
            return isValid
        }
    }
}
</script>


