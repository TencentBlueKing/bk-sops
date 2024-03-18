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
        <NodeTreeItem
            :active-id="activeId"
            :node-list="nodeData"
            @dynamicLoad="handleDynamicLoad"
            @click="handleClickNode">
        </NodeTreeItem>
    </div>
</template>
<script>

    import NodeTreeItem from './components/NodeTreeItem'
    import tools from '@/utils/tools.js'
    import { NODE_DICT } from '@/constants/index.js'
    import { mapActions } from 'vuex'

    export default {
        name: 'NodeTree',
        components: {
            NodeTreeItem
        },
        props: {
            instanceFlow: {
                type: String,
                required: true
            },
            defaultActiveId: {
                type: String,
                default: ''
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            nodeStateMapping: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            loading: {
                type: Boolean,
                default: true
            }
        },
        data () {
            const pipelineData = JSON.parse(this.instanceFlow)
            return {
                nodeData: [],
                pipelineData,
                activeId: this.defaultActiveId,
                nodeIds: {},
                convergeInfo: {},
                nodeSourceMaps: {},
                nodeTargetMaps: {},
                allCheckoutNodes: [],
                subprocessLoading: false,
                subNodesExpanded: [] // 节点树展开的独立子流程节点
            }
        },
        watch: {
            defaultActiveId: {
                handler (val) {
                    if (!val) return
                    this.activeId = val
                    let nodeId = val.split('-')[0]
                    let parentId = []
                    // 分支条件默认选中特殊处理
                    if (val.match('condition')) {
                        // 小画布默认id会携带parentId
                        const nodes = val.split('-').slice(0, -1)
                        nodeId = nodes.slice(0, 2).join('-')
                        this.activeId = nodes.join('-')
                        parentId = nodes.slice(2)
                    }
                    // 根据父节点过滤节点树
                    this.getNodeData()
                    let nodes = this.nodeData
                    parentId = parentId.length ? parentId : val.split('-').slice(1)
                    if (parentId.length) {
                        parentId.forEach(id => {
                            nodes.some(item => {
                                if (item.id === id) {
                                    nodes = item.children
                                    return true
                                }
                            })
                        })
                    }
                    this.setDefaultActiveId(nodes, nodeId)
                },
                immediate: true
            },
            loading: {
                // 当节点详情加载完毕后，这时则需处理子流程节点的信息
                async handler (val) {
                    if (val) return
                    const { root_node, node_id, component_code } = this.nodeDetailConfig
                    if (this.executeInfo && component_code === 'subprocess_plugin') {
                        const taskInfo = this.executeInfo.outputs.find(item => item.key === 'task_id') || {}
                        const taskId = taskInfo.value
                        const nodeInfo = this.getNodeInfo(this.nodeData, root_node, node_id)
                        // 如果子流程任务已执行，获取详情和状态
                        if (taskId) {
                            try {
                                this.subprocessLoading = true
                                // 获取子流程任务详情
                                await this.getSubprocessData(taskId, nodeInfo, true)
                                this.$emit('updateSubprocessState', {
                                    root_node,
                                    node_id,
                                    taskId
                                })
                            } catch (error) {
                                console.warn(error)
                            }
                        } else {
                            nodeInfo.dynamicLoad = false
                            this.subprocessLoading = false
                            this.setSubNodeExpanded(nodeInfo)
                        }
                    }
                },
                deep: true
            },
            nodeStateMapping: {
                handler (val) {
                    if (!val) return
                    // 设置节点树状态
                    this.getNodeData()
                    this.nodeAddStatus(this.nodeData, val)
                },
                deep: true,
                immediate: true
            },
            subprocessLoading: {
                handler (val) {
                    this.$emit('updateSubprocessLoading', val)
                },
                immediate: true
            }
        },
        methods: {
            ...mapActions('task/', [
                'getTaskInstanceData'
            ]),
            getNodeData () {
                if (this.nodeData.length) return
                this.nodeData = this.getOrderedTree(this.pipelineData)
            },
            getOrderedTree (data, pipelineInfo = {}) {
                const startNode = tools.deepClone(data.start_event)
                const endNode = tools.deepClone(data.end_event)
                const fstLine = startNode.outgoing
                const nodeId = data.flows[fstLine].target
                const { parentId, independentId, parentLevel, lastLevelStyle, taskId } = pipelineInfo
                let marginLeft
                if (lastLevelStyle) {
                    marginLeft = lastLevelStyle.match(/[0-9]+/g)[0]
                    marginLeft = Number(marginLeft)
                    marginLeft = marginLeft + 42
                } else {
                    marginLeft = 0
                }
                let subprocessStack
                if (parentId) {
                    subprocessStack = independentId ? parentId.split(independentId)[1] : parentId
                    subprocessStack = subprocessStack?.split('-') || []
                    subprocessStack = subprocessStack.filter(item => item)
                }
                const orderedData = [Object.assign({}, startNode, {
                    title: this.$t('开始节点'),
                    name: this.$t('开始节点'),
                    nodeLevel: 1,
                    parentId,
                    subprocessStack,
                    expanded: false,
                    taskId,
                    style: `margin-left: ${marginLeft}px`
                })]
                const endEvent = Object.assign({}, endNode, {
                    title: this.$t('结束节点'),
                    name: this.$t('结束节点'),
                    nodeLevel: 1,
                    parentId,
                    subprocessStack,
                    expanded: false,
                    taskId,
                    style: `margin-left: ${marginLeft}px`
                })
                this.getNodeTargetMaps(data)
                this.getNodeSourceMaps(data)
                const nodeInfo = { id: nodeId, parentId, independentId, parentLevel, lastLevelStyle, taskId }
                this.retrieveLines(data.id, data, nodeInfo, orderedData)
                orderedData.push(endEvent)
                // 过滤root最上层汇聚网关
                return orderedData
            },
            /**
             * 根据节点连线遍历任务节点，返回按广度优先排序的节点数据
             * @param {String} flowId 画布id
             * @param {Object} data 画布数据
             * @param {Object} nodeInfo 节点属性
             * @param {Array} ordered 排序后的节点数据
             * @param {Array} parentOrdered 父级排序
             *
             */
            retrieveLines (flowId, data, nodeInfo, ordered, parentOrdered) {
                const {
                    id,
                    gatewayId,
                    branchId,
                    nodeLevel = 1,
                    parentId,
                    independentId,
                    parentLevel,
                    lastLevelStyle,
                    lastId,
                    taskId,
                    isLevelUp,
                    style
                } = nodeInfo
                const { activities, gateways, flows } = data
                const nodeConfig = activities[id] || gateways[id]
                if (this.nodeIds[flowId] && this.nodeIds[flowId].includes(id)) {
                    const isBack = this.judgeNodeBack(id, id, [])
                    if (isBack) { // 打回节点
                        const lastNode = this.getMatchOrderedNode(ordered, lastId, false)
                        const existNode = this.getMatchOrderedNode(ordered, id, false)
                        lastNode.isCallback = true
                        lastNode.callbackInfo = {
                            ...existNode,
                            children: []
                        }
                    } else {
                        const isConverge = Object.values(this.convergeInfo).find(item => item.convergeNode === id)
                        if (isConverge) { // 网关汇聚
                            return
                        } else { // 分支汇聚
                            const existNode = this.getMatchOrderedNode(ordered, id, false)
                            const isSameLevel = existNode && existNode.nodeLevel === nodeLevel
                            if (isSameLevel) { // 同层次汇聚
                                const gatewayOrdered = this.getMatchOrderedNode(ordered, gatewayId, false)
                                const convergeIndex = gatewayOrdered.children.findIndex(item => item.id === id)
                                const branchIndex = gatewayOrdered.children.findIndex(item => item.id === branchId)
                                const branchInfo = gatewayOrdered.children.splice(branchIndex, 1)
                                gatewayOrdered.children.splice(convergeIndex, 0, branchInfo[0])
                            } else if (existNode) { // 跨层级汇聚
                                const lastNode = this.getMatchOrderedNode(ordered, lastId, false)
                                parentOrdered.push({
                                    ...existNode,
                                    isLevelUp: lastNode.isLevelUp,
                                    style: lastNode.style,
                                    isDifferLevelConverge: true,
                                    children: []
                                })
                            }
                        }
                    }
                    return
                }
                if (nodeConfig) {
                    const targetNodes = this.nodeTargetMaps[id]
                    const taskAndGwNodeMap = Object.assign({}, activities, gateways)
                    const treeItem = {
                        id: id,
                        type: nodeConfig.type,
                        parentId,
                        expanded: false,
                        nodeLevel: parentLevel ? parentLevel + nodeLevel : nodeLevel,
                        isLevelUp,
                        taskId
                    }
                    if (parentId) {
                        let subprocessStack = independentId ? parentId.split(independentId)[1] : parentId
                        subprocessStack = subprocessStack?.split('-') || []
                        treeItem.subprocessStack = subprocessStack.filter(item => item)
                    }
                    let marginLeft = 0
                    if (treeItem.nodeLevel === 1) {
                        marginLeft = 0
                    } else if (lastLevelStyle) {
                        marginLeft = lastLevelStyle.match(/[0-9]+/g)[0]
                        marginLeft = Number(marginLeft)
                        if (treeItem.parentId) {
                            marginLeft = marginLeft + 42
                        } else {
                            marginLeft = marginLeft + 33
                        }
                    }
                    treeItem.style = style || `margin-left: ${marginLeft}px`
                    let conditions = []

                    if (id in gateways) { // 网关节点
                        const name = NODE_DICT[nodeConfig.type.toLowerCase()]
                        treeItem.title = name
                        treeItem.name = name
                        treeItem.isGateway = true
                        treeItem.children = []
                        // 分支，条件并行
                        if (['ExclusiveGateway', 'ConditionalParallelGateway'].includes(nodeConfig.type)) {
                            treeItem.gatewayId = parentOrdered ? gatewayId : id
                            this.getGatewayConvergeNodes({
                                id,
                                parentId: id,
                                convergeInfo: this.convergeInfo
                            })
                            const loopList = [] // 需要打回的node的incoming
                            targetNodes.forEach(item => {
                                const curNode = taskAndGwNodeMap[item]
                                if (curNode && this.nodeIds[flowId]?.find(ite => ite === curNode.id)) {
                                    loopList.push(...curNode.incoming)
                                }
                            })
                            conditions = Object.keys(nodeConfig.conditions).map((key, index) => {
                                const { name: branchName, evaluate } = nodeConfig.conditions[key]
                                return {
                                    id: id + '-' + key,
                                    name: branchName,
                                    title: branchName,
                                    value: evaluate,
                                    nodeLevel: treeItem.nodeLevel + 1,
                                    parentId,
                                    conditionType: 'condition', // 条件、条件并行网关
                                    expanded: false,
                                    target: flows[key].target,
                                    gatewayId: id,
                                    children: [],
                                    taskId
                                }
                            })
                            // 添加条件分支默认节点
                            if (nodeConfig.default_condition) {
                                const { name: branchName, flow_id, evaluate } = nodeConfig.default_condition
                                // 默认条件置顶
                                conditions.unshift({
                                    id: id + '-' + flow_id,
                                    name: branchName,
                                    title: branchName,
                                    value: evaluate,
                                    nodeLevel: treeItem.nodeLevel + 1,
                                    parentId,
                                    conditionType: 'default',
                                    expanded: false,
                                    target: flows[flow_id].target,
                                    gatewayId: id,
                                    children: [],
                                    taskId
                                })
                            }
                        } else if (nodeConfig.type === 'ParallelGateway') {
                            treeItem.gatewayId = gatewayId || id
                            this.getGatewayConvergeNodes({
                                id,
                                parentId: id,
                                convergeInfo: this.convergeInfo
                            })
                            // 添加并行默认条件
                            conditions = nodeConfig.outgoing.map((key, index) => {
                                const branchName = this.$t('并行') + (index + 1)
                                return {
                                    id: branchName + '-' + id,
                                    name,
                                    title: this.$t('并行'),
                                    nodeLevel: treeItem.nodeLevel + 1,
                                    parentId,
                                    expanded: false,
                                    conditionType: 'parallel',
                                    target: flows[key].target,
                                    gatewayId: id,
                                    children: [],
                                    taskId
                                }
                            })
                            if (this.nodeIds[flowId]) {
                                this.nodeIds[flowId].push(id)
                            } else {
                                this.nodeIds[flowId] = [id]
                            }
                        }
                    } else { // 任务节点
                        if (nodeConfig.type === 'SubProcess' || nodeConfig.component.code === 'subprocess_plugin') {
                            const parentInfo = {
                                parentId: parentId ? parentId + '-' + id : id,
                                parentLevel: nodeLevel,
                                lastLevelStyle: 'margin-left: 0px'
                            }
                            // 兼容旧数据
                            if (nodeConfig.pipeline) {
                                this.getNodeTargetMaps(nodeConfig.pipeline)
                                this.getNodeSourceMaps(nodeConfig.pipeline)
                                treeItem.children = this.getOrderedTree(nodeConfig.pipeline, parentInfo)
                            } else {
                                let { data: componentData } = nodeConfig.component
                                componentData = componentData && componentData.subprocess
                                componentData = componentData && componentData.value
                                componentData = componentData && componentData.pipeline
                                if (componentData) {
                                    this.getNodeTargetMaps(componentData)
                                    this.getNodeSourceMaps(componentData)
                                    if (this.nodeIds[componentData.id]) {
                                        delete this.nodeIds[componentData.id]
                                    }
                                    parentInfo.independentId = id
                                    treeItem.children = this.getOrderedTree(componentData, parentInfo)
                                }
                                treeItem.type = 'SubProcess'
                                treeItem.dynamicLoad = true
                            }
                            treeItem.isSubProcess = true
                        }
                        treeItem.gatewayId = gatewayId
                        treeItem.name = nodeConfig.name
                        treeItem.title = nodeConfig.name
                    }
                    if (this.nodeIds[flowId]) {
                        this.nodeIds[flowId].push(id)
                    } else {
                        this.nodeIds[flowId] = [id]
                    }
                    const nextNodeInfo = { ...nodeInfo }
                    let newOrdered = parentOrdered
                    if (parentOrdered) {
                        if (nodeConfig.incoming.length > 1) {
                            let result
                            const convergeNode = Object.values(this.convergeInfo).find(item => item.convergeNode === id)
                            if (convergeNode) {
                                result = this.getMatchOrderedNode(ordered, convergeNode.id, true)
                                const gatewayInfo = this.getMatchOrderedNode(ordered, convergeNode.id, false)
                                const { gatewayId, nodeLevel } = result[0]
                                treeItem.nodeLevel = nodeLevel
                                treeItem.style = gatewayInfo.style
                                treeItem.isLevelUp = gatewayInfo.isLevelUp
                                // 添加同级的汇聚网关标识
                                if (gateways[id]?.type === 'ConvergeGateway') {
                                    gatewayInfo.hasConvergeGW = true
                                }
                                result.push(treeItem)
                                newOrdered = result
                                nextNodeInfo.gatewayId = gatewayId
                                nextNodeInfo.nodeLevel = nodeLevel
                                nextNodeInfo.isLevelUp = treeItem.isLevelUp
                                nextNodeInfo.style = treeItem.style
                            } else {
                                result = this.getMatchOrderedNode(ordered, gatewayId, false)
                                if (result) {
                                    treeItem.nodeLevel = result.children[0].nodeLevel
                                    treeItem.style = result.children[0].style
                                    treeItem.isLevelUp = true
                                    result.children.push(treeItem)
                                    newOrdered = result.children
                                    nextNodeInfo.gatewayId = result.gatewayId
                                    nextNodeInfo.nodeLevel = treeItem.nodeLevel
                                    nextNodeInfo.isLevelUp = true
                                    nextNodeInfo.style = treeItem.style
                                } else {
                                    parentOrdered.push(treeItem)
                                }
                            }
                            // 汇聚节点层级会提高
                            if (treeItem.nodeLevel === 1 && !parentId) {
                                treeItem.style = 'margin-left: 0px'
                            }
                        } else {
                            parentOrdered.push(treeItem)
                        }
                    } else {
                        ordered.push(treeItem)
                        newOrdered = null
                    }

                    if (conditions.length) {
                        conditions.forEach(item => {
                            item.style = `margin-left: ${item.parentId ? 16 : marginLeft + 33}px`
                            item.subprocessStack = treeItem.subprocessStack
                            treeItem.children.push(item)
                            this.retrieveLines(
                                flowId,
                                data,
                                {
                                    id: item.target,
                                    branchId: item.id,
                                    nodeLevel: item.nodeLevel,
                                    parentId,
                                    independentId,
                                    gatewayId: id,
                                    lastId: item.id,
                                    taskId
                                },
                                ordered,
                                item.children
                            )
                        })
                    } else {
                        targetNodes.forEach(node => {
                            this.retrieveLines(
                                flowId,
                                data,
                                {
                                    ...nextNodeInfo,
                                    id: node,
                                    lastId: id
                                },
                                ordered,
                                newOrdered
                            )
                        })
                    }
                }
            },
            getMatchOrderedNode (ordered, id, isParent) {
                let result
                ordered.some(item => {
                    if (item.id === id) {
                        result = isParent ? ordered : item
                        return true
                    } else if (item.children?.length) {
                        result = this.getMatchOrderedNode(item.children, id, isParent)
                        return result && !!Object.keys(result).length
                    }
                    return false
                })
                return result
            },

            getNodeSourceMaps (pipelineData) {
                const sourceMap = pipelineData.line.reduce((acc, cur) => {
                    const { source, target } = cur
                    if (acc[target.id]) {
                        acc[target.id].push(source.id)
                    } else {
                        acc[target.id] = [source.id]
                    }
                    return acc
                }, {})
                Object.assign(this.nodeSourceMaps, sourceMap)
            },
            getNodeTargetMaps (pipelineData) {
                const targetMap = pipelineData.line.reduce((acc, cur) => {
                    const { source, target } = cur
                    if (acc[source.id]) {
                        acc[source.id].push(target.id)
                    } else {
                        acc[source.id] = [target.id]
                    }
                    return acc
                }, {})
                Object.assign(this.nodeTargetMaps, targetMap)
            },
            /**
             * id: 当前查找的id
             * parentId: 最外层的网关id
             * convergeInfo: { 汇聚详情
             *    id: '', 网关节点
             *    checkedNodes: [], 已经查找过的节点
             *    convergeNode: '', 最终汇聚的节点
             *    branchCount: 1 总共有多少条分支
             * }
             * index: 当前节点属于哪条分支下的
             * isDeep: 是否递归
            */
            getGatewayConvergeNodes (data) {
                const {
                    id,
                    parentId,
                    convergeInfo = {},
                    index,
                    isDeep,
                    isLastBranch
                } = data
                if (!id) return
                if (!convergeInfo[parentId]) {
                    convergeInfo[parentId] = {
                        id: parentId,
                        checkedNodes: [],
                        convergeNode: '',
                        branchCount: 1 // 默认是一条分支
                    }
                }
                // 如果该节点的查找次数大于输入连线的数量则退出递归
                if (this.allCheckoutNodes[parentId]) {
                    this.allCheckoutNodes[parentId].push(id)
                } else {
                    this.allCheckoutNodes[parentId] = [id]
                }
                const checkedCount = this.allCheckoutNodes[parentId].filter(item => item === id).length
                const sourceCount = this.nodeSourceMaps[id].length
                if (checkedCount > sourceCount) return

                const targetNodes = this.nodeTargetMaps[id] || []
                // 多条输出分支
                if (targetNodes.length > 1) {
                    if (!convergeInfo[id]) {
                        const subConvergeInfo = {}
                        this.getGatewayConvergeNodes({
                            id: id,
                            parentId: id,
                            convergeInfo: subConvergeInfo
                        })
                        const { convergeNode: subConvergeNodes } = subConvergeInfo[id]
                        convergeInfo[parentId].checkedNodes.push(subConvergeNodes)
                        const branchConvergeNode = convergeInfo[parentId][`branch${index}`]
                        if (!branchConvergeNode) {
                            convergeInfo[parentId][`branch${index}`] = [subConvergeNodes]
                        } else if (!branchConvergeNode.includes(subConvergeNodes)) {
                            branchConvergeNode.push(subConvergeNodes)
                        }
                        // 如果是最后一条分支，则需要判断是否找到最终汇聚节点
                        if (isLastBranch) {
                            this.getGatewayConvergeNodes({
                                id: this.pipelineData.end_event.id,
                                parentId,
                                convergeInfo,
                                index,
                                isDeep,
                                isLastBranch
                            })
                        }
                        return
                    }
                    convergeInfo[parentId].branchCount = targetNodes.length
                    targetNodes.forEach((targetId, branchIndex) => {
                        // 非递归时使用传入的分支数
                        const newIndex = isDeep ? index : branchIndex
                        this.getGatewayConvergeNodes({
                            id: targetId,
                            parentId,
                            convergeInfo,
                            index: newIndex,
                            isDeep,
                            isLastBranch: branchIndex === targetNodes.length - 1
                        })
                    })
                } else {
                    // 单条输出分支
                    const { checkedNodes, branchCount = 0 } = convergeInfo[parentId]
                    const countArr = [...Array(branchCount).keys()]
                    const { end_event } = this.pipelineData
                    // 已查找过的节点、结束节点、汇聚节点
                    if ([...checkedNodes, end_event.id].includes(id) || this.nodeSourceMaps[id].length > 1) {
                        // 记录分支下的汇聚节点
                        const branchConvergeNode = convergeInfo[parentId][`branch${index}`]
                        if (!branchConvergeNode) {
                            convergeInfo[parentId][`branch${index}`] = [id]
                        } else if (!branchConvergeNode.includes(id)) {
                            branchConvergeNode.push(id)
                        }
                        // 记录查找过的节点
                        if (!checkedNodes.includes(id)) {
                            checkedNodes.push(id)
                        }
                        // 所有分支下的汇聚节点
                        const convergeNodes = countArr.map(item => {
                            const data = convergeInfo[parentId][`branch${item}`] || []
                            return [...new Set(data)]
                        }).flat()
                        // 如果重复出现汇聚节点的最大次数等于分支数则表示已经找到最终的汇聚节点了
                        const countMap = this.getCountMap(convergeNodes)
                        const matchNode = Object.keys(countMap).filter(key => countMap[key] === branchCount)
                        if (matchNode[0]) {
                            convergeInfo[parentId].convergeNode = matchNode[0]
                        } else if (index === branchCount - 1 && (isDeep ? isLastBranch : true)) { // 最后一条分支
                            // 没找到汇聚节点则继续向下递归
                            if (!convergeInfo[parentId].convergeNode) {
                                countArr.forEach(idx => {
                                    // 根据各条分支最后的汇聚节点继续查找
                                    const data = convergeInfo[parentId][`branch${idx}`] || []
                                    const [lastId] = data.slice(-1)
                                    const targetIds = this.nodeTargetMaps[lastId] || [lastId]
                                    // 向下递归
                                    targetIds.forEach(targetId => {
                                        this.getGatewayConvergeNodes({
                                            id: targetId,
                                            parentId,
                                            convergeInfo,
                                            index: idx,
                                            isDeep: true,
                                            isLastBranch: idx === countArr.length - 1
                                        })
                                    })
                                })
                            }
                        }
                    } else {
                        checkedNodes.push(id)
                        const targetId = targetNodes[0]
                        this.getGatewayConvergeNodes({
                            id: targetId,
                            parentId,
                            convergeInfo,
                            index,
                            isDeep,
                            isLastBranch
                        })
                    }
                }
            },
            getCountMap (arr) {
                if (!arr.length) return {}
                const countMap = arr.reduce((acc, cur) => {
                    acc[cur] ? acc[cur] += 1 : acc[cur] = 1
                    return acc
                }, {})
                return countMap
            },
            judgeNodeBack (id, backId, checked) {
                if (checked.includes(id)) return id === backId
                const targetNodes = this.nodeTargetMaps[id]
                if (!targetNodes) return false
                checked.push(id)
                if (targetNodes.length > 1) {
                    if (targetNodes.includes(backId)) {
                        return true
                    }
                    return targetNodes.some(targetId => {
                        return this.judgeNodeBack(targetId, backId, checked)
                    })
                } else {
                    const targetId = targetNodes[0]
                    if (targetId === backId) {
                        return true
                    } else {
                        return this.judgeNodeBack(targetId, backId, checked)
                    }
                }
            },
            // 获取独立子流程节点详情
            async getSubprocessData (taskId, nodeInfo, updateState) {
                try {
                    const parentId = nodeInfo.parentId?.split('-') || []
                    if (nodeInfo.dynamicLoad || updateState) {
                        this.suspendLines = []
                        const resp = await this.getTaskInstanceData(taskId)
                        const pipelineTree = JSON.parse(resp.pipeline_tree)
                        const parentInfo = {
                            parentId: nodeInfo.parentId ? nodeInfo.parentId + '-' + nodeInfo.id : nodeInfo.id,
                            independentId: nodeInfo.id,
                            parentLevel: nodeInfo.nodeLevel,
                            lastLevelStyle: 'margin-left: 0px',
                            taskId
                        }
                        this.nodeIds[pipelineTree.id] = []
                        nodeInfo.children = this.getOrderedTree(pipelineTree, parentInfo)
                        nodeInfo.dynamicLoad = false
                        nodeInfo.expanded = true

                        this.$emit('updateParentPipelineData', {
                            parentId,
                            nodeId: nodeInfo.id,
                            pipeline: { ...pipelineTree, taskId }
                        })
                        // 如果当前选中的节点是子流程下的节点，且是子流程未执行时选中的，那么当节点树变更时默认选中该子流程
                        if (this.executeInfo.state === 'READY' && this.nodeDetailConfig.root_node?.indexOf(nodeInfo.id) > -1) {
                            this.handleClickNode(nodeInfo)
                        }
                    }
                } catch (error) {
                    console.warn(error)
                    this.subprocessLoading = false
                }
            },
            // 设置节点树状态
            nodeAddStatus (treeData = [], states) {
                treeData.forEach(node => {
                    const { id, conditionType, children = [] } = node
                    if (conditionType) {
                        if (children.length) {
                            this.nodeAddStatus(children, states)
                        }
                        return
                    }
                    if (!states[id]) {
                        this.$set(node, 'state', '')
                        return
                    }
                    const nodeState = states[id].skip ? 'SKIP' : states[id].state
                    this.$set(node, 'state', nodeState)
                    const index = this.subNodesExpanded.findIndex(item => item === node.id)
                    if (index > -1) {
                        this.subNodesExpanded.splice(index, 1)
                        this.handleDynamicLoad(node, true)
                    }
                    if (children.length) {
                        this.nodeAddStatus(children, states)
                    }
                })
            },
            // 只点击子流程展开/收起
            async handleDynamicLoad (node, updateState) {
                try {
                    // 检查是否需要更新子流程状态
                    if (!updateState) {
                        // 如果节点未动态加载、已收起或未执行，则不进行更新
                        if (!node.dynamicLoad || !node.expanded || !node.state) {
                            if (!node.state) {
                                // 子流程任务未执行，更新节点状态并记录
                                node.dynamicLoad = false
                                this.subprocessLoading = false
                                this.setSubNodeExpanded(node)
                            }
                            return
                        }
                    }
                    const { instance_id } = this.$route.query
                    // 该独立子流程节点的父流程也可能为独立子流程
                    const nodeDetailConfig = this.getNodeDetailConfig(node, node.taskId || instance_id)
                    const parentInstance = this.$parent.$parent
                    const nodeConfig = await parentInstance.getTaskNodeDetail(nodeDetailConfig)
                    if (!nodeConfig) return

                    // 获取子流程任务id
                    const taskInfo = nodeConfig.outputs.find(item => item.key === 'task_id') || {}
                    this.subprocessLoading = false
                    // 更新子流程树
                    const taskId = taskInfo.value
                    if (taskId) {
                        await this.getSubprocessData(taskId, node, updateState)
                        this.$emit('updateSubprocessState', {
                            root_node: node.parentId,
                            node_id: node.id,
                            taskId
                        })
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            // 获取节点配置
            getNodeDetailConfig (node, instance_id) {
                const { id, parentId, taskId } = node
                let pipelineData = this.pipelineData
                if (parentId) {
                    parentId.split('-').forEach(item => {
                        const nodeData = pipelineData.activities[item]
                        pipelineData = nodeData.pipeline || nodeData.component.data?.subprocess?.value?.pipeline || pipelineData
                    })
                }
                let code, version, componentData
                const nodeInfo = pipelineData.activities[id]
                if (nodeInfo) {
                    componentData = nodeInfo.component.data
                    code = nodeInfo.component.code
                    version = nodeInfo.component.version || 'legacy'
                }
                const subprocessStack = parentId && !taskId ? parentId.split('-') : []
                return {
                    component_code: code,
                    version: version,
                    node_id: id,
                    instance_id,
                    root_node: parentId,
                    subprocess_stack: JSON.stringify(subprocessStack),
                    componentData
                }
            },
            // 记录独立子流程展开收起
            setSubNodeExpanded (node) {
                // 子任务展开收起
                if (node.expanded) { // 记录展开的子流程id
                    if (!this.subNodesExpanded.includes(node.id)) {
                        this.subNodesExpanded.push(node.id)
                    }
                } else {
                    const index = this.subNodesExpanded.findIndex(item => item === node.id)
                    if (index > -1) {
                        this.subNodesExpanded.splice(index, 1)
                    }
                }
            },
            // 获取节点树节点详情
            getNodeInfo (data, rootId, nodeId) {
                let nodes = data
                if (rootId) {
                    rootId.split('-').forEach(id => {
                        nodes.some(item => {
                            if (item.id === id) {
                                nodes = item.children
                                return true
                            }
                        })
                    })
                }
                let nodeInfo
                nodes.some(item => {
                    if (item.id === nodeId) {
                        nodeInfo = item
                        return true
                    } else if (item.children?.length) {
                        nodeInfo = this.getNodeInfo(item.children, '', nodeId)
                        return !!nodeInfo
                    }
                })
                return nodeInfo
            },
            handleClickNode (node) {
                this.activeId = node.parentId ? node.id + '-' + node.parentId : node.id
                this.$emit('onSelectNode', node)
            },
            setDefaultActiveId (treeData = [], id) {
                return treeData.some(item => {
                    if (item.id === id) {
                        item.expanded = !!item.isSubProcess || !!item.conditionType || item.isGateway
                        return true
                    } else if (item.children?.length) {
                        if (item.expanded) {
                            return this.setDefaultActiveId(item.children, id)
                        }
                        item.expanded = this.setDefaultActiveId(item.children, id)
                        return item.expanded
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.node-tree-wrapper {
    width: 100%;
    padding: 16px 16px 16px 8px;
    height: 100%;
    overflow-x: auto;
    @include scrollbar;
}
</style>
