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
            :primitive-tpl-id="primitiveTplId"
            :primitive-tpl-source="primitiveTplSource"
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
            :params-can-be-modify="paramsCanBeModify"
            :pending-nodes="pendingNodes"
            @moveNodeToView="moveNodeToView"
            @onSelectSubflow="onSelectSubflow"
            @onOperationClick="onOperationClick"
            @onTaskParamsClick="onTaskParamsClick"
            @onInjectGlobalVariable="onInjectGlobalVariable">
        </task-operation-header>
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
                    :node-variable-info="nodeVariableInfo"
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
                    @onTogglePerspective="onTogglePerspective"
                    @onSubflowPauseResumeClick="onSubflowPauseResumeClick">
                </TemplateCanvas>
            </div>
        </div>
        <bk-sideslider
            :is-show.sync="isNodeInfoPanelShow"
            :width="['viewNodeDetails', 'executeInfo'].includes(nodeInfoType) ? 1300 : 960"
            :quick-close="true"
            :before-close="onBeforeClose"
            @hidden="onHiddenSideslider">
            <div slot="header">
                <div class="header">
                    <span>{{sideSliderTitle}}</span>
                    <div class="sub-title" v-if="nodeInfoType === 'modifyParams' && retryNodeId">
                        {{ retryNodeName }}
                    </div>
                </div>
            </div>
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
                    :is-sub-canvas="nodeNav.length > 1"
                    @nodeTaskRetry="nodeTaskRetry"
                    @packUp="packUp">
                </ModifyParams>
                <ExecuteInfo
                    v-if="nodeInfoType === 'executeInfo' || nodeInfoType === 'viewNodeDetails'"
                    :state="state"
                    :node-data="nodeData"
                    :engine-ver="engineVer"
                    :node-display-status="nodeDisplayStatus"
                    :admin-view="adminView"
                    :pipeline-data="nodePipelineData"
                    :default-active-id="defaultActiveId"
                    :is-condition="isCondition"
                    :node-detail-config="nodeDetailConfig"
                    :is-readonly="true"
                    :is-show.sync="isShowConditionEdit"
                    :constants="pipelineData.constants"
                    :gateways="pipelineData.gateways"
                    :condition-data="conditionData"
                    @close="onCloseConfigPanel"
                    @onRetryClick="onRetryClick"
                    @onSkipClick="onSkipClick"
                    @onTaskNodeResumeClick="onTaskNodeResumeClick"
                    @onPauseClick="onPauseClick"
                    @onContinueClick="onContinueClick"
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
        <injectVariableDialog
            :is-inject-var-dialog-show="isInjectVarDialogShow"
            @onConfirmInjectVar="onConfirmInjectVar"
            @onCancelInjectVar="onCancelInjectVar">
        </injectVariableDialog>
        <!-- <condition-edit
            v-if="isShowConditionEdit"
            ref="conditionEdit"
            :is-readonly="true"
            :is-show.sync="isShowConditionEdit"
            :gateways="pipelineData.gateways"
            :condition-data="conditionData"
            @close="onCloseConfigPanel">
        </condition-edit> -->
        <bk-dialog
            width="600"
            :theme="'primary'"
            :mask-close="false"
            :auto-close="false"
            header-position="left"
            :title="$t('审批')"
            :loading="approval.pending"
            :value="approval.dialogShow"
            :cancel-text="$t('取消')"
            @confirm="onApprovalConfirm"
            @cancel="onApprovalCancel">
            <bk-form
                ref="approvalForm"
                class="approval-dialog-content"
                form-type="vertical"
                :model="approval"
                :rules="approval.rules">
                <bk-form-item :label="$t('审批意见')" :required="true">
                    <bk-radio-group v-model="approval.is_passed" @change="$refs.approvalForm.clearError()">
                        <bk-radio :value="true">{{ $t('通过') }}</bk-radio>
                        <bk-radio :value="false">{{ $t('拒绝') }}</bk-radio>
                    </bk-radio-group>
                </bk-form-item>
                <bk-form-item :label="$t('备注')" property="message" :required="!approval.is_passed">
                    <bk-input v-model="approval.message" type="textarea" :row="4"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapMutations, mapState } from 'vuex'
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
    import permission from '@/mixins/permission.js'
    import TaskOperationHeader from './TaskOperationHeader'
    import TemplateData from './TemplateData'
    import injectVariableDialog from './InjectVariableDialog.vue'
    import tplPerspective from '@/mixins/tplPerspective.js'

    const CancelToken = axios.CancelToken
    let source = CancelToken.source()

    const TASK_OPERATIONS = {
        reExecute: {
            action: 'reExecute',
            icon: 'bk-icon icon-refresh-line',
            text: i18n.t('再次执行'),
            disabled: false
        },
        execute: {
            action: 'execute',
            icon: 'bk-icon icon-play-shape',
            text: i18n.t('执行')
        },
        pause: {
            action: 'pause',
            icon: 'common-icon-pause',
            text: i18n.t('暂停执行')
        },
        resume: {
            action: 'resume',
            icon: 'bk-icon icon-play-shape',
            text: i18n.t('继续执行')
        },
        revoke: {
            action: 'revoke',
            icon: 'common-icon-terminate',
            text: i18n.t('终止执行'),
            disabled: false
        }
    }
    // 执行按钮的变更
    const STATE_OPERATIONS = {
        'RUNNING': 'pause',
        'NODE_SUSPENDED': 'pause',
        'PENDING_PROCESSING': 'pause',
        'SUSPENDED': 'resume',
        'CREATED': 'execute',
        'FAILED': 'reExecute'
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
            TaskOperationHeader,
            TemplateData,
            injectVariableDialog
        },
        mixins: [permission, tplPerspective],
        props: {
            project_id: [Number, String],
            instance_id: [Number, String],
            engineVer: Number,
            instanceFlow: String,
            instanceName: String,
            template_id: [Number, String],
            primitiveTplId: [Number, String],
            primitiveTplSource: String,
            templateSource: String,
            isChildTaskFlow: Boolean,
            instanceActions: Array,
            routerType: String,
            creatorName: String,
            unclaimFuncTask: Boolean
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
                cacheStatus: undefined, // 总任务缓存状态信息；只有总任务完成、终止时才存在
                instanceStatus: {},
                taskParamsType: '',
                timer: null,
                pipelineData: pipelineData,
                nodeTreePipelineData: tools.deepClone(pipelineData),
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
                retryNodeId: undefined,
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
                nodeInfo: {},
                nodeInputs: {},
                isExecRecordOpen: false,
                nodeExecRecordInfo: {},
                isInjectVarDialogShow: false,
                nodeIds: {},
                nodeDisplayStatus: {},
                showNodeList: [0, 1, 2],
                converNodeList: [],
                isCondition: false,
                conditionOutgoing: [],
                unrenderedCoverNode: [],
                subProcessTaskId: null,
                nodeData: [],
                convergeInfo: {},
                nodeSourceMaps: {},
                nodeTargetMaps: {},
                retryNodeName: ''
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                hasAdminPerm: state => state.hasAdminPerm,
                infoBasicConfig: state => state.infoBasicConfig,
                username: state => state.username
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
                        return { ...item, mode: 'execute', checked: true, code, ready: true }
                    }),
                    branchConditions
                }
            },
            previewData () {
                return tools.deepClone(this.pipelineData)
            },
            common () {
                return this.templateSource !== 'project'
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

                    if (
                        this.state === 'CREATED'
                        && this.unclaimFuncTask
                        && this.isTopTask
                        && this.creatorName !== this.username
                    ) {
                        executePauseBtn.disabled = true
                        executePauseBtn.text = this.$t('未认领的职能化任务不允许执行')
                    }

                    operationBtns.push(executePauseBtn, revokeBtn)
                } else if (this.state) {
                    operationBtns.push(TASK_OPERATIONS['reExecute'])
                }
                return operationBtns
            },
            paramsCanBeModify () {
                return !['FINISHED', 'REVOKED'].includes(this.state)
            },
            // 审计中心/轻应用时,隐藏[查看流程]按钮
            isShowViewProcess () {
                return this.routerType !== 'audit' && this.view_mode !== 'appmaker'
            },
            adminView () {
                return this.hasAdminPerm && this.$route.query.is_admin === 'true'
            },
            pendingNodes () {
                const { children = {} } = this.instanceStatus
                const pendingStatus = ['PENDING_APPROVAL', 'PENDING_CONFIRMATION', 'PENDING_PROCESSING']
                return Object.values(children).reduce((acc, cur) => {
                    if (pendingStatus.includes(cur.state)) {
                        acc.push({
                            id: cur.id,
                            name: this.activities[cur.id].name,
                            state: cur.state,
                            statusText: TASK_STATE_DICT[cur.state]
                        })
                    }
                    return acc
                }, [])
            }
        },
        watch: {
            instanceStatus: {
                handler (val) {
                    const { state, children = {} } = val
                    const pendingStatus = ['PENDING_APPROVAL', 'PENDING_CONFIRMATION', 'PENDING_PROCESSING', 'SUSPENDED']
                    const { activities, gateways, flows, start_event, end_event } = tools.deepClone(this.pipelineData)
                    if (pendingStatus.includes(state)) {
                        Object.values(children).forEach(node => {
                            // 非任务节点/网关节点
                            if ([start_event.id, end_event.id].includes(node.id)) return
                            // 查看输出节点状态
                            let { outgoing } = activities[node.id] || gateways[node.id] || {}
                            if (!Array.isArray(outgoing)) {
                                outgoing = [outgoing]
                            }
                            outgoing.forEach(outLine => {
                                const targetNode = flows[outLine].target
                                const isExecuted = targetNode in children
                                // 输出节点未被执行则表明任务暂停后该分支在当前节点停止往下继续执行
                                this.setLineSuspendState(node.id, outLine, isExecuted)
                            })
                        })
                    }
                },
                deep: true
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
            ...mapMutations('template/', [
                'setLine'
            ]),
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
                'subflowNodeRetry',
                'taskFlowConvertCommonTask'
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
                    if (['FINISHED', 'REVOKED'].includes(this.state) && this.cacheStatus && this.cacheStatus.children[this.taskId]) { // 总任务：完成/终止时,取实例缓存数据
                        instanceStatus = await this.getGlobalCacheStatus(this.taskId)
                    } else if (
                        this.instanceStatus.state
                        && this.instanceStatus.state === 'FINISHED' // 任务实例才会出现终止，子流程不存在
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
                        // 任务暂停时如果有节点正在执行，需轮询节点状态
                        let suspendedRunning = false
                        if (this.state === 'SUSPENDED') {
                            suspendedRunning = Object.values(instanceStatus.data.children).some(item => item.state === 'RUNNING')
                        }
                        // 节点执行记录显示时，重新计算当前执行时间/判断是否还在执行中
                        if (this.isExecRecordOpen) {
                            const execNodeConfig = this.instanceStatus.children[this.nodeExecRecordInfo.nodeId]
                            if (execNodeConfig) {
                                const elapsedTime = this.formatDuring(execNodeConfig.elapsed_time)
                                if (execNodeConfig.state === 'RUNNING') {
                                    this.nodeExecRecordInfo.curTime = elapsedTime
                                } else if (this.nodeExecRecordInfo.curTime) {
                                    // 如果节点执行完成，需要把当前执行的时间插入到执行历史里面，count + 1
                                    this.nodeExecRecordInfo.curTime = ''
                                    this.nodeExecRecordInfo.execTime.unshift(elapsedTime)
                                    this.nodeExecRecordInfo.count += 1
                                }
                                this.nodeExecRecordInfo.state = execNodeConfig.state
                            }
                        }
                        if (this.state === 'RUNNING' || (!this.isTopTask && this.state === 'FINISHED' && !['FINISHED', 'REVOKED', 'FAILED'].includes(this.rootState)) || suspendedRunning) {
                            if (this.isExecRecordOpen && this.nodeExecRecordInfo.state) { // 节点执行中一秒查一次
                                this.setTaskStatusTimer(1000)
                            } else {
                                this.setTaskStatusTimer()
                            }
                            this.setRunningNode(instanceStatus.data.children)
                        }
                        this.updateNodeInfo()
                    } else {
                        // 查询流程状态接口返回失败后再请求一次
                        this.pollErrorTimes += 1
                        if (this.pollErrorTimes > 2) {
                            this.cancelTaskStatusTimer()
                        } else {
                            this.setTaskStatusTimer()
                        }
                    }
                    this.nodeDisplayStatus = tools.deepClone(this.instanceStatus)
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
                    const params = { scope: 'task' }
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
            async taskPause (subflowPause, nodeId, taskId) {
                let res, state, message
                try {
                    if (!this.isTopTask || subflowPause) { // 子流程画布暂停或子流程节点暂停
                        const data = {
                            instance_id: taskId || this.instance_id,
                            node_id: nodeId || this.taskId
                        }
                        res = await this.subInstancePause(data)
                        state = 'NODE_SUSPENDED'
                        const { activities } = this.pipelineData
                        const { name } = activities[nodeId]
                        message = name + ' ' + i18n.t('节点已暂停执行')
                    } else {
                        res = await this.instancePause(this.instance_id)
                        state = 'SUSPENDED'
                        message = i18n.t('任务已暂停执行')
                    }
                    if (res.result) {
                        this.state = state
                        this.setTaskStatusTimer()
                        this.$bkMessage({
                            message,
                            theme: 'success'
                        })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.task = false
                }
            },
            async taskResume (subflowResume, nodeId, taskId) {
                let res, message
                try {
                    if (!this.isTopTask || subflowResume) {
                        const data = {
                            instance_id: taskId || this.instance_id,
                            node_id: nodeId || this.taskId
                        }
                        res = await this.subInstanceResume(data)
                        const { activities } = this.pipelineData
                        const { name } = activities[nodeId]
                        message = name + ' ' + i18n.t('节点已继续执行')
                    } else {
                        res = await this.instanceResume(this.instance_id)
                        message = i18n.t('任务已继续执行')
                    }
                    if (res.result) {
                        this.state = 'RUNNING'
                        this.setTaskStatusTimer()
                        this.$bkMessage({
                            message,
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
                    this.activeOperation = 'revoke'
                    const res = await this.instanceRevoke(this.instance_id)
                    if (res.result) {
                        this.state = 'REVOKED'
                        this.$bkMessage({
                            message: i18n.t('任务终止成功'),
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
            async nodeTaskSkip (id, taskId) {
                if (this.pending.skip) {
                    return
                }

                this.pending.skip = true
                try {
                    const data = {
                        instance_id: taskId || this.instance_id,
                        node_id: id
                    }
                    const res = await this.instanceNodeSkip(data)
                    if (res.result) {
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
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
            async nodeForceFail (id, taskId) {
                if (this.pending.forceFail) {
                    return
                }
                this.pending.forceFail = true
                try {
                    const params = {
                        node_id: id,
                        task_id: Number(taskId || this.instance_id)
                    }
                    const res = await this.forceFail(params)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('强制终止执行成功'),
                            theme: 'success'
                        })
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
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
            async nodeResume (id, taskId) {
                if (this.pending.parseNodeResume) {
                    return
                }
                this.pending.parseNodeResume = true
                try {
                    const data = {
                        instance_id: taskId || this.instance_id,
                        node_id: id,
                        data: { callback: 'resume' }
                    }
                    const res = await this.pauseNodeResume(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('继续成功'),
                            theme: 'success'
                        })
                        this.isNodeInfoPanelShow = false
                        this.nodeInfoType = ''
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
                        auto_retry: autoRetry,
                        ready: false,
                        task_state: this.state // 任务状态
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
            async onRetryClick (id, info) {
                try {
                    const { taskId } = info || {}
                    this.subProcessTaskId = taskId
                    // 独立子任务重试使用二次确认弹框
                    if (this.isChildTaskFlow || (info && info.isSubNode)) {
                        const nodeConfig = this.nodeTreePipelineData.activities[id]
                        const name = info ? info.name : nodeConfig.name
                        const title = info.isSubProcessNode
                            ? this.$t('确定重试子流程【n】 ？', { n: name })
                            : this.$t('确定重试节点【n】 ？', { n: name })
                        const h = this.$createElement
                        this.$bkInfo({
                            subHeader: h('div', { class: 'custom-header' }, [
                                h('div', {
                                    class: 'custom-header-title',
                                    directives: [{
                                        name: 'bk-overflow-tips'
                                    }]
                                }, [title]),
                                h('div', {
                                    class: 'custom-header-sub-title bk-dialog-header-inner',
                                    directives: [{
                                        name: 'bk-overflow-tips'
                                    }]
                                }, [this.$t('非根节点仅支持以原参数进行重试')])
                            ]),
                            width: 450,
                            extCls: 'dialog-custom-header-title',
                            maskClose: false,
                            confirmLoading: true,
                            cancelText: this.$t('取消'),
                            confirmFn: async () => {
                                this.retryNodeId = id
                                await this.nodeTaskRetry()
                            }
                        })
                        return
                    }
                    const resp = await this.getInstanceRetryParams({ id: taskId || this.instance_id })
                    if (resp.data.enable) {
                        this.openNodeInfoPanel('retryNode', i18n.t('重试节点'))
                        this.setNodeDetailConfig(id)
                        if (this.nodeDetailConfig.component_code) {
                            await this.loadNodeInfo(id)
                        }
                    } else {
                        this.setNodeDetailConfig(id)
                        const nodeConfig = this.nodeTreePipelineData.activities[id]
                        const isSubProcessNode = nodeConfig?.component.code === 'subprocess_plugin'
                        this.retryNodeName = nodeConfig.name
                        this.openNodeInfoPanel('modifyParams', isSubProcessNode ? i18n.t('重试子流程') : i18n.t('重试节点'))
                        this.retryNodeId = id
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            async loadNodeInfo (id = this.retryNodeId) {
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
                                    let pipelineData = this.nodeTreePipelineData
                                    if (this.nodeDetailConfig.root_node) {
                                        const parentIdList = this.nodeDetailConfig.root_node.split('-')
                                        parentIdList.forEach(item => {
                                            const nodeData = pipelineData.activities[item]
                                            if (nodeData.pipeline) {
                                                pipelineData = nodeData.pipeline
                                            }
                                        })
                                    }
                                    const nodeConfig = pipelineData.activities[id]
                                    const subprocess = nodeConfig.component.data.subprocess
                                    nodeInfo.data.inputs[key] = subprocess.value
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
            async onRetryTask (renderData) {
                const { component_code } = this.nodeDetailConfig
                try {
                    let res
                    if (component_code) {
                        res = await this.instanceRetry(renderData)
                    } else {
                        res = await this.subflowNodeRetry(renderData)
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
            onSkipClick (id, info) {
                const h = this.$createElement
                let name = ''
                let taskId = this.instance_id
                let title = ''
                let subTitle = ''
                let isSubProcessNode = false
                if (info) {
                    name = info.name
                    taskId = info.taskId
                    isSubProcessNode = info.isSubProcessNode
                } else {
                    const nodeConfig = this.nodeTreePipelineData.activities[id]
                    name = nodeConfig.name
                    isSubProcessNode = nodeConfig.component.code === 'subprocess_plugin'
                }
                if (isSubProcessNode) {
                    title = this.$t('确定跳过子流程【n】 ？', { n: name })
                    subTitle = this.$t('跳过子流程将忽略子流程中所有未完成节点')
                } else {
                    title = this.$t('确定跳过节点【n】 ？', { n: name })
                    subTitle = this.$t('跳过节点将忽略失败继续往后执行')
                }
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [title]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [subTitle])
                    ]),
                    width: 450,
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.nodeTaskSkip(id, taskId)
                    }
                })
            },
            async nodeTaskRetry () {
                try {
                    this.pending.retry = true
                    if (!this.nodeDetailConfig.component_code) {
                        this.setNodeDetailConfig(this.retryNodeId)
                    }
                    await this.loadNodeInfo()

                    const { component_code, node_id } = this.nodeDetailConfig
                    const data = {
                        instance_id: this.subProcessTaskId || this.instance_id,
                        component_code,
                        node_id
                    }
                    if (component_code) {
                        if (component_code === 'subprocess_plugin') {
                            const { inputs } = this.nodeInfo.data
                            data.inputs = inputs
                            data.inputs['_escape_render_keys'] = ['subprocess']
                        } else {
                            const inputs = tools.deepClone(this.nodeInputs)
                            // 当重试节点引用了变量时，对应的inputs值设置为变量
                            const { constants } = this.nodeTreePipelineData
                            for (const key in constants) {
                                const values = constants[key]
                                if (this.retryNodeId in values.source_info) {
                                    values.source_info[this.retryNodeId].forEach(code => {
                                        if (code in inputs) {
                                            inputs[code] = values.key
                                        }
                                    })
                                }
                            }
                            data.inputs = inputs
                        }
                        data.node_id = node_id
                    }
                    await this.onRetryTask(data)
                    this.isNodeInfoPanelShow = false
                    this.retryNodeId = undefined
                    // 重新轮询任务状态
                    this.setTaskStatusTimer()
                    this.updateNodeActived(this.nodeDetailConfig.id, false)
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.pending.retry = false
                }
            },
            onForceFailClick (id, taskId) {
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确定强制终止当前节点？')]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('强制终止将强行修改节点状态为失败，但不会中断已经发送到其它系统的请求')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.nodeForceFail(id, taskId)
                    }
                })
            },
            onModifyTimeClick (id, taskId) {
                this.subProcessTaskId = taskId
                this.openNodeInfoPanel('modifyTime', i18n.t('修改时间'))
                if (!taskId) {
                    this.setNodeDetailConfig(id)
                }
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
                if (nodeGateway.default_condition) {
                    branches.unshift({
                        id: nodeGateway.default_condition.flow_id,
                        node_id: id,
                        name: nodeGateway.default_condition.name,
                        converge_gateway_id: nodeGateway.converge_gateway_id || undefined
                    })
                }
                this.isCondParallelGw = nodeGateway.type === 'ConditionalParallelGateway'
                this.gatewayBranches = branches
                this.isGatewaySelectDialogShow = true
            },
            onTaskNodeResumeClick (id, taskId) {
                this.$bkInfo({
                    title: i18n.t('确定继续往后执行?'),
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.nodeResume(id, taskId)
                    }
                })
            },
            onApprovalClick (id, taskId) {
                this.approval.id = id
                this.subProcessTaskId = taskId
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
                            task_id: this.subProcessTaskId || this.instance_id,
                            node_id: id
                        }
                        // 如果存在子流程任务节点时则不需要传subprocess_id
                        if (!this.subProcessTaskId) {
                            let { subprocess_stack: stack } = this.nodeDetailConfig
                            if (stack) {
                                stack = JSON.parse(stack)
                                params.subprocess_id = stack.join(',')
                            }
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
            onPauseClick (id, taskId) {
                this.taskPause(true, id, taskId)
                this.isNodeInfoPanelShow = false
                this.nodeInfoType = ''
                setTimeout(() => {
                    this.setTaskStatusTimer()
                }, 1000)
            },
            onContinueClick (id, taskId) {
                this.taskResume(true, id, taskId)
                this.isNodeInfoPanelShow = false
                this.nodeInfoType = ''
                setTimeout(() => {
                    this.setTaskStatusTimer()
                }, 1000)
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
                    case 'reExecute':
                        return true
                    case 'execute':
                        return this.state === 'CREATED' && this.isTopTask
                    case 'pause':
                        return ['RUNNING', 'NODE_SUSPENDED'].includes(this.state)
                    case 'resume':
                        return this.state === 'SUSPENDED'
                    case 'revoke':
                        return this.isTopTask && ['RUNNING', 'SUSPENDED', 'PENDING_PROCESSING', 'FAILED'].includes(this.state)
                    default:
                        break
                }
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
                            this.getGatewayConvergeNodes(id, id, this.convergeInfo)
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
                                    children: []
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
                                    children: []
                                })
                            }
                        } else if (nodeConfig.type === 'ParallelGateway') {
                            treeItem.gatewayId = gatewayId || id
                            this.getGatewayConvergeNodes(id, id, this.convergeInfo)
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
                                    children: []
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
                                    lastId: item.id
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
            getGatewayConvergeNodes (id, parentId, convergeInfo = {}, index, isDeep) {
                if (!id) return
                if (!convergeInfo[parentId]) {
                    convergeInfo[parentId] = {
                        id: parentId,
                        checkedNodes: [],
                        convergeNode: '',
                        branchCount: 1
                    }
                }
                const targetNodes = this.nodeTargetMaps[id] || []
                if (targetNodes.length > 1) {
                    if (!isDeep) {
                        convergeInfo[parentId].branchCount += targetNodes.length - 1
                    }
                    targetNodes.forEach((targetId, branchIndex) => {
                        let newIndex = branchIndex
                        if (index !== 0) {
                            const branches = Object.keys(convergeInfo[parentId]).filter(item => /^branch[0-9]*$/.test(item))
                            newIndex = branches.length
                        }
                        newIndex = isDeep ? index : newIndex
                        this.getGatewayConvergeNodes(targetId, parentId, convergeInfo, newIndex, isDeep)
                    })
                } else {
                    const { checkedNodes, branchCount = 0 } = convergeInfo[parentId]
                    const countArr = [...Array(branchCount).keys()]
                    const { end_event } = this.pipelineData
                    if ([...checkedNodes, end_event.id].includes(id) || this.nodeSourceMaps[id].length > 1) {
                        const branchConvergeNode = convergeInfo[parentId][`branch${index}`]
                        if (!branchConvergeNode) {
                            convergeInfo[parentId][`branch${index}`] = [id]
                        } else if (!branchConvergeNode.includes(id)) {
                            branchConvergeNode.push(id)
                        }
                        if (!checkedNodes.includes(id)) {
                            checkedNodes.push(id)
                        }
                        const convergeNodes = countArr.map(item => {
                            const data = convergeInfo[parentId][`branch${item}`] || []
                            return [...new Set(data)]
                        }).flat()
                        if (this.findMost(convergeNodes) === branchCount) {
                            convergeInfo[parentId].convergeNode = id
                        } else if (index === branchCount - 1) {
                            countArr.forEach(item => {
                                if (!convergeInfo[parentId].convergeNode) {
                                    const data = convergeInfo[parentId][`branch${item}`] || []
                                    const [lastId] = data.slice(-1)
                                    const targetIds = this.nodeTargetMaps[lastId] || [lastId]
                                    targetIds.forEach(targetId => {
                                        this.getGatewayConvergeNodes(targetId, parentId, convergeInfo, item, true)
                                    })
                                }
                            })
                        }
                    } else {
                        checkedNodes.push(id)
                        const targetId = targetNodes[0]
                        this.getGatewayConvergeNodes(targetId, parentId, convergeInfo, index, isDeep)
                    }
                }
            },
            findMost (arr) {
                if (!arr.length) return
                if (arr.length === 1) return 1
                let maxNum = 0
                arr.reduce((acc, cur) => {
                    acc[cur] ? acc[cur] += 1 : acc[cur] = 1
                    if (acc[cur] > maxNum) {
                        maxNum = acc[cur]
                    }
                    return acc
                }, {})
                return maxNum
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
            updateNodeActived (id, isActived) {
                this.$refs.templateCanvas.onUpdateNodeInfo(id, { isActived })
            },
            // 查看参数、修改参数 （侧滑面板 标题 点击遮罩关闭）
            onTaskParamsClick (type, name) {
                if (type === 'viewNodeDetails') {
                    const { start_event, flows, location } = this.pipelineData
                    const nodeId = flows[start_event.outgoing].target
                    const locInfo = location.find(item => item.id === nodeId)
                    const type = locInfo.type === 'subflow' ? 'subflowDetail' : locInfo.type
                    this.onNodeClick(nodeId, type)
                    return
                }
                if (type === 'templateData') {
                    this.templateData = JSON.stringify(this.pipelineData, null, 4)
                }
                this.openNodeInfoPanel(type, name)
            },
            // 打开节点参数信息面板
            openNodeInfoPanel (type, name, isCondition = false) {
                this.sideSliderTitle = name
                this.isNodeInfoPanelShow = true
                this.nodeInfoType = type
                this.isCondition = isCondition
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

                const requestPerm = action !== 'reExecute' ? 'task_operate' : this.templateSource === 'project' ? 'flow_create_task' : 'common_flow_create_task'
                if (!this.hasPermission([requestPerm], this.instanceActions)) {
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
                    if (action === 'reExecute') {
                        const flowKey = this.templateSource === 'project' ? 'flow' : 'common_flow'
                        resourceData[flowKey] = [{
                            id: this.template_id,
                            name: this.templateName
                        }]
                    }
                    this.applyForPermission(['task_operate'], this.instanceActions, resourceData)
                    return
                }

                if (action === 'revoke') {
                    const h = this.$createElement
                    this.$bkInfo({
                        subHeader: h('div', { class: 'custom-header' }, [
                            h('div', {
                                class: 'custom-header-title',
                                directives: [{
                                    name: 'bk-overflow-tips'
                                }]
                            }, [i18n.t('确定终止当前任务?')]),
                            h('div', {
                                class: 'custom-header-sub-title bk-dialog-header-inner',
                                directives: [{
                                    name: 'bk-overflow-tips'
                                }]
                            }, [i18n.t('终止任务将停止执行任务，但执行中节点将运行完成')])
                        ]),
                        extCls: 'dialog-custom-header-title',
                        maskClose: false,
                        confirmLoading: true,
                        cancelText: this.$t('取消'),
                        confirmFn: async () => {
                            await this.taskRevoke()
                        }
                    })
                    return
                }
                // 职能化任务--【任务创建人】执行时弹出二次确认弹框
                if (
                    action === 'execute'
                    && this.unclaimFuncTask
                    && this.isTopTask
                    && this.creatorName === this.username
                ) {
                    const h = this.$createElement
                    this.$bkInfo({
                        title: this.$t('确定开始执行?'),
                        subHeader: h('div', {
                            style: {
                                'font-size': '14px',
                                'color': '#63656e',
                                'line-height': '1.5',
                                'text-align': 'center',
                                'word-break': 'break-all'
                            }
                        }, [
                            h('p', this.$t('任务还未认领，请通知职能化人员')),
                            h('p', this.$t('若坚持执行，职能化人员将无法操作该任务'))
                        ]),
                        width: 500,
                        maskClose: false,
                        confirmLoading: true,
                        cancelText: this.$t('取消'),
                        confirmFn: async () => {
                            this.pending.task = true
                            const resp = await this.taskFlowConvertCommonTask({ taskId: this.instance_id })
                            if (resp.result) {
                                this.$parent.unclaimFuncTask = false
                                this.activeOperation = action
                                const actionType = 'task' + action.charAt(0).toUpperCase() + action.slice(1)
                                this[actionType]()
                            } else {
                                this.pending.task = false
                            }
                        }
                    })
                    return
                }
                this.pending.task = true
                this.activeOperation = action
                const actionType = 'task' + action.charAt(0).toUpperCase() + action.slice(1)
                this[actionType]()
            },
            onNodeClick (id, type) {
                this.defaultActiveId = id
                this.setNodeDetailConfig(id)
                if (this.nodeDetailConfig.node_id) {
                    this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                }
                this.updateNodeActived(id, true)
                // 如果为子流程节点则需要重置pipelineData的constants
                this.nodePipelineData = { ...this.nodeTreePipelineData }
                this.convergeInfo = {}
                this.nodeIds = {}
                this.nodeData = this.getOrderedTree(this.completePipelineData)
                this.openNodeInfoPanel('executeInfo', i18n.t('节点详情'))
            },
            onOpenConditionEdit (data, isCondition = true) {
                if (isCondition && data) {
                    this.onNodeClick(data.nodeId)
                    // 生成网关添加id 网关id + 分支条件outgoning + 特殊标识
                    this.defaultActiveId = data.nodeId + '-' + data.id + '-condition'
                    this.isCondition = true
                    this.isShowConditionEdit = true
                    this.conditionData = { ...data }
                }
                this.isCondition = isCondition
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
                        const resp = await this.getNodeExecutionRecord({ tempNodeId, taskId: this.instance_id })
                        const { execution_time = [], total = 0 } = resp.data
                        this.nodeExecRecordInfo = {}
                        const execTime = execution_time.map(item => {
                            return this.formatDuring(item.elapsed_time)
                        })
                        const execNodeConfig = this.instanceStatus.children[nodeId]
                        let curTime = this.formatDuring(execNodeConfig.elapsed_time)
                        let count = total
                        // 如果节点执行完成，任务未之前完成，需要把当前执行的时间插入到执行历史里面，count + 1
                        if (execNodeConfig.state === 'FINISHED') {
                            if (this.state !== 'FINISHED') {
                                execTime.unshift(curTime)
                                count += 1
                            }
                            curTime = ''
                        }
                        this.nodeExecRecordInfo = {
                            nodeId,
                            curTime: curTime,
                            execTime,
                            state: execNodeConfig.state,
                            count
                        }
                    } else {
                        this.$refs.templateCanvas.closeNodeExecRecord()
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            formatDuring (time) {
                if (!time && time !== 0) return '--'
                if (time === 0) {
                    return `${i18n.tc('小于')} ${i18n.tc('秒', 1)}`
                }
                const days = parseInt(time / (60 * 60 * 24))
                const hours = parseInt((time % (60 * 60 * 24)) / (60 * 60))
                const minutes = parseInt((time % (60 * 60)) / (60))
                const seconds = (time % (60)).toFixed(0)
                let str = ''
                if (days) {
                    str = i18n.tc('天', days, { n: days > 99 ? '99+' : days }) + ' '
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
                // this.isNodeInfoPanelShow = false
                this.nodeDetailConfig = {}
                this.cancelTaskStatusTimer()
                this.updateTaskStatus(id)
            },
            async onClickTreeNode (node) {
                const { id, conditionType, parentId, taskId, subprocessStack = [] } = node
                if (this.nodeDetailConfig.node_id) {
                    this.updateNodeActived(this.nodeDetailConfig.node_id, false)
                }
                this.updateNodeActived(id, true)
                let pipelineData = this.nodeTreePipelineData
                if (parentId) {
                    const parentIdList = parentId.split('-')
                    parentIdList.forEach(item => {
                        const nodeData = pipelineData.activities[item]
                        if (nodeData.pipeline) {
                            pipelineData = nodeData.pipeline
                        } else {
                            let { data: componentData } = nodeData.component
                            componentData = componentData && componentData.subprocess
                            componentData = componentData && componentData.value
                            componentData = componentData && componentData.pipeline
                            pipelineData = componentData || pipelineData
                        }
                    })
                }
                let code, version, componentData
                const nodeInfo = pipelineData.activities[id]
                if (nodeInfo) {
                    componentData = nodeInfo.type === 'ServiceActivity' ? nodeInfo.component.data : {}
                    code = nodeInfo.type === 'ServiceActivity' ? nodeInfo.component.code : ''
                    version = (nodeInfo.type === 'ServiceActivity' ? nodeInfo.component.version : nodeInfo.version) || 'legacy'
                }
                let nodeId = id
                this.isCondition = false
                if (conditionType) {
                    nodeId = id.split('-')[0]
                    this.isCondition = true
                    this.conditionData = { ...node }
                }
                this.nodeDetailConfig = {
                    component_code: code,
                    version: version,
                    node_id: nodeId,
                    instance_id: taskId || this.instance_id,
                    taskId,
                    root_node: parentId,
                    subprocess_stack: JSON.stringify(subprocessStack),
                    componentData
                }
                // 节点树切换时，如果为子流程节点则需要重置pipelineData的constants
                this.nodePipelineData = { ...pipelineData }
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
                // 失败时不允许点击暂停按钮，创建是不允许点击终止按钮，操作执行过程不允许点击
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
                            confirmFn: () => {
                                this.isNodeInfoPanelShow = false
                                this.retryNodeId = undefined
                            }
                        })
                    }
                }
            },
            onHiddenSideslider () {
                this.subProcessTaskId = null
                this.nodeInfoType = ''
                this.retryNodeName = ''
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
            /**
             * 移动画布，将节点放到画布左上角
             */
            moveNodeToView (id) {
                // 获取对应dom
                const nodeEl = document.querySelector(`#${id} .canvas-node-item`)
                // 判断dom是否存在当前视图中
                const isInViewPort = this.judgeInViewPort(nodeEl)
                // 如果存在只需要节点摇晃，不存在需要将节点挪到画布中间并节点摇晃
                if (!isInViewPort) {
                    const { width, height } = document.querySelector('#canvasContainer').getBoundingClientRect()
                    const { x, y } = this.canvasData.locations.find(item => item.id === id)
                    const offsetX = (width - 154) / 2 - x
                    const offsetY = (height - 54) / 2 - y
                    this.$refs.templateCanvas.setCanvasPosition(offsetX, offsetY, true)
                }
                // 移动画布到选中节点位置的摇晃效果
                if (nodeEl) {
                    nodeEl.classList.add('node-shake')
                    setTimeout(() => {
                        nodeEl.classList.remove('node-shake')
                    }, 500)
                }
            },
            // dom是否存在当前视图中
            judgeInViewPort (element) {
                if (!element) return false
                const viewWidth = window.innerWidth || document.documentElement.clientWidth
                const viewHeight = window.innerHeight || document.documentElement.clientHeight
                const { top, right, bottom, left } = element.getBoundingClientRect()
                return top >= 0 && left >= 0 && right <= viewWidth && bottom <= viewHeight
            },
            setLineSuspendState (nodeId, lineId, isExecuted, location = 0.5) {
                const tplInstance = this.$refs.templateCanvas
                const line = this.canvasData.lines.find(item => item.id === lineId)
                // 分支添加暂停icon
                if (isExecuted) {
                    // 如果当前连线存在暂停icon，则删除旧的连线再生成新的
                    const pauseDoms = document.querySelectorAll(`.suspend-${lineId}`)
                    if (pauseDoms.length) {
                        tplInstance.setPaintStyle(lineId, '#a9adb6')
                        pauseDoms.forEach(dom => {
                            dom.style.display = 'none'
                        })
                    }
                } else if (location > 0) {
                    // 设置连线颜色
                    tplInstance.setPaintStyle(lineId, '#ffb848')
                    const labelData = {
                        type: 'Label',
                        location,
                        name: `<i class="common-icon-pause"></i>`,
                        cls: `suspend-line suspend-${lineId}`
                    }
                    tplInstance.$refs.jsFlow.addLineOverlay(line, labelData)
                    // 根据暂停icon所在线段的方向设置平移
                    this.$nextTick(() => {
                        const pauseDoms = document.querySelectorAll(`.suspend-${lineId}`)
                        const pauseDom = Array.from(pauseDoms).filter(dom => dom.style.display !== 'none')[0]
                        const direction = this.judgeIntersectSegmentDirection(tplInstance, line, nodeId, pauseDom)
                        if (!pauseDom) return
                        if (direction === 'vertical') { // 垂直
                            const pauseIconDom = pauseDom.querySelector('i')
                            pauseIconDom.style.display = 'inline-block'
                            pauseIconDom.style.transform = 'rotate(90deg)'
                        } else if (!direction) { // icon正在停在弯曲线段上
                            pauseDom.style.display = 'none'
                            // 给曲线上的icon添加偏移计算量太大，改为删除旧的label生成一条偏移量location - 0.1的label
                            this.setLineSuspendState(nodeId, lineId, isExecuted, location - 0.1)
                        }
                    })
                }
            },
            // 计算与暂停图标相交的线段方向
            judgeIntersectSegmentDirection (tplInstance, line, nodeId, pauseDom) {
                // 节点尺寸坐标
                if (!pauseDom) return
                const iconPos = this.getDomPos(pauseDom)
                const { width: iWidth, height: iHeight } = pauseDom.getBoundingClientRect()
                // 存在偏移，所以真实坐标需要减去高/宽的一半
                iconPos.left = iconPos.left - iWidth / 2
                iconPos.top = iconPos.top - iHeight / 2

                // 暂停图标是在水平线还是垂直线还是曲线
                let direction = ''
                // 获取连线实例
                let connection = tplInstance.$refs.jsFlow.getConnectorsByNodeId(nodeId)
                if (Array.isArray(connection)) {
                    connection = connection.find(item => item.sourceId === line.source.id && item.targetId === line.target.id)
                }
                // 连线各个线段
                const { left: lineLeft, top: lineTop } = this.getDomPos(connection.canvas)
                let segments = connection.connector.getSegments()
                // 第一段线段坐标
                const { x1, x2, y1, y2 } = segments[0].params
                const firstSegmentWidth = x2 - x1
                const firstSegmentHeight = y2 - y1
                // 切除插入到节点内部的两端线段
                segments = segments.slice(1, -1)
                // 克隆线段列表，直线时会对线段宽高重新计算，避免影响
                segments = tools.deepClone(segments)
                // 纯直线会重叠了1px，为线的折点预留的位置
                if (segments.length === 2 && segments.every(item => item.type === 'Straight')) {
                    // 整合为一条线段
                    let params = {}
                    const { x1, x2, y1, y2 } = segments[0].params
                    if (x1 === x2) {
                        if (y1 > y2) {
                            params = { x1: 0, x2: 0, y1, y2: 0 }
                        } else {
                            params = { x1: 0, x2: 0, y1: 0, y2: y2 * 2 }
                        }
                    } else if (y1 === y2) {
                        if (x1 > x2) {
                            params = { x1, x2: 0, y1: 0, y2: 0 }
                        } else {
                            params = { x1: 0, x2: x2 * 2, y1: 0, y2: 0 }
                        }
                    }
                    segments[0].params = params
                    segments = segments.slice(0, 1)
                }
                // 过滤掉圆弧线段
                segments = segments.filter(item => item.type === 'Straight')
                segments.some(item => {
                    // 计算线段的高宽和坐标
                    const { x1, x2, y1, y2 } = item.params
                    // 线段的坐标的最大值/最小值
                    const maxX = Math.max(x1, x2)
                    const minX = Math.min(x1, x2)
                    const maxY = Math.max(y1, y2)
                    const minY = Math.min(y1, y2)

                    let left, top, height, width
                    if (x1 === x2) { // 垂直
                        height = maxY - minY
                        top = lineTop + minY + firstSegmentHeight
                        left = lineLeft + minX + firstSegmentWidth
                        if (top < iconPos.top && top + height > iconPos.top + iHeight && left > iconPos.left && left < iconPos.left + iWidth) {
                            direction = 'vertical'
                        }
                    } else if (y1 === y2) { // 水平
                        width = maxX - minX
                        top = lineTop + minY + firstSegmentHeight + 5
                        left = lineLeft + minX + firstSegmentWidth
                        if (top > iconPos.top && top < iconPos.top + iHeight && left < iconPos.left && left + width > iconPos.left + iWidth) {
                            direction = 'horizontal'
                        }
                    }
                    return !!direction
                })
                return direction
            },
            getDomPos (dom) {
                let { cssText } = dom.style
                cssText = cssText.split(';').filter(value => /:.(\-)?[0-9.]+px/.test(value))
                let left = cssText.find(item => item.indexOf('left') > -1)
                left = left ? /:.((\-)?[0-9.]+)px/.exec(left)[1] : 0
                left = Number(left)
                let top = cssText.find(item => item.indexOf('top') > -1)
                top = top ? /:.((\-)?[0-9.]+)px/.exec(top)[1] : 0
                top = Number(top)
                return { left, top }
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
            /deep/ .canvas-wrapper.jsflow {
                background: #f5f7fa;
                .jtk-endpoint {
                    z-index: 2 !important;
                }
            }
        }
    }
}
/deep/.bk-sideslider-content {
    height: calc(100% - 60px);
}
.header {
    display: flex;
    .bread-crumbs-wrapper {
        margin-left: 20px;
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
    .sub-title {
        margin-left: 20px;
    }
    .bread-crumbs-wrapper,
    .sub-title {
        position: relative;
        &::before {
            content: '-';
            position: absolute;
            left: -14px;
        }
    }
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
    /deep/.bk-label {
        width: auto !important;
    }
}
/deep/.suspend-line {
    font-size: 12px;
    color: #ffb946;
    margin-top: -1px;
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
