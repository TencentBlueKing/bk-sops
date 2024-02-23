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
            <div slot="aside">
                <NodeTree
                    :tree-data="nodeData"
                    :default-active-id="defaultActiveId"
                    @dynamicLoad="handleDynamicLoad"
                    @onSelectNode="onSelectNode">
                </NodeTree>
            </div>
            <div slot="main" class="execute-content">
                <div class="execute-head">
                    <span class="node-name">{{isCondition ? conditionData.name : nodeActivity.name || executeInfo.name}}</span>
                    <bk-divider direction="vertical"></bk-divider>
                    <div class="node-state">
                        <span :class="displayStatus"></span>
                        <span class="status-text-messages">{{nodeState}}</span>
                    </div>
                </div>
                <div :class="['scroll-box', { 'subprocess-scroll': subProcessPipeline }]">
                    <div
                        class="sub-process"
                        :style="{ height: `${subProcessHeight}px` }"
                        v-if="subProcessPipeline"
                        v-bkloading="{ isLoading: subprocessLoading, opacity: 1, zIndex: 100 }">
                        <TemplateCanvas
                            ref="subProcessCanvas"
                            :key="canvasRandomKey"
                            class="sub-flow"
                            :show-palette="false"
                            :show-tool="false"
                            :editable="false"
                            :canvas-data="canvasData"
                            @onConditionClick="onOpenConditionEdit"
                            @onNodeClick="onNodeClick">
                        </TemplateCanvas>
                        <div class="flow-option">
                            <i
                                class="bk-icon icon-narrow-line"
                                :class="{ 'disabled': zoom === 0.25 }"
                                v-bk-tooltips.top="$t('缩小')"
                                @click="onZoomOut">
                            </i>
                            <i
                                class="bk-icon icon-enlarge-line"
                                :class="{ 'disabled': zoom === 1.5 }"
                                v-bk-tooltips.top="$t('放大')"
                                @click="onZoomIn">
                            </i>
                        </div>
                        <!--可拖拽-->
                        <template v-if="!subprocessLoading">
                            <div class="resize-trigger" @mousedown.left="handleMousedown($event)"></div>
                            <i :class="['resize-proxy', 'top']" ref="resizeProxy"></i>
                            <div class="resize-mask" ref="resizeMask"></div>
                        </template>
                    </div>
                    <div
                        v-if="location"
                        :key="randomKey"
                        :class="['execute-info', { 'loading': loading }]"
                        v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
                        <bk-tab
                            :active.sync="curActiveTab"
                            type="unborder-card"
                            ext-cls="execute-info-tab"
                            @tab-change="onTabChange">
                            <bk-tab-panel name="record" v-if="!isCondition" :label="$t('执行详情')"></bk-tab-panel>
                            <bk-tab-panel name="config" v-if="isCondition || (!loading && ['tasknode', 'subflow'].includes(location.type))" :label="$t('配置快照')"></bk-tab-panel>
                            <bk-tab-panel name="history" v-if="!isCondition" :label="$t('操作历史')"></bk-tab-panel>
                            <bk-tab-panel name="log" v-if="!isCondition" :label="$t('调用日志')"></bk-tab-panel>
                        </bk-tab>
                        <div class="scroll-area">
                            <task-condition
                                v-if="isCondition"
                                ref="conditionEdit"
                                :is-readonly="true"
                                :is-show.sync="isShow"
                                :gateways="gateways"
                                :condition-data="conditionData"
                                @close="close">
                            </task-condition>
                            <template v-else>
                                <section class="execute-time-section" v-if="isExecuteTimeShow">
                                    <div class="cycle-wrap" v-if="loop > 1">
                                        <span>{{$t('第')}}</span>
                                        <bk-select
                                            :clearable="false"
                                            :value="theExecuteTime"
                                            @selected="onSelectExecuteTime">
                                            <bk-option
                                                v-for="index in loop"
                                                :key="index"
                                                :id="index"
                                                :name="index">
                                            </bk-option>
                                        </bk-select>
                                        <span>{{$t('次循环')}}</span>
                                    </div>
                                    <span class="divid-line" v-if="loop > 1 && historyInfo.length > 1"></span>
                                    <div class="time-wrap" v-if="historyInfo.length > 1">
                                        <span>{{$t('第')}}</span>
                                        <bk-select
                                            :clearable="false"
                                            :value="theExecuteRecord"
                                            @selected="onSelectExecuteRecord">
                                            <bk-option
                                                v-for="index in historyInfo.length"
                                                :key="index"
                                                :id="index"
                                                :name="index">
                                            </bk-option>
                                        </bk-select>
                                        <span>{{$t('次执行')}}</span>
                                    </div>
                                    <p class="retry-details-tips" v-if="realTimeState.retry">
                                        <template v-if="autoRetryInfo.m">
                                            {{ $t('包含自动重试 m 次', autoRetryInfo)}}
                                            <span v-if="autoRetryInfo.n">{{ $t('，手动重试 n 次', autoRetryInfo)}}</span>
                                        </template>
                                        <span v-else>{{ $t('包含手动重试 n 次', { n: realTimeState.retry })}}</span>
                                    </p>
                                </section>
                                <ExecuteRecord
                                    v-if="curActiveTab === 'record'"
                                    :admin-view="adminView"
                                    :loading="loading"
                                    :location="location"
                                    :node-state="nodeState"
                                    :node-activity="nodeActivity"
                                    :execute-info="executeRecord"
                                    :node-detail-config="nodeDetailConfig"
                                    :not-performed-sub-node="notPerformedSubNode"
                                    :is-sub-process-node="isSubProcessNode"
                                    @onTabChange="onTabChange">
                                </ExecuteRecord>
                                <ExecuteInfoForm
                                    v-else-if="curActiveTab === 'config'"
                                    :node-activity="nodeActivity"
                                    :execute-info="executeInfo"
                                    :node-detail-config="nodeDetailConfig"
                                    :constants="pipelineData.constants"
                                    :is-third-party-node="isThirdPartyNode"
                                    :third-party-node-code="thirdPartyNodeCode"
                                    :not-performed-sub-node="notPerformedSubNode"
                                    :is-sub-process-node="isSubProcessNode">
                                </ExecuteInfoForm>
                                <section class="info-section" data-test-id="taskExecute_form_operatFlow" v-else-if="curActiveTab === 'history'">
                                    <NodeOperationFlow
                                        :locations="pipelineData.location"
                                        :node-id="executeInfo.id"
                                        :sub-process-task-id="subProcessTaskId"
                                        :not-performed-sub-node="notPerformedSubNode">
                                    </NodeOperationFlow>
                                </section>
                                <NodeLog
                                    v-else-if="curActiveTab === 'log'"
                                    ref="nodeLog"
                                    :admin-view="adminView"
                                    :node-detail-config="nodeDetailConfig"
                                    :execute-info="executeRecord"
                                    :third-party-node-code="thirdPartyNodeCode"
                                    :engine-ver="engineVer">
                                </NodeLog>
                            </template>
                        </div>
                    </div>
                </div>
                <div class="action-wrapper" v-if="isShowActionWrap && !loading">
                    <bk-button
                        v-if="isShowContinueBtn"
                        theme="primary"
                        data-test-id="taskExecute_form_continueBtn"
                        @click="onContinueClick">
                        {{ $t('继续执行') }}
                    </bk-button>
                    <template v-if="['RUNNING', 'PENDING_PROCESSING', 'PENDING_CONFIRMATION', 'PENDING_APPROVAL'].includes(realTimeState.state)">
                        <bk-button
                            v-if="realTimeState.state !== 'PENDING_PROCESSING' && (isLegacySubProcess || isSubProcessNode)"
                            theme="primary"
                            data-test-id="taskExecute_form_pauseBtn"
                            @click="onPauseClick">
                            {{ $t('暂停执行') }}
                        </bk-button>
                        <bk-button
                            v-if="nodeDetailConfig.component_code === 'pause_node'"
                            theme="primary"
                            data-test-id="taskExecute_form_resumeBtn"
                            @click="onResumeClick">
                            {{ $t('确认继续') }}
                        </bk-button>
                        <bk-button
                            v-else-if="nodeDetailConfig.component_code === 'bk_approve'"
                            theme="primary"
                            data-test-id="taskExecute_form_approvalBtn"
                            @click="onApprovalClick">
                            {{ $t('审批') }}
                        </bk-button>
                        <bk-button
                            v-else-if="!isLegacySubProcess"
                            data-test-id="taskExecute_form_mandatoryFailBtn"
                            @click="mandatoryFailure">
                            {{ $t('强制终止') }}
                        </bk-button>
                    </template>
                    <template v-if="isShowRetryBtn || isShowSkipBtn">
                        <span
                            v-bk-tooltips="{
                                content: $t('节点自动重试中，暂时无法手动重试'),
                                disabled: !autoRetryInfo.h || autoRetryInfo.m === autoRetryInfo.c
                            }">
                            <bk-button
                                theme="primary"
                                v-if="isShowRetryBtn"
                                data-test-id="taskExecute_form_retryBtn"
                                :disabled="autoRetryInfo.h && autoRetryInfo.m !== autoRetryInfo.c"
                                @click="onRetryClick">
                                {{ isSubProcessNode ? $t('重试子流程') : $t('重试') }}
                            </bk-button>
                        </span>
                        <bk-button
                            theme="default"
                            v-if="isShowSkipBtn"
                            data-test-id="taskExecute_form_skipBtn"
                            @click="onSkipClick">
                            {{ isSubProcessNode ? $t('跳过子流程') : $t('跳过') }}
                        </bk-button>
                    </template>
                </div>
            </div>
        </bk-resize-layout>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import { mapState, mapActions } from 'vuex'
    import axios from 'axios'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { TASK_STATE_DICT, NODE_DICT } from '@/constants/index.js'
    import { checkDataType, getDefaultValueFormat } from '@/utils/checkDataType.js'
    import NodeTree from './NodeTree'
    import NodeOperationFlow from './ExecuteInfo/NodeOperationFlow.vue'
    import ExecuteRecord from './ExecuteInfo/ExecuteRecord.vue'
    import NodeLog from './ExecuteInfo/NodeLog.vue'
    import ExecuteInfoForm from './ExecuteInfo/ExecuteInfoForm.vue'
    import taskCondition from './taskCondition.vue'
    import lineSuspendState from '@/mixins/lineSuspendState.js'

    const CancelToken = axios.CancelToken
    let source = CancelToken.source()

    export default {
        name: 'ExecuteInfo',
        components: {
            NodeTree,
            NodeOperationFlow,
            ExecuteRecord,
            NodeLog,
            ExecuteInfoForm,
            taskCondition,
            TemplateCanvas
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
            nodeData: {
                type: Array,
                default () {
                    return []
                }
            },
            defaultActiveId: {
                type: String,
                default: ''
            },
            isCondition: {
                type: Boolean,
                default: false
            },
            pipelineData: {
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
            isShow: Boolean,
            constants: Object,
            gateways: Object,
            conditionData: Object,
            backToVariablePanel: Boolean,
            isReadonly: {
                type: Boolean,
                default: false
            },
            smallMapImg: {
                type: String,
                default: ''
            },
            sidebarWidth: Number
        },
        data () {
            return {
                randomKey: '',
                canvasRandomKey: null,
                loading: true,
                isRenderOutputForm: false,
                executeInfo: {},
                pluginOutputs: [],
                historyInfo: [],
                renderConfig: [],
                outputRenderData: {},
                outputRenderConfig: [],
                outputRenderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false,
                    formEdit: true,
                    formMode: true
                },
                loop: 1,
                theExecuteTime: undefined,
                curActiveTab: 'record',
                theExecuteRecord: 0,
                executeRecord: {},
                subFlowData: {},
                subCanvasData: {},
                timer: null,
                subprocessLoading: true,
                subprocessTasks: {},
                subprocessNodeStatus: {},
                subNodesExpanded: [], // 节点树展开的独立子流程节点
                subProcessHeight: 160,
                zoom: 0.75,
                notPerformedSubNode: false // 是否为未执行的独立子流程节点
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config,
                'atomOutputConfig': state => state.atomForm.outputConfig,
                'atomFormInfo': state => state.atomForm.form,
                'pluginOutput': state => state.atomForm.output
            }),
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            autoRetryInfo () {
                const { taskId } = this.nodeDetailConfig
                const retryInfos = taskId
                    ? this.subprocessNodeStatus[taskId].data.auto_retry_infos || {}
                    : this.nodeDisplayStatus.auto_retry_infos || {}
                const retryInfo = retryInfos[this.nodeDetailConfig.node_id] || {}
                return {
                    h: !!Object.keys(retryInfo).length,
                    m: retryInfo.auto_retry_times || 0,
                    c: retryInfo.max_auto_retry_times || 10,
                    n: this.realTimeState.retry - retryInfo.auto_retry_times || 0
                }
            },
            // 节点实时状态
            realTimeState () {
                const { root_node, node_id, taskId } = this.nodeDetailConfig
                let nodes = this.nodeDisplayStatus.children || {}
                // 独立子流程节点状态特殊处理
                if (taskId) {
                    nodes = this.subprocessNodeStatus[taskId]
                    nodes = nodes ? nodes.data.children : {}
                }
                if (this.subProcessPipeline) {
                    const parentId = root_node?.split('-') || []
                    parentId.forEach(id => {
                        if (nodes[id]) {
                            nodes = nodes[id].children
                        }
                    })
                }
                return nodes[node_id] || { state: 'READY' }
            },
            // 子任务状态
            subTaskStatus () {
                const taskId = this.isSubProcessNode ? this.subProcessPipeline.taskId : this.subProcessTaskId
                if (!taskId) return 'READY'
                const stateInfo = this.subprocessNodeStatus[taskId]
                return stateInfo && stateInfo.data.state
            },
            displayStatus () {
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
                        state = skip || error_ignored ? 'common-icon-fail-skip' : 'bk-icon icon-check-circle-shape'
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
            nodeState () {
                // 如果整体任务未执行的话不展示描述
                if (this.state === 'CREATED') return i18n.t('未执行')
                // 如果整体任务执行完毕但有的节点没执行的话不展示描述
                if (['FAILED', 'FINISHED'].includes(this.state) && this.realTimeState.state === 'READY') return i18n.t('未执行')
                const { state, skip, error_ignored } = this.realTimeState
                return skip ? i18n.t('失败后手动跳过') : error_ignored ? i18n.t('失败后自动跳过') : state && TASK_STATE_DICT[state]
            },
            location () {
                const { node_id, subprocess_stack = [] } = this.nodeDetailConfig
                return this.pipelineData.location.find(item => {
                    if (item.id === node_id || subprocess_stack.includes(item.id)) {
                        return true
                    }
                })
            },
            isThirdPartyNode () {
                const compCode = this.nodeDetailConfig.component_code
                return !!compCode && compCode === 'remote_plugin'
            },
            isSubProcessNode () {
                const compCode = this.nodeDetailConfig.component_code
                return !!compCode && compCode === 'subprocess_plugin'
            },
            thirdPartyNodeCode () {
                if (!this.isThirdPartyNode) return ''
                const nodeInfo = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                if (!nodeInfo) return ''
                let codeInfo = nodeInfo.component.data
                codeInfo = codeInfo && codeInfo.plugin_code
                codeInfo = codeInfo.value
                return codeInfo
            },
            nodeActivity () {
                const { node_id: nodeId } = this.nodeDetailConfig
                const { activities, end_event, start_event, gateways } = this.pipelineData
                const nodeMap = {
                    ...activities,
                    ...gateways,
                    [start_event.id]: { ...start_event, name: this.$t('开始节点') },
                    [end_event.id]: { ...end_event, name: this.$t('结束节点') }
                }
                return nodeMap[nodeId]
            },
            isExecuteTimeShow () {
                return ['record', 'log'].includes(this.curActiveTab) && (this.loop > 1 || this.historyInfo.length > 1)
            },
            isShowContinueBtn () {
                if (this.isLegacySubProcess) {
                    return [this.realTimeState.state, this.executeInfo.state].includes('SUSPENDED')
                } else if (this.isSubProcessNode) {
                    const { taskId } = this.subProcessPipeline
                    const taskState = this.subprocessNodeStatus[taskId]?.data?.state
                    return [this.realTimeState.state, taskState].includes('SUSPENDED')
                }
                return false
            },
            isShowSkipBtn () {
                let isShow = false
                if (this.realTimeState.state === 'FAILED') {
                    const { type } = this.location
                    if (type === 'tasknode') {
                        // 任务节点和独立子任务节点
                        const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                        isShow = activity.skippable
                    } else if (type !== 'subflow') {
                        // 网关节点
                        isShow = true
                    }
                }
                return isShow
            },
            isShowRetryBtn () {
                let isShow = false
                if (this.realTimeState.state === 'FAILED') {
                    const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                    isShow = this.location.type === 'tasknode' ? activity.retryable : false
                }
                return isShow
            },
            isExecutingState () {
                return ['RUNNING', 'PENDING_PROCESSING', 'PENDING_APPROVAL', 'PENDING_CONFIRMATION']
            },
            isShowActionWrap () {
                // 任务终止时禁止节点操作
                if (this.state === 'REVOKED' || (!this.isSubProcessNode && this.subTaskStatus === 'REVOKED')) {
                    return false
                }
                // 判断父级节点是否存在失败后跳过
                if (this.nodeDetailConfig.taskId) {
                    const allNodeStatus = {
                        ...this.nodeDisplayStatus.children,
                        ...Object.values(this.subprocessNodeStatus).reduce((acc, item) => {
                            return {
                                ...acc,
                                ...item.data.children
                            }
                        }, {})
                    }

                    const parentIds = this.nodeDetailConfig.root_node.split('-')
                    const isFailedSkip = parentIds.some(id => {
                        const { state, skip } = allNodeStatus[id] || {}
                        return state === 'FINISHED' && skip
                    })

                    if (isFailedSkip) {
                        return false
                    }

                    // 检查根节点的状态，如果有撤销的状态，则不继续执行
                    const rootNodeStates = Object.keys(this.subprocessTasks).reduce((acc, taskId) => {
                        const stateInfo = this.subprocessTasks[taskId]
                        if (parentIds.includes(stateInfo.node_id)) {
                            const { state } = this.subprocessNodeStatus[taskId].data
                            acc.push(state)
                        }
                        return acc
                    }, [])

                    if (rootNodeStates.includes('REVOKED')) {
                        return false
                    }
                }
                const executeState = this.isExecutingState.includes(this.realTimeState.state)
                return executeState
                    || this.isShowRetryBtn
                    || this.isShowSkipBtn
                    || this.isShowContinueBtn
            },
            isLegacySubProcess () { // 是否为旧版子流程
                return !this.isSubProcessNode && this.nodeActivity && this.nodeActivity.type === 'SubProcess'
            },
            subProcessTaskId () { // 独立子流程节点的任务id
                return this.nodeDetailConfig.taskId
            },
            subProcessPipeline () {
                let pipelineData
                if (this.isSubProcessNode || this.isLegacySubProcess) {
                    if (this.nodeActivity.pipeline) {
                        pipelineData = this.nodeActivity.pipeline
                    } else {
                        let { data: componentData } = this.nodeActivity.component
                        componentData = componentData && componentData.subprocess
                        componentData = componentData && componentData.value
                        componentData = componentData && componentData.pipeline
                        pipelineData = componentData || pipelineData
                    }
                } else if (this.nodeDetailConfig.root_node) {
                    pipelineData = this.pipelineData
                }
                return pipelineData
            },
            canvasData () {
                if (!this.subProcessPipeline) return {}
                const { line, location, gateways, activities } = this.subProcessPipeline
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
            }
        },
        watch: {
            nodeDetailConfig: {
                handler (val) {
                    if (val.node_id !== undefined) {
                        this.loop = 1
                        this.theExecuteTime = undefined
                        this.curActiveTab = 'record'
                        // 未执行的独立子流程节点
                        if (this.notPerformedSubNode) {
                            this.loading = false
                            this.subprocessLoading = false
                            this.randomKey = new Date().getTime()
                            const nodeInfo = this.getNodeInfo(this.nodeData, val.root_node, val.node_id)
                            nodeInfo.dynamicLoad = false
                        } else {
                            this.executeInfo.state = ''
                            this.loadNodeInfo()
                        }
                    }
                    if (val.component_code === 'subprocess_plugin') {
                        this.subCanvasData = val.componentData.subprocess.value.pipeline
                        const { lines, locations: nodes } = this.subCanvasData
                        this.subFlowData = {
                            lines,
                            nodes
                        }
                    }
                },
                deep: true
            },
            nodeDisplayStatus: {
                handler (val) {
                    // 设置节点树状态
                    this.nodeAddStatus(this.nodeData, val.children, false)
                    this.updateNodeInfo()
                },
                deep: true,
                immediate: true
            },
            async 'realTimeState.state' (val, oldVal) {
                if (val !== oldVal && this.isSubProcessNode) {
                    await this.loadNodeInfo()
                    // 拉取独立子流程状态
                    const { root_node, component_code, taskId } = this.nodeDetailConfig
                    if (val === 'RUNNING' && taskId && component_code !== 'subprocess_plugin') {
                        const nodes = root_node.split('-')
                        const parentNode = nodes.slice(-1)[0]
                        const parentRoot = nodes.slice(0, -1).join('-')
                        // 获取最新节点树
                        const nodeInfo = this.getNodeInfo(this.nodeData, parentRoot, parentNode)
                        await this.getSubprocessData(taskId, nodeInfo, true)
                        this.subprocessTasks[taskId] = {
                            root_node: parentRoot,
                            node_id: parentNode
                        }
                        // 获取独立子流程任务状态
                        this.loadSubprocessStatus()
                    }
                }
            },
            'realTimeState.subprocess_state': {
                handler (val, oldVal) {
                    // 非独立
                    if (this.isLegacySubProcess) {
                        this.handleLinesSuspendState({
                            state: val,
                            oldState: oldVal,
                            children: this.realTimeState.children
                        })
                    }
                },
                immediate: true
            },
            realTimeState: {
                handler (val, oldVal) {
                    // 节点状态没变，重试次数变了，需要重新获取节点状态
                    const { state, retry } = val
                    const { state: oldState, retry: oldRetry } = oldVal
                    if (state === 'FAILED' && state === oldState && retry !== oldRetry) {
                        this.loadNodeInfo()
                    }
                },
                deep: true
            }
        },
        mounted () {
            this.loadNodeInfo()
            if (this.subProcessPipeline) {
                this.$nextTick(() => {
                    this.setCanvasZoomPosition()
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
                'getNodeActDetail',
                'getTaskInstanceData',
                'getBatchInstanceStatus'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail',
                'loadPluginServiceAppDetail'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeDetail'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    this.renderConfig = []
                    let respData = await this.getTaskNodeDetail()
                    if (!respData) {
                        this.executeInfo = {}
                        this.theExecuteTime = undefined
                        this.historyInfo = []
                        return
                    }
                    respData = this.adminView && this.engineVer === 1 ? { ...respData, ...respData.execution_info } : respData

                    await this.setFillRecordField(respData)
                    if (this.theExecuteTime === undefined) {
                        this.loop = respData.loop
                        this.theExecuteTime = respData.loop
                    }
                    this.executeInfo = respData
                    // 独立子流程任务特殊处理
                    if (this.isSubProcessNode) {
                        const taskInfo = respData.outputsInfo.find(item => item.key === 'task_id') || {}
                        const taskId = taskInfo.value
                        const { root_node, node_id } = this.nodeDetailConfig
                        this.subprocessLoading = true
                        const nodeInfo = this.getNodeInfo(this.nodeData, root_node, node_id)
                        if (taskId) { // 子流程任务已执行才可以查详情和状态
                            // 获取子流程任务详情
                            await this.getSubprocessData(taskId, nodeInfo, true)
                            this.subprocessTasks[taskId] = {
                                root_node,
                                node_id
                            }
                            // 获取独立子流程任务状态
                            await this.loadSubprocessStatus()
                        } else {
                            nodeInfo.dynamicLoad = false
                            this.subprocessLoading = false
                            // 记录子流程展开收起
                            this.setSubNodeExpanded(nodeInfo)
                        }
                    } else if (this.subProcessPipeline) {
                        this.subprocessLoading = false
                    }
                    // 【失败后跳过】过滤掉最新的记录
                    this.historyInfo = respData.skip ? [] : [respData]
                    if (respData.histories) {
                        this.historyInfo.unshift(...respData.histories)
                    }
                    // 记录当前循环下，总共执行的次数
                    this.theExecuteRecord = this.historyInfo.length
                    // 获取记录详情
                    await this.onSelectExecuteRecord(this.theExecuteRecord)
                    this.executeInfo.name = this.location.name || NODE_DICT[this.location.type]
                    const { component_code: componentCode, version } = this.nodeDetailConfig
                    this.executeInfo.plugin_version = this.isThirdPartyNode ? respData.inputs.plugin_version : version
                    if (this.isThirdPartyNode) {
                        const resp = await this.loadPluginServiceAppDetail({ plugin_code: this.thirdPartyNodeCode })
                        this.executeInfo.plugin_name = resp.data.name
                    } else if (atomFilter.isConfigExists(componentCode, version, this.atomFormInfo)) {
                        const pluginInfo = this.atomFormInfo[componentCode][version]
                        this.executeInfo.plugin_name = `${pluginInfo.group_name}-${pluginInfo.name}`
                    }
                } catch (e) {
                    this.theExecuteTime = undefined
                    this.executeInfo = {}
                    this.historyInfo = []
                    console.log(e)
                } finally {
                    this.randomKey = new Date().getTime()
                    this.loading = false
                    this.subprocessLoading = false
                }
            },
            close () {
                this.$emit('close')
            },
            // 补充记录缺少的字段
            async setFillRecordField (record) {
                const { version, component_code: componentCode } = this.nodeDetailConfig
                const { inputs, state } = record
                let outputs = record.outputs
                // 执行记录的outputs可能为Object格式，需要转为Array格式
                if (!this.adminView && !Array.isArray(outputs)) {
                    const executeOutputs = this.executeInfo.outputs
                    outputs = Object.keys(outputs).reduce((acc, key) => {
                        const outputInfo = executeOutputs.find(item => item.key === key)
                        if (outputInfo) {
                            acc.push({ ...outputInfo, value: outputs[key] })
                        } else if (key !== 'ex_data') {
                            acc.push({
                                key,
                                name: key,
                                value: outputs[key],
                                preset: true
                            })
                        }
                        return acc
                    }, [])
                }
                let outputsInfo = []
                const renderData = {}
                const constants = {}
                let inputsInfo = inputs
                let failInfo = ''
                // 添加插件输出表单所需上下文
                $.context.input_form.inputs = inputs
                $.context.output_form.outputs = outputs
                $.context.output_form.state = state
                // 获取子流程配置详情
                if (componentCode === 'subprocess_plugin' || this.isLegacySubProcess) {
                    const { constants } = this.subProcessPipeline
                    const renderConfig = await this.getSubflowInputsConfig(constants)
                    const keys = Object.keys(inputs)
                    this.renderConfig = renderConfig.filter(item => keys.includes(item.tag_code))
                } else if (componentCode) { // 任务节点需要加载标准插件
                    await this.getNodeConfig(componentCode, version, inputs.plugin_version)
                }
                inputsInfo = Object.keys(inputs).reduce((acc, cur) => {
                    const scheme = Array.isArray(this.renderConfig) ? this.renderConfig.find(item => item.tag_code === cur) : null
                    if (scheme) {
                        const defaultValueFormat = getDefaultValueFormat(scheme)
                        const valueType = checkDataType(inputs[cur])
                        const isTypeValid = Array.isArray(defaultValueFormat.type)
                            ? defaultValueFormat.type.indexOf(valueType) > -1
                            : defaultValueFormat.type === valueType
                        // 标记数据类型不同的表单项并原样展示数据
                        if (!isTypeValid) {
                            if ('attrs' in scheme) {
                                scheme.attrs.usedValue = true
                            } else {
                                scheme.attrs = { usedValue: true }
                            }
                        }
                    }
                    acc[cur] = inputs[cur]
                    return acc
                }, {})
                for (const key in inputsInfo) {
                    renderData[key] = inputsInfo[key]
                }

                // 兼容 JOB 执行作业输出参数
                // 输出参数 preset 为 true 或者 preset 为 false 但在输出参数的全局变量中存在时，才展示
                if (componentCode === 'job_execute_task' && inputs.hasOwnProperty('job_global_var')) {
                    outputsInfo = outputs.filter(output => {
                        const outputIndex = inputs['job_global_var'].findIndex(prop => prop.name === output.key)
                        if (!output.preset && outputIndex === -1) {
                            return false
                        }
                        return true
                    })
                } else {
                    if (this.isThirdPartyNode) {
                        const excludeList = []
                        outputsInfo = outputs.filter(item => {
                            if (!item.preset) {
                                excludeList.push(item)
                            }
                            return item.preset
                        })
                        excludeList.forEach(item => {
                            const output = this.pluginOutputs.find(output => output.key === item.key)
                            if (output) {
                                const { name, key } = output
                                const info = {
                                    key,
                                    name,
                                    value: item.value
                                }
                                outputsInfo.push(info)
                            }
                        })
                    } else if (this.isLegacySubProcess) {
                        // 兼容旧版本子流程节点输出数据
                        outputsInfo = outputs.reduce((acc, cur) => {
                            const { value, key } = cur
                            if (key !== 'ex_data') {
                                const constants = this.nodeActivity.pipeline.constants
                                const name = constants[key] ? constants[key].name : key
                                acc.push({ value, name, key })
                            }
                            return acc
                        }, [])
                    } else if (this.adminView) {
                        outputsInfo = outputs
                    } else { // 普通插件展示 preset 为 true 的输出参数
                        outputsInfo = outputs.filter(output => output.preset)
                    }
                }
                if (record.ex_data && record.ex_data.show_ip_log) {
                    failInfo = this.transformFailInfo(record.ex_data.exception_msg)
                } else {
                    failInfo = this.transformFailInfo(record.ex_data)
                }
                this.$set(record, 'renderData', renderData)
                this.$set(record, 'renderConfig', this.renderConfig)
                this.$set(record, 'constants', constants)
                this.$set(record, 'outputsInfo', outputsInfo)
                this.$set(record, 'outputs', outputs)
                this.$set(record, 'inputs', inputsInfo)
                this.$set(record, 'failInfo', failInfo)
                this.$set(record, 'last_time', tools.timeTransform(record.elapsed_time))
                this.$set(record, 'isExpand', true)
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
                        this.subprocessLoading = false
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            async getNodeConfig (type, version, pluginVersion) {
                if (
                    atomFilter.isConfigExists(type, version, this.atomFormConfig)
                    && atomFilter.isConfigExists(type, version, this.atomOutputConfig)
                ) {
                    this.renderConfig = this.atomFormConfig[type][version]
                    this.outputRenderConfig = this.atomOutputConfig[type][version]
                    this.isRenderOutputForm = true
                } else {
                    try {
                        const res = await this.loadAtomConfig({ atom: type, version, scope: 'task' })
                        // 第三方插件节点拼接输出参数
                        if (this.isThirdPartyNode) {
                            const resp = await this.loadPluginServiceDetail({
                                plugin_code: this.thirdPartyNodeCode,
                                plugin_version: pluginVersion,
                                with_app_detail: true
                            })
                            if (!resp.result) return
                            const { outputs: respsOutputs, forms, inputs } = resp.data
                            // 输出参数
                            const storeOutputs = this.pluginOutput['remote_plugin']['1.0.0']
                            const outputs = []
                            for (const [key, val] of Object.entries(respsOutputs.properties)) {
                                outputs.push({
                                    name: val.title,
                                    key,
                                    type: val.type,
                                    schema: { description: val.description || '--' }
                                })
                            }
                            this.pluginOutputs = outputs
                            this.outputRenderConfig = [...storeOutputs, ...outputs]
                            if (forms.renderform) {
                                // 设置host
                                const { origin } = window.location
                                const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${this.thirdPartyNodeCode}/`
                                $.context.bk_plugin_api_host[this.thirdPartyNodeCode] = hostUrl
                                // 输入参数
                                const renderFrom = forms.renderform
                                /* eslint-disable-next-line */
                                eval(renderFrom)
                                const config = $.atoms[this.thirdPartyNodeCode]
                                this.renderConfig = config || []
                            } else {
                                $.atoms[this.thirdPartyNodeCode] = inputs
                                this.renderConfig = inputs || {}
                                this.outputs = [] // jsonschema form输出参数
                            }
                            return
                        }
                        this.renderConfig = this.atomFormConfig[type] && this.atomFormConfig[type][version]
                        if (res.isRenderOutputForm && this.atomOutputConfig[type]) {
                            this.outputRenderConfig = this.atomOutputConfig[type][version]
                        }
                        this.isRenderOutputForm = res.isRenderOutputForm
                    } catch (e) {
                        this.$bkMessage({
                            message: e,
                            theme: 'error',
                            delay: 10000
                        })
                    }
                }
            },
            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubflowInputsConfig (subflowForms) {
                const inputs = []
                const variables = Object.keys(subflowForms)
                    .map(key => subflowForms[key])
                    .filter(item => item.show_type === 'show')
                    .sort((a, b) => a.index - b.index)

                await Promise.all(variables.map(async (variable) => {
                    const { key } = variable
                    const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(variable)
                    const version = variable.version || 'legacy'
                    const isThird = Boolean(variable.plugin_code)
                    const atomConfig = await this.getAtomConfig({ plugin: atom, version, classify, name, isThird })
                    let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    if (variable.is_meta || formItemConfig.meta_transform) {
                        formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                        if (!variable.meta) {
                            variable.meta = tools.deepClone(variable)
                            variable.value = formItemConfig.attrs.value
                        }
                    }
                    // 特殊处理逻辑，针对子流程节点，如果为自定义类型的下拉框变量，默认开始支持用户创建不存在的选项配置项
                    if (variable.custom_type === 'select') {
                        formItemConfig.attrs.allowCreate = true
                    }
                    formItemConfig.tag_code = key.slice(2, -1)
                    formItemConfig.attrs.name = variable.name
                    // 自定义输入框变量正则校验添加到插件配置项
                    if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: i18n.t('默认值不符合正则规则：') + variable.validation
                        })
                    }
                    // 参数填写时为保证每个表单 tag_code 唯一，原表单 tag_code 会被替换为变量 key，导致事件监听不生效
                    if (formItemConfig.hasOwnProperty('events')) {
                        formItemConfig.events.forEach(e => {
                            if (e.source === tagCode) {
                                e.source = '${' + e.source + '}'
                            }
                        })
                    }
                    inputs.push(formItemConfig)
                }))
                return inputs
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (config) {
                const { plugin, version, classify, name } = config
                try {
                    // 先取标准节点缓存的数据
                    const pluginGroup = this.atomFormConfig[plugin]
                    if (pluginGroup && pluginGroup[version]) {
                        return pluginGroup[version]
                    }
                    await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id: this.project_id })
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.log(e)
                }
            },
            transformFailInfo (data) {
                if (!data) {
                    return ''
                }
                if (typeof data === 'string') {
                    const info = data.replace(/\n/g, '<br>')
                    return info
                } else {
                    return data
                }
            },
            onSelectExecuteTime (time) {
                this.theExecuteTime = time
                this.loadNodeInfo()
                this.randomKey = new Date().getTime()
            },
            async onSelectExecuteRecord (time) {
                this.theExecuteRecord = time
                const record = this.historyInfo[time - 1]
                if (record) {
                    if (!('isExpand' in record)) {
                        await this.setFillRecordField(record)
                    }
                    this.executeRecord = record
                } else {
                    this.executeRecord = {}
                }
                this.randomKey = new Date().getTime()
            },
            onNodeClick (node) {
                let parentId = ''
                const { node_id: nodeId, root_node: rootNode } = this.nodeDetailConfig
                if (nodeId === this.subProcessPipeline.id) {
                    parentId = rootNode ? `${rootNode}-${nodeId}` : nodeId
                } else {
                    parentId = rootNode
                }
                const nodeInfo = this.getNodeInfo(this.nodeData, parentId, node)
                if (nodeInfo) {
                    nodeInfo && this.onSelectNode(nodeInfo)
                    const parentInstance = this.$parent.$parent
                    if (nodeInfo.conditionType) {
                        parentInstance.defaultActiveId = node + '-' + nodeInfo.parentId + '-condition'
                    } else {
                        parentInstance.defaultActiveId = node + '-' + nodeInfo.parentId
                    }
                }
            },
            onOpenConditionEdit (data) {
                this.onNodeClick(`${data.nodeId}-${data.id}`)
            },
            onZoomOut () {
                const jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance.onZoomOut()
                this.zoom = jsFlowInstance.zoomRatio / 100
            },
            onZoomIn () {
                const jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance.onZoomIn()
                this.zoom = jsFlowInstance.zoomRatio / 100
            },
            onTabChange (name) {
                this.curActiveTab = name
                if (['record', 'log'].includes(name)) {
                    this.onSelectExecuteRecord(this.theExecuteRecord)
                }
            },
            onSelectNode (node) {
                this.loading = true
                // 如果子节点的父流程为独立任务且未执行时不调接口，默认数据为空
                this.notPerformedSubNode = false
                if (node.parentId && !node.state) {
                    const ids = node.parentId.split('-')
                    const rootId = ids.slice(0, -1).join('-')
                    const parentInfo = this.getNodeInfo(this.nodeData, rootId, ids.pop())
                    if (parentInfo && !parentInfo.state && 'dynamicLoad' in parentInfo) {
                        this.notPerformedSubNode = true
                    }
                }
                if (this.subProcessPipeline) {
                    this.toggleNodeActive(this.nodeDetailConfig.node_id, false)
                }
                // 如果点击的是子流程节点或者是不属于当前所选中节点树的节点，需要重新刷新子流程画布
                let updateCanvas = false
                if (node.isSubProcess) {
                    updateCanvas = node.id !== this.nodeDetailConfig.node_id
                }
                if (!updateCanvas && node.parentId) {
                    const nodeId = node.conditionType ? node.id.split('-')[0] : node.id
                    updateCanvas = !this.subProcessPipeline?.location.find(item => item.id === nodeId)
                }
                if (updateCanvas) {
                    this.canvasRandomKey = new Date().getTime()
                    this.$nextTick(() => {
                        this.setCanvasZoomPosition()
                    })
                }
                this.$emit('onClickTreeNode', node)
                this.$nextTick(() => {
                    if (node.parentId) {
                        this.toggleNodeActive(node.id, true)
                    }
                    let nodeStatus
                    if (node.taskId && Object.keys(this.subprocessNodeStatus).length) {
                        nodeStatus = this.subprocessNodeStatus[node.taskId]
                        nodeStatus = nodeStatus.data.children
                    }
                    this.updateNodeInfo(nodeStatus)
                    if (node.parentId && !node.isSubProcess) { // 只有子流程下的节点在画布上才能找到
                        this.moveNodeToView(node.id)
                    }
                })
                // 清空默认选中节点
                const parentInstance = this.$parent.$parent
                parentInstance.defaultActiveId = ''
            },
            // 移动画布，将节点放到画布中央
            moveNodeToView (id) {
                // 判断dom是否存在当前视图中
                const nodeEl = document.querySelector(`#${id} .canvas-node-item`)
                if (!nodeEl) return
                const isInViewPort = this.judgeInViewPort(nodeEl)
                // 如果不存在需要将节点挪到画布中间
                if (!isInViewPort) {
                    const { width, height } = this.$el.querySelector('#canvasContainer').getBoundingClientRect()
                    const { x, y } = this.canvasData.locations.find(item => item.id === id)
                    const { width: nodeWidth, height: nodeHeight } = nodeEl.getBoundingClientRect()
                    let jsFlowInstance = this.$refs.subProcessCanvas
                    jsFlowInstance = jsFlowInstance.$refs.jsFlow
                    let offsetX = (width - nodeWidth) / 2 - x
                    offsetX = offsetX * jsFlowInstance.zoom
                    let offsetY = (height - nodeHeight) / 2 - y
                    offsetY = offsetY * jsFlowInstance.zoom
                    jsFlowInstance.setCanvasPosition(offsetX, offsetY, true)
                }
            },
            // dom是否存在当前视图中
            judgeInViewPort (element) {
                if (!element) return false
                const { width, height, top: canvasTop, left: canvasLeft } = this.$el.querySelector('.sub-flow').getBoundingClientRect()
                const { top, left } = element.getBoundingClientRect()
                return top > canvasTop && top < canvasTop + height && left > canvasLeft && left < canvasLeft + width
            },
            // 画布初始化时缩放比偏移
            setCanvasZoomPosition () {
                if (!this.canvasData.locations) return
                // 设置默认高度
                const subprocessDom = this.$el.querySelector('.sub-process')
                const { top } = subprocessDom.getBoundingClientRect()
                this.subProcessHeight = window.innerHeight - top - 320
                // 设置缩放比例
                let jsFlowInstance = this.$refs.subProcessCanvas
                jsFlowInstance = jsFlowInstance && jsFlowInstance.$refs.jsFlow
                jsFlowInstance && jsFlowInstance.setZoom(this.zoom, 0, 0)
                // 设置偏移量
                const startNode = this.canvasData.locations.find(item => item.type === 'startpoint')
                // 判断dom是否存在当前视图中
                const nodeEl = document.querySelector(`#${startNode.id} .canvas-node-item`)
                if (!nodeEl) return
                const isInViewPort = this.judgeInViewPort(nodeEl)
                if (!isInViewPort) {
                    let jsFlowInstance = this.$refs.subProcessCanvas
                    jsFlowInstance = jsFlowInstance.$refs.jsFlow
                    const offsetX = (20 - startNode.x) * this.zoom
                    const offsetY = (160 - startNode.y) * this.zoom
                    jsFlowInstance && jsFlowInstance.setCanvasPosition(offsetX, offsetY, true)
                }
            },

            toggleNodeActive (id, isActive) {
                const node = document.getElementById(id)
                if (!id || !node) return
                if (!isActive) {
                    node.classList.remove('active')
                } else {
                    node.classList.add('active')
                }
            },
            // 设置节点树状态
            nodeAddStatus (treeData = [], states, independent) {
                treeData.forEach(node => {
                    const { id, conditionType, isSubProcess, children, taskId } = node
                    if (conditionType) {
                        if (children?.length) {
                            this.nodeAddStatus(children, states, independent)
                        }
                        return
                    }
                    if (!states[id]) {
                        if (independent && taskId) {
                            this.$set(node, 'state', '')
                        }
                        return
                    }
                    const nodeState = states[id].skip ? 'SKIP' : states[id].state
                    this.$set(node, 'state', nodeState)
                    if (this.subNodesExpanded.includes(node.id)) {
                        const index = this.subNodesExpanded.findIndex(item => item === node.id)
                        if (index > -1) {
                            this.subNodesExpanded.splice(index, 1)
                        }
                        this.handleDynamicLoad(node, true)
                    }
                    if (children) {
                        const newStates = isSubProcess ? Object.assign({}, states, states[id].children) : states
                        this.nodeAddStatus(children, newStates, independent)
                    }
                })
            },
            /**
             * 更新子流程画布
             * nodeStatus 独立子流程任务状态
            */
            updateNodeInfo (nodeStatus, retryInfo = {}) {
                if (!this.subProcessPipeline) return
                const { root_node, node_id } = this.nodeDetailConfig
                const parentId = root_node?.split('-') || []
                if (this.isSubProcessNode || this.isLegacySubProcess) {
                    parentId.push(node_id)
                }
                let nodes = nodeStatus || this.nodeDisplayStatus.children
                parentId.forEach(id => {
                    if (nodes[id]) {
                        nodes = nodes[id].children
                    }
                })
                for (const id in nodes) {
                    let code, skippable, retryable, errorIgnorable, autoRetry
                    const currentNode = nodes[id]
                    const nodeActivity = this.subProcessPipeline.activities[id]
                    // 独立子流程节点特殊处理
                    if (this.subProcessTaskId && !nodeStatus) {
                        return
                    }

                    if (nodeActivity) {
                        code = nodeActivity.component ? nodeActivity.component.code : ''
                        skippable = nodeActivity.isSkipped || nodeActivity.skippable
                        retryable = nodeActivity.can_retry || nodeActivity.retryable
                        errorIgnorable = nodeActivity.error_ignorable
                        autoRetry = nodeActivity.auto_retry
                    }
                    const data = {
                        code,
                        skippable,
                        retryable,
                        loop: currentNode.loop,
                        status: currentNode.state,
                        skip: currentNode.skip,
                        auto_retry_info: retryInfo[id] || {},
                        retry: currentNode.retry,
                        error_ignored: currentNode.error_ignored,
                        error_ignorable: errorIgnorable,
                        auto_retry: autoRetry,
                        ready: false,
                        task_state: this.state // 任务状态
                    }

                    this.$nextTick(() => {
                        this.onUpdateNodeInfo(id, data)
                    })
                }
            },
            onUpdateNodeInfo (id, info) {
                this.$refs.subProcessCanvas && this.$refs.subProcessCanvas.onUpdateNodeInfo(id, info)
            },
            // 只点击子流程展开/收起
            async handleDynamicLoad (node, updateState) {
                try {
                    if (!updateState) {
                        // 独立子流程任务节点
                        if (!node.dynamicLoad) return
                        // 记录子流程展开收起
                        this.setSubNodeExpanded(node)
                        // 节点收起
                        if (!node.expanded) return
                        // 子流程任务未执行时，节点树从父流程取
                        if (!node.state) {
                            node.dynamicLoad = false
                            this.subprocessLoading = false
                            return
                        }
                    }
                    const { id, parentId } = node
                    const { instance_id } = this.$route.query
                    // 该独立子流程节点的父流程也可能为独立子流程
                    const nodeDetailConfig = this.getNodeDetailConfig(node, node.taskId || instance_id)
                    const nodeConfig = await this.getTaskNodeDetail(nodeDetailConfig)
                    if (!nodeConfig) return
                    // 获取子流程任务id
                    const taskInfo = nodeConfig.outputs.find(item => item.key === 'task_id') || {}
                    const taskId = taskInfo.value
                    this.subprocessLoading = false
                    if (taskId) { // 子流程任务已执行才可以查详情和状态
                        await this.getSubprocessData(taskId, node, updateState)
                        this.subprocessTasks[taskId] = {
                            root_node: parentId,
                            node_id: id
                        }
                        this.loadSubprocessStatus()
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
                    componentData = nodeInfo.component.data
                    code = nodeInfo.component.code
                    version = nodeInfo.component.version || 'legacy'
                }
                this.isCondition = false
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
            // 获取独立子流程节点详情
            async getSubprocessData (taskId, nodeInfo, updateState) {
                try {
                    const parentId = nodeInfo.parentId?.split('-') || []
                    if (nodeInfo.dynamicLoad || updateState) {
                        if (source) {
                            source.cancel('cancelled') // 取消定时器里已经执行的请求
                            this.timer = null
                        }
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
                        const parentInstance = this.$parent.$parent
                        parentInstance.nodeIds[pipelineTree.id] = []
                        nodeInfo.children = parentInstance.getOrderedTree(pipelineTree, parentInfo)
                        nodeInfo.dynamicLoad = false
                        nodeInfo.expanded = true

                        let pipelineData = parentInstance.nodeTreePipelineData
                        if (parentId) {
                            parentId.forEach(item => {
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
                        const nodeActivity = pipelineData.activities[nodeInfo.id]
                        this.$set(nodeActivity, 'pipeline', { ...pipelineTree, taskId })
                        this.canvasRandomKey = new Date().getTime()
                        this.$nextTick(() => {
                            this.setCanvasZoomPosition()
                        })
                    }
                } catch (error) {
                    console.warn(error)
                    this.subprocessLoading = false
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
            getNodeInfo (data, rootId, nodeId) {
                let nodes = data
                if (rootId) {
                    const parentId = rootId.split('-') || []
                    parentId.forEach(id => {
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
                    const { id, children } = item
                    if (id === nodeId) {
                        nodeInfo = item
                        return true
                    } else if (children && children.length) {
                        nodeInfo = this.getNodeInfo(item.children, '', nodeId)
                        return !!nodeInfo
                    }
                })
                return nodeInfo
            },
            async loadSubprocessStatus () {
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
                    // 当前展示的子任务id
                    const taskId = this.isSubProcessNode ? this.subProcessPipeline.taskId : this.subProcessTaskId
                    // 记录之前的子任务状态
                    const { state: oldState } = this.subprocessNodeStatus[taskId]?.data || {}

                    Object.keys(resp.data).forEach(key => {
                        this.$set(this.subprocessNodeStatus, key, resp.data[key])
                    })
                    for (const [key, value] of Object.entries(resp.data)) {
                        const { root_node, node_id } = this.subprocessTasks[key] || {}
                        const nodeInfo = this.getNodeInfo(this.nodeData, root_node, node_id)
                        const { auto_retry_infos: retryInfo, children, state } = value.data
                        // 如果子任务暂停时，节点存在READY状态则将状态置为PENDING_TASK_CONTINUE
                        Object.values(children).forEach(item => {
                            item.state = state === 'SUSPENDED' && item.state === 'READY' ? 'PENDING_TASK_CONTINUE' : item.state
                        })
                        this.nodeAddStatus(nodeInfo.children, children, true)
                        this.updateNodeInfo(children, retryInfo)
                        
                        let continueRunning = ['CREATED', 'RUNNING', 'PENDING_PROCESSING'].includes(state)
                        // 任务暂停时如果有节点正在执行，需轮询节点状态
                        if (state === 'SUSPENDED') {
                            continueRunning = Object.values(children).some(item => this.isExecutingState.includes(item.state))
                        }
                        // 任务失败时如果又节点还没自动重试完，需轮询节点状态
                        if (state === 'FAILED') {
                            continueRunning = Object.values(retryInfo).some(item => item.max_auto_retry_times > item.auto_retry_times)
                        }
                        if (!continueRunning) {
                            // 添加notContinue字段，防止子任务继续请求
                            this.subprocessTasks[key].notContinue = true
                        }
                    }
                    const isContinue = Object.values(this.subprocessTasks).some(item => !item.notContinue)
                    if (isContinue) {
                        this.setTaskStatusTimer()
                    }
                    // 根据子任务的状态，设置边的暂停样式
                    const { state, children = {} } = resp.data[taskId]?.data || {}
                    this.handleLinesSuspendState({ state, oldState, children })
                } catch (error) {
                    console.warn(error)
                } finally {
                    source = null
                }
            },
            // 根据子任务的状态，设置边的暂停样式
            handleLinesSuspendState (info) {
                const { state, oldState, children = {} } = info
                if (![state, oldState].includes('SUSPENDED')) return
                const { activities, gateways, flows, start_event, end_event } = tools.deepClone(this.subProcessPipeline)
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
                        const isExecuted = state === 'SUSPENDED' ? (node.state === 'PENDING_TASK_CONTINUE' || targetNode in children) : true
                        // 输出节点未被执行则表明任务暂停后该分支在当前节点停止往下继续执行
                        this.$nextTick(() => {
                            this.setLineSuspendState({
                                nodeId: node.id,
                                lineId: outLine,
                                isExecuted,
                                location: 0.5,
                                ref: 'subProcessCanvas'
                            })
                        })
                    })
                })
            },
            setTaskStatusTimer (time = 3000) {
                this.cancelTaskStatusTimer()
                this.timer = setTimeout(() => {
                    this.loadSubprocessStatus()
                }, time)
            },
            cancelTaskStatusTimer () {
                if (this.timer) {
                    clearTimeout(this.timer)
                    this.timer = null
                }
            },
            onRetryClick () {
                const info = {
                    name: this.executeInfo.name,
                    taskId: this.subProcessTaskId,
                    isSubProcessNode: this.isSubProcessNode,
                    isSubNode: !!this.nodeDetailConfig.root_node
                }
                this.$emit('onRetryClick', this.nodeDetailConfig.node_id, info)
            },
            onSkipClick () {
                const info = {
                    name: this.executeInfo.name,
                    taskId: this.subProcessTaskId,
                    isSubProcessNode: this.isSubProcessNode
                }
                this.$emit('onSkipClick', this.nodeDetailConfig.node_id, info)
            },
            onResumeClick () {
                this.$emit('onTaskNodeResumeClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            onApprovalClick () {
                this.$emit('onApprovalClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            onModifyTimeClick () {
                this.$emit('onModifyTimeClick', this.nodeDetailConfig.node_id, this.subProcessTaskId)
            },
            mandatoryFailure () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subProcessPipeline.taskId : this.subProcessTaskId
                const info = {
                    name: this.executeInfo.name,
                    taskId,
                    isSubProcessNode: this.isSubProcessNode
                }
                this.$emit('onForceFail', this.nodeDetailConfig.node_id, info)
            },
            onPauseClick () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subProcessPipeline.taskId : this.subProcessTaskId
                const info = {
                    taskId,
                    name: this.executeInfo.name,
                    independent: this.isSubProcessNode
                }
                this.$emit('onPauseClick', this.nodeDetailConfig.node_id, info)
            },
            onContinueClick () {
                // 节点绑定的是父流程的taskId，独立子流程节点操作应从子流程树中取taskId
                const taskId = this.isSubProcessNode ? this.subProcessPipeline.taskId : this.subProcessTaskId
                const info = {
                    taskId,
                    name: this.executeInfo.name,
                    independent: this.isSubProcessNode
                }
                this.$emit('onContinueClick', this.nodeDetailConfig.node_id, info)
            },
            handleMousedown (event) {
                this.updateResizeMaskStyle()
                this.updateResizeProxyStyle()
                document.addEventListener('mousemove', this.handleMouseMove)
                document.addEventListener('mouseup', this.handleMouseUp)
            },
            handleMouseMove (event) {
                const flowDom = this.$el.querySelector('.sub-flow')
                const { top: flowTop } = flowDom.getBoundingClientRect()
                let top = event.clientY - flowTop
                let maxHeight = window.innerHeight - 180
                maxHeight = maxHeight - (this.isShowActionWrap ? 48 : 0)
                top = top > maxHeight ? maxHeight : top
                top = top < 160 ? 160 : top
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.top = `${top}px`
            },
            updateResizeMaskStyle () {
                const resizeMask = this.$refs.resizeMask
                resizeMask.style.display = 'block'
                resizeMask.style.cursor = 'row-resize'
            },
            updateResizeProxyStyle () {
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'visible'
            },
            handleMouseUp () {
                const resizeMask = this.$refs.resizeMask
                const resizeProxy = this.$refs.resizeProxy
                resizeProxy.style.visibility = 'hidden'
                resizeMask.style.display = 'none'
                this.subProcessHeight = resizeProxy.style.top.slice(0, -2)
                document.removeEventListener('mousemove', this.handleMouseMove)
                document.removeEventListener('mouseup', this.handleMouseUp)
            }
        }
    }
</script>
<style lang="scss">
    .log-info {
        .common-section-title {
            margin-bottom: 10px;
        }
        .bk-tab-header {
            top: -10px;
        }
        .bk-tab-section {
            padding: 0px;
        }
        .no-data-wrapper {
            margin-top: 50px;
        }
    }
</style>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
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
        .common-icon-fail-skip {
            font-size: 14px;
            color: #f7b6b6;
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
    .sub-process {
        flex-shrink: 0;
        height: 320px;
        margin: 0 25px 8px 15px;
        position: relative;
        background: #f5f7fa;
        .sub-flow {
            height: 100%;
            border: 0;
            /deep/.canvas-wrapper {
                background: #f5f7fa;
            }
            /deep/.canvas-flow {
                .active {
                    box-shadow: none;
                    &::before {
                        content: '';
                        display: block;
                        height: calc(100% + 16px);
                        width: calc(100% + 16px);
                        position: absolute;
                        top: -9px;
                        left: -9px;
                        z-index: -1;
                        background: #e1ecff;
                        border: 1px solid #1768ef;
                        border-radius: 2px;
                    }
                }
                .state-icon {
                    display: none;
                }
                .task-node {
                    &.actived {
                        .node-name {
                            border-color: #b4becd !important;
                            background-color: #fff !important;
                        }
                    }
                }
            }
            /deep/.node-tips-content {
                display: none;
            }
        }
        .flow-option {
            width: 68px;
            height: 32px;
            position: absolute;
            bottom: 16px;
            right: 16px;
            z-index: 5;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: #979ba5;
            background: #fff;
            box-shadow: 0 2px 4px 0 #0000001a;
            border-radius: 2px;
            i {
                cursor: pointer;
                &:last-child {
                    margin-left: 14px;
                }
                &:hover {
                    color: #3a84ff;
                }
                &.disabled {
                    color: #ccc;
                    cursor: not-allowed;
                }
            }
        }
    }
    .execute-info {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding-bottom: 0;
        color: #313238;
        &.loading {
            overflow: hidden;
        }
        &.admin-view {
            .code-block-wrap {
                background: #313238;
                padding: 10px;
                /deep/ .vjs-tree {
                    color: #ffffff;
                }
            }
        }
        /deep/ .vjs-tree {
            font-size: 12px;
        }
        /deep/.execute-info-tab .bk-tab-section{
            padding: 0;
        }
        .scroll-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            padding: 16px 24px 18px 15px;
            @include scrollbar;
        }
        .execute-time-section {
            display: flex;
            align-items: center;
            height: 40px;
            font-size: 12px;
            padding: 8px 16px;
            background: #f5f7fa;
            margin-bottom: 24px;
            .cycle-wrap,
            .time-wrap {
                display: flex;
                align-items: center;
                /deep/.bk-select {
                    width: 64px;
                    height: 24px;
                    line-height: 22px !important;
                    margin: 0 8px;
                    .bk-select-angle {
                        top: 0;
                    }
                    .bk-select-name {
                        height: 24px;
                    }
                }
            }
            .divid-line {
                display: inline-block;
                width: 1px;
                height: 16px;
                margin: 0 16px;
                background: #dcdee5;
            }
            .retry-details-tips {
                color: #979ba5;
                margin-left: 16px;
            }
        }
        .panel-title {
            margin: 0;
            color: #313238;
            font-size: 14px;
            font-weight: 600;
        }
        /deep/.common-section-title {
            color: #313238;
            font-weight: 600;
            line-height: 18px;
            font-size: 12px;
            margin-bottom: 16px;
            &::before {
                height: 18px;
                top: 0;
            }
        }
        /deep/ .primary-value.code-editor {
            height: 300px;
        }
        /deep/.log-section {
            min-height: 758px;
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
            .scroll-area {
                overflow-y: initial;
            }
        }
    }
    .resize-trigger {
        height: 5px;
        width: calc(100% + 40px);
        position: absolute;
        left: -15px;
        bottom: -5px;
        cursor: row-resize;
        z-index: 3;
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 1px;
            width: 100%;
        }
        &::after {
            content: "";
            position: absolute;
            top: 5px;
            right: 50%;
            width: 2px;
            height: 2px;
            color: #979ba5;
            transform: translate3d(0,-50%,0);
            background: currentColor;
            box-shadow: 4px 0 0 0 currentColor,8px 0 0 0 currentColor,-4px 0 0 0 currentColor,-8px 0 0 0 currentColor;
        }
        &:hover::before {
            background-color: #3a84ff;
        }
    }
    .resize-proxy {
        visibility: hidden;
        position: absolute;
        pointer-events: none;
        z-index: 9999;
        &.top {
            top: 320px;
            left: -15px;
            width: calc(100% + 40px);
            border-top: 1px dashed #3a84ff;
        }
    }
    .resize-mask {
        display: none;
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        z-index: 9999;
    }
}
</style>
