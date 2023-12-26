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
        :class="[
            'task-node',
            'subflow-node',
            node.status ? node.status.toLowerCase() : '',
            { 'fail-skip': node.status === 'FINISHED' && node.skip },
            { 'ready': node.ready },
            { 'actived': node.isActived }
        ]">
        <div class="node-status-block">
            <i class="node-icon-font common-icon-sub-process"></i>
            <div v-if="node.stage_name" class="stage-name">{{ node.stage_name }}</div>
        </div>
        <div class="node-name">
            <div class="name-text" v-bk-overflow-tips>{{ node.name }}</div>
        </div>
        <div class="node-options-icon">
            <template v-if="node.optional">
                <span v-if="node.mode === 'edit'" class="dark-circle common-icon-dark-circle-checkbox"></span>
                <bk-checkbox
                    v-else-if="node.mode === 'select'"
                    :value="node.checked"
                    :disabled="node.checkDisable"
                    @change="onNodeCheckClick">
                </bk-checkbox>
            </template>
            <!-- 节点循环次数 -->
            <div v-if="node.loop > 1" :class="['task-status-icon task-node-loop', { 'loop-plural': node.loop > 9 }]">
                <i :class="`common-icon-loading-${ node.loop > 9 ? 'oval' : 'round' }`"></i>
                <span>{{ node.loop > 99 ? '99+' : node.loop }}</span>
            </div>
            <!-- 任务节点自动重试/手动重试 -->
            <template v-if="node.mode === 'execute'">
                <span v-if="node.retry - node.auto_skip > 0" class="error-handle-icon">
                    <span class="text">MR</span>
                    <span class="count">{{ node.retry - node.auto_skip }}</span>
                </span>
                <span v-if="node.auto_skip" class="error-handle-icon">
                    <span class="text">AR</span>
                    <span class="count">{{ node.auto_skip }}</span>
                </span>
            </template>
            <template v-else>
                <span v-if="node.error_ignorable" class="error-handle-icon"><span class="text">AS</span></span>
                <span v-if="node.isSkipped || node.skippable" class="error-handle-icon"><span class="text">MS</span></span>
                <span v-if="node.can_retry || node.retryable" class="error-handle-icon"><span class="text">MR</span></span>
                <span v-if="node.auto_retry && node.auto_retry.enable" class="error-handle-icon"><span class="text">AR</span></span>
            </template>
        </div>
        <div v-if="node.hasUpdated" class="updated-dot">
            <div class="ripple"></div>
        </div>
        <!-- 节点右上角执行相关的icon区域 -->
        <node-right-icon-status :node="node"></node-right-icon-status>
        <!-- tooltip提示（任务终止时禁止节点操作） -->
        <div class="state-icon" :class="{ 'subprocess-operate': isSubProcessNode && node.status === 'FAILED' }">
            <template v-if="node.task_state !== 'REVOKED'">
                <template v-if="node.status === 'FAILED' && node.type === 'tasknode'">
                    <span v-if="isShowRetryBtn" @click.stop="$emit('onRetryClick', node.id)">
                        <i class="common-icon-retry"></i>
                        {{ $t('重试子流程') }}
                    </span>
                    <span v-if="isShowSkipBtn" @click.stop="$emit('onSkipClick', node.id)">
                        <i class="common-icon-skip"></i>
                        {{ $t('跳过子流程') }}
                    </span>
                </template>
                <span v-if="isShowPauseBtn" @click.stop="onSubflowPauseResumeClick('pause')">
                    <i class="common-icon-dark-circle-pause"></i>
                    {{ $t('暂停执行') }}
                </span>
                <span v-if="isShowContinueBtn" @click.stop="onSubflowPauseResumeClick('resume')">
                    <i class="bk-icon icon-play-circle-shape"></i>
                    {{ $t('继续执行') }}
                </span>
                <span v-if="isShowForceFailBtn" @click.stop="$emit('onForceFail', node.id)">
                    <i class="common-icon-dark-force-fail"></i>
                    {{ $t('强制终止') }}
                </span>
            </template>
        </div>
    </div>
</template>
<script>
    import NodeRightIconStatus from './NodeRightIconStatus.vue'
    export default {
        name: 'Subflow',
        components: {
            NodeRightIconStatus
        },
        props: {
            hasAdminPerm: {
                type: Boolean,
                default: false
            },
            node: {
                type: Object,
                default () {
                    return {}
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
                if (this.node.status === 'FAILED' && (this.node.skippable || this.node.errorIgnorable)) {
                    return true
                }
                return false
            },
            isShowRetryBtn () {
                if (this.node.status === 'FAILED' && (this.node.retryable || this.node.errorIgnorable)) {
                    return true
                }
                return false
            },
            isSubProcessNode () {
                return this.node.code === 'subprocess_plugin'
            },
            isShowPauseBtn () {
                const { status } = this.node
                return status === 'RUNNING'
            },
            isShowForceFailBtn () {
                const { status } = this.node
                return this.isSubProcessNode && ['RUNNING', 'PENDING_PROCESSING', 'PENDING_APPROVAL', 'PENDING_CONFIRMATION'].includes(status)
            },
            isShowContinueBtn () {
                const { status, subprocessState } = this.node
                return status === 'SUSPENDED' || subprocessState === 'SUSPENDED'
            }
        },
        methods: {
            onSubflowPauseResumeClick (value) {
                this.$emit('onSubflowPauseResumeClick', this.node.id, value)
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
    .task-node {
        &::before {
            content: '';
            position: absolute;
            bottom: -6px;
            right: -6px;
            width: 100%;
            height: 100%;
            background: #b5c0d599;
            border: 1px solid #B5C0D5;
            border-radius: 4px;
            z-index: -1;
        }
    }
    .updated-dot {
        position: absolute;
        top: -4px;
        right: -4px;
        width: 8px;
        height: 8px;
        background: #ff5757;
        border-radius: 50%;
        z-index: 1;
        &.show-animation .ripple {
            position: absolute;
            top: 50%;
            left: 50%;
            height: 100%;
            width: 100%;
            background: transparent;
            border: 1px solid #ff5757;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: ripple .8s ease-out 5;
        }
    }
    @keyframes ripple {
        100% {
            width: 200%;
            height: 200%;
        }
    }
    .subprocess-operate {
        right: -18px !important;
    }
</style>
