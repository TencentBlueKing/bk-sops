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
import tools from '@/utils/tools.js'
import { checkDataType } from '@/utils/checkDataType.js'

const COMMON_ATTRS = {
    tagCode: {
        type: String,
        required: true
    },
    name: {
        type: String
    },
    hookable: {
        type: Boolean
    },
    validation: {
        type: Array,
        default () {
            return []
        }
    },
    default: {
        type: [String, Number, Boolean, Array, Object],
        required: false
    },
    hidden: {
        type: Boolean,
        default: false
    },
    formEdit: {
        type: Boolean,
        default: true
    },
    formMode: {
        type: Boolean
    },
    parentValue: {
        type: [String, Number, Boolean, Array, Object]
    }
}

export function getFormMixins (attrs = {}) {
    attrs = tools.deepClone(attrs)
    const inheritAttrs = {} // 继承属性
    const noInheritAttrs = {} // 非继承属性

    Object.keys(attrs).forEach(item => {
        if (item !== 'value') {
            const attrsDefault = attrs[item].default
            let attrsValue

            if (typeof attrsDefault === 'function') {
                attrsValue = attrs[item].type === Function ? attrsDefault : attrsDefault()
            } else {
                attrsValue = attrsDefault
            }
            noInheritAttrs[item] = attrsValue
        } else {
            inheritAttrs[item] = tools.deepClone(attrs[item])
        }
    })

    return {
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            ...COMMON_ATTRS, // 公共属性
            ...inheritAttrs, // tag 继承属性(value)
            atomEvents: {
                type: Array,
                default () {
                    return []
                }
            },
            atomMethods: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            const noInheritData = {}
            // 非 prop 属性注册到 data 对象
            // 优先取标准插件配置项里的值
            Object.keys(noInheritAttrs).forEach(item => {
                noInheritData[item] = this.$attrs.hasOwnProperty(item) ? this.$attrs[item] : noInheritAttrs[item]
            })

            return {
                eventActions: {}, // 标准插件配置项定义的事件回调函数
                validateInfo: {
                    valid: true,
                    message: ''
                },
                ...noInheritData,
                editable: this.formEdit
            }
        },
        created () {
            // 注册标准插件配置项里的事件函数到父父组件实例
            // 父父组件目前包括 RenderForm(根组件)、FormGroup(combine 类型)、TagDataTable(表格类型)
            this.atomEvents.map(item => {
                const eventSource = `${item.source}_${item.type}`
                this.eventActions[eventSource] = item.action
                this.$parent.$parent.$on(eventSource, (data) => {
                    this.eventActions[eventSource].call(this, data)
                })
            })

            // 注册标准插件配置项 methods 属性里的方法到 Tag 实例组件
            // 标准插件配置项里的方法会重载 mixins 里定义的方法
            Object.keys(this.atomMethods).map(item => {
                if (typeof this.atomMethods[item] === 'function') {
                    this[item] = this.atomMethods[item]
                }
            })
        },
        mounted () {
            // 部分 Tag 组件需要执行初始化操作
            this._tag_init && this._tag_init()

            // 组件插入到 DOM 后， 在父父组件上发布该 Tag 组件的 init 事件，触发标准插件配置项里监听的函数
            this.$nextTick(()=>{
                this.$parent.$parent.$emit(`${this.tagCode}_init`, this.value)
            })
        },
        methods: {
            updateForm (val) {
                const fieldsArr = [this.tagCode]
                this.$emit('change', fieldsArr, val)
                this.$nextTick(()=> {
                    this.onChange()
                    this.validate()
                })
            },
            /**
             * formItem 组件校验方法，默认调用通用校验规则
             * 若在 tag 内有自定义校验方法 customValidate，则调用该方法执行校验
             *
             * @returns {Boolean} isValid 校验结果是否合法
             */
            validate () {
                if (this.customValidate) {
                    return this.customValidate()
                }
                if (!this.validation) return true
                
                const isValid = this.validation.every(item => {
                    const result = this.getValidateResult(item, this.value, this.parentValue)
                    this.validateInfo = result
                    return result.valid
                })
                return isValid
            },
            /**
             * 通用校验规则
             * @param {Object} config tag 配置项
             * @param {Any} value tag 值
             * @param {Object} parentValue 父组件值
             *
             * @returns {Object} 校验结果和提示信息
             */
            getValidateResult (config, value, parentValue) {
                let valid = true
                let message = ''
                switch (config.type) {
                    case 'required':
                        const valueType = checkDataType(value)
                        let valueEmpty = false
                        if (valueType === 'Object') {
                            valueEmpty = !Object.keys(value).length
                        } else if (valueType === 'String' || valueType === 'Array') {
                            valueEmpty = !value.length
                        } else if (valueType === 'Number') {
                            valueEmpty = !value.toString()
                        }
                        if (valueEmpty) {
                            valid = false
                            message = gettext('必填项')
                        }
                        break
                    case 'regex':
                        const reg = new RegExp(config.args)
                        if (!reg.test(value)) {
                            valid = false
                            message = config.error_message
                        }
                        break
                    case 'custom':
                        if (!/^\${[^${}]+}$/.test(value)) {
                            const validateInfo = config.args.call(this, value, parentValue)
                            if (!validateInfo.result) {
                                valid = false
                                message = validateInfo.error_message
                            }
                        }
                        break
                    default:
                        break
                }
                return { valid, message }
            },
            emit_event (name, type, data) {
                this.$parent.$parent.$emit(`${name}_${type}`, data)
            },
            onChange () {
                this.emit_event(this.tagCode, 'change', this.value)
            },
            show () {
                this.$emit('onShow')
            },
            hide () {
                this.$emit('onHide')
            },
            // 获取 form 项实例
            get_form_instance () {
                return this.$parent
            },
            // 获取 combine 实例或根元素实例
            get_parent () {
                return this.$parent.$parent
            },
            _get_value () {
                return this.value
            },
            _set_value (value) {
                this.updateForm(value)
            }
        }
    }
}
