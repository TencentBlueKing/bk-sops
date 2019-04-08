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
    <div class="rf-form-group" v-show="showForm">
        <div v-if="!hook && option.showGroup && scheme.attrs.name" class="rf-group-name">
            <h3 class="name">{{scheme.attrs.name}}</h3>
            <div v-if="scheme.attrs.desc" class="rf-group-desc">
                <i v-bktooltips.left="scheme.attrs.desc" class="common-icon-dark-circle-warning"></i>
            </div>
        </div>
        <div v-if="hook" class="rf-form-item rf-has-hook">
            <label v-if="option.showLabel" class="rf-tag-label">
                {{scheme.attrs.name}}
            </label>
            <div class="rf-tag-form rf-has-hook">
                <el-input :disabled="true" :value="String(value)"></el-input>
            </div>
        </div>
        <component
            v-else
            v-for="(form, index) in scheme.attrs.children"
            :key="`${form.tag_code}_${index}`"
            :is="form.type === 'combine' ? 'FormGroup' : 'FormItem'"
            :class="{'rf-has-hook': form.type !== 'combine' && showHook}"
            :scheme="form"
            :option="groupOption"
            :value="value[form.tag_code]"
            :parentValue="value"
            @change="updateForm">
        </component>
        <div class="rf-tag-hook" v-if="showHook">
            <BaseCheckbox
                v-bktooltips="{
                    content: hook ? i18n.hooked : i18n.cancelHook,
                    placements: ['left'],
                    customClass: 'offset-left-tooltip'
                }"
                :isChecked="hook"
                @checkCallback="onHookForm">
            </BaseCheckbox>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import FormItem from './FormItem.vue'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'

export default {
    name: 'FormGroup',
    components: {
        FormItem,
        BaseCheckbox
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
        hook: {
            type: Boolean,
            default: false
        }
    },
    data () {
        // 子 tag 配置项里 showHook 置为 false
        const groupOption = Object.assign({}, this.option,{ showHook: false, showGroup: false })

        const showForm = ('hidden' in this.scheme.attrs) ? !this.scheme.attrs.hidden : true
        const showHook = ('hookable' in this.scheme.attrs) ?
            (this.scheme.attrs.hookable && this.option.showHook) :
            !!this.option.showHook

        return {
            eventActions: {}, // combine 类型配置项定义的事件回调函数
            groupOption,
            showForm, // combine 类型 Tag 组是否显示
            showHook, // combine 类型 Tag 组是否可勾选
            i18n: {
                hooked: gettext('取消勾选'),
                cancelHook: gettext('勾选参数作为全局变量')
            }
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
                this.eventActions[eventSource] = item.action
                this.$parent.$on(eventSource, (data) => {
                    this.eventActions[eventSource].call(this, data)
                })
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
    mounted () {
        // 组件插入到 DOM 后， 在父组件上发布该 combine 组件的 init 事件，触发标准插件配置项里监听的函数
        this.$nextTick(()=>{
            this.$parent.$emit(`${this.tagCode}_init`, this.value)
        })
    },
    methods: {
        updateForm (fieldArr, val) {
            fieldArr.unshift(this.scheme.tag_code)
            this.$emit('change', fieldArr, val)
        },
        onHookForm (val) {
            this.$emit('onHook', this.scheme.tag_code, val)
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
            return isValid
        }
    }
}
</script>
<style lang="scss">
.rf-form-group {
    position: relative;
    .rf-group-name {
        display: block
    }
    .rf-tag-hook {
        position: absolute;
        top: 3px;
        right: 0;
        z-index: 1;
    }
}
</style>
