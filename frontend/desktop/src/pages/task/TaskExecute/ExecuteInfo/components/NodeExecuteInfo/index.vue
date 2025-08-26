<template>
    <div :class="['node-execute-info', { 'loading': loading || isRecordLoading }]" :key="randomKey">
        <bk-tab
            :active.sync="curActiveTab"
            type="unborder-card"
            ext-cls="execute-info-tab"
            @tab-change="onTabChange">
            <bk-tab-panel name="record" v-if="!isBranchCondition" :label="$t('执行详情')"></bk-tab-panel>
            <bk-tab-panel name="config" v-if="isBranchCondition || ['ServiceActivity', 'SubProcess'].includes(nodeDetailConfig.type)" :label="$t('配置快照')"></bk-tab-panel>
            <bk-tab-panel name="history" v-if="!isBranchCondition" :label="$t('操作历史')"></bk-tab-panel>
            <bk-tab-panel name="log" v-if="!isBranchCondition" :label="$t('调用日志')"></bk-tab-panel>
        </bk-tab>
        <div class="scroll-area">
            <TaskCondition
                v-if="isBranchCondition"
                ref="conditionEdit"
                :condition-data="conditionData">
            </TaskCondition>
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
                    :constants="pipelineTree.constants"
                    :is-third-party-node="isThirdPartyNode"
                    :third-party-node-code="thirdPartyNodeCode"
                    :is-sub-process-node="isSubProcessNode">
                </ExecuteInfoForm>
                <section class="info-section" data-test-id="taskExecute_form_operatFlow" v-else-if="curActiveTab === 'history'">
                    <NodeOperationFlow
                        :node-id="executeInfo.id"
                        :sub-process-task-id="nodeDetailConfig.taskId"
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
</template>

<script>
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { checkDataType, getDefaultValueFormat } from '@/utils/checkDataType.js'
    import NodeOperationFlow from './components/NodeOperationFlow.vue'
    import ExecuteRecord from './components/ExecuteRecord/index.vue'
    import NodeLog from './components/NodeLog.vue'
    import ExecuteInfoForm from './components/ExecuteInfoForm.vue'
    import TaskCondition from './components/TaskCondition.vue'
    import { mapState, mapActions } from 'vuex'
    export default {
        name: 'nodeExecuteInfo',
        components: {
            NodeOperationFlow,
            ExecuteRecord,
            NodeLog,
            ExecuteInfoForm,
            TaskCondition
        },
        props: {
            adminView: {
                type: Boolean,
                default: false
            },
            loading: {
                type: Boolean,
                default: false
            },
            conditionData: {
                type: Object,
                default: () => ({})
            },
            nodeActivity: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({}),
                required: true
            },
            pipelineTree: {
                type: Object,
                default: () => ({})
            },
            notPerformedSubNode: {
                type: Boolean,
                default: false
            },
            engineVer: {
                type: Number,
                required: true
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            subprocessPipeline: {
                type: Object,
                default: () => ({})
            },
            realTimeState: {
                type: Object,
                default: () => ({})
            },
            autoRetryInfo: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                randomKey: null,
                isRecordLoading: false,
                curActiveTab: 'record',
                loop: 1,
                theExecuteTime: undefined,
                theExecuteRecord: 0,
                historyInfo: [],
                executeRecord: {},
                renderConfig: [],
                outputRenderConfig: [],
                isRenderOutputForm: false
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config,
                'atomOutputConfig': state => state.atomForm.outputConfig,
                'atomFormInfo': state => state.atomForm.form,
                'pluginOutput': state => state.atomForm.output
            }),
            isExecuteTimeShow () {
                return ['record', 'log'].includes(this.curActiveTab) && (this.loop > 1 || this.historyInfo.length > 1)
            },
            isThirdPartyNode () {
                const compCode = this.nodeDetailConfig.component_code
                return !!compCode && compCode === 'remote_plugin'
            },
            isSubProcessNode () {
                const compCode = this.nodeDetailConfig.component_code
                return !!compCode && compCode === 'subprocess_plugin'
            },
            isLegacySubProcess () { // 是否为旧版子流程
                return !this.isSubProcessNode && this.nodeActivity && this.nodeActivity.type === 'SubProcess'
            },
            thirdPartyNodeCode () {
                if (!this.isThirdPartyNode) return ''
                const nodeInfo = this.pipelineTree.activities[this.nodeDetailConfig.node_id]
                return nodeInfo ? nodeInfo.component.data?.plugin_code?.value : ''
            },
            isBranchCondition () {
                const { conditionType } = this.conditionData
                return conditionType && conditionType !== 'parallel'
            }
        },
        watch: {
            loading: {
                handler (val) {
                    if (val) return
                    // 当节点详情加载完毕后，这时则需加载节点记录详情
                    if (Object.keys(this.executeInfo).length) {
                        this.initLoad()
                    } else {
                        this.executeRecord = {}
                        this.theExecuteTime = undefined
                        this.historyInfo = []
                    }
                },
                deep: true
            },
            isRecordLoading (val) {
                this.$emit('updateExecuteInfoLoading', val)
            }
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            async initLoad () {
                try {
                    this.isRecordLoading = true
                    const record = await this.getExecuteRecord(this.executeInfo)
                    // 设置执行次数和循环次数
                    if (this.theExecuteTime === undefined) {
                        this.loop = record.loop
                        this.theExecuteTime = record.loop
                    }
                    // 【失败后跳过】过滤掉最新的记录
                    this.historyInfo = record.skip ? [] : [record]
                    if (record.histories) {
                        this.historyInfo.unshift(...record.histories)
                    }
                    // 记录当前循环下，总共执行的次数
                    this.theExecuteRecord = this.historyInfo.length
                    // 记录详情
                    this.executeRecord = record
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isRecordLoading = false
                }
            },
            // 获取执行记录数据
            async getExecuteRecord (record) {
                const { version, component_code: componentCode, componentData = {} } = this.nodeDetailConfig
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
                    const { constants } = this.subprocessPipeline
                    const renderConfig = await this.getSubflowInputsConfig(constants)
                    const keys = Object.keys(inputs)
                    this.renderConfig = renderConfig.filter(item => keys.includes(item.tag_code))
                } else if (componentCode) { // 任务节点需要加载标准插件
                    const pluginVersion = componentData.plugin_version?.value
                    await this.getNodeConfig(componentCode, version, pluginVersion)
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
                        outputs.forEach(param => {
                            // 判断preset是否为true
                            if (param.preset) {
                                outputsInfo.push(param)
                            } else {
                                // 判断key是否与插件配置项对应
                                const output = this.pluginOutputs.find(output => output.key === param.key)
                                if (output) {
                                    outputsInfo.push(param)
                                } else {
                                    // 判断key是否变量
                                    const varKey = `\${${param.key}}`
                                    const varInfo = this.pipelineTree.constants[varKey]
                                    let isHooked = false
                                    if (varInfo && varInfo.source_type === 'component_outputs') {
                                        isHooked = this.nodeActivity.id in varInfo.source_info
                                    }
                                    if (isHooked) {
                                        outputsInfo.push(param)
                                    }
                                }
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
                return {
                    ...record,
                    renderData,
                    renderConfig: this.renderConfig,
                    constants,
                    outputsInfo,
                    outputs,
                    inputs: inputsInfo,
                    failInfo,
                    last_time: tools.timeTransform(record.elapsed_time),
                    isExpand: true
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
                            // 设置host
                            const { origin } = window.location
                            const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${this.thirdPartyNodeCode}/`
                            $.context.bk_plugin_api_host[this.thirdPartyNodeCode] = hostUrl
                            if (forms.renderform) {
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
                    if (formItemConfig.type === 'combine') {
                        formItemConfig.name = variable.name
                    }
                    // 自定义输入框变量正则校验添加到插件配置项
                    if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: this.$t('默认值不符合正则规则：') + variable.validation
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
                const { plugin, version, classify, name, isThird } = config
                try {
                    // 先取标准节点缓存的数据
                    const pluginGroup = this.atomFormConfig[plugin]
                    if (pluginGroup && pluginGroup[version]) {
                        return pluginGroup[version]
                    }
                    // 第三方插件
                    if (isThird) {
                        const resp = await this.loadPluginServiceDetail({
                            plugin_code: plugin,
                            plugin_version: version,
                            with_app_detail: true
                        })
                        if (!resp.result) return
                        // 获取参数
                        const { forms, inputs } = resp.data
                        // 获取host
                        const { origin } = window.location
                        const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${plugin}/`
                        $.context.bk_plugin_api_host[plugin] = hostUrl
                        if (forms.renderform) {
                            // 输入参数
                            $.atoms[plugin] = {}
                            const renderFrom = forms.renderform
                            /* eslint-disable-next-line */
                            eval(renderFrom)
                        } else {
                            $.atoms[plugin] = inputs
                        }
                    } else {
                        await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id: this.project_id })
                    }
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
                    // 只渲染a标签，不过滤换行
                    let info = data.replace(/\n/g, '<br>')
                    info = this.filterXSS(info, {
                        whiteList: {
                            br: []
                        }
                    })
                    return info
                } else {
                    return data
                }
            },
            onTabChange (name) {
                this.curActiveTab = name
                if (['record', 'log'].includes(name)) {
                    this.onSelectExecuteRecord(this.theExecuteRecord)
                }
            },
            onSelectExecuteTime (time) {
                this.theExecuteTime = time
                this.$emit('onSelectExecuteTime', time)
                this.randomKey = new Date().getTime()
            },
            async onSelectExecuteRecord (time) {
                this.theExecuteRecord = time
                let record = this.historyInfo[time - 1]
                if (record) {
                    if (!('isExpand' in record)) {
                        record = await this.getExecuteRecord(record)
                    }
                    this.executeRecord = record
                } else {
                    this.executeRecord = {}
                }
                this.randomKey = new Date().getTime()
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.node-execute-info {
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
            ::v-deep .vjs-tree {
                color: #ffffff;
            }
        }
    }
    ::v-deep .vjs-tree {
        font-size: 12px;
    }
    ::v-deep .execute-info-tab .bk-tab-section{
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
            ::v-deep .bk-select {
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
    ::v-deep .common-section-title {
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
    ::v-deep .primary-value.code-editor {
        height: 300px;
    }
    ::v-deep .log-section {
        min-height: 758px;
    }
}
</style>
