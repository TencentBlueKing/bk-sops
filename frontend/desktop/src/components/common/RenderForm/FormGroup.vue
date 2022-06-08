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
<template>
    <div class="rf-form-group" :class="[{ 'rf-has-hook': option.showHook }, scheme.status || '']" v-show="showForm">
        <!-- 分组名称和描述 -->
        <div v-if="showFormTitle" :class="['rf-group-name', { 'not-reuse': showNotReuseTitle }]">
            <span class="name">{{scheme.name || scheme.attrs.name}} ({{ scheme.tag_code }})</span>
            <span v-if="scheme.attrs.desc" class="rf-group-desc">
                <i
                    v-bk-tooltips="{
                        content: scheme.attrs.desc,
                        placements: ['right'],
                        zIndex: 2006
                    }"
                    class="common-icon-info">
                </i>
            </span>
            <span v-if="showNotReuseTitle" class="not-reuse-tip">
                <i class="common-icon-dark-circle-warning"></i>
                {{ $t('未能重用') }}
            </span>
            <span class="pre-mako-tip" v-if="scheme.attrs.pre_mako_tip">
                <i class="bk-icon icon-exclamation-circle"></i>
                {{ scheme.attrs.pre_mako_tip }}
            </span>
        </div>
        <!-- 分组勾选 -->
        <div v-if="hook" class="rf-form-item rf-has-hook show-label">
            <label v-if="option.showLabel" class="rf-tag-label">
                {{scheme.attrs.name}}
            </label>
            <div class="rf-tag-form rf-has-hook">
                <bk-input :disabled="true" :value="String(value)"></bk-input>
            </div>
        </div>
        <!-- 分组表单元素 -->
        <component
            v-else
            v-for="(form, index) in scheme.attrs.children"
            :key="`${form.tag_code}_${index}`"
            :is="form.type === 'combine' ? 'FormGroup' : 'FormItem'"
            :constants="constants"
            :scheme="form"
            :option="groupOption"
            :value="value[form.tag_code]"
            :parent-value="value"
            @init="$emit('init', $event)"
            @change="updateForm">
        </component>
        <!-- 变量勾选checkbox -->
        <div class="rf-tag-hook" v-if="showHook">
            <i
                :class="['common-icon-variable-cite hook-icon', { actived: hook, disabled: !option.formEdit || !render }]"
                v-bk-tooltips="{
                    content: hook ? i18n.hooked : i18n.cancelHook,
                    placement: 'bottom',
                    zIndex: 3000
                }"
                @click="onHookForm(!hook)">
            </i>
            <i
                :class="['common-icon-render-skip render-skip-icon', { actived: !render, disabled: !option.formEdit || hook }]"
                v-bk-tooltips="{
                    content: !render ? $t('取消渲染豁免') : $t('渲染豁免'),
                    placement: 'bottom',
                    zIndex: 3000
                }"
                @click="onRenderChange">
            </i>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'

    export default {
        name: 'FormGroup',
        components: {
            FormItem: () => import('./FormItem.vue')
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
                type: [Object, String],
                default () {
                    return {}
                }
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
            if ('formViewHidden' in this.scheme.attrs) {
                showForm = !this.scheme.attrs.formViewHidden
            }

            // 子 tag 配置项里 showHook 置为 false
            const groupOption = Object.assign({}, this.option, { showHook: false, showGroup: false })
            // 是否展示右侧变量勾选checkbox
            const showHook = ('hookable' in this.scheme.attrs)
                ? (this.scheme.attrs.hookable && this.option.showHook)
                : !!this.option.showHook

            return {
                eventActions: {}, // combine 类型配置项定义的事件回调函数
                groupOption,
                showForm, // combine 类型 Tag 组是否显示
                showHook, // combine 类型 Tag 组是否可勾选
                i18n: {
                    hooked: gettext('取消引用为全局变量'),
                    cancelHook: gettext('引用为全局变量')
                }
            }
        },
        computed: {
            showFormTitle () {
                return !this.hook && this.option.showGroup && !!(this.scheme.name || this.scheme.attrs.name)
            },
            showNotReuseTitle () {
                return this.option.formEdit && this.scheme.attrs.notReuse
            }
        },
        watch: {
            option: {
                handler: function (val) {
                    const option = Object.assign({}, this.groupOption, val, { showHook: false, showGroup: false })
                    this.groupOption = option
                },
                deep: true
            }
        },
        created () {
            const scheme = this.scheme

            // 注册 combine 配置项里的事件函数到父组件实例
            // 父组件目前包括 RenderForm(根组件)、FormGroup(combine 类型)、TagDataTable(表格类型)
            if (scheme.events) {
                scheme.events.map(item => {
                    const eventSource = `${item.source}_${item.type}`
                    this.eventActions[eventSource] = this.getEventHandler(item.action)
                    this.$parent.$on(eventSource, this.eventActions[eventSource])
                })
            }

            // 注册标准插件配置项 methods 属性里的方法到 Tag 实例组件
            // 标准插件配置项里的方法会重载 mixins 里定义的方法
            if (scheme.methods) {
                Object.keys(scheme.methods).map(item => {
                    if (typeof scheme.methods[item] === 'function') {
                        this[item] = scheme.methods[item]
                    }
                })
            }
        },
        beforeDestroy () {
            if (this.scheme.events) {
                this.scheme.events.forEach((item) => {
                    const eventSource = `${item.source}_${item.type}`
                    this.$parent.$off(eventSource, this.eventActions[eventSource])
                })
            }
        },
        mounted () {
            // 组件插入到 DOM 后， 在父组件上发布该 combine 组件的 init 事件，触发标准插件配置项里监听的函数
            this.$nextTick(() => {
                this.emit_event(this.tagCode, 'init', this.value)
            })
        },
        methods: {
            updateForm (fieldArr, val) {
                fieldArr.unshift(this.scheme.tag_code)
                this.$emit('change', fieldArr, val)
            },
            onHookForm (val) {
                if (!this.option.formEdit || !this.render) {
                    return
                }
                this.$emit('onHook', this.scheme.tag_code, val)
            },
            onRenderChange () {
                if (!this.option.formEdit || this.hook) {
                    return
                }
                this.$emit('onRenderChange', this.scheme.tag_code, !this.render)
            },
            get_parent () {
                return this.$parent
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
                            // combine组件或tag组件
                            childComponent = tagCode === 'combine' ? item : item.$refs.tagComponent
                            return true
                        }
                    })
                } else {
                    childComponent = this.$children.map(item => {
                        return item.scheme.tag_code === 'combine' ? item : item.$refs.tagComponent
                    })
                }
                return childComponent
            },
            getEventHandler (action) {
                return (data) => {
                    action.call(this, data)
                }
            },
            emit_event (name, type, data) {
                this.$parent.$emit(`${name}_${type}`, data)
            },
            show () {
                this.showForm = true
            },
            hide () {
                this.showForm = false
            },
            validate () {
                let isValid = true
                // 表单未被勾选并且为显示状态
                if (!this.hook && this.showForm) {
                    this.$children.forEach(childComp => {
                        const compType = childComp.$options.name

                        if (compType !== 'FormItem' && compType !== 'FormGroup') {
                            return
                        }

                        const singleItemValid = childComp.validate()

                        if (isValid) {
                            isValid = singleItemValid
                        }
                    })
                }
                
                return isValid
            }
        }
    }
</script>
<style lang="scss">
.rf-form-group {
    position: relative;
    &.added {
        background: rgba(220,255,226,0.30);
    }
    &.deleted {
        background: #ffeeec;
    }
    &.rf-has-hook .rf-tag-form {
        margin-right: 64px;
    }
    .rf-group-name {
        display: block
    }
    .rf-tag-hook {
        position: absolute;
        top: 0;
        right: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 8px;
        width: 56px;
        height: 32px;
        background: #f0f1f5;
        border-radius: 2px;
        z-index: 1;
        .hook-icon,
        .render-skip-icon {
            font-size: 16px;
            color: #979ba5;
            cursor: pointer;
            &.disabled {
                color: #c4c6cc;
                cursor: not-allowed;
            }
            &.actived {
                color: #3a84ff;
            }
        }
        .hook-icon {
            font-size: 19px;
        }
    }
}
</style>
