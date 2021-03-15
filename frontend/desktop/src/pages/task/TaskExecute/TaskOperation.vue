/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-operation">
        <task-operation-header
            :node-nav="nodeNav"
            :project_id="project_id"
            :template_id="template_id"
            :template-source="templateSource"
            :node-info-type="nodeInfoType"
            :task-operation-btns="taskOperationBtns"
            :instance-actions="instanceActions"
            :admin-view="adminView"
            :is-breadcrumb-show="isBreadcrumbShow"
            :is-show-view-process="isShowViewProcess"
            :is-task-operation-btns-show="isTaskOperationBtnsShow"
            @onSelectSubflow="onSelectSubflow"
            @onOperationClick="onOperationClick"
            @onTaskParamsClick="onTaskParamsClick">
        </task-operation-header>
        <div :class="['task-status', state]">
            <span class="task-status-name">
                {{taskState}}
            </span>
        </div>
        <div class="task-container">
            <div class="pipeline-nodes">
                <TemplateCanvas
                    class="task-management-page"
                    ref="templateCanvas"
                    v-if="!nodeSwitching"
                    :editable="false"
                    :show-palette="false"
                    :canvas-data="canvasData"
                    :has-admin-perm="adminView"
                    @hook:mounted="onTemplateCanvasMounted"
                    @onNodeClick="onNodeClick"
                    @onConditionClick="onOpenConditionEdit"
                    @onRetryClick="onRetryClick"
                    @onForceFail="onForceFailClick"
                    @onSkipClick="onSkipClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onGatewaySelectionClick="onGatewaySelectionClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
                </TemplateCanvas>
            </div>
        </div>
        <bk-sideslider :is-show.sync="isNodeInfoPanelShow" :width="798" :quick-close="quickClose" @hidden="onHiddenSideslider">
            <div slot="header">{{sideSliderTitle}}</div>
            <div class="node-info-panel" ref="nodeInfoPanel" v-if="isNodeInfoPanelShow" slot="content">
                <ModifyParams
                    v-if="nodeInfoType === 'modifyParams'"
                    :params-can-be-modify="paramsCanBeModify"
                    :instance-actions="instanceActions"
                    :instance-name="instanceName"
                    :instance_id="instance_id"
                    @packUp="packUp">
                </ModifyParams>
                <ExecuteInfo
                    v-if="nodeInfoType === 'executeInfo' || nodeInfoType === 'viewNodeDetails'"
                    :state="state"
                    :node-data="nodeData"
                    :selected-flow-path="selectedFlowPath"
                    :admin-view="adminView"
                    :pipeline-data="pipelineData"
                    :default-active-id="defaultActiveId"
                    :node-detail-config="nodeDetailConfig"
                    @onRetryClick="onRetryClick"
                    @onSkipClick="onSkipClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onForceFail="onForceFailClick"
                    @onClickTreeNode="onClickTreeNode">
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
                <OperationFlow
                    v-if="nodeInfoType === 'operateFlow'"
                    class="operation-flow">
                </OperationFlow>
                <TaskInfo
                    v-if="nodeInfoType === 'taskExecuteInfo'"
                    :task-id="instance_id">
                </TaskInfo>
                <TemplateData
                    v-if="nodeInfoType === 'templateData'"
                    :template-data="templateData"
                    @onshutDown="onshutDown">
                </TemplateData>
            </div>
        </bk-sideslider>
        <gatewaySelectDialog
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
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            header-position="left"
            :mask-close="false"
            :auto-close="false"
            :title="$t('跳过节点')"
            :loading="pending.skip"
            :value="isSkipDialogShow"
            @confirm="nodeTaskSkip(skipNodeId)"
            @cancel="onSkipCancel">
            <div class="leave-tips" style="padding: 30px 20px;">{{ $t('是否跳过该任务节点？') }}</div>
        </bk-dialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            header-position="left"
            :mask-close="false"
            :auto-close="false"
            :title="$t('强制失败')"
            :loading="pending.forceFail"
            :value="isForceFailDialogShow"
            @confirm="nodeForceFail(forceFailId)"
            @cancel="onForceFailCancel">
            <div class="leave-tips" style="padding: 30px 20px;">{{ $t('是否将该任务节点强制执行失败？') }}</div>
        </bk-dialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            header-position="left"
            :mask-close="false"
            :auto-close="false"
            :title="$t('继续执行')"
            :loading="pending.parseNodeResume"
            :value="isNodeResumeDialogShow"
            @confirm="nodeResume(nodeResumeId)"
            @cancel="onTaskNodeResumeCancel">
            <div class="leave-tips" style="padding: 30px 20px;">{{ $t('是否完成暂停节点继续向后执行？') }}</div>
        </bk-dialog>
        <condition-edit
            ref="conditionEdit"
            :is-readonly="true"
            :is-show.sync="isShowConditionEdit"
            :condition-data="conditionData">
        </condition-edit>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import axios from 'axios'
    import tools from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { TASK_STATE_DICT } from '@/constants/index.js'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import ModifyParams from './ModifyParams.vue'
    import ExecuteInfo from './ExecuteInfo.vue'
    import RetryNode from './RetryNode.vue'
    import ModifyTime from './ModifyTime.vue'
    import OperationFlow from './OperationFlow.vue'
    import TaskInfo from './TaskInfo.vue'
    import gatewaySelectDialog from './GatewaySelectDialog.vue'
    import revokeDialog from './revokeDialog.vue'
    import permission from '@/mixins/permission.js'
    import TaskOperationHeader from './TaskOperationHeader'
    import TemplateData from './TemplateData'
    import ConditionEdit from '../../template/TemplateEdit/ConditionEdit.vue'

    const CancelToken = axios.CancelToken
    let source = CancelToken.source()

    const TASK_OPERATIONS = {
        execute: {
            action: 'execute',
            icon: 'common-icon-right-triangle',
            text: i18n.t('执行')
        },
        pause: {
            action: 'pause',
            icon: 'common-icon-double-vertical-line',
            text: i18n.t('暂停')
        },
        resume: {
            action: 'resume',
            icon: 'common-icon-right-triangle',
            text: i18n.t('继续')
        },
        revoke: {
            action: 'revoke',
            icon: 'common-icon-return-arrow',
            text: i18n.t('撤销')
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
            TemplateCanvas,
            ModifyParams,
            ExecuteInfo,
            RetryNode,
            ModifyTime,
            OperationFlow,
            TaskInfo,
            gatewaySelectDialog,
            revokeDialog,
            TaskOperationHeader,
            TemplateData,
            ConditionEdit
        },
        mixins: [permission],
        props: {
            project_id: [Number, String],
            instance_id: [Number, String],
            instanceFlow: String,
            instanceName: String,
            template_id: [Number, String],
            templateSource: String,
            instanceActions: Array,
            routerType: String
        },
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
                templateData: '', // 模板数据
                defaultActiveId: '',
                locations: [],
                setNodeDetail: true,
                atomList: [],
                quickClose: true,
                sideSliderTitle: '',
                taskId: this.instance_id,
                isNodeInfoPanelShow: false,
                nodeInfoType: '',
                state: '',
                selectedNodeId: '',
                selectedFlowPath: path, // 选择面包屑路径
                cacheStatus: undefined, // 总任务缓存状态信息；只有总任务完成、撤销时才存在
                instanceStatus: {},
                taskParamsType: '',
                timer: null,
                pipelineData: pipelineData,
                treeNodeConfig: {},
                nodeDetailConfig: {},
                nodeSwitching: false,
                isGatewaySelectDialogShow: false,
                gatewayBranches: [],
                canvasMountedQueues: [], // canvas pending queues
                pending: {
                    skip: false,
                    forceFail: false,
                    selectGateway: false,
                    task: false,
                    parseNodeResume: false,
                    subflowPause: false,
                    subflowResume: false
                },
                activeOperation: '', // 当前任务操作（头部区域操作按钮触发）
                isRevokeDialogShow: false,
                isSkipDialogShow: false,
                skipNodeId: undefined,
                isForceFailDialogShow: false,
                forceFailId: undefined,
                isNodeResumeDialogShow: false,
                nodeResumeId: undefined,
                operateLoading: false,
                retrievedCovergeGateways: [], // 遍历过的汇聚节点
                pollErrorTimes: 0, // 任务状态查询异常连续三次后，停止轮询
                isShowConditionEdit: false, // 条件分支侧栏
                conditionData: {}
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                hasAdminPerm: state => state.hasAdminPerm
            }),
            ...mapState('project', {
                projectId: state => state.project_id,
                projectName: state => state.projectName
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
                const { line, location, gateways, activities } = this.pipelineData
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
                        const code = item.type === 'tasknode' ? activities[item.id].component.code : ''
                        return { ...item, mode: 'execute', checked: true, code }
                    }),
                    branchConditions
                }
            },
            nodeData () {
                return [{
                    id: this.instance_id,
                    name: this.instanceName,
                    title: this.instanceName,
                    expanded: true,
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
            // 职能化/审计中心/轻应用时,隐藏[查看流程]按钮
            isShowViewProcess () {
                return !['function', 'audit'].includes(this.routerType) && this.view_mode !== 'appmaker'
            },
            adminView () {
                return this.hasAdminPerm && this.$route.query.is_admin === 'true'
            }
        },
        mounted () {
            this.loadTaskStatus()
            this.getSingleAtomList()
        },
        beforeDestroy () {
            if (source) {
                source.cancel('cancelled')
            }
            this.cancelTaskStatusTimer()
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
                'pauseNodeResume',
                'getNodeActInfo',
                'forceFail'
            ]),
            ...mapActions('atomForm/', [
                'loadSingleAtomList'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeForceFail'
            ]),
            async loadTaskStatus () {
                try {
                    this.$emit('taskStatusLoadChange', true)
                    let instanceStatus = {}
                    if (['FINISHED', 'REVOKED'].includes(this.state) && this.cacheStatus && this.cacheStatus.children[this.taskId]) { // 总任务：完成/撤销时,取实例缓存数据
                        instanceStatus = await this.getGlobalCacheStatus(this.taskId)
                    } else if (
                        this.instanceStatus.state
                        && this.instanceStatus.state === 'FINISHED' // 任务实例才会出现撤销，子流程不存在
                        && this.instanceStatus.children
                        && this.instanceStatus.children[this.taskId]
                    ) { // 局部：完成时，取局部缓存数据
                        instanceStatus = await this.getLocalCacheStatus()
                    } else {
                        if (source) {
                            source.cancel('cancelled') // 取消定时器里已经执行的请求
                        }
                        source = CancelToken.source()
                        const data = {
                            instance_id: this.taskId,
                            project_id: this.project_id,
                            cancelToken: source.token
                        }
                        if (this.selectedFlowPath.length > 1 && this.selectedFlowPath[1].type !== 'ServiceActivity') {
                            data.instance_id = this.instance_id
                            data.subprocess_id = this.taskId
                        }
                        instanceStatus = await this.getInstanceStatus(data)
                    }
                    // 处理返回数据
                    if (instanceStatus.result) {
                        this.state = instanceStatus.data.state
                        this.instanceStatus = instanceStatus.data
                        this.pollErrorTimes = 0

                        if (
                            !this.cacheStatus
                            && ['FINISHED', 'REVOKED'].includes(this.state)
                            && this.taskId === this.instance_id
                        ) { // save cacheStatus
                            this.cacheStatus = instanceStatus.data
                        }
                        if (this.state === 'RUNNING') {
                            this.setTaskStatusTimer()
                        }
                        this.updateNodeInfo()
                    } else {
                        this.pollErrorTimes += 1
                        if (this.pollErrorTimes > 2) {
                            this.cancelTaskStatusTimer()
                        } else {
                            this.setTaskStatusTimer()
                        }
                        errorHandler(instanceStatus, this)
                    }
                } catch (e) {
                    this.cancelTaskStatusTimer()
                    if (e.message !== 'cancelled') {
                        errorHandler(e, this)
                    }
                } finally {
                    source = null
                    this.$emit('taskStatusLoadChange', false)
                }
            },
            /**
             * 加载标准插件列表
             */
            async getSingleAtomList () {
                try {
                    const params = {}
                    if (!this.common) {
                        params.project_id = this.project_id
                    }
                    const data = await this.loadSingleAtomList(params)
                    const atomList = []
                    data.forEach(item => {
                        const atom = atomList.find(atom => atom.code === item.code)
                        if (atom) {
                            atom.list.push(item)
                        } else {
                            const { code, desc, name, group_name, group_icon } = item
                            atomList.push({
                                code,
                                desc,
                                name,
                                group_name,
                                group_icon,
                                type: group_name,
                                list: [item]
                            })
                        }
                    })
                    this.atomList = atomList
                    this.markNodesPhase()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.singleAtomListLoading = false
                }
            },
            /**
             * 标记任务节点的生命周期
             */
            markNodesPhase () {
                Object.keys(this.pipelineData.activities).forEach(id => {
                    const node = this.pipelineData.activities[id]
                    if (node.type === 'ServiceActivity') {
                        let atom = ''
                        this.atomList.some(group => {
                            if (group.code === node.component.code) {
                                return group.list.some(item => {
                                    if (item.version === (node.component.version || 'legacy')) {
                                        atom = item
                                    }
                                })
                            }
                        })
                        if (atom) {
                            this.$refs.templateCanvas.onUpdateNodeInfo(node.id, { phase: atom.phase })
                        }
                    }
                })
            },
            /**
             * 从总任务实例状态信息中取数据
             */
            getGlobalCacheStatus (taskId) {
                return new Promise((resolve) => {
                    const levels = this.nodeNav.map(nav => nav.id).slice(1)
                    let instanStatus = tools.deepClone(this.cacheStatus)
                    levels.forEach(subNodeId => {
                        instanStatus = instanStatus.children[subNodeId]
                    })
                    setTimeout(() => {
                        resolve({
                            data: instanStatus,
                            result: true
                        })
                    }, 0)
                })
            },
            /**
             * 获取局部（子流程）缓存状态数据
             * @description
             * 待jsFlow更新 updateCanvas 方法解决后删除异步代码，
             * 然后使用 updateCanvas 替代 v-if
             */
            getLocalCacheStatus () {
                return new Promise((resolve) => {
                    const cacheStatus = this.instanceStatus.children
                    setTimeout(() => {
                        resolve({
                            data: cacheStatus[this.taskId],
                            result: true
                        })
                    }, 0)
                })
            },
            async taskExecute () {
                try {
                    const res = await this.instanceStart(this.instance_id)
                    if (res.result) {
                        this.state = 'RUNNING'
                        this.setTaskStatusTimer()
                        this.$bkMessage({
                            message: i18n.t('任务开始执行'),
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
                            message: i18n.t('任务暂停成功'),
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
                            message: i18n.t('任务继续成功'),
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
                        this.state = 'REVOKED'
                        this.$bkMessage({
                            message: i18n.t('任务撤销成功'),
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
            async nodeTaskSkip (id) {
                if (this.pending.skip) {
                    return
                }

                this.pending.skip = true
                try {
                    const data = {
                        instance_id: this.instance_id,
                        node_id: id
                    }
                    const res = await this.instanceNodeSkip(data)
                    if (res.result) {
                        this.isNodeInfoPanelShow = false
                        this.isSkipDialogShow = false
                        this.nodeInfoType = ''
                        this.skipNodeId = undefined
                        this.$bkMessage({
                            message: i18n.t('跳过成功'),
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
                    this.pending.skip = false
                }
            },
            async nodeForceFail (id) {
                if (this.pending.forceFail) {
                    return
                }
                this.pending.forceFail = true
                try {
                    const params = {
                        node_id: id,
                        task_id: Number(this.instance_id)
                    }
                    const res = await this.forceFail(params)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('强制失败执行成功'),
                            theme: 'success'
                        })
                        this.isForceFailDialogShow = false
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
                        this.forceFailId = undefined
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.forceFail = false
                }
            },
            async selectGatewayBranch (data) {
                this.pending.selectGateway = true
                try {
                    const res = await this.skipExclusiveGateway(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('跳过成功'),
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
                    this.pending.selectGateway = false
                }
            },
            async nodeResume (id) {
                if (this.pending.parseNodeResume) {
                    return
                }
                this.pending.parseNodeResume = true
                try {
                    const data = {
                        instance_id: this.instance_id,
                        node_id: id,
                        data: { callback: 'resume' }
                    }
                    const res = await this.pauseNodeResume(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('继续成功'),
                            theme: 'success'
                        })
                        this.isNodeResumeDialogShow = false
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
                        this.nodeResumeId = undefined
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
            async updateTaskStatus (id) {
                this.taskId = id
                this.setCanvasData()
                await this.loadTaskStatus()
            },
            // 更新节点状态
            updateNodeInfo () {
                const nodes = this.instanceStatus.children
                for (const id in nodes) {
                    let code, skippable, retryable
                    const currentNode = nodes[id]
                    const nodeActivities = this.pipelineData.activities[id]

                    if (nodeActivities) {
                        code = nodeActivities.component ? nodeActivities.component.code : ''
                        skippable = nodeActivities.isSkipped || nodeActivities.skippable
                        retryable = nodeActivities.can_retry || nodeActivities.retryable
                    }

                    const data = { status: currentNode.state, code, skippable, retryable, skip: currentNode.skip, retry: currentNode.retry }

                    this.setTaskNodeStatus(id, data)
                }
            },
            setTaskNodeStatus (id, data) {
                this.$refs.templateCanvas && this.$refs.templateCanvas.onUpdateNodeInfo(id, data)
            },
            async setNodeDetailConfig (id, firstNodeData) {
                const nodeActivities = firstNodeData || this.pipelineData.activities[id]
                let subprocessStack = []
                if (this.selectedFlowPath.length > 1) {
                    subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
                }
                this.nodeDetailConfig = {
                    component_code: nodeActivities.component.code,
                    version: nodeActivities.component.version || 'legacy',
                    node_id: nodeActivities.id,
                    instance_id: this.instance_id,
                    subprocess_stack: JSON.stringify(subprocessStack)
                }
            },
            onRetryClick (id) {
                this.onSidesliderConfig('retryNode', i18n.t('重试'))
                this.setNodeDetailConfig(id)
            },
            onSkipClick (id) {
                this.isSkipDialogShow = true
                this.skipNodeId = id
            },
            onSkipCancel () {
                this.isSkipDialogShow = false
                this.skipNodeId = undefined
            },
            onForceFailClick (id) {
                this.forceFailId = id
                this.isForceFailDialogShow = true
            },
            onForceFailCancel () {
                this.isForceFailDialogShow = false
                this.forceFailId = undefined
            },
            onModifyTimeClick (id) {
                this.onSidesliderConfig('modifyTime', i18n.t('修改时间'))
                this.setNodeDetailConfig(id)
            },
            onGatewaySelectionClick (id) {
                const nodeGateway = this.pipelineData.gateways[id]
                const branches = []
                for (const item in nodeGateway.conditions) {
                    branches.push({
                        id: item,
                        node_id: id,
                        name: nodeGateway.conditions[item].name || nodeGateway.conditions[item].evaluate
                    })
                }
                this.gatewayBranches = branches
                this.isGatewaySelectDialogShow = true
            },
            onTaskNodeResumeClick (id) {
                this.nodeResumeId = id
                this.isNodeResumeDialogShow = true
            },
            onTaskNodeResumeCancel () {
                this.isNodeResumeDialogShow = false
                this.nodeResumeId = undefined
            },
            onSubflowPauseResumeClick (id, value) {
                if (this.pending.subflowPause) return
                value === 'pause' ? this.taskPause(true, id) : this.taskResume(true, id)
            },
            // 设置画布数据，更新页面
            setCanvasData () {
                this.$nextTick(() => {
                    this.nodeSwitching = false
                    this.$nextTick(() => {
                        this.markNodesPhase()
                    })
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
                const orderedData = []
                const passedNodes = []
                this.retrieveLines(data, fstLine, orderedData, passedNodes)
                orderedData.sort((a, b) => a.level - b.level)
                return orderedData
            },
            /**
             * 根据节点连线遍历任务节点，返回按广度优先排序的节点数据
             * @param {Object} data 画布数据
             * @param {Array} lineId 连线ID
             * @param {Array} ordered 排序后的节点数据
             * @param {Array} passedNodes 遍历过的节点
             * @param {Number} level 任务节点与开始节点的距离
             *
             */
            retrieveLines (data, lineId, ordered, passedNodes, level = 0) {
                const { activities, gateways, flows } = data
                const currentNode = flows[lineId].target
                const activity = activities[currentNode]
                const gateway = gateways[currentNode]
                const node = activity || gateway

                if (node && !passedNodes.includes(node.id)) {
                    passedNodes.push(node.id)

                    if (activity) {
                        const isExistInList = ordered.find(item => item.id === activity.id)
                        if (!isExistInList) {
                            if (activity.pipeline) {
                                activity.children = this.getOrderedTree(activity.pipeline)
                            }
                            activity.level = level
                            activity.title = activity.name
                            activity.expanded = activity.pipeline
                            ordered.push(activity)
                        }
                    }

                    const outgoing = Array.isArray(node.outgoing) ? node.outgoing : [node.outgoing]
                    // 分支网关
                    if (gateway) {
                        level += 1
                    }
                    outgoing.forEach((line, index, arr) => {
                        this.retrieveLines(data, line, ordered, passedNodes, level)
                    })
                }
            },
            updateNodeActived (id, isActived) {
                this.$refs.templateCanvas.onUpdateNodeInfo(id, { isActived })
            },
            // 查看参数、修改参数 （侧滑面板 标题 点击遮罩关闭）
            onTaskParamsClick (type, name) {
                if (type === 'viewNodeDetails') {
                    let nodeData = tools.deepClone(this.nodeData)
                    let firstNodeId = null
                    let firstNodeData = null
                    const rootNode = []
                    while (nodeData[0]) {
                        if (nodeData[0].type && nodeData[0].type === 'ServiceActivity') {
                            firstNodeId = nodeData[0].id
                            firstNodeData = nodeData[0]
                            nodeData[0] = false
                        } else {
                            rootNode.push(nodeData[0])
                            nodeData = nodeData[0].children
                        }
                    }
                    this.defaultActiveId = firstNodeId
                    let subprocessStack = []
                    if (rootNode.length > 1) {
                        subprocessStack = rootNode.map(item => item.id).slice(1)
                    }
                    this.nodeDetailConfig = {
                        component_code: firstNodeData.component.code,
                        version: firstNodeData.component.version || 'legacy',
                        node_id: firstNodeData.id,
                        instance_id: this.instance_id,
                        subprocess_stack: JSON.stringify(subprocessStack)
                    }
                }
                if (type === 'templateData') {
                    this.templateData = JSON.stringify(this.pipelineData, null, 4)
                }
                this.onSidesliderConfig(type, name)
            },
            // 侧滑面板配置
            onSidesliderConfig (type, name) {
                this.sideSliderTitle = name
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = type
                this.quickClose = true
                if (['retryNode', 'modifyTime', 'modifyParams'].includes(type)) {
                    this.quickClose = false
                }
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

                if (!this.hasPermission(['task_operate'], this.instanceActions)) {
                    const resourceData = {
                        task: [{
                            id: this.instance_id,
                            name: this.instanceName
                        }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['task_operate'], this.instanceActions, resourceData)
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
            onNodeClick (id, type) {
                this.defaultActiveId = id
                if (type === 'tasknode') {
                    this.handleSingleNodeClick(id, 'singleAtom')
                } else if (type === 'subflow') {
                    this.handleSubflowAtomClick(id)
                } else {
                    this.handleSingleNodeClick(id, 'controlNode')
                }
            },
            handleSingleNodeClick (id, type) {
                // 节点执行状态
                const nodeState = this.instanceStatus.children && this.instanceStatus.children[id]
                // 任务节点
                if (type === 'singleAtom') {
                    // updateNodeActived 设置节点选中态
                    if (this.nodeDetailConfig.node_id) {
                        this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                    }
                    this.setNodeDetailConfig(id)
                    this.onSidesliderConfig('executeInfo', i18n.t('节点参数'))
                    this.updateNodeActived(id, true)
                } else {
                    // 分支网关节点失败时展开侧滑面板
                    if (nodeState && nodeState.state === 'FAILED') {
                        let subprocessStack = []
                        if (this.selectedFlowPath.length > 1) {
                            subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
                        }
                        this.nodeDetailConfig = {
                            component_code: '',
                            version: undefined,
                            node_id: id,
                            instance_id: this.instance_id,
                            subprocess_stack: JSON.stringify(subprocessStack)
                        }
                        this.onSidesliderConfig('executeInfo', i18n.t('节点参数'))
                    }
                }
            },
            onOpenConditionEdit (data) {
                this.isShowConditionEdit = true
                this.conditionData = { ...data }
            },
            handleSubflowAtomClick (id) {
                this.cancelTaskStatusTimer()
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
                this.cancelTaskStatusTimer()
                this.updateTaskStatus(id)
            },
            async onClickTreeNode (nodeHeirarchy, selectNodeId, nodeType) {
                let nodeActivities
                let parentNodeActivities
                const nodePath = [{
                    id: this.instance_id,
                    name: this.instanceName,
                    nodeId: this.completePipelineData.id
                }]
                if (this.nodeDetailConfig.node_id) {
                    this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                }
                const heirarchyList = nodeHeirarchy.split('.').reverse().splice(1)
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
                        if (nodeActivities.type === 'SubProcess') {
                            parentNodeActivities = nodeActivities
                        }
                    })
                    this.selectedFlowPath = nodePath
                    if (nodeActivities.type === 'SubProcess') {
                        await this.switchCanvasView(nodeActivities)
                        this.treeNodeConfig = {}
                    } else {
                        if (parentNodeActivities && parentNodeActivities.id !== this.taskId) { // 不在当前 taskId 的任务中
                            await this.switchCanvasView(parentNodeActivities)
                        } else if (!parentNodeActivities && this.taskId !== this.instance_id) { // 属于第二级任务
                            await this.switchCanvasView(this.completePipelineData, true)
                        }
                        let subprocessStack = []
                        if (this.selectedFlowPath.length > 1) {
                            subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1, -1)
                        }
                        this.treeNodeConfig = {
                            component_code: nodeActivities.component.code,
                            version: nodeActivities.component.version || 'legacy',
                            node_id: nodeActivities.id,
                            instance_id: this.instance_id,
                            subprocess_stack: JSON.stringify(subprocessStack)
                        }
                        this.updataNodeParamsInfo(nodeActivities)
                    }
                } else {
                    this.selectedFlowPath = nodePath
                    await this.switchCanvasView(this.completePipelineData, true)
                    this.treeNodeConfig = {}
                }
                if (nodeType !== 'subflow') {
                    this.setNodeDetailConfig(selectNodeId)
                }
                this.updateNodeActived(selectNodeId, true)
            },
            // 切换画布视图
            async switchCanvasView (nodeActivities, isRootNode = false) {
                const id = isRootNode ? this.instance_id : nodeActivities.id
                this.nodeSwitching = true
                this.pipelineData = isRootNode ? nodeActivities : nodeActivities.pipeline
                this.cancelTaskStatusTimer()
                await this.updateTaskStatus(id)
                this.locations = this.canvasData.locations
            },
            // 更新节点的参数面板信息
            updataNodeParamsInfo (nodeActivities) {
                let subprocessStack = []
                if (this.selectedFlowPath.length > 1) {
                    subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1, -1)
                }
                this.treeNodeConfig = {
                    component_code: nodeActivities.component.code,
                    version: nodeActivities.component.version || 'legacy',
                    node_id: nodeActivities.id,
                    instance_id: this.instance_id,
                    subprocess_stack: JSON.stringify(subprocessStack),
                    name: nodeActivities.name
                }
                this.cancelSelectedNode(this.selectedNodeId)
                this.addSelectedNode(nodeActivities.id)
            },
            // 添加选中节点
            addSelectedNode (nodeId) {
                this.selectedNodeId = nodeId
                if (this.$refs.templateCanvas && this.nodeSwitching === false) {
                    this.$refs.templateCanvas.toggleSelectedNode(nodeId, true)
                    return
                }
                this.addToCanvasQueues(() => {
                    this.$refs.templateCanvas.toggleSelectedNode(nodeId, true)
                }, [nodeId])
            },
            cancelSelectedNode (nodeId) {
                const canvasTempalte = this.$refs.templateCanvas
                canvasTempalte && canvasTempalte.toggleSelectedNode(nodeId, false)
            },
            /**
             * 往画布组件队列中添加待执行事件
             * @param {Function} func -事件
             * @param {Array} params -事件参数
             */
            addToCanvasQueues (func, params) {
                this.canvasMountedQueues.push({
                    params: params,
                    func
                })
            },
            // 下次画布组件更新后执行队列
            onTemplateCanvasMounted () {
                this.canvasMountedQueues.forEach(action => {
                    action.func.apply(this, action.params)
                })
                this.canvasMountedQueues = []
            },
            onRetrySuccess (id) {
                this.isNodeInfoPanelShow = false
                this.setTaskStatusTimer()
                this.updateNodeActived(id, false)
            },
            onRetryCancel (id) {
                this.isNodeInfoPanelShow = false
                this.updateNodeActived(id, false)
            },
            onModifyTimeSuccess (id) {
                this.isNodeInfoPanelShow = false
                this.setTaskStatusTimer()
                this.updateNodeActived(id, false)
            },
            onModifyTimeCancel (id) {
                this.isNodeInfoPanelShow = false
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
            },
            packUp () {
                this.isNodeInfoPanelShow = false
            },
            onshutDown () {
                this.isNodeInfoPanelShow = false
                this.templateData = ''
            },
            onHiddenSideslider () {
                this.nodeInfoType = ''
                this.updateNodeActived(this.nodeDetailConfig.node_id, false)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/animation/operate.scss';
.task-operation {
    position: relative;
    height: 100%;
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
        &.RUNNING,
        &.READY {
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
                color: #ea3636;
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
        .task-management-page {
            /deep/ .canvas-wrapper.jsflow .jtk-endpoint {
                z-index: 2 !important;
            }
        }
    }
}
/deep/.bk-sideslider-content {
    height: calc(100% - 60px);
}
.node-info-panel {
    height: 100%;
    .operation-flow {
        padding: 20px 30px;
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
        line-height: 1;
        box-sizing: content-box;
    }
}
</style>
