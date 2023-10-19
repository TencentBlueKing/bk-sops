<template>
    <div :class="['plugin-config', { 'edit-mode': !isViewMode }]">
        <bk-collapse v-show="activeTab === 'pluginConfig'" class="variable-collapse" v-model="activeCollapse">
            <bk-collapse-item :hide-arrow="true" name="plugin">
                <i class="common-icon-next-triangle-shape"></i>
                {{ $t('插件选择') }}
                <BasicInfo
                    slot="content"
                    ref="basicInfo"
                    :basic-info="basicInfo"
                    :is-view-mode="isViewMode"
                    :is-sub-flow="isSubFlow"
                    :common="common"
                    :project_id="project_id"
                    :version-list="versionList"
                    :node-config="nodeConfig"
                    :input-loading="inputLoading"
                    :output-loading="outputLoading"
                    :sub-flow-updated="subFlowUpdated"
                    v-bkloading="{ isLoading: isBaseInfoLoading }"
                    @openSelectorPanel="isSelectorPanelShow = true"
                    @update="updateBasicInfo"
                    @versionChange="versionChange"
                    @selectScheme="onSelectSubFlowScheme"
                    @updateSubFlowVersion="updateSubFlowVersion">
                </BasicInfo>
            </bk-collapse-item>
            <bk-collapse-item :hide-arrow="true" name="inputParams">
                <i class="common-icon-next-triangle-shape"></i>
                {{ $t('输入参数') }}
                <div slot="content" v-if="!inputLoading" class="inputs-wrapper" v-bkloading="{ isLoading: inputLoading, zIndex: 100 }">
                    <template v-if="Array.isArray(inputs)">
                        <input-params
                            v-if="inputs.length > 0"
                            ref="inputParams"
                            :node-id="nodeId"
                            :scheme="inputs"
                            :plugin="basicInfo.plugin"
                            :version="basicInfo.version"
                            :sub-flow-forms="subFlowForms"
                            :forms-not-referred="formsNotReferred"
                            :value="inputsParamValue"
                            :render-config="inputsRenderConfig"
                            :is-sub-flow="isSubFlow"
                            :is-view-mode="isViewMode"
                            :constants="localConstants"
                            :third-party-code="isThirdParty ? basicInfo.plugin : ''"
                            @hookChange="onHookChange"
                            @renderConfigChange="onRenderConfigChange"
                            @update="updateInputsValue">
                        </input-params>
                        <no-data v-else :message="$t('暂无参数')"></no-data>
                    </template>
                    <template v-else>
                        <jsonschema-input-params
                            v-if="inputs.properties && Object.keys(inputs.properties).length > 0"
                            :inputs="inputs"
                            :value="inputsParamValue"
                            @update="updateInputsValue">
                        </jsonschema-input-params>
                        <no-data v-else :message="$t('暂无参数')"></no-data>
                    </template>
                </div>
            </bk-collapse-item>
            <bk-collapse-item :hide-arrow="true" name="outputParams">
                <i class="common-icon-next-triangle-shape"></i>
                {{ $t('输出参数') }}
                <div slot="content" class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading, zIndex: 100 }">
                    <template v-if="!outputLoading">
                        <output-params
                            v-if="outputs.length"
                            ref="outputParams"
                            :constants="localConstants"
                            :params="outputs"
                            :version="basicInfo.version"
                            :node-id="nodeId"
                            :is-third-party="isThirdParty"
                            :is-view-mode="isViewMode"
                            @hookChange="onHookChange">
                        </output-params>
                        <no-data v-else :message="$t('暂无参数')"></no-data>
                    </template>
                </div>
            </bk-collapse-item>
        </bk-collapse>
        <!-- 流程控制选项 -->
        <ControlOption
            v-show="activeTab === 'controlOption'"
            :is-view-mode="isViewMode"
            :node-id="nodeId"
            @update="updateBasicInfo"
            @close="$emit('close')">
        </ControlOption>
        <!-- 插件/子流程选择面板 -->
        <selectPanel
            v-if="isSelectorPanelShow"
            :crt-plugin="basicInfo.plugin"
            :is-third-party="isThirdParty"
            :built-in-plugin="atomTypeList.tasknode"
            @select="onPluginOrTplChange">
        </selectPanel>
        <div class="btn-footer">
            <bk-button
                v-if="!isViewMode"
                theme="primary"
                :disabled="inputLoading || (isSubFlow && subFlowListLoading)"
                data-test-id="templateEdit_form_saveNodeConfig"
                @click="onSaveConfig">
                {{ $t('确定') }}
            </bk-button>
            <bk-button
                theme="default"
                data-test-id="templateEdit_form_cancelNodeConfig"
                @click="onClosePanel()">
                {{ isViewMode ? $t('关闭') : $t('取消') }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState, mapMutations } from 'vuex'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import BasicInfo from './BasicInfo.vue'
    import InputParams from './InputParams.vue'
    import JsonschemaInputParams from './JsonschemaInputParams.vue'
    import OutputParams from './OutputParams.vue'
    import SelectPanel from './SelectPanel.vue'
    // import VariableEdit from '../TemplateSetting/TabGlobalVariables/VariableEdit.vue'
    // import QuickOperateVariable from '../../common/QuickOperateVariable.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import bus from '@/utils/bus.js'
    import permission from '@/mixins/permission.js'
    import formSchema from '@/utils/formSchema.js'
    import ControlOption from './ControlOption.vue'

    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            JsonschemaInputParams,
            OutputParams,
            // SelectPanel,
            // VariableEdit,
            NoData,
            ControlOption,
            SelectPanel
            // QuickOperateVariable
        },
        mixins: [permission],
        props: {
            project_id: [String, Number],
            nodeId: String,
            isShow: Boolean,
            activeTab: String,
            isShowSelect: Boolean,
            atomList: Array,
            subflowList: Array,
            atomTypeList: Object,
            templateLabels: Array,
            common: [String, Number],
            subFlowListLoading: Boolean,
            backToVariablePanel: Boolean,
            isNotExistAtomOrVersion: Boolean,
            pluginLoading: Boolean,
            isViewMode: Boolean,
            isolationAtomConfig: Object
        },
        data () {
            return {
                activeCollapse: ['plugin', 'inputParams', 'outputParams'],
                sideWidth: 800, // 侧栏宽度
                subFlowUpdated: false, // 子流程是否更新
                taskNodeLoading: false, // 普通任务节点数据加载
                subFlowLoading: false, // 子流程任务节点数据加载
                constantsLoading: false, // 子流程输入参数配置项加载
                subFlowVersionUpdating: false, // 子流程更新
                isCancelGloVarDialogShow: false, // 取消勾选全局变量
                nodeConfig: {}, // 任务节点的完整 activity 配置参数
                isBaseInfoLoading: true, // 基础信息loading
                basicInfo: {}, // 基础信息模块
                versionList: [], // 标准插件版本
                inputs: [], // 输入参数表单配置项
                inputsParamValue: {}, // 输入参数值
                inputsRenderConfig: {}, // 输入参数是否配置渲染豁免
                outputs: [], // 输出参数
                subFlowForms: {}, // 子流程输入参数
                formsNotReferred: {}, // 未被子流程引用的全局变量
                isSelectorPanelShow: false, // 是否显示选择插件(子流程)面板
                isVariablePanelShow: false, // 是否显示变量编辑面板
                variableData: {}, // 当前编辑的变量
                localConstants: {}, // 全局变量列表，用来维护当前面板勾选、反勾选后全局变量的变化情况，保存时更新到 store
                randomKey: new Date().getTime(), // 输入、输出参数勾选状态改变时更新popover
                isThirdParty: false, // 是否为第三方插件
                variableCited: {}, // 全局变量被任务节点、网关节点以及其他全局变量引用情况
                unhookingVarForm: {}, // 正被取消勾选的表单配置
                isUpdateConstants: false, // 是否更新输入参数配置
                isDataChange: false // 数据是否改变
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable,
                'locations': state => state.template.location,
                'pluginConfigs': state => state.atomForm.config,
                'pluginOutput': state => state.atomForm.output,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            variableList () {
                const systemVars = Object.keys(this.internalVariable).map(key => this.internalVariable[key])
                const userVars = Object.keys(this.localConstants).map(key => this.localConstants[key])
                return [...systemVars, ...userVars]
            },
            isSubFlow () {
                return this.nodeConfig.type !== 'ServiceActivity'
            },
            atomGroup () { // 某一标准插件下所有版本分组
                let atom = this.atomList.find(item => item.code === this.basicInfo.plugin)
                atom = atom || this.isolationAtomConfig
                return atom
            },
            inputLoading () { // 以下任一方法处于 pending 状态，输入参数展示 loading 效果
                return this.isBaseInfoLoading || this.taskNodeLoading || this.subFlowLoading || this.constantsLoading || this.subFlowVersionUpdating
            },
            outputLoading () {
                return this.isBaseInfoLoading || this.taskNodeLoading || this.subFlowLoading
            },
            selectorTitle () {
                return this.isSubFlow ? i18n.t('选择子流程') : i18n.t('选择标准插件')
            },
            // 子流程节点是否为公共流程
            isCommonTpl () {
                return this.common || this.nodeConfig.template_source === 'common'
            }
        },
        watch: {
            constants (val) {
                this.localConstants = tools.deepClone(val)
            },
            subFlowListLoading (val) {
                if (!val) {
                    // 获取子流程模板的名称
                    Promise.resolve(this.getNodeBasic(this.nodeConfig)).then(res => {
                        this.basicInfo = res
                    })
                }
            }
        },
        created () {
            /**
             * notice: 该方法为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
             * description: 切换作业模板时，将当前作业的全局变量表格数据部分添加到输出参数
             */
            bus.$on('jobExecuteTaskOutputs', args => {
                const { plugin, version } = this.basicInfo
                if (!this.isSubFlow && plugin === 'job_execute_task') {
                    // tagDatatable 值发生变更前后的值
                    const { val, oldVal } = args
                    const outputs = [...this.pluginOutput[plugin][version]]
                    if (val && val.length > 0) {
                        val.forEach(item => {
                            if (item.category === 1) {
                                outputs.push({
                                    name: item.name,
                                    key: item.name,
                                    version
                                })
                            }
                        })
                    }
                    if (oldVal && oldVal.length > 0) {
                        // 清除变更后不存在且被勾选的输出变量
                        oldVal.forEach(item => {
                            if (item.category === 1) {
                                // 切换前后一直存在的变量不处理
                                if (val.find(v => v.id === item.id)) {
                                    return
                                }
                                Object.keys(this.localConstants).some(key => {
                                    const constant = this.localConstants[key]
                                    const sourceInfo = constant.source_info[this.nodeId]
                                    if (sourceInfo && sourceInfo.includes(item.name)) {
                                        this.deleteVariable(key)
                                        return true
                                    }
                                })
                            }
                        })
                    }

                    this.outputs = outputs
                }
            })
            this.localConstants = tools.deepClone(this.constants)
        },
        async mounted () {
            const defaultData = await this.initDefaultData()
            for (const [key, val] of Object.entries(defaultData)) {
                this[key] = val
            }
            this.initData()
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceMeta',
                'loadPluginServiceDetail',
                'loadPluginServiceAppDetail'
            ]),
            ...mapActions('template/', [
                'loadTemplateData',
                'getVariableCite',
                'getProcessOpenChdProcess'
            ]),
            ...mapActions('task', [
                'loadSubflowConfig'
            ]),
            ...mapMutations('template/', [
                'setSubprocessUpdated',
                'setActivities',
                'addVariable',
                'setConstants',
                'setOutputs'
            ]),
            async initDefaultData () {
                const nodeConfig = tools.deepClone(this.activities[this.nodeId])
                const isThirdParty = nodeConfig.component && nodeConfig.component.code === 'remote_plugin'
                if (nodeConfig.type === 'ServiceActivity') {
                    this.basicInfo = await this.getNodeBasic(nodeConfig)
                } else {
                    this.isSelectorPanelShow = !nodeConfig.template_id
                    this.basicInfo = await this.getNodeBasic(nodeConfig)
                }
                this.$nextTick(() => {
                    this.isBaseInfoLoading = false
                })
                const basicInfo = this.basicInfo
                let versionList = []
                if (nodeConfig.type === 'ServiceActivity') {
                    const code = isThirdParty ? nodeConfig.name : nodeConfig.component.code
                    versionList = this.getAtomVersions(code, isThirdParty)
                }
                const isSelectorPanelShow = nodeConfig.type === 'ServiceActivity' ? !basicInfo.plugin : !basicInfo.tpl
                return {
                    nodeConfig,
                    isThirdParty,
                    basicInfo,
                    versionList,
                    isSelectorPanelShow
                }
            },
            // 初始化节点数据
            async initData () {
                if (!this.basicInfo.plugin && !this.basicInfo.tpl) { // 未选择插件
                    return
                }
                if (!this.isSubFlow) {
                    const paramsVal = {}
                    const renderConfig = {}
                    Object.keys(this.nodeConfig.component.data || {}).forEach(key => {
                        const val = tools.deepClone(this.nodeConfig.component.data[key].value)
                        paramsVal[key] = val
                        renderConfig[key] = 'need_render' in this.nodeConfig.component.data[key] ? this.nodeConfig.component.data[key].need_render : true
                    })
                    this.inputsParamValue = paramsVal
                    this.inputsRenderConfig = renderConfig
                    await this.getPluginDetail()
                } else {
                    const { tpl, version } = this.basicInfo
                    const forms = {}
                    const renderConfig = {}
                    Object.keys(this.nodeConfig.constants).forEach(key => {
                        const form = this.nodeConfig.constants[key]
                        if (form.show_type === 'show') {
                            forms[key] = form
                            renderConfig[key] = 'need_render' in form ? form.need_render : true
                        }
                    })
                    await this.getSubFlowDetail(tpl, version)
                    this.inputs = await this.getSubFlowInputsConfig()
                    this.inputsParamValue = this.getSubFlowInputsValue(forms)
                    this.inputsRenderConfig = renderConfig
                }
                // 节点参数错误时，配置项加载完成后，执行校验逻辑，提示用户错误信息
                const location = this.locations.find(item => item.id === this.nodeConfig.id)
                if (location && location.status === 'FAILED') {
                    this.validate()
                }
                // 获取插件配置时会去更新baseInfo，这个时候数据并没有修改
                this.isDataChange = false
            },
            /**
             * 加载标准插件节点输入参数表单配置项，获取输出参数列表
             */
            async getPluginDetail () {
                const { plugin, version } = this.basicInfo
                this.taskNodeLoading = true
                try {
                    // 获取输入输出参数
                    this.inputs = await this.getAtomConfig({ plugin, version, isThird: this.isThirdParty })
                    if (!this.isThirdParty) {
                        this.outputs = this.atomGroup.list.find(item => item.version === version).output
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.taskNodeLoading = false
                }
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (config) {
                const { plugin, version, classify, name, isThird } = config
                const project_id = this.isCommonTpl ? undefined : this.project_id
                try {
                    // 先取标准节点缓存的数据
                    const pluginGroup = this.pluginConfigs[plugin]
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
                        const { outputs: respOutputs, forms, inputs } = resp.data
                        // 获取不同版本的描述
                        let desc = resp.data.desc || ''
                        if (desc && desc.includes('\n')) {
                            const descList = desc.split('\n')
                            desc = descList.join('<br>')
                        }
                        this.updateBasicInfo({ desc })
                        if (forms.renderform) {
                            if (!this.isSubFlow) {
                                // 获取第三方插件公共输出参数
                                if (!this.pluginOutput['remote_plugin']) {
                                    await this.loadAtomConfig({ atom: 'remote_plugin', version: '1.0.0' })
                                }
                                // 输出参数
                                const storeOutputs = this.pluginOutput['remote_plugin']['1.0.0']
                                const outputs = []
                                for (const [key, val] of Object.entries(respOutputs.properties)) {
                                    outputs.push({
                                        name: val.title,
                                        key,
                                        type: val.type,
                                        schema: { description: val.description || '--' }
                                    })
                                }
                                this.outputs = [...storeOutputs, ...outputs]
                            }
                            // 获取host
                            const { origin } = window.location
                            const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${plugin}/`
                            $.context.bk_plugin_api_host[plugin] = hostUrl
                            // 输入参数
                            $.atoms[plugin] = {}
                            const renderFrom = forms.renderform
                            /* eslint-disable-next-line */
                            eval(renderFrom)
                        } else {
                            $.atoms[plugin] = inputs
                            this.outputs = [] // jsonschema form输出参数
                        }
                    } else {
                        await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id })
                    }
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.log(e)
                }
            },
            /**
             * 加载子流程任务节点输入、输出、版本配置项
             */
            async getSubFlowDetail (tpl, version = '') {
                this.subFlowLoading = true
                try {
                    const schemeIds = this.basicInfo.schemeIdList.filter(item => item)
                    const params = {
                        template_id: tpl,
                        scheme_id_list: schemeIds,
                        version
                    }
                    if (this.isCommonTpl) {
                        params.template_source = 'common'
                    } else {
                        params.project_id = this.project_id
                    }
                    const resp = await this.loadSubflowConfig(params)
                    // 子流程的输入参数包括流程引用的变量、自定义变量和未被引用的变量
                    this.subFlowForms = { ...resp.data.pipeline_tree.constants, ...resp.data.custom_constants, ...resp.data.constants_not_referred }
                    this.formsNotReferred = resp.data.constants_not_referred
                    // 子流程模板版本更新时，未带版本信息，需要请求接口后获取最新版本
                    this.updateBasicInfo({ version: resp.data.version })

                    // 输出变量
                    this.outputs = Object.keys(resp.data.outputs).map(item => {
                        const output = resp.data.outputs[item]
                        return {
                            plugin_code: output.plugin_code,
                            name: output.name,
                            key: output.key,
                            version: output.hasOwnProperty('version') ? output.version : 'legacy'
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.subFlowLoading = false
                }
            },
            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubFlowInputsConfig () {
                this.constantsLoading = true
                const variables = Object.keys(this.subFlowForms)
                    .map(key => this.subFlowForms[key])
                    .filter(item => item.show_type === 'show')
                    .sort((a, b) => a.index - b.index)

                const inputs = await Promise.all(variables.map(async (variable) => {
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
                    return formItemConfig
                }))
                this.constantsLoading = false
                return inputs
            },
            /**
             * 获取任务节点基础信息数据
             */
            async getNodeBasic (config) {
                if (config.type === 'ServiceActivity') {
                    const {
                        component, name, stage_name = '', labels, error_ignorable, can_retry,
                        retryable, isSkipped, skippable, optional, auto_retry, timeout_config,
                        executor_proxy
                    } = config
                    let basicInfoName = i18n.t('请选择插件')
                    let code = ''
                    let desc = ''
                    let version = ''
                    // 节点已选择标准插件
                    if (component.code && !this.isNotExistAtomOrVersion) { // 节点插件存在
                        if (component.code === 'remote_plugin') {
                            const atom = this.$parent.thirdPartyList[this.nodeId]
                            code = component.data.plugin_code.value
                            const resp = await this.loadPluginServiceAppDetail({ plugin_code: code })
                            basicInfoName = resp.data.name
                            version = atom.version
                            desc = atom.desc
                        } else {
                            let atom = this.atomList.find(item => item.code === component.code)
                            atom = atom || this.isolationAtomConfig
                            code = component.code
                            basicInfoName = `${atom.group_name}-${atom.name}`
                            version = component.hasOwnProperty('version') ? component.version : 'legacy'
                            // 获取不同版本的描述
                            desc = atom.list.find(item => item.version === version).desc
                        }
                        if (desc && desc.includes('\n')) {
                            const descList = desc.split('\n')
                            desc = descList.join('<br>')
                        }
                    }
                    const executorProxy = executor_proxy ? executor_proxy.split(',') : []

                    return {
                        plugin: code,
                        name: basicInfoName, // 插件名称
                        nodeName: name, // 节点名称
                        stageName: stage_name,
                        nodeLabel: labels || [], // 兼容旧数据，节点标签字段为后面新增
                        version, // 标准插件版本
                        desc, // 空节点不存在插件描述信息
                        ignorable: error_ignorable,
                        // isSkipped 和 can_retry 为旧数据字段，后来分别变更为 skippable、retryable，节点点开编辑保存后会删掉旧字段
                        // 这里取值做兼容处理，新旧数据不可能同时存在，优先取旧数据字段
                        skippable: isSkipped === undefined ? skippable : isSkipped,
                        retryable: can_retry === undefined ? retryable : can_retry,
                        selectable: optional,
                        autoRetry: Object.assign({}, { enable: false, interval: 0, times: 1 }, auto_retry),
                        timeoutConfig: timeout_config || { enable: false, seconds: 10, action: 'forced_fail' },
                        executor_proxy: executorProxy
                    }
                } else {
                    const {
                        template_id, name, stage_name = '', labels, optional, always_use_latest, scheme_id_list, executor_proxy,
                        auto_retry, timeout_config, error_ignorable, isSkipped, skippable, can_retry, retryable
                    } = config
                    let templateName = i18n.t('请选择子流程')

                    if (template_id) {
                        const subFlowInfo = this.atomTypeList.subflow.find(item => item.template_id === Number(template_id))
                        if (subFlowInfo) {
                            templateName = subFlowInfo.name
                        } else {
                            const templateData = await this.loadTemplateData({
                                templateId: template_id,
                                common: this.common || config.template_source === 'common',
                                checkPermission: true })
                                .catch(error => {
                                    this.onClosePanel()
                                    console.log(error)
                                }) || {}
                            templateName = templateData.name
                        }
                    }
                    const executorProxy = executor_proxy ? executor_proxy.split(',') : []
                    return {
                        tpl: template_id || '',
                        name: templateName, // 流程模版名称
                        nodeName: name, // 节点名称
                        stageName: stage_name,
                        nodeLabel: labels || [], // 兼容旧数据，节点标签字段为后面新增
                        selectable: optional,
                        alwaysUseLatest: always_use_latest || false, // 兼容旧数据，该字段为新增
                        schemeIdList: scheme_id_list || [], // 兼容旧数据，该字段为后面新增
                        version: config.hasOwnProperty('version') ? config.version : '', // 子流程版本，区别于标准插件版本
                        ignorable: error_ignorable,
                        skippable: isSkipped === undefined ? skippable : isSkipped,
                        retryable: can_retry === undefined ? retryable : can_retry,
                        autoRetry: Object.assign({}, { enable: false, interval: 0, times: 1 }, auto_retry),
                        timeoutConfig: timeout_config || { enable: false, seconds: 10, action: 'forced_fail' },
                        executor_proxy: executorProxy
                    }
                }
            },
            /**
             * 获取某一标准插件所有版本列表
             */
            getAtomVersions (code, isThirdParty = false) {
                if (!code || this.isNotExistAtomOrVersion) {
                    return []
                }
                let atom
                if (isThirdParty) {
                    atom = this.$parent.thirdPartyList[this.nodeId]
                    return atom && atom.list
                } else {
                    atom = this.atomList.find(item => item.code === code)
                    atom = atom || this.isolationAtomConfig
                    return atom.list.map(item => {
                        return {
                            version: item.version
                        }
                    }).reverse()
                }
            },
            /**
             * 获取子流程任务节点输入参数值，有三种情况：
             * 1.节点点开编辑时取 activitity 里的 constants 数据
             * 2.切换子流程时，取接口返回的 form 数据
             * 3.子流程更新时，先判断表单项是否为勾选状态，勾选取旧表单项数据，
             * 未勾选则判断新旧表单项数据 custom_type(自定义全局变量)或者 source_tag(标准插件表单项)是否相同，
             * 相同取旧数据里的表单值，否则取新数据
             */
            getSubFlowInputsValue (forms, oldForms = {}) {
                return Object.keys(forms).reduce((acc, cur) => { // 遍历新表单项
                    const variable = forms[cur]
                    if (variable.show_type === 'show') {
                        let canReuse = false
                        const oldVariable = oldForms[cur]
                        const isHooked = this.isInputParamsInConstants(variable)
                        if (oldVariable && !isHooked) { // 旧版本中存在相同key的表单项，且不是勾选状态
                            if (variable.custom_type || oldVariable.custom_type) {
                                canReuse = variable.custom_type === oldVariable.custom_type
                            } else {
                                canReuse = variable.source_tag === oldVariable.source_tag
                            }
                        }
                        const val = canReuse ? this.inputsParamValue[cur] : variable.value
                        acc[variable.key] = tools.deepClone(val)
                    }

                    return acc
                }, {})
            },
            // 输入参数是否已被勾选到全局变量
            isInputParamsInConstants (form) {
                return Object.keys(this.localConstants).some(key => {
                    const varItem = this.localConstants[key]
                    const sourceInfo = varItem.source_info[this.nodeId]
                    return sourceInfo && sourceInfo.includes(form.tag_code)
                })
            },
            // 由标准插件(子流程)选择面板返回配置面板
            goBackToConfig () {
                if (this.isSelectorPanelShow && (this.basicInfo.plugin || this.basicInfo.tpl)) {
                    this.isSelectorPanelShow = false
                }
            },
            // 标准插件（子流程）选择面板切换插件（子流程）
            // isThirdParty 是否为第三方插件
            async onPluginOrTplChange (val) {
                let inputs = this.inputs
                if (this.isSubFlow) {
                    // 重置basicInfo, 避免基础信息面板因监听basicInfo导致重复调取接口，初始化时获取空值
                    const { id, name, version } = val
                    const config = {
                        name,
                        version,
                        tpl: id,
                        nodeName: name,
                        selectable: true,
                        alwaysUseLatest: false,
                        schemeIdList: []
                    }
                    this.updateBasicInfo(config)
                    if ('project' in val && typeof val.project.id === 'number') {
                        this.$set(this.nodeConfig, 'template_source', 'business')
                    } else {
                        this.$set(this.nodeConfig, 'template_source', 'common')
                    }
                    // 清空输入参数，否则会先加载上一个的子流程的配置再去加载选中的子流程配置
                    inputs = tools.deepClone(this.inputs)
                    this.inputs = []
                }
                this.isSelectorPanelShow = false
                this.isThirdParty = val.id === 'remote_plugin'
                await this.clearParamsSourceInfo(inputs)
                if (this.isSubFlow) {
                    this.tplChange(val)
                } else {
                    this.pluginChange(val)
                }
            },
            /**
             * 标准插件切换
             * - 清除勾选变量与全局变量关联
             * - 更新基础信息
             * - 加载插件配置详情
             * - 校验基础信息
             */
            async pluginChange (atomGroup) {
                const { code, group_name, name, list } = atomGroup
                this.versionList = this.isThirdParty ? list : this.getAtomVersions(code)
                // 获取不同版本的描述
                let desc = atomGroup.desc || ''
                if (!this.isThirdParty) {
                    let atom = this.atomList.find(item => item.code === code)
                    atom = atom || this.isolationAtomConfig
                    desc = atom.list.find(item => item.version === list[list.length - 1].version).desc
                } else {
                    desc = ''
                }
                if (desc && desc.includes('\n')) {
                    const descList = desc.split('\n')
                    desc = descList.join('<br>')
                }
                const config = {
                    plugin: code,
                    version: list[list.length - 1].version,
                    name: this.isThirdParty ? name : `${group_name}-${name}`,
                    nodeName: name,
                    stageName: '',
                    nodeLabel: [],
                    desc,
                    ignorable: false,
                    skippable: true,
                    retryable: true,
                    selectable: true
                }
                this.updateBasicInfo(config)
                this.inputsParamValue = {}
                await this.getPluginDetail()
                if (Array.isArray(this.inputs)) {
                    this.inputsRenderConfig = this.inputs.reduce((acc, crt) => {
                        acc[crt.tag_code] = crt.type !== 'code_editor'
                        return acc
                    }, {})
                }
                this.$refs.basicInfo && this.$refs.basicInfo.validate() // 清除节点保存报错时的错误信息
            },
            /**
             * 标准插件版本切换
             */
            async versionChange (val) {
                // 获取不同版本的描述
                let desc = this.basicInfo.desc
                if (!this.isThirdParty) {
                    let atom = this.atomList.find(item => item.code === this.basicInfo.plugin)
                    atom = atom || this.isolationAtomConfig
                    desc = atom.list.find(item => item.version === val).desc
                }
                if (desc && desc.includes('\n')) {
                    const descList = desc.split('\n')
                    desc = descList.join('<br>')
                }
                this.updateBasicInfo({ version: val, desc })
                await this.clearParamsSourceInfo()
                this.inputsParamValue = {}
                await this.getPluginDetail()
                if (Array.isArray(this.inputs)) {
                    this.inputsRenderConfig = this.inputs.reduce((acc, crt) => {
                        acc[crt.tag_code] = crt.type !== 'code_editor'
                        return acc
                    }, {})
                }
            },
            /**
             * 子流程切换
             * - 清除勾选变量与全局变量关联
             * - 请求子流程模板详情，组装 scheme 和 value，更新基础信息
             * - 清除子流程更新（每次都调用，store 里方法对不存在新版本的模板有做兼容）
             * - 校验基础信息
             */
            async tplChange (data) {
                await this.getSubFlowDetail(data.id, data.version)
                this.inputs = await this.getSubFlowInputsConfig()
                this.inputsParamValue = this.getSubFlowInputsValue(this.subFlowForms)
                this.inputsRenderConfig = Object.keys(this.subFlowForms).reduce((acc, crt) => {
                    const formItem = this.subFlowForms[crt]
                    if (formItem.show_type === 'show') {
                        acc[crt] = 'need_render' in formItem ? formItem.need_render : true
                    }
                    return acc
                }, {})
                this.setSubprocessUpdated({
                    expired: false,
                    subprocess_node_id: this.nodeConfig.id
                })
                this.$refs.basicInfo && this.$refs.basicInfo.validate() // 清除节点保存报错时的错误信息
            },
            /**
             * 更新基础信息
             * 填写基础信息表单，切换插件/子流程，选择插件版本，子流程更新
             */
            updateBasicInfo (data) {
                this.isDataChange = true
                this.basicInfo = Object.assign({}, this.basicInfo, data)
            },
            // 输入参数表单值更新
            updateInputsValue (val) {
                this.isDataChange = true
                this.inputsParamValue = val
            },
            /**
             * 子流程版本更新
             */
            async updateSubFlowVersion () {
                this.subFlowVersionUpdating = true
                const oldForms = Object.assign({}, this.subFlowForms)
                await this.getSubFlowDetail(this.basicInfo.tpl)
                await this.subFlowUpdateParamsChange()
                this.inputs = await this.getSubFlowInputsConfig()
                this.subFlowVersionUpdating = false
                this.$nextTick(() => {
                    this.inputsParamValue = this.getSubFlowInputsValue(this.subFlowForms, oldForms)
                    this.inputsRenderConfig = Object.keys(this.subFlowForms).reduce((acc, crt) => {
                        const formItem = this.subFlowForms[crt]
                        if (formItem.show_type === 'show') {
                            acc[crt] = 'need_render' in formItem ? formItem.need_render : true
                        }
                        return acc
                    }, {})
                    this.subFlowUpdated = true
                })
            },
            /**
             * 子流程版本更新后，输入、输出参数如果有变更，需要处理全局变量的 source_info 更新
             * 分为两种情况：
             * 1.输入、输出参数被勾选，并且对应变量在新流程模板中被删除或者变量 source_tag 有更新，需要在更新后修改全局变量 source_info 信息
             * 2.新增和修改输入、输出参数，不做处理
             */
            async subFlowUpdateParamsChange () {
                this.isUpdateConstants = true
                this.variableCited = await this.getVariableCitedData() || {}
                const nodeId = this.nodeConfig.id
                for (const key in this.localConstants) {
                    const varItem = this.localConstants[key]
                    const { source_type, source_info } = varItem
                    const sourceInfo = source_info[this.nodeId]
                    if (sourceInfo) {
                        if (source_type === 'component_inputs') {
                            sourceInfo.forEach(nodeFormItem => {
                                const newTplVar = this.subFlowForms[nodeFormItem]

                                if (!newTplVar || newTplVar.source_tag !== varItem.source_tag) { // 变量被删除或者变量类型有变更
                                    this.setVariableSourceInfo({
                                        key,
                                        id: nodeId,
                                        type: 'delete',
                                        tagCode: nodeFormItem
                                    })
                                }
                            })
                        }
                        if (source_type === 'component_outputs') {
                            sourceInfo.forEach(nodeFormItem => {
                                if (!this.outputs.find(item => item.key === nodeFormItem)) {
                                    this.setVariableSourceInfo({
                                        key,
                                        id: nodeId,
                                        type: 'delete',
                                        tagCode: nodeFormItem
                                    })
                                }
                            })
                        }
                    }
                }
                this.variableCited = {}
                this.isUpdateConstants = false
            },
            // 取消已勾选为全局变量的输入、输出参数勾选状态
            async clearParamsSourceInfo (inputs = this.inputs) {
                this.isUpdateConstants = true
                this.variableCited = await this.getVariableCitedData() || {}
                const nodeId = this.nodeConfig.id
                for (const key in this.localConstants) {
                    const varItem = this.localConstants[key]
                    const { source_type, source_info } = varItem
                    const sourceInfo = source_info[this.nodeId]
                    if (sourceInfo) {
                        if (source_type === 'component_inputs') {
                            inputs.forEach(formItem => {
                                if (sourceInfo.includes(formItem.tag_code)) {
                                    this.setVariableSourceInfo({
                                        key,
                                        id: nodeId,
                                        type: 'delete',
                                        tagCode: formItem.tag_code
                                    })
                                }
                            })
                        }
                        if (source_type === 'component_outputs') {
                            this.outputs.forEach(formItem => {
                                if (sourceInfo.includes(formItem.key)) {
                                    this.setVariableSourceInfo({
                                        key,
                                        id: nodeId,
                                        type: 'delete',
                                        tagCode: formItem.key
                                    })
                                }
                            })
                        }
                    }
                }
                this.variableCited = {}
                this.isUpdateConstants = false
            },
            // 重选插件
            handleReselectPlugin () {
                this.$parent.isNotExistAtomOrVersion = false
                this.isSelectorPanelShow = true
            },
            // 查看子流程模板
            onViewSubFlow (id) {
                const { name } = this.$route
                const routerName = name === 'commonTemplatePanel'
                    ? 'commonTemplatePanel'
                    : this.isCommonTpl
                        ? 'projectCommonTemplatePanel'
                        : 'templatePanel'
                const pathData = {
                    name: routerName,
                    params: {
                        type: 'view',
                        project_id: name === 'commonTemplatePanel' ? undefined : this.project_id
                    },
                    query: {
                        template_id: id,
                        common: name === 'templatePanel' ? undefined : '1'
                    }
                }
                const { href } = this.$router.resolve(pathData)
                window.open(href, '_blank')
            },
            // 切换子流程执行方案，需要重新请求输入、输出参数
            async onSelectSubFlowScheme () {
                const oldForms = Object.assign({}, this.subFlowForms)
                await this.getSubFlowDetail(this.basicInfo.tpl, this.basicInfo.version)
                await this.subFlowUpdateParamsChange()
                this.inputs = await this.getSubFlowInputsConfig()
                this.$nextTick(() => {
                    this.inputsParamValue = this.getSubFlowInputsValue(this.subFlowForms, oldForms)
                    this.inputsRenderConfig = Object.keys(this.subFlowForms).reduce((acc, crt) => {
                        const formItem = this.subFlowForms[crt]
                        if (formItem.show_type === 'show') {
                            acc[crt] = 'need_render' in formItem ? formItem.need_render : true
                        }
                        return acc
                    }, {})
                })
            },
            // 是否渲染豁免切换
            onRenderConfigChange (data) {
                this.isDataChange = true
                const [key, val] = data
                this.inputsRenderConfig[key] = val
            },
            // 输入、输出参数勾选状态变化
            onHookChange (type, data) {
                if (type === 'create') {
                    this.$set(this.localConstants, data.key, data)
                } else {
                    this.variableCited = {}
                    this.setVariableSourceInfo(data)
                }
                // 如果全局变量数据有变，需要更新popover
                this.randomKey = new Date().getTime()
            },
            // 更新全局变量的 source_info
            async setVariableSourceInfo (data) {
                const { type, id, key, tagCode, source } = data
                const constant = this.localConstants[key]
                if (!constant) return
                const sourceInfo = constant.source_info
                if (type === 'add') {
                    if (sourceInfo[id]) {
                        sourceInfo[id].push(tagCode)
                    } else {
                        this.$set(sourceInfo, id, [tagCode])
                    }
                } else if (type === 'delete') {
                    this.unhookingVarForm = { ...data, value: constant.value }
                    if (!Object.keys(this.variableCited).length) {
                        this.variableCited = await this.getVariableCitedData() || {}
                    }
                    const { activities, conditions, constants } = this.variableCited[key]
                    const citedNum = activities.length + conditions.length + constants.length
                    if (citedNum <= 1) {
                        this.deleteUnhookingVar()
                    } else {
                        // 当变量来源为0时，自动删除变量
                        if (sourceInfo[id].length <= 1) {
                            this.$delete(sourceInfo, id)
                        } else {
                            let atomIndex
                            sourceInfo[id].some((item, index) => {
                                if (item === tagCode) {
                                    atomIndex = index
                                    return true
                                }
                            })
                            sourceInfo[id].splice(atomIndex, 1)
                        }
                        if (Object.keys(sourceInfo).length === 0) {
                            this.$delete(this.localConstants, key)
                        }
                        const refDom = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                        refDom && refDom.setFormData({ ...this.unhookingVarForm })
                    }
                }
            },
            async getVariableCitedData () {
                try {
                    const config = this.getNodeFullConfig()
                    const activities = Object.assign({}, this.activities, { [this.nodeId]: config })
                    const data = {
                        activities,
                        gateways: this.gateways,
                        constants: { ...this.internalVariable, ...this.localConstants }
                    }
                    const resp = await this.getVariableCite(data)
                    if (resp.result) {
                        return resp.data.defined
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            deleteUnhookingVar () {
                const { key, source } = this.unhookingVarForm
                this.$delete(this.localConstants, key)
                const refDom = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                refDom && refDom.setFormData({ ...this.unhookingVarForm })
                this.isCancelGloVarDialogShow = false
            },
            onCancelVarConfirmClick () {
                const { key, source } = this.unhookingVarForm
                const constant = this.localConstants[key]
                constant.source_info = {}
                const refDom = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                refDom && refDom.setFormData({ ...this.unhookingVarForm })
                this.isCancelGloVarDialogShow = false
            },
            // 删除全局变量
            deleteVariable (key) {
                const constant = this.localConstants[key]

                for (const key in this.localConstants) {
                    const varItem = this.localConstants[key]
                    if (varItem.index > constant.index) {
                        varItem.index = varItem.index - 1
                    }
                }

                this.$delete(this.localConstants, key)
            },
            // 节点配置面板表单校验，基础信息和输入参数
            validate () {
                return this.$refs.basicInfo.validate().then(validator => {
                    if (this.$refs.inputParams) {
                        return this.$refs.inputParams.validate()
                    } else {
                        return true
                    }
                })
            },
            getNodeFullConfig () {
                let config
                if (this.isSubFlow) {
                    const { nodeName, stageName, nodeLabel, selectable, alwaysUseLatest, schemeIdList, version, tpl, executor_proxy, retryable, skippable, ignorable, autoRetry, timeoutConfig } = this.basicInfo
                    const constants = {}
                    Object.keys(this.subFlowForms).forEach(key => {
                        const constant = tools.deepClone(this.subFlowForms[key])
                        if (constant.show_type === 'show') {
                            constant.value = key in this.inputsParamValue ? tools.deepClone(this.inputsParamValue[key]) : constant.value
                            constant.need_render = key in this.inputsRenderConfig ? this.inputsRenderConfig[key] : true
                        }
                        constants[key] = constant
                    })
                    config = Object.assign({}, this.nodeConfig, {
                        constants,
                        version,
                        name: nodeName,
                        stage_name: stageName,
                        labels: nodeLabel,
                        template_id: tpl,
                        optional: selectable,
                        always_use_latest: alwaysUseLatest,
                        scheme_id_list: schemeIdList.filter(item => item),
                        retryable,
                        skippable,
                        error_ignorable: ignorable,
                        auto_retry: autoRetry,
                        timeout_config: timeoutConfig
                    })
                    if (this.common) {
                        config['executor_proxy'] = executor_proxy.join(',')
                    }
                } else {
                    const { ignorable, nodeName, stageName, nodeLabel, plugin, retryable, skippable, selectable, version, autoRetry, timeoutConfig, executor_proxy } = this.basicInfo
                    const data = {} // 标准插件节点在 activity 的 component.data 值
                    Object.keys(this.inputsParamValue).forEach(key => {
                        const formVal = this.inputsParamValue[key]
                        let hook = false
                        // 获取输入参数的勾选状态
                        if (this.$refs.inputParams && this.$refs.inputParams.hooked) {
                            hook = this.$refs.inputParams.hooked[key] || false
                        }
                        data[key] = {
                            hook, // 页面实际未用到这个字段，作为一个标识位更新，确保数据正确
                            need_render: key in this.inputsRenderConfig ? this.inputsRenderConfig[key] : true,
                            value: tools.deepClone(formVal)
                        }
                    })
                    // 第三方插件需手动设置plugin_code和plugin_version
                    if (this.isThirdParty) {
                        data['plugin_code'] = {
                            hook: false,
                            value: plugin
                        }
                        data['plugin_version'] = {
                            hook: false,
                            value: version
                        }
                    }
                    const component = {
                        code: this.isThirdParty ? 'remote_plugin' : plugin,
                        data,
                        version: this.isThirdParty ? '1.0.0' : version
                    }
                    config = Object.assign({}, this.nodeConfig, {
                        component,
                        retryable,
                        skippable,
                        name: nodeName,
                        stage_name: stageName,
                        labels: nodeLabel,
                        error_ignorable: ignorable,
                        optional: selectable,
                        auto_retry: autoRetry,
                        timeout_config: timeoutConfig
                    })
                    if (this.common) {
                        config['executor_proxy'] = executor_proxy.join(',')
                    }
                    delete config.can_retry
                    delete config.isSkipped
                }
                return config
            },
            /**
             * 同步节点配置面板数据到 store.activities
             */
            syncActivity () {
                const config = this.getNodeFullConfig()
                this.nodeConfig = config
                this.setActivities({ type: 'edit', location: config })
            },
            handleVariableChange () {
                // 如果变量已删除，需要删除变量是否输出的勾选状态
                this.$store.state.template.outputs.forEach(key => {
                    if (!(key in this.localConstants)) {
                        this.setOutputs({ changeType: 'delete', key })
                    }
                })
                // 设置全局变量面板icon小红点
                const localConstantKeys = Object.keys(this.localConstants)
                if (Object.keys(this.constants).length !== localConstantKeys.length) {
                    this.$emit('globalVariableUpdate', true)
                } else {
                    localConstantKeys.some(key => {
                        if (!(key in this.constants)) {
                            this.$emit('globalVariableUpdate', true)
                            return true
                        }
                    })
                }

                this.setConstants(this.localConstants)
            },
            /**
             * 获取标准插件生命周期状态
             */
            getAtomPhase () {
                let phase = ''
                let atom = this.atomList.find(group => group.code === this.basicInfo.plugin)
                atom = atom || this.isolationAtomConfig
                atom.list.some(item => {
                    if (item.version === (this.basicInfo.version || 'legacy')) {
                        phase = item.phase
                    }
                })
                return phase
            },
            isOutputsChanged () {
                const localOutputs = []
                const outputs = []
                Object.keys(this.localConstants).forEach(key => {
                    const item = this.localConstants[key]
                    if (item.source_type === 'component_outputs') {
                        localOutputs.push(item)
                    }
                })
                Object.keys(this.constants).forEach(key => {
                    const item = this.constants[key]
                    if (item.source_type === 'component_outputs') {
                        outputs.push(item)
                    }
                })
                return !tools.isDataEqual(localOutputs, outputs)
            },
            // 打开全局变量编辑面板
            openVariablePanel (variable = {}) {
                if (variable.key) {
                    this.variableData = variable
                } else {
                    this.variableData = {
                        custom_type: 'input',
                        desc: '',
                        form_schema: {},
                        index: Object.keys(this.constants).length + 1,
                        key: '',
                        name: '',
                        show_type: 'show',
                        source_info: {},
                        source_tag: 'input.input',
                        source_type: 'custom',
                        validation: '^.+$',
                        pre_render_mako: false,
                        value: '',
                        version: 'legacy'
                    }
                }
                this.isVariablePanelShow = true
            },
            beforeClose () {
                if (this.isViewMode) {
                    this.onClosePanel()
                    return true
                }
                if (this.isSelectorPanelShow) { // 当前为插件/子流程选择面板，但没有选择时，支持自动关闭
                    if (!(this.isSubFlow ? this.basicInfo.tpl : this.basicInfo.plugin)) {
                        this.onClosePanel()
                        return true
                    }
                }
                if (this.isVariablePanelShow) { // 变量编辑时，点击遮罩需要确认是否保存变量
                    this.$refs.variableEdit.handleMaskClick()
                    return false
                }
                if (!this.isDataChange && !this.isOutputsChanged()) {
                    this.onClosePanel()
                    return true
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.onClosePanel()
                        }
                    })
                    this.isSelectorPanelShow = false
                    return false
                }
            },
            onSaveConfig () {
                this.validate().then(result => {
                    if (result) {
                        ['stageName', 'nodeName'].forEach(item => {
                            this.basicInfo[item] = this.basicInfo[item].trim()
                        })
                        const { alwaysUseLatest, latestVersion, version, skippable, retryable, selectable: optional,
                                desc, nodeName, autoRetry, timeoutConfig, executor_proxy, ignorable
                        } = this.basicInfo
                        const nodeData = {
                            status: '',
                            skippable,
                            retryable,
                            optional,
                            auto_retry: autoRetry,
                            timeout_config: timeoutConfig,
                            isActived: false,
                            error_ignorable: ignorable
                        }
                        if (this.common) {
                            nodeData['executor_proxy'] = executor_proxy.join(',')
                        }
                        if (!this.isSubFlow) {
                            const phase = this.getAtomPhase()
                            nodeData.phase = phase
                        } else {
                            if (this.subFlowUpdated || alwaysUseLatest) {
                                this.setSubprocessUpdated({
                                    expired: false,
                                    subprocess_node_id: this.nodeConfig.id
                                })
                            }
                            if (!alwaysUseLatest && latestVersion && latestVersion !== version) {
                                this.setSubprocessUpdated({ expired: true, subprocess_node_id: this.nodeConfig.id })
                            }
                            const inputRef = this.$refs.inputParams
                            // 更新子流程已勾选的变量值
                            Object.keys(this.localConstants).forEach(key => {
                                const constantValue = this.localConstants[key]
                                const formValue = this.subFlowForms[key]
                                let hook = false
                                // 获取输入参数的勾选状态
                                if (inputRef && inputRef.hooked) {
                                    hook = inputRef.hooked[key] || false
                                }
                                if (constantValue.is_meta && formValue && hook) {
                                    const schema = formSchema.getSchema(formValue.key, this.inputs)
                                    constantValue['form_schema'] = schema
                                    constantValue.meta = formValue.meta
                                    // 如果之前选中的下拉项被删除了，则删除对应的值
                                    const curVal = constantValue.value
                                    const isMatch = curVal ? schema.attrs.items.find(item => item.value === curVal) : true
                                    constantValue.value = isMatch ? curVal : ''
                                }
                            })
                        }
                        this.syncActivity()
                        // 将第三方插件信息传给父级存起来
                        if (this.isThirdParty) {
                            const params = {
                                desc,
                                nodeName,
                                version,
                                list: tools.deepClone(this.versionList)
                            }
                            this.$parent.thirdPartyList[this.nodeId] = params
                        }
                        this.handleVariableChange() // 更新全局变量列表、全局变量输出列表、全局变量面板icon小红点
                        this.$emit('updateNodeInfo', this.nodeId, nodeData)
                        this.$emit('templateDataChanged')
                        this.$emit('close')
                    }
                })
            },
            onClosePanel (openVariablePanel) {
                this.$emit('updateNodeInfo', this.nodeId, { isActived: false })
                this.$emit('close', openVariablePanel)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.plugin-config {
    position: relative;
    height: calc(100vh - 198px);
    margin-top: 16px;
    /deep/.variable-collapse {
        height: calc(100% - 48px);
        overflow-y: auto;
        @include scrollbar;
        .bk-collapse-item-header {
            height: 32px;
            font-size: 12px;
            line-height: 32px;
            padding-left: 15px;
            font-weight: bold;
            background: #f0f1f5;
            .common-icon-next-triangle-shape {
                display: inline-block;
                color: #979ba5;
                margin: 0 10px 0 1px;
                transition: all .2s linear;
            }
            &:hover {
                .common-icon-next-triangle-shape {
                    color: #3a84ff;
                }
            }
        }
        .bk-collapse-item-active {
            .common-icon-next-triangle-shape {
                transform: rotate(90deg);
            }
        }
    }
    .btn-footer {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 8px 24px;
        background: #fafbfd;
        box-shadow: 0 -1px 0 0 #dcdee5;
        z-index: 10;
    }
    &::before {
        content: '';
        display: block;
        height: calc(100vh - 60px);
        width: calc(100vh);
        top: -98px;
        left: -100vh;
        background: black;
        position: absolute;
        z-index: 1;
        opacity: 0.1;
    }
    &.edit-mode {
        height: calc(100vh - 158px);
    }
}
</style>
