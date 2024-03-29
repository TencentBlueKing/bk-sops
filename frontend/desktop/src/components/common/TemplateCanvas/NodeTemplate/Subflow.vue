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
        <div class="node-name" :title="node.name">
            <div class="name-text">{{ node.name }}</div>
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
        </div>
        <div v-if="node.hasUpdated" class="updated-dot">
            <div class="ripple"></div>
        </div>
        <!-- 节点右上角执行相关的icon区域 -->
        <node-right-icon-status :node="node"></node-right-icon-status>
        <!-- tooltip提示（任务终止时禁止节点操作） -->
        <div class="state-icon" :class="{ 'subprocess-operate': isSubProcessNode }">
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
                <template v-if="!isSubProcessNode && node.status === 'RUNNING'">
                    <span @click.stop="onSubflowPauseResumeClick('pause')">
                        <i class="common-icon-mandatory-failure"></i>
                        {{ $t('暂停') }}
                    </span>
                    <span v-if="hasAdminPerm" @click.stop="$emit('onForceFail', node.id)">
                        <i class="common-icon-resume"></i>
                        {{ $t('强制终止') }}
                    </span>
                </template>
                <span v-if="!isSubProcessNode && node.status === 'SUSPENDED'" @click.stop="onSubflowPauseResumeClick('resume')">
                    <i class="common-icon-play"></i>
                    {{ $t('继续') }}
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
