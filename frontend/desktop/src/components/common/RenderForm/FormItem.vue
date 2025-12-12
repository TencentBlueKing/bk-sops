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
<template>
    <div
        v-show="showForm"
        :key="randomKey"
        :class="[
            'rf-form-item',
            'clearfix',
            scheme.status || '',
            {
                'rf-has-hook': option.showHook,
                'show-label': option.showLabel,
                'show-render': isShowRenderIcon,
                'rf-view-mode': !option.formMode,
                'rf-col-layout': scheme.attrs.cols,
                'rf-section-item': scheme.type === 'section'
            }
        ]"
        :style="{
            width: (scheme.attrs.cols ? scheme.attrs.cols / 12 * 100 : 100) + '%'
        }">
        <!-- 分组 Tag，样式特殊处理 -->
        <tag-section
            v-if="scheme.type === 'section'"
            ref="tagComponent"
            :name="scheme.attrs.name"
            :tag-code="scheme.tag_code">
        </tag-section>
        <template v-else>
            <!-- 表单作为全局变量时的名称 -->
            <div v-if="showFormTitle" :class="['rf-group-name', { 'not-reuse': showNotReuseTitle, 'scheme-select-name': scheme.type === 'select' && !scheme.attrs.remote }]">
                <span class="scheme-name">{{scheme.name || scheme.attrs.name}}</span>
                <span class="required" v-if="isRequired()">*</span>
                <span class="scheme-code" v-if="!option.showHook">{{ scheme.tag_code }}</span>
                <i
                    v-if="showNotReuseTitle || showPreMakoTip"
                    v-bk-tooltips="{
                        content: showNotReuseTitle ? $t('未能重用') : scheme.attrs.pre_mako_tip,
                        placement: 'top-end',
                        boundary: 'window',
                        zIndex: 2072
                    }"
                    class="common-icon-dark-circle-warning">
                </i>
                <!-- <span class="used-tip" v-else-if="!scheme.attrs.html_used_tip && scheme.attrs.used_tip">
                    <i class="common-icon-dark-circle-warning"></i>
                    {{ scheme.attrs.used_tip }}
                </span> -->
            </div>
            <!-- 表单名称 -->
            <label
                v-if="option.showLabel && scheme.attrs.name"
                class="rf-tag-label">
                <span
                    v-bk-tooltips="{
                        allowHtml: true,
                        content: scheme.attrs.tips,
                        placement: 'top-start',
                        theme: 'light',
                        extCls: 'rf-label-tips',
                        boundary: 'window',
                        zIndex: 2072,
                        disabled: !!!scheme.attrs.tips
                    }"
                    class="label"
                    :class="{ 'tag-label-tips': scheme.attrs.tips }">
                    {{scheme.attrs.name}}
                </span>
                <span class="required" v-if="isRequired()">*</span>
            </label>
            <!-- 参数被使用占位popover -->
            <bk-popover
                v-if="scheme.attrs.html_used_tip"
                ref="htmlUsedTipPopper"
                placement="top-start"
                theme="light"
                always
                :z-index="2072"
                class="html-used-tippy"
                ext-cls="html-used-tippy-popper">
                <div class="empty-box"></div>
                <template slot="content">
                    <p class="tip-title">
                        <i class="common-icon-dark-circle-warning"></i>
                        {{ scheme.attrs.used_tip }}
                    </p>
                    <p class="tip-content">{{ $t('将沿用原参数值提交') }}</p>
                    <p class="tip-btn" @click="handleFoldUsedTip">{{ $t('知道了') }}</p>
                </template>
            </bk-popover>
            <!-- 表单勾选为全局变量 -->
            <div v-show="hook" class="rf-tag-form">
                <bk-input :disabled="true" :value="String(value)"></bk-input>
            </div>
            <!-- 表单元素 -->
            <component
                v-show="!hook"
                :class="[
                    scheme.attrs.name ? 'rf-tag-form' : '',
                    groupComponent ? 'form-item-group' : '',
                    showTagUsedStyle
                ]"
                ref="tagComponent"
                :is="tagComponent"
                v-bind="getDefaultAttrs()"
                :tag-code="scheme.tag_code"
                :hook="hook"
                :render="render"
                :constants="constants"
                :scheme="scheme"
                :atom-events="scheme.events"
                :atom-methods="scheme.methods"
                :value="formValue"
                :parent-value="parentValue"
                @init="$emit('init', $event)"
                @blur="$emit('blur', $event)"
                @change="updateForm"
                @onShow="onShowForm"
                @onHide="onHideForm">
            </component>
            <!-- 变量勾选checkbox -->
            <div class="rf-tag-hook" v-if="showHook" :class="{ 'hide-render-icon': !isShowRenderIcon }">
                <i
                    :class="['common-icon-variable-hook hook-icon', { actived: hook, disabled: !option.formEdit || !render }]"
                    v-bk-tooltips="{
                        content: hook ? $t('取消使用变量，节点内维护') : $t('转换为变量，集中维护'),
                        placement: 'bottom',
                        zIndex: 3000
                    }"
                    @click="onHookForm(!hook)">
                </i>
                <i
                    v-if="isShowRenderIcon"
                    :class="['common-icon-render-skip render-skip-icon', { actived: !render, disabled: !option.formEdit || hook }]"
                    v-bk-tooltips="{
                        content: !render ? $t('取消变量免渲染') : $t('变量免渲染'),
                        placement: 'bottom',
                        zIndex: 3000
                    }"
                    @click="onRenderChange">
                </i>
            </div>
            <div class="scheme-desc-wrap" v-if="scheme.attrs.desc">
                <div class="hide-html-text">{{ scheme.attrs.desc }}</div>
                <div :class="['rf-group-desc', { 'is-fold': !isExpand }]">{{ scheme.attrs.desc }}</div>
                <div :class="{ 'mt10': isExpand }" v-if="isDescTipsShow">
                    <span v-if="!isExpand">...</span>
                    <span class="expand-btn" @click="isExpand = !isExpand">{{ isExpand ? $t('收起') : $t('展开全部') }}</span>
                </div>
            </div>
        </template>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'
    import { checkDataType, getDefaultValueFormat } from '@/utils/checkDataType.js'
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
                return `-${match.toLowerCase()}`
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
            // 表单是否勾选为全局变量
            hook: {
                type: Boolean,
                default: false
            },
            // 表单是否配置渲染豁免
            render: {
                type: Boolean,
                default: true
            },
            constants: {
                type: Object,
                default () {
                    return {}
                }
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
                randomKey: null,
                tagComponent: `tag-${this.scheme.type.replace(/_/g, '-')}`,
                showForm,
                showHook,
                formValue,
                isDescTipsShow: false,
                isExpand: false,
                isShowRenderIcon: false // 是否展示免渲染icon
            }
        },
        computed: {
            showFormTitle () {
                return this.option.showGroup && !!(this.scheme.name || this.scheme.attrs.name)
            },
            showNotReuseTitle () {
                return this.option.formEdit && this.scheme.attrs.notReuse
            },
            showPreMakoTip () {
                return this.option.formEdit && this.scheme.attrs.pre_mako_tip
            },
            showTagUsedStyle () {
                const { type, attrs } = this.scheme
                if (attrs.html_used_tip && ['input', 'textarea', 'select'].includes(type)) {
                    return 'rf-tag-used'
                }
                return ''
            },
            groupComponent () {
                const groupComponent = [
                    'tag-set-allocation',
                    'tag-upload',
                    'tag-ip-selector',
                    'tag-host-allocation',
                    'tag-datatable'
                ]
                return groupComponent.includes(this.tagComponent)
            }
        },
        watch: {
            scheme (val) {
                this.tagComponent = `tag-${this.scheme.type.replace(/_/g, '-')}`
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
        created () {
            // 移除「变量免渲染」的功能开关
            const { type, attrs } = this.scheme
            if (type === 'code_editor') {
                if (attrs.variable_render === false) { // variable_render 开启变量渲染
                    /**
                     * need_render:
                        1. false
                            之前已勾选，现在去掉免渲染icon
                        2.true，判断value
                            a. 不包含${}，需要把need_render置为false，去掉免渲染icon
                            b. 包含${}，保留免渲染icon
                     */
                    if (this.render) {
                        const regex = /\${[a-zA-Z_]\w*}/g
                        const matchList = this.value.match(regex)
                        const isMatch = matchList && matchList.some(item => {
                            return !!this.constants[item]
                        })
                        if (isMatch) {
                            this.isShowRenderIcon = true
                        } else {
                            this.showHook = false
                            this.$nextTick(() => {
                                this.onRenderChange('automatic')
                            })
                        }
                    } else {
                        this.showHook = false
                    }
                } else {
                    if (!this.render) {
                        this.isShowRenderIcon = true
                    }
                }
            } else if (!this.render) { // 如果开启了免渲染则展示按钮
                this.isShowRenderIcon = true
            }
        },
        mounted () {
            const showDom = this.$el.querySelector('.rf-group-desc')
            const hideDom = this.$el.querySelector('.hide-html-text')
            if (showDom && hideDom) {
                const showDomHeight = showDom.getBoundingClientRect().height
                const hideDomHeight = hideDom.getBoundingClientRect().height
                this.isDescTipsShow = hideDomHeight > showDomHeight
            }
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
                // 不使用默认值
                if (this.scheme.attrs.usedValue) {
                    return tools.deepClone(val)
                }
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
                    defaultValueFormat = getDefaultValueFormat(this.scheme)
                }

                const defaultValueType = Array.isArray(defaultValueFormat.type) ? defaultValueFormat.type : [defaultValueFormat.type]

                // 处理非密码框表单使用密码变量时，需要展示******的场景
                // 非密码框且值类型包含string的表单，如果当前value为Object类型，且type值为password_value时，展示值为******
                if (this.scheme.type !== 'password' && defaultValueType.includes('String') && checkDataType(val) === 'Object' && val.type === 'password_value') {
                    return '******'
                }

                // 元变量表单数据为Object格式时，取默认值
                if (this.constants[this.scheme.tag_code]?.is_meta && checkDataType(val) === 'Object') {
                    return val.default
                }

                if (defaultValueType.includes(valueType)) {
                    formValue = tools.deepClone(val)
                } else {
                    formValue = tools.deepClone(defaultValueFormat.value)
                    this.updateForm([this.scheme.tag_code], formValue)
                }

                return formValue
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
                if (!this.option.formEdit || !this.render) {
                    return
                }
                this.$emit('onHook', this.scheme.tag_code, val)
            },
            onRenderChange (source = 'click') {
                if (!this.option.formEdit || this.hook) {
                    return
                }
                this.$emit('onRenderChange', {
                    key: this.scheme.tag_code,
                    value: !this.render,
                    name: this.scheme.attrs.name,
                    source
                })
            },
            validate (combineValue) {
                // 表单未被勾选并且为显示状态
                if (!this.hook && this.showForm) {
                    return this.$refs.tagComponent.validate(combineValue)
                }
                return true
            },
            handleFoldUsedTip () {
                this.$refs['htmlUsedTipPopper'].hideHandler()
                this.scheme.attrs.html_used_tip = false
                this.scheme.attrs.disabled = true
                this.formValue = this.constants[this.scheme.tag_code].value
                this.updateForm([this.scheme.tag_code], this.formValue)
                this.randomKey = new Date().getTime()
            }
        }
    }
</script>
<style lang="scss">
.rf-form-item {
    position: relative;
    margin-top: 15px;
    min-height: 32px;
    font-size: 12px;
    color: #63656e;
    &:first-child {
        margin-top: 0;
    }
    &:last-child {
        margin-bottom: 0;
    }
    &.rf-has-hook {
        & > .rf-tag-form {
            margin-right: 40px;
        }
    }
    &.show-render {
        > .rf-tag-form {
            margin-right: 58px;
        }
        .hook-icon {
            padding-right: 3px !important;
        }
    }
    &.rf-col-layout {
        display: inline-block;
        padding-right: 10px;
        vertical-align: text-bottom;
    }
    &.rf-view-mode {
        margin: 8px 0;
    }
    &.rf-section-item {
        min-height: initial;
    }
    &.added {
        background: rgba(220,255,226,0.30);
    }
    &.deleted {
        background: #ffeeec;
    }
    .required {
        color: #F00;
        margin-left: 5px;
        font-family: "SimSun";
    }
    .rf-tag-label {
        float: left;
        position: relative;
        margin-top: 8px;
        width: 100px;
        font-size: 12px;
        color: #666666;
        text-align: right;
        word-wrap: break-word;
        word-break: break-all;
        .tag-label-tips {
            position: relative;
            &::after {
                content: '';
                position: absolute;
                left: 0;
                bottom: -3px;
                border-top: 1px dashed #979ba5;
                width: 100%
            }
        }
    }
    &.show-label > .rf-tag-form {
        margin-left: 130px;
    }
    .html-used-tippy {
        position: absolute;
        z-index: -2;
        left: 130px;
        .empty-box {
            width: 32px;
            height: 32px;
        }
    }
    .rf-tag-hook {
        position: absolute;
        top: 0;
        right: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 32px;
        background: #f0f1f5;
        border-radius: 2px;
        z-index: 1;
        cursor: pointer;
        .hook-icon,
        .render-skip-icon {
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            color: #979ba5;
            &.disabled {
                color: #c4c6cc;
                cursor: not-allowed;
            }
            &.actived {
                color: #3a84ff;
            }
        }
        .hook-icon {
            line-height: 31px;
            padding: 0 8px;
            font-size: 16px;
        }
        .render-skip-icon {
            padding: 0 8px 0 3px;
        }
        .icon-angle-up-fill {
            font-size: 12px;
            color: #c4c6cc;
            margin: 3px 0 0 6px;
        }
        &.hide-render-icon {
            justify-content: center;
        }
    }
    .rf-view-value {
        display: inline-block;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        word-wrap: break-word;
        word-break: break-all;
    }
    .el-table__empty-text{
        line-height: 20px;
        width: 100%;
    }
    .el-input:not(.el-input--mini) {
        .el-input__inner {
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            border-radius: 2px !important;
        }
        .el-input__prefix {
            .el-input__icon {
                line-height: 32px;
            }
            .el-icon-time {
                line-height: 36px;
            }
        }
        &.is-disabled {
            .el-input__inner{
                background-color: #fafbfd !important;
                border-color: #dcdee5 !important;
            }
        }
    }
    .el-select:not(.el-select--mini) {
        .el-input__suffix {
            .el-input__icon {
                line-height: 32px;
            }
        }
    }
    .el-radio__label,
    .el-checkbox__label {
        font-size: 12px;
        font-weight: normal;
        color: #63656e;
    }
    .el-tree-node__label,
    .el-tree__empty-block {
        font-size: 12px;
    }
}
.tag-component-popper {
    // magicbox 组件引入了 popover 管理，z-index 起始值从 2000 开始，而 element-ui 组件自己的 popover 管理也是从 2000 开始
    // 两边组件的 z-index 维护，并不能保证所有组件层级按照一个值递增，所以会出现弹出层可能被盖住的情况
    // 这里把 tag 组件里涉及到弹出层情况的 z-index 固定为 3300
    // notice：新增的弹出层组件需要手动添加这个 class
    z-index: 3300 !important;
}
.el-select-dropdown .el-select-dropdown__item {
    font-size: 12px;
}
.el-input__icon {
    line-height: 32px;
}
.rf-label-tips {
    max-width: 480px;
    .tippy-tooltip {
        color: #63656e;
        border: 1px solid #dcdee5;
        box-shadow: 0 0 5px 0 rgba(0,0,0,0.09);
    }
}
</style>
