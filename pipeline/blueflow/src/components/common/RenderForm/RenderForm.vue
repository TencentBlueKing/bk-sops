/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<script>
/**
 * 原子分发渲染组件
 *
 * {Object} config 原子表单配置项
 * {Object} option 表单 UI 选项 （label、checkbox、groupName）
 * {Object} data 表单值
 */
import '@/utils/i18n.js'
import { random4 } from '@/utils/uuid.js'
import { checkDataType } from '@/utils/checkDataType.js'
import lowerFirst from 'lodash/lowerFirst'
import toLower from 'lodash/toLower'

import BaseCheckbox from '../base/BaseCheckbox.vue'
import BaseInput from '../base/BaseInput.vue'

// import tags for components registry
const innerComponent = require.context(
    '.',
    false,
    /Tag[A-Z]\w+\.(vue|js)$/
)

const userComponent = require.context(
    '../../tag',
    false,
    /Tag[A-Z]\w+\.(vue|js)$/
)

const registry = {}

const register = (fileNmae, context) => {
    const componentConfig = context(fileNmae)
    const comp = componentConfig.default
    const name = 'tag-' + toLower(comp.name.slice(3))
    registry[name] = comp
}

innerComponent.keys().forEach(fileNmae => {
    register(fileNmae, innerComponent)
})

userComponent.keys().forEach(fileName => {
    register(fileName, userComponent)
})


export default {
    name: 'RenderForm',
    components: {
        ...registry,
        BaseCheckbox,
        BaseInput
    },
    props: {
        config: {
            type: Array,
            default () {
                return []
            }
        },
        option: {
            type: Object,
            default () {
                return {
                    showHook: false,
                    showGroup: false,
                    showLabel: false,
                    editable: true
                }
            }
        },
        data: {
            type: Object
        }
    },
    methods: {
        validate () {
            let isValid = true
            for (let ref in this.$refs) {
                let singleItemValid = true
                const component = this.$refs[ref]
                if (checkDataType(component) === 'Undefined') {
                    delete this.$refs[ref]
                } else if (checkDataType(component) === 'Array') {
                    component.forEach(item => {
                        singleItemValid = !item.validate || item.validate()
                    })
                } else {
                    singleItemValid = !component.validate || component.validate()
                }
                if (isValid) {
                    isValid = singleItemValid
                }
            }
            return isValid
        },
        get_child (tagCode) {
            let childComponent
            this.$children.some(item => {
                if (item.tag_code === tagCode) {
                    childComponent = item
                    return true
                }
            })
            return childComponent
        }
    },
    render (h) {
        const self = this
        function getFormItem (config, option, data, h) {
            return  config.map((item, formIndex) => {
                const formId = item.tag_code + '_' + formIndex
                const isRenderTagHook = item.attrs.hookable && option.showHook
                let isHooked
                if (item.variableKey) {
                    isHooked = data.hook && (data.hook[item.variableKey] || data.hook[item.tag_code])
                } else {
                    isHooked = data.hook && (data.hook[item.tag_code] || data.hook['${' + item.tag_code + '}'])
                }
                // combine
                if (item.type === 'combine' && item.attrs.children.length) {
                    const childrenItems = []
                    const childrenOption = Object.assign({}, option)
                    if (option.showGroup) {  // 分组名称
                        const groupName =  data.extend && data.extend[item.variableKey].name
                        const groupLabel = h('div', {class: 'group-name'},
                            [
                                h('h3', {class: 'name'}, groupName)
                            ]
                        )
                        childrenOption.showGroup = false
                        childrenItems.push(groupLabel)
                    }
                    if (isRenderTagHook) { // hook
                        childrenItems.push(h('bk-tooltip', {
                            class: 'tag-hook',
                            props: {
                                content: isHooked ? gettext('取消勾选') : gettext('勾选参数作为全局变量'),
                                placement: 'left'
                            }
                        }, [h('BaseCheckbox', {
                            props: {
                                isChecked: isHooked
                            },
                            on: {
                                'checkCallback' (checked) {
                                    self.$emit('hookChange', checked, item.tag_code, item.variableKey)
                                }
                            }
                        })]
                        ))
                    }
                    // 标识 form-item 属于哪个变量
                    item.attrs.children.forEach(cItem => {
                        cItem.variableKey = item.variableKey
                    })
                    const combineKey = item.variableKey || item.tag_code
                    const groupData = {
                        hook: data.hook[combineKey],
                        value: data.value[combineKey]
                    }

                    if (isHooked) {
                        // combine 类型变量勾选
                        childrenItems.push(
                            h('div', {
                                class: "form-item clearfix"
                            }, [
                                h('label', {
                                    class: {
                                        'tag-label': true,
                                        'required': false
                                    }
                                }, item.attrs.name),
                                h('div',
                                    {
                                        class: {
                                            'tag-form': true
                                        }
                                    },
                                    [h(`BaseInput`, {
                                        class: {
                                            'baseInput': true,
                                            'disabled': true
                                        },
                                        attrs: {
                                            disabled: true,
                                            value: groupData.value
                                        }
                                    })]
                                )
                            ])
                        )
                    } else {
                        childrenItems.push(getFormItem(item.attrs.children, childrenOption, groupData, h))
                    }
                    return h(`tag-group`, {
                        'class': ['form-group']
                    }, childrenItems)
                }

                const formComponents = []
                const propAttrs = {}

                // 遍历原子配置文件属性，作为 props 项传递到 tag
                Object.keys(item.attrs).forEach(attr => {
                    let attrKey = `initial${attr.charAt(0).toUpperCase() + attr.slice(1)}`
                    propAttrs[attrKey] = item.attrs[attr]
                    // editabel 属性优先取 UI 配置项里的值
                    if (attr === 'editable') {
                        propAttrs[attrKey] = ('editable' in option) ? option.editable : item.attrs[attr]
                    }
                })

                const hasAttrsInConfig = !!item.attrs
                let propValue = ''
                let valueFromUp
                if (checkDataType(data.value) === 'Object') {
                    if (item.variableKey in data.value) {
                        valueFromUp = data.value[item.variableKey]
                    } else if (item.tag_code in data.value) {
                        valueFromUp = data.value[item.tag_code]
                    } else {
                        data.value['${' + item.tag_code + '}']
                    }
                } else {
                    valueFromUp = data.value
                }

                if (valueFromUp && valueFromUp != undefined) {
                    if (typeof valueFromUp === 'string') {
                        propValue = valueFromUp
                    } else if (Array.isArray(valueFromUp)){
                        propValue = [...valueFromUp]
                    } else {
                        propValue = valueFromUp || data.value['${' + item.tag_code + '}']
                    }
                } else if (hasAttrsInConfig && item.attrs.default) {
                    propValue = item.attrs.default
                }
                // name
                if (option.showGroup) {
                    const name = data.extend && data.extend[item.variableKey] && data.extend[item.variableKey].name
                    formComponents.push(h('div', {class: {'group-name': true}},
                        [
                            h('h3', {class: {'name': true}}, name || item.attrs.name)
                        ]
                    ))
                }
                // desc
                if (option.showDesc && data.extend && data.extend[item.variableKey] && data.extend[item.variableKey].desc) {
                    formComponents.push(
                        h('bk-tooltip', {
                            class: {'desc': true},
                            props: {
                                content: data.extend[item.variableKey].desc,
                                placement: 'left'
                            }
                        }, [
                            h('i', {
                                class: {
                                    'common-icon-warning': true
                                }
                            })
                        ])
                    )
                }
                // label
                if (option.showLabel) {
                    let labelName = ''
                    let isRequired = false
                    if (item.attrs) {
                        labelName = item.attrs.name
                        if (item.attrs.validation) {
                            isRequired = item.attrs.validation.some(item => {
                                return item.type === 'required'
                            })
                        }
                    }
                    formComponents.push(
                        h('label', {
                            class: {
                                'tag-label': true,
                                'required': isRequired
                            }
                        }, labelName)
                    )
                }
                if (isHooked) {
                    // checked input
                    formComponents.push(
                        h('div',
                            {
                                class: {
                                    'tag-form': true
                                }
                            },
                            [h(`BaseInput`, {
                                class: {
                                    'baseInput': true,
                                    'disabled': true
                                },
                                attrs: {
                                    disabled: true,
                                    value: propValue
                                },
                                ref: formId
                            })]
                        )
                    )
                } else {
                // full form
                    const editable = ('editable' in option) ? option.editable : true
                    const props = {
                        initialTag_id: formId,
                        initialTag_code: item.tag_code,
                        initialType: item.type,
                        initialMethods: item.methods || {},
                        initialEvents: item.events || [],
                        initialEditable: editable,
                        ...propAttrs
                    }
                    propValue && (props.initialValue = propValue)
                    formComponents.push(
                        h(`tag-${item.type}`, {
                            on: {
                                change: function (val, tagCode) {
                                    self.$emit('dataChange', val, tagCode, item.variableKey)
                                }
                            },
                            props: props,
                            key: item.tag_code,
                            ref: formId
                        })
                    )
                }
                // hook
                if (isRenderTagHook) {
                    formComponents.push(
                        h('bk-tooltip', {
                            class: 'tag-hook',
                            props: {
                                content: isHooked ? gettext('取消勾选') : gettext('勾选参数作为全局变量'),
                                placement: 'left'
                            }
                        }, [
                            h('BaseCheckbox', {
                                props: {
                                    isChecked: isHooked
                                },
                                on: {
                                    'checkCallback' (checked) {
                                        self.$emit('hookChange', checked, item.tag_code, item.variableKey)
                                    }
                                }
                            })
                        ])
                    )
                }
                return h('div', {
                    class: "form-item clearfix"
                }, formComponents)
            })
        }
        const formItems = getFormItem(this.config, this.option, this.data, h)
        return h('div', {class: "render-form"}, formItems)
    }
}
</script>
<style lang="scss" scoped>
    .group-name {
        display: block
    }
    .form-group {
        position: relative;
    }
    .form-item {
        position: relative;
        margin: 15px 0;
        &:first-child {
            margin-top: 0;
        }
        /deep/ .view-value {
            display: inline-block;
            height: 36px;
            line-height: 36px;
            font-size: 14px;
            word-wrap: break-word;
            word-break: break-all;
        }
    }
    .tag-label {
        float: left;
        position: relative;
        margin-top: 8px;
        width: 100px;
        font-size: 14px;
        font-weight: bold;
        color: #666666;
        text-align: right;
        word-wrap: break-word;
        word-break: break-all;
        &.required {
            &:before {
                content: '*';
                position: absolute;
                top: 0px;
                right: -10px;
                color: #F00;
                font-family: "SimSun";
            }
        }
    }
    .tag-form {
        margin-left: 120px;
    }
    .tag-hook {
        position: absolute;
        top: 11px;
        right: 0;
        z-index: 1;
    }
</style>
