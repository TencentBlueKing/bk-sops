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
    <div class="node-tree-wrapper">
        <div class="tree-item" v-for="tree in treeData" :key="tree.id" data-test-id="taskExcute_tree_nodeTree">
            <div v-if="!tree.children || tree.name === '汇聚网关'" :class="['tree-item-info', tree.isGateway ? 'gateway' : '']">
                <div class="tree-line"></div>
                <div class="tree-item-status">
                    <span class="tree-item-expanded"></span>
                    <span v-if="tree.type === 'ConvergeGateway'" class="commonicon-icon common-icon-node-convergegateway"></span>
                    <span v-else :class="['default-node', nodeStateMap[tree.state]]"></span>
                </div>
                <div :class="['tree-item-name', curSelectId === tree.id ? 'active-name' : '']" @click="onClickNode(tree)">{{ tree.name }}</div>
            </div>
            <div v-else class="tree-item-children">
                <bk-tree
                    class="node-tree"
                    :data="[tree]"
                    :show-icon="showIcon"
                    :tpl="tpl"
                    :has-border="true">
                </bk-tree>
            </div>
        </div>
        <!-- <Tree :tree-data="treeData"></Tree> -->
    </div>
</template>
<script>

    import { bkTree } from 'bk-magic-vue'
    import tools from '@/utils/tools.js'
    // import Tree from './Tree.vue'

    export default {
        name: 'NodeTree',
        components: {
            bkTree
            // Tree
        },
        props: {
            data: {
                type: Array,
                default () {
                    return []
                }
            },
            nodeNav: {
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
            },
            isCondition: Boolean
        },
        data () {
            const gatewayType = {
                'SubProcess': 'commonicon-icon ',
                'EmptyStartEvent': 'commonicon-icon common-icon-node-startpoint-en',
                'EmptyEndEvent': 'commonicon-icon common-icon-node-endpoint-en',
                'ParallelGateway': 'commonicon-icon common-icon-node-parallelgateway-shortcut',
                'ExclusiveGateway': 'commonicon-icon common-icon-node-branchgateway',
                'ConvergeGateway': 'commonicon-icon common-icon-node-convergegateway conver',
                'ConditionalParallelGateway': 'commonicon-icon common-icon-node-conditionalparallelgateway'
            }
            const stateColor = {
                FINISHED: 'color:#61c861;',
                FAILED: 'color:#da443c;',
                WAIT: 'color:#dedfe6;',
                BLOCKED: 'color:#4b81f7;',
                RUNNING: 'color:#4d83f7;',
                SKIP: 'color: #edbbb8',
                SUSPENDED: 'color: #699df4'
            }
            const nodeStateMap = {
                FINISHED: 'finished',
                FAILED: 'failed',
                WAIT: 'wait',
                RUNNING: 'running',
                SKIP: 'skip',
                SUSPENDED: 'running'
            }
            return {
                curSelectId: '',
                treeData: [],
                subTreeData: [],
                showIcon: false,
                allNodeDate: {},
                gatewayType,
                stateColor,
                nodeStateMap,
                cacheSubflowSelectNode: {},
                curSelectTreeId: '',
                setDefaultGateway: false
            }
        },
        watch: {
            data: {
                handler (value) {
                    this.treeData = tools.deepClone(value[0].children)
                    this.$nextTick(() => {
                        this.nodeAddStatus(this.treeData, this.nodeDisplayStatus.children)
                        this.setDefaultActiveId(this.treeData, this.treeData, this.defaultActiveId)
                    })
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
            onClickNode (node) {
                console.log(node)
                this.setDefaultGateway = false
                if (node.children && node.children.length === 0) return
                // this.$emit('onOpenGatewayInfo', this.cachecallbackData, false)
                node.expanded = !node.expanded
                this.curSelectId = node.id
                const nodeHeirarchy = node.id
                this.$emit('onSelectNode', nodeHeirarchy, node.id, 'tasknode')
            },
            renderSubProcessData (node) {
                if (node) {
                    this.$nextTick(() => {
                        this.treeData = node.subChildren
                    })
                }
            },
            nodeAddStatus (data, states) {
                if (data) {
                    data.forEach(item => {
                        if (item.id && states[item.id]) {
                            item.state = states[item.id].skip ? 'SKIP' : states[item.id].state
                        } else {
                            item.state = 'WAIT'
                        }
                        if (item.isGateway) {
                            item.state = 'Gateway'
                        }
                        if (item.type === 'SubProcess') {
                            this.nodeAddStatus(item.subChildren, states)
                        }
                        if (item.children && item.children.length !== 0) {
                            this.nodeAddStatus(item.children, states)
                        }
                    })
                }
            },
            tpl (node) {
                if (!this.allNodeDate[node.id] && node.id !== 'undefined') {
                    this.allNodeDate[node.id] = node
                }
                // 退回节点
                const callbackTip = node.isLoop ? this.$t('退回节点：') + node.callbackName : ''
                const isSubIcon = node.parent && node.parent.type === 'SubProcess' && (node.type === 'EmptyStartEvent' || node.type === 'EmptyEndEvent')
                const iconClass = isSubIcon ? `node ${this.nodeStateMap[node.state]} ` : this.gatewayType[node.type]
                // 并行、条件分支样式
                let conditionClass = node.title !== '默认' ? 'condition' : 'default-conditon'
                if (node.isLoop) conditionClass = 'callback-condition'
                // 选中样式
                const isActive = this.curSelectId === node.id ? 'is-node-active' : 'default-tpl-node'
                // 节点样式
                const nodeClass = node.parent !== null ? `node ${this.nodeStateMap[node.state]} ` : `root-node ${this.nodeStateMap[node.state]}`
                // 处理条件分支
                if (node.isGateway) {
                    return <span class={conditionClass}>
                        <span class={'commonicon-icon common-icon-return-arrow callback'} onClick={(e) => this.onSelectNode(e, node, 'callback')} v-bk-tooltips={callbackTip}></span>
                        <span class={isActive} style={'font-size:12px'} data-node-id={node.id} domPropsInnerHTML={node.title} onClick={(e) => this.onSelectNode(e, node, 'gateway')}></span>
                    </span>
                } else if (this.gatewayType[node.type]) {
                    return <span style={'font-size: 16px'}>
                        <span class={iconClass} style={this.stateColor[node.state]}></span>
                        <span class={isActive} data-node-id={node.id} data-gateway-type={node.gatewayType} domPropsInnerHTML={node.name} onClick={(e) => this.onSelectNode(e, node, 'gateway')}></span>
                    </span>
                } else {
                    return <span style={'font-size: 10px'}>
                        <span class={nodeClass}></span>
                        <span class={isActive} data-node-id={node.id} domPropsInnerHTML={node.name} onClick={(e) => this.onSelectNode(e, node, 'node')}></span>
                    </span>
                }
            },
            setDefaultActiveId (data, nodes, id) {
                this.curSelectId = id
                if (nodes) {
                    nodes.forEach(node => {
                        if (node.id === id) {
                            this.$set(node, 'selected', true)
                            if (this.setDefaultGateway) {
                                this.$set(node, 'expanded', true)
                            }
                            if (node.parent) {
                                node.parent.expanded = true
                                this.setExpand(node.parent)
                            }
                        } else {
                            this.$set(node, 'selected', false)
                        }
                        if (node.children) {
                            this.setDefaultActiveId(data, node.children, id)
                        }
                    })
                }
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
            onSelectNode (e, node, type) {
                // 当父节点展开且未选中、 节点为并行、网关条件时阻止冒泡
                // this.setDefaultGateway = false
                // if (node.selected && node.type === 'SubProcess') {
                //     node.selected = false
                //     node.parent.expanded = true
                // }
                // if (node.expanded && !node.selected) e.stopPropagation()
                // if ((node.conditionType === 'parallel' || node.conditionType === 'default') && type === 'gateway') {
                //     node.expanded = !node.expanded
                //     e.stopPropagation()
                //     return
                // }
                // // this.$emit('onOpenGatewayInfo', node.callbackData, false)
                // if (type === 'gateway') {
                //     // 分支条件没有id,使用name 代替
                //     if (node.state === 'Gateway') {
                //         this.curSelectId = node.id || node.name
                //         this.$emit('onOpenGatewayInfo', node.callbackData, true)
                //         return
                //     }
                // }
                // if (type === 'node' || type === 'callback') {
                //     const treeNodes = Array.from(document.querySelectorAll('.tree-node'))
                //     if (node.parent) {
                //         const curNodeIndex = node.parent.children.findIndex(item => item.id === node.id)
                //         node.parent.children.forEach((item, index) => {
                //             if (item.type === 'ConvergeGateway') {
                //                 const converge = treeNodes.filter(dom => dom.dataset.gatewayType === 'converge')
                //                 if (index > curNodeIndex) {
                //                     if (!node.expanded) {
                //                         converge.forEach(cdom => {
                //                             cdom.style.display = 'block'
                //                         })
                //                     } else {
                //                         converge.forEach(cdom => {
                //                             cdom.style.display = 'none'
                //                         })
                //                     }
                //                 }
                //             }
                //         })
                //     }
                //     if (type === 'callback') {
                //         node.cacheId = node.id // 选择打回节点前缓存id
                //         node.id = node.callbackData ? node.callbackData.id : node.id
                //     }
                // }
                // if (this.curSelectId === node.id) {
                //     // 画布节点参数入口 子流程选中状态可点击
                //     if (node.type === 'SubProcess') {
                //         this.cacheSubflowSelectNode[this.curSelectTreeId] = tools.deepClone(this.treeData)
                //         // this.$emit('onNodeClick', node.id, 'subflow')
                //         this.renderSubProcessData(node)
                //         return
                //     }
                //     // 当打回节点选中时，还原该条件id
                //     node.id = node.cacheId ? node.cacheId : node.id
                //     return
                // }
                // this.curSelectId = node.id
                const nodeType = node.type === 'ServiceActivity' ? 'tasknode' : (node.type === 'SubProcess' ? 'subflow' : 'controlNode')
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
                // const parentIds = this.nodeNav.slice(1).map(item => item.id).toString().split(',').join('.')
                // 最外层网关为null时传递id
                nodeHeirarchy = node.parent ? nodeHeirarchy.split('.').reverse()[0] + '.' + node.id : node.id
                this.setDefaultActiveId(this.treeData, this.treeData, node.id)
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
.bk-tree .tree-drag-node {
    line-height: 36px;
}
</style>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.finished {
    background-color: #e5f6ea !important;
    border: 1px solid #3fc06d !important;
}
.failed {
    background-color: #ecbbb7 !important;
    border: 1px solid #ecbbb7 !important;
}
.wait {
    background-color: #e0e1e9 !important;
    border: 1px solid #e0e1e9 !important;
}
.running {
    background-color: #7ea2f0 !important;
    border: 1px solid #4d83f7 !important;
}
.skip {
    background-color: #f8c4c1 !important;
    border: 1px solid #da635f !important;
}
.conver {
    margin-left: -20px;
    background: #fff;
    position: relative;
    z-index: 99;
}
.node-tree-wrapper {
    display: inline-block;
    width: 237px;
    // min-width: 229px;
    padding: 8px;
    height: 100%;
    white-space: nowrap;
    overflow-x: auto;
    @include scrollbar;
}
.tree-item {
    position: relative;
    min-height: 28px;
    margin: 9px 0;
    font-size: 14px;
    color: #63656E;
    line-height: 28px;
    .tree-item-info {
        
        display: flex;
        align-items: center;
       
        .tree-item-status {
            display: flex;
            align-items: center;
            width: 36px;
            height: 16px;
            position: relative;
            .tree-item-expanded {
                width: 14px;
                height: 14px;
                cursor: pointer;
            }
            .default-node {
                line-height: 28px;
                display: block;
                width: 8px;
                height: 8px;
                background: #E5F6EA;
                border: 1px solid #3FC06D;
                border-radius: 4px;
                margin: 0 4px;
                
            }
        }
        
        .tree-item-name {
            width: 160px;
            max-width: 100px;
            height: 28px;
            cursor: pointer;
            user-select: none;
        }
        .tree-line {
            display: inline-block;
            position: relative;
            width: 1px;
            height: 16px;
            ::before {
                content: "";
                position: absolute;
                border-width: 1px;
                border-left: 1px dashed #c3cdd7;
            }
        }
    }
    .tree-item-children {
        // width: 100px;
        min-height: 28px;
        // background-color: #3FC06D;
    }
    .gateway {
        height: 20px;
        background: #FBF9E2;
        border: 1px solid #CCC79E;
        border-radius: 1px;
        width: 100px;
        &::after {
            content: '';
            width: 1px;
            height: 10px;
            position: absolute;
            right: auto;
            border-width: 1px;
            border-left: 1px dashed #c3cdd7;
            bottom: 50px;
            top: -14px;
            left: 7px;
        }
        .tree-item-status {
            width: 16px;
        }
    }
}
.active-name {
    color: #3a84ff !important;
}
.is-node-active {
    color: #3a84ff !important;
    font-size: 14px;
    padding: 0 4px;
    cursor: pointer;
    user-select: none;
}
.activity-node {
    display: inline-block;
    border: 2px solid #81d79f;
    width: 8px;
    height: 8px;
    margin: 0 4px;
    border-radius: 4px;
    background: #e5f6ea;
    user-select: none;
}
.callback-condition {
    font-size: 10px;
    background: #FBF9E2;
    border: 1px solid #CCC79E;
    border-radius: 1px;
    color: #968E4D;
    position: relative;
    padding:0 4px;
    cursor: pointer;
    margin-left: -20px;
    z-index: 999;
    user-select: none;
    .callback {
        display: inline-block;
        height: 17px;
        width: 17px;
        line-height: 20px;
        padding: 0px 0px;
        color: #c0c4cc;
    }
}
.condition {
    font-size: 10px;
    background: #FBF9E2;
    border: 1px solid #CCC79E;
    border-radius: 1px;
    color: #968E4D;
    position: relative;
    padding-right: 4px;
    cursor: pointer;
    user-select: none;
    left: -20px;
    padding-left: 20px;
    z-index: 88;
    .callback {
        display: none;
    }
}
.default-conditon {
    font-size: 10px;
    background: #F0F1F5;
    border: 1px solid #C4C6CC;
    border-radius: 1px;
    color: #968E4D;
    position: relative;
    padding-right: 4px;
    user-select: none;
    left: -20px;
    padding-left: 20px;
    z-index: 88;
    .callback {
        display: none;
    }
}
.tpl-gateway {
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
.default-tpl-node {
    font-size: 14px;
    padding: 0 4px;
    cursor: pointer;
    user-select: none;
}
</style>
