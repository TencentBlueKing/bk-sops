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
        @click.stop="onNodeClick">
        <component
            :is="nodeTemplate"
            :node="node"
            @onNodeCheckClick="onNodeCheckClick"
            @onRetryClick="onRetryClick"
            @onSkipClick="onSkipClick"
            @onModifyTimeClick="onModifyTimeClick"
            @onGatewaySelectionClick="onGatewaySelectionClick"
            @onTaskNodeResumeClick="onTaskNodeResumeClick"
            @onSubflowPauseResumeClick="onSubflowPauseResumeClick" />
        <i
            v-if="editable"
            class="common-icon-dark-circle-close close-icon"
            @click.stop="onNodeRemove">
        </i>
        <ShortcutPanel
            :node="node"
            :id-of-node-shortcut-panel="idOfNodeShortcutPanel"
            :canvas-data="canvasData"
            @onAppendNode="onAppendNode"
            @onInsertNode="onInsertNode"
            @onShowNodeConfig="onShowNodeConfig">
        </ShortcutPanel>
    </div>
</template>
<script>
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
                }
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
            },
            onNodeClick (e) {
                const moveBuffer = 2
                const { pageX: x, pageY: y } = e
                if (
                    Math.abs(x - this.moveFlag.x) < moveBuffer
                    && Math.abs(y - this.moveFlag.y) < moveBuffer
                ) {
                    if (
                        [
                            'startpoint',
                            'tasknode',
                            'subflow',
                            'parallelgateway',
                            'branchgateway',
                            'convergegateway'
                        ].indexOf(this.node.type) > -1) {
                        this.$emit('onNodeWrapClick', this.node.id, e)
                        // e.stopPropagation()
                    }
                }
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
            onShowNodeConfig (id) {
                this.$emit('onShowNodeConfig', id)
            },
            onInsertNode (data) {
                this.$emit('onInsertNode', data)
            }
        }
    }
</script>
<style lang="scss">
    $blueDark: #53699d;
    $redDark: #ff5757;
    $yellowDark: #f8b53f;
    $greenDark: #30d878;
    $defaultShadow: rgba(0, 0, 0, 0.15);
    $activeShadow: rgba(0, 0, 0, 0.3);
    $redShadow: rgba(255, 87, 87, 0.15);
    $yellowShadow: rgba(248, 181, 63, 0.15);
    $greenShadow: rgba(48, 216, 120, 0.15);

    @mixin circleStatusStyle ($color, $shadow) {
        border-color: $color;
        color: $color;
        &:hover {
            box-shadow: -1px 1px 8px $shadow, 1px -1px 8px $shadow;
        }
        .circle-node-text {
            background: $color;
        }
        .node-type-icon {
            color: $color;
        }
    }

    @mixin taskNodeStyle ($color) {
        .node-status-block {
            background-color: $color;
        }
       .sub-body {
            .t-left .triangle, .blue-bar{
                background-color: $color;
            }
        }
    }
    .jsflow-node.selected {
        outline: 1px dashed #348af3;
    }
    .canvas-node-item {
        position: relative;
        user-select: none;
        z-index: 3;
        &:hover {
            .close-icon {
                display: inline-block;
            }
        }
        &>.subflow-node + .close-icon{
            right: 14px;
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
            width: 40px;
            height: 40px;
            background: #96a1b9;
            border-radius: 50%;
            &:hover {
                box-shadow: -1px 1px 8px $activeShadow, 1px -1px 8px $activeShadow;
            }
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
            height: 36px;
            width: 36px;
            text-align: center;
            &:before {
                content: '';
                position: absolute;
                top: 4px;
                left: 4px;
                width: 28px;
                height: 28px;
                background: #ffffff;
                border-radius: 3px;
                transform: rotate(45deg);
                z-index: -1;
            }
        }
        .node-type-icon {
            height: 36px;
            line-height: 36px;
            font-size: 24px;
            color: $blueDark;
            text-align: center;
        }
        .process-node {
            position: relative;
            width: 150px;
            height: 42px;
            line-height: 42px;
            text-align: center;
            background: #ffffff;
            border-radius: 4px;
            box-shadow: 0px 0px 20px 0px  $defaultShadow;
            cursor: pointer;
            &.actived {
                box-shadow: 0px 0px 20px 0px $activeShadow;
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
            }
            .node-name {
                margin-left: 32px;
                width: 116px;
                font-size: 12px;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
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
            
        }
        .subflow-node {
            &:hover > .ui-node-shadow {
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
        }
        .subflow-node-icon {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 17px;
            height: 8px;
            background: $blueDark;
            border-top-left-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        .task-status-icon {
            position: absolute;
            top: -10px;
            right: -8px;
            width: 18px;
            height: 18px;
            line-height: 18px;
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
                margin-top: 2px;
            }
            .common-icon-loading {
                display: inline-block;
                vertical-align: -1px;
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
