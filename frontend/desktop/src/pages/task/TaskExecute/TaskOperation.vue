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
    <div class="task-operation">
        <div class="operation-header clearfix">
            <div class="bread-crumbs-wrapper" v-if="isBreadcrumbShow">
                <span
                    :class="['path-item', { 'name-ellipsis': nodeNav.length > 1 }]"
                    v-for="(path, index) in nodeNav"
                    :key="path.id"
                    :title="showNodeList.includes(index) ? path.name : ''">
                    <span v-if="!!index && showNodeList.includes(index) || index === 1">
                        &gt;
                    </span>
                    <span v-if="showNodeList.includes(index)" class="node-name" :title="path.name" @click="onSelectSubflow(path.id)">
                        {{path.name}}
                    </span>
                    <span class="node-ellipsis" v-else-if="index === 1">
                        {{ellipsis}}
                    </span>
                </span>
            </div>
            <div class="operation-container clearfix">
                <div class="task-operation-btns" v-show="isTaskOperationBtnsShow">
                    <template v-for="operation in taskOperationBtns">
                        <bk-button
                            :class="['operation-btn', operation.action === 'revoke' ? 'revoke-btn' : 'execute-btn']"
                            theme="default"
                            size="mini"
                            hide-text="true"
                            :icon="'common-icon ' + operation.icon"
                            :key="operation.action"
                            :loading="operation.loading"
                            :disabled="operation.disabled"
                            v-bk-tooltips="{
                                content: operation.text,
                                placements: ['bottom']
                            }"
                            @click="onOperationClick(operation.action)">
                        </bk-button>
                    </template>
                </div>
                <div class="task-params-btns">
                    <bk-button
                        :class="['params-btn', 'solid-eye', {
                            actived: nodeInfoType === 'viewParams'
                        }]"
                        theme="default"
                        size="mini"
                        hide-text="true"
                        icon="common-icon common-icon-solid-eye params-btn-icon"
                        v-bk-tooltips="{
                            content: i18n.params,
                            placements: ['bottom']
                        }"
                        @click="onTaskParamsClick('viewParams')">
                    </bk-button>
                    <bk-button
                        :class="['params-btn', {
                            actived: nodeInfoType === 'modifyParams'
                        }]"
                        theme="default"
                        size="mini"
                        hide-text="true"
                        icon="common-icon common-icon-edit params-btn-icon"
                        v-bk-tooltips="{
                            content: i18n.changeParams,
                            placements: ['bottom']
                        }"
                        @click="onTaskParamsClick('modifyParams')">
                    </bk-button>
                    <router-link
                        v-if="isShowViewProcess"
                        class="jump-tpl-page-btn common-icon-link params-btn-icon"
                        target="_blank"
                        v-bk-tooltips="{
                            content: i18n.checkFlow,
                            placements: ['bottom']
                        }"
                        :to="getTplURL()">
                    </router-link>
                </div>
            </div>
        </div>
        <div :class="['task-status', state]">
            <span class="task-status-name">
                {{taskState}}
            </span>
        </div>
        <div class="task-container">
            <div :class="['pipeline-nodes', {
                'task-params-show': isTaskParamsShow
            }]">
                <PipelineCanvas
                    ref="pipelineCanvas"
                    v-if="!nodeSwitching"
                    :is-menu-bar-show="false"
                    :is-config-bar-show="false"
                    :is-edit="false"
                    :canvas-data="canvasData"
                    @onNodeClick="onNodeClick">
                </PipelineCanvas>
            </div>
        </div>
        <transition name="slideRight">
            <!-- 执行详情 -->
            <div class="node-info-panel" ref="nodeInfoPanel" v-if="isNodeInfoPanelShow">
                <ViewParams
                    v-if="nodeInfoType === 'viewParams'"
                    :node-data="nodeData"
                    :selected-flow-path="selectedFlowPath"
                    :tree-node-config="treeNodeConfig"
                    @onClickTreeNode="onClickTreeNode">
                </ViewParams>
                <ModifyParams
                    v-if="nodeInfoType === 'modifyParams'"
                    :params-can-be-modify="paramsCanBeModify"
                    :instance_id="instance_id">
                </ModifyParams>
                <ExecuteInfo
                    v-if="nodeInfoType === 'executeInfo'"
                    :node-detail-config="nodeDetailConfig">
                </ExecuteInfo>
                <RetryNode
                    v-if="nodeInfoType === 'retryNode'"
                    :node-detail-config="nodeDetailConfig"
                    @retrySuccess="onRetrySuccess"
                    @retryCancel="onRetryCancel">
                </RetryNode>
                <ModifyTime
                    v-if="nodeInfoType === 'modifyTime'"
                    :node-detail-config="nodeDetailConfig"
                    @modifyTimeSuccess="onModifyTimeSuccess"
                    @modifyTimeCancel="onModifyTimeCancel">
                </ModifyTime>
                <div class="close-node-info-panel" @click="onToggleNodeInfoPanel">
                    <i class="common-icon-double-arrow"></i>
                </div>
            </div>
        </transition>
        <gatewaySelectDialog
            v-if="isGatewaySelectDialogShow"
            :is-gateway-select-dialog-show="isGatewaySelectDialogShow"
            :gateway-branches="gatewayBranches"
            @onConfirm="onConfirmGatewaySelect"
            @onCancel="onCancelGatewaySelect">
        </gatewaySelectDialog>
        <revokeDialog
            :is-revoke-dialog-show="isRevokeDialogShow"
            @onConfirmRevokeTask="onConfirmRevokeTask"
            @onCancelRevokeTask="onCancelRevokeTask">
        </revokeDialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapState } from 'vuex'
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
    import revokeDialog from './revokeDialog.vue'

    const TASK_OPERATIONS = {
        execute: {
            action: 'execute',
            icon: 'common-icon-right-triangle',
            text: gettext('执行')
        },
        pause: {
            action: 'pause',
            icon: 'common-icon-double-vertical-line',
            text: gettext('暂停')
        },
        resume: {
            action: 'resume',
            icon: 'common-icon-right-triangle',
            text: gettext('继续')
        },
        revoke: {
            action: 'revoke',
            icon: 'common-icon-return-arrow',
            text: gettext('撤销')
        }
    }
    // 执行按钮的变更
    const STATE_OPERATIONS = {
        'RUNNING': 'pause',
        'SUSPENDED': 'resume',
        'CREATED': 'execute',
        'FAILED': 'pause'
    }
    export default {
        name: 'TaskOperation',
        components: {
            PipelineCanvas,
            ViewParams,
            ModifyParams,
            ExecuteInfo,
            RetryNode,
            ModifyTime,
            gatewaySelectDialog,
            revokeDialog
        },
        props: ['cc_id', 'instance_id', 'instanceFlow', 'instanceName', 'template_id', 'templateSource'],
        data () {
            const pipelineData = JSON.parse(this.instanceFlow)
            const path = []
            path.push({
                id: this.instance_id,
                name: this.instanceName,
                nodeId: pipelineData.id,
                type: 'root'
            })

            return {
                i18n: {
                    params: gettext('查看参数'),
                    changeParams: gettext('修改参数'),
                    checkFlow: gettext('查看流程')
                },
                taskId: this.instance_id,
                isTaskParamsShow: false,
                isNodeInfoPanelShow: false,
                nodeInfoType: '',
                state: '',
                selectedFlowPath: path, // 选择面包屑路径
                instanceStatus: {},
                taskParamsType: '',
                timer: null,
                pipelineData: pipelineData,
                treeNodeConfig: {},
                nodeDetailConfig: {},
                nodeSwitching: false,
                isGatewaySelectDialogShow: false,
                gatewayBranches: [],
                nodeTooltipInstance: {},
                pending: {
                    skip: false,
                    selectGateway: false,
                    task: false,
                    parseNodeResume: false,
                    subflowPause: false,
                    subflowResume: false
                },
                activeOperation: '', // 当前任务操作（头部区域操作按钮触发）
                isRevokeDialogShow: false,
                showNodeList: [0, 1, 2],
                ellipsis: '...',
                operateLoading: false,
                retrievedCovergeGateways: [] // 遍历过的汇聚节点
            }
        },
        computed: {
            ...mapState({
                userType: state => state.userType
            }),
            completePipelineData () {
                return JSON.parse(this.instanceFlow)
            },
            isBreadcrumbShow () {
                return this.completePipelineData.location.some(item => {
                    return item.type === 'subflow'
                })
            },
            canvasData () {
                const { line, location, gateways } = this.pipelineData
                const branchConditions = {}
                for (const gKey in gateways) {
                    const item = gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                return {
                    lines: line,
                    locations: location.map(item => {
                        return { ...item, mode: 'preview', checked: true }
                    }),
                    branchConditions
                }
            },
            nodeData () {
                return [{
                    id: this.instance_id,
                    name: this.instanceName,
                    children: this.getOrderedTree(this.completePipelineData)
                }]
            },
            taskState () {
                return TASK_STATE_DICT[this.state]
            },
            nodeNav () {
                return this.selectedFlowPath.filter(item => item.type !== 'ServiceActivity')
            },
            // 当前画布是否为最外层
            isTopTask () {
                return this.nodeNav.length === 1
            },
            isTaskOperationBtnsShow () {
                return this.state !== 'REVOKED' && this.state !== 'FINISHED'
            },
            taskOperationBtns () {
                const operationBtns = []
                const operationType = STATE_OPERATIONS[this.state]
                if (this.state && operationType) {
                    const executePauseBtn = Object.assign({}, TASK_OPERATIONS[operationType])
                    const revokeBtn = Object.assign({}, TASK_OPERATIONS['revoke'])
                    
                    if (this.pending.task) {
                        executePauseBtn.loading = this.activeOperation === executePauseBtn.action
                        revokeBtn.loading = this.activeOperation === revokeBtn.action
                    }

                    executePauseBtn.disabled = !this.getOptBtnIsClickable(executePauseBtn.action)
                    revokeBtn.disabled = !this.getOptBtnIsClickable(revokeBtn.action)

                    operationBtns.push(executePauseBtn, revokeBtn)
                }
                return operationBtns
            },
            paramsCanBeModify () {
                return this.isTopTask && this.state === 'CREATED'
            },
            // 职能化/审计中心时,隐藏[查看流程]按钮
            isShowViewProcess () {
                return this.userType !== 'functor' && this.userType !== 'auditor'
            }
        },
        watch: {
            nodeNav (val) {
                if (val.length > 3) {
                    this.showNodeList = [0, val.length - 1, val.length - 2]
                } else {
                    this.showNodeList = [0, 1, 2]
                }
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
                const data = {
                    instance_id: this.taskId,
                    cc_id: this.cc_id
                }
                try {
                    this.$emit('taskStatusLoadChange', true)
                    const instanceStatus = await this.getInstanceStatus(data)
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
                    this.$emit('taskStatusLoadChange', false)
                }
            },
            async taskExecute () {
                try {
                    const res = await this.instanceStart(this.instance_id)
                    if (res.result) {
                        this.state = 'RUNNING'
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
            async taskPause (subflowPause, nodeId) {
                let res
                try {
                    if (!this.isTopTask || subflowPause) { // 子流程画布暂停或子流程节点暂停
                        const data = {
                            instance_id: this.instance_id,
                            node_id: nodeId || this.taskId
                        }
                        res = await this.subInstancePause(data)
                    } else {
                        res = await this.instancePause(this.instance_id)
                    }
                    if (res.result) {
                        this.state = 'SUSPENDED'
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
            async taskResume (subflowResume, nodeId) {
                let res
                try {
                    if (!this.isTopTask || subflowResume) {
                        const data = {
                            instance_id: this.instance_id,
                            node_id: nodeId || this.taskId
                        }
                        res = await this.subInstanceResume(data)
                    } else {
                        res = await this.instanceResume(this.instance_id)
                    }
                    if (res.result) {
                        this.state = 'RUNNING'
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
                        this.state = 'REVOKE'
                        this.$bkMessage({
                            message: gettext('任务撤销成功'),
                            theme: 'success'
                        })
                        setTimeout(() => {
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
            async nodeTaskSkip (tooltipDom, data) {
                tooltipDom.style.display = 'none'
                this.pending.skip = true
                try {
                    const res = await this.instanceNodeSkip(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: gettext('跳过成功'),
                            theme: 'success'
                        })
                        this.destroyTooltipInstance(data.id)
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    } else {
                        tooltipDom.style.display = 'block'
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
                        setTimeout(() => {
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
                        setTimeout(() => {
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
                this.timer = setTimeout(() => {
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
                for (const id in nodes) {
                    const nodeActivities = this.pipelineData.activities[id]
                    const nodeEl = document.querySelector(`#${id}`)
                    let isSkipped = false
                    if (nodes[id].state === 'FINISHED') {
                        isSkipped = nodes[id].skip || nodes[id].error_ignorable
                        this.destroyTooltipInstance(id)
                    } else if (nodes[id].state === 'FAILED') { // 初始化失败节点重试 tooltip（任务节点、分支网关）
                        const type = nodeEl ? nodeEl.dataset.type : 'undefined'
                        if (type === 'tasknode') {
                            const tpl = this.getFailedBtnTpl(id, nodeActivities.isSkipped, nodeActivities.can_retry)
                            this.generateTooltipInstance(nodeEl, id, tpl)
                        } else if (type === 'branchgateway') {
                            const tpl = this.getGatewayBtnTpl(id)
                            this.generateTooltipInstance(nodeEl, id, tpl)
                        }
                    } else if ( // 初始化定时节点修改时间 tooltip
                        nodes[id].state === 'RUNNING'
                        && nodeActivities
                        && nodeActivities.component
                        && nodeActivities.component.code === 'sleep_timer'
                        && !this.nodeTooltipInstance[id]
                    ) {
                        const tpl = this.getModityTimeBtnTpl(id)
                        this.generateTooltipInstance(nodeEl, id, tpl)
                    } else if ( // 初始化暂停节点继续 tooltip
                        nodes[id].state === 'RUNNING'
                        && nodeActivities
                        && nodeActivities.component
                        && nodeActivities.component.code === 'pause_node'
                        && !this.nodeTooltipInstance[id]
                    ) {
                        const tpl = this.getPauseResumeBtnTpl(id)
                        this.generateTooltipInstance(nodeEl, id, tpl)
                    } else if ( // 初始化子流程节点暂停 tooltip
                        nodes[id].state === 'RUNNING'
                        && nodeActivities
                        && nodeActivities.type === 'SubProcess'
                    ) {
                        const tpl = this.getSubflowPauseBtnTpl(id)
                        if (!this.nodeTooltipInstance[id]) {
                            this.generateTooltipInstance(nodeEl, id, tpl)
                        } else {
                            this.nodeTooltipInstance[id].updateTitleContent(tpl)
                        }
                    } else if ( // 初始化子流程节点继续 tooltip
                        nodes[id].state === 'SUSPENDED'
                        && nodeActivities
                        && nodeActivities.type === 'SubProcess'
                    ) {
                        const tpl = this.getSubflowResumeBtnTpl(id)
                        if (!this.nodeTooltipInstance[id]) {
                            this.generateTooltipInstance(nodeEl, id, tpl)
                        } else {
                            this.nodeTooltipInstance[id].updateTitleContent(tpl)
                        }
                    }
                    const data = { status: nodes[id].state, isSkipped }

                    // 暂停节点右上角显示暂停icon
                    if (nodes[id].state === 'RUNNING'
                        && nodeActivities
                        && nodeActivities.component
                        && nodeActivities.component.code === 'pause_node'
                    ) {
                        data.status = 'SUSPENDED'
                    }

                    // 定时节点右上角显示时钟icon
                    if (nodes[id].state === 'RUNNING'
                        && nodeActivities
                        && nodeActivities.component
                        && nodeActivities.component.code === 'sleep_timer'
                    ) {
                        data.isShowClockIcon = true
                    }

                    this.setTaskNodeStatus(id, data)
                }
            },
            setTaskNodeStatus (id, data) {
                this.$refs.pipelineCanvas && this.$refs.pipelineCanvas.onUpdateNodeInfo(id, data)
            },
            getFailedBtnTpl (id, isSkipped, retry) {
                const i18n_retry = gettext('重试')
                const i18n_skip = gettext('跳过')
                const atom_failed = gettext('流程模板中该标准插件节点未配置失败处理方式，不可操作')
                let content = `<div class="btn-wrapper">`
                if (retry) {
                    content += `<div class="tooltip-btn retry-btn" data-id="${id}">${i18n_retry}</div>`
                }
                if (isSkipped) {
                    content += `<div class="tooltip-btn skip-btn" data-id="${id}">${i18n_skip}</div>`
                }
                // 兼容老数据
                if (retry === undefined && isSkipped === undefined) {
                    content += `<div class="tooltip-btn retry-btn" data-id="${id}">${i18n_retry}</div>`
                    content += `<div class="tooltip-btn skip-btn" data-id="${id}">${i18n_skip}</div>`
                } else if (!retry && !isSkipped) {
                    content += `<div class="atom-failed">${atom_failed}</div>`
                }
                content += `</div>`
                return content
            },
            getModityTimeBtnTpl (id) {
                const i18n_change_timer = gettext('修改时间')
                return `<div class="btn-wrapper">
                <div class="tooltip-btn modify-time-btn" data-id="${id}">${i18n_change_timer}</div>
            </div>`
            },
            getGatewayBtnTpl (id) {
                const i18n_skip = gettext('跳过')
                return `<div class="btn-wrapper">
                <div class="tooltip-btn gateway-select-btn" data-id="${id}">${i18n_skip}</div>
            </div>`
            },
            getPauseResumeBtnTpl (id) {
                const i18n_continue = gettext('继续')
                return `<div class="btn-wrapper">
                <div class="tooltip-btn pause-resume-btn" data-id="${id}">${i18n_continue}</div>
            </div>`
            },
            getSubflowPauseBtnTpl (id) {
                const i18n_pause = gettext('暂停')
                return `<div class="btn-wrapper">
                <div class="tooltip-btn subflow-pause-btn" data-id="${id}">${i18n_pause}</div>
            </div>`
            },
            getSubflowResumeBtnTpl (id) {
                const i18n_continue = gettext('继续')
                return `<div class="btn-wrapper">
                <div class="tooltip-btn subflow-resume-btn" data-id="${id}">${i18n_continue}</div>
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
                if (this.selectedFlowPath.length > 1) {
                    subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
                }
                this.nodeDetailConfig = {
                    component_code: nodeActivities.component.code,
                    node_id: nodeActivities.id,
                    instance_id: this.instance_id,
                    subprocess_stack: JSON.stringify(subprocessStack)
                }
            },
            // 节点 tooltip 操作
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
                } else if (classList.contains('subflow-pause-btn')) {
                    this.handleSubflowPauseClick(e)
                } else if (classList.contains('subflow-resume-btn')) {
                    this.handleSubflowResumeClick(e)
                }
            },
            handleNodeInfoPanelHide (e) {
                const classList = e.target.classList
                const isParamsBtn = classList.contains('params-btn-icon')
                const isTooltipBtn = classList.contains('tooltip-btn')
                if (!this.isNodeInfoPanelShow || isParamsBtn || isTooltipBtn) {
                    return
                }
                const NodeInfoPanel = document.querySelector('.node-info-panel')
                if (NodeInfoPanel) {
                    if (!dom.nodeContains(NodeInfoPanel, e.target)) {
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
                        this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                    }
                }
            },
            handleNodeRetryClick (e) {
                const id = e.target.dataset.id
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = 'retryNode'
                this.setNodeDetailConfig(id)
                this.updateNodeActived(id, true)
            },
            handleNodeSkipClick (e) {
                if (this.pending.skip) return
                const id = e.target.dataset.id
                const data = {
                    instance_id: this.instance_id,
                    node_id: id
                }
                const tooltipDom = e.target.parentNode.parentNode.parentNode
                this.nodeTaskSkip(tooltipDom, data)
            },
            handleNodeModifyTimeClick (e) {
                const id = e.target.dataset.id
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = 'modifyTime'
                this.setNodeDetailConfig(id)
                this.updateNodeActived(id, true)
            },
            handleGatewaySelectClick (e) {
                const id = e.target.dataset.id
                const nodeGateway = this.pipelineData.gateways[id]
                const branches = []
                for (const item in nodeGateway.conditions) {
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
                const data = {
                    instance_id: this.instance_id,
                    node_id: id,
                    data: JSON.stringify({ callback: 'resume' })
                }
                this.nodeResume(data)
            },
            handleSubflowPauseClick (e) {
                if (this.pending.subflowPause) return
                const id = e.target.dataset.id
                this.taskPause(true, id)
            },
            handleSubflowResumeClick (e) {
                if (this.pending.subflowResume) return
                const id = e.target.dataset.id
                this.taskResume(true, id)
            },
            // 设置画布数据，更新页面
            setCanvasData () {
                this.$nextTick(() => {
                    this.nodeSwitching = false
                })
            },
            getOptBtnIsClickable (action) {
                switch (action) {
                    case 'execute':
                        return this.state === 'CREATED' && this.isTopTask
                    case 'pause':
                        return this.state === 'RUNNING'
                    case 'resume':
                        return this.state === 'SUSPENDED'
                    case 'revoke':
                        return this.isTopTask
                            && (this.state === 'RUNNING'
                            || this.state === 'SUSPENDED'
                            || this.state === 'NODE_SUSPENDED'
                            || this.state === 'FAILED')
                    default:
                        break
                }
            },
            getOrderedTree (data) {
                const fstLine = data.start_event.outgoing
                const orderedData = this.retrieveLines(data, fstLine)
                return orderedData
            },
            /**
             * 根据节点连线遍历任务节点，返回按广度优先排序的节点数据
             * @param {Object} data 画布数据
             * @param {Array} line 节点连线
             *
             * @return {Array} nodes 排序后的节点
             */
            retrieveLines (data, line) {
                let nodes = []
                const { flows, activities, gateways } = data
                const curNode = data.flows[line].target
                const activityNode = activities[curNode]
                if (activityNode) {
                    const node = Object.assign({}, activityNode)
                    if (node.pipeline) {
                        node.children = this.getOrderedTree(node.pipeline)
                    }
                    nodes.push(node)
                    nodes = nodes.concat(this.retrieveLines(data, node.outgoing))
                } else {
                    const gatewayNode = gateways[curNode]
                    if (gatewayNode) {
                        if (gatewayNode.type === 'ParallelGateway' || gatewayNode.type === 'ExclusiveGateway') {
                            const gatewayLinkedNodes = []
                            gatewayNode.outgoing.forEach(line => {
                                const linkedNode = activities[flows[line].target]
                                if (linkedNode) {
                                    if (linkedNode.pipeline) {
                                        linkedNode.children = this.getOrderedTree(linkedNode.pipeline)
                                    }
                                    gatewayLinkedNodes.push(linkedNode)
                                    nodes.push(linkedNode)
                                } else {
                                    nodes = nodes.concat(this.retrieveLines(data, line))
                                }
                            })
                            gatewayLinkedNodes.forEach(node => {
                                nodes = nodes.concat(this.retrieveLines(data, node.outgoing))
                            })
                        } else if (gatewayNode.type === 'ConvergeGateway') {
                            if (gatewayNode.hasRun) {
                                gatewayNode.hasRun.push(gatewayNode.id)
                            } else {
                                gatewayNode.hasRun = [gatewayNode.id]
                            }
                            if (gatewayNode.hasRun.length === gatewayNode.incoming.length) {
                                nodes = nodes.concat(this.retrieveLines(data, gatewayNode.outgoing))
                            }
                        } else {
                            nodes = nodes.concat(this.retrieveLines(data, gatewayNode.outgoing))
                        }
                    }
                }
                return nodes
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
            updateNodeActived (id, isActived) {
                this.$refs.pipelineCanvas.onUpdateNodeInfo(id, { isActived })
            },
            // 查看参数、修改参数
            onTaskParamsClick (type) {
                if (this.nodeInfoType === type) {
                    this.isNodeInfoPanelShow = false
                    this.nodeInfoType = ''
                } else {
                    this.isNodeInfoPanelShow = true
                    this.nodeInfoType = type
                }
            },
            getTplURL () {
                let routerData = ''
                if (this.templateSource === 'business') {
                    routerData = `/template/edit/${this.cc_id}/?template_id=${this.template_id}`
                } else if (this.templateSource === 'common') {
                    routerData = `/template/home/${this.cc_id}/?common=1&common_template=common`
                }
                return routerData
            },
            onToggleNodeInfoPanel () {
                this.isNodeInfoPanelShow = false
                this.nodeInfoType = ''
                this.updateNodeActived(this.nodeDetailConfig.node_id, false)
            },
            onOperationClick (action) {
                if (this.pending.task || !this.getOptBtnIsClickable(action)) {
                    return
                }
                if (action === 'revoke') {
                    this.isRevokeDialogShow = true
                    return
                }
                this.pending.task = true
                this.activeOperation = action
                const actionType = 'task' + action.charAt(0).toUpperCase() + action.slice(1)
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
                const nodeState = this.instanceStatus.children && this.instanceStatus.children[id]
                const nodeActivities = this.pipelineData.activities[id]
                const componentCode = type === 'singleAtom' ? nodeActivities.component.code : ''
                let isPanelShow = false
                if (nodeState) {
                    if (type === 'singleAtom') {
                        // 标准插件节点执行中、完成、失败状态，点击展开详情
                        isPanelShow = ['RUNNING', 'FINISHED', 'FAILED'].indexOf(nodeState.state) > -1
                    } else {
                        // 控制节点失败时点击展开详情
                        isPanelShow = nodeState.state === 'FAILED'
                    }
                }
                if (isPanelShow) {
                    let subprocessStack = []
                    if (this.selectedFlowPath.length > 1) {
                        subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
                    }
                    this.isNodeInfoPanelShow = true
                    this.nodeInfoType = 'executeInfo'
                    if (this.nodeDetailConfig.node_id) {
                        this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                    }
                    this.nodeDetailConfig = {
                        component_code: componentCode,
                        node_id: id,
                        instance_id: this.instance_id,
                        subprocess_stack: JSON.stringify(subprocessStack)
                    }
                    this.updateNodeActived(id, true)
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
            // 面包屑点击
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
                this.isNodeInfoPanelShow = false
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
                const heirarchyList = nodeHeirarchy.split('.').splice(1)
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
                        this.treeNodeConfig = {}
                    } else { // click single task node
                        let subprocessStack = []
                        if (this.selectedFlowPath.length > 1) {
                            subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1, -1)
                        }
                        this.treeNodeConfig = {
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
                    this.treeNodeConfig = {}
                }
            },
            onRetrySuccess (id) {
                this.isNodeInfoPanelShow = false
                this.destroyTooltipInstance(id)
                this.setTaskStatusTimer()
                this.updateNodeActived(id, false)
            },
            onRetryCancel (id) {
                this.isNodeInfoPanelShow = false
                this.nodeInfoType = ''
                this.updateNodeActived(id, false)
            },
            onModifyTimeSuccess (id) {
                this.isNodeInfoPanelShow = false
                this.destroyTooltipInstance(id)
                this.setTaskStatusTimer()
                this.updateNodeActived(id, false)
            },
            onModifyTimeCancel (id) {
                this.isNodeInfoPanelShow = false
                this.nodeInfoType = ''
                this.updateNodeActived(id, false)
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
            },
            onConfirmRevokeTask () {
                this.isRevokeDialogShow = false
                this.activeOperation = 'revoke'
                this.taskRevoke()
            },
            onCancelRevokeTask () {
                this.isRevokeDialogShow = false
            },
            unclickableOperation (type) {
                // 失败时不允许点击暂停按钮，创建是不允许点击撤销按钮，操作执行过程不允许点击
                return (this.state === 'FAILED' && type !== 'revoke') || (this.state === 'CREATED' && type === 'revoke') || this.operateLoading || !this.isTopTask
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/animation/operate.scss';
.task-operation {
    position: relative;
    height: calc(100% - 118px);
    min-height: 500px;
    overflow: hidden;
    background: #f4f7fa;
    .task-status {
        height: 30px;
        line-height: 30px;
        font-size: 14px;
        color: #63656e;
        border-right: 1px solid #d2d4dd;
        text-align: center;
        background-color: #dcdee5;
        &.CREATED {
            border-top: 1px solid #d2d4dd;
            border-bottom: 1px solid #d2d4dd;
            .task-status-name {
                color: #63656e;
            }
        }
        &.FINISHED {
            background-color: #cceed9;
            border-top: 1px solid #b6e4c7;
            border-bottom: 1px solid #b6e4c7;
            .task-status-name {
                color: #2dcb56;
            }
        }
        &.RUNNING {
            background-color: #cfdffb;
            border-top: 1px solid #c0d4f8;
            border-bottom: 1px solid #c0d4f8;
            .task-status-name {
                color: #3a84ff;
            }
        }
        &.SUSPENDED, &.NODE_SUSPENDED {
            background-color: #ffe8c3;
            border-top: 1px solid #e6cfaa;
            border-bottom: 1px solid #e6cfaa;
            .task-status-name {
                color: #d78300;
            }
        }
        &.FAILED {
            background-color: #f2d0d3;
            border-top: 1px solid #efb9be;
            border-bottom: 1px solid #efb9be;
            .task-status-name {
                color: #EA3636;
            }
        }
        &.REVOKED {
            background-color: #f2d0d3;
            border-top: 1px solid #efb9be;
            border-bottom: 1px solid #efb9be;
            .task-status-name {
                color: #ea3636;
            }
        }
    }
}

/deep/ .atom-failed {
    font-size: 12px;
}
.operation-header {
    margin: 0 20px;
    height: 50px;
    line-height: 50px;
    background: #f4f7fa;
    border-top: 1px solid #cacedb;

    .bread-crumbs-wrapper {
        display: inline-block;
        font-size: 14px;
        height: 50px;
        .path-item {
            display: inline-block;
            overflow: hidden;
            &.name-ellipsis {
                max-width: 190px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            .node-name {
                margin: 0 4px;
                font-size: 14px;
                color: #3a84ff;
                cursor: pointer;
            }
            .node-ellipsis {
                margin-right: 4px;
            }
            &:first-child {
                .node-name {
                    margin-left: 0px;
                }
            }
            &:last-child {
                .node-name {
                    &:last-child {
                        color: #313238;
                        cursor: text;
                    }
                }
            }
        }
    }
    .operation-container {
        float: right;
        .task-operation-btns,
        .task-params-btns {
            float: left;
            .bk-button {
                border: none;
                background: transparent;
                cursor: pointer;
            }
            /deep/ .bk-icon {
                float: initial;
                & + span {
                    margin-left: 0;
                }
            }
        }
        .task-operation-btns {
            margin: 9px 35px 0 0;
            line-height: initial;
            border-right: 1px solid #dde4eb;
            .operation-btn {
                margin-right: 35px;
                height: 32px;
                line-height: 32px;
                font-size: 14px;
            }
            .execute-btn {
                width: 140px;
                color: #ffffff;
                background: #2dcb56 !important; // 覆盖 bk-button important 规则
                &:hover {
                    background: #1f9c40 !important; // 覆盖 bk-button important 规则
                }
                &.is-disabled {
                    color: #ffffff !important; // 覆盖 bk-button important 规则
                    opacity: 0.4;
                }
            }
            .revoke-btn {
                padding: 0;
                background: transparent !important; // 覆盖 bk-button important 规则
                color: #ea3636;
                &:hover {
                    color: #c32929;
                }
                &.is-disabled {
                    color: #d8d8d8;
                }
            }
        }
        .task-params-btns {
            .params-btn, .jump-tpl-page-btn {
                margin-right: 36px;
                padding: 0;
                color: #979ba5;
                font-size: 14px;
                &.actived {
                    color: #63656e;
                }
                &:hover {
                    color: #63656e;
                }
            }
            .jump-tpl-page-btn {
                display: inline-block;
                position: relative;
                height: 24px;
                width: 16px;
                top: 2px;
                line-height: 22px;
            }
            .solid-eye {
                font-size: 12px;
            }
            .params-btn-icon, .params-btn {
                font-size: 15px;
            }
        }
    }
}
.task-container {
    position: relative;
    width: 100%;
    height: calc(100% - 80px);
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
                background: #e1e4e8;
            }
            .tool-wrapper {
                top: 19px;
                left: 40px;
            }
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
    box-shadow: -1px 1px 8px rgba(130, 130, 130, .15), 1px -1px 8px rgba(130, 130, 130, .15);
    z-index: 4;
    .task-params-show {
        width: 750px;
        border-left: 1px solid $commonBorderColor;
    }
    .toggle-params-panel {
        position: absolute;
        top: 50%;
        left: -20px;
        margin-top: -12px;
        width: 20px;
        height: 38px;
        line-height: 38px;
        font-size: 12px;
        color: $whiteDefault;
        text-align: center;
        background: $blueDefault;
        border-right: none;
        border-radius: 4px;
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        box-shadow: -1px 1px 8px rgba(60, 150, 255, .25), 1px -1px 8px rgba(60, 150, 255, .25);
        cursor: pointer;
        transform: rotate(0);
        &:hover {
            background: #0082ff;
        }
        &.actived {
            transform: rotate(-180deg);
        }
    }
}
.node-info-panel {
    position: absolute;
    top: 50px;
    right: 0;
    width: 764px;
    height: calc(100% - 50px);
    background: $whiteDefault;
    border-top: 1px solid #dde4eb;
    border-left: 1px solid #dde4eb;
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
        background:#3c96ff;
        border-right: none;
        border-radius: 4px;
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        box-shadow: -1px 1px 8px rgba(60, 150, 255, .25), 1px -1px 8px rgba(60, 150, 255, .25);
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
    .bk-flow-canvas .tooltip .tooltip-inner {
        height: 34px;
        width: 80px;
        line-height: 34px;
        padding: 0;
    }
}
</style>
