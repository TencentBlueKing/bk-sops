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
    <div
        :class="['execute-info', {
            'loading': loading,
            'admin-view': adminView
        }]"
        v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="excute-time" v-if="!adminView">
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
            <span>{{$t('次执行')}}</span>
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
        <section class="info-section">
            <h4 class="common-section-title">{{ $t('执行信息') }}</h4>
            <table class="operation-table">
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
        </section>
        <section class="info-section" v-if="!adminView">
            <h4 class="common-section-title">{{ $t('输入参数') }}</h4>
            <div>
                <RenderForm
                    v-if="!isEmptyParams && !loading"
                    :scheme="renderConfig"
                    :form-option="renderOption"
                    v-model="renderData">
                </RenderForm>
                <NoData v-else></NoData>
            </div>
        </section>
        <section class="info-section" v-else>
            <h4 class="common-section-title">{{ $t('输入参数') }}</h4>
            <div class="code-block-wrap">
                <VueJsonPretty :data="inputsInfo"></VueJsonPretty>
            </div>
        </section>
        <section class="info-section" v-if="!adminView">
            <h4 class="common-section-title">{{ $t('输出参数') }}</h4>
            <table class="operation-table outputs-table">
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
        </section>
        <section class="info-section" v-else>
            <h4 class="common-section-title">{{ $t('输出参数') }}</h4>
            <div class="code-block-wrap">
                <VueJsonPretty :data="outputsInfo"></VueJsonPretty>
            </div>
        </section>
        <section class="info-section ex-data-wrap" v-if="executeInfo.ex_data">
            <h4 class="common-section-title">{{ $t('异常信息') }}</h4>
            <div v-html="failInfo"></div>
            <IpLogContent
                v-if="executeInfo.ex_data.show_ip_log"
                :project-id="renderData.biz_cc_id"
                :node-info="executeInfo">
            </IpLogContent>
        </section>
        <section class="info-section" v-if="adminView">
            <h4 class="common-section-title">{{ $t('节点日志') }}</h4>
            <div class="code-block-wrap code-editor">
                <code-editor
                    :value="logInfo"
                    :options="{ readOnly: readOnly, language: 'javascript' }">
                </code-editor>
            </div>
        </section>
        <section class="info-section" v-if="historyInfo.length">
            <h4 class="common-section-title">{{ $t('执行记录') }}</h4>
            <bk-table
                class="retry-table"
                :data="historyInfo"
                @expand-change="onHistoyExpand">
                <bk-table-column type="expand" :width="60">
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
                            <div class="common-form-content ex-data-wrap">
                                <div v-html="props.row.ex_data"></div>
                            </div>
                        </div>
                        <div class="common-form-item" v-if="adminView">
                            <label>{{ $t('日志') }}</label>
                            <div class="common-form-content">
                                <div v-bkloading="{ isLoading: historyLogLoading[props.row.history_id], opacity: 1 }">
                                    <div class="code-block-wrap">
                                        <VueJsonPretty :data="historyLog[props.row.history_id]"></VueJsonPretty>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('序号')" :width="70">
                    <template slot-scope="props">
                        {{props.$index + 1}}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('执行次数')" :width="100" prop="loop"></bk-table-column>
                <bk-table-column
                    v-for="col in historyCols"
                    :key="col.id"
                    :label="col.title"
                    :prop="col.id">
                </bk-table-column>
            </bk-table>
        </section>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import VueJsonPretty from 'vue-json-pretty'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { URL_REG, TASK_STATE_DICT } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import IpLogContent from '@/components/common/Individualization/IpLogContent.vue'
    import CodeEditor from '@/components/common/CodeEditor.vue'
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
            id: 'error_ignorable'
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
            id: 'error_ignorable'
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
            CodeEditor
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            nodeDetailConfig: {
                type: Object,
                required: true
            }
        },
        data () {
            return {
                readOnly: true,
                loading: true,
                executeInfo: {},
                inputsInfo: {},
                outputsInfo: [],
                logInfo: '',
                historyInfo: [],
                historyLog: {},
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
                renderData: {},
                loop: 1,
                theExecuteTime: undefined
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config,
                'atomFormInfo': state => state.atomForm.form
            }),
            isEmptyParams () {
                return this.renderConfig && this.renderConfig.length === 0
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
                }
                return state
            },
            nodeState () {
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
            }
        },
        watch: {
            'nodeDetailConfig.node_id' (val) {
                if (val !== undefined) {
                    this.theExecuteTime = 1
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
                'loadAtomConfig'
            ]),
            ...mapActions('admin/', [
                'taskflowNodeDetail',
                'taskflowHistroyLog'
            ]),
            async loadNodeInfo () {
                this.loading = true

                try {
                    const respData = await this.getTaskNodeDetail()
                    const { execution_info, outputs, inputs, log, history } = respData
                    
                    const version = this.nodeDetailConfig.version
                    const componentCode = this.nodeDetailConfig.component_code
                    // 任务节点需要加载标准插件
                    if (componentCode) {
                        this.renderConfig = await this.getNodeConfig(componentCode, version)
                    }

                    if (this.adminView) {
                        this.executeInfo = execution_info
                        this.outputsInfo = outputs
                        this.inputsInfo = inputs
                        this.logInfo = log
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
                        this.historyInfo = respData.histories
                        
                        for (const key in this.inputsInfo) {
                            this.$set(this.renderData, key, this.inputsInfo[key])
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
                            // 普通插件展示 preset 为 true 的输出参数
                            this.outputsInfo = outputs.filter(output => output.preset)
                        }
                        
                        if (this.theExecuteTime === undefined) {
                            this.loop = respData.loop
                            this.theExecuteTime = respData.loop
                        }
                    }
                    this.executeInfo.plugin_version = version
                    if (atomFilter.isConfigExists(componentCode, version, this.atomFormInfo)) {
                        const pluginInfo = this.atomFormInfo[componentCode][version]
                        this.executeInfo.plugin_name = `${pluginInfo.group_name}-${pluginInfo.name}`
                    }
                    this.historyInfo.forEach(item => {
                        item.last_time = this.getLastTime(item.elapsed_time)
                    })

                    if (this.executeInfo.ex_data && this.executeInfo.ex_data.show_ip_log) {
                        this.failInfo = this.transformFailInfo(this.executeInfo.ex_data.exception_msg)
                    } else {
                        this.failInfo = this.transformFailInfo(this.executeInfo.ex_data)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            async getTaskNodeDetail () {
                try {
                    let query = Object.assign({}, this.nodeDetailConfig, { loop: this.theExecuteTime })
                    let getData = this.getNodeActDetail

                    // 分支网关请求参数不传 component_code
                    if (!this.nodeDetailConfig.component_code) {
                        delete query.component_code
                    }
                    
                    if (this.adminView) {
                        const { instance_id: task_id, node_id, subprocess_stack } = this.nodeDetailConfig
                        query = { task_id, node_id, subprocess_stack }
                        getData = this.taskflowNodeDetail
                    }

                    const res = await getData(query)
                    if (res.result) {
                        return res.data
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            async getNodeConfig (type, version) {
                if (atomFilter.isConfigExists(type, version, this.atomFormConfig)) {
                    return this.atomFormConfig[type][version]
                } else {
                    try {
                        await this.loadAtomConfig({ atom: type, version })
                        return this.atomFormConfig[type][version]
                    } catch (e) {
                        this.$bkMessage({
                            message: e,
                            theme: 'error'
                        })
                    }
                }
            },
            async getHistoryLog (id) {
                try {
                    this.$set(this.historyLogLoading, id, true)
                    const data = {
                        node_id: this.nodeDetailConfig.node_id,
                        history_id: id
                    }
                    const resp = await this.taskflowHistroyLog(data)
                    if (resp.result) {
                        this.$set(this.historyLog, id, resp.data.log)
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.historyLogLoading[id] = false
                }
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
            onHistoyExpand (row, expended) {
                const id = Number(row.history_id)
                if (this.adminView && expended && !this.historyLog.hasOwnProperty(id)) {
                    this.getHistoryLog(id)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.execute-info {
    padding: 30px 20px;
    height: 100%;
    color: #313238;
    overflow-y: auto;
    @include scrollbar;
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
    /deep/ .code-editor {
        height: 300px;
    }
    .excute-time {
        margin-bottom: 40px;
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
        padding-bottom: 7px;
        border-bottom: 1px solid #cacedb;
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
    /deep/ .bk-table .bk-table-expanded-cell {
        padding: 20px;
    }
}
</style>
