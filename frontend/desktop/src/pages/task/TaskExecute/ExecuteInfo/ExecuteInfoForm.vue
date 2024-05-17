<template>
    <section class="info-section" data-test-id="taskExecute_form_excuteInfo">
        <h4 class="common-section-title">{{ $t('基础信息') }}</h4>
        <ul class="operation-table">
            <li v-if="isSubProcessNode || isLegacySubProcess">
                <span class="th">{{ $t('流程模板') }}</span>
                <span v-if="templateName" class="td">
                    {{ templateName }}
                    <i class="commonicon-icon common-icon-jump-link" @click="onSkipSubTemplate"></i>
                </span>
                <span v-else class="td">
                    {{ '--' }}
                </span>
            </li>
            <template v-else>
                <li>
                    <span class="th">{{ $t('标准插件') }}</span>
                    <span class="td">{{ executeInfo.plugin_name || '--' }}</span>
                </li>
                <li>
                    <span class="th">{{ $t('插件版本') }}</span>
                    <span class="td">{{ executeInfo.plugin_version || '--' }}</span>
                </li>
            </template>
            <li>
                <span class="th">{{ $t('节点名称') }}</span>
                <span class="td">{{ templateConfig.name || '--' }}</span>
            </li>
            <li>
                <span class="th">{{ $t('步骤名称') }}</span>
                <span class="td">{{ templateConfig.stage_name || '--' }}</span>
            </li>
            <li v-if="isSubProcessNode || isLegacySubProcess">
                <span class="th">{{ $t('执行方案') }}</span>
                <span class="td">{{ schemeTextValue || '--' }}</span>
            </li>
            <li v-if="!isLegacySubProcess">
                <span class="th">{{ $t('失败处理') }}</span>
                <span class="error-handle-td td" v-if="templateConfig.error_ignorable || templateConfig.skippable || templateConfig.retryable || (templateConfig.auto_retry && templateConfig.auto_retry.enable)">
                    <template v-if="templateConfig.error_ignorable">
                        <span class="error-handle-icon"><span class="text">AS</span></span>
                        {{ $t('自动跳过') }};
                    </template>
                    <template v-if="templateConfig.skippable">
                        <span class="error-handle-icon"><span class="text">MS</span></span>
                        {{ $t('手动跳过') }};
                    </template>
                    <template v-if="templateConfig.retryable">
                        <span class="error-handle-icon"><span class="text">MR</span></span>
                        {{ $t('手动重试') }};
                    </template>
                    <template v-if="templateConfig.auto_retry && templateConfig.auto_retry.enable">
                        <span class="error-handle-icon"><span class="text">AR</span></span>
                        {{ $t('自动重试') + ' ' + templateConfig.auto_retry.times + ' ' + $t('次') + $t('，') + $t('间隔') + ' ' + templateConfig.auto_retry.interval + ' ' + $t('error_handle_秒') }}
                    </template>
                </span>
                <span v-else class="td">{{ '--' }}</span>
            </li>
            <li v-if="!isSubProcessNode && !isLegacySubProcess">
                <span class="th">{{ $t('超时控制') }}</span>
                <span class="td">{{ timeoutTextValue }}</span>
            </li>
            <li>
                <span class="th">{{ $t('是否可选') }}</span>
                <span class="td">{{ templateConfig.optional ? $t('是') : $t('否') }}</span>
            </li>
            <li v-if="isSubProcessNode || isLegacySubProcess">
                <span class="th">{{ $t('总是使用最新版本') }}</span>
                <span class="td">{{ !('always_use_latest' in componentValue) ? '--' : componentValue.always_use_latest ? $t('是') : $t('否') }}</span>
            </li>
        </ul>
        <template v-if="inputAndOutputWrapShow">
            <h4 class="common-section-title">{{ $t('输入参数') }}</h4>
            <div class="input-wrap" v-bkloading="{ isLoading: inputLoading, zIndex: 100 }">
                <template v-if="Array.isArray(inputs)">
                    <render-form
                        v-if="inputs.length > 0"
                        ref="renderForm"
                        :class="{ 'subflow-form': isLegacySubProcess }"
                        :scheme="inputs"
                        :hooked="hooked"
                        :constants="isSubProcessNode ? subflowForms : constants"
                        :form-option="option"
                        :form-data="inputsFormData"
                        :render-config="inputsRenderConfig">
                    </render-form>
                    <no-data v-else :message="$t('暂无参数')"></no-data>
                </template>
                <template v-else>
                    <jsonschema-input-params
                        v-if="inputs.properties && Object.keys(inputs.properties).length > 0"
                        :is-view-mode="true"
                        :inputs="inputs"
                        :value="inputsFormData">
                    </jsonschema-input-params>
                    <no-data v-else :message="$t('暂无参数')"></no-data>
                </template>
            </div>
            <h4 class="common-section-title">{{ $t('输出参数') }}</h4>
            <div class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading, zIndex: 100 }">
                <bk-table v-if="outputs.length" :data="outputList" :col-border="false" :row-class-name="getRowClassName">
                    <bk-table-column :label="$t('名称')" :width="180" prop="name"></bk-table-column>
                    <bk-table-column :label="$t('说明')">
                        <template slot-scope="props">
                            <div
                                v-if="props.row.description"
                                v-bk-overflow-tips>
                                {{ props.row.description }}
                            </div>
                            <span v-else>--</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="Key" class-name="param-key" :width="260">
                        <template slot-scope="props">
                            <div v-bk-overflow-tips :style="{ color: props.row.hooked ? '#3a84ff' : '#63656e' }">{{ props.row.key }}</div>
                            <span class="hook-icon-wrap">
                                <i
                                    :class="['common-icon-variable-cite hook-icon', {
                                        actived: props.row.hooked,
                                        disabled: true
                                    }]"
                                    v-bk-tooltips="{
                                        content: props.row.hooked ? $t('取消变量引用') : $t('设置为变量'),
                                        placement: 'bottom',
                                        zIndex: 3000
                                    }">
                                </i>
                            </span>
                        </template>
                    </bk-table-column>
                </bk-table>
                <no-data v-else :message="$t('暂无参数')"></no-data>
            </div>
        </template>
    </section>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import JsonschemaInputParams from '@/pages/template/TemplateEdit/NodeConfig/JsonschemaInputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        components: {
            RenderForm,
            JsonschemaInputParams,
            NoData
        },
        props: {
            nodeActivity: {
                type: Object,
                default: () => ({})
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            constants: {
                type: Object,
                default: () => ({})
            },
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            isThirdPartyNode: {
                type: Boolean,
                default: false
            },
            thirdPartyNodeCode: {
                type: String,
                default: ''
            },
            isSubProcessNode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                templateName: '',
                schemeTextValue: '',
                templateConfig: {},
                inputs: [],
                outputs: [],
                hooked: {},
                option: {
                    showGroup: true,
                    showHook: true,
                    showLabel: true,
                    showVarList: true,
                    formEdit: false
                },
                inputsFormData: {},
                inputsRenderConfig: {},
                subflowForms: {},
                taskNodeLoading: false,
                subflowLoading: false,
                constantsLoading: false
            }
        },
        computed: {
            ...mapState('project', {
                'project_id': state => state.project_id,
                'projectName': state => state.projectName
            }),
            ...mapState({
                'pluginConfigs': state => state.atomForm.config,
                'pluginOutput': state => state.atomForm.output
            }),
            timeoutTextValue () {
                const timeoutConfig = this.nodeActivity['timeout_config']
                if (!timeoutConfig || !timeoutConfig.enable) return '--'
                const actionText = timeoutConfig.action === 'forced_fail' ? i18n.t('强制终止') : i18n.t('强制终止后跳过')
                return i18n.t('超时') + ' ' + timeoutConfig.seconds + ' ' + i18n.tc('秒', 0) + i18n.t('后') + i18n.t('则') + actionText
            },
            componentValue () {
                if (this.isSubProcessNode) {
                    return this.nodeActivity.component.data.subprocess.value
                }
                return this.nodeActivity
            },
            inputLoading () {
                return this.taskNodeLoading || this.subflowLoading || this.constantsLoading
            },
            outputLoading () {
                return this.taskNodeLoading || this.subflowLoading
            },
            outputList () {
                return this.getOutputsList()
            },
            inputAndOutputWrapShow () {
                const { original_template_id, type } = this.nodeActivity
                // 普通任务节点展示/该功能上线后的子流程任务展示
                return (!this.isSubProcessNode && type !== 'SubProcess')
                    || (original_template_id && !this.templateConfig.isOldData)
            },
            isLegacySubProcess () {
                return !this.isSubProcessNode && this.nodeActivity && this.nodeActivity.type === 'SubProcess'
            }
        },
        mounted () {
            $.context.exec_env = 'NODE_EXEC_DETAIL'
            this.initData()
            if (this.nodeActivity.original_template_id) {
                this.getTemplateData()
            }
        },
        beforeDestroy () {
            $.context.exec_env = ''
        },
        methods: {
            ...mapActions('template/', [
                'getTemplatePublicData',
                'getCommonTemplatePublicData'
            ]),
            ...mapActions('task', [
                'loadSubflowConfig',
                'getNodeSnapshotConfig'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            // 初始化节点数据
            async initData () {
                try {
                    // 获取对应模板配置
                    const tplConfig = await this.getNodeSnapshotConfig(this.nodeDetailConfig)
                    this.templateConfig = tplConfig.data || { ...this.nodeActivity, isOldData: true } || {}
                    if (this.isSubProcessNode || this.nodeActivity.type === 'SubProcess') { // 子流程任务节点
                        // tplConfig.data为null为该功能之前的旧数据，没有original_template_id字段的，不调接口
                        if (!tplConfig.data || !this.nodeActivity.original_template_id) {
                            return
                        }
                        const forms = {}
                        const renderConfig = {}
                        const constants = this.templateConfig.constants || {}
                        Object.keys(constants).forEach(key => {
                            const form = constants[key]
                            if (form.show_type === 'show') {
                                forms[key] = form
                                renderConfig[key] = 'need_render' in form ? form.need_render : true
                            }
                        })
                        await this.getSubflowDetail(this.templateConfig.version)
                        this.inputs = await this.getSubflowInputsConfig()
                        this.inputsFormData = this.getSubflowInputsValue(forms)
                        this.inputsRenderConfig = renderConfig
                    } else { // 普通任务节点
                        const { component } = this.nodeActivity
                        const paramsVal = {}
                        const renderConfig = {}
                        Object.keys(component.data || {}).forEach(key => {
                            const val = tools.deepClone(component.data[key].value)
                            paramsVal[key] = val
                            renderConfig[key] = 'need_render' in component.data[key] ? component.data[key].need_render : true
                        })
                        this.inputsFormData = paramsVal
                        this.inputsRenderConfig = renderConfig
                        await this.getPluginDetail()
                    }
                    // 获取输入参数的勾选状态
                    this.hooked = this.getFormsHookState()
                } catch (error) {
                    console.warn(error)
                }
            },
            // 获取输入参数勾选状态
            getFormsHookState () {
                const hooked = {}
                const keys = Object.keys(this.constants)
                Array.isArray(this.inputs) && this.inputs.forEach(form => {
                    // 已勾选到全局变量中, 判断勾选的输入参数生成的变量及自定义全局变量source_info是否包含该节点对应表单tag_code
                    // 可能存在表单勾选时已存在相同key的变量，选择复用自定义变量
                    const isHooked = keys.some(item => {
                        const varItem = this.constants[item]
                        if (['component_inputs', 'custom'].includes(varItem.source_type)) {
                            const sourceInfo = varItem.source_info[this.nodeActivity.id]
                            if (sourceInfo && sourceInfo.includes(form.tag_code)) {
                                return true
                            }
                        }
                    })
                    hooked[form.tag_code] = isHooked
                })
                return hooked
            },
            /**
             * 加载子流程任务节点输入、输出、版本配置项
             */
            async getSubflowDetail (version = '') {
                this.subflowLoading = true
                try {
                    const params = {
                        template_id: this.nodeActivity.original_template_id,
                        scheme_id_list: this.nodeActivity.schemeIdList || [],
                        version
                    }
                    if (this.componentValue.template_source === 'common') {
                        params.template_source = 'common'
                    } else {
                        params.project_id = this.project_id
                    }
                    const resp = await this.loadSubflowConfig(params)
                    // 子流程的输入参数包括流程引用的变量、自定义变量和未被引用的变量
                    this.subflowForms = { ...resp.data.pipeline_tree.constants, ...resp.data.custom_constants, ...resp.data.constants_not_referred }

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
                    this.subflowLoading = false
                }
            },

            /**
             * 加载子流程输入参数表单配置项
             * 遍历每个非隐藏的全局变量，由 source_tag、coustom_type 字段确定需要加载的标准插件
             * 同时根据 source_tag 信息获取全局变量对应标准插件的某一个表单配置项
             *
             * @return {Array} 每个非隐藏全局变量对应表单配置项组成的数组
             */
            async getSubflowInputsConfig () {
                this.constantsLoading = true
                const inputs = []
                const variables = Object.keys(this.subflowForms)
                    .map(key => this.subflowForms[key])
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
                this.constantsLoading = false
                return inputs
            },
            /**
             * 加载标准插件表单配置项文件
             */
            async getAtomConfig (config) {
                const { plugin, version, classify, name, isThird } = config
                const project_id = this.componentValue.template_source === 'common' ? undefined : this.project_id
                try {
                    // 先取标准节点缓存的数据
                    const pluginGroup = this.pluginConfigs[plugin]
                    if (pluginGroup && pluginGroup[version]) {
                        return pluginGroup[version]
                    }
                    // 第三方插件
                    if (isThird) {
                        await this.getThirdConfig(plugin, version)
                    } else {
                        await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id, scope: 'task' })
                        this.outputs = this.pluginOutput[plugin][version]
                    }
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.log(e)
                }
            },
            // 第三方插件输入输出配置
            async getThirdConfig (plugin, version) {
                try {
                    const resp = await this.loadPluginServiceDetail({
                        plugin_code: plugin,
                        plugin_version: version,
                        with_app_detail: true
                    })
                    if (!resp.result) return
                    // 获取参数
                    const { outputs: respOutputs, forms, inputs } = resp.data
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

                    // 输出参数
                    const outputs = []
                    // 获取第三方插件公共输出参数
                    if (!this.pluginOutput['remote_plugin']) {
                        await this.loadAtomConfig({ atom: 'remote_plugin', version: '1.0.0' })
                    }
                    const storeOutputs = this.pluginOutput['remote_plugin']['1.0.0']
                    for (const [key, val] of Object.entries(respOutputs.properties)) {
                        outputs.push({
                            name: val.title || key,
                            key,
                            type: val.type,
                            schema: { description: val.description }
                        })
                    }
                    this.outputs = [...storeOutputs, ...outputs]
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 获取子流程任务节点输入参数值
             */
            getSubflowInputsValue (forms, oldForms = {}) {
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
                return Object.keys(this.constants).some(key => {
                    const varItem = this.constants[key]
                    const sourceInfo = varItem.source_info[this.nodeId]
                    return sourceInfo && sourceInfo.includes(form.tag_code)
                })
            },
            /**
             * 加载标准插件节点输入参数表单配置项，获取输出参数列表
             */
            async getPluginDetail () {
                const { component_code, componentData } = this.nodeDetailConfig
                const plugin = this.isThirdPartyNode ? this.thirdPartyNodeCode : component_code
                const version = this.isThirdPartyNode ? componentData.plugin_version.value : this.nodeDetailConfig.version
                this.taskNodeLoading = true
                try {
                    // 获取输入输出参数
                    this.inputs = await this.getAtomConfig({ plugin, version, isThird: this.isThirdPartyNode }) || []
                    if (!this.isThirdPartyNode) {
                        this.outputs = this.pluginOutput[plugin][version]
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.taskNodeLoading = false
                }
            },
            // 获取输出变量列表
            getOutputsList () {
                const list = []
                const varKeys = Object.keys(this.constants)
                this.outputs.forEach(param => {
                    let key = param.key
                    const isHooked = varKeys.some(item => {
                        const varItem = this.constants[item]
                        if (varItem.source_type === 'component_outputs') {
                            const sourceInfo = varItem.source_info[this.nodeActivity.id]
                            if (sourceInfo && sourceInfo.includes(param.key)) {
                                key = item
                                return true
                            }
                        }
                    })
                    list.push({
                        key,
                        name: param.name,
                        description: param.schema ? param.schema.description : '--',
                        version: param.version,
                        status: param.status,
                        hooked: isHooked
                    })
                })
                return list
            },
            getRowClassName ({ row }) {
                return row.status || ''
            },
            async getTemplateData () {
                const { template_source, scheme_id_list: schemeIds } = this.componentValue
                const data = {
                    templateId: this.nodeActivity.original_template_id,
                    project__id: this.project_id
                }
                let templateData = {}
                if (template_source === 'common') {
                    templateData = await this.getCommonTemplatePublicData(data)
                } else {
                    templateData = await this.getTemplatePublicData(data)
                }
                this.templateName = templateData.data.name
                this.schemeTextValue = templateData.data.schemes.reduce((acc, cur) => {
                    if (schemeIds.includes(cur.id)) {
                        acc = acc ? acc + ',' + cur.name : cur.name
                    }
                    return acc
                }, '')
            },
            onSkipSubTemplate () {
                const { href } = this.$router.resolve({
                    name: this.componentValue.template_source === 'common' ? 'projectCommonTemplatePanel' : 'templatePanel',
                    params: { type: 'view' },
                    query: { template_id: this.nodeActivity.original_template_id }
                })
                window.open(href, '_blank')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .operation-table {
        font-size: 12px;
        border: 1px solid #dcdee5 !important;
        border-bottom: none !important;
        margin-bottom: 32px;
        li {
            display: flex;
            height: 42px;
            line-height: 41px;
            color: #63656e;
            border-bottom: 1px solid #dcdee5;
            .th {
                width: 20%;
                font-weight: 400;
                color: #313238;
                padding-left: 12px;
                border-right: 1px solid #dcdee5;
                background: #fafbfd;
            }
            .td {
                flex: 1;
                position: relative;
                padding-left: 12px;
            }
        }
    }
    .error-handle-icon {
        display: inline-block;
        line-height: 12px;
        color: #ffffff;
        background: #979ba5;
        border-radius: 2px;
        .text {
            display: inline-block;
            font-size: 12px;
            transform: scale(0.8);
        }
    }
    .common-icon-jump-link {
        position: absolute;
        top: 15px;
        right: 10px;
        color: #3a84ff;
        cursor: pointer;
    }
    .input-wrap {
        margin-bottom: 32px;
    }
    .hook-icon-wrap {
        position: absolute;
        right: 22px;
        top: 9px;
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        background: #f0f1f5;
        text-align: center;
        border-radius: 2px;
        .hook-icon {
            font-size: 18px;
            color: #979ba5;
            cursor: pointer;
            &.disabled {
                color: #c4c6cc;
                cursor: not-allowed;
            }
            &.actived {
                color: #3a84ff;
            }
        }
    }
    .no-data-wrapper {
        padding-top: 20px;
    }
    /deep/.render-form {
        >.rf-form-item {
            .rf-group-name {
                display: none;
            }
            .rf-tag-label {
                width: 20%;
            }
            .rf-tag-form {
                margin-left: 20%;
            }

            .hide-render-icon {
                top: 0;
            }
        }
        .rf-form-group {
            .rf-group-name {
                display: none;
            }
            .rf-tag-hook {
                top: 0;
            }
        }
        >.rf-form-group {
            .form-item-group >.rf-form-item {
                .rf-tag-label {
                    width: 20%;
                }
                .rf-tag-form {
                    margin-left: 20%;
                }
            }
        }
        .rf-tag-label {
            width: 20%;
            padding-right: 24px;
            .label {
                white-space: initial;
            }
            .required {
                position: absolute;
                top: 2px;
                right: 15px;
            }
        }
    }
    /deep/.subflow-form {
        .rf-form-group {
            .rf-group-name {
                display: block;
                width: 20%;
                padding-right: 24px;
                text-align: right;
                .scheme-name {
                    font-size: 12px;
                }
            }
            .rf-has-hook {
                .rf-tag-label {
                    display: none;
                }
            }
            .rf-tag-hook {
                top: 0;
            }
        }
        >.rf-form-group {
            .rf-group-name {
                float: left;
            }
            .form-item-group {
                margin-left: 20%;
            }
        }
        .form-item-group {
            padding: 16px;
            margin-right: 40px;
            background: #f5f7fa;
            .rf-tag-form {
                margin-right: 0;
            }
            .rf-form-item {
                .rf-tag-label {
                    display: flex;
                    text-align: left;
                    color: #63656e;
                    width: 100px;
                    line-height: 20px;
                    padding-right: 10px;
                    margin-top: 6px;
                    .label {
                        white-space: initial;
                    }
                    .required {
                        position: initial;
                    }
                }
                .rf-tag-form {
                    margin-left: 100px;
                }
                &:last-child {
                    margin-bottom: 0;
                }
            }
            .form-item-group {
                padding: 0;
                margin-right: 0;
            }
            .tag-ip-selector-wrap,
            .resource-allocation {
                border: none;
                padding: 0;
            }
        }
        .show-render {
            .form-item-group {
                margin-right: 64px;
            }
        }
    }

</style>
