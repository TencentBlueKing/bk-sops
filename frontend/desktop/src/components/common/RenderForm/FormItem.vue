/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        v-show="showForm"
        :class="[
            'rf-form-item',
            'clearfix',
            {
                'rf-has-hook': showHook,
                'show-label': option.showLabel,
                'rf-has-hook': option.showHook,
                'rf-col-layout': scheme.attrs.cols
            }
        ]"
        :style="{
            width: (scheme.attrs.cols ? scheme.attrs.cols / 12 * 100 : 100) + '%'
        }">
        <div v-if="!hook && option.showGroup && scheme.attrs.name" class="rf-group-name">
            <span class="name">{{scheme.attrs.name}}</span>
            <span v-if="scheme.attrs.desc" class="rf-group-desc">
                <i
                    v-bk-tooltips="{
                        content: scheme.attrs.desc,
                        placements: ['right'],
                        zIndex: 2002
                    }"
                    class="common-icon-info">
                </i>
            </span>
        </div>
        <!-- 表单名称 -->
        <label
            v-if="option.showLabel"
            :class="['rf-tag-label', { 'required': isRequired() }]">
            {{scheme.attrs.name}}
        </label>
        <!-- 表单勾选为全局变量 -->
        <div v-show="hook" class="rf-tag-form">
            <el-input :disabled="true" :value="String(value)"></el-input>
        </div>
        <!-- 表单元素 -->
        <component
            v-show="!hook"
            class="rf-tag-form"
            ref="tagComponent"
            :is="tagComponent"
            v-bind="getDefaultAttrs()"
            :tag-code="scheme.tag_code"
            :atom-events="scheme.events"
            :atom-methods="scheme.methods"
            :value="formValue"
            :parent-value="parentValue"
            @change="updateForm"
            @onShow="onShowForm"
            @onHide="onHideForm">
        </component>
        <!-- 变量勾选checkbox -->
        <div class="rf-tag-hook" v-if="showHook">
            <bk-checkbox
                v-bk-tooltips="{
                    content: hook ? i18n.hooked : i18n.cancelHook,
                    placements: ['left'],
                    customClass: 'offset-left-tooltip',
                    zIndex: 2002
                }"
                :value="hook"
                @change="onHookForm">
            </bk-checkbox>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import { checkDataType } from '@/utils/checkDataType.js'
    import FormGroup from './FormGroup.vue'

    // 导入 tag 文件注册为组件
    function registerTag () {
        const innerComponent = require.context(
            './tags/',
            false,
            /Tag[A-Z]\w+\.(vue|js)$/
        )
        const userComponent = require.context(
            '../../tags/',
            false,
            /Tag[A-Z]\w+\.(vue|js)$/
        )
        const tagComponent = {}
        const register = (fileName, context) => {
            const componentConfig = context(fileName)
            const comp = componentConfig.default
            const typeName = comp.name.slice(3).replace(/[A-Z]/g, match => {
                return `_${match.toLowerCase()}`
            })
            const name = 'tag' + typeName

            tagComponent[name] = comp
        }
        innerComponent.keys().forEach(fileName => {
            register(fileName, innerComponent)
        })
        userComponent.keys().forEach(fileName => {
            register(fileName, userComponent)
        })

        return tagComponent
    }

    export default {
        name: 'FormItem',
        components: {
            FormGroup
        },
        props: {
            scheme: {
                type: Object,
                default () {
                    return {}
                }
            },
            option: {
                type: Object,
                default () {
                    return {}
                }
            },
            value: {
                type: [String, Number, Boolean, Array, Object]
            },
            parentValue: {
                type: [String, Number, Boolean, Array, Object]
            },
            hook: {
                type: Boolean,
                default: false
            }
        },
        data () {
            let showForm = true
            // 原子配置为默认隐藏
            if ('hidden' in this.scheme.attrs) {
                showForm = !this.scheme.attrs.hidden
            }
            // 原子配置为非编辑状态下隐藏，优先级高于 hidden
            if ('formViewHidden' in this.scheme.attrs && !this.option.formEdit) {
                showForm = !this.scheme.attrs.formViewHidden
            }

            // 是否展示右侧变量勾选checkbox
            const showHook = ('hookable' in this.scheme.attrs)
                ? (this.scheme.attrs.hookable && this.option.showHook)
                : !!this.option.showHook
            const formValue = this.getFormValue(this.value)

            return {
                tagComponent: `tag_${this.scheme.type}`,
                showForm,
                showHook,
                formValue,
                i18n: {
                    hooked: gettext('取消勾选'),
                    cancelHook: gettext('勾选参数作为全局变量')
                }
            }
        },
        watch: {
            scheme (val) {
                this.tagComponent = `tag_${this.scheme.type}`
            },
            value (val) {
                this.formValue = this.getFormValue(val)
            }
        },
        beforeCreate () {
            const tagComponent = registerTag()
            Object.keys(tagComponent).forEach(item => {
                this.$options.components[item] = tagComponent[item]
            })
        },
        methods: {
            getDefaultAttrs () {
                const attrs = tools.deepClone(this.scheme.attrs)
                attrs.showVarList = this.option.showVarList // 是否自动显示变量列表
                attrs.formEdit = this.option.formEdit
                attrs.formMode = this.option.formMode
                attrs.validateSet = this.option.validateSet

                // UI 配置项里的 formEdit 优先于标准插件配置项里的 editable 属性
                // if ('editable' in this.option) {
                //     attrs.editable = this.option.editable
                // }

                return { ...attrs }
            },
            getFormValue (val) {
                const valueType = checkDataType(val)

                if (valueType === 'Undefined') {
                    return
                }

                let defaultValueFormat
                let formValue

                if (this.hook) {
                    defaultValueFormat = {
                        type: 'String',
                        value: ''
                    }
                } else {
                    defaultValueFormat = this.getDefaultValueFormat()
                }

                const isTypeValid = Array.isArray(defaultValueFormat.type)
                    ? defaultValueFormat.type.indexOf(valueType) > -1
                    : defaultValueFormat.type === valueType

                if (isTypeValid) {
                    formValue = tools.deepClone(val)
                } else {
                    formValue = tools.deepClone(defaultValueFormat.value)
                    this.updateForm([this.scheme.tag_code], formValue)
                }

                return formValue
            },
            getDefaultValueFormat () {
                let valueFormat
                switch (this.scheme.type) {
                    case 'input':
                    case 'textarea':
                    case 'radio':
                    case 'text':
                    case 'datetime':
                    case 'password':
                        valueFormat = {
                            type: ['String', 'Number', 'Boolean'],
                            value: ''
                        }
                        break
                    case 'checkbox':
                    case 'datatable':
                    case 'tree':
                    case 'upload':
                        valueFormat = {
                            type: 'Array',
                            value: []
                        }
                        break
                    case 'select':
                        if (this.scheme.attrs.multiple) {
                            valueFormat = {
                                type: 'Array',
                                value: []
                            }
                        } else {
                            valueFormat = {
                                type: ['String', 'Number', 'Boolean'],
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
                                selectors: [],
                                ip: [],
                                topo: [],
                                filters: [],
                                excludes: []
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
            },
            isRequired () {
                let required = false
                if (this.option.showRequired === true && 'validation' in this.scheme.attrs) {
                    required = this.scheme.attrs.validation.some(item => {
                        return item.type === 'required'
                    })
                }
                return required
            },
            updateForm (fieldArr, val) {
                this.$emit('change', fieldArr, val)
            },
            onShowForm () {
                this.showForm = true
            },
            onHideForm () {
                this.showForm = false
            },
            onHookForm (val) {
                this.$emit('onHook', this.scheme.tag_code, val)
            },
            validate (combineValue) {
                if (!this.hook) {
                    return this.$refs.tagComponent.validate(combineValue)
                }
                return true
            }
        }
    }
</script>
<style lang="scss">
.rf-form-item {
    position: relative;
    margin: 15px 0;
    min-height: 36px;
    &:first-child {
        margin-top: 0;
    }
    &:last-child {
        margin-bottom: 0;
    }
    &.rf-has-hook {
        & > .rf-tag-form {
            margin-right: 30px;
        }
    }
    &.rf-col-layout {
        display: inline-block;
    }
    .rf-tag-label {
        float: left;
        position: relative;
        margin-top: 8px;
        width: 100px;
        font-size: 14px;
        color: #313238;
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
    &.show-label > .rf-tag-form {
        margin-left: 120px;
    }
    .rf-tag-hook {
        position: absolute;
        top: 8px;
        right: 0;
        z-index: 1;
    }
    .rf-view-value {
        display: inline-block;
        height: 36px;
        line-height: 36px;
        font-size: 14px;
        word-wrap: break-word;
        word-break: break-all;
    }
    .el-table__empty-text{
        line-height: 20px;
        width: 100%;
    }
}
</style>
