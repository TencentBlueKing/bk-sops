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
    <div class="variable-item">
        <div class="variable-content" @click="onEditVariable(variableData.key, variableData.index)">
            <i v-if="!isSystemVar && !isProjectVar && !showCitedList" class="col-item-drag bk-icon icon-sort"></i>
            <i v-if="isSystemVar" class="variable-icon common-icon-lock-disable"></i>
            <i v-if="isProjectVar" class="variable-icon common-icon-paper"></i>
            <span :title="variableData.name" class="col-item col-name">
                {{ variableData.name }}
            </span>
            <span class="col-item col-key">
                {{ variableData.key }}
                <i
                    class="common-icon-double-paper-2 copy-icon"
                    v-bk-tooltips.bottom="$t('复制')"
                    @click.stop="onCopyKey(variableData.key)">
                </i>
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
                        'disabled': citedNum === 0
                    }
                ]"
                @click.stop="onViewCitedList">
                {{ citedNum }}
            </span>
            <span class="col-item col-operation">
                <span
                    v-if="isSystemVar || isProjectVar"
                    class="col-operation-item"
                    @click.stop="onEditVariable(variableData.key, variableData.index)">
                    {{ $t('查看') }}
                </span>
                <template v-else>
                    <span
                        class="col-operation-item"
                        @click.stop="onPreviewValue(variableData.key)">
                        {{ $t('预览值') }}
                    </span>
                    <span
                        class="col-operation-item"
                        @click.stop="onCloneVariable()">
                        {{ $t('克隆') }}
                    </span>
                    <i class="bk-icon icon-close delete-icon" @click.stop="onDeleteVariable(variableData.key)"></i>
                </template>
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
            variableCited: Object
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
                'project_id': state => state.project.project_id,
                'bizId': state => state.project.bizId
            }),
            isSystemVar () {
                return this.variableData.source_type === 'system'
            },
            isProjectVar () {
                return this.variableData.source_type === 'project'
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
                    message: i18n.t('已复制'),
                    theme: 'success'
                })
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
            onChangeVariableOutput (key, checked) {
                this.$emit('onChangeVariableOutput', { key, checked })
            },
            // 查看变量预览值
            onPreviewValue () {
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
            onDeleteVariable (key) {
                this.$emit('onDeleteVariable', key)
            },
            onEditVariable (key, index) {
                this.$emit('onEditVariable', key, index)
            },
            onCloneVariable () {
                this.$emit('onCloneVariable', this.variableData)
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
    &:hover {
        .col-operation .delete-icon {
            display: inline-block;
        }
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
        position: relative;
        padding-right: 30px;
        width: 180px;
        .copy-icon {
            display: none;
            position: absolute;
            right: 10px;
            top: 14px;
            font-size: 14px;
            color: #3a84ff;
        }
        &:hover {
            .copy-icon {
                display: inline-block;
            }
        }
    }
    .col-attributes {
        width: 64px;
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
        width: 54px;
    }
    .col-cited {
        width: 50px;
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
.variable-icon {
    position: absolute;
    top: 50%;
    left: 20px;
    transform: translate(0, -50%);
    color: #979ba5;
}
</style>
