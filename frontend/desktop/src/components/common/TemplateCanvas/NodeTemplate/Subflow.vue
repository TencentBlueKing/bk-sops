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
            { 'actived': node.isActived }
        ]">
        <div class="node-status-block">
            <i class="node-icon-font common-icon-subflow-mark"></i>
            <div v-if="node.stage_name" class="stage-name">{{ node.stage_name }}</div>
        </div>
        <div class="node-name" :title="node.name">
            <div class="name-text">{{ node.name }}</div>
            <div class="subflow-mark"></div>
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
        <div class="node-execute-icon">
            <!-- 节点执行顶部右侧 icon， 执行中、重试次数、是否为跳过-->
            <div v-if="node.status === 'RUNNING'" class="task-status-icon">
                <i class="common-icon-loading"></i>
            </div>
            <div v-else-if="node.status === 'FINISHED' && (node.retry > 0 || node.skip)" class="task-status-icon">
                <i v-if="node.skip" class="bk-icon icon-arrows-right-shape"></i>
                <span v-else-if="node.retry > 0" class="retry-times">{{ node.retry > 99 ? '100+' : node.retry }}</span>
            </div>
            <!-- 节点失败后自动忽略icon -->
            <div v-else-if="node.status === 'FINISHED' && node.error_ignored" class="task-status-icon node-subscript">
                <i class="bk-icon icon-arrows-right-shape"></i>
            </div>
            <!-- 节点循环次数 -->
            <div v-if="node.loop > 1" :class="['task-status-icon task-node-loop', { 'loop-plural': node.loop > 9 }]">
                <i :class="`common-icon-loading-${ node.loop > 9 ? 'oval' : 'round' }`"></i>
                <span>{{ node.loop > 99 ? '99+' : node.loop }}</span>
            </div>
            <!-- 节点顶部右侧生命周期 icon -->
            <div class="node-phase-icon" v-if="[1, 2].includes(node.phase)">
                <i
                    :class="['bk-icon', 'icon-exclamation-circle', {
                        'phase-warn': node.phase === 1,
                        'phase-error': node.phase === 2
                    }]"
                    v-bk-tooltips="{
                        content: phaseStr[node.phase],
                        width: 210
                    }">
                </i>
            </div>
        </div>
        <!-- tooltip提示 -->
        <div class="state-icon">
            <template v-if="node.status === 'FAILED'">
                <el-tooltip v-if="isShowRetryBtn" placement="bottom" :content="$t('重试')">
                    <span
                        class="common-icon-retry"
                        @click.stop="$emit('onRetryClick', node.id)">
                    </span>
                </el-tooltip>
                <el-tooltip v-if="isShowSkipBtn" placement="bottom" :content="$t('跳过')">
                    <span
                        class="common-icon-skip"
                        @click.stop="$emit('onSkipClick', node.id)">
                    </span>
                </el-tooltip>
            </template>
            <el-tooltip placement="bottom" :content="$t('节点参数')">
                <span
                    class="common-icon-bkflow-setting"
                    @click.stop="$emit('onSubflowDetailClick', node.id)">
                </span>
            </el-tooltip>
            <template v-if="node.status === 'RUNNING'">
                <el-tooltip placement="bottom" :content="$t('暂停')">
                    <span
                        class="common-icon-resume"
                        @click.stop="onSubflowPauseResumeClick('pause')">
                    </span>
                </el-tooltip>
                <el-tooltip v-if="hasAdminPerm" placement="bottom" :content="$t('强制失败')">
                    <span
                        class="common-icon-mandatory-failure"
                        @click.stop="$emit('onForceFail', node.id)">
                    </span>
                </el-tooltip>
            </template>
            <el-tooltip v-if="node.status === 'SUSPENDED'" placement="bottom" :content="$t('继续')">
                <span
                    class="common-icon-play"
                    @click.stop="onSubflowPauseResumeClick('resume')">
                </span>
            </el-tooltip>
        </div>
    </div>
</template>
<script>

    export default {
        name: 'Subflow',
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
    .node-name {
        position: relative;
        .subflow-mark {
            &::before {
                content: '';
                position: absolute;
                bottom: -1px;
                right: -1px;
                background: linear-gradient(to left top,
                    #a2a5ad, #9fa3aa 40%, #82848a 50%, #ffffff 60%, #ffffff) 100% 0 no-repeat;
                width: 11px;
                height: 11px;
                border-top: 1px solid #e5e5e5;
                border-left: 1px solid #e5e5e5;
                border-bottom-right-radius: 4px;
                box-shadow: -1px -1px 2px -2px rgba(0, 0, 0, .5);
            }
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
</style>
