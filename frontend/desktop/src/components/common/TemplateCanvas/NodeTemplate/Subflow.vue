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
                { 'actived': node.isActived }
            ]">
            <!-- 子节点背景图 -->
            <div class="sub-body">
                <div class="t-left">
                    <div class="triangle"></div>
                </div>
                <div class="blue-bar"></div>
                <div class="t-center"></div>
                <div class="t-right">
                    <div class="triangle"></div>
                </div>
            </div>
            <div class="ui-node-shadow"></div>
            <!-- 子流程图标 -->
            <i class="node-icon common-icon-subflow-mark"></i>
            <div class="node-name" :title="node.name">
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
            </div>
            <div v-if="node.hasUpdated" class="updated-dot"></div>
            <div v-if="node.status === 'SUSPENDED' || node.status === 'RUNNING'" class="task-status-icon subflow-status">
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
    .subflow-node {
        position: relative;
        width: 168px;
        height: 42px;
        cursor: pointer;
        z-index: 1;
        &.failed {
           .sub-body .t-left .triangle {
               background: #ff5757;
           }
           .sub-body .t-center {
               border-left-color: #ff5757;
           }
        }
        .sub-body {
            position: absolute;
            width: 168px;
            height: 42px;
            z-index: 1;
            .t-left,.t-center,.t-right {
                position: relative;
                height: 100%;
                overflow: hidden;
            }
            .t-left {
                float: left;
                width: 38px;
                .triangle {
                    left: 10px;
                    background: #52699d;
                }
            }
            .blue-bar {
                position: absolute;
                left: 37px;
                top: 0;
                width: 6px;
                height: 100%;
                background: #52699d;
            }
            .t-center {
                position: absolute;
                left: 43px;
                top: 0;
                width: 95px;
                height: 100%;
                background: #fafbfd;
                // border-left: 6px solid #52699d;
            }
            .t-right {
                float: right;
                width: 38px;
                .triangle {
                    right: 10px;
                }
            }
            .triangle {
                position: absolute;
                top: 0;
                width: 42px;
                height: 42px;
                background: #fafbfd;
                border-radius: 4px;
                transform: rotate(45deg);
                z-index: -1;
                border-radius: 18px 4px 18px 4px;
            }
        }
        .ui-node-shadow {
            position: absolute;
            left: 50%;
            top: 50%;
            width: 128px;
            height: 40px;
            transform: translate(-50%,-50%);
            z-index: -1;
            box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, .15);
        }
    }
    .node-icon {
        position: absolute;
        left: 16px;
        top: 50%;
        transform: translate(0, -50%);
        color: #ffffff;
        font-size: 18px;
        z-index: 1;
    }
    .node-name {
        position: absolute;
        left: 50px;
        top: 0;
        width: 100px;
        height: 42;
        line-height: 42px;
        font-size: 12px;
        text-align: center;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        z-index: 1;
    }
    .node-options-icon {
        position: absolute;
        top: -24px;
        left: 23px;
        z-index: 1;
        height: 16px;
        .bk-form-checkbox, .optional-icon {
            vertical-align: bottom;
        }
    }
    .optional-icon {
        display: inline-block;
        position: relative;
        width: 11px;
        height: 11px;
        line-height: 11px;
        font-size: 12px;
        color: #ffffff;
        text-align: center;
        border-radius: 100%;
        background: #979ba5;
        &::after {
            content: "";
            position: absolute;
            left: 3px;
            top: 3px;
            height: 2px;
            width: 5px;
            border-left: 1px solid;
            border-bottom: 1px solid;
            border-color: #ffffff;
            -webkit-transform: rotate(-45deg);
            transform: rotate(-45deg);
        }
    }
    .updated-dot {
        position: absolute;
        top: -6px;
        right: 15px;
        width: 10px;
        height: 10px;
        background: #ff5757;
        border-radius: 50%;
        z-index: 1;
    }
</style>
