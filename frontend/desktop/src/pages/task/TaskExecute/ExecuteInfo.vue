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
        <NodeTree
            class="nodeTree"
            :data="nodeData"
            :selected-flow-path="selectedFlowPath"
            :default-active-id="defaultActiveId"
            @onSelectNode="onSelectNode">
        </NodeTree>
        <div
            v-if="location"
            :class="['execute-info', { 'loading': loading, 'admin-view': adminView }]"
            v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
            <div class="excute-time" v-if="!adminView && isReadyStatus">
                <span>{{$t('第')}}</span>
                <bk-select
                    :clearable="false"
                    :value="theExecuteTime"
                    @selected="onSelectExecuteTime">
                    <bk-option
                        v-for="index in loopTimes"
                        :key="index"
                        :id="index"
                        :name="index">
                    </bk-option>
                </bk-select>
                <span>{{$t('次循环')}}</span>
            </div>
            <div class="execute-head">
                <div class="node-name">
                    <span>{{executeInfo.name}}</span>
                    <div class="node-state">
                        <span :class="displayStatus"></span>
                        <span class="status-text-messages">{{nodeState}}</span>
                    </div>
                </div>
            </div>
            <div class="scroll-area" :key="randomKey">
                <ExecuteInfoForm
                    :is-ready-status="isReadyStatus"
                    :admin-view="adminView"
                    :execute-info="executeInfo">
                </ExecuteInfoForm>
                <section class="info-section" data-test-id="taskExcute_form_operatFlow" v-if="executeInfo.id && location.type !== 'subflow'">
                    <h4 class="common-section-title">{{ $t('操作流水') }}</h4>
                    <OperationFlow :locations="pipelineData.location" :node-id="executeInfo.id"></OperationFlow>
                </section>
                <template v-if="['tasknode', 'subflow'].includes(location.type)">
                    <InputParams
                        :admin-view="adminView"
                        :inputs="inputsInfo"
                        :render-config="renderConfig"
                        :constants="subFlowConstants"
                        :render-data="renderData">
                    </InputParams>
                    <OutputParams
                        :admin-view="adminView"
                        :outputs="outputsInfo"
                        :node-detail-config="nodeDetailConfig">
                    </OutputParams>
                </template>
                <section
                    class="info-section"
                    data-test-id="taskExcute_form_outputFrom"
                    v-if="isRenderOutputForm && outputRenderConfig && outputRenderConfig.length !== 0 && !loading">
                    <h4 class="common-section-title">{{ $t('输出表单') }}</h4>
                    <div class="code-block-wrap">
                        <RenderForm
                            :scheme="outputRenderConfig"
                            :form-option="outputRenderOption"
                            v-model="outputRenderData">
                        </RenderForm>
                    </div>
                </section>
                <NodeLog
                    ref="nodeLog"
                    :node-detail-config="nodeDetailConfig"
                    :execute-info="executeInfo"
                    :third-party-node-code="thirdPartyNodeCode"
                    :engine-ver="engineVer">
                </NodeLog>
                <section class="info-section" data-test-id="taskExcute_form_exceptionInfo" v-if="executeInfo.ex_data">
                    <h4 class="common-section-title">{{ $t('异常信息') }}</h4>
                    <div v-html="failInfo"></div>
                    <IpLogContent
                        v-if="executeInfo.ex_data.show_ip_log"
                        :project-id="renderData.biz_cc_id"
                        :node-info="executeInfo">
                    </IpLogContent>
                </section>
                <ExecuteLog
                    :admin-view="adminView"
                    :history-info="historyInfo"
                    :is-third-party-node="isThirdPartyNode"
                    :third-party-node-code="thirdPartyNodeCode"
                    :node-detail-config="nodeDetailConfig"
                    :engine-ver="engineVer">
                </ExecuteLog>
            </div>
            <div v-if="executeInfo.state === 'RUNNING'" class="action-wrapper">
                <bk-button
                    v-if="nodeDetailConfig.component_code === 'pause_node'"
                    theme="primary"
                    data-test-id="taskExcute_form_resumeBtn"
                    @click="onResumeClick">
                    {{ $t('继续执行') }}
                </bk-button>
                <span
                    v-if="nodeDetailConfig.component_code === 'sleep_timer'"
                    v-bk-tooltips="{
                        content: $t('修改时间实际是强制失败后重试节点，需配置可重试才能修改时间'),
                        disabled: nodeActivity.retryable !== false,
                        hideOnClick: false
                    }">
                    <bk-button
                        theme="primary"
                        :disabled="nodeActivity.retryable === false"
                        data-test-id="taskExcute_form_modifyTimeBtn"
                        @click="onModifyTimeClick">
                        {{ $t('修改时间') }}
                    </bk-button>
                </span>
                <bk-button
                    v-if="nodeDetailConfig.component_code === 'bk_approve'"
                    theme="primary"
                    data-test-id="taskExcute_form_approvalBtn"
                    @click="$emit('onApprovalClick', nodeDetailConfig.node_id)">
                    {{ $t('审批') }}
                </bk-button>
                <bk-button
                    v-if="location.type !== 'subflow'"
                    data-test-id="taskExcute_form_mandatoryFailBtn"
                    @click="mandatoryFailure">
                    {{ $t('强制失败') }}
                </bk-button>
            </div>
            <div class="action-wrapper" v-if="isShowRetryBtn || isShowSkipBtn">
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
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import IpLogContent from '@/components/common/Individualization/IpLogContent.vue'
    import NodeTree from './NodeTree'
    import OperationFlow from './OperationFlow.vue'
    import ExecuteInfoForm from './ExecuteInfo/ExecuteInfoForm.vue'
    import InputParams from './ExecuteInfo/InputParams.vue'
    import OutputParams from './ExecuteInfo/OutputParams.vue'
    import NodeLog from './ExecuteInfo/NodeLog.vue'
    import ExecuteLog from './ExecuteInfo/ExecuteLog.vue'

    export default {
        name: 'ExecuteInfo',
        components: {
            RenderForm,
            IpLogContent,
            NodeTree,
            OperationFlow,
            ExecuteInfoForm,
            InputParams,
            OutputParams,
            NodeLog,
            ExecuteLog
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
            defaultActiveId: {
                type: String,
                default: ''
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
            }
        },
        data () {
            return {
                randomKey: '',
                loading: true,
                isRenderOutputForm: false,
                executeInfo: {},
                inputsInfo: {},
                pluginOutputs: [],
                outputsInfo: [],
                logInfo: '',
                historyInfo: [],
                failInfo: '',
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
                renderData: {},
                subFlowConstants: {}, // 子流程constants
                loop: 1,
                theExecuteTime: undefined,
                isReadyStatus: true,
                isShowSkipBtn: false,
                isShowRetryBtn: false
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
            noDataMessage () {
                return i18n.t('请点击标准插件节点查看参数')
            },
            displayStatus () {
                let state = ''
                if (this.executeInfo.state === 'RUNNING') {
                    state = 'common-icon-dark-circle-ellipsis'
                } else if (this.executeInfo.state === 'SUSPENDED') {
                    state = 'common-icon-dark-circle-pause'
                } else if (this.executeInfo.state === 'FINISHED') {
                    state = 'bk-icon icon-check-circle-shape'
                } else if (this.executeInfo.state === 'FAILED') {
                    state = 'common-icon-dark-circle-close'
                } else if (this.executeInfo.state === 'CREATED') {
                    state = 'common-icon-dark-circle-shape'
                } else if (this.executeInfo.state === 'READY') {
                    state = 'common-icon-dark-circle-shape'
                }
                return state
            },
            nodeState () {
                // 如果整体任务未执行的话不展示描述
                if (this.state === 'CREATED') return ''
                // 如果整体任务执行完毕但有的节点没执行的话不展示描述
                if (['FAILED', 'FINISHED'].includes(this.state) && this.executeInfo.state === 'READY') return ''
                return this.executeInfo.state && TASK_STATE_DICT[this.executeInfo.state]
            },
            loopTimes () {
                const times = []
                for (let i = 0; i < this.loop; i++) {
                    times.push(this.loop - i)
                }

                return times
            },
            currentNode () {
                return this.selectedFlowPath.slice(-1)[0].id
            },
            location () {
                const { node_id, subprocess_stack } = this.nodeDetailConfig
                return this.pipelineData.location.find(item => {
                    if (item.id === node_id || subprocess_stack.includes(item.id)) {
                        return true
                    }
                })
            },
            isThirdPartyNode () {
                const compCode = this.nodeDetailConfig.component_code
                return compCode && compCode === 'remote_plugin'
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
            isSubFlow () {
                return this.location.type === 'subflow'
            },
            nodeActivity () {
                return this.pipelineData.activities[this.nodeDetailConfig.node_id]
            }
        },
        watch: {
            'nodeDetailConfig.node_id' (val) {
                if (val !== undefined) {
                    this.theExecuteTime = undefined
                    this.executeInfo = {}
                    this.inputsInfo = {}
                    this.outputsInfo = []
                    this.logInfo = ''
                    this.historyInfo = []
                    this.failInfo = ''
                    this.randomKey = new Date().getTime()
                    this.loadNodeInfo()
                }
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
                    const respData = await this.getTaskNodeDetail()
                    if (!respData) {
                        this.isReadyStatus = false
                        this.executeInfo = {}
                        this.outputsInfo = []
                        this.inputsInfo = {}
                        this.subFlowConstants = {}
                        this.renderData = {}
                        this.logInfo = ''
                        return
                    }
                    const { execution_info, outputs, log, history } = respData
                    const inputs = respData.inputs || {}
                    const state = this.adminView ? execution_info.state : respData.state
                    this.isReadyStatus = ['RUNNING', 'SUSPENDED', 'FINISHED', 'FAILED'].indexOf(state) > -1
                    const version = this.nodeDetailConfig.version
                    const componentCode = this.nodeDetailConfig.component_code

                    // 添加插件输出表单所需上下文
                    $.context.input_form.inputs = inputs
                    $.context.output_form.outputs = outputs
                    $.context.output_form.state = state

                    // 任务节点需要加载标准插件
                    if (componentCode) {
                        await this.getNodeConfig(componentCode, version, inputs.plugin_version)
                    } else if (this.location.type === 'subflow') { // 获取子流程配置详情
                        const constants = this.pipelineData.constants
                        this.renderConfig = await this.getSubflowInputsConfig(constants)
                    }
                    if (this.adminView) {
                        this.executeInfo = execution_info
                        this.outputsInfo = outputs
                        this.inputsInfo = inputs
                        this.logInfo = log
                        history.forEach(item => {
                            this.$set(item, 'historyLogTab', 'build_in_plugin')
                            this.$set(item, 'scrollId', '')
                            this.$set(item, 'observer', null)
                            this.$set(item, 'pageInfo', null)
                        })
                        this.historyInfo = history.sort((a, b) => {
                            if (a.loop === b.loop) {
                                return b.history_id - a.history_id
                            } else {
                                return b.loop - a.loop
                            }
                        })
                    } else {
                        this.executeInfo = respData
                        if (this.isSubFlow) { // 获取子流程输入参数 (subflow_detail_var 标识当前为子流程节点详情)
                            this.subFlowConstants = { subflow_detail_var: true, ...inputs }
                            this.inputsInfo = Object.values(this.pipelineData.constants).reduce((acc, cur) => {
                                if (cur.show_type === 'show') {
                                    acc[cur.key] = cur.value
                                }
                                return acc
                            }, {})
                        } else {
                            this.subFlowConstants = {}
                            this.inputsInfo = inputs
                        }
                        if (respData.histories) {
                            this.historyInfo = respData.histories.map(item => {
                                this.$set(item, 'historyLogTab', 'build_in_plugin')
                                this.$set(item, 'scrollId', '')
                                this.$set(item, 'observer', null)
                                this.$set(item, 'pageInfo', null)
                                return item
                            })
                        }
                        this.renderData = {}
                        for (const key in this.inputsInfo) {
                            this.$set(this.renderData, key, this.inputsInfo[key])
                        }
                        if (this.executeInfo.state && !['READY', 'CREATED'].includes(this.executeInfo.state)) {
                            const query = Object.assign({}, this.nodeDetailConfig, {
                                history_id: respData.history_id,
                                version: respData.version
                            })
                            const nodeLogDom = this.$refs.nodeLog
                            nodeLogDom && nodeLogDom.getPerformLog(query)
                        }

                        // 兼容 JOB 执行作业输出参数
                        // 输出参数 preset 为 true 或者 preset 为 false 但在输出参数的全局变量中存在时，才展示
                        if (componentCode === 'job_execute_task' && this.inputsInfo.hasOwnProperty('job_global_var')) {
                            this.outputsInfo = outputs.filter(output => {
                                const outputIndex = this.inputsInfo['job_global_var'].findIndex(prop => prop.name === output.key)
                                if (!output.preset && outputIndex === -1) {
                                    return false
                                }
                                return true
                            })
                        } else {
                            let outputsInfo = []
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
                            } else if (this.isSubFlow) {
                                outputsInfo = outputs.map(item => {
                                    const { value, key } = item
                                    const constants = this.nodeActivity.pipeline.constants
                                    const name = constants[key] ? constants[key].name : key
                                    return { value, name }
                                })
                            } else { // 普通插件展示 preset 为 true 的输出参数
                                outputsInfo = outputs.filter(output => output.preset)
                            }
                            this.outputsInfo = outputsInfo
                        }
                        this.outputsInfo.forEach(out => {
                            this.$set(this.outputRenderData, out.key, out.value)
                        })
                        if (this.theExecuteTime === undefined) {
                            this.loop = respData.loop
                            this.theExecuteTime = respData.loop
                        }
                    }

                    this.executeInfo.plugin_version = this.isThirdPartyNode ? inputs.plugin_version : version
                    this.executeInfo.name = this.location.name || NODE_DICT[this.location.type]
                    if (this.isThirdPartyNode) {
                        const resp = await this.loadPluginServiceAppDetail({ plugin_code: this.thirdPartyNodeCode })
                        this.executeInfo.plugin_name = resp.data.name
                    } else if (atomFilter.isConfigExists(componentCode, version, this.atomFormInfo)) {
                        const pluginInfo = this.atomFormInfo[componentCode][version]
                        this.executeInfo.plugin_name = `${pluginInfo.group_name}-${pluginInfo.name}`
                    }
                    if (this.historyInfo) {
                        this.historyInfo.forEach(item => {
                            item.last_time = tools.timeTransform(item.elapsed_time)
                        })
                    }
                    if (this.executeInfo.ex_data && this.executeInfo.ex_data.show_ip_log) {
                        this.failInfo = this.transformFailInfo(this.executeInfo.ex_data.exception_msg)
                    } else {
                        this.failInfo = this.transformFailInfo(this.executeInfo.ex_data)
                    }
                    // 获取执行失败节点是否允许跳过，重试状态
                    if (this.executeInfo.state === 'FAILED') {
                        const activity = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                        this.isShowSkipBtn = this.location.type === 'tasknode' && activity.skippable
                        this.isShowRetryBtn = this.location.type === 'tasknode' ? activity.retryable : this.isSubFlow
                    } else {
                        this.isShowSkipBtn = false
                        this.isShowRetryBtn = false
                    }
                    // 获取第三方插件节点日志
                    const traceId = outputs.length && outputs[0].value
                    if (this.isThirdPartyNode && traceId) {
                        const nodeLogDom = this.$refs.nodeLog
                        nodeLogDom && nodeLogDom.handleTabChange(traceId)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
                }
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

                    if (this.adminView) {
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
                            theme: 'error'
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
            onSelectExecuteTime (val) {
                this.theExecuteTime = val
                this.randomKey = new Date().getTime()
                this.loadNodeInfo()
            },
            onSelectNode (nodeHeirarchy, selectNodeId, nodeType) {
                this.editScrollDom = null
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
    display: flex;
    height: 100%;
    .nodeTree{
        border-right: 1px solid #DCDEE5;
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
    .excute-time {
        padding: 20px 20px 0;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        &>span {
            font-size: 14px;
            font-weight: bold;
        }
        .bk-select {
            margin: 0 6px;
            width: 100px;
        }
    }
    .execute-head {
        display: flex;
        align-items: center;
        font-size: 14px;
        padding: 20px 20px 7px;
        border-bottom: 1px solid #cacedb;
    }
    .scroll-area {
        flex: 1;
        overflow-y: auto;
        padding: 0 20px;
        @include scrollbar;
    }
    .panel-title {
        margin: 0;
        color: #313238;
        font-size: 14px;
        font-weight: 600;
    }
    .status-text-messages {
        margin-left: 0px;
        font-size: 12px;
        font-weight: 400;
    }
    .node-name {
        font-weight: 600;
        word-break: break-all;
    }
    .node-state {
        display: inline-block;
        white-space: nowrap;
        :first-child {
            margin: 0 6px;
            vertical-align: middle;
        }
    }
    .info-section {
        font-size: 12px;
        margin: 30px 0;
        word-wrap: break-word;
        word-break: break-all;
        /deep/ a {
            color: #4b9aff;
        }
    }
    /deep/.common-section-title {
        color: #313238;
        font-size: 14px;
        margin-bottom: 20px;
    }
    /deep/.input-parameter,
    /deep/.output-parameter {
        height: 20px;
        line-height: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 22px;
        .input-title,
        .output-title {
            color: #313238;
        }
        .origin-value {
            font-size: 12px;
            color: #87878e;
            .bk-switcher {
                margin-right: 5px;
            }
        }
    }
    /deep/.operation-table {
        font-size: 12px;
        table-layout: fixed;
        .output-name {
            width: 35%;
        }
        th {
            width: 260px;
            font-weight: 400;
            color: #313238;
        }
        td {
            color: #313238;
        }
    }
    .ex-data-wrap {
        /deep/ pre {
            white-space: pre-wrap;
        }
    }
    .common-icon-dark-circle-ellipsis {
        font-size: 12px;
        color: #3a84ff;
    }
    .common-icon-dark-circle-pause {
        font-size: 12px;
        color: #f8B53f;
    }
    .icon-check-circle-shape {
        font-size: 12px;
        color: #30d878;
    }
    .common-icon-dark-circle-close {
        font-size: 12px;
        color: #ff5757;
    }
    .common-icon-dark-circle-shape {
        color: #979BA5;
        font-size: 12px;
    }
    /deep/ .bk-table .bk-table-expanded-cell {
        padding: 20px;
    }
    /deep/ .primary-value.code-editor {
        height: 300px;
    }
    .action-wrapper {
        padding-left: 20px;
        height: 60px;
        line-height: 60px;
        border-top: 1px solid $commonBorderColor;
        .bk-button {
            margin-right: 5px;
        }
    }
}
</style>
