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
            node.mode === 'execute' ? 'default' : '',
            'task-node',
            'process-node',
            node.status ? node.status.toLowerCase() : '',
            { 'fail-skip': node.status === 'FINISHED' && (node.skip || node.error_ignored) },
            { 'ready': node.ready },
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
            <div class="name-text" :class="{ 'default-name': isShowDefaultNodeName }">{{ isShowDefaultNodeName ? $t('请选择插件') : node.name }}</div>
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
            <span v-if="node.error_ignorable" class="error-handle-icon"><span class="text">AS</span></span>
            <span v-if="node.isSkipped || node.skippable" class="error-handle-icon"><span class="text">MS</span></span>
            <span v-if="node.can_retry || node.retryable" class="error-handle-icon"><span class="text">MR</span></span>
            <span v-if="node.auto_retry && node.auto_retry.enable" class="error-handle-icon"><span class="text">AR</span></span>
        </div>
        <!-- 节点右上角执行相关的icon区域 -->
        <node-right-icon-status :node="node"></node-right-icon-status>
        <!-- tooltip提示（任务终止时禁止节点操作） -->
        <div class="state-icon" v-if="node.mode === 'execute' && node.task_state !== 'REVOKED'">
            <span v-if="isShowRetryBtn" @click.stop="$emit('onRetryClick', node.id)">
                <i class="common-icon-retry"></i>
                {{ $t('重试') }}
            </span>
            <span v-if="isShowSkipBtn" @click.stop="$emit('onSkipClick', node.id)">
                <i class="common-icon-skip"></i>
                {{ $t('跳过') }}
            </span>
            <template v-if="node.status === 'RUNNING'">
                <span v-if="node.code === 'pause_node'" @click.stop="$emit('onTaskNodeResumeClick', node.id)">
                    <i class="common-icon-play"></i>
                    {{ $t('继续') }}
                </span>
                <span v-else-if="node.code === 'bk_approve'" @click.stop="$emit('onApprovalClick', node.id)">
                    <i class="common-icon-circulation"></i>
                    {{ $t('审批') }}
                </span>
                <span v-else @click.stop="$emit('onForceFail', node.id)">
                    <i class="common-icon-mandatory-failure"></i>
                    {{ $t('强制终止') }}
                </span>
            </template>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { SYSTEM_GROUP_ICON, BK_PLUGIN_ICON } from '@/constants/index.js'
    import NodeRightIconStatus from './NodeRightIconStatus.vue'

    export default {
        name: 'TaskNode',
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
            },
            isShowDefaultNodeName () {
                return this.node.mode === 'edit' && !this.node.name
            }
        },
        methods: {
            getIconCls (node) {
                const { code, group } = node
                if (BK_PLUGIN_ICON[code]) {
                    return BK_PLUGIN_ICON[code]
                }

                if (code === 'remote_plugin') {
                    return 'common-icon-sys-third-party'
                }
                const systemType = SYSTEM_GROUP_ICON.find(item => new RegExp(item).test(group))
                if (systemType) {
                    return `common-icon-sys-${systemType.toLowerCase()}`
                }
                return 'common-icon-sys-default'
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
<style lang="scss">
.task-node-tooltip {
    padding: 0;
    .popper__arrow {
        color: #000000;
    }
}
</style>
