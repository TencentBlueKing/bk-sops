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
    <el-tooltip placement="bottom" popper-class="task-node-tooltip" :disabled="!isOpenTooltip">
        <div
            :class="[
                'task-node',
                'process-node',
                node.status ? node.status.toLowerCase() : '',
                { 'actived': node.isActived }
            ]">
            <div class="node-status-block">
                <img v-if="node.icon" class="node-icon" :src="node.icon" />
                <i v-else :class="['node-icon-font', getIconCls(node)]"></i>
            </div>
            <div class="node-name">
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
                <span v-if="node.error_ignorable && node.mode === 'edit'" class="dark-circle common-icon-dark-circle-i"></span>
                <span v-if="node.isSkipped || node.skippable" class="dark-circle common-icon-dark-circle-s"></span>
                <span v-if="node.can_retry || node.retryable" class="dark-circle common-icon-dark-circle-r"></span>
            </div>
            <div v-if="node.status === 'SUSPENDED' || node.status === 'RUNNING'" class="task-status-icon">
                <i v-if="node.status === 'RUNNING' && node.code === 'sleep_timer'" class="common-icon-clock"></i>
                <template v-else>
                    <i v-if="node.status === 'SUSPENDED' || node.code === 'pause_node'" class="common-icon-double-vertical-line"></i>
                    <i v-else-if="node.status === 'RUNNING'" class="common-icon-loading"></i>
                </template>
            </div>
        </div>
        <div class="node-tooltip-content" slot="content">
            <bk-button
                v-if="isShowSkipBtn"
                @click.stop="onRetryClick">
                {{ $t('重试') }}
            </bk-button>
            <bk-button
                v-if="isShowRetryBtn"
                @click.stop="onSkipClick">
                {{ $t('跳过') }}
            </bk-button>
            <span v-if="node.status === 'FAILED' && !isShowSkipBtn && !isShowRetryBtn">{{ $t('流程模板中该标准插件节点未配置失败处理方式，不可操作') }}</span>
            <template v-if="node.status === 'RUNNING'">
                <bk-button
                    v-if="node.code === 'sleep_timer'"
                    @click.stop="onModifyTimeClick">
                    {{ $t('修改时间') }}
                </bk-button>
                <bk-button
                    v-if="node.code === 'pause_node'"
                    @click.stop="onResumeClick">
                    {{ $t('继续') }}
                </bk-button>
                <bk-button
                    v-if="hasAdminPerm"
                    @click.stop="$emit('onForceFail', node.id)">
                    {{ $t('强制失败') }}
                </bk-button>
            </template>
        </div>
    </el-tooltip>

</template>
<script>
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
