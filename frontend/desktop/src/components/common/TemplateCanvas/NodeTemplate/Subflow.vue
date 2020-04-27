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
    <el-tooltip
        placement="bottom"
        popper-class="task-node-tooltip"
        :disabled="!isOpenTooltip">
        <div
            :class="[
                'task-node',
                'subflow-node',
                node.status ? node.status.toLowerCase() : '',
                { 'actived': node.isActived }
            ]">
            <div class="node-status-block">
                <i class="node-icon-font common-icon-subflow-mark"></i>
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
            <div v-if="node.status === 'SUSPENDED' || node.status === 'RUNNING'" class="task-status-icon subflow-status">
                <i v-if="node.status === 'SUSPENDED'" class="common-icon-double-vertical-line"></i>
                <i v-if="node.status === 'RUNNING'" class="common-icon-loading"></i>
            </div>
        </div>
        <div class="node-tooltip-content" slot="content">
            <template v-if="node.status === 'RUNNING'">
                <bk-button @click="onSubflowPauseResumeClick('pause')">{{ i18n.pause }}</bk-button>
                <bk-button v-if="hasAdminPerm" @click="$emit('onForceFail', node.id)">{{ i18n.forceFail }}</bk-button>
            </template>
            <bk-button v-if="node.status === 'SUSPENDED'" @click="onSubflowPauseResumeClick('resume')">{{ i18n.resume }}</bk-button>
        </div>
    </el-tooltip>
</template>
<script>
    import '@/utils/i18n.js'

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
        data () {
            return {
                i18n: {
                    pause: gettext('暂停'),
                    resume: gettext('继续'),
                    forceFail: gettext('强制失败')
                }
            }
        },
        computed: {
            isOpenTooltip () {
                return ['RUNNING', 'SUSPENDED'].indexOf(this.node.status) > -1
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
                bottom: 0;
                right: 0;
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
