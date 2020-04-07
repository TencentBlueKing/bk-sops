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
    <li
        :class="['clearfix', 'variable-item',
                 { 'variable-editing': isVariableEditing && theKeyOfEditing === constant.key }
        ]">
        <div class="variable-content" @click="onEditVariable(constant.key, constant.index)">
            <i v-if="!isSystemVar && !isShowVariableEdit && theKeyOfViewCited !== constant.key" class="col-item-drag bk-icon icon-sort"></i>
            <i v-if="isSystemVar" class="common-icon-lock-disable"></i>
            <span :title="constant.name" class="col-item col-name">
                {{ constant.name }}
            </span>
            <span class="col-item col-key">
                {{ constant.key }}
            </span>
            <span class="col-item col-attributes">
                <span class="icon-wrap">
                    <i
                        v-if="constant.source_type !== 'component_outputs'"
                        class="common-icon-show-left"
                        v-bk-tooltips="{
                            content: i18n.inputs,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-hide-right color-org"
                        v-bk-tooltips="{
                            content: i18n.outputs,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-if="constant.show_type === 'show'"
                        class="common-icon-eye-show"
                        v-bk-tooltips="{
                            content: i18n.show,
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-eye-hide color-org"
                        v-bk-tooltips="{
                            content: i18n.hide,
                            placements: ['bottom']
                        }">
                    </i>
                </span>
            </span>
            <span class="col-item col-output">
                <div @click.stop>
                    <bk-switcher
                        size="min"
                        theme="primary"
                        :value="outputed"
                        @change="onChangeVariableOutput(constant.key, $event)">
                    </bk-switcher>
                </div>
            </span>
            <span
                :class="[
                    'col-item',
                    'col-cited',
                    {
                        'disabled': citedList.length === 0
                    }
                ]"
                @click.stop="onViewCitedList">
                {{ citedList.length }}
            </span>
            <span class="col-item col-operation">
                <span class="col-operation-item"
                    v-bk-tooltips.click="{
                        content: i18n.copied,
                        placements: ['bottom']
                    }"
                    @click.stop="onCopyKey(constant.key)">
                    {{ i18n.copy }}
                </span>
                <span
                    v-if="!isSystemVar"
                    class="col-operation-item"
                    @click.stop="onDeleteVariable(constant.key)">
                    {{ i18n.delete }}
                </span>
            </span>
        </div>
        <div
            v-if="isShowVariableEdit && !isSystemVar"
            :key="`${constant.key}-edit`">
            <VariableEdit
                ref="editVariablePanel"
                :variable-data="variableData"
                :variable-type-list="variableTypeList"
                :is-system-var="isSystemVar"
                :is-new-variable="false"
                :is-hide-system-var="isHideSystemVar"
                :system-constants="systemConstants"
                :var-operating-tips="varOperatingTips"
                @scrollPanelToView="scrollPanelToView"
                @onChangeEdit="onChangeEdit">
            </VariableEdit>
        </div>
        <div
            v-if="isShowVariableEdit && isSystemVar">
            <SystemVariableEdit
                :variable-data="variableData"
                :var-operating-tips="varOperatingTips">
            </SystemVariableEdit>
        </div>
        <VariableCitedList
            v-if="theKeyOfViewCited === constant.key"
            :constant="constant"
            :cited-list="citedList"
            @onCitedNodeClick="onCitedNodeClick">
        </VariableCitedList>
    </li>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    import VariableEdit from './VariableEdit.vue'
    import VariableCitedList from './VariableCitedList.vue'
    import SystemVariableEdit from './SystemVariableEdit.vue'
    export default {
        name: 'VariableItem',
        components: {
            VariableEdit,
            VariableCitedList,
            SystemVariableEdit
        },
        props: [
            'outputed',
            'constant',
            'variableData',
            'varOperatingTips',
            'theKeyOfEditing',
            'theKeyOfViewCited',
            'isHideSystemVar',
            'systemConstants',
            'variableTypeList',
            'isVariableEditing'
        ],
        data () {
            return {
                copyText: '',
                i18n: {
                    copied: gettext('已复制'),
                    inputs: gettext('输入'),
                    outputs: gettext('输出'),
                    show: gettext('显示'),
                    hide: gettext('隐藏'),
                    copy: gettext('复制'),
                    delete: gettext('删除')
                }
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities
            }),
            isSystemVar () {
                return this.constant.source_type === 'system'
            },
            isShowVariableEdit () {
                return this.isVariableEditing && this.theKeyOfEditing === this.constant.key
            },
            citedList () {
                const sourceInfo = this.constant.source_info
                // 该全局变量被哪些节点勾选的集合
                const nodes = Object.keys(sourceInfo).map(id => id)

                // 输入参数表单直接填写变量key的情况
                const escapeStr = this.constant.key.replace(/[${}]/g, '\\$&')
                const keyReg = new RegExp(escapeStr)
                Object.keys(this.activities).forEach(id => {
                    // 节点已在引用节点列表中需要去重
                    if (nodes.includes(id)) {
                        return
                    }
                    const activity = this.activities[id]
                    if (activity.type === 'SubProcess') { // 子流程任务节点
                        Object.keys(activity.constants).forEach(key => {
                            const varItem = activity.constants[key]
                            // 隐藏类型变量不考虑
                            if (varItem.show_type === 'hide') {
                                return
                            }
                            // 表单已勾选到全局变量
                            const isExist = sourceInfo[id] && sourceInfo[id].includes(varItem.key)
                            if (isExist) {
                                return
                            }
                            // 匹配表单项的值是否包含变量的key
                            if (typeof varItem.value === 'string' && keyReg.test(varItem.value)) {
                                nodes.push(id)
                            }
                        })
                    } else { // 标准插件任务节点
                        const component = activity.component
                        Object.keys(component.data || {}).forEach(form => { // 空任务节点可能会存在 data 为 undefined 的情况
                            const val = component.data[form].value
                            const isExist = sourceInfo[id] && sourceInfo[id].includes(form)
                            if (isExist) {
                                return
                            }
                            if (typeof val === 'string' && keyReg.test(val)) {
                                nodes.push(id)
                            }
                        })
                    }
                })
                return nodes
            }
        },
        methods: {
            /**
             * 变量 key 复制
             */
            onCopyKey (key) {
                this.copyText = key
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            /**
             * 复制操作回调函数
             */
            copyHandler (e) {
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                e.preventDefault()
            },
            // 查看引用节点信息
            onViewCitedList () {
                // 节点详情点开时不显示引用列表
                if (this.citedList.length > 0) {
                    this.onChangeEdit(false)
                    this.$emit('onViewCitedList', this.constant.key)
                }
            },
            onChangeVariableOutput (key, checked) {
                this.$emit('onChangeVariableOutput', { key, checked })
            },
            onDeleteVariable (key) {
                this.$emit('onDeleteVariable', key)
            },
            onEditVariable (key, index) {
                this.$emit('onEditVariable', key, index)
            },
            scrollPanelToView (index) {
                this.$emit('scrollPanelToView', index)
            },
            onChangeEdit (val) {
                this.$emit('onChangeEdit', val)
            },
            onCitedNodeClick (nodeId) {
                this.$emit('onCitedNodeClick', nodeId)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
$localBorderColor: #d8e2e7;
.variable-header, .variable-list {
    position: relative;
    font-size: 12px;
}
.variable-item {
    position: relative;
    border-bottom: 1px solid #ebebeb;
    &.variable-editing {
        background: $blueStatus;
    }
    .variable-content {
        position: relative;
        padding-left: 50px;
        display: flex;
        height: 42px;
        line-height: 42px;
        cursor: pointer;
        &:hover {
            background: $blueStatus;
            .col-item-drag {
                display: inline-block;
            }
        }
    }
    .col-name {
        width: 242px;
    }
    .col-key {
        width: 174px;
    }
    .col-attributes {
        width: 77px;
        .icon-wrap {
            vertical-align: middle;
            line-height: 1;
            display: inline-block;
            .common-icon-show-left {
                color: #219f42;
                font-size: 14px;
            }
            .common-icon-hide-right {
                font-size: 14px;
            }
            .common-icon-eye-show {
                margin-left: 8px;
                color: #219f42;
                font-size: 12px;
            }
            .common-icon-eye-hide {
                margin-left: 8px;
                font-size: 15px;
            }
            .color-org{
                color: #de9524;
            }
        }
    }
    .col-output {
        width: 58px;
    }
    .col-cited {
        width: 54px;
        color: #3a84ff;
        cursor: pointer;
        &.disabled {
            color: #333333;
        }
    }
}
.col-item {
    display: inline-block;
    font-size: 12px;
    vertical-align: middle;
    word-break: break-all;
    text-align: left;
}
.col-item-drag {
    display: none;
    position: absolute;
    top: 50%;
    left: 20px;
    transform: translate(0, -50%);
    color: #979ba5;
    cursor: move;
    &:hover {
        color: #348aff;
    }
}
.col-name {
    overflow: hidden;
    text-overflow:ellipsis;
    white-space: nowrap;
}
.col-key {
    position: relative;
    overflow: hidden;
    text-overflow:ellipsis;
    white-space: nowrap;
    .col-key-copy {
        display: none;
        margin-left: 2px;
        color: #52699d;
        text-decoration: underline;
    }
}
.col-operation {
    .col-operation-item {
        color: #3a84ff;
        cursor: pointer;
        &:not(:first-child) {
            margin-left: 10px;
        }
    }
}
.common-icon-lock-disable {
    position: absolute;
    top: 50%;
    left: 20px;
    transform: translate(0, -50%);
    color: #979ba5;
}
</style>
