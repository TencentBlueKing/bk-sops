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
            :engine-ver="engineVer"
            :state-str="taskState"
            :state="state"
            :is-breadcrumb-show="isBreadcrumbShow"
            :is-show-view-process="isShowViewProcess"
            :is-task-operation-btns-show="isTaskOperationBtnsShow"
            @onSelectSubflow="onSelectSubflow"
            @onOperationClick="onOperationClick"
            @onTaskParamsClick="onTaskParamsClick"
            @onInjectGlobalVariable="onInjectGlobalVariable">
        </task-operation-header>
        <bk-alert v-if="isFailedSubproceeNodeInfo" type="error" class="subprocess-failed-tips">
            <template slot="title">
                <span>{{ $t('存在子流程节点执行失败，可从节点执行记录去往子任务处理，并及时') }}</span>
                <bk-link theme="primary" @click="handleRefreshTaskStatus">{{ $t('刷新任务状态') }}</bk-link>
                {{ $t('。') }}
            </template>
        </bk-alert>
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
                    :node-exec-record-info="nodeExecRecordInfo"
                    @hook:mounted="onTemplateCanvasMounted"
                    @onNodeClick="onNodeClick"
                    @onConditionClick="onOpenConditionEdit"
                    @onRetryClick="onRetryClick"
                    @onForceFail="onForceFailClick"
                    @onSkipClick="onSkipClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onGatewaySelectionClick="onGatewaySelectionClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @onApprovalClick="onApprovalClick"
                    @nodeExecRecord="onNodeExecRecord"
                    @closeNodeExecRecord="onCloseNodeExecRecord"
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
                </TemplateCanvas>
            </div>
        </div>
        <bk-sideslider :is-show.sync="isNodeInfoPanelShow" :width="960" :quick-close="true" @hidden="onHiddenSideslider" :before-close="onBeforeClose">
            <div slot="header">{{sideSliderTitle}}</div>
            <div class="node-info-panel" ref="nodeInfoPanel" v-if="isNodeInfoPanelShow" slot="content">
                <ModifyParams
                    ref="modifyParams"
                    v-if="nodeInfoType === 'modifyParams'"
                    :state="state"
                    :params-can-be-modify="paramsCanBeModify"
                    :instance-actions="instanceActions"
                    :instance-name="instanceName"
                    :instance_id="instance_id"
                    :retry-node-id="retryNodeId"
                    @nodeTaskRetry="nodeTaskRetry"
                    @packUp="packUp">
                </ModifyParams>
                <ExecuteInfo
                    v-if="nodeInfoType === 'executeInfo' || nodeInfoType === 'viewNodeDetails'"
                    :state="state"
                    :node-data="nodeData"
                    :engine-ver="engineVer"
                    :selected-flow-path="selectedFlowPath"
                    :admin-view="adminView"
                    :pipeline-data="nodePipelineData"
                    :default-active-id="defaultActiveId"
                    :node-detail-config="nodeDetailConfig"
                    @onRetryClick="onRetryClick"
                    @onSkipClick="onSkipClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @onModifyTimeClick="onModifyTimeClick"
                    @onForceFail="onForceFailClick"
                    @onApprovalClick="onApprovalClick"
                    @onClickTreeNode="onClickTreeNode">
                </ExecuteInfo>
                <RetryNode
                    ref="retryNode"
                    v-if="nodeInfoType === 'retryNode'"
                    :node-detail-config="nodeDetailConfig"
                    :engine-ver="engineVer"
                    :node-info="nodeInfo"
                    :retrying="pending.retry"
                    :node-inputs="nodeInputs"
                    @retrySuccess="onRetrySuccess"
                    @retryCancel="onRetryCancel">
                </RetryNode>
                <ModifyTime
                    ref="modifyTime"
                    v-if="nodeInfoType === 'modifyTime'"
                    :node-detail-config="nodeDetailConfig"
                    @modifyTimeSuccess="onModifyTimeSuccess"
                    @modifyTimeCancel="onModifyTimeCancel">
                </ModifyTime>
                <OperationFlow
                    :locations="canvasData.locations"
                    v-if="nodeInfoType === 'operateFlow'"
                    class="operation-flow">
                </OperationFlow>
                <GlobalVariable
                    v-if="nodeInfoType === 'globalVariable'"
                    :task-id="instance_id">
                </GlobalVariable>
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
            :is-cond-parallel-gw="isCondParallelGw"
            :gateway-branches="gatewayBranches"
            @onConfirm="onConfirmGatewaySelect"
            @onCancel="onCancelGatewaySelect">
        </gatewaySelectDialog>
        <revokeDialog
            :is-revoke-dialog-show="isRevokeDialogShow"
            @onConfirmRevokeTask="onConfirmRevokeTask"
            @onCancelRevokeTask="onCancelRevokeTask">
        </revokeDialog>
        <injectVariableDialog
            :is-inject-var-dialog-show="isInjectVarDialogShow"
            @onConfirmInjectVar="onConfirmInjectVar"
            @onCancelInjectVar="onCancelInjectVar">
        </injectVariableDialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            header-position="left"
            :mask-close="false"
            :auto-close="false"
            :title="$t('跳过节点')"
            :loading="pending.skip"
            :value="isSkipDialogShow"
            data-test-id="taskExcute_dialog_skipNodeDialog"
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
            data-test-id="taskExcute_dialog_forceFailDialog"
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
            data-test-id="taskExcute_dialog_resumeDialog"
            @confirm="nodeResume(nodeResumeId)"
            @cancel="onTaskNodeResumeCancel">
            <div class="leave-tips" style="padding: 30px 20px;">{{ $t('是否完成暂停节点继续向后执行？') }}</div>
        </bk-dialog>
        <condition-edit
            v-if="isShowConditionEdit"
            ref="conditionEdit"
            :is-readonly="true"
            :is-show.sync="isShowConditionEdit"
            :gateways="pipelineData.gateways"
            :condition-data="conditionData"
            @close="onCloseConfigPanel">
        </condition-edit>
        <bk-dialog
            width="600"
            :theme="'primary'"
            :mask-close="false"
            :auto-close="false"
            header-position="left"
            :title="$t('审批')"
            :loading="approval.pending"
            :value="approval.dialogShow"
            @confirm="onApprovalConfirm"
            @cancel="onApprovalCancel">
            <bk-form
                ref="approvalForm"
                class="approval-dialog-content"
                form-type="vertical"
                :model="approval"
                :rules="approval.rules">
                <bk-form-item label="审批意见" :required="true">
                    <bk-radio-group v-model="approval.is_passed" @change="$refs.approvalForm.clearError()">
                        <bk-radio :value="true">{{ $t('通过') }}</bk-radio>
                        <bk-radio :value="false">{{ $t('拒绝') }}</bk-radio>
                    </bk-radio-group>
                </bk-form-item>
                <bk-form-item label="备注" property="message" :required="!approval.is_passed">
                    <bk-input v-model="approval.message" type="textarea" :row="4"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState } from 'vuex'
    import axios from 'axios'
    import tools from '@/utils/tools.js'
    import { TASK_STATE_DICT, NODE_DICT } from '@/constants/index.js'
    import dom from '@/utils/dom.js'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import ModifyParams from './ModifyParams.vue'
    import ExecuteInfo from './ExecuteInfo.vue'
    import RetryNode from './RetryNode.vue'
    import ModifyTime from './ModifyTime.vue'
    import OperationFlow from './OperationFlow.vue'
    import GlobalVariable from './GlobalVariable.vue'
    import TaskInfo from './TaskInfo.vue'
    import gatewaySelectDialog from './GatewaySelectDialog.vue'
    import revokeDialog from './revokeDialog.vue'
    import permission from '@/mixins/permission.js'
    import TaskOperationHeader from './TaskOperationHeader'
    import TemplateData from './TemplateData'
    import ConditionEdit from '../../template/TemplateEdit/ConditionEdit.vue'
    import injectVariableDialog from './InjectVariableDialog.vue'

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
            GlobalVariable,
            TaskInfo,
            gatewaySelectDialog,
            revokeDialog,
            TaskOperationHeader,
            TemplateData,
            ConditionEdit,
            injectVariableDialog
        },
        mixins: [permission],
        props: {
            project_id: [Number, String],
            instance_id: [Number, String],
            engineVer: Number,
            instanceFlow: String,
            instanceName: String,
            template_id: [Number, String],
            templateSource: String,
            instanceActions: Array,
            routerType: String
        },
        data () {
            const $this = this
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
                sideSliderTitle: '',
                taskId: this.instance_id,
                isNodeInfoPanelShow: false,
                nodeInfoType: '',
                state: '', // 当前流程状态，画布切换时会更新
                rootState: '', // 根流程状态
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
                isCondParallelGw: false,
                gatewayBranches: [],
                canvasMountedQueues: [], // canvas pending queues
                pending: {
                    skip: false,
                    retry: false,
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
                retryNodeId: undefined,
                isForceFailDialogShow: false,
                forceFailId: undefined,
                isNodeResumeDialogShow: false,
                nodeResumeId: undefined,
                operateLoading: false,
                retrievedCovergeGateways: [], // 遍历过的汇聚节点
                pollErrorTimes: 0, // 任务状态查询异常连续三次后，停止轮询
                isShowConditionEdit: false, // 条件分支侧栏
                conditionData: {},
                tabIconState: '',
                approval: { // 节点审批
                    id: '',
                    dialogShow: false,
                    pending: false,
                    is_passed: true, // 是否通过
                    message: '', // 备注信息
                    rules: {
                        message: [{
                            validator (val) {
                                console.log($this.approval.is_passed, val)
                                return $this.approval.is_passed || val !== ''
                            },
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }]
                    }
                },
                nodePipelineData: {},
                isFailedSubproceeNodeInfo: null,
                nodeInfo: {},
                nodeInputs: {},
                isExecRecordOpen: false,
                nodeExecRecordInfo: {},
                isInjectVarDialogShow: false
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                hasAdminPerm: state => state.hasAdminPerm,
                infoBasicConfig: state => state.infoBasicConfig
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
                    if (item.default_condition) {
                        const nodeId = item.default_condition.flow_id
                        branchConditions[item.id][nodeId] = item.default_condition
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
                const data = this.getOrderedTree(this.completePipelineData)
                return [{
                    id: this.instance_id,
                    name: this.instanceName,
                    title: this.instanceName,
                    expanded: true,
                    children: data
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
                return this.isTopTask && !['FINISHED', 'REVOKED'].includes(this.state)
            },
            // 审计中心/轻应用时,隐藏[查看流程]按钮
            isShowViewProcess () {
                return this.routerType !== 'audit' && this.view_mode !== 'appmaker'
            },
            adminView () {
                return this.hasAdminPerm && this.$route.query.is_admin === 'true'
            }
        },
        mounted () {
            this.loadTaskStatus()
            this.getSingleAtomList()
            const { is_now } = this.$route.params
            if (is_now) {
                this.$nextTick(() => {
                    this.onOperationClick('execute')
                })
            }
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
                'skipCondParallelGateWay',
                'pauseNodeResume',
                'getNodeActInfo',
                'forceFail',
                'itsmTransition',
                'getInstanceRetryParams',
                'getNodeExecutionRecord',
                'getNodeActInfo',
                'instanceRetry',
                'subflowNodeRetry'
            ]),
            ...mapActions('atomForm/', [
                'loadSingleAtomList'
            ]),
            ...mapActions('admin/', [
                'taskFlowUpdateContext'
            ]),
            async loadTaskStatus () {
                try {
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
                        if (!this.isTopTask) {
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
                        if (this.isTopTask) {
                            this.rootState = this.state
                        }
                        if (
                            !this.cacheStatus
                            && ['FINISHED', 'REVOKED'].includes(this.state)
                            && this.taskId === this.instance_id
                        ) { // save cacheStatus
                            this.cacheStatus = instanceStatus.data
                        }
                        if (this.state === 'RUNNING' || (!this.isTopTask && this.state === 'FINISHED' && !['FINISHED', 'REVOKED', 'FAILED'].includes(this.rootState))) {
                            if (this.isExecRecordOpen) {
                                this.nodeExecRecordInfo.curTime = this.formatDuring(this.instanceStatus.elapsed_time)
                                this.setTaskStatusTimer(1000)
                            } else {
                                this.setTaskStatusTimer()
                            }
                            this.setRunningNode(instanceStatus.data.children)
                        }
                        this.updateNodeInfo()
                        this.isFailedSubproceeNodeInfo = this.canvasData.locations.find(item => {
                            return item.code === 'subprocess_plugin' && item.status === 'FAILED'
                        })
                    } else {
                        // 查询流程状态接口返回失败后再请求一次
                        this.pollErrorTimes += 1
                        if (this.pollErrorTimes > 2) {
                            this.cancelTaskStatusTimer()
                        } else {
                            this.setTaskStatusTimer()
                        }
                    }
                    this.modifyPageIcon()
                } catch (e) {
                    this.cancelTaskStatusTimer()
                    if (e.message !== 'cancelled') {
                        console.log(e)
                    }
                } finally {
                    source = null
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
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.task = false
                }
            },
            async nodeTaskSkip (id) {
                if (this.pending.skip) {
                    return
                }

                this.pending.skip = true
                this.isFailedSubproceeNodeInfo = null
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
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.forceFail = false
                }
            },
            async selectGatewayBranch (data) {
                this.pending.selectGateway = true
                try {
                    let res
                    if (this.isCondParallelGw) {
                        res = await this.skipCondParallelGateWay(data)
                    } else {
                        res = await this.skipExclusiveGateway(data)
                    }
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('跳过成功'),
                            theme: 'success'
                        })
                        setTimeout(() => {
                            this.setTaskStatusTimer()
                        }, 1000)
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.parseNodeResume = false
                }
            },
            setTaskStatusTimer (time = 2000) {
                this.cancelTaskStatusTimer()
                this.timer = setTimeout(() => {
                    this.loadTaskStatus()
                }, time)
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
                    let code, skippable, retryable, errorIgnorable, autoRetry
                    const currentNode = nodes[id]
                    const nodeActivities = this.pipelineData.activities[id]

                    if (nodeActivities) {
                        code = nodeActivities.component ? nodeActivities.component.code : ''
                        skippable = nodeActivities.isSkipped || nodeActivities.skippable
                        retryable = nodeActivities.can_retry || nodeActivities.retryable
                        errorIgnorable = nodeActivities.error_ignorable
                        autoRetry = nodeActivities.auto_retry
                    }

                    const data = {
                        code,
                        skippable,
                        retryable,
                        loop: currentNode.loop,
                        status: currentNode.state,
                        skip: currentNode.skip,
                        retry: currentNode.retry,
                        error_ignored: currentNode.error_ignored,
                        error_ignorable: errorIgnorable,
                        auto_retry: autoRetry
                    }

                    this.setTaskNodeStatus(id, data)
                }
            },
            setTaskNodeStatus (id, data) {
                this.$refs.templateCanvas && this.$refs.templateCanvas.onUpdateNodeInfo(id, data)
            },
            async setNodeDetailConfig (id, rootNode) {
                let code, version, componentData
                const node = this.pipelineData.activities[id]
                if (node) {
                    componentData = node.type === 'ServiceActivity' ? node.component.data : {}
                    code = node.type === 'ServiceActivity' ? node.component.code : ''
                    version = (node.type === 'ServiceActivity' ? node.component.version : node.version) || 'legacy'
                }
                let subprocessStack = []
                if (this.selectedFlowPath.length > 1) {
                    subprocessStack = this.selectedFlowPath.map(item => item.nodeId).slice(1)
                }
                this.nodeDetailConfig = {
                    component_code: code,
                    version: version,
                    node_id: id,
                    instance_id: this.instance_id,
                    root_node: rootNode,
                    subprocess_stack: JSON.stringify(subprocessStack),
                    componentData
                }
            },
            async onRetryClick (id) {
                try {
                    const resp = await this.getInstanceRetryParams({ id: this.instance_id })
                    if (resp.data.enable) {
                        this.openNodeInfoPanel('retryNode', i18n.t('重试'))
                        this.setNodeDetailConfig(id)
                        if (this.nodeDetailConfig.component_code) {
                            await this.loadNodeInfo()
                        }
                    } else {
                        this.openNodeInfoPanel('modifyParams', i18n.t('重试任务'))
                        this.retryNodeId = id
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            async loadNodeInfo () {
                try {
                    const nodeInputs = {}
                    const { componentData } = this.nodeDetailConfig
                    const nodeInfo = await this.getNodeActInfo(this.nodeDetailConfig)
                    if (nodeInfo.result) {
                        for (const key in nodeInfo.data.inputs) {
                            if (this.engineVer === 1) {
                                nodeInputs[key] = nodeInfo.data.inputs[key]
                            } else if (this.nodeDetailConfig.component_code === 'subprocess_plugin') { // 新版子流程任务节点输入参数处理
                                const value = nodeInfo.data.inputs[key]
                                if (key === 'subprocess') {
                                    Object.keys(value.pipeline.constants).forEach(key => {
                                        const data = value.pipeline.constants[key]
                                        nodeInputs[key] = data.value
                                    })
                                } else {
                                    nodeInputs[key] = value
                                }
                            } else if (componentData[key]) {
                                const { hook, value } = componentData[key]
                                if (hook) {
                                    nodeInputs[key] = nodeInfo.data.inputs[key]
                                } else {
                                    nodeInputs[key] = value
                                }
                            }
                        }
                        this.nodeInputs = nodeInputs
                    }
                    this.nodeInfo = nodeInfo
                } catch (e) {
                    console.warn(e)
                }
            },
            async onRetryTask (renderData = this.nodeInputs) {
                const { instance_id, component_code, node_id } = this.nodeDetailConfig
                try {
                    let res
                    if (component_code) {
                        const data = {
                            instance_id,
                            node_id,
                            component_code,
                            inputs: renderData
                        }
                        if (component_code === 'subprocess_plugin') {
                            const { inputs } = this.nodeInfo.data
                            const constants = inputs.subprocess ? inputs.subprocess.pipeline.constants : {}
                            Object.keys(constants).forEach(key => {
                                constants[key].value = renderData[key]
                            })
                            data.inputs = inputs
                        }
                        res = await this.instanceRetry(data)
                    } else {
                        res = await this.subflowNodeRetry({ instance_id, node_id })
                    }
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('重试成功'),
                            theme: 'success'
                        })
                        this.nodeInfo = {}
                        this.nodeInputs = {}
                        return true
                    }
                } catch (e) {
                    console.warn(e)
                }
            },
            onSkipClick (id) {
                this.isSkipDialogShow = true
                this.skipNodeId = id
            },
            onSkipCancel () {
                this.isSkipDialogShow = false
                this.skipNodeId = undefined
            },
            async nodeTaskRetry () {
                try {
                    this.pending.retry = true
                    this.setNodeDetailConfig(this.retryNodeId)
                    await this.loadNodeInfo()
                    await this.onRetryTask()
                    this.isNodeInfoPanelShow = false
                    this.retryNodeId = undefined
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.pending.retry = false
                }
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
                this.openNodeInfoPanel('modifyTime', i18n.t('修改时间'))
                this.setNodeDetailConfig(id)
            },
            onGatewaySelectionClick (id) {
                const nodeGateway = this.pipelineData.gateways[id]
                const branches = []
                for (const item in nodeGateway.conditions) {
                    branches.push({
                        id: item,
                        node_id: id,
                        name: nodeGateway.conditions[item].name || nodeGateway.conditions[item].evaluate,
                        converge_gateway_id: nodeGateway.converge_gateway_id || undefined
                    })
                }
                this.isCondParallelGw = nodeGateway.type === 'ConditionalParallelGateway'
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
            onApprovalClick (id) {
                this.approval.id = id
                this.approval.dialogShow = true
            },
            onApprovalConfirm () {
                if (this.approval.pending) {
                    return
                }

                this.$refs.approvalForm.validate().then(async () => {
                    try {
                        this.approval.pending = true
                        const { id, is_passed, message } = this.approval
                        const params = {
                            is_passed,
                            message,
                            project_id: this.project_id,
                            task_id: this.instance_id,
                            node_id: id
                        }
                        if (!this.isTopTask) {
                            const selectedFlowIds = this.selectedFlowPath.reduce((acc, cur) => {
                                if (cur.type !== 'root') {
                                    acc = acc ? acc + ',' + cur.id : cur.id
                                }
                                return acc
                            }, '')
                            params.subprocess_id = selectedFlowIds
                        }
                        await this.itsmTransition(params)
                        this.approval.id = ''
                        this.approval.is_passed = true
                        this.approval.message = ''
                        this.approval.dialogShow = false
                    } catch (e) {
                        console.error(e)
                    } finally {
                        this.approval.pending = false
                    }
                })
            },
            onApprovalCancel () {
                this.approval.id = ''
                this.approval.is_passed = true
                this.approval.message = ''
                this.approval.dialogShow = false
            },
            onCloseConfigPanel () {
                this.isShowConditionEdit = false
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
                        return this.isTopTask && ['RUNNING', 'SUSPENDED', 'NODE_SUSPENDED', 'FAILED'].includes(this.state)
                    default:
                        break
                }
            },
            getOrderedTree (data, level = 0) {
                const startNode = tools.deepClone(data.start_event)
                const fstLine = startNode.outgoing
                const orderedData = [Object.assign({}, startNode, {
                    level,
                    title: this.$t('开始节点'),
                    name: this.$t('开始节点'),
                    expanded: false
                })]
                this.retrieveLines(data, fstLine, orderedData, level)
                orderedData.sort((a, b) => a.level - b.level)
                const endEventIndex = orderedData.findIndex(item => item.type === 'EmptyEndEvent')
                const endEvent = orderedData.splice(endEventIndex, 1)
                orderedData.push(endEvent[0])
                return orderedData
            },
            /**
             * 根据节点连线遍历任务节点，返回按广度优先排序的节点数据
             * @param {Object} data 画布数据
             * @param {Array} lineId 连线ID
             * @param {Array} ordered 排序后的节点数据
             * @param {Number} level 任务节点与开始节点的距离
             *
             */
            retrieveLines (data, lineId, ordered, level = 0) {
                const { end_event, activities, gateways, flows } = data
                const currentNode = flows[lineId].target
                const endEvent = end_event.id === currentNode ? tools.deepClone(end_event) : undefined
                const activity = tools.deepClone(activities[currentNode])
                const gateway = tools.deepClone(gateways[currentNode])
                const node = endEvent || activity || gateway

                if (node && ordered.findIndex(item => item.id === node.id) === -1) {
                    if (endEvent) {
                        const name = this.$t('结束节点')
                        endEvent.title = name
                        endEvent.name = name
                        endEvent.expanded = false
                        ordered.push(endEvent)
                    } else if (gateway) { // 网关节点
                        const name = NODE_DICT[gateway.type.toLowerCase()]
                        level += 1
                        gateway.level = level
                        gateway.title = name
                        gateway.name = name
                        gateway.expanded = false
                        ordered.push(gateway)
                    } else if (activity) { // 任务节点
                        if (activity.pipeline) {
                            activity.children = this.getOrderedTree(activity.pipeline, level)
                        }
                        activity.level = level
                        activity.title = activity.name
                        activity.expanded = activity.pipeline
                        ordered.push(activity)
                    }

                    let outgoing
                    if (Array.isArray(node.outgoing)) {
                        outgoing = node.outgoing
                    } else {
                        outgoing = node.outgoing ? [node.outgoing] : []
                    }
                    outgoing.forEach(line => {
                        this.retrieveLines(data, line, ordered, level)
                    })
                }
            },
            updateNodeActived (id, isActived) {
                this.$refs.templateCanvas.onUpdateNodeInfo(id, { isActived })
            },
            // 查看参数、修改参数 （侧滑面板 标题 点击遮罩关闭）
            onTaskParamsClick (type, name) {
                if (type === 'viewNodeDetails') {
                    let nodeData = tools.deepClone(this.nodeData[0].children)
                    let firstTaskNode = null
                    const subprocessStack = []
                    while (nodeData) {
                        const activityNode = nodeData.find(item => item.type === 'ServiceActivity' || item.type === 'SubProcess')
                        if (activityNode.type === 'ServiceActivity') {
                            firstTaskNode = activityNode
                            nodeData = null
                        } else {
                            subprocessStack.push(activityNode.id)
                            nodeData = null
                        }
                    }
                    this.defaultActiveId = firstTaskNode.id
                    this.nodeDetailConfig = {
                        component_code: firstTaskNode.component.code,
                        version: firstTaskNode.component.version || 'legacy',
                        node_id: firstTaskNode.id,
                        instance_id: this.instance_id,
                        subprocess_stack: JSON.stringify(subprocessStack)
                    }
                    this.nodePipelineData = { ...this.pipelineData }
                }
                if (type === 'templateData') {
                    this.templateData = JSON.stringify(this.pipelineData, null, 4)
                }
                this.openNodeInfoPanel(type, name)
            },
            // 打开节点参数信息面板
            openNodeInfoPanel (type, name) {
                this.sideSliderTitle = name
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = type
            },
            // 注入全局变量
            onInjectGlobalVariable () {
                this.isInjectVarDialogShow = true
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
                if (type === 'subflow') {
                    this.handleSubflowCanvasChange(id)
                    return
                }
                this.setNodeDetailConfig(id)
                if (this.nodeDetailConfig.node_id) {
                    this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                }
                this.updateNodeActived(id, true)
                // 如果为子流程节点则需要重置pipelineData的constants
                this.nodePipelineData = { ...this.pipelineData }
                // 兼容旧版本子流程节点输出数据
                const selectLocation = this.canvasData.locations.find(item => item.id === id)
                if (selectLocation.type === 'subflow') {
                    const { constants } = this.pipelineData.activities[id].pipeline
                    this.nodePipelineData['constants'] = constants
                }
                this.openNodeInfoPanel('executeInfo', i18n.t('节点参数'))
            },
            onOpenConditionEdit (data) {
                this.isShowConditionEdit = true
                this.conditionData = { ...data }
            },
            /**
             * 切换为子流程画布
             */
            handleSubflowCanvasChange (id) {
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
            // 获取节点执行记录
            async onNodeExecRecord (nodeId) {
                try {
                    this.isExecRecordOpen = true
                    const tempNodeId = this.pipelineData.activities[nodeId]?.template_node_id
                    if (tempNodeId) {
                        const resp = await this.getNodeExecutionRecord({ tempNodeId })
                        const { execution_time = [] } = resp.data
                        this.nodeExecRecordInfo = {}
                        let latestTime, meanTime, deadline
                        execution_time.forEach((item, index) => {
                            if (index === 0) {
                                latestTime = item.elapsed_time
                                deadline = item.archived_time
                            }
                            meanTime = (meanTime || 0) + item.elapsed_time
                        })
                        this.nodeExecRecordInfo = {
                            latestTime: this.formatDuring(latestTime),
                            meanTime: this.formatDuring(meanTime / execution_time.length),
                            deadline: deadline ? deadline.replace('T', ' ').split('+')[0] : '--',
                            curTime: this.formatDuring(this.instanceStatus.elapsed_time),
                            count: execution_time.length
                        }
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            formatDuring (time) {
                if (!time) return '--'
                const days = parseInt(time / (60 * 60 * 24))
                const hours = parseInt((time % (60 * 60 * 24)) / (60 * 60))
                const minutes = parseInt((time % (60 * 60)) / (60))
                const seconds = (time % (60)).toFixed(0)
                let str = ''
                if (days) {
                    str = i18n.tc('天', days) + ' '
                }
                if (hours) {
                    str = str + hours + ' ' + i18n.t('时') + ' '
                }
                if (minutes) {
                    str = str + minutes + ' ' + i18n.t('分') + ' '
                }
                if (seconds) {
                    str = str + seconds + ' ' + i18n.tc('秒', 0)
                }
                return str
            },
            onCloseNodeExecRecord () {
                this.isExecRecordOpen = false
                this.nodeExecRecordInfo = {}
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

                this.setNodeDetailConfig(selectNodeId, !nodeHeirarchy)
                // 节点树切换时，如果为子流程节点则需要重置pipelineData的constants
                this.nodePipelineData = { ...this.pipelineData }
                // 兼容旧版本子流程节点输出数据
                const selectLocation = this.canvasData.locations.find(item => item.id === selectNodeId)
                if (selectLocation.type === 'subflow') {
                    const { constants } = this.pipelineData.activities[selectNodeId].pipeline
                    this.nodePipelineData['constants'] = constants
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
            // 根据当前任务的状态修改页面对应浏览器tab的icon
            modifyPageIcon () {
                let nameSuffix = ''
                switch (this.state) {
                    case 'CREATED':
                        nameSuffix = 'created'
                        break
                    case 'FINISHED':
                        nameSuffix = 'finished'
                        break
                    case 'FAILED':
                    case 'REVOKED':
                        nameSuffix = 'failed'
                        break
                    case 'RUNNING':
                    case 'READY':
                        nameSuffix = 'running'
                        if (this.tabIconState === 'SUSPENDED') {
                            nameSuffix = 'suspended'
                        }
                        break
                    case 'SUSPENDED':
                    case 'NODE_SUSPENDED':
                        nameSuffix = 'suspended'
                }
                const picName = nameSuffix ? `bk_sops_${nameSuffix}` : 'bk_sops'
                const path = `${window.SITE_URL}static/core/images/${picName}.png`
                dom.setPageTabIcon(path)
            },
            // 下次画布组件更新后执行队列
            onTemplateCanvasMounted () {
                this.canvasMountedQueues.forEach(action => {
                    action.func.apply(this, action.params)
                })
                this.canvasMountedQueues = []
            },
            async onRetrySuccess (data) {
                try {
                    this.pending.retry = true
                    await this.onRetryTask(data)
                    this.isNodeInfoPanelShow = false
                    this.isFailedSubproceeNodeInfo = null
                    this.setTaskStatusTimer()
                    this.updateNodeActived(this.nodeDetailConfig.id, false)
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.pending.retry = false
                }
            },
            onRetryCancel (id) {
                this.isNodeInfoPanelShow = false
                this.retryNodeId = undefined
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
                    node_id: selected[0].node_id,
                    instance_id: this.instance_id,
                    converge_gateway_id: this.isCondParallelGw ? selected[0].converge_gateway_id : undefined
                }
                if (this.isCondParallelGw) {
                    data.flow_ids = selected.reduce((arr, cur) => {
                        arr.push(cur.id)
                        return arr
                    }, [])
                } else {
                    data.flow_id = selected[0].id
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
            async onConfirmInjectVar (context) {
                try {
                    const params = {
                        task_id: this.taskId,
                        context
                    }
                    const resp = await this.taskFlowUpdateContext(params)
                    if (resp.result) {
                        this.isInjectVarDialogShow = false
                        this.$bkMessage({
                            message: i18n.t('注入全局变量成功'),
                            theme: 'success'
                        })
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            onCancelInjectVar () {
                this.isInjectVarDialogShow = false
            },
            unclickableOperation (type) {
                // 失败时不允许点击暂停按钮，创建是不允许点击撤销按钮，操作执行过程不允许点击
                return (this.state === 'FAILED' && type !== 'revoke') || (this.state === 'CREATED' && type === 'revoke') || this.operateLoading || !this.isTopTask
            },
            packUp () {
                this.isNodeInfoPanelShow = false
                this.retryNodeId = undefined
            },
            onshutDown () {
                this.isNodeInfoPanelShow = false
                this.templateData = ''
            },
            onBeforeClose () {
                // 除修改参数/修改时间/重试外  其余侧滑没有操作修改功能，支持自动关闭
                if (!['modifyParams', 'modifyTime', 'retryNode'].includes(this.nodeInfoType)) {
                    this.isNodeInfoPanelShow = false
                } else {
                    const isEqual = this.$refs[this.nodeInfoType].judgeDataEqual()
                    if (isEqual === true) {
                        this.isNodeInfoPanelShow = false
                        this.retryNodeId = undefined
                    } else if (isEqual === false) {
                        this.$bkInfo({
                            ...this.infoBasicConfig,
                            cancelFn: () => {
                                this.isNodeInfoPanelShow = false
                                this.retryNodeId = undefined
                            }
                        })
                    }
                }
            },
            onHiddenSideslider () {
                this.nodeInfoType = ''
                this.updateNodeActived(this.nodeDetailConfig.node_id, false)
            },
            // 判断RUNNING的节点是否有暂停节点，若有，则将当前任务状态标记为暂停状态
            setRunningNode (node = {}) {
                this.tabIconState
                    = Object.keys(node).some(key => (node[key].state === 'RUNNING'
                        && this.pipelineData.activities[key]
                        && this.pipelineData.activities[key].type === 'ServiceActivity'
                        && this.pipelineData.activities[key].component.code === 'pause_node'))
                        ? 'SUSPENDED'
                        : ''
            },
            // 刷新任务状态
            handleRefreshTaskStatus () {
                const nodeId = this.isFailedSubproceeNodeInfo.id
                this.isFailedSubproceeNodeInfo = null
                this.setTaskStatusTimer()
                this.updateNodeActived(nodeId, false)
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
}

/deep/ .atom-failed {
    font-size: 12px;
}

.subprocess-failed-tips {
    margin-top: -1px;
    color: #63656e;
    /deep/.bk-alert-title {
        display: flex;
    }
    /deep/.bk-link {
        vertical-align: initial;
        line-height: 16px;
        .bk-link-text {
            font-size: 12px;
        }
    }
}
.task-container {
    position: relative;
    width: 100%;
    height: calc(100vh - 100px);
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
.approval-dialog-content {
    /deep/ .bk-form-radio {
        margin-right: 10px;
    }
}
</style>
<style lang="scss">
@import '@/scss/config.scss';
.task-operation {
    .operation-table {
        width: 100%;
        font-size: 12px;
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
