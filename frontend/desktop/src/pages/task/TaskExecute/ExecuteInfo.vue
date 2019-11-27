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
    <div :class="['execute-info', { 'loading': loading }]" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="excute-time">
            <span>{{i18n.theTime}}</span>
            <bk-select
                :clearable="false"
                v-model="theExecuteTime"
                @change="onSelectExecuteTime">
                <bk-option
                    v-for="index in loopTimes"
                    :key="index"
                    :id="index"
                    :name="index">
                </bk-option>
            </bk-select>
            <span>{{i18n.executeTime}}</span>
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
            <h4 class="common-section-title">{{ i18n.executeInfo }}</h4>
            <table class="operation-table">
                <tr v-for="col in executeCols" :key="col.id">
                    <th>{{ col.title }}</th>
                    <td>
                        <template v-if="typeof executeInfo[col.id] === 'boolean'">
                            {{executeInfo[col.id] ? i18n.yes : i18n.no}}
                        </template>
                        <template v-else-if="col.id === 'elapsed_time'">
                            {{getLastTime(executeInfo.elapsed_time)}}
                        </template>
                        <template v-else-if="col.id === 'callback_data'">
                            {{JSON.stringify(executeInfo.callback_data, null, 4)}}
                        </template>
                        <template v-else>
                            {{ executeInfo[col.id] }}
                        </template>
                    </td>
                </tr>
            </table>
        </section>
        <section class="info-section" v-show="isSingleAtom">
            <h4 class="common-section-title">{{ i18n.inputsParams }}</h4>
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
        <section class="info-section" v-show="isSingleAtom">
            <h4 class="common-section-title">{{ i18n.outputsParams }}</h4>
            <table class="operation-table outputs-table">
                <thead>
                    <tr>
                        <th class="output-name">{{ i18n.name }}</th>
                        <th class="output-value">{{ i18n.value }}</th>
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
        <section class="info-section" v-if="executeInfo.ex_data">
            <h4 class="common-section-title">{{ i18n.exception }}</h4>
            <div v-html="failInfo"></div>
            <IpLogContent
                v-if="executeInfo.ex_data.show_ip_log"
                :project-id="renderData.biz_cc_id"
                :node-info="executeInfo">
            </IpLogContent>
        </section>
        <section class="info-section" v-if="logInfo">
            <h4 class="common-section-title">{{ i18n.nodeLog }}</h4>
            <div>{{ logInfo }}</div>
        </section>
        <section class="info-section" v-if="historyInfo.length">
            <h4 class="common-section-title">{{ i18n.retries }}</h4>
            <bk-table
                class="retry-table"
                :data="historyInfo">
                <bk-table-column type="expand" :width="60">
                    <template slot-scope="props">
                        <div class="common-form-item">
                            <label>{{ i18n.inputsParams }}</label>
                            <div class="common-form-content">
                                <VueJsonPretty
                                    :data="props.row.inputs">
                                </VueJsonPretty>
                            </div>
                        </div>
                        <div class="common-form-item">
                            <label>{{ i18n.outputsParams }}</label>
                            <div class="common-form-content">
                                <VueJsonPretty
                                    :data="props.row.outputs">
                                </VueJsonPretty>
                            </div>
                        </div>
                        <div class="common-form-item">
                            <label>{{ i18n.exception }}</label>
                            <div class="common-form-content">
                                <div v-html="props.row.ex_data"></div>
                            </div>
                        </div>
                        <div class="common-form-item" v-if="hasAdminPerm">
                            <label>{{ i18n.log }}</label>
                            <div class="common-form-content">
                                <div v-bkloading="{ isLoading: historyLogLoading, opacity: 1 }">
                                    {{ historyLog[props.row.history_id] || '--' }}
                                </div>
                            </div>
                        </div>
                    </template>
                </bk-table-column>
                <bk-table-column :label="i18n.index" :width="'70'">
                    <template slot-scope="props">
                        {{props.$index + 1}}
                    </template>
                </bk-table-column>
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
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import VueJsonPretty from 'vue-json-pretty'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { URL_REG, TASK_STATE_DICT } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import IpLogContent from '@/components/common/Individualization/IpLogContent.vue'

    const EXECUTE_INFO_COL = [
        {
            title: gettext('开始时间'),
            id: 'start_time'
        },
        {
            title: gettext('结束时间'),
            id: 'finish_time'
        },
        {
            title: gettext('耗时'),
            id: 'elapsed_time'
        },
        {
            title: gettext('失败后跳过'),
            id: 'skip'
        },
        {
            title: gettext('失败后自动忽略'),
            id: 'error_ignorable'
        },
        {
            title: gettext('重试次数'),
            id: 'retry'
        },
        {
            title: gettext('执行版本'),
            id: 'version'
        }
    ]

    const ADMIN_EXECUTE_INFO_COL = [
        {
            title: gettext('开始时间'),
            id: 'start_time'
        },
        {
            title: gettext('结束时间'),
            id: 'archive_time'
        },
        {
            title: gettext('耗时'),
            id: 'elapsed_time'
        },
        {
            title: gettext('失败后跳过'),
            id: 'skip'
        },
        {
            title: gettext('失败后自动忽略'),
            id: 'error_ignorable'
        },
        {
            title: gettext('重试次数'),
            id: 'retry_times'
        },
        {
            title: gettext('ID'),
            id: 'id'
        },
        {
            title: gettext('状态'),
            id: 'state'
        },
        {
            title: gettext('循环次数'),
            id: 'loop'
        },
        {
            title: gettext('创建时间'),
            id: 'create_time'
        },
        {
            title: gettext('执行版本'),
            id: 'version'
        },
        {
            title: gettext('调度ID'),
            id: 'schedule_id'
        },
        {
            title: gettext('正在被调度'),
            id: 'is_scheduling'
        },
        {
            title: gettext('调度次数'),
            id: 'schedule_times'
        },
        {
            title: gettext('等待回调'),
            id: 'wait_callback'
        },
        {
            title: gettext('完成调度'),
            id: 'is_finished'
        },
        {
            title: gettext('调度节点版本'),
            id: 'schedule_version'
        },
        {
            title: gettext('回调数据'),
            id: 'callback_data'
        }
    ]

    const HISTORY_COLS = [
        {
            title: gettext('开始时间'),
            id: 'start_time'
        },
        {
            title: gettext('结束时间'),
            id: 'finish_time'
        },
        {
            title: gettext('耗时'),
            id: 'last_time'
        }
    ]

    const ADMIN_HISTORY_COLS = [
        {
            title: gettext('开始时间'),
            id: 'started_time'
        },
        {
            title: gettext('结束时间'),
            id: 'finished_time'
        },
        {
            title: gettext('耗时'),
            id: 'elapsed_time'
        }
    ]

    export default {
        name: 'ExecuteInfo',
        components: {
            VueJsonPretty,
            RenderForm,
            NoData,
            IpLogContent
        },
        props: {
            nodeDetailConfig: {
                type: Object,
                required: true
            }
        },
        data () {
            return {
                i18n: {
                    executeInfo: gettext('执行信息'),
                    lastTime: gettext('耗时'),
                    inputsParams: gettext('输入参数'),
                    outputsParams: gettext('输出参数'),
                    name: gettext('参数名'),
                    value: gettext('参数值'),
                    exception: gettext('异常信息'),
                    retries: gettext('执行记录'),
                    index: gettext('序号'),
                    yes: gettext('是'),
                    no: gettext('否'),
                    nodeLog: gettext('节点日志'),
                    log: gettext('日志'),
                    running: gettext('执行中'),
                    suspended: gettext('暂停'),
                    failed: gettext('失败'),
                    finished: gettext('完成'),
                    theTime: gettext('第'),
                    executeTime: gettext('次执行')
                },
                loading: true,
                executeInfo: {},
                inputsInfo: {},
                outputsInfo: [],
                logInfo: '',
                historyInfo: [],
                historyLog: [],
                historyLogLoading: false,
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
                'hasAdminPerm': state => state.hasAdminPerm
            }),
            isSingleAtom () {
                return !!this.nodeDetailConfig.component_code
            },
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
                const loop = this.executeInfo.hasOwnProperty('loop') ? this.executeInfo.loop : 1
                for (let i = 0; i < loop; i++) {
                    times.push(loop - i)
                }

                return times
            },
            executeCols () {
                return this.hasAdminPerm ? ADMIN_EXECUTE_INFO_COL : EXECUTE_INFO_COL
            },
            historyCols () {
                return this.hasAdminPerm ? ADMIN_HISTORY_COLS : HISTORY_COLS
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
            ...mapMutations('atomForm/', [
                'setAtomConfig'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    const respData = await this.getTaskNodeDetail()
                    
                    if (this.isSingleAtom) {
                        const version = this.nodeDetailConfig.version
                        this.renderConfig = await this.getNodeConfig(this.nodeDetailConfig.component_code, version)
                    }

                    if (this.hasAdminPerm) {
                        this.executeInfo = respData.execution_info

                        if (Object.prototype.toString.call(this.outputsInfo) === '[Object Object]') {
                            this.outputsInfo = Object.keys(respData.outputs).map(item => {
                                return {
                                    name: item,
                                    value: respData.outputs[item]
                                }
                            })
                        }

                        this.historyInfo = respData.history
                        this.getHistoryLog()
                    } else {
                        this.executeInfo = respData
                        this.outputsInfo = respData.outputs
                        this.historyInfo = respData.histories
                        this.outputsInfo = this.outputsInfo.filter(output => output.preset)
                    }
                    this.inputsInfo = respData.inputs

                    this.historyInfo.forEach(item => {
                        item.last_time = this.getLastTime(item.elapsed_time)
                    })
                    for (const key in this.inputsInfo) {
                        this.$set(this.renderData, key, this.inputsInfo[key])
                    }
                    if (this.nodeDetailConfig.component_code === 'job_execute_task') {
                        this.outputsInfo = this.outputsInfo.filter(output => {
                            const outputIndex = this.outputsInfo['job_global_var'].findIndex(prop => prop.name === output.key)
                            if (!output.preset && outputIndex === -1) {
                                return false
                            }
                            return true
                        })
                    }

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
                    
                    if (this.hasAdminPerm) {
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
                        await this.loadAtomConfig({ atomType: type, version })
                        return this.atomFormConfig[type][version]
                    } catch (e) {
                        this.$bkMessage({
                            message: e,
                            theme: 'error'
                        })
                    }
                }
            },
            async getHistoryLog () {
                try {
                    this.historyLogLoading = true
                    for (const history of this.historyInfo) {
                        const data = {
                            node_id: this.nodeDetailConfig.node_id,
                            history_id: history.history_id
                        }
                        const resp = await this.taskflowHistroyLog(data)
                        if (resp.result) {
                            this.historyLog[history.history_id] = resp.data.log
                        } else {
                            errorHandler(resp, this)
                        }
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.historyLogLoading = false
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
            onSelectExecuteTime () {
                this.loadNodeInfo()
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
    .common-icon-dark-circle-ellipsis {
        font-size: 12px;
        color: #3c96ff;
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
