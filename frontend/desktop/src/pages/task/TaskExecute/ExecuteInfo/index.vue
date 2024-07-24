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
    <div class="parameter-details">
        <bk-resize-layout class="details-wrapper" placement="left" :max="sidebarWidth - 600" :initial-divide="243" :min="240">
            <NodeTree
                slot="aside"
                ref="nodeTree"
                :loading="loading"
                :pipeline-data="pipelineData"
                :default-active-id="defaultActiveId"
                :execute-info="executeInfo"
                :node-state-mapping="nodeStateMapping"
                :node-detail-config="nodeDetailConfig"
                :subprocess-key="subprocessPipeline && subprocessPipeline.randomKey"
                @updateSubprocessLoading="subprocessLoading = $event"
                @updateParentPipelineData="updateParentPipelineData"
                @updateSubprocessState="updateSubprocessState"
                @onSelectNode="onSelectNode">
            </NodeTree>
            <div slot="main" class="execute-content">
                <div class="execute-head">
                    <span class="node-name">{{conditionData.name || nodeActivity.name}}</span>
                    <bk-divider direction="vertical"></bk-divider>
                    <div class="node-state">
                        <span :class="displayState"></span>
                        <span class="status-text-messages">{{ nodeStateText }}</span>
                    </div>
                </div>
                <div :class="['scroll-box', { 'subprocess-scroll': subprocessPipeline }]">
                    <NodeCanvas
                        v-if="subprocessPipeline"
                        ref="nodeCanvas"
                        :key="canvasRandomKey"
                        :loading="subprocessLoading"
                        :node-state-mapping="nodeStateMapping"
                        :subprocess-state="subprocessState"
                        :subprocess-pipeline="subprocessPipeline"
                        :subprocess-height="subprocessHeight"
                        @updateSubprocessHeight="subprocessHeight = $event"
                        @onNodeClick="handleSubCanvasNodeClick">
                    </NodeCanvas>
                    <NodeExecuteInfo
                        v-if="nodeActivity"
                        v-bkloading="{ isLoading: loading || executeInfoLoading, opacity: 1, zIndex: 100 }"
                        :key="executeInfoRandomKey"
                        :loading="loading"
                        :condition-data="conditionData"
                        :node-activity="nodeActivity"
                        :node-detail-config="nodeDetailConfig"
                        :pipeline-tree="nodePipelineData"
                        :not-performed-sub-node="notPerformedSubNode"
                        :execute-info="executeInfo"
                        :engine-ver="engineVer"
                        :node-state="nodeStateText"
                        :subprocess-pipeline="subprocessPipeline"
                        :real-time-state="realTimeState"
                        :auto-retry-info="autoRetryInfo"
                        @updateExecuteInfoLoading="executeInfoLoading = $event"
                        @onSelectExecuteTime="onSelectExecuteTime">
                    </NodeExecuteInfo>
                </div>
                <NodeAction
                    v-if="!loading && !executeInfoLoading"
                    :state="state"
                    :real-time-state="realTimeState"
                    :node-detail-config="nodeDetailConfig"
                    :node-state-mapping="nodeStateMapping"
                    :subprocess-tasks="subprocessTasks"
                    :subprocess-nodes-state="subprocessNodesState"
                    :pipeline-data="nodePipelineData"
                    :execute-info="executeInfo"
                    :subprocess-state="subprocessState"
                    :subprocess-pipeline="subprocessPipeline"
                    :auto-retry-info="autoRetryInfo"
                    @onRetryClick="onRetryClick"
                    @onSkipClick="onSkipClick"
                    @onResumeClick="onResumeClick"
                    @onApprovalClick="onApprovalClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onForceFail="onForceFail"
                    @onPauseClick="onPauseClick"
                    @onContinueClick="onContinueClick">
                </NodeAction>
            </div>
        </bk-resize-layout>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import axios from 'axios'
    import { TASK_STATE_DICT, NODE_DICT } from '@/constants/index.js'
    import NodeTree from './components/NodeTree/index.vue'
    import NodeCanvas from './components/NodeCanvas/index.vue'
    import NodeExecuteInfo from './components/NodeExecuteInfo/index.vue'
    import NodeAction from './components/NodeAction/index.vue'
    import lineSuspendState from '@/mixins/lineSuspendState.js'

    const CancelToken = axios.CancelToken
    let source = CancelToken.source()

    export default {
        name: 'ExecuteInfo',
        components: {
            NodeTree,
            NodeCanvas,
            NodeExecuteInfo,
            NodeAction
        },
        mixins: [lineSuspendState],
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            nodeDetailConfig: {
                type: Object,
                required: true
            },
            defaultActiveId: {
                type: String,
                default: ''
            },
            pipelineData: { // 最外层画布的流程树
                type: Object,
                default () {
                    return {}
                }
            },
            nodePipelineData: { // 当前节点所对应的流程树
                type: Object,
                default () {
                    return {}
                }
            },
            state: { // 总任务状态
                type: String,
                default: ''
            },
            engineVer: {
                type: Number,
                required: true
            },
            nodeDisplayStatus: {
                type: Object,
                required: true
            },
            conditionData: Object,
            sidebarWidth: Number
        },
        data () {
            return {
                canvasRandomKey: null,
                executeInfoRandomKey: null,
                subprocessHeight: 0,
                loading: true,
                executeInfo: {},
                theExecuteTime: undefined,
                timer: null,
                subprocessLoading: true,
                executeInfoLoading: true,
                subprocessTasks: {},
                subprocessNodesState: {},
                notPerformedSubNode: false // 是否为未执行的独立子流程节点
            }
        },
        computed: {
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            // 节点实时状态
            realTimeState () {
                const { node_id } = this.nodeDetailConfig
                if (node_id in this.nodeStateMapping) {
                    return this.nodeStateMapping[node_id]
                }
                return { state: 'READY' }
            },
            // 子任务状态
            subprocessState () {
                const { root_node, type, component_code } = this.nodeDetailConfig
                const { taskId } = this.subprocessPipeline || {}
                let state = 'READY'
                if (type === 'Subprocess') { // 非独立子流程节点
                    state = this.realTimeState.subprocess_state || state
                } else if (taskId) { // 独立子流程节点/独立子流程下的节点
                    state = this.subprocessNodesState[taskId]?.state || state
                } else if (root_node && component_code !== 'subprocess_plugin') { // 非独立子流程下的节点
                    const parentNode = root_node.split('-').slice(-1)[0]
                    state = this.nodeStateMapping[parentNode]?.subprocess_state || state
                }
                return state
            },
            displayState () {
                let state = ''
                switch (this.realTimeState.state) {
                    case 'RUNNING':
                        state = 'common-icon-dark-circle-ellipsis'
                        break
                    case 'SUSPENDED':
                        state = 'common-icon-dark-circle-pause'
                        break
                    case 'PENDING_PROCESSING':
                        state = 'common-icon-dark-circle-pending-process'
                        break
                    case 'PENDING_APPROVAL':
                        state = 'common-icon-dark-circle-pending-approval'
                        break
                    case 'PENDING_CONFIRMATION':
                        state = 'common-icon-dark-circle-pending-confirm'
                        break
                    case 'FINISHED':
                        const { skip, error_ignored } = this.realTimeState
                        state = skip ? 'common-icon-manual-skip' : 'bk-icon icon-check-circle-shape'
                        state = error_ignored ? 'common-icon-auto-skip' : state
                        break
                    case 'FAILED':
                        state = 'common-icon-dark-circle-close'
                        break
                    case 'CREATED':
                    case 'READY':
                        state = 'common-icon-waitting'
                        break
                }
                return state
            },
            nodeStateText () {
                // 如果整体任务未执行的话不展示描述
                if (this.state === 'CREATED') return i18n.t('未执行')
                // 如果整体任务执行完毕但有的节点没执行的话不展示描述
                if (['FAILED', 'FINISHED'].includes(this.state) && this.realTimeState.state === 'READY') return i18n.t('未执行')
                const { state, skip, error_ignored } = this.realTimeState
                return skip ? i18n.t('失败后手动跳过') : error_ignored ? i18n.t('失败后自动跳过') : state && TASK_STATE_DICT[state]
            },
            nodeActivity () {
                const { node_id: nodeId } = this.nodeDetailConfig
                const { activities, end_event, start_event, gateways } = this.nodePipelineData
                const nodeMap = {
                    ...activities,
                    ...Object.values(gateways).reduce((acc, cur) => {
                        acc[cur.id] = {
                            ...cur,
                            name: NODE_DICT[cur.type.toLowerCase()]
                        }
                        return acc
                    }, {}),
                    [start_event.id]: { ...start_event, name: this.$t('开始节点') },
                    [end_event.id]: { ...end_event, name: this.$t('结束节点') }
                }
                return nodeMap[nodeId]
            },
            subprocessPipeline () {
                let pipelineData
                const { type, component_code } = this.nodeDetailConfig
                if (component_code === 'subprocess_plugin' || type === 'SubProcess') {
                    if (this.nodeActivity.pipeline) {
                        pipelineData = this.nodeActivity.pipeline
                    } else {
                        const componentData = this.nodeActivity.component.data?.subprocess?.value?.pipeline
                        pipelineData = componentData || pipelineData
                    }
                } else if (this.nodeDetailConfig.root_node) {
                    pipelineData = this.nodePipelineData
                }
                return pipelineData
            },
            autoRetryInfo () {
                const { taskId, node_id } = this.nodeDetailConfig
                const retryInfos = taskId
                    ? this.subprocessNodesState[taskId].auto_retry_infos || {}
                    : this.nodeDisplayStatus.auto_retry_infos || {}
                const retryInfo = retryInfos[node_id] || {}
                return {
                    h: !!Object.keys(retryInfo).length,
                    m: retryInfo.auto_retry_times || 0,
                    c: retryInfo.max_auto_retry_times || 10,
                    n: this.realTimeState.retry - retryInfo.auto_retry_times || 0
                }
            },
            nodeStateMapping () {
                const stateMapping = {}
                const getNodeState = (states) => {
                    Object.values(states).forEach(item => {
                        stateMapping[item.id] = item
                        if (item.children && Object.keys(item.children).length) {
                            getNodeState(item.children)
                        }
                    })
                }
                getNodeState(this.nodeDisplayStatus.children)
                return {
                    ...stateMapping,
                    ...Object.values(this.subprocessNodesState).reduce((acc, cur) => {
                        const { auto_retry_infos: retryInfo = {}, children } = cur
                        Object.keys(retryInfo).forEach(key => {
                            children[key].retryInfo = retryInfo[key]
                        })
                        return {
                            ...acc,
                            ...children
                        }
                    }, {})
                }
            }
        },
        watch: {
            nodeDetailConfig: {
                handler (val) {
                    if (val.node_id !== undefined) {
                        this.theExecuteTime = undefined
                        // 节点切换时重新加载执行详情
                        this.executeInfoRandomKey = new Date().getTime()
                        // 未执行的独立子流程节点
                        if (this.notPerformedSubNode) {
                            this.loading = false
                            this.subprocessLoading = false
                            this.executeInfoLoading = false
                        } else {
                            this.executeInfo.state = ''
                            this.loadNodeInfo()
                        }
                    }
                },
                deep: true
            },
            realTimeState: {
                handler (val, oldVal) {
                    // 节点状态没变，重试次数变了，需要重新获取节点状态
                    const { state, retry } = val
                    const { state: oldState, retry: oldRetry } = oldVal
                    if (state === 'FAILED' && state === oldState && retry !== oldRetry) {
                        this.loadNodeInfo()
                    }

                    // 节点由READY态到执行态时需重新获取节点详情
                    if (oldState === 'READY' && state !== oldState) {
                        this.loadNodeInfo()
                    }
                },
                deep: true
            }
        },
        mounted () {
            this.loadNodeInfo()
        },
        beforeDestroy () {
            if (source) {
                source.cancel('cancelled')
            }
            this.cancelTaskStateTimer()
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActDetail',
                'getTaskInstanceData',
                'getBatchInstanceStatus'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeDetail'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    const respData = await this.getTaskNodeDetail()
                    if (!respData) return

                    this.executeInfo = this.adminView && this.engineVer === 1
                        ? { ...respData, ...respData.execution_info }
                        : respData
                } catch (e) {
                    this.executeInfo = {}
                    console.warn(e)
                } finally {
                    this.loading = false
                    this.subprocessLoading = false
                }
            },
            async getTaskNodeDetail (nodeConfig = this.nodeDetailConfig) {
                try {
                    let query = Object.assign({}, nodeConfig, { loop: this.theExecuteTime })
                    let res

                    // 非任务节点请求参数不传 component_code
                    if (!nodeConfig.component_code) {
                        delete query.component_code
                    }

                    if (this.adminView && this.engineVer === 1) {
                        const { instance_id: task_id, node_id, subprocess_stack } = nodeConfig
                        query = { task_id, node_id, subprocess_stack }
                        res = await this.taskflowNodeDetail(query)
                    } else {
                        query.subprocess_simple_inputs = true // 标记独立子流程取{key: value}类型数据
                        res = await this.getNodeActDetail(query)
                    }
                    if (res.result) {
                        return res.data
                    } else {
                        this.executeInfo = {}
                        this.subprocessLoading = false
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            // 子流程画布节点点击
            handleSubCanvasNodeClick (node) {
                const { node_id: nodeId, root_node: rootNode } = this.nodeDetailConfig
                let parentId = rootNode
                if (nodeId === this.subprocessPipeline.id) {
                    parentId = rootNode ? `${rootNode}-${nodeId}` : nodeId
                }
                const nodeInfo = this.getNodeInfo(parentId, node, 'canvas')
                if (nodeInfo) {
                    const parentInstance = this.$parent.$parent
                    parentInstance.defaultActiveId = ''
                    if (nodeInfo.conditionType) {
                        parentInstance.defaultActiveId = node + '-' + nodeInfo.parentId + '-condition'
                    } else {
                        parentInstance.defaultActiveId = node + '-' + nodeInfo.parentId
                    }
                    // 子流程节点选中时会切换画布，所以先设置节点树默认选中节点，再去加载节点详情
                    this.$nextTick(() => {
                        this.onSelectNode(nodeInfo)
                    })
                }
            },
            // 节点树节点点击
            onSelectNode (node) {
                this.loading = true
                // 如果子节点的父流程为独立任务且未执行时不调接口，默认数据为空
                this.notPerformedSubNode = false
                if (node.parentId && !node.state) {
                    const ids = node.parentId.split('-')
                    const rootId = ids.slice(0, -1).join('-')
                    // 获取父节点详情
                    const parentInfo = this.getNodeInfo(rootId, ids.pop())
                    if (parentInfo && !parentInfo.state && 'dynamicLoad' in parentInfo) {
                        node.dynamicLoad = false
                        this.notPerformedSubNode = true
                    }
                }
                // 子画布节点取消选中态
                if (this.subprocessPipeline) {
                    this.toggleNodeActive(this.nodeDetailConfig.node_id, false)
                }
                // 如果点击的是子流程节点或者是不属于当前所选中节点树的节点，需要重新刷新子流程画布
                let updateCanvas = false
                if (node.isSubProcess) {
                    updateCanvas = node.id !== this.nodeDetailConfig.node_id
                }
                if (!updateCanvas && node.parentId) {
                    const nodeId = node.conditionType ? node.id.split('-')[0] : node.id
                    if (this.subprocessPipeline) {
                        const { randomKey, location } = this.subprocessPipeline
                        updateCanvas = !location.find(item => item.id === nodeId && node.flowKey === randomKey)
                    } else {
                        updateCanvas = true
                    }
                }
                if (updateCanvas) {
                    this.canvasRandomKey = new Date().getTime()
                }
                this.$emit('onClickTreeNode', node)
                this.$nextTick(() => {
                    // 画布节点添加选中态
                    if (node.parentId) {
                        this.toggleNodeActive(node.id, true)
                    }
                    // 画布出屏节点挪到画布中央
                    if (node.parentId && !node.isSubProcess) {
                        this.moveNodeToView(node.id)
                    }
                    // 更新子流程画布状态
                    const nodeCanvas = this.$refs.nodeCanvas
                    nodeCanvas && nodeCanvas.updateNodeInfo(this.nodeStateMapping)
                })
            },
            // 移动画布，将节点放到画布中央
            moveNodeToView (id) {
                const nodeCanvas = this.$refs.nodeCanvas
                nodeCanvas && nodeCanvas.moveNodeToView(id)
            },
            // 子画布设置选中态
            toggleNodeActive (id, isActive) {
                const node = document.getElementById(id)
                if (!id || !node) return
                if (!isActive) {
                    node.classList.remove('active')
                } else {
                    node.classList.add('active')
                }
            },
            // 更新父级节点树
            updateParentPipelineData (data) {
                const { parentId, nodeId, pipeline, reset } = data
                const parentInstance = this.$parent.$parent
                let pipelineData = parentInstance.nodeTreePipelineData
                // 更新当前节点所对应的流程树
                if (reset) {
                    this.$set(parentInstance, 'nodePipelineData', { ...pipeline })
                    return
                }
                if (parentId) {
                    parentId.forEach(item => {
                        const nodeData = pipelineData.activities[item]
                        if (nodeData.pipeline) {
                            pipelineData = nodeData.pipeline
                        } else {
                            pipelineData = nodeData.component.data?.subprocess?.value?.pipeline || pipelineData
                        }
                    })
                }
                const nodeActivity = pipelineData.activities[nodeId]
                this.$set(nodeActivity, 'pipeline', pipeline)
                this.canvasRandomKey = new Date().getTime()
            },
            // 更新子任务状态
            updateSubprocessState (info) {
                const { root_node, node_id, taskId } = info
                this.subprocessTasks[taskId] = {
                    root_node,
                    node_id,
                    pollErrorTimes: 0
                }
                // 获取独立子流程任务状态
                this.loadSubprocessState()
            },
            // 获取节点树节点详情
            getNodeInfo (rootId, nodeId, eventSource) {
                let nodeInfo = null
                const nodeTreeRef = this.$refs.nodeTree
                if (nodeTreeRef) {
                    nodeInfo = nodeTreeRef.getNodeInfo(nodeTreeRef.nodeData, rootId, nodeId, eventSource)
                }
                return nodeInfo
            },
            async loadSubprocessState () {
                try {
                    if (source) {
                        source.cancel('cancelled') // 取消定时器里已经执行的请求
                        this.timer = null
                    }
                    source = CancelToken.source()
                    const taskIds = Object.keys(this.subprocessTasks).filter(key => !this.subprocessTasks[key].notContinue)
                    if (!taskIds.length) return
                    const data = {
                        task_ids: taskIds,
                        project_id: this.project_id,
                        cancelToken: source.token
                    }
                    const resp = await this.getBatchInstanceStatus(data)
                    if (!resp.result) return

                    Object.keys(resp.data).forEach(key => {
                        this.$set(this.subprocessNodesState, key, resp.data[key].data)
                    })
                    for (const [key, value] of Object.entries(resp.data)) {
                        const { auto_retry_infos: retryInfo = {}, children, state } = value.data
                        // 如果子任务暂停时，节点存在READY状态则将状态置为PENDING_TASK_CONTINUE
                        Object.values(children).forEach(item => {
                            item.state = state === 'SUSPENDED' && item.state === 'READY' ? 'PENDING_TASK_CONTINUE' : item.state
                        })
                        
                        // 是否继续请求子任务
                        let continueRequest = ['CREATED', 'RUNNING', 'PENDING_PROCESSING'].includes(state)
                        // 任务暂停时如果有节点正在执行，需轮询节点状态
                        if (state === 'SUSPENDED') {
                            const executingStates = ['RUNNING', 'PENDING_PROCESSING', 'PENDING_APPROVAL', 'PENDING_CONFIRMATION']
                            continueRequest = Object.values(children).some(item => executingStates.includes(item.state))
                        }
                        // 任务失败时如果又节点还没自动重试完，需轮询节点状态
                        if (state === 'FAILED') {
                            continueRequest = Object.values(retryInfo).some(item => item.max_auto_retry_times > item.auto_retry_times)
                        }
                        if (!continueRequest) {
                            // 查询流程状态接口返回失败后再请求三次
                            this.subprocessTasks[key].pollErrorTimes += 1
                            if (this.subprocessTasks[key].pollErrorTimes > 3) {
                                // 添加notContinue字段，防止子任务继续请求
                                this.subprocessTasks[key].notContinue = true
                            }
                        } else if (this.subprocessTasks[key].pollErrorTimes) {
                            this.subprocessTasks[key].pollErrorTimes = 0
                        }
                    }
                    const isContinue = Object.values(this.subprocessTasks).some(item => !item.notContinue)
                    if (isContinue) {
                        this.setTaskStateTimer()
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    source = null
                    this.subprocessLoading = false
                }
            },
            setTaskStateTimer (time = 3000) {
                this.cancelTaskStateTimer()
                this.timer = setTimeout(() => {
                    this.loadSubprocessState()
                }, time)
            },
            cancelTaskStateTimer () {
                if (this.timer) {
                    clearTimeout(this.timer)
                    this.timer = null
                }
            },
            onSelectExecuteTime (time) {
                this.theExecuteTime = time
                this.loadNodeInfo()
            },
            onRetryClick (nodeId, info) {
                this.$emit('onRetryClick', nodeId, info)
            },
            onSkipClick (nodeId, info) {
                this.$emit('onSkipClick', nodeId, info)
            },
            onResumeClick (nodeId, info) {
                this.$emit('onTaskNodeResumeClick', nodeId, info)
            },
            onApprovalClick (nodeId, info) {
                this.$emit('onApprovalClick', nodeId, info)
            },
            onModifyTimeClick (nodeId, info) {
                this.$emit('onModifyTimeClick', nodeId, info)
            },
            onForceFail (nodeId, info) {
                this.$emit('onForceFail', nodeId, info)
            },
            onPauseClick (nodeId, info) {
                this.$emit('onPauseClick', nodeId, info)
            },
            onContinueClick (nodeId, info) {
                this.$emit('onContinueClick', nodeId, info)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.parameter-details{
    height: 100%;
    display: flex;
    flex-direction: column;
    .details-wrapper {
        display: flex;
        flex: 1;
        height: calc(100% - 48px);
        border-bottom: 1px solid $commonBorderColor;
    }
    .bk-resize-layout-border {
        border: none;
        .bk-resize-layout-aside {
            overflow: hidden;
        }
    }
    .action-wrapper {
        width: 100%;
        padding-left: 20px;
        line-height: 48px;
        background: #fafbfd;
        box-shadow: 0 -1px 0 0 #dcdee5;
        z-index: 2;
        .bk-button {
            min-width: 88px;
            margin-right: 5px;
        }
    }
}
.execute-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    .execute-head {
        display: flex;
        align-items: center;
        line-height: 20px;
        font-size: 14px;
        padding: 15px 24px 16px 15px;
        .node-name {
            font-weight: 600;
            padding-right: 4px;
            word-break: break-all;
        }
        .node-state {
            display: flex;
            align-items: center;
            :first-child {
                margin: 0 5px;
            }
        }
        .common-icon-dark-circle-ellipsis {
            font-size: 14px;
            color: #3a84ff;
        }
        .common-icon-dark-circle-pause,
        .common-icon-dark-circle-pending-process,
        .common-icon-dark-circle-pending-approval,
        .common-icon-dark-circle-pending-confirm {
            font-size: 14px;
            color: #f8B53f;
        }
        .icon-check-circle-shape {
            font-size: 14px;
            color: #30d878;
        }
        .common-icon-dark-circle-close {
            font-size: 14px;
            color: #ff5757;
        }
        .common-icon-waitting {
            font-size: 16px;
            color: #dcdee5;
        }
        .common-icon-manual-skip,
        .common-icon-auto-skip {
            font-size: 14px;
            color: #f0a0a0;
        }
        .icon-circle-shape {
            display: inline-block;
            height: 14px;
            width: 14px;
            background: #f0f1f5;
            border: 1px solid #c4c6cc;
            border-radius: 50%;
            &::before {
                content: initial;
            }
        }
    }
    .scroll-box {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        &::-webkit-scrollbar {
            width: 6px;
            height: 6px;
            &-thumb {
                border-radius: 20px;
                background: #dcdee5;
                box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
            }
        }
        &.subprocess-scroll {
            /deep/.scroll-area {
                overflow-y: initial;
            }
        }
    }
    
}
</style>
