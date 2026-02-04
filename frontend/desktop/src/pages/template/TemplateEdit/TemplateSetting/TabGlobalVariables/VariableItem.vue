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
    <div class="variable-item" :class="{ 'variable-animation': newCloneKeys.includes(variableData.key) }">
        <div :class="['variable-content', { 'view-model': isViewMode }]" @click="onEditVariable(variableData.key, variableData.index)">
            <i v-if="!isSystemVar && !isProjectVar && !showCitedList" class="col-item-drag common-icon-drawable f16"></i>
            <span v-if="!isViewMode && !isSystemVar && !isProjectVar" @click.stop class="col-item-checkbox">
                <bk-checkbox
                    :disabled="isComponentVar"
                    :value="variableChecked"
                    v-bk-tooltips="{ content: componentVarDisabledTip, disabled: !isComponentVar }"
                    @change="onChooseVariable">
                </bk-checkbox>
            </span>
            <i v-if="isSystemVar" class="variable-icon common-icon-lock-disable"></i>
            <i v-if="isProjectVar" class="variable-icon common-icon-paper"></i>
            <span class="col-item col-name" v-bk-overflow-tips="{ distance: 0 }">
                {{ variableData.name }}
            </span>
            <span class="col-item col-key" v-bk-overflow-tips="{ distance: 0 }">
                {{ variableData.key }}
                <i
                    class="common-icon-double-paper-2 copy-icon"
                    v-bk-tooltips.bottom="{
                        content: $t('复制'),
                        placement: 'bottom',
                        boundary: 'window'
                    }"
                    @click.stop="onCopyKey(variableData.key)">
                </i>
            </span>
            <span
                :class="['col-item col-cited', { 'active': showCitedList }]"
                @click.stop="onViewCitedList">
                {{ citedNum }}
            </span>
            <span
                :class="['col-item col-type', { 'active': showPreviewValue }]"
                v-bk-overflow-tips="{ distance: 0 }"
                @click.stop="onPreviewValue">
                {{ variableData.type || '--' }}
            </span>
            <!-- <span class="col-item col-attributes">
                <i
                    v-if="variableData.source_type !== 'component_outputs'"
                    class="common-icon-show-left"
                    v-bk-tooltips="{
                        content: $t('输入'),
                        placements: ['bottom'],
                        boundary: 'window'
                    }">
                </i>
                <i
                    v-else
                    class="common-icon-hide-right"
                    v-bk-tooltips="{
                        content: $t('输出') + $t('（') + $t('点击可快速定位原节点') + $t('）'),
                        placements: ['bottom'],
                        boundary: 'window'
                    }"
                    @click.stop="viewClick">
                </i>
            </span> -->
            <span class="col-item col-show" @click.stop>
                <bk-switcher
                    size="small"
                    theme="primary"
                    :disabled="isViewMode || variableData.isSysVar || variableData.source_type === 'component_outputs'"
                    :value="variableData.show_type === 'show'"
                    @change="onChangeVariableShow(variableData.key, $event)">
                </bk-switcher>
            </span>
            <span class="col-item col-output">
                <div @click.stop>
                    <bk-switcher
                        size="small"
                        theme="primary"
                        :value="outputed"
                        :disabled="isViewMode || variableData.isSysVar"
                        @change="onChangeVariableOutput(variableData.key, $event)">
                    </bk-switcher>
                </div>
            </span>
            <span class="col-item col-operation">
                <span
                    v-if="isViewMode || isInternalVal"
                    class="col-operation-item"
                    @click.stop="onEditVariable(variableData.key, variableData.index)">
                    {{ $t('查看') }}
                </span>
                <span v-else class="col-operation-item">{{ $t('编辑') }}</span>
            </span>
            <span class="col-item col-more" v-if="!isViewMode && !isInternalVal">
                <bk-popover placement="bottom" theme="light" :distance="0" :arrow="false" ext-cls="var-operate-popover">
                    <i class="bk-icon icon-more"></i>
                    <template slot="content">
                        <p
                            v-if="!isComponentVar"
                            class="operate-item"
                            @click.stop="onCloneVariable()">
                            {{ $t('克隆') }}
                        </p>
                        <p
                            :class="['operate-item', { 'disabled': isComponentIutputs }]"
                            v-bk-tooltips="{ content: componentVarDisabledTip, disabled: !isComponentIutputs }"
                            @click.stop="onDeleteVariable">{{ $t('删除') }}
                        </p>
                    </template>
                </bk-popover>
            </span>
        </div>
        <VariableCitedList
            v-if="showCitedList"
            :cited-list="citedList"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)">
        </VariableCitedList>
        <VariablePreviewValue
            v-if="showPreviewValue"
            :keyid="variableData.key"
            :params="previewParams">
        </VariablePreviewValue>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState } from 'vuex'
    import VariableCitedList from './VariableCitedList.vue'
    import VariablePreviewValue from './VariablePreviewValue.vue'

    export default {
        name: 'VariableItem',
        components: {
            VariableCitedList,
            VariablePreviewValue
        },
        props: {
            outputed: Boolean,
            variableData: Object,
            common: [String, Number],
            variableCited: Object,
            variableChecked: Boolean,
            newCloneKeys: Array,
            isViewMode: Boolean
        },
        data () {
            return {
                showCitedList: false,
                showPreviewValue: false,
                copyText: '',
                previewParams: {}
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable,
                'project_id': state => state.project.project_id,
                'bizId': state => state.project.bizId
            }),
            // 是否为内置变量
            isInternalVal () {
                const keys = Object.keys(this.internalVariable)
                return keys.some(key => key === this.variableData.key)
            },
            isSystemVar () {
                return this.variableData.source_type === 'system'
            },
            isProjectVar () {
                return this.variableData.source_type === 'project'
            },
            isComponentVar () {
                return ['component_outputs', 'component_inputs'].includes(this.variableData.source_type)
            },
            isComponentIutputs () {
                return this.variableData.source_type === 'component_inputs'
            },
            componentVarDisabledTip () {
                return this.variableData.source_type === 'component_inputs'
                    ? i18n.t('节点输入型变量仅支持从节点"取消使用变量"来删除')
                    : i18n.t('节点输出型变量仅支持从节点"取消接收输出"来删除')
            },
            citedList () {
                const defaultCiteData = {
                    activities: [],
                    conditions: [],
                    constants: []
                }
                return this.variableCited[this.variableData.key] || defaultCiteData
            },
            citedNum () {
                const { activities, conditions, constants } = this.citedList
                return activities.length + conditions.length + constants.length
            }
        },
        methods: {
            /**
             * 递归查找标准插件/子流程保存值中，存在匹配变量 key 的情况，更新节点引用列表
             * @param {Any} value 表单保存的值
             * @param {Array} nodes 保存引用节点的数组
             * @param {String} id 当前节点 id
             */
            setCitingVarNodes (value, nodes, id) {
                if (nodes.includes(id)) {
                    return
                }

                if (typeof value === 'string') {
                    const keyStr = this.variableData.key.replace(/[\$\{\}]/g, '')
                    const reg = /\$\{[\S\s]*?\}/gm
                    const matchResult = value.match(reg)

                    if (matchResult && matchResult.length) {
                        matchResult.some(result => {
                            if (result.includes(keyStr)) {
                                nodes.push(id)
                                return true
                            }
                        })
                    }
                } else if (typeof value === 'object') {
                    if (Array.isArray(value)) {
                        value.forEach(item => {
                            this.setCitingVarNodes(item, nodes, id)
                        })
                    } else if (Object.prototype.toString.call(value) === '[object Object]') {
                        Object.keys(value).forEach(key => {
                            const item = value[key]
                            this.setCitingVarNodes(item, nodes, id)
                        })
                    }
                }
            },
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
                e.preventDefault()
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                this.$bkMessage({
                    message: 'key' + i18n.t('已复制'),
                    theme: 'success'
                })
            },
            viewClick () {
                const { source_info: sourceInfo } = this.variableData
                const id = Object.keys(sourceInfo)[0]
                this.$emit('viewClick', id)
            },
            // 查看引用节点信息
            onViewCitedList () {
                this.showPreviewValue = false
                if (this.citedNum > 0 && !this.showCitedList) {
                    this.showCitedList = true
                } else {
                    this.showCitedList = false
                }
            },
            onChangeVariableShow (key, checked) {
                this.$emit('onChangeVariableShow', { key, checked })
            },
            onChangeVariableOutput (key, checked) {
                this.$emit('onChangeVariableOutput', { key, checked })
            },
            // 查看变量预览值
            onPreviewValue () {
                if (!this.variableData.type) return
                this.showCitedList = false
                if (this.showPreviewValue) {
                    this.showPreviewValue = false
                } else {
                    this.previewParams = {
                        constants: this.constants,
                        extra_data: {
                            executor: this.username,
                            project_id: this.common ? undefined : this.project_id,
                            biz_cc_id: this.common ? undefined : this.bizId
                        }
                    }
                    this.showPreviewValue = true
                }
            },
            onDeleteVariable () {
                if (this.isComponentIutputs) return
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('全局变量') + `【${this.variableData.key}】?`]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('删除变量将导致所有变量引用失效，请及时检查并更新节点配置')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: () => {
                        this.$emit('onDeleteVariable', this.variableData.key)
                    }
                })
            },
            onEditVariable (key, index) {
                this.$emit('onEditVariable', key, index)
            },
            onCloneVariable () {
                if (this.isComponentVar) return
                this.$emit('onCloneVariable', this.variableData)
            },
            onChooseVariable (value) {
                this.$emit('onChooseVariable', this.variableData, value)
            }
        }
    }
</script>
<style lang="scss">
    .var-operate-popover {
        width: 92px;
        height: 72px;
        .tippy-tooltip {
            padding: 4px 0;
            border: 1px solid #dcdee5;
        }
        .operate-item {
            line-height: 32px;
            font-size: 12px;
            padding-left: 12px;
            color: #63656e;
            cursor: pointer;
            &:hover {
                background: rgba(225,236,255,0.60);
                color: #3a84ff;
            }
            &.disabled {
                color: #cccccc;
                cursor: not-allowed;
                background: #fff;
            }
        }
    }
</style>
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
    &:not(:last-child) {
        border-bottom: 1px solid #ebebeb;
    }
    &:hover {
        .col-operation .delete-icon {
            display: inline-block;
        }
    }
    .variable-content {
        position: relative;
        padding-left: 55px;
        display: flex;
        height: 42px;
        line-height: 42px;
        cursor: pointer;
        &:hover {
            background: $blueStatus;
            .col-item-drag {
                display: inline-block;
            }
            .copy-icon {
                display: inline-block;
            }
        }
        &.view-model {
            .col-item-drag {
                display: none;
            }
        }
    }
    .col-name {
        width: 170px;
        padding-right: 10px;
    }
    .col-key {
        position: relative;
        padding-right: 30px;
        width: 150px;
        .copy-icon {
            display: none;
            position: absolute;
            right: 10px;
            top: 14px;
            font-size: 14px;
            color: #3a84ff;
        }
    }
    .col-type {
        width: 80px;
        overflow: hidden;
        text-overflow:ellipsis;
        white-space: nowrap;
        padding-right: 15px;
        &.active {
            color: #3a84ff;
        }
    }
    .col-attributes {
        width: 50px;
        padding-left: 10px;
        .common-icon-show-left {
            color: #63656e;
            font-size: 14px;
        }
        .common-icon-hide-right {
            font-size: 14px;
            color: #339dff;
        }
    }
    .col-show {
        width: 100px;
    }
    .col-output {
        width: 50px;
    }
    .col-cited {
        width: 50px;
        color: #333333;
        cursor: pointer;
        &.active {
            color: #3a84ff;
        }
    }
}
.variable-animation {
    animation: bgAnimation 3.5s;
}
@keyframes bgAnimation {
    0%{ background: #f2fcf5; }
    85%{ background: #f2fcf5; }
    100%{ background: #fff; }
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
    margin-top: 2px;
    top: 50%;
    left: 5px;
    transform: translate(0, -50%);
    color: #979ba5;
    cursor: move;
    &:hover {
        color: #348aff;
    }
}
.col-item-checkbox {
    display: inline-block;
    position: absolute;
    left: 28px;
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
    width: 40px;
    display: flex;
    align-items: center;
    .col-operation-item {
        color: #3a84ff;
        cursor: pointer;
        &:not(:first-child) {
            margin-left: 8px;
        }
    }
    .delete-icon {
        display: none;
        margin-left: 4px;
        font-size: 20px;
        color: #979ba5;
        &:hover {
            color: #3a84ff;
        }
    }
}
.col-more {
    width: 40px;
    font-size: 18px;
    line-height: 42px;
    cursor: pointer;
    color: #666;
    &:hover {
        color: #3a84ff;
    }
}
.variable-icon {
    position: absolute;
    top: 50%;
    left: 28px;
    font-size: 16px;
    transform: translate(0, -50%);
    color: #979ba5;
}
</style>
