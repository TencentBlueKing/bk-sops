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
    <div class="canvas-node-item">
        <component :is="nodeTemplate" :node="node" />
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

    export default {
        name: 'NodeTemplate',
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
        }
    }
</script>
<style lang="scss">
    .canvas-node-item {
        position: relative;
        z-index: 3;
        .circle-node {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            background: #ffffff;
            border: 1px dashed #b1b5bc;
            border-radius: 50%;
        }
        .circle-node-text {
            width: 50px;
            height: 50px;
            line-height: 50px;
            font-size: 12px;
            background: #53699d;
            color: #ffffff;
            text-align: center;
            border-radius: 50%;
        }
        .node-type-icon {
            font-size: 30px;
            color: #53699d;
            text-align: center;
        }
        .task-node,
        .subflow-node {
            width: 152px;
            height: 90px;
            text-align: center;
            cursor: pointer;
        }
        .subflow-node .node-name {
            border-top: 5px solid #53699d;
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
            background: #53699d;
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
            background: #53699d;
            border-top: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }
</style>
