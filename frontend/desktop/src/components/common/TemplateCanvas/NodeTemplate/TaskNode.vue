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
                'process-node',
                node.status ? node.status.toLowerCase() : '',
                { 'actived': node.isActived }
            ]">
            <div class="node-status-block">
                <img v-if="node.icon" class="node-icon" :src="node.icon" />
                <i v-else :class="['node-icon-font', getIconCls(node)]"></i>
            </div>
            <div class="node-name">
                {{ node.name }}
            </div>
            <div class="node-options-icon">
                <template v-if="node.optional">
                    <span v-if="node.mode === 'edit'" class="optional-icon"></span>
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
                <bk-button
                    v-if="hasAdminPerm"
                    @click.stop="$emit('onForceFail', node.id)">
                    {{ i18n.forceFail }}
                </bk-button>
            </template>
        </div>
    </el-tooltip>

</template>
<script>
    import '@/utils/i18n.js'
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
                i18n: {
                    retry: gettext('重试'),
                    skip: gettext('跳过'),
                    resume: gettext('继续'),
                    modifyTime: gettext('修改时间'),
                    forceFail: gettext('强制失败'),
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
<style lang="scss" scoped>
    .task-node {
        position: relative;
        width: 150px;
        height: 42px;
        text-align: center;
        background: #ffffff;
        border-radius: 4px;
        box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
        cursor: pointer;
        &.actived {
            box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.3);
        }
        .node-name {
            margin-left: 32px;
            width: 118px;
            height: 100%;
            font-size: 12px;
            word-break: break-all;
        }
    }
    .node-status-block {
        float: left;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 100%;
        background: #52699d;
        border-top-left-radius: 4px;
        border-bottom-left-radius: 4px;
        .node-icon {
            width: 16px;
        }
        .node-icon-font {
            font-size: 18px;
            color: #ffffff;
        }
    }
    .node-options-icon {
        position: absolute;
        top: -25px;
        left: 0;
        .bk-form-checkbox,
        &>[class*="common-icon"] {
            display: inline-block;
            vertical-align: bottom;
        }
    }
    .optional-icon {
        display: inline-block;
        position: relative;
        width: 12px;
        height: 12px;
        line-height: 12px;
        font-size: 13px;
        color: #ffffff;
        text-align: center;
        border-radius: 100%;
        background: #979ba5;
        vertical-align: bottom;
        &::after {
            content: "";
            position: absolute;
            left: 3px;
            top: 4px;
            height: 2px;
            width: 5px;
            border-left: 1px solid;
            border-bottom: 1px solid;
            border-color: #ffffff;
            transform: rotate(-45deg);
        }
    }
    .dark-circle {
        font-size: 12px;
        color: #979ba5;
    }
</style>
