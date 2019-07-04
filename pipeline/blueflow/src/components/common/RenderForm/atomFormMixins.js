/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import { checkDataType } from '@/utils/checkDataType.js'

const initialDefaultValue = {
    editable: true,
    hidden: true,
    hookable: true
}

export function getInitialProps (props = {}) {
    const initialProps = {}
    for (let propKey in props) {
        initialProps['initial' + propKey.charAt(0).toUpperCase() + propKey.slice(1)] = props[propKey] || initialDefaultValue[propKey]
    }
    return initialProps
}

export function getAtomFormMixins (atomAttrs = {}) {
    const commonProps = ['tag_id', 'tag_code', 'type', 'value', 'methods', 'events', 'editable', 'validation', 'hidden']
    const allProps = commonProps.concat(Object.keys(atomAttrs))
    const propsToPass = allProps.map(item => {
        return 'initial' + item.charAt(0).toUpperCase() + item.slice(1)
    })
    return {
        props: propsToPass,
        data () {
            const localStates = {}
            allProps.forEach((item, index) => {
                localStates[item] = this[propsToPass[index]]
            })
            return {
                showForm: this.initialHidden === undefined ? true : !this.initialHidden, // 是否展示表单，不包含label、checkbox
                action_init: {},
                validateInfo: {
                    valid: true,
                    message: ''
                },
                ...localStates
            }
        },
        watch: {
            value (val) {
                this.$emit('change', val, this.tag_code)
                this.validate()
            }
        },
        created () {
            this.initialEvents && this.initialEvents.map(item => {
                const source_type = `${item.source}_${item.type}`
                this.action_init[source_type] = item.action
                this.$parent.$on(source_type, (data) => {
                    this.action_init[source_type].call(this, data)
                })
            })
            if (this.initialMethods) {
                for (let methodKey in this.initialMethods) {
                    this.methods[methodKey] = this.initialMethods[methodKey]
                }
            }
        },
        mounted () {
            if (this.initialHidden) {
                this.$el.parentNode && (this.$el.parentNode.style.display = 'none')
            }
            this.$nextTick(()=>{
                this.$parent.$emit(`${this.tag_code}_init`, this.value)
            })
        },
        methods: {
            validate () {
                if (!this.validation) return true
                const isValid = this.validation.every(item => {
                    const result = this.getValidateResult(item, this.value)
                    this.validateInfo = result
                    return result.valid
                })
                return isValid
            },
            getValidateResult (config, value) {
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
                            const validateInfo = config.args.call(this, value)
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
            onChange () {
                this.emit_event(this.tag_code, 'change', this.value)
            },
            _get_value () {
                return this.value
            },
            _set_value (value) {
                this.value = value
            },
            emit_event (name, type, data) {
                this.$parent.$emit(`${name}_${type}`, data)
            },
            show () {
                this.showForm = true
                this.$el.parentNode && (this.$el.parentNode.style.display = 'block')
            },
            hide () {
                this.showForm = false
                this.$el.parentNode && (this.$el.parentNode.style.display = 'none')
            }
        }
    }
}
