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
        <div class="details-wrapper">
            <NodeTree
                class="nodeTree"
                :data="nodeData"
                :node-nav="nodeNav"
                :node-display-status="nodeDisplayStatus"
                :selected-flow-path="selectedFlowPath"
                :default-active-id="defaultActiveId"
                :is-condition="isCondition"
                @onOpenGatewayInfo="onOpenGatewayInfo"
                @onNodeClick="onNodeClick"
                @onSelectNode="onSelectNode">
            </NodeTree>
            <div
                v-if="location"
                :class="['execute-info', { 'loading': loading }]"
                v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
                <div class="execute-head">
                    <span class="node-name">{{isCondition ? conditionData.name : executeInfo.name}}</span>
                    <div class="node-state">
                        <span :class="displayStatus"></span>
                        <span class="status-text-messages">{{nodeState}}</span>
                    </div>
                </div>
                <bk-tab
                    :key="nodeDetailConfig.node_id"
                    :active.sync="curActiveTab"
                    type="unborder-card"
                    ext-cls="execute-info-tab"
                    @tab-change="onTabChange">
                    <bk-tab-panel name="record" v-if="!isCondition" :label="$t('执行记录')"></bk-tab-panel>
                    <bk-tab-panel name="config" v-if="isCondition || (['tasknode', 'subflow'].includes(location.type))" :label="$t('配置快照')"></bk-tab-panel>
                    <bk-tab-panel name="history" v-if="!isCondition" :label="$t('操作历史')"></bk-tab-panel>
                    <bk-tab-panel name="log" v-if="!isCondition" :label="$t('调用日志')"></bk-tab-panel>
                </bk-tab>
                <div class="scroll-area" :key="randomKey">
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
                        </section>
                        <ExecuteRecord
                            v-if="curActiveTab === 'record'"
                            :admin-view="adminView"
                            :loading="loading"
                            :location="location"
                            :is-ready-status="isReadyStatus"
                            :node-activity="nodeActivity"
                            :execute-info="executeRecord"
                            :node-detail-config="nodeDetailConfig"
                            :is-sub-process-node="isSubProcessNode">
                        </ExecuteRecord>
                        <ExecuteInfoForm
                            v-else-if="curActiveTab === 'config'"
                            :node-activity="nodeActivity"
                            :execute-info="executeInfo"
                            :node-detail-config="nodeDetailConfig"
                            :constants="pipelineData.constants"
                            :is-third-party-node="isThirdPartyNode"
                            :third-party-node-code="thirdPartyNodeCode"
                            :is-sub-process-node="isSubProcessNode">
                        </ExecuteInfoForm>
                        <section class="info-section" data-test-id="taskExcute_form_operatFlow" v-else-if="curActiveTab === 'history'">
                            <NodeOperationFlow :locations="pipelineData.location" :node-id="executeInfo.id"></NodeOperationFlow>
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
                <div class="action-wrapper" v-if="isShowActionWrap">
                    <template v-if="realTimeState === 'RUNNING' && !isSubProcessNode">
                        <bk-button
                            v-if="nodeDetailConfig.component_code === 'pause_node'"
                            theme="primary"
                            data-test-id="taskExcute_form_resumeBtn"
                            @click="onResumeClick">
                            {{ $t('继续执行') }}
                        </bk-button>
                        <bk-button
                            v-else-if="nodeDetailConfig.component_code === 'bk_approve'"
                            theme="primary"
                            data-test-id="taskExcute_form_approvalBtn"
                            @click="$emit('onApprovalClick', nodeDetailConfig.node_id)">
                            {{ $t('审批') }}
                        </bk-button>
                        <bk-button
                            v-else
                            data-test-id="taskExcute_form_mandatoryFailBtn"
                            @click="mandatoryFailure">
                            {{ $t('强制终止') }}
                        </bk-button>
                    </template>
                    <template v-if="isShowRetryBtn || isShowSkipBtn">
                        <bk-button
                            theme="primary"
                            v-if="isShowRetryBtn"
                            data-test-id="taskExcute_form_retryBtn"
                            @click="onRetryClick">
                            {{ $t('重试') }}
                        </bk-button>
                        <bk-button
                            theme="default"
                            v-if="isShowSkipBtn"
                            data-test-id="taskExcute_form_skipBtn"
                            @click="onSkipClick">
                            {{ $t('跳过') }}
                        </bk-button>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { TASK_STATE_DICT, NODE_DICT } from '@/constants/index.js'
    import NodeTree from './NodeTree'
    import NodeOperationFlow from './ExecuteInfo/NodeOperationFlow.vue'
    import ExecuteRecord from './ExecuteInfo/ExecuteRecord.vue'
    import NodeLog from './ExecuteInfo/NodeLog.vue'
    import ExecuteInfoForm from './ExecuteInfo/ExecuteInfoForm.vue'
    import taskCondition from './taskCondition.vue'

    export default {
        name: 'ExecuteInfo',
        components: {
            NodeTree,
            NodeOperationFlow,
            ExecuteRecord,
            NodeLog,
            ExecuteInfoForm,
            taskCondition
        },
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
            selectedFlowPath: {
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
            gateways: Object,
            conditionData: Object,
            backToVariablePanel: Boolean,
            isReadonly: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                randomKey: '',
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
                isReadyStatus: true,
                isShowSkipBtn: false,
                isShowRetryBtn: false,
                curActiveTab: 'record',
                theExecuteRecord: 0,
                executeRecord: {}
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
            // 节点实时状态
            realTimeState () {
                const nodeStateMap = this.nodeDisplayStatus.children || {}
                return nodeStateMap[this.nodeActivity.id] || 'READY'
            },
            displayStatus () {
                let state = ''
                if (this.realTimeState.state === 'RUNNING') {
                    state = 'common-icon-dark-circle-ellipsis'
                } else if (this.realTimeState.state === 'SUSPENDED') {
                    state = 'common-icon-dark-circle-pause'
                } else if (this.realTimeState.state === 'FINISHED') {
                    state = this.realTimeState.skip ? 'common-icon-fail-skip' : 'bk-icon icon-check-circle-shape'
                } else if (this.realTimeState.state === 'FAILED') {
                    state = 'common-icon-dark-circle-close'
                } else if (this.realTimeState.state === 'CREATED') {
                    state = 'common-icon-waitting'
                } else if (this.realTimeState.state === 'READY') {
                    state = 'common-icon-waitting'
                }
                return state
            },
            nodeState () {
                // 如果整体任务未执行的话不展示描述
                if (this.state === 'CREATED') return i18n.t('未执行')
                // 如果整体任务执行完毕但有的节点没执行的话不展示描述
                if (['FAILED', 'FINISHED'].includes(this.state) && this.realTimeState.state === 'READY') return i18n.t('未执行')
                const { state, skip } = this.realTimeState
                return skip ? i18n.t('失败后跳过') : state && TASK_STATE_DICT[state]
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
                return this.pipelineData.activities[this.nodeDetailConfig.node_id]
            },
            componentValue () {
                return this.isSubProcessNode ? this.nodeActivity.component.data.subprocess.value : {}
            },
            isExecuteTimeShow () {
                return ['record', 'log'].includes(this.curActiveTab) && (this.loop > 1 || this.historyInfo.length > 1)
            },
            isShowActionWrap () {
                // 任务终止时禁止节点操作
                return this.state !== 'REVOKED' && ((this.realTimeState.state === 'RUNNING' && !this.isSubProcessNode) || this.isShowRetryBtn || this.isShowSkipBtn)
            }
        },
        watch: {
            'nodeDetailConfig.node_id': {
                handler (val) {
                    if (val !== undefined) {
                        this.loop = 1
                        this.theExecuteTime = undefined
                        this.curActiveTab = 'record'
                        this.loadNodeInfo()
                    }
                },
                deep: true
            }
        },
        mounted () {
            this.loadNodeInfo()
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActDetail'
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
                        this.isReadyStatus = false
                        this.executeInfo = {}
                        this.theExecuteTime = undefined
                        this.historyInfo = []
                        return
                    }
                    respData = this.adminView && this.engineVer === 1 ? { ...respData, ...respData.execution_info } : respData
                    this.isReadyStatus = ['RUNNING', 'SUSPENDED', 'FINISHED', 'FAILED'].indexOf(respData.state) > -1

                    await this.setFillRecordField(respData)
                    if (this.theExecuteTime === undefined) {
                        this.loop = respData.loop
                        this.theExecuteTime = respData.loop
                    }
                    this.executeInfo = respData
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
                    // 获取执行失败节点是否允许跳过，重试状态
                    if (this.realTimeState.state === 'FAILED') {
                        const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                        this.isShowSkipBtn = this.location.type === 'tasknode' && activity.skippable
                        this.isShowRetryBtn = this.location.type === 'tasknode' ? activity.retryable : false
                    } else {
                        this.isShowSkipBtn = false
                        this.isShowRetryBtn = false
                    }
                } catch (e) {
                    this.theExecuteTime = undefined
                    this.executeInfo = {}
                    this.historyInfo = []
                    console.log(e)
                } finally {
                    this.randomKey = new Date().getTime()
                    this.loading = false
                }
            },
            onNodeClick (id, type, event) {
                this.$emit('onNodeClick', id, type)
            },
            onOpenGatewayInfo (data, isCondition) {
                this.$emit('onOpenGatewayInfo', data, isCondition)
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
                let constants = {}
                let inputsInfo = inputs
                let failInfo = ''
                // 判断是否为旧版子流程
                const islegacySubProcess = !this.isSubProcessNode && this.nodeActivity && this.nodeActivity.type === 'SubProcess'
                // 添加插件输出表单所需上下文
                $.context.input_form.inputs = inputs
                $.context.output_form.outputs = outputs
                $.context.output_form.state = state
                // 获取子流程配置详情
                if (componentCode === 'subprocess_plugin' || islegacySubProcess) {
                    const { constants } = islegacySubProcess ? this.pipelineData : this.componentValue.pipeline
                    this.renderConfig = await this.getSubflowInputsConfig(constants)
                } else if (componentCode) { // 任务节点需要加载标准插件
                    await this.getNodeConfig(componentCode, version, inputs.plugin_version)
                }
                if (this.isSubProcessNode) { // 新版子流程任务节点输入参数处理
                    inputsInfo = Object.keys(inputs).reduce((acc, cur) => {
                        const value = inputs[cur]
                        if (cur === 'subprocess') {
                            Object.keys(value.pipeline.constants).forEach(key => {
                                const data = value.pipeline.constants[key]
                                acc[key] = data.value
                            })
                        } else {
                            acc[cur] = value
                        }
                        return acc
                    }, {})
                } else if (islegacySubProcess) {
                    /**
                     * 兼容旧版本子流程节点输入数据
                     * 获取子流程输入参数 (subflow_detail_var 标识当前为子流程节点详情)
                     */
                    inputsInfo = Object.values(this.pipelineData.constants).reduce((acc, cur) => {
                        if (cur.show_type === 'show') {
                            acc[cur.key] = cur.value
                        }
                        return acc
                    }, {})
                    constants = { subflow_detail_var: true, ...inputsInfo }
                }
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
                    } else if (islegacySubProcess) {
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
            async getTaskNodeDetail () {
                try {
                    if (this.nodeDetailConfig.root_node) return
                    let query = Object.assign({}, this.nodeDetailConfig, { loop: this.theExecuteTime })
                    let res

                    // 非任务节点请求参数不传 component_code
                    if (!this.nodeDetailConfig.component_code) {
                        delete query.component_code
                    }

                    if (this.adminView && this.engineVer === 1) {
                        const { instance_id: task_id, node_id, subprocess_stack } = this.nodeDetailConfig
                        query = { task_id, node_id, subprocess_stack }
                        res = await this.taskflowNodeDetail(query)
                    } else {
                        res = await this.getNodeActDetail(query)
                    }
                    if (res.result) {
                        return res.data
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
                        const res = await this.loadAtomConfig({ atom: type, version })
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
                    formItemConfig.tag_code = key
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
            onTabChange (name) {
                this.curActiveTab = name
                if (['record', 'log'].includes(name)) {
                    this.onSelectExecuteRecord(this.theExecuteRecord)
                }
            },
            onSelectNode (nodeHeirarchy, selectNodeId, nodeType) {
                this.loading = true
                this.$emit('onClickTreeNode', nodeHeirarchy, selectNodeId, nodeType)
            },
            onRetryClick () {
                this.$emit('onRetryClick', this.nodeDetailConfig.node_id)
            },
            onSkipClick () {
                this.$emit('onSkipClick', this.nodeDetailConfig.node_id)
            },
            onResumeClick () {
                this.$emit('onTaskNodeResumeClick', this.nodeDetailConfig.node_id)
            },
            onModifyTimeClick () {
                this.$emit('onModifyTimeClick', this.nodeDetailConfig.node_id)
            },
            mandatoryFailure () {
                this.$emit('onForceFail', this.nodeDetailConfig.node_id)
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
    .nodeTree{
        border-right: 1px solid #DCDEE5;
    }
    .details-wrapper {
        display: flex;
        flex: 1;
        height: calc(100% - 48px);
        border-bottom: 1px solid $commonBorderColor;
    }
    .action-wrapper {
        padding-left: 20px;
        height: 48px;
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
.execute-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-bottom: 0;
    width: 500px;
    height: 100%;
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
    .execute-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        line-height: 20px;
        font-size: 14px;
        padding: 15px 16px 16px;
        .node-name {
            font-weight: 600;
            word-break: break-all;
        }
        .node-state {
            display: flex;
            align-items: center;
            :first-child {
                margin: 2px 5px 0;
            }
        }
    }
    /deep/.execute-info-tab .bk-tab-section{
        padding: 0;
    }
    .scroll-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        padding: 16px 24px 16px 16px;
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
    .common-icon-dark-circle-ellipsis {
        font-size: 14px;
        color: #3a84ff;
    }
    .common-icon-dark-circle-pause {
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
    /deep/ .primary-value.code-editor {
        height: 300px;
    }
}
</style>
