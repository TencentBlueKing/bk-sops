/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-operation">
        <div class="operation-header clearfix">
            <span :class="['task-status', state]">
                <span class="task-status-icon">
                    <i :class="['status-icon', taskStatusIcon]"></i>
                </span>
                <span class="task-status-name">{{taskState}}</span>
            </span>
            <div class="bread-crumbs-wrapper">
                <span
                    class="path-item"
                    v-for="(path, index) in nodeNav"
                    :key="path.id">
                        <span v-if="!!index">&gt;</span>
                        <span class="node-name" @click="onSelectSubflow(path.id)">{{path.name}}</span>
                </span>
            </div>
            <ul class="operation-container clearfix">
                <li
                    v-for="operation in operationList"
                    :key="operation.type"
                    :class="['operation-btn', operation.icon, {
                        'actived': activeOperation === operation.type,
                        'clickable': getBtnClickAble(operation.type)
                    }]"
                    v-bktooltips.bottom="operation.text"
                    @click="onOperationClick(operation.type)">
                </li>
                <li
                    :class="['operation-btn common-icon-menu-view clickable',{
                        'actived': taskParamsType === 'viewParams'
                    }]"
                    v-bktooltips.bottom="i18n.params"
                    @click="onViewTaskParams">
                </li>
                <li :class="['operation-btn', 'common-icon-edit', 'clickable', {
                        'actived': taskParamsType === 'modifyParams'
                    }]"
                    v-bktooltips.bottom="i18n.change_params"
                    @click="onModifyTaskParams">
                </li>
            </ul>
        </div>
        <div class="task-container">
            <div :class="['pipeline-nodes', {
                    'task-params-show': isTaskParamsShow
                }]">
                <PipelineCanvas
                    ref="pipelineCanvas"
                    v-if="!nodeSwitching"
                    :isMenuBarShow="false"
                    :isConfigBarShow="false"
                    :isEdit="false"
                    :canvasData="canvasData"
                    @onNodeClick="onNodeClick">
                </PipelineCanvas>
            </div>
            <transition name="slideRight">
                <div class="task-params" v-show="isTaskParamsShow">
                    <ViewParams
                        v-if="taskParamsType === 'viewParams'"
                        :nodeData="nodeData"
                        :selectedFlowPath="selectedFlowPath"
                        :nodeDetailConfig="nodeDetailConfig"
                        @onClickTreeNode="onClickTreeNode">
                    </ViewParams>
                    <ModifyParams
                        v-if="taskParamsType === 'modifyParams'"
                        :paramsCanBeModify="paramsCanBeModify"
                        :instance_id="instance_id">
                    </ModifyParams>
                    <div class="toggle-params-panel" @click="onToggleParamPanel">
                        <i :class="['common-icon-double-arrow', {actived: isTaskParamsShow}]"></i>
                    </div>
                </div>
            </transition>
        </div>
        <transition name="slideRight">
            <div class="node-info-panel" ref="nodeInfoPanel" v-if="isNodeInfoPanelShow">
                <ExecuteInfo
                    v-if="nodeInfoType==='executeInfo'"
                    :nodeDetailConfig="nodeDetailConfig">
                </ExecuteInfo>
                <RetryNode
                    v-if="nodeInfoType==='retryNode'"
                    :nodeDetailConfig="nodeDetailConfig"
                    @retrySuccess="onRetrySuccess"
                    @retryCancel="onRetryCancel">
                </RetryNode>
                <ModifyTime
                    v-if="nodeInfoType==='modifyTime'"
                    :nodeDetailConfig="nodeDetailConfig"
                    @modifyTimeSuccess="onModifyTimeSuccess"
                    @modifyTimeCancel="onModifyTimeCancel">
                </ModifyTime>
                <div class="close-node-info-panel" @click="onToggleNodeInfoPanel">
                    <i class="common-icon-close"></i>
                </div>
            </div>
        </transition>
        <gatewaySelectDialog
            v-if="isGatewaySelectDialogShow"
            :isGatewaySelectDialogShow="isGatewaySelectDialogShow"
            :gatewayBranches="gatewayBranches"
            @onConfirm="onConfirmGatewaySelect"
            @onCancel="onCancelGatewaySelect">
        </gatewaySelectDialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapActions } from 'vuex'
import Tooltip from 'tooltip.js'
import { errorHandler } from '@/utils/errorHandler.js'
import dom from '@/utils/dom.js'
import { TASK_STATE_DICT } from '@/constants/index.js'
import PipelineCanvas from '@/components/common/PipelineCanvas'
import ViewParams from './ViewParams.vue'
import ModifyParams from './ModifyParams.vue'
import ExecuteInfo from './ExecuteInfo.vue'
import RetryNode from './RetryNode.vue'
import ModifyTime from './ModifyTime.vue'
import gatewaySelectDialog from './GatewaySelectDialog.vue'

const OPERATIONS = [
    {
        type: 'execute',
        icon: 'common-icon-execute',
        text: gettext('执行')
    },
    {
        type: 'pause',
        icon: 'common-icon-suspended',
        text: gettext('暂停')
    },
    {
        type: 'resume',
        icon: 'common-icon-resume',
        text: gettext('继续')
    },
    {
        type: 'revoke',
        icon: 'common-icon-revoke',
        text: gettext('撤销')
    }
]

export default {
    name: 'TaskOperation',
    components: {
        PipelineCanvas,
        ViewParams,
        ModifyParams,
        ExecuteInfo,
        RetryNode,
        ModifyTime,
        gatewaySelectDialog
    },
    props: ['cc_id', 'instance_id', 'instanceFlow', 'instanceName'],
    data () {
        const pipelineData =  JSON.parse(this.instanceFlow)
        const path = []
        path.push({
            id: this.instance_id,
            name: this.instanceName,
            nodeId: pipelineData.id,
            type: 'root'
        })

        return {
            i18n: {
                params: gettext("查看参数"),
                change_params: gettext("修改参数")
            },
            loading: true,
            operationList: OPERATIONS,
            taskId: this.instance_id,
            isTaskParamsShow: false,
            isNodeInfoPanelShow: false,
            nodeInfoType: '',
            activeOperation: '',
            state: '',
            selectedFlowPath: path, // 选择面包屑路径
            instanceStatus: {},
            taskParamsType: '',
            timer: null,
            pipelineData: pipelineData,
            nodeDetailConfig: {},
            nodeSwitching: false,
            isGatewaySelectDialogShow: false,
            gatewayBranches: [],
            nodeTooltipInstance: {},
            pending: {
                skip: false,
                selectGateway: false,
                task: false,
                parseNodeResume: false
            }
        }
    },
    computed: {
        completePipelineData () {
            return JSON.parse(this.instanceFlow)
        },
        canvasData () {
            const {lines, locations, gateways} = this.pipelineData
            const branchConditions = {}
            for (let gKey in gateways) {
                const item = gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            return {
                lines: this.pipelineData.line,
                locations: this.pipelineData.location.map(item => {return {...item, mode: 'preview', checked: true}}),
                branchConditions
            }

        },
        nodeData () {
            return {
                rootNode: {
                    id: this.instance_id,
                    name: this.instanceName,
                    pipeline: {
                        activities: this.completePipelineData.activities
                    }
                }
            }
        },
        taskState () {
            return TASK_STATE_DICT[this.state]
        },
        taskStatusIcon () {
            let iconName
            switch (this.state) {
                case 'CREATED':
                    iconName = 'icon-task-default'
                    break
                case 'RUNNING':
                    iconName = 'common-icon-loading'
                    break
                case 'SUSPENDED':
                    iconName = 'common-icon-suspended'
                    break
                case 'NODE_SUSPENDED':
                    iconName = 'common-icon-suspended'
                    break
                case 'FAILED':
                    iconName = 'common-icon-close-circle'
                    break
                case 'FINISHED':
                    iconName = 'icon-task-done'
                    break
                case 'REVOKED':
                    iconName = 'common-icon-revoke'
                    break
            }
            return iconName
        },
        nodeNav () {
            return this.selectedFlowPath.filter(item => item.type !== 'ServiceActivity')
        },
        // mark the current canvas is root or not
        isTopTask () {
            return this.nodeNav.length === 1
        },
        paramsCanBeModify () {
            return this.isTopTask && this.state === 'CREATED'
        }
    },
    mounted () {
        this.loadTaskStatus()
        this.$el.addEventListener('click', this.handleNodeHoverClick, false)
        window.addEventListener('click', this.handleNodeInfoPanelHide, false)
    },
    beforeDestroy () {
        this.cancelTaskStatusTimer()
        this.$el.removeEventListener('click', this.handleNodeHoverClick, false)
        window.removeEventListener('click', this.handleNodeInfoPanelHide, false)
    },
    methods: {
        ...mapActions('task/', [
            'getInstanceStatus',
            'instanceStart',
            'instancePause',
            'subInstancePause',
            'instanceResume',
            'subInstanceResume',
            'instanceRevoke',
            'instanceNodeSkip',
            'instanceBranchSkip',
            'skipExclusiveGateway',
            'pauseNodeResume'
        ]),
        async loadTaskStatus () {
            this.loading =  true
            try {
                const instanceStatus = await this.getInstanceStatus(this.taskId)
                if (instanceStatus.result) {
                    this.state = instanceStatus.data.state
                    this.instanceStatus = instanceStatus.data
                    if (this.state === 'RUNNING') {
                        this.setTaskStatusTimer()
                    }
                    this.updateNodeInfo()
                } else {
                    this.cancelTaskStatusTimer()
                    errorHandler(instanceStatus, this)
                }
            } catch (e) {
                this.cancelTaskStatusTimer()
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        async taskExecute () {
            try {
                const res = await this.instanceStart(this.instance_id)
                if (res.result) {
                    this.setTaskStatusTimer()
                    this.$bkMessage({
                        message: gettext('任务开始执行'),
                        theme: 'success'
                    })
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.task = false
            }
        },
        async taskPause () {
            let res
            try {
                if (this.isTopTask) {
                    res = await this.instancePause(this.instance_id)
                } else {
                    const data = {
                        instance_id: this.instance_id,
                        node_id: this.taskId
                    }
                    res = await this.subInstancePause(data)
                }
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('任务暂停成功'),
                        theme: 'success'
                    })
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.task = false
            }
        },
        async taskResume () {
            let res
            try {
                if (this.isTopTask) {
                    res = await this.instanceResume(this.instance_id)
                } else {
                    const data = {
                        instance_id: this.instance_id,
                        node_id: this.taskId
                    }
                    res = await this.subInstanceResume(data)
                }
                if (res.result) {
                    this.setTaskStatusTimer()
                    this.$bkMessage({
                        message: gettext('任务继续成功'),
                        theme: 'success'
                    })
                } else {
                    errorHandler(res, this)
                }

            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.task = false
            }
        },
        async taskRevoke () {
            try {
                const res = await this.instanceRevoke(this.instance_id)
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('任务撤销成功'),
                        theme: 'success'
                    })
                    setTimeout(()=> {
                        this.setTaskStatusTimer()
                    }, 1000)
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.task = false
            }
        },
        async nodeTaskSkip (data) {
            this.pending.skip = true
            try {
                const res = await this.instanceNodeSkip(data)
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('跳过成功'),
                        theme: 'success'
                    })
                    this.destroyTooltipInstance(data.id)
                    setTimeout(()=> {
                        this.setTaskStatusTimer()
                    }, 1000)
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.skip = false
            }
        },
        async selectGatewayBranch (data) {
            this.pending.selectGateway = true
            try {
                const res = await this.skipExclusiveGateway(data)
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('跳过成功'),
                        theme: 'success'
                    })
                    this.destroyTooltipInstance(data.id)
                    setTimeout(()=> {
                        this.setTaskStatusTimer()
                    }, 1000)
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.selectGateway = false
            }
        },
        async nodeResume (data) {
            this.pending.parseNodeResume = true
            try {
                const res = await this.pauseNodeResume(data)
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('继续成功'),
                        theme: 'success'
                    })
                    this.destroyTooltipInstance(data.id)
                    setTimeout(()=> {
                        this.setTaskStatusTimer()
                    }, 1000)
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.pending.parseNodeResume = false
            }
        },
        setTaskStatusTimer () {
            this.cancelTaskStatusTimer()
            this.timer = setTimeout(()=>{
                this.loadTaskStatus()
            }, 2000)
        },
        cancelTaskStatusTimer () {
            if (this.timer) {
                clearTimeout(this.timer)
                this.timer = null
            }
        },
        updateTaskStatus (id) {
            this.taskId = id
            this.setCanvasData()
            this.loadTaskStatus()
        },
        // 更新节点状态
        updateNodeInfo () {
            const nodes = this.instanceStatus.children
            for (let id in nodes) {
                const nodeActivities = this.pipelineData.activities[id]
                const nodeEl = document.querySelector(`#${id}`)
                let isSkipped = false
                if (nodes[id].state === 'FINISHED') {
                    isSkipped = nodes[id].skip || nodes[id].error_ignorable
                    this.destroyTooltipInstance(id)
                } else if (nodes[id].state === 'FAILED') {
                    const type = nodeEl.dataset.type
                    if (type === 'tasknode') {
                        const tpl = this.getFailedBtnTpl(id)
                        this.generateTooltipInstance(nodeEl, id, tpl)
                    } else if (type === 'branchgateway') {
                        const tpl = this.getGatewayBtnTpl(id)
                        this.generateTooltipInstance(nodeEl, id, tpl)
                    }

                } else if ( // modify timer node's time
                    nodes[id].state === 'RUNNING' &&
                    nodeActivities.component &&
                    nodeActivities.component.code === 'sleep_timer' &&
                    !this.nodeTooltipInstance[id]
                ) {
                    const tpl = this.getModityTimeBtnTpl(id)
                    this.generateTooltipInstance(nodeEl, id, tpl)
                } else if ( // resume pause node
                    nodes[id].state === 'RUNNING' &&
                    nodeActivities.component &&
                    nodeActivities.component.code === 'pause_node' &&
                    !this.nodeTooltipInstance[id]
                ) {
                    const tpl = this.getPauseResumeBtnTpl(id)
                    this.generateTooltipInstance(nodeEl, id, tpl)
                }
                const data = {status: nodes[id].state, isSkipped}
                this.setTaskNodeStatus(id, data)
            }
        },
        setTaskNodeStatus (id, data) {
            this.$refs.pipelineCanvas && this.$refs.pipelineCanvas.onUpdateNodeInfo(id, data)
        },
        getFailedBtnTpl (id) {
            const i18n_retry = gettext("重试")
            const i18n_skip = gettext("跳过")
            return `<div class="btn-wrapper">
                <div class="tooltip-btn retry-btn" data-id="${id}">${i18n_retry}</div>
                <div class="tooltip-btn skip-btn" data-id="${id}">${i18n_skip}</div>
            </div>`
        },
        getModityTimeBtnTpl (id) {
            const i18n_change_timer = gettext("修改时间")
            return `<div class="btn-wrapper">
                <div class="tooltip-btn modify-time-btn" data-id="${id}">${i18n_change_timer}</div>
            </div>`
        },
        getGatewayBtnTpl (id) {
            const i18n_skip = gettext("跳过")
            return `<div class="btn-wrapper">
                <div class="tooltip-btn gateway-select-btn" data-id="${id}">${i18n_skip}</div>
            </div>`
        },
        getPauseResumeBtnTpl (id) {
            const i18n_continue = gettext("继续")
            return `<div class="btn-wrapper">
                <div class="tooltip-btn pause-resume-btn" data-id="${id}">${i18n_continue}</div>
            </div>`
        },
        generateTooltipInstance (el, id, tpl) {
            this.destroyTooltipInstance(id)
            this.nodeTooltipInstance[id] = new Tooltip(el, {
                placement: 'bottom',
                html: true,
                title: tpl
            })
        },
        setNodeDetailConfig (id) {
            const nodeActivities = this.pipelineData.activities[id]
            let subprocessStack = []
            if (this.selectedFlowPath.length > 1){
                subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
            }
            this.nodeDetailConfig = {
                component_code: nodeActivities.component.code,
                node_id: nodeActivities.id,
                instance_id: this.instance_id,
                subprocess_stack: JSON.stringify(subprocessStack)
            }
        },
        // node tooltip click
        handleNodeHoverClick (e) {
            const classList = e.target.classList
            if (!classList) return
            if (classList.contains('retry-btn')) {
                this.handleNodeRetryClick(e)
            } else if (classList.contains('skip-btn')) {
                this.handleNodeSkipClick(e)
            } else if (classList.contains('modify-time-btn')) {
                this.handleNodeModifyTimeClick(e)
            } else if (classList.contains('gateway-select-btn')) {
                this.handleGatewaySelectClick(e)
            } else if (classList.contains('pause-resume-btn')) {
                this.handlePauseResumeClick(e)
            }
        },
        handleNodeInfoPanelHide (e) {
            const classList = e.target.classList
            const isTooltipBtn = classList.contains('tooltip-btn')
            if (!this.isNodeInfoPanelShow || isTooltipBtn) return
            const NodeInfoPanel = document.querySelector(".node-info-panel")
            if (NodeInfoPanel) {
                if (!dom.nodeContains(NodeInfoPanel, e.target)) {
                    this.isNodeInfoPanelShow = false
                }
            }
        },
        handleNodeRetryClick (e) {
            const id = e.target.dataset.id
            this.isNodeInfoPanelShow = true
            this.nodeInfoType = 'retryNode'
            this.setNodeDetailConfig(id)
        },
        handleNodeSkipClick (e) {
            if (this.pending.skip) return
            const id = e.target.dataset.id
            const nodeActivities = this.pipelineData.activities[id]
            const data = {
                instance_id: this.instance_id,
                node_id: id
            }
            this.nodeTaskSkip(data)
        },
        handleNodeModifyTimeClick (e) {
            const id = e.target.dataset.id
            this.isNodeInfoPanelShow = true
            this.nodeInfoType = 'modifyTime'
            this.setNodeDetailConfig(id)
        },
        handleGatewaySelectClick (e) {
            const id = e.target.dataset.id
            const nodeGateway = this.pipelineData.gateways[id]
            const branches = []
            for (let item in nodeGateway.conditions) {
                branches.push({
                    id: item,
                    node_id: id,
                    name: nodeGateway.conditions[item].evaluate
                })
            }
            this.gatewayBranches = branches
            this.isGatewaySelectDialogShow = true
        },
        handlePauseResumeClick (e) {
            if (this.pending.parseNodeResume) return
            const id = e.target.dataset.id
            const nodeActivities = this.pipelineData.activities[id]
            const data = {
                instance_id: this.instance_id,
                node_id: id,
                data: JSON.stringify({callback: 'resume'})
            }
            this.nodeResume(data)
        },
        // update pipeline canvas
        setCanvasData () {
            this.$nextTick(()=>{
                this.nodeSwitching = false
            })
        },
        getBtnClickAble (type) {
            switch (type) {
                case 'execute':
                    return this.state === 'CREATED' && this.isTopTask
                    break
                case 'pause':
                    return this.state === 'RUNNING'
                    break
                case 'resume':
                    return this.state === 'SUSPENDED'
                    break
                case 'revoke':
                    return (this.state === 'RUNNING' ||
                        this.state === 'SUSPENDED' ||
                        this.state === 'NODE_SUSPENDED' ||
                        this.state === 'FAILED') && this.isTopTask
                    break
                default:
                    break
            }
        },
        destroyTooltipInstance (id) {
            if (this.nodeTooltipInstance[id]) {
                this.nodeTooltipInstance[id].dispose()
                delete this.nodeTooltipInstance[id]
            }
        },
        clearTooltipInstance () {
            Object.keys(this.nodeTooltipInstance).forEach(item => {
                this.destroyTooltipInstance(item)
            })
        },
        // trigger view task params and select node panel
        onViewTaskParams () {
            this.isTaskParamsShow = true
            this.taskParamsType = 'viewParams'
        },
        // trigger modify task params panel
        onModifyTaskParams () {
            this.isTaskParamsShow = true
            this.taskParamsType = 'modifyParams'
        },
        // trigger view params panel
        onToggleParamPanel () {
            this.isTaskParamsShow = false
            this.taskParamsType = ''
        },
        // trigger node information panel
        onToggleNodeInfoPanel () {
            this.isNodeInfoPanelShow = false
            this.nodeInfoType = ''
        },
        onOperationClick (type) {
            if (!this.getBtnClickAble(type) || this.pending.task)  return
            this.pending.task = true
            this.activeOperation = this.activeOperation ? '' : type
            const actionType = 'task' + type.charAt(0).toUpperCase() + type.slice(1)
            this[actionType]()
        },
        onNodeClick (id) {
            const node = this.canvasData.locations.filter(item => item.id === id)[0]
            if (node.type === 'tasknode') {
                this.handleSingleNodeClick(id, 'singleAtom')
            } else if (node.type === 'subflow') {
                this.handleSubflowAtomClick(id)
            } else {
                this.handleSingleNodeClick(id, 'controlNode')
            }
        },
        handleSingleNodeClick (id, type) {
            const nodeState =  this.instanceStatus.children && this.instanceStatus.children[id]
            const nodeActivities = this.pipelineData.activities[id]
            const componentCode = type === 'singleAtom' ? nodeActivities.component.code : ''
            let isPanelShow = false
            if (nodeState) {
                if (type === 'singleAtom') {
                    isPanelShow = nodeState.state === 'FINISHED' || nodeState.state === 'FAILED'
                } else {
                    isPanelShow = nodeState.state === 'FAILED'
                }
            }
            if (isPanelShow) {
                let subprocessStack = []
                if (this.selectedFlowPath.length > 1){
                    subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1, -1)
                }
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = 'executeInfo'
                this.nodeDetailConfig = {
                    component_code: componentCode,
                    node_id: id,
                    instance_id: this.instance_id,
                    subprocess_stack: JSON.stringify(subprocessStack)
                }
            }
        },
        handleSubflowAtomClick (id) {
            this.cancelTaskStatusTimer()
            this.clearTooltipInstance()
            const nodeActivities = this.pipelineData.activities[id]
            this.nodeSwitching = true
            this.selectedFlowPath.push({
                id: nodeActivities.id,
                name: nodeActivities.name,
                nodeId: nodeActivities.id,
                type: 'SubProcess'
            })
            this.pipelineData = this.pipelineData.activities[id].pipeline
            this.updateTaskStatus(id)
        },
        // bread crumbs click
        onSelectSubflow (id) {
            let nodeIndex = 0
            this.selectedFlowPath.some((item, index) => {
                if (id === item.id) {
                    nodeIndex = index
                    return true
                }
            })
            if (nodeIndex === (this.selectedFlowPath.length - 1)) return // the last level node
            this.nodeSwitching = true
            this.selectedFlowPath.splice(nodeIndex + 1)
            if (nodeIndex === 0) {
                this.pipelineData = this.completePipelineData
            } else {
                const pathList = this.selectedFlowPath.slice(1)
                let nodeActivities = this.completePipelineData.activities
                pathList.forEach((item, index) => {
                    nodeActivities = index ? nodeActivities.pipeline.activities[item.id] : nodeActivities[item.id]
                })
                this.pipelineData = nodeActivities.pipeline
            }
            this.nodeDetailConfig = {}
            this.clearTooltipInstance()
            this.cancelTaskStatusTimer()
            this.updateTaskStatus(id)
        },
        onClickTreeNode (nodeHeirarchy, nodeType) {
            let nodeActivities
            const nodePath = [{
                id: this.instance_id,
                name: this.instanceName,
                nodeId: this.completePipelineData.id
            }]
            let heirarchyList = nodeHeirarchy.split('.').splice(1)
            if (heirarchyList.length) { // not root node
                nodeActivities = this.completePipelineData.activities
                heirarchyList.forEach((key, index) => {
                    nodeActivities = index ? nodeActivities.pipeline.activities[key] : nodeActivities[key]
                    nodePath.push({
                        id: nodeActivities.id,
                        name: nodeActivities.name,
                        nodeId: nodeActivities.id,
                        type: nodeActivities.type
                    })
                })
                this.selectedFlowPath = nodePath
                if (nodeActivities.type === 'SubProcess') { // click subprocess node
                    this.nodeSwitching = true
                    this.pipelineData = nodeActivities.pipeline
                    this.cancelTaskStatusTimer()
                    this.updateTaskStatus(nodeActivities.id)
                    this.nodeDetailConfig = {}
                } else { // click single task node
                    let subprocessStack = []
                    if (this.selectedFlowPath.length > 1){
                        subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1, -1)
                    }
                    this.nodeDetailConfig = {
                        component_code: nodeActivities.component.code,
                        node_id: nodeActivities.id,
                        instance_id: this.instance_id,
                        subprocess_stack: JSON.stringify(subprocessStack)
                    }
                }
            } else {
                nodeActivities = this.completePipelineData
                this.nodeSwitching = true
                this.pipelineData = nodeActivities
                this.cancelTaskStatusTimer()
                this.updateTaskStatus(this.instance_id)
                this.selectedFlowPath = nodePath
                this.nodeDetailConfig = {}
            }
        },
        onRetrySuccess (id) {
            this.isNodeInfoPanelShow = false
            this.destroyTooltipInstance(id)
            this.setTaskStatusTimer()
        },
        onRetryCancel () {
            this.isNodeInfoPanelShow = false
            this.nodeInfoType = ''
        },
        onModifyTimeSuccess (id) {
            this.isNodeInfoPanelShow = false
            this.destroyTooltipInstance(id)
            this.setTaskStatusTimer()
        },
        onModifyTimeCancel () {
            this.isNodeInfoPanelShow = false
            this.nodeInfoType = ''
        },
        onConfirmGatewaySelect (selected) {
            const data = {
                flow_id: selected.id,
                node_id: selected.node_id,
                instance_id: this.instance_id
            }
            this.isGatewaySelectDialogShow = false
            this.selectGatewayBranch(data)
        },
        onCancelGatewaySelect () {
            this.isGatewaySelectDialogShow = false
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-operation {
    position: relative;
    height: calc(100% - 60px);
    overflow: hidden;
}
.operation-header {
    padding: 0 0 0 10px;
    height: 50px;
    line-height: 50px;
    background: $commonBgColor;
    border-bottom: 1px solid $commonBorderColor;
    .task-status {
        display: inline-block;
        padding-right: 10px;
        height: 20px;
        line-height: 20px;
        font-size: 14px;
        color: $whiteDefault;
        border-right: 1px solid $commonBorderColor;
        text-align: center;
        .task-status-icon {
            position: relative;
            float: left;
            margin-top: 2px;
            margin-right: 4px;
            width: 16px;
            height: 16px;
            line-height: 16px;
            border-radius: 50%;
            font-size: 12px;
            text-align: center;
        }
        &.CREATED {
            .task-status-icon {
                background: $blueDefault;
                & > i {
                    display: inline-block;
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: $whiteDefault;
                    vertical-align: 2px;
                }
            }
            .task-status-name {
                color: $blueDefault;
            }
        }
        &.FINISHED {
            .task-status-icon {
                background: $greenDark;

            }
            .icon-task-done:after {
                content: "";
                position: absolute;
                left: 3px;
                top: 4px;
                height: 4px;
                width: 8px;
                border-left: 1px solid;
                border-bottom: 1px solid;
                border-color: #ffffff;
                -webkit-transform: rotate(-45deg);
                transform: rotate(-45deg);
            }
            .task-status-name {
                color: $greenDark;
            }
        }
        &.RUNNING {
            .task-status-icon {
                background: $yellowDefault;
            }
            .task-status-name {
                color: $yellowDefault;
            }
            .common-icon-loading {
                display: inline-block;
                font-size: 12px;
                animation: bk-button-loading 1.4s infinite linear;
            }
            @keyframes bk-button-loading {
                from {
                  -webkit-transform: rotate(0);
                  transform: rotate(0); }
                to {
                  -webkit-transform: rotate(360deg);
                  transform: rotate(360deg);
                }
            }
        }
        &.SUSPENDED, &.NODE_SUSPENDED {
            .task-status-icon {
                color: $whiteDefault;
                background: $yellowDefault;
            }
            .task-status-name {
                color: $yellowDefault;
            }
        }
        &.FAILED {
            .task-status-icon {
                color: $redDefault;
                font-size: 16px;
            }
            .task-status-name {
                color: $redDefault;
            }
        }
        &.REVOKED {
            .task-status-icon {
                background: $blueDisable;
            }
            .task-status-name {
                color: $blueDisable;
            }
        }
    }
    .bread-crumbs-wrapper {
        display: inline-block;
        font-size: 14px;
        .path-item {
            display: inline-block;
            .node-name {
                margin: 0 4px;
                color: $blueDefault;
                cursor: pointer;

            }
            &:last-child {
                .node-name {
                    &:last-child {
                        color: $greyDefault;
                        cursor: text;
                    }
                }
            }
        }
    }
    .operation-container {
        float: right;
        .operation-btn {
            float: left;
            width: 60px;
            height: 49px;
            line-height: 49px;
            font-size: 22px;
            text-align: center;
            color: $greyDisable;
            &.clickable {
                color: $greyDefault;
                cursor: pointer;
                &:hover {
                    color: $greenDefault;
                }
                &.actived {
                    color: $greenDefault;
                    background: $whiteDefault;
                }
            }
            &.common-icon-menu-view {
                border-left: 1px solid $commonBorderColor;
            }
        }
    }
}
.task-container {
    position: relative;
    width: 100%;
    height: calc(100% - 52px);
    background: $whiteDefault;
    overflow: hidden;
    .pipeline-nodes {
        width: 100%;
        height: 100%;
        transition: width 0.5s ease-in-out;
        /deep/ .pipeline-canvas{
            width: 100%;
            .node-canvas {
                width: 100%;
                height: 100%;
                background: $whiteDefault;
            }
        }
    }
    .task-params {
        position: absolute;
        top: 0;
        right: 0;
        width: 750px;
        height: 100%;
        background: $whiteDefault;
        border-left: 1px solid $commonBorderColor;
        z-index: 4;
        .task-params-show {
            width: 750px;
            border-left: 1px solid $commonBorderColor;
        }
        .toggle-params-panel {
            position: absolute;
            top: 50%;
            left: -18px;
            margin-top: -12px;
            width: 18px;
            height: 38px;
            line-height: 38px;
            font-size: 14px;
            color: #5a5a68;
            text-align: center;
            background: $commonBgColor;
            border: 1px solid $commonBorderColor;
            border-right: none;
            border-radius: 2px;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
            cursor: pointer;
            transform: rotate(0);
            &:hover {
                color: $blueDefault;
                background: $greyDash;
            }
            &.actived {
                transform: rotate(-180deg);
            }
        }
    }
}
.node-info-panel {
    position: absolute;
    top: 0;
    right: 0;
    width: 764px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    z-index: 5;
    .close-node-info-panel {
        position: absolute;
        top: 0;
        left: -18px;
        width: 18px;
        height: 50px;
        line-height: 50px;
        font-size: 12px;
        color: $whiteDefault;
        text-align: center;
        background: $blueThinBg;
        cursor: pointer;
        &:hover {
            background: $blueDefault;
        }
    }
}
</style>
<style lang="scss">
@import '@/scss/config.scss';
.task-operation {
    .operation-table {
        width: 100%;
        font-size: 14px;
        border: 1px solid #ebebeb;
        border-collapse: collapse;
        th {
            background: $whiteNodeBg
        }
        th,td {
            padding: 10px;
            color: $greyDefault;
            text-align: left;
            border: 1px solid #ebeef5;
        }
    }
}
</style>


