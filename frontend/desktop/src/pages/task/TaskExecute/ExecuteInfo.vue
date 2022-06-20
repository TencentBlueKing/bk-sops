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
            <div class="scroll-area">
                <section class="info-section" data-test-id="taskExcute_form_excuteInfo">
                    <h4 class="common-section-title">{{ $t('执行信息') }}</h4>
                    <table class="operation-table" v-if="executeCols && isReadyStatus">
                        <tr v-for="col in executeCols" :key="col.id">
                            <th>{{ col.title }}</th>
                            <td>
                                <template v-if="typeof executeInfo[col.id] === 'boolean'">
                                    {{executeInfo[col.id] ? $t('是') : $t('否')}}
                                </template>
                                <template v-else-if="col.id === 'elapsed_time'">
                                    {{getLastTime(executeInfo.elapsed_time)}}
                                </template>
                                <template v-else-if="col.id === 'callback_data'">
                                    <div class="code-block-wrap">
                                        <VueJsonPretty :data="executeInfo.callback_data"></VueJsonPretty>
                                    </div>
                                </template>
                                <template v-else>
                                    {{ executeInfo[col.id] }}
                                </template>
                            </td>
                        </tr>
                    </table>
                    <NoData v-else></NoData>
                </section>
                <section class="info-section" data-test-id="taskExcute_form_operatFlow" v-if="executeInfo.id && location.type !== 'subflow'">
                    <h4 class="common-section-title">{{ $t('操作流水') }}</h4>
                    <OperationFlow :locations="pipelineData.location" :node-id="executeInfo.id"></OperationFlow>
                </section>
                <section class="info-section" data-test-id="taskExcute_form_inputParams" v-if="nodeDetailConfig.component_code">
                    <div class="common-section-title input-parameter">
                        <div class="input-title">{{ $t('输入参数') }}</div>
                        <div class="origin-value" v-if="!adminView">
                            <bk-switcher @change="inputSwitcher" v-model="isShowInputOrigin"></bk-switcher>
                            {{ $t('原始值') }}
                        </div>
                    </div>
                    <div v-if="!adminView">
                        <div v-if="!isShowInputOrigin">
                            <RenderForm
                                v-if="!isEmptyParams && !loading"
                                :scheme="renderConfig"
                                :form-option="renderOption"
                                v-model="renderData">
                            </RenderForm>
                            <NoData v-else></NoData>
                        </div>
                        <full-code-editor v-else :value="inputsInfo"></full-code-editor>
                    </div>
                    <div class="code-block-wrap" v-else>
                        <VueJsonPretty :data="inputsInfo"></VueJsonPretty>
                    </div>
                </section>
                <section class="info-section" data-test-id="taskExcute_form_outputParams" v-if="['tasknode', 'subflow'].includes(location.type)">
                    <div class="common-section-title output-parameter">
                        <div class="output-title">{{ $t('输出参数') }}</div>
                        <div class="origin-value" v-if="!adminView">
                            <bk-switcher @change="outputSwitcher" v-model="isShowOutputOrigin"></bk-switcher>
                            {{ $t('原始值') }}
                        </div>
                    </div>
                    <div v-if="!adminView">
                        <table class="operation-table outputs-table" v-if="!isShowOutputOrigin">
                            <thead>
                                <tr>
                                    <th class="output-name">{{ $t('参数名') }}</th>
                                    <th class="output-value">{{ $t('参数值') }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="output in outputsInfo" :key="output.name">
                                    <td class="output-name">{{getOutputName(output)}}</td>
                                    <td v-if="isUrl(output.value)" class="output-value" v-html="getOutputValue(output)"></td>
                                    <td v-else class="output-value">{{ getOutputValue(output) }}</td>
                                </tr>
                                <tr v-if="Object.keys(outputsInfo).length === 0">
                                    <td colspan="2"><no-data></no-data></td>
                                </tr>
                            </tbody>
                        </table>
                        <full-code-editor v-else :value="outputsInfo"></full-code-editor>
                    </div>
                    <div class="code-block-wrap" v-else>
                        <VueJsonPretty :data="outputsInfo" v-if="outputsInfo"></VueJsonPretty>
                        <NoData v-else></NoData>
                    </div>
                </section>
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
                <section class="info-section" data-test-id="taskExcute_form_exceptionInfo" v-if="executeInfo.ex_data">
                    <h4 class="common-section-title">{{ $t('异常信息') }}</h4>
                    <div v-html="failInfo"></div>
                    <IpLogContent
                        v-if="executeInfo.ex_data.show_ip_log"
                        :project-id="renderData.biz_cc_id"
                        :node-info="executeInfo">
                    </IpLogContent>
                </section>
                <section class="info-section log-info" data-test-id="taskExcute_form_nodeLog">
                    <h4 class="common-section-title">{{ $t('节点日志') }}</h4>
                    <!-- 内置插件/第三方插件tab -->
                    <bk-tab v-if="isThirdPartyNode" :active.sync="curPluginTab" type="unborder-card">
                        <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('节点日志') }"></bk-tab-panel>
                        <bk-tab-panel
                            v-bind="{ name: 'third_party_plugin', label: $t('第三方节点日志') }">
                        </bk-tab-panel>
                    </bk-tab>
                    <div class="perform-log" v-bkloading="{ isLoading: isLogLoading, opacity: 1, zIndex: 100 }">
                        <full-code-editor
                            v-if="curPluginTab === 'build_in_plugin' ? logInfo : executeInfo.thirdPartyNodeLog"
                            class="scroll-editor"
                            :key="curPluginTab"
                            :value="curPluginTab === 'build_in_plugin' ? logInfo : executeInfo.thirdPartyNodeLog">
                        </full-code-editor>
                        <NoData v-else></NoData>
                    </div>
                </section>
                <section class="info-section" data-test-id="taskExcute_form_excuteLog" v-if="historyInfo && historyInfo.length">
                    <h4 class="common-section-title">{{ $t('执行记录') }}</h4>
                    <bk-table
                        class="retry-table"
                        :data="historyInfo"
                        @expand-change="onHistoyExpand">
                        <bk-table-column type="expand" :width="30">
                            <template slot-scope="props">
                                <div class="common-form-item">
                                    <label>{{ $t('输入参数') }}</label>
                                    <div class="common-form-content">
                                        <div class="code-block-wrap">
                                            <VueJsonPretty :data="props.row.inputs"></VueJsonPretty>
                                        </div>
                                    </div>
                                </div>
                                <div class="common-form-item">
                                    <label>{{ $t('输出参数') }}</label>
                                    <div class="common-form-content">
                                        <div class="code-block-wrap">
                                            <VueJsonPretty :data="props.row.outputs"></VueJsonPretty>
                                        </div>
                                    </div>
                                </div>
                                <div class="common-form-item" v-if="props.row.ex_data">
                                    <label>{{ $t('异常信息') }}</label>
                                    <div class="common-form-content">
                                        <div v-html="props.row.ex_data"></div>
                                    </div>
                                </div>
                                <div class="common-form-item executeLog">
                                    <label>{{ $t('日志') }}</label>
                                    <!-- 内置插件/第三方插件tab -->
                                    <bk-tab
                                        v-if="isThirdPartyNode"
                                        :active.sync="props.row.historyLogTab"
                                        type="unborder-card">
                                        <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('节点日志') }"></bk-tab-panel>
                                        <bk-tab-panel
                                            v-bind="{ name: 'third_party_plugin', label: $t('第三方节点日志') }">
                                        </bk-tab-panel>
                                    </bk-tab>
                                    <div class="perform-log" v-bkloading="{ isLoading: historyLogLoading[props.row.history_id], opacity: 1, zIndex: 100 }">
                                        <div v-show="getHistoryLogData(props.row)">
                                            <VueJsonPretty
                                                v-show="adminView"
                                                :data="getHistoryLogData(props.row)">
                                            </VueJsonPretty>
                                            <full-code-editor
                                                v-show="!adminView"
                                                :class="[
                                                    `history-editor-${props.row.history_id}`
                                                ]"
                                                :value="getHistoryLogData(props.row)">
                                            </full-code-editor>
                                        </div>
                                        <NoData v-show="!getHistoryLogData(props.row)"></NoData>
                                    </div>

                                </div>
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('序号')" :width="60">
                            <template slot-scope="props">
                                {{props.$index + 1}}
                            </template>
                        </bk-table-column>
                        <bk-table-column :label="$t('执行次数')" :width="100" prop="loop"></bk-table-column>
                        <bk-table-column
                            v-for="col in historyCols"
                            show-overflow-tooltip
                            :key="col.id"
                            :label="col.title"
                            :prop="col.id">
                        </bk-table-column>
                    </bk-table>
                </section>
            </div>
            <div v-if="executeInfo.state === 'RUNNING'" class="action-wrapper">
                <bk-button
                    v-if="nodeDetailConfig.component_code === 'pause_node'"
                    theme="primary"
                    data-test-id="taskExcute_form_resumeBtn"
                    @click="onResumeClick">
                    {{ $t('继续执行') }}
                </bk-button>
                <bk-button
                    v-if="nodeDetailConfig.component_code === 'sleep_timer'"
                    theme="primary"
                    data-test-id="taskExcute_form_modifyTimeBtn"
                    @click="onModifyTimeClick">
                    {{ $t('修改时间') }}
                </bk-button>
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
    import VueJsonPretty from 'vue-json-pretty'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { URL_REG, TASK_STATE_DICT, NODE_DICT } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import IpLogContent from '@/components/common/Individualization/IpLogContent.vue'
    import NodeTree from './NodeTree'
    import FullCodeEditor from './FullCodeEditor.vue'
    import OperationFlow from './OperationFlow.vue'

    const EXECUTE_INFO_COL = [
        {
            title: i18n.t('开始时间'),
            id: 'start_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'finish_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        },
        {
            title: i18n.t('失败后跳过'),
            id: 'skip'
        },
        {
            title: i18n.t('失败后自动忽略'),
            id: 'error_ignored'
        },
        {
            title: i18n.t('重试次数'),
            id: 'retry'
        },
        {
            title: i18n.t('插件版本'),
            id: 'plugin_version'
        },
        {
            title: i18n.t('插件名称'),
            id: 'plugin_name'
        },
        {
            title: i18n.t('节点ID'),
            id: 'id'
        }
    ]

    const ADMIN_EXECUTE_INFO_COL = [
        {
            title: i18n.t('开始时间'),
            id: 'start_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'archive_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        },
        {
            title: i18n.t('失败后跳过'),
            id: 'skip'
        },
        {
            title: i18n.t('失败后自动忽略'),
            id: 'error_ignored'
        },
        {
            title: i18n.t('重试次数'),
            id: 'retry_times'
        },
        {
            title: i18n.t('ID'),
            id: 'id'
        },
        {
            title: i18n.t('状态'),
            id: 'state'
        },
        {
            title: i18n.t('循环次数'),
            id: 'loop'
        },
        {
            title: i18n.t('创建时间'),
            id: 'create_time'
        },
        {
            title: i18n.t('调度ID'),
            id: 'schedule_id'
        },
        {
            title: i18n.t('正在被调度'),
            id: 'is_scheduling'
        },
        {
            title: i18n.t('调度次数'),
            id: 'schedule_times'
        },
        {
            title: i18n.t('等待回调'),
            id: 'wait_callback'
        },
        {
            title: i18n.t('完成调度'),
            id: 'is_finished'
        },
        {
            title: i18n.t('调度节点版本'),
            id: 'schedule_version'
        },
        {
            title: i18n.t('执行版本'),
            id: 'version'
        },
        {
            title: i18n.t('回调数据'),
            id: 'callback_data'
        },
        {
            title: i18n.t('插件版本'),
            id: 'plugin_version'
        },
        {
            title: i18n.t('插件名称'),
            id: 'plugin_name'
        },
        {
            title: i18n.t('节点ID'),
            id: 'id'
        }
    ]

    const HISTORY_COLS = [
        {
            title: i18n.t('开始时间'),
            id: 'start_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'finish_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'last_time'
        }
    ]

    const ADMIN_HISTORY_COLS = [
        {
            title: i18n.t('开始时间'),
            id: 'started_time'
        },
        {
            title: i18n.t('结束时间'),
            id: 'finished_time'
        },
        {
            title: i18n.t('耗时'),
            id: 'elapsed_time'
        }
    ]

    export default {
        name: 'ExecuteInfo',
        components: {
            VueJsonPretty,
            RenderForm,
            NoData,
            IpLogContent,
            NodeTree,
            FullCodeEditor,
            OperationFlow
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
                curPluginTab: 'build_in_plugin',
                isLogLoading: false,
                isShowInputOrigin: false,
                isShowOutputOrigin: false,
                readOnly: true,
                loading: true,
                isRenderOutputForm: false,
                executeInfo: {},
                inputsInfo: {},
                pluginOutputs: [],
                outputsInfo: [],
                logInfo: '',
                historyInfo: [],
                historyLog: {},
                thirdHistoryLog: {},
                historyLogLoading: {},
                failInfo: '',
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false,
                    formEdit: false,
                    formMode: false
                },
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
                loop: 1,
                theExecuteTime: undefined,
                isReadyStatus: true,
                isShowSkipBtn: false,
                isShowRetryBtn: false,
                scrollId: '',
                observer: null,
                editScrollDom: null,
                nodeLogPageInfo: null
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
            isEmptyParams () {
                return this.renderConfig && this.renderConfig.length === 0
            },
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
            executeCols () {
                return this.adminView ? ADMIN_EXECUTE_INFO_COL : EXECUTE_INFO_COL
            },
            historyCols () {
                return this.adminView ? ADMIN_HISTORY_COLS : HISTORY_COLS
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
                const nodeInfo = this.pipelineData.activities[this.nodeDetailConfig.node_id]
                let codeInfo = nodeInfo.component.data
                codeInfo = codeInfo && codeInfo.plugin_code
                codeInfo = codeInfo.value
                return codeInfo
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
                    this.historyLog = {}
                    this.thirdHistoryLog = {}
                    this.historyLogLoading = {}
                    this.failInfo = ''
                    this.loadNodeInfo()
                }
            },
            curPluginTab (val) {
                this.editScrollDom = null
                if (val === 'third_party_plugin' || this.nodeLogPageInfo) {
                    this.watchEditorScroll()
                }
            }
        },
        mounted () {
            this.loadNodeInfo()
        },
        beforeDestroy () {
            if (this.observer) {
                this.observer.disconnect()
                this.observer.takeRecords()
                this.observer = null
            }
            if (this.historyInfo.length) {
                this.historyInfo.forEach(item => {
                    if (item.observe) {
                        item.observer.disconnect()
                        item.observer.takeRecords()
                        item.observer = null
                    }
                })
            }
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActInfo',
                'getNodeActDetail',
                'getEngineVerNodeLog',
                'getNodeExecutionRecordLog'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail',
                'loadPluginServiceLog',
                'loadPluginServiceAppDetail'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeDetail',
                'taskflowHistroyLog'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    this.isShowInputOrigin = false
                    this.isShowOutputOrigin = false
                    this.curPluginTab = 'build_in_plugin'
                    this.scrollId = ''
                    const respData = await this.getTaskNodeDetail()
                    if (!respData) {
                        this.isReadyStatus = false
                        this.executeInfo = {}
                        this.outputsInfo = []
                        this.inputsInfo = {}
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
                        this.inputsInfo = inputs
                        if (respData.histories) {
                            this.historyInfo = respData.histories.map(item => {
                                this.$set(item, 'historyLogTab', 'build_in_plugin')
                                this.$set(item, 'scrollId', '')
                                this.$set(item, 'observer', null)
                                this.$set(item, 'pageInfo', null)
                                return item
                            })
                        }
                        for (const key in this.inputsInfo) {
                            this.$set(this.renderData, key, this.inputsInfo[key])
                        }
                        if (this.executeInfo.state && !['READY', 'CREATED'].includes(this.executeInfo.state)) {
                            const query = Object.assign({}, this.nodeDetailConfig, {
                                history_id: respData.history_id,
                                version: respData.version
                            })
                            this.getPerformLog(query)
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
                            item.last_time = this.getLastTime(item.elapsed_time)
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
                        this.isShowRetryBtn = this.location.type === 'tasknode' ? activity.retryable : this.location.type === 'subflow'
                    } else {
                        this.isShowSkipBtn = false
                        this.isShowRetryBtn = false
                    }
                    // 获取第三方插件节点日志
                    const traceId = outputs.length && outputs[0].value
                    if (this.isThirdPartyNode && traceId) {
                        this.handleTabChange(traceId)
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
            // 非admin 用户执行记录
            async getPerformLog (query) {
                try {
                    this.isLogLoading = true
                    let performLog = {}
                    // 不同引擎版本的任务调用不同的接口
                    if (this.engineVer === 1) {
                        performLog = await this.getNodeExecutionRecordLog(query)
                    } else if (this.engineVer === 2) {
                        performLog = await this.getEngineVerNodeLog(query)
                    }
                    this.logInfo = this.logInfo + (this.logInfo ? '\n' : '') + performLog.data
                    this.nodeLogPageInfo = performLog.page
                    if (this.nodeLogPageInfo && !this.editScrollDom) {
                        this.watchEditorScroll()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.isLogLoading = false
                }
            },
            watchEditorScroll () {
                // 第三方日志滚动加载
                this.$nextTick(() => {
                    // 滚动dom
                    const editScrollDom = document.querySelector('.scroll-editor .code-editor .vertical .slider')
                    if (!editScrollDom) return
                    // 编辑器dom
                    const editDom = document.querySelector('.scroll-editor .monaco-editor')
                    const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver

                    // 监听滚动dom
                    this.observer = new MutationObserver(mutation => {
                        const { height } = editScrollDom.getBoundingClientRect()
                        const { height: editHeight } = editDom && editDom.getBoundingClientRect()
                        const top = editScrollDom.offsetTop
                        const offsetBottom = editHeight > 300 ? 180 : 80
                        if (this.curPluginTab === 'third_party_plugin') {
                            if (editHeight - height - top < offsetBottom && !this.isLogLoading && this.scrollId) {
                                const { outputs } = this.executeInfo
                                const traceId = outputs.length && outputs[0].value
                                this.handleTabChange(traceId)
                            }
                        } else if (this.nodeLogPageInfo) {
                            const { page, total, page_size } = this.nodeLogPageInfo
                            if (editHeight - height - top < offsetBottom && !this.isLogLoading && page < Math.ceil(total / page_size)) {
                                const { history_id, version } = this.executeInfo
                                const query = Object.assign({}, this.nodeDetailConfig, {
                                    page: page + 1,
                                    history_id,
                                    version
                                })
                                this.getPerformLog(query)
                            }
                        }
                    })
                    this.observer.observe(editScrollDom, {
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: true
                    })
                    this.editScrollDom = editScrollDom
                })
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
                            const { outputs: respsOutputs, forms } = resp.data
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
            async handleTabChange (traceId) {
                try {
                    this.isLogLoading = true
                    const resp = await this.loadPluginServiceLog({
                        plugin_code: this.thirdPartyNodeCode,
                        trace_id: traceId,
                        scroll_id: this.scrollId || undefined
                    })
                    if (!resp.result) {
                        this.scrollId = ''
                        return
                    }
                    const { logs, scroll_id } = resp.data
                    const thirdPartyLogs = this.executeInfo.thirdPartyNodeLog || ''
                    this.executeInfo.thirdPartyNodeLog = thirdPartyLogs + logs
                    this.scrollId = logs && scroll_id ? scroll_id : ''
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isLogLoading = false
                }
            },
            async getHistoryLog (id, row) {
                try {
                    this.$set(this.historyLogLoading, id, true)
                    const data = {
                        page: row.pageInfo ? (row.pageInfo.page + 1) : 1,
                        node_id: this.nodeDetailConfig.node_id,
                        history_id: id,
                        instance_id: this.nodeDetailConfig.instance_id,
                        version: row.version
                    }
                    let resp = null
                    if (this.adminView) {
                        resp = await this.taskflowHistroyLog(data)
                    } else if (this.engineVer === 1) {
                        resp = await this.getNodeExecutionRecordLog(data)
                    } else if (this.engineVer === 2) {
                        resp = await this.getEngineVerNodeLog(data)
                    }
                    if (resp.result) {
                        const respData = this.adminView ? resp.data.log : resp.data
                        row.pageInfo = this.adminView ? resp.data.page : resp.page
                        const curLog = this.historyLog[id] || ''
                        this.$set(this.historyLog, id, curLog + (curLog ? '\n' : '') + respData)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.historyLogLoading[id] = false
                }
            },
            // 设置第三方节点历史日志
            setHistoryLogWatch (row) {
                try {
                    // 滚动dom
                    const editorDom = document.querySelector(`.history-editor-${row.history_id}`)
                    const scrollDom = editorDom && editorDom.querySelector('.code-editor .vertical .slider')
                    if (!scrollDom) return
                    // 编辑器dom
                    const editDom = editorDom && editorDom.querySelector('.monaco-editor')
                    const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver
                    // 监听滚动dom
                    row.observer = new MutationObserver(async mutation => {
                        const { height } = scrollDom.getBoundingClientRect()
                        const { height: editHeight } = editDom && editDom.getBoundingClientRect()
                        const top = scrollDom.offsetTop
                        const offsetBottom = editHeight > 300 ? 180 : 100
                        if (row.historyLogTab === 'third_party_plugin') {
                            if (editHeight - height - top < offsetBottom && !this.historyLogLoading[row.history_id] && row.scrollId) {
                                this.historyLogLoading[row.history_id] = true
                                // 设置第三方节点历史日志
                                await this.setThirdHistoryLog(row)
                            }
                        } else if (row.nodeInfo) {
                            const { page, total, page_size } = row.nodeInfo
                            if (editHeight - height - top < offsetBottom && !this.this.historyLogLoading[row.history_id] && page < Math.ceil(total / page_size)) {
                                const id = Number(row.history_id)
                                this.getHistoryLog(id, row)
                            }
                        }
                    })
                    row.observer.observe(scrollDom, {
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: true
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.historyLogLoading[row.history_id] = false
                }
            },
            // 设置第三方节点历史日志
            async setThirdHistoryLog (row) {
                try {
                    const id = Number(row.history_id)
                    const traceId = row.outputs.trace_id
                    const thirdLogsResp = await this.loadPluginServiceLog({
                        plugin_code: this.thirdPartyNodeCode,
                        trace_id: traceId,
                        scroll_id: row.scrollId || undefined
                    })
                    if (thirdLogsResp.result) {
                        const { logs, scroll_id } = thirdLogsResp.data
                        const thirdPartyLogs = this.thirdHistoryLog[id] || ''
                        this.$set(this.thirdHistoryLog, id, thirdPartyLogs + logs)
                        row.scrollId = logs && scroll_id ? scroll_id : ''
                    } else {
                        row.scrollId = ''
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.historyLogLoading[row.history_id] = false
                }
            },
            getHistoryLogData (row) {
                return row.historyLogTab === 'build_in_plugin' ? this.historyLog[row.history_id] : this.thirdHistoryLog[row.history_id]
            },
            isUrl (val) {
                return typeof val === 'string' && URL_REG.test(val)
            },
            getOutputValue (output) {
                if (output.value === 'undefined' || output.value === '') {
                    return '--'
                } else if (!output.preset && this.nodeDetailConfig.component_code === 'job_execute_task') {
                    return output.value
                } else {
                    if (this.isUrl(output.value)) {
                        return `<a class="info-link" target="_blank" href="${output.value}">${output.value}</a>`
                    }
                    return output.value
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
            getLastTime (time) {
                return tools.timeTransform(time)
            },
            getOutputName (output) {
                if (this.nodeDetailConfig.component_code === 'job_execute_task' && output.perset) {
                    return output.key
                }
                return output.name
            },
            onSelectExecuteTime (val) {
                this.theExecuteTime = val
                this.loadNodeInfo()
            },
            async onHistoyExpand (row, expended) {
                const id = Number(row.history_id)
                if (expended && !this.historyLog.hasOwnProperty(id)) {
                    // 获取普通节点历史日志
                    await this.getHistoryLog(id, row)
                    // 获取第三方插件的执行历史日志
                    const traceId = row.outputs.trace_id
                    if (traceId) {
                        // 设置第三方节点历史日志
                        await this.setThirdHistoryLog(row)
                    } else {
                        this.$set(this.thirdHistoryLog, id, i18n.t('输出参数中不包含trace_id，无法查看第三方节点日志'))
                    }
                }
                if (row && !row.observer) {
                    this.$nextTick(() => {
                        // 给历史日志设置监听事件
                        this.setHistoryLogWatch(row)
                    })
                }
            },
            onSelectNode (nodeHeirarchy, selectNodeId, nodeType) {
                this.editScrollDom = null
                this.$emit('onClickTreeNode', nodeHeirarchy, selectNodeId, nodeType)
            },
            inputSwitcher () {
                if (!this.isShowInputOrigin) {
                    this.inputsInfo = JSON.parse(this.inputsInfo)
                } else {
                    this.inputsInfo = JSON.stringify(this.inputsInfo, null, 4)
                }
            },
            outputSwitcher () {
                if (!this.isShowOutputOrigin) {
                    this.outputsInfo = JSON.parse(this.outputsInfo)
                } else {
                    this.outputsInfo = JSON.stringify(this.outputsInfo, null, 4)
                }
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
    .common-section-title {
        color: #313238;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .input-parameter,
    .output-parameter {
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
    .operation-table {
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
    .retry-table {
        font-size: 12px;
        .common-form-item {
            & > label {
                margin-top: 0;
                width: 60px;
                font-size: 12px;
            }
            .commont-form-content {
                margin-left: 100px;
                font-size: 12px;
            }
        }
        .executeLog {
            /deep/.bk-tab {
                position: relative;
                top: -16px;
                margin-left: 120px;
                .bk-tab-section {
                    padding: 0;
                }
            }
            .perform-log {
                margin-left: 120px;
                .no-data-wrapper {
                    margin: 20px 0;
                }
            }
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
