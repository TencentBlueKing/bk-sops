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
                'subflow-node',
                node.status ? node.status.toLowerCase() : '',
                { 'isActived': node.isActived }
            ]">
            <div class="node-name">
                <div class="subflow-node-icon">
                    <i class="common-icon-add"></i>
                </div>
                <p>{{ node.name }}</p>
            </div>
            <div class="stage-name">{{ node.stage_name }}</div>
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
            </div>
            <div v-if="node.hasUpdated" class="updated-dot"></div>
            <div v-if="node.status === 'SUSPENDED' || node.status === 'RUNNING'" class="task-status-icon">
                <i v-if="node.status === 'SUSPENDED'" class="common-icon-double-vertical-line"></i>
                <i v-if="node.status === 'RUNNING'" class="common-icon-loading"></i>
            </div>
        </div>
        <div id="node-tooltip-content" slot="content">
            <bk-button v-if="node.status === 'RUNNING'" @click="onSubflowPauseResumeClick('pause')">{{ i18n.pause }}</bk-button>
            <bk-button v-if="node.status === 'SUSPENDED'" @click="onSubflowPauseResumeClick('resume')">{{ i18n.resume }}</bk-button>
        </div>
    </el-tooltip>
</template>
<script>
    import '@/utils/i18n.js'

    export default {
        name: 'Subflow',
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
                    pause: gettext('暂停'),
                    resume: gettext('继续')
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
    .node-options-icon {
        display: inline-block;
        position: absolute;
        top: -10px;
        left: -20px;
        width: 14px;
        border: 1px solid #ddd;
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
    .updated-dot {
        position: absolute;
        top: -6px;
        right: -7px;
        width: 10px;
        height: 10px;
        background: #ff5757;
        border-radius: 50%;
        z-index: 1;
    }
</style>
