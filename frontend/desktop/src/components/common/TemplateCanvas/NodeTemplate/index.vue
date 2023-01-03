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
        class="canvas-node-item"
        @mousedown="onMousedown"
        @mouseenter="$emit('onNodeMouseEnter', node)"
        @click="onNodeClick"
        @dblclick="onNodeDblclick">
        <div class="canvas-node-content">
            <component
                :is="nodeTemplate"
                :node="node"
                :has-admin-perm="hasAdminPerm"
                @onNodeCheckClick="onNodeCheckClick"
                @onRetryClick="$emit('onRetryClick', $event)"
                @onSkipClick="$emit('onSkipClick', $event)"
                @onModifyTimeClick="$emit('onModifyTimeClick', $event)"
                @onGatewaySelectionClick="$emit('onGatewaySelectionClick', $event)"
                @onTaskNodeResumeClick="$emit('onTaskNodeResumeClick', $event)"
                @onApprovalClick="$emit('onApprovalClick', $event)"
                @onForceFail="$emit('onForceFail', $event)"
                @onSubflowPauseResumeClick="onSubflowPauseResumeClick"
                @onSubflowDetailClick="onSubflowDetailClick" />
        </div>
    </div>
</template>
<script>
    import StartPoint from './StartPoint.vue'
    import EndPoint from './EndPoint.vue'
    import TaskNode from './TaskNode.vue'
    import Subflow from './Subflow.vue'
    import BranchGateway from './BranchGateway.vue'
    import ParallelGateway from './ParallelGateway.vue'
    import ConditionalParallelGateway from './ConditionalParallelGateway.vue'
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
            },
            hasAdminPerm: {
                type: Boolean,
                default: false
            },
            activities: {
                type: Object,
                default: () => ({})
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
                    conditionalparallelgateway: ConditionalParallelGateway,
                    convergegateway: ConvergeGateway
                },
                clickTimer: null
            }
        },
        computed: {
            nodeTemplate () {
                if (this.node.code === 'subprocess_plugin') {
                    return this.components.subflow
                }
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
            onSubflowPauseResumeClick (id, value) {
                this.$emit('onSubflowPauseResumeClick', id, value)
            },
            onSubflowDetailClick (id) {
                this.$emit('onNodeClick', id, 'subflowDetail')
            }
        }
    }
</script>
<style lang="scss">
    @import '@/scss/mixins/multiLineEllipsis.scss';
    @import '@/scss/mixins/scrollbar.scss';

    $grayDark: #b4becd;
    $blueDark: #699df4;
    $defaultColor: #738abe;
    $redDark: #ea3636;
    $yellowDark: #ff9c01;
    $greenDark: #9adc9e;
    $brightRedDark: #f0a0a0;
    $whiteColor: #ffffff;
    $defaultShadow: rgba(0, 0, 0, 0.15);
    $activeShadow: rgba(0, 0, 0, 0.3);
    $redShadow: rgba(255, 87, 87, 0.15);
    $yellowShadow: rgba(248, 181, 63, 0.15);
    $greenShadow: rgba(48, 216, 120, 0.15);
    $blueShadow: rgba(58, 132, 255, 0.15);

    @mixin circleStatusStyle ($color) {
        background-color: $color;
        box-shadow: 0 0 0 2px $color;
        .circle-node-text {
            color: $whiteColor;
        }
    }

    @mixin taskNodeStyle ($color) {
        &:hover {
            .node-name {
                border-color: $color;
            }
            .state-icon {
                display: block;
            }
        }
        .node-status-block {
            background-color: $color;
        }
        .task-status-icon {
            background: $color;
        }
    }
    @mixin nodeClick ($color) {
        .node-name {
            border-color: $color;
            background-color: rgba($color, 0.3);
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
            width: 34px;
            height: 34px;
            background: #96a1b9;
            border-radius: 50%;
            box-shadow: 0 0 0 2px #96a1b9;
            &.ready {
                @include circleStatusStyle($grayDark);
            }
            &.finished {
                @include circleStatusStyle($greenDark);
                &.end-point {
                    @include circleStatusStyle(#2dcb56);
                }
            }
            &.running {
                @include circleStatusStyle($blueDark)
            }
            &.failed {
                @include circleStatusStyle($redDark)
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
            &:hover {
                .state-icon {
                    display: block;
                }
            }
            &.ready {
                @include gatewayStyle($grayDark);
            }
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
            .state-icon {
                position: absolute;
                right: -5px;
                bottom: -20px;
                display: none;
                width: max-content;
                color: #63656e;
                font-size: 12px;
                z-index: 5;
                padding-top: 5px;
                > span {
                    display: flex;
                    align-items: center;
                    i {
                        color: #979ba5;
                        margin-right: 5px;
                    }
                    &:hover {
                        cursor: pointer;
                        color: #3a84ff;
                        i {
                            color: #3a84ff;
                        }
                    }
                }
            }
        }
        .node-type-icon {
            height: 32px;
            line-height: 32px;
            font-size: 24px;
            color: $defaultColor;
            text-align: center;
        }
        .task-node {
            position: relative;
            width: 154px;
            height: 54px;
            text-align: center;
            background: #ffffff;
            border-radius: 4px;
            cursor: pointer;
            &.actived {
                box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.3);
            }
            &.default {
                @include taskNodeStyle ($defaultColor);
                &.actived {
                     @include nodeClick ($defaultColor);
                }
            }
            &.ready {
                @include taskNodeStyle ($grayDark);
                &.actived {
                     @include nodeClick ($grayDark);
                }
            }
            &.failed {
                box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
                .node-name {
                    border-color: $redDark;
                }
                @include taskNodeStyle ($redDark);
                &.actived {
                    @include nodeClick ($redDark);
                }
            }
            &.suspended {
                @include taskNodeStyle ($blueDark);
                &.actived {
                    @include nodeClick ($blueDark);
                }
            }
            &.running {
                box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.15);
                .node-name {
                    border-color: $blueDark;
                }
                @include taskNodeStyle ($blueDark);
                &.actived {
                    @include nodeClick ($blueDark);
                }
            }
            &.finished {
                @include taskNodeStyle ($greenDark);
                &.actived {
                     @include nodeClick ($greenDark);
                }
            }
            &.fail-skip {
                @include taskNodeStyle ($brightRedDark);
                .node-name .name-text {
                    color: #c4c6cc;
                }
                &.actived {
                    @include nodeClick ($brightRedDark);
                }
            }

            .node-status-block {
                display: flex;
                align-items: center;
                padding: 0 8px;
                height: 20px;
                background: $defaultColor;
                text-align: left;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                .node-icon {
                    width: 16px;
                }
                .node-icon-font {
                    font-size: 16px;
                    color: #ffffff;
                }
                .stage-name {
                    padding: 0 4px;
                    width: 170px;
                    font-size: 12px;
                    color: #ffffff;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    overflow: hidden;
                }
            }
            .node-name {
                display: flex;
                align-items: center;
                padding: 0 8px;
                height: calc(100% - 20px);
                line-height: 14px;
                border: 1px solid #ffffff;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                border-color: $grayDark;
                .name-text {
                    display: -webkit-box;
                    width: 100%;
                    font-size: 12px;
                    color: #63656e;
                    text-align: left;
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
                overflow: hidden;
                .bk-form-checkbox,
                .dark-circle {
                    float: left;
                    margin-right: 2px;
                    font-size: 14px;
                    color: #979ba5;
                }
                .error-handle-icon {
                    float: left;
                    margin-right: 2px;
                    padding: 0 3px;
                    line-height: 12px;
                    color: #ffffff;
                    background: #979ba5;
                    border-radius: 2px;
                    .text {
                        display: inline-block;
                        font-size: 12px;
                        transform: scale(0.8);
                    }
                }
            }
            .state-icon {
                position: absolute;
                right: 5px;
                bottom: -20px;
                display: none;
                color: #63656e;
                font-size: 12px;
                width: max-content;
                padding-top: 5px;
                > span {
                    &:not(:last-child) {
                        margin-right: 23px;
                        position: relative;
                        &::after {
                            content: '';
                            position: absolute;
                            top: 0;
                            right: -11px;
                            display: inline-block;
                            height: 16px;
                            width: 1px;
                            background: #979ba5;
                        }
                    }
                    i {
                        color: #979ba5;
                        margin-right: 5px;
                        &.common-icon-play {
                            font-size: 14px;
                        }
                    }
                    &:hover {
                        cursor: pointer;
                        color: #3a84ff;
                        i {
                            color: #3a84ff;
                        }
                    }
                }
            }
        }
        .node-execute-icon {
            position: absolute;
            display: flex;
            flex-direction: row-reverse;
            align-items: center;
            justify-content: space-between;
            top: -10px;
            right: -8px;
            height: 18px;
        }
        .task-status-icon {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-left: 2px;
            width: 18px;
            height: 18px;
            font-size: 14px;
            border-radius: 50%;
            background: #f8b53f;
            color: #ffffff;
            box-shadow: 0px 2px 4px 0px rgba(0, 0, 0, 0.1);
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
            .icon-arrows-right-shape {
                font-size: 12px;
            }
            .retry-times {
                font-size: 12px;
            }
            &.task-node-loop {
                position: relative;
                height: 16px;
                width: 16px;
                color: #3a84ff;
                background: #fff !important;
                > i {
                    position: absolute;
                    font-size: 14px;
                }
                > span {
                    position: relative;
                    top: -0.5px;
                    font-weight: 700;
                    font-size: 18px;
                    transform: scale(.5);
                }
                &.loop-plural {
                    width: 26px;
                    height: 16px;
                    border-radius: 8px;
                }
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
        .node-subscript {
            font-size: 12px;
            background: #ea3636 !important;
        }
        .node-phase-icon {
            i {
                font-size: 14px;
                &.phase-warn {
                    color: $yellowDark;
                }
                &.phase-error {
                    color: $redDark;
                }
            }
        }
    }
    .task-node-tooltip.el-tooltip__popper {
        z-index: 4 !important;
    }
</style>
<style lang="scss">
    .node-tooltip-content {
        padding: 10px;
        background: #303133;
        border-radius: 2px;
        overflow: hidden;
        .bk-button {
            float: left;
            padding: 0 10px;
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
            &:first-child {
                padding-left: 0;
            }
            &:last-child {
                padding-right: 0;
            }
            &:not(:last-child) {
                border-right: 1px solid #63656e;
            }
        }
    }
</style>
