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
        @click="onNodeClick">
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

    export default {
        name: 'NodeTemplate',
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
                    if (['tasknode', 'subflow'].indexOf(this.node.type) > -1) {
                        this.$emit('onNodeClick', this.node.id)
                        e.stopPropagation()
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
            }
        }
    }
</script>
<style lang="scss">
    $blueDark: #53699d;
    $redDark: #ff5757;
    $yellowDark: #f8b53f;
    $greenDark: #30d878;
    $greyShadow: rgba(83, 105, 157, 0.15);
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

    @mixin taskNodeStyle ($color, $shadow) {
        &:hover {
            box-shadow: -1px 1px 8px $shadow, 1px -1px 8px $shadow;
        }
        .node-name {
            border-color: $color;
        }
        .stage-name {
            background-color: $color;
        }
        .subflow-node-icon {
            background-color: $color;
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
        .close-icon {
            display: none;
            position: absolute;
            top: -8px;
            right: -8px;
            font-size: 16px;
            color: #ff5757;
            background: #ffffff;
            border-radius: 50%;
            z-index: 2;
            cursor: pointer;
        }
        .circle-node {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            background: #ffffff;
            border: 1px dashed #b1b5bc;
            border-radius: 50%;
            &:hover {
                box-shadow: -1px 1px 8px $greyShadow, 1px -1px 8px $greyShadow;
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
            width: 50px;
            height: 50px;
            line-height: 50px;
            font-size: 12px;
            background: $blueDark;
            color: #ffffff;
            text-align: center;
            border-radius: 50%;
        }
        .node-type-icon {
            font-size: 30px;
            color: $blueDark;
            text-align: center;
        }
        .task-node,
        .subflow-node {
            position: relative;
            width: 152px;
            height: 90px;
            text-align: center;
            cursor: pointer;
            &:hover {
                box-shadow: -1px 1px 8px $greyShadow, 1px -1px 8px $greyShadow;
            }
            &.failed {
                @include taskNodeStyle ($redDark, $redShadow)
            }
            &.suspended {
                @include taskNodeStyle ($yellowDark, $yellowShadow)
            }
            &.running {
                @include taskNodeStyle ($yellowDark, $yellowShadow)
            }
            &.finished {
                @include taskNodeStyle ($greenDark, $greenShadow)
            }
        }
        .subflow-node .node-name {
            border-top: 5px solid $blueDark;
        }
        .subflow-node-icon {
            position: absolute;
            top: 0;
            left: 0;
            width: 24px;
            height: 19px;
            line-height: 19px;
            font-size: 18px;
            color: #ffffff;
            background: $blueDark;
        }
        .node-name {
            display: table;
            width: 100%;
            font-size: 12px;
            height: 60px;
            background: #fafafa;
            border: 1px solid #a9adb5;
            border-bottom: none;
            table-layout: fixed;
            overflow: hidden;
            & > p {
                display: table-cell;
                padding: 0 10px;
                width: 100%;
                vertical-align: middle;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
        }
        .stage-name {
            height: 30px;
            line-height: 30px;
            font-size: 14px;
            color: #ffffff;
            background: $blueDark;
            border-top: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
