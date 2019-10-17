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
    <el-tooltip placement="bottom" popper-class="task-node-tooltip" :disabled="!isOpenTooltip">
        <div
            :class="[
                'task-node',
                node.status ? node.status.toLowerCase() : '',
                { 'isActived': node.isActived }
            ]">
            <div class="node-name">
                <p>{{ node.name }}</p>
            </div>
            <div class="stage-name">{{node.stage_name}}</div>
            <div class="node-options-icon">
                <template v-if="node.optional">
                    <div v-if="node.mode === 'edit'" class="optional-icon"></div>
                    <bk-checkbox
                        v-else-if="node.mode === 'select'"
                        :value="node.checked"
                        :disabled="node.checkDisable"
                        @change="onNodeCheckClick">
                    </bk-checkbox>
                </template>
                <div v-if="node.error_ignorable && node.mode === 'edit'" class="dark-circle common-icon-dark-circle-i"></div>
                <div v-if="node.isSkipped" class="dark-circle common-icon-dark-circle-s"></div>
                <div v-if="node.can_retry" class="dark-circle common-icon-dark-circle-r"></div>
            </div>
            <div v-if="node.status === 'SUSPENDED' || node.status === 'RUNNING'" class="task-status-icon">
                <i v-if="node.status === 'RUNNING' && node.code === 'sleep_timer'" class="common-icon-clock"></i>
                <template v-else>
                    <i v-if="node.status === 'SUSPENDED' || node.code === 'pause_node'" class="common-icon-double-vertical-line"></i>
                    <i v-else-if="node.status === 'RUNNING'" class="common-icon-loading"></i>
                </template>
            </div>
        </div>
        <div id="node-tooltip-content" slot="content">
            <bk-button
                v-if="isShowSkipBtn"
                @click.stop="onRetryClick">
                {{ i18n.retry }}
            </bk-button>
            <bk-button
                v-if="isShowRetryBtn"
                @click.stop="onSkipClick">
                {{ i18n.skip }}
            </bk-button>
            <span v-if="node.status === 'FAILED' && !isShowSkipBtn && !isShowRetryBtn">{{ i18n.atomFailed }}</span>
            <template v-if="node.status === 'RUNNING'">
                <bk-button
                    v-if="node.code === 'sleep_timer'"
                    @click.stop="onModifyTimeClick">
                    {{ i18n.modifyTime }}
                </bk-button>
                <bk-button
                    v-if="node.code === 'pause_node'"
                    @click.stop="onResumeClick">
                    {{ i18n.resume }}
                </bk-button>
            </template>
        </div>
    </el-tooltip>

</template>
<script>
    import '@/utils/i18n.js'

    export default {
        name: 'TaskNode',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                i18n: {
                    retry: gettext('重试'),
                    skip: gettext('跳过'),
                    resume: gettext('继续'),
                    modifyTime: gettext('修改时间'),
                    atomFailed: gettext('流程模板中该标准插件节点未配置失败处理方式，不可操作')
                }
            }
        },
        computed: {
            isOpenTooltip () {
                if (this.node.mode === 'execute') {
                    if (this.node.status === 'RUNNING') {
                        return ['sleep_timer', 'pause_node'].indexOf(this.node.code) > -1
                    }
                    return this.node.status === 'FAILED'
                }
                return false
            },
            isShowSkipBtn () {
                if (this.node.status === 'FAILED') {
                    if ((this.node.canSkipped === undefined && this.node.canRetry === undefined)
                        || this.node.canSkipped
                    ) {
                        return true
                    }
                }
                return false
            },
            isShowRetryBtn () {
                if (this.node.status === 'FAILED') {
                    if ((this.node.canSkipped === undefined && this.node.canRetry === undefined)
                        || this.node.canRetry
                    ) {
                        return true
                    }
                }
                return false
            }
        },
        methods: {
            onRetryClick () {
                this.$emit('onRetryClick', this.node.id)
            },
            onSkipClick () {
                this.$emit('onSkipClick', this.node.id)
            },
            onResumeClick () {
                this.$emit('onTaskNodeResumeClick', this.node.id)
            },
            onModifyTimeClick () {
                this.$emit('onModifyTimeClick', this.node.id)
            },
            onNodeCheckClick () {
                if (this.node.checkDisable) {
                    return
                }
                this.$emit('onNodeCheckClick', this.node.id, !this.node.checked)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .node-options-icon {
        display: inline-block;
        position: absolute;
        top: -10px;
        left: -20px;
        width: 14px;
    }
    .optional-icon {
        position: relative;
        width: 14px;
        height: 14px;
        line-height: 14px;
        font-size: 12px;
        color: #ffffff;
        text-align: center;
        border-radius: 100%;
        background: #348aff;
        &::after {
            content: "";
            position: absolute;
            left: 2px;
            top: 3px;
            height: 4px;
            width: 8px;
            border-left: 1px solid;
            border-bottom: 1px solid;
            border-color: #ffffff;
            transform: rotate(-45deg);
        }
    }
    .dark-circle {
        margin-top: 2px;
        font-size: 14px;
        color: #348af3;
    }
</style>
