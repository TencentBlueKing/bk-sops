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
    <div class="node-tree-wrapper" data-test-id="taskExcute_tree_nodeTree">
        <bk-tree
            class="node-tree"
            ref="tree1"
            :data="treeData"
            :show-icon="showIcon"
            :node-key="'id'"
            :tpl="tpl"
            :has-border="true">
        </bk-tree>
    </div>
</template>
<script>

    import { bkTree } from 'bk-magic-vue'
    import tools from '@/utils/tools.js'
    export default {
        name: 'NodeTree',
        components: {
            bkTree
        },
        props: {
            data: {
                type: Array,
                default () {
                    return []
                }
            },
            selectedFlowPath: {
                type: Array,
                default () {
                    return []
                }
            },
            heirarchy: {
                type: String,
                default: ''
            },
            level: {
                type: Number,
                default: 1
            },
            defaultActiveId: {
                type: String,
                default: ''
            },
            nodeDisplayStatus: {
                type: Object,
                default: {},
                required: true
            }
        },
        data () {
            return {
                curSelectId: '',
                treeData: [],
                showIcon: false,
                allNodeDate: {}
            }
        },
        watch: {
            data: {
                handler () {
                    this.treeData = tools.deepClone(this.data)
                    this.nodeAddStatus(this.treeData, this.nodeDisplayStatus.children)
                },
                deep: true,
                immediate: true
            },
            nodeDisplayStatus: {
                handler (val) {
                    this.nodeAddStatus(this.treeData, val.children)
                },
                deep: true,
                immediate: true
            }
        },
        mounted () {
            if (this.defaultActiveId) {
                this.setDefaultActiveId(this.treeData, this.treeData, this.defaultActiveId)
            }
        },
        methods: {
            nodeAddStatus (data, states) {
                data.forEach(item => {
                    if (item.id && states[item.id]) {
                        item.state = states[item.id].state
                    } else {
                        item.state = 'WAIT'
                    }
                    if (item.isGateway) {
                        item.state = 'Gateway'
                    }
                    if (item.children && item.children.length !== 0) {
                        this.nodeAddStatus(item.children, states)
                    }
                })
            },
            tpl (node) {
                if (!this.allNodeDate[node.id] && node.id !== 'undefined') {
                    this.allNodeDate[node.id] = node
                }
                
                const gatewayType = {
                    'EmptyStartEvent': 'commonicon-icon common-icon-node-startpoint-en',
                    'EmptyEndEvent': 'commonicon-icon common-icon-node-endpoint-en',
                    'ParallelGateway': 'commonicon-icon common-icon-node-parallelgateway-shortcut',
                    'ExclusiveGateway': 'commonicon-icon common-icon-node-branchgateway',
                    'ConvergeGateway': 'commonicon-icon common-icon-node-convergegateway'
                }
                const stateColor = {
                    FINISHED: 'color:#61c861;',
                    FAILED: 'color:#d84038;',
                    WAIT: 'color:#dedfe6;',
                    BLOCKED: 'color:#4b81f7;'
                }
                const nodeStateMap = {
                    FINISHED: 'background: #E5F6EA;border: 1px solid #3FC06D;',
                    FAILED: 'background: #ecbbb7;border: 1px solid #ecbbb7;',
                    WAIT: 'background: #e0e1e9;border: 1px solid #e0e1e9;',
                    RUNNING: 'background: #7ea2f0;border: 1px solid #4d83f7;'
                }
                const iconClass = gatewayType[node.type]
                // 并行、条件分支样式
                const conditionClass = node.title !== '默认' ? 'condition' : 'default-conditon'
                // 选中样式
                const isActive = node.selected ? 'is-node-active' : 'default-node'
                // 节点样式
                const nodeClass = node.parent !== null ? 'node' : 'root-node'
                // 处理条件分支
                if (node.isGateway) {
                    return <span class={conditionClass}>
                        <span style={'font-size:12px'} data-node-id={node.id} domPropsInnerHTML={node.name} onClick={node => this.onSelectNode(node)}></span>
                    </span>
                } else if (gatewayType[node.type]) {
                    return <span style={'font-size: 16px'}>
                        <span class={iconClass} style={stateColor[node.state]}></span>
                        <span class={isActive} data-node-id={node.id} domPropsInnerHTML={node.name} onClick={node => this.onSelectNode(node)}></span>
                    </span>
                } else {
                    return <span style={'font-size: 10px'}>
                        <span class={nodeClass} style={nodeStateMap[node.state]}></span>
                        <span class={isActive} data-node-id={node.id} domPropsInnerHTML={node.name} onClick={node => this.onSelectNode(node)}></span>
                    </span>
                }
            },
            setDefaultActiveId (data, nodes, id) {
                this.curSelectId = id
                nodes.forEach(node => {
                    if (node.children) {
                        this.setDefaultActiveId(data, node.children, id)
                    }
                    if (node.id === id) {
                        this.$set(node, 'selected', true)
                        node.parent.expanded = true
                        this.setExpand(node.parent)
                    } else {
                        this.$set(node, 'selected', false)
                    }
                })
            },
            setExpand (node) {
                if (node.parent) {
                    node.parent.expanded = true
                    this.setExpand(node.parent)
                }
            },
            getNodeActivedState (id) {
                const len = this.selectedFlowPath.length
                if (this.selectedFlowPath[len - 1].id === id) {
                    return true
                }
                return false
            },
            onSelectNode (e) {
                const id = e.target.dataset.nodeId
                const node = this.allNodeDate[id]
                const nodeType = node.type === 'ServiceActivity' ? 'tasknode' : (node.type === 'SubProcess' ? 'subflow' : 'controlNode')
                node.selected = nodeType !== 'subflow'
                let rootNode = node
                let nodeHeirarchy = ''
                if (!rootNode.id) return
                while (rootNode.parent) {
                    if (nodeHeirarchy) {
                        nodeHeirarchy += '.' + rootNode.parent.id
                    } else {
                        nodeHeirarchy += rootNode.parent.id
                    }
                    rootNode = rootNode.parent
                }
                nodeHeirarchy = nodeHeirarchy.split('.').reverse()[0]
                if (this.curSelectId === node.id) return
                this.setDefaultActiveId(this.treeData, this.treeData, id)
                this.$emit('onSelectNode', nodeHeirarchy, node.id, nodeType)
            }
        }
    }
</script>
<style lang="scss">
.bk-tree .tree-drag-node .tree-expanded-icon {
    margin-right: 3px;
    z-index: 99;
}
</style>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.node-tree-wrapper {
    display: inline-block;
    width: 229px;
    min-width: 229px;
    padding: 24px 8px 0;
}
.node-tree {
    height: 100%;
    white-space: nowrap;
    overflow-x: auto;
    @include scrollbar;
}
.is-node-active {
    color: #3a84ff !important;
    font-size: 10px;
    padding: 0 4px;
    cursor: pointer;
}
.activity-node {
    display: inline-block;
    border: 2px solid #81d79f;
    width: 8px;
    height: 8px;
    margin: 0 4px;
    border-radius: 4px;
    background: #e5f6ea;
}
.condition {
    font-size: 10px;
    background: #FBF9E2;
    border: 1px solid #CCC79E;
    border-radius: 1px;
    color: #968E4D;
    position: relative;
    border-left: none;
    padding-right: 4px;
    ::before {
        content: '';
        position: absolute;
        top: -1px;
        left: -20px;
        width: 20px;
        height: 16px;
        background-color: #FBF9E2;
        border: 1px solid #CCC79E;
        border-right: none;
        border-radius: 1px;
        color: #968E4D;
        z-index: 88;
    }
}
.default-conditon {
    font-size: 10px;
    background: #F0F1F5;
    border: 1px solid #C4C6CC;
    border-radius: 1px;
    color: #968E4D;
    position: relative;
    border-left: none;
    padding-right: 4px;
    ::before {
        content: '';
        position: absolute;
        top: -1px;
        left: -20px;
        width: 20px;
        height: 16px;
        background-color: #F0F1F5;
        border: 1px solid #C4C6CC;
        border-right: none;
        border-radius: 1px;
        color: #968E4D;
        z-index: 88;
    }
}
.gateway {
    font-size: 10px;
}
.root-node {
    display: none;
    color: #7ea2f0;
}
.node {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #E5F6EA;
    border: 1px solid #3FC06D;
    border-radius: 4px;
    margin:0 3px;
    font-size: 10px;
    padding: 0 2px;
    cursor: pointer;
}
.default-node {
    font-size: 10px;
    padding: 0 4px;
    cursor: pointer;
}
</style>
