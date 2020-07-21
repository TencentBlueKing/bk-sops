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
    <div class="variable-item">
        <div class="variable-content" @click="onEditVariable(variableData.key, variableData.index)">
            <i v-if="!isSystemVar && !showCitedList" class="col-item-drag bk-icon icon-sort"></i>
            <i v-if="isSystemVar" class="common-icon-lock-disable"></i>
            <span :title="variableData.name" class="col-item col-name">
                {{ variableData.name }}
            </span>
            <span class="col-item col-key">
                {{ variableData.key }}
            </span>
            <span class="col-item col-attributes">
                <span class="icon-wrap">
                    <i
                        v-if="variableData.source_type !== 'component_outputs'"
                        class="common-icon-show-left"
                        v-bk-tooltips="{
                            content: $t('输入'),
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-hide-right color-org"
                        v-bk-tooltips="{
                            content: $t('输出'),
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-if="variableData.show_type === 'show'"
                        class="common-icon-eye-show"
                        v-bk-tooltips="{
                            content: $t('显示'),
                            placements: ['bottom']
                        }">
                    </i>
                    <i
                        v-else
                        class="common-icon-eye-hide color-org"
                        v-bk-tooltips="{
                            content: $t('隐藏'),
                            placements: ['bottom']
                        }">
                    </i>
                </span>
            </span>
            <span class="col-item col-output">
                <div @click.stop>
                    <bk-switcher
                        size="small"
                        theme="primary"
                        :value="outputed"
                        @change="onChangeVariableOutput(variableData.key, $event)">
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
                        content: $t('已复制'),
                        placements: ['bottom']
                    }"
                    @click.stop="onCopyKey(variableData.key)">
                    {{ $t('复制') }}
                </span>
                <span
                    v-if="!isSystemVar"
                    class="col-operation-item"
                    @click.stop="onDeleteVariable(variableData.key)">
                    {{ $t('删除') }}
                </span>
            </span>
        </div>
        <VariableCitedList
            v-if="showCitedList"
            :cited-list="citedList"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)">
        </VariableCitedList>
    </div>
</template>
<script>
    import { mapState } from 'vuex'
    import VariableCitedList from './VariableCitedList.vue'
    export default {
        name: 'VariableItem',
        components: {
            VariableCitedList
        },
        props: {
            outputed: Boolean,
            variableData: Object
        },
        data () {
            return {
                showCitedList: false,
                copyText: ''
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities
            }),
            isSystemVar () {
                return this.variableData.source_type === 'system'
            },
            citedList () {
                const sourceInfo = this.variableData.source_info
                // 该全局变量被哪些节点勾选的集合
                const nodes = Object.keys(sourceInfo).map(id => id)

                // 输入参数表单直接填写变量key的情况
                const escapeStr = this.variableData.key.replace(/[${}]/g, '\\$&')
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
                    this.showCitedList = true
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
    &:not(:last-child) {
        border-bottom: 1px solid #ebebeb;
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
