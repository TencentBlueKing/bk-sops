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
    <div
        :class="[
            node.mode === 'execute' ? 'default' : '',
            'task-node',
            'process-node',
            node.status ? node.status.toLowerCase() : '',
            { 'actived': node.isActived }
        ]">
        <!-- 节点左侧的色块区域 -->
        <div class="node-status-block">
            <img v-if="node.icon" class="node-icon" :src="node.icon" />
            <i v-else :class="['node-icon-font', getIconCls(node)]"></i>
            <div v-if="node.stage_name" class="stage-name">{{ node.stage_name }}</div>
        </div>
        <!-- 节点名称 -->
        <div class="node-name">
            <div class="name-text">{{ node.name }}</div>
        </div>
        <!-- 节点顶部左侧区域 icon，是否可选、跳过等 -->
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
            <span v-if="node.error_ignorable && node.mode === 'edit'" class="dark-circle common-icon-dark-circle-i"></span>
            <span v-if="node.isSkipped || node.skippable" class="dark-circle common-icon-dark-circle-s"></span>
            <span v-if="node.can_retry || node.retryable" class="dark-circle common-icon-dark-circle-r"></span>
        </div>
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
        <!-- tooltip提示 -->
        <div class="state-icon" v-if="node.mode === 'execute'">
            <el-tooltip v-if="isShowRetryBtn" placement="bottom" :content="$t('重试')">
                <span
                    class="common-icon-retry"
                    @click.stop="onRetryClick">
                </span>
            </el-tooltip>
            <el-tooltip v-if="isShowSkipBtn" placement="bottom" :content="$t('跳过')">
                <span
                    class="common-icon-skip"
                    @click.stop="onSkipClick">
                </span>
            </el-tooltip>
            <el-tooltip
                v-if="node.status === 'FAILED' && !isShowSkipBtn && !isShowRetryBtn"
                placement="bottom"
                :content="$t('流程模板中该标准插件节点未配置失败处理方式，不可操作')">
                <span
                    class="common-icon-mandatory-failure">
                </span>
            </el-tooltip>
            <template v-if="node.status === 'RUNNING'">
                <el-tooltip v-if="node.code === 'sleep_timer'" placement="bottom" :content="$t('修改时间')">
                    <span
                        class="common-icon-clock"
                        @click.stop="onModifyTimeClick">
                    </span>
                </el-tooltip>
                <el-tooltip v-if="node.code === 'pause_node'" placement="bottom" :content="$t('继续执行')">
                    <span
                        class="common-icon-play"
                        @click.stop="onResumeClick">
                    </span>
                </el-tooltip>
                <el-tooltip placement="bottom" :content="$t('强制失败')">
                    <span
                        class="common-icon-mandatory-failure"
                        @click.stop="mandatoryFailure">
                    </span>
                </el-tooltip>
            </template>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { SYSTEM_GROUP_ICON, BK_PLUGIN_ICON } from '@/constants/index.js'

    export default {
        name: 'TaskNode',
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
        data () {
            return {
                phaseStr: {
                    '1': i18n.t('当前插件即将停止维护，请更新插件版本'),
                    '2': i18n.t('当前插件已停止维护，请更新插件版本')
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
            }
        },
        methods: {
            getIconCls (node) {
                const { code, group } = node
                if (BK_PLUGIN_ICON[code]) {
                    return BK_PLUGIN_ICON[code]
                }

                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(group))
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
            },
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
            },
            mandatoryFailure () {
                this.$emit('onForceFail', this.node.id)
            }
        }
    }
</script>
<style lang="scss">
.task-node-tooltip {
    padding: 0;
    .popper__arrow {
        color: #000000;
    }
}
</style>
