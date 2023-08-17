<template>
    <ul class="node-tree">
        <li
            v-for="(node,index) in nodeList"
            :key="index"
            :style="node.style"
            :class="[
                'tree-node-container',
                {
                    'branch-condition-container': node.conditionType,
                    'parallel-gateway-container': node.type === 'ParallelGateway',
                    'gateway-border-line': node.isGateway && node.expanded && node.type !== 'ConvergeGateway',
                    'subprocess-border-line': node.isSubProcess && node.expanded
                }
            ]">
            <div
                :class="['tree-node-item', { 'node-active': node.id === activeId }]"
                @click="handleClickNode(node)">
                <!-- 左侧图标 -->
                <div :class="['node-flex-start', { expanded: node.expanded }]">
                    <!--打回图标-->
                    <span
                        v-if="node.isCallback"
                        class="callback-box"
                        v-bk-tooltips.top="$t('退回节点：') + node.callbackInfo.name"
                        @click.stop="handleClickNode(node.callbackInfo)">
                        <i class="common-icon-reback-branch"></i>
                    </span>
                    <!--子流程展开/收起-->
                    <span
                        v-if="node.isSubProcess"
                        class="common-icon-next-triangle-shape gateway-triangle"
                        @click.stop="toggleExpanded(node)">
                    </span>
                    <!--分支条件图标-->
                    <span
                        v-else-if="node.conditionType && (node.isCallback ? node.children.length : true)"
                        class="branch-condition-box"
                        :class="{ 'default-condition': node.conditionType === 'default' }"
                        @click.stop="toggleExpanded(node)">
                        <i v-if="node.children && node.children.length" class="common-icon-next-triangle-shape"></i>
                    </span>
                    <!--空的占位符-->
                    <span v-else-if="node.isCallback ? false : !node.parentId" class="empty-div"></span>
                    <!--网关图标-->
                    <span
                        v-if="nodeType[node.type]"
                        :class="[
                            nodeType[node.type],
                            nodeStateMap[node.state]
                        ]"
                        @click.stop="toggleExpanded(node)">
                    </span>
                    <!--开始/结束/普通任务图标-->
                    <span v-else-if="!node.conditionType" class="default-node" :class="nodeStateMap[node.state]"></span>
                </div>
                <!-- 节点名称 -->
                <span v-bk-overflow-tips class="node-name">{{ node.title }}</span>
            </div>
            <div
                v-if="node.expanded && node.dynamicLoad"
                class="dynamic-load"
                v-bkloading="{ isLoading: node.expanded && node.dynamicLoad, opacity: 1 }">
            </div>
            <NodeTreeItem
                v-else-if="node.expanded && node.children && node.children.length"
                v-show="node.expanded"
                :active-id="activeId"
                :node-list="node.children"
                @dynamicLoad="$emit('dynamicLoad', $event)"
                @click="handleClickNode">
            </NodeTreeItem>
        </li>
    </ul>
</template>

<script>
    export default {
        name: 'NodeTreeItem',
        components: { },
        props: {
            nodeList: {
                type: Array,
                default: () => ([]),
                required: true
            },
            activeId: {
                type: String,
                default: ''
            }
        },
        data () {
            const nodeType = {
                'SubProcess': 'subprocess-icon common-icon-sub-process',
                'ParallelGateway': 'gateway-icon common-icon-parallel-gateway',
                'ExclusiveGateway': 'gateway-icon common-icon-branch-gateway',
                'ConvergeGateway': 'gateway-icon common-icon-converge-gateway',
                'ConditionalParallelGateway': 'gateway-icon common-icon-node-conditionalparallelgateway'
            }
            const nodeStateMap = {
                FINISHED: 'finished',
                FAILED: 'failed',
                READY: 'ready',
                RUNNING: 'running',
                SKIP: 'skip',
                SUSPENDED: 'running'
            }
            return {
                nodeType,
                nodeStateMap
            }
        },
        methods: {
            toggleExpanded (node) {
                node.expanded = !node.expanded
                if (!node.expanded) {
                    node.children.forEach(item => {
                        item.expanded = false
                    })
                }
                if (node.dynamicLoad) {
                    this.$emit('dynamicLoad', node)
                }
            },
            handleClickNode (node) {
                const { conditionType, children } = node
                if (conditionType) {
                    if (conditionType === 'parallel') {
                        node.expanded = true
                        return
                    }
                    if (children.length === 0) {
                        return
                    }
                }
                if (!node.expanded) {
                    node.expanded = true
                }
                this.$emit('click', node)
            }
        }
    }
</script>

<style lang="scss" scoped>

.node-tree {
    width: 100%;

    .tree-node-container {
        position: relative;
        .tree-node-item {
            position: relative;
            display: flex;
            align-items: center;
            height: 32px;
            font-size: 14px;
            color: #63656e;
            cursor: pointer;
            &:hover {
                background-color: #f0f1f5;
            }
            .node-flex-start {
                display: flex;
                align-items: center;
                flex-shrink: 0;
                font-size: 16px;
                margin-right: 6px;
                .gateway-triangle {
                    font-size: 14px;
                    color: #c3c6cc;
                    margin-right: 4px;
                }
                .empty-div {
                    height: 14px;
                    width: 18px;
                }
                .common-icon-next-triangle-shape {
                    font-size: 14px;
                    color: #c3c6cc;
                }
                .callback-box,
                .branch-condition-box {
                    width: 16px;
                    height: 16px;
                    font-size: 12px;
                    text-align: center;
                    background: #fbf9e2;
                    border: 1px solid #ccc79e;
                    border-radius: 1px;
                    .common-icon-reback-branch,
                    .common-icon-next-triangle-shape {
                        display: inline-block;
                        position: relative;
                        top: -2px;
                        font-size: 12px;
                        color: #c3c6cc;
                    }
                    &.default-condition {
                        background: #f0f1f5;
                        border-color: #c4c6cc;
                    }

                }
                .subprocess-icon,
                .gateway-icon {
                    margin-top: 2px;
                    &.finished {
                        color: #2dcb56;
                    }
                    &.failed {
                        color: #ea3636;
                    }
                    &.ready {
                        color: #c4c6cc;
                    }
                    &.running {
                        color: #4d83f7;
                    }
                    &.skip {
                        color: #da635f;
                    }
                }
                .default-node {
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #f0f4f5;
                    border: 1px solid #c4c6cc;
                    border-radius: 4px;
                    margin: 1px 4px 0;
                    &.finished {
                        background: #e5f6ea;
                        border-color: #3fc06d;
                    }
                    &.failed {
                        background: #ecbbb7;
                        border-color: #ecbbb7;
                    }
                    &.ready {
                        background: #f0f4f5;
                        border-color: #c4c6cc;
                    }
                    &.running {
                        background: #f0f5ff;
                        border-color: #699df4;
                    }
                    &.skip {
                        background: #f8c4c1;
                        border-color: #da635f;
                    }
                }
                &.expanded {
                    .common-icon-next-triangle-shape {
                        transform: rotate(90deg);
                        transition: transform .2s;
                    }
                }
            }

            .node-name {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
        .node-active {
            background: #e1ecff;
            .node-name {
                color: #3a84ff;
            }
        }
    }
    .gateway-border-line {
        &::before {
            content: '';
            display: block;
            height: calc(100% - 20px);
            position: absolute;
            top: 28px;
            left: 25.5px;
            width: 1px;
            border-left: 1px solid #dcdee5;
        }
        >.node-tree {
            >.branch-condition-container::before {
                content: '';
                display: block;
                position: absolute;
                top: 15.5px;
                left: -7px;
                width: 7px;
                height: 1px;
                border-top: 1px solid #dcdee5;
            }
        }
        &.parallel-gateway-container::before {
            height: calc(100% - 44px);
        }
    }
    .subprocess-border-line {
        &::before {
            content: '';
            display: block;
            height: calc(100% - 20px);
            position: absolute;
            top: 28px;
            left: 25.5px;
            width: 1px;
            border-left: 1px dashed #dcdee5;
        }
    }
    .dynamic-load {
        margin-left: 42px;
        height: 40px;
        /deep/.bk-loading-wrapper {
            top: 70%;
            left: 15%;
        }
    }
}
</style>