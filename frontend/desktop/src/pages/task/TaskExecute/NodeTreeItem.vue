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
                    'has-converge-gateway': node.hasConvergeGW,
                    'subprocess-border-line': node.isSubProcess && node.expanded,
                    'condition-or-level-up': node.conditionType || node.isLevelUp
                }
            ]">
            <div
                :class="['tree-node-item', { 'node-active': (node.parentId ? `${node.id}-${node.parentId}` : node.id) === activeId }]"
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
                        v-if="node.isSubProcess && node.children.length"
                        class="common-icon-next-triangle-shape gateway-triangle"
                        @click.stop="toggleExpanded(node)">
                    </span>
                    <!--分支条件图标-->
                    <span
                        v-else-if="node.conditionType && (node.isCallback ? node.children.length : true)"
                        class="branch-condition-box"
                        :class="{
                            'default-condition': node.conditionType === 'default',
                            'empty-condition': !node.children || !node.children.length
                        }"
                        @click.stop="toggleExpanded(node)">
                        <i class="common-icon-next-triangle-shape"></i>
                    </span>
                    <!--空的占位符-->
                    <span v-else-if="node.isCallback || node.isLevelUp ? false : !node.parentId" class="empty-div"></span>
                    <!--汇合图标-->
                    <span
                        v-if="node.isDifferLevelConverge"
                        :class="['common-icon-converge-node', nodeStateMap[node.state]]">
                    </span>
                    <!--网关图标-->
                    <span
                        v-else-if="nodeType[node.type]"
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
                <span class="node-name">
                    <span class="name" v-bk-overflow-tips>{{ node.title }}</span>
                    <span v-if="node.conditionType && (!node.children || !node.children.length)" class="empty-branch">
                        {{ $t('（') + $t('空分支') + $t('）') }}
                    </span>
                </span>
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
                @click="$emit('click', $event)">
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
                if (node.conditionType === 'parallel') {
                    node.expanded = true
                    return
                }
                if (node.expanded) {
                    const activeId = node.parentId ? node.id + '-' + node.parentId : node.id
                    node.expanded = activeId !== this.activeId
                } else {
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
                    &.empty-condition {
                        color: #63656e;
                        background: #f5f7fa;
                        border-color: #dcdee5;
                    }

                }
                .common-icon-converge-node,
                .subprocess-icon,
                .gateway-icon {
                    margin-top: 2px;
                    color: #c4c6cc;
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
                .common-icon-converge-node {
                    font-size: 12px;
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
                        top: -3px;
                        transform: rotate(90deg);
                        transition: transform .2s;
                    }
                }
            }

            .node-name {
                flex: 1;
                display: flex;
                align-items: center;
                overflow: hidden;
                .name {
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .empty-branch {
                    flex-shrink: 0;
                    font-size: 12px;
                    color: #979ba5;
                }
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
        >.node-tree {
            >.tree-node-container {
                &:not(:last-child)::before {
                    content: '';
                    display: block;
                    position: absolute;
                    top: -6px;
                    left: -8px;
                    width: 1px;
                    height: 100%;
                    border-left: 1px solid #dcdee5;
                }
                &.branch-condition-container::after {
                    content: '';
                    display: block;
                    position: absolute;
                    top: 15.5px;
                    left: -8px;
                    width: 8px;
                    height: 1px;
                    border-top: 1px solid #dcdee5;
                }
                &:last-child {
                    >.tree-node-item::before {
                        content: '';
                        display: block;
                        position: absolute;
                        top: -6px;
                        left: -6px;
                        width: 1px;
                        height: calc(100% - 10px);
                        border-left: 1px solid #dcdee5;
                    }
                }
            }
        }
        &.has-converge-gateway {
            >.node-tree {
                >.tree-node-container:last-child {
                    &::before {
                        content: '';
                        display: block;
                        position: absolute;
                        top: 5px;
                        left: -8px;
                        width: 1px;
                        height: 100%;
                        border-left: 1px solid #dcdee5;
                    }
                    >.tree-node-item::before {
                        content: '';
                    }
                }
            }
        }
    }
    .subprocess-border-line {
        &::after {
            content: '';
            display: block;
            height: calc(100% - 23px);
            position: absolute;
            top: 28px;
            left: 25.5px;
            width: 1px;
            border-left: 1px dashed #dcdee5;
        }
    }
    .condition-or-level-up {
        >.tree-node-item {
            padding: 2px;
            margin-left: -2px;
        }
        >.node-tree {
            >.branch-condition-container {
                margin-left: 15px !important;
            }
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
