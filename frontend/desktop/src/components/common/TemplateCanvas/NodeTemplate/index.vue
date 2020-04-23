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
    <div
        class="canvas-node-item"
        @mousedown="onMousedown"
        @click="onNodeClick"
        @dblclick="onNodeDblclick">
        <div class="canvas-node-content">
            <component
                :is="nodeTemplate"
                :node="node"
                :has-admin-perm="hasAdminPerm"
                @onNodeCheckClick="onNodeCheckClick"
                @onRetryClick="onRetryClick"
                @onSkipClick="onSkipClick"
                @onModifyTimeClick="onModifyTimeClick"
                @onGatewaySelectionClick="onGatewaySelectionClick"
                @onTaskNodeResumeClick="onTaskNodeResumeClick"
                @onForceFail="onForceFail"
                @onSubflowPauseResumeClick="onSubflowPauseResumeClick" />
            <i
                v-if="editable"
                class="common-icon-dark-circle-close close-icon"
                @click.stop="onNodeRemove">
            </i>
        </div>
        <ShortcutPanel
            :node="node"
            :id-of-node-shortcut-panel="idOfNodeShortcutPanel"
            :canvas-data="canvasData"
            @onAppendNode="onAppendNode"
            @onInsertNode="onInsertNode"
            @onConfigBtnClick="onConfigBtnClick">
        </ShortcutPanel>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import StartPoint from './StartPoint.vue'
    import EndPoint from './EndPoint.vue'
    import TaskNode from './TaskNode.vue'
    import Subflow from './Subflow.vue'
    import BranchGateway from './BranchGateway.vue'
    import ParallelGateway from './ParallelGateway.vue'
    import ConvergeGateway from './ConvergeGateway.vue'
    import ShortcutPanel from './ShortcutPanel.vue'
    export default {
        name: 'NodeTemplate',
        components: {
            ShortcutPanel
        },
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            },
            editable: {
                type: Boolean,
                default: true
            },
            idOfNodeShortcutPanel: {
                type: String,
                default: ''
            },
            hasAdminPerm: {
                type: Boolean,
                default: false
            },
            canvasData: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                moveFlag: {
                    x: 0,
                    y: 0
                },
                components: {
                    startpoint: StartPoint,
                    endpoint: EndPoint,
                    tasknode: TaskNode,
                    subflow: Subflow,
                    branchgateway: BranchGateway,
                    parallelgateway: ParallelGateway,
                    convergegateway: ConvergeGateway
                },
                clickTimer: null
            }
        },
        computed: {
            nodeTemplate () {
                return this.components[this.node.type.toLowerCase()]
            }
        },
        methods: {
            onMousedown (e) {
                const { pageX: x, pageY: y } = e
                this.moveFlag = { x, y }
                this.$emit('onNodeMousedown', this.node.id)
            },
            onNodeDblclick () {
                clearTimeout(this.clickTimer)
                this.$emit('onNodeDblclick', this.node.id)
            },
            onNodeClick (e) {
                if ((e.ctrlKey || e.metaKey) && this.editable) {
                    this.$emit('addNodesToDragSelection', this.node)
                    return
                }
                clearTimeout(this.clickTimer)
                this.clickTimer = setTimeout(() => {
                    const moveBuffer = 2
                    const { pageX: x, pageY: y } = e
                    if (
                        Math.abs(x - this.moveFlag.x) < moveBuffer
                        && Math.abs(y - this.moveFlag.y) < moveBuffer
                    ) {
                        this.$emit('onNodeClick', this.node.id, this.node.type, e)
                    }
                }, 200)
            },
            onNodeCheckClick (id, val) {
                this.$emit('onNodeCheckClick', id, val)
            },
            onNodeRemove () {
                this.$emit('onNodeRemove', this.node)
            },
            onRetryClick (id) {
                this.$emit('onRetryClick', id)
            },
            onForceFail (id) {
                this.$emit('onForceFail', id)
            },
            onSkipClick (id) {
                this.$emit('onSkipClick', id)
            },
            onModifyTimeClick (id) {
                this.$emit('onModifyTimeClick', id)
            },
            onGatewaySelectionClick (id) {
                this.$emit('onGatewaySelectionClick', id)
            },
            onTaskNodeResumeClick (id) {
                this.$emit('onTaskNodeResumeClick', id)
            },
            onSubflowPauseResumeClick (id, value) {
                this.$emit('onSubflowPauseResumeClick', id, value)
            },
            onAppendNode (data) {
                this.$emit('onAppendNode', data)
            },
            onConfigBtnClick (id) {
                this.$emit('onConfigBtnClick', id)
            },
            onInsertNode (data) {
                this.$emit('onInsertNode', data)
            }
        }
    }
</script>
<style lang="scss">
    @import '@/scss/mixins/multiLineEllipsis.scss';

    $blueDark: #52699D;
    $redDark: #ea3636;
    $yellowDark: #ff9C01;
    $greenDark: #2dcb56;
    $whiteColor: #ffffff;
    $defaultShadow: rgba(0, 0, 0, 0.15);
    $activeShadow: rgba(0, 0, 0, 0.3);
    $redShadow: rgba(255, 87, 87, 0.15);
    $yellowShadow: rgba(248, 181, 63, 0.15);
    $greenShadow: rgba(48, 216, 120, 0.15);
    $blueShadow: rgba(58, 132, 255, 0.15);

    @mixin circleStatusStyle ($color, $shadow) {
        background-color: $color;
        &:hover {
            box-shadow: -1px 1px 8px $shadow, 1px -1px 8px $shadow;
        }
        .circle-node-text {
            color: $whiteColor;
        }
    }

    @mixin taskNodeStyle ($color) {
        .node-status-block {
            background-color: $color;
        }
        .task-status-icon {
            background: $color;
        }
    }
    @mixin gatewayStyle ($color) {
        .node-type-icon {
            color: $color;
        }
    }
    @keyframes shake {
        25% {
            transform: rotate(-2deg);
        }
        50% {
            transform: rotate(0);
        }
        75% {
            transform: rotate(2deg);
        }
        100% {
            transform: rotate(0);
        }
    }
    .jsflow-node.selected {
        outline: 1px dashed #348af3;
    }
    .jsflow-node:not(.adding-node) {
        & .canvas-node-item .canvas-node-content:hover {
            .close-icon {
                display: inline-block;
            }
        }
    }
    .canvas-node-item {
        position: relative;
        user-select: none;
        z-index: 3;
        &>.subflow-node + .close-icon{
            right: 14px;
        }
        &.node-shake {
            animation: shake .2s ease-in-out 2;
        }
        .close-icon {
            display: none;
            position: absolute;
            top: -8px;
            right: -8px;
            font-size: 16px;
            color: #63656e;
            background: #ffffff;
            border-radius: 50%;
            z-index: 2;
            cursor: pointer;
        }
        .circle-node {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            background: #96a1b9;
            border-radius: 50%;
            &.finished {
                @include circleStatusStyle($greenDark, $greenShadow)
            }
            &.running {
                @include circleStatusStyle($yellowDark, $yellowShadow)
            }
            &.failed {
                @include circleStatusStyle($redDark, $redShadow)
            }
        }
        .circle-node-text {
            font-size: 12px;
            color: #ffffff;
        }
        .gateway-node {
            position: relative;
            height: 34px;
            width: 34px;
            text-align: center;
            &.failed {
                @include gatewayStyle($redDark);
            }
            &.finished {
                @include gatewayStyle($greenDark);
            }
            &:before {
                content: '';
                position: absolute;
                top: 2px;
                left: 3px;
                width: 28px;
                height: 28px;
                background: #ffffff;
                border-radius: 3px;
                transform: rotate(45deg);
                z-index: -1;
            }
        }
        .node-type-icon {
            height: 32px;
            line-height: 32px;
            font-size: 24px;
            color: $blueDark;
            text-align: center;
        }
        .task-node {
            position: relative;
            width: 150px;
            height: 54px;
            text-align: center;
            background: #ffffff;
            border-radius: 4px;
            box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            &.actived {
                box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.3);
            }
            &:hover {
                box-shadow: 0px 0px 20px 0px $activeShadow;
            }
            &.failed {
                @include taskNodeStyle ($redDark)
            }
            &.suspended {
                @include taskNodeStyle ($yellowDark)
            }
            &.running {
                @include taskNodeStyle ($yellowDark)
            }
            &.finished {
                @include taskNodeStyle ($greenDark)
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
            .node-name {
                display: flex;
                align-items: center;
                margin-left: 32px;
                padding: 0 10px;
                width: 118px;
                height: 100%;
                .name-text {
                    display: -webkit-box;
                    width: 100%;
                    font-size: 12px;
                    color: #63656e;
                    text-align: center;
                    overflow : hidden;
                    text-overflow: ellipsis;
                    word-break: break-all;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                }
            }
            .node-options-icon {
                display: flex;
                align-items: flex-end;
                position: absolute;
                top: -20px;
                left: 0;
                height: 18px;
                overflow: hidden;
                .bk-form-checkbox,
                .dark-circle {
                    float: left;
                    margin-right: 2px;
                    font-size: 12px;
                    color: #979ba5;
                }
            }
        }
        .task-status-icon {
            position: absolute;
            top: -10px;
            right: -8px;
            width: 18px;
            height: 18px;
            line-height: 16px;
            font-size: 14px;
            border-radius: 50%;
            background: #f8b53f;
            color: #ffffff;
            text-align: center;
            .common-icon-double-vertical-line {
                display: inline-block;
                font-size: 12px;
                transform: scale(0.8);
            }
            .common-icon-clock {
                display: inline-block;
            }
            .common-icon-loading {
                display: inline-block;
                animation: loading 1.4s infinite linear;
            }
            @keyframes loading {
                from {
                    transform: rotate(0);
                }
                to {
                    transform: rotate(360deg);
                }
            }
            &.subflow-status {
                right: 12px;
                top: -14px;
                z-index: 1;
            }
        }
    }
    .task-node-tooltip.el-tooltip__popper {
        z-index: 4 !important;
    }
    #node-tooltip-content {
        .bk-button {
            padding: 0;
            min-width: auto;
            height: 16px;
            line-height: 16px;
            font-size: 12px;
            background: transparent;
            color: #ffffff;
            border: none;
            &:hover {
                color: #3a84ff;
            }
        }
    }
</style>
