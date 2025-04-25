<template>
    <div class="batch-update-dialog-content">
        <div class="header-wrapper">
            <h4>{{ $t('批量更新子流程') + $t('（') + expiredTplNum + $t('）') }}</h4>
            <div class="legend-area">
                <span class="legend-item delete">{{ $t('删除') }}</span>
                <span class="legend-item add">{{ $t('新增') }}</span>
            </div>
            <i class="bk-dialog-close bk-icon icon-close" @click="onCloseDialog(false)"></i>
        </div>
        <bk-alert ref="diffAlert" type="warning" style="margin: 10px;" :show-icon="false">
            <div class="diff-alert" slot="title">
                <span>{{ $t('子流程更新时，如果新旧版本存在相同表单，表单数据会默认取原表单数据') }}</span>
            </div>
        </bk-alert>
        <div class="subflow-form-wrap" v-bkloading="{ isLoading: subflowFormsLoading, opacity: 1 }">
            <section
                v-for="subflow in subflowForms"
                :key="subflow.id"
                class="subflow-item">
                <div class="header-area" @click.self="subflow.fold = !subflow.fold">
                    <bk-checkbox v-model="subflow.checked"></bk-checkbox>
                    <h3>{{ subflow.name }}</h3>
                    <i :class="['bk-icon', 'icon-angle-up', 'fold-icon', subflow.fold ? 'fold' : '']" @click="subflow.fold = !subflow.fold"></i>
                </div>
                <div v-show="!subflow.fold" class="form-area">
                    <!-- 当前版本表单 -->
                    <div class="current-form">
                        <div class="version-tag">{{ $t('原版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.currentForm.inputsConfig.length > 0"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :editable="false"
                                    :scheme="subflow.currentForm.inputsConfig"
                                    :version="subflow.currentForm.version"
                                    :subflow-forms="subflow.currentForm.form"
                                    :value="subflow.currentForm.inputsValue"
                                    :render-config="subflow.currentForm.inputsRenderConfig"
                                    :constants="$store.state.template.constants">
                                </input-params>
                                <no-data v-else :message="$t('暂无参数')"></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.currentForm.outputs.length > 0"
                                    :constants="$store.state.template.constants"
                                    :params="subflow.currentForm.outputs"
                                    :hook="false"
                                    :version="subflow.currentForm.version"
                                    :node-id="subflow.id">
                                </output-params>
                                <no-data v-else :message="$t('暂无参数')"></no-data>
                            </div>
                        </section>
                    </div>
                    <!-- 新版本表单 -->
                    <div class="latest-form">
                        <div class="version-tag lastest">{{ $t('待更新版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.latestForm.inputsConfig.length > 0"
                                    ref="inputParams"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :scheme="subflow.latestForm.inputsConfig"
                                    :version="subflow.latestForm.version"
                                    :subflow-forms="subflow.latestForm.form"
                                    :value="subflow.latestForm.inputsValue"
                                    :render-config="subflow.latestForm.inputsRenderConfig"
                                    :constants="localConstants"
                                    @hookChange="onHookChange"
                                    @renderConfigChange="onRenderConfigChange(subflow.id, $event)"
                                    @update="updateInputsValue(subflow.id, $event)">
                                </input-params>
                                <no-data v-else :message="$t('暂无参数')"></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.latestForm.outputs.length"
                                    ref="outputParams"
                                    :constants="localConstants"
                                    :params="subflow.latestForm.outputs"
                                    :version="subflow.latestForm.version"
                                    :node-id="subflow.id"
                                    @hookChange="onHookChange">
                                </output-params>
                                <no-data v-else :message="$t('暂无参数')"></no-data>
                            </div>
                        </section>
                    </div>
                </div>
            </section>
        </div>
        <div class="bk-dialog-footer">
            <bk-checkbox
                class="selecte-all"
                :indeterminate="selectedTplNum > 0 && selectedTplNum < expiredTplNum"
                :value="selectedTplNum > 0 && selectedTplNum === expiredTplNum"
                @change="onSelectedAllChange">
                {{ $t('全选') }}
            </bk-checkbox>
            <div class="action-btns">
                <span v-if="selectedTplNum > 0" class="selected-tips">{{ $t('已选择') + selectedTplNum + $t('个') + $t('待更新的子流程') }}</span>
                <bk-button
                    theme="primary"
                    style="margin-right: 8px;"
                    :disabled="subflowFormsLoading || !selectedTplNum"
                    @click="onConfirm">
                    {{ isSourceList ? $t('立即更新并保存') : $t('批量更新') }}
                </bk-button>
                <bk-button
                    :theme="isSourceList ? 'primary' : 'default'"
                    @click="onCancel">
                    {{ isSourceList ? $t('跳转到流程') : $t('取消') }}
                </bk-button>
            </div>
        </div>
        <bk-dialog
            width="480"
            ext-cls="cancel-global-variable-dialog"
            header-position="left"
            :mask-close="false"
            :value="isCancelGloVarDialogShow"
            :cancel-text="$t('取消')"
            :title="$t('取消变量引用')">
            <p style="word-break: break-all;">{{ $t('全局变量【 x 】的引用数已为 0。如果不再使用，可立即删除变量; 也可以稍后在全局变量面板中删除', { key: unhookingVarForm.key })}}</p>
            <template slot="footer">
                <bk-button theme="primary" @click="varReferenceDialogClick(true)">{{ $t('删除变量') }}</bk-button>
                <bk-button @click="varReferenceDialogClick(false)">{{ $t('以后再说') }}</bk-button>
            </template>
        </bk-dialog>
    </div>
</template>
<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import i18n from '@/config/i18n/index.js'
    import formSchema from '@/utils/formSchema.js'
    import InputParams from './NodeConfig/InputParams.vue'
    import OutputParams from './NodeConfig/OutputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'BatchUpdateDialog',
        components: {
            InputParams,
            OutputParams,
            NoData
        },
        props: {
            projectId: [Number, String],
            common: {
                type: String,
                default: ''
            },
            list: {
                type: Array,
                default () {
                    return []
                }
            },
            source: {
                type: String,
                default: ''
            },
            templateId: [Number, String]
        },
        data () {
            return {
                subflowFormsLoading: false,
                subflowForms: [],
                localConstants: tools.deepClone(this.$store.state.template.constants), // 全局变量列表，用来维护当前面板勾选、反勾选后全局变量的变化情况，保存时更新到 store
                isCancelGloVarDialogShow: false,
                variableCited: {},
                unhookingVarForm: {} // 正被取消勾选的表单配置
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'gateways': state => state.template.gateways,
                'internalVariable': state => state.template.internalVariable,
                'pluginConfigs': state => state.atomForm.config
            }),
            expiredTplNum () {
                return this.list.filter(item => item.expired).length
            },
            selectedTplNum () {
                return this.subflowForms.filter(item => item.checked).length
            },
            isSourceList () {
                return this.source === 'list'
            }
        },
        created () {
            this.loadSubflowForms()
        },
        methods: {
            ...mapMutations('template/', [
                'setActivities',
                'setConstants',
                'setOutputs',
                'setSubprocessUpdated'
            ]),
            ...mapActions('template', [
                'getBatchForms',
                'getVariableCite'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            // 批量加载待更新流程模版当前版本和最新版本表单数据
            async loadSubflowForms () {
                try {
                    this.subflowFormsLoading = true
                    const tpls = []
                    const nodeList = Object.values(this.activities)
                    this.list.map(item => {
                        if (item.expired) {
                            const nodeInfo = nodeList.find(node => node.id === item.subprocess_node_id) || {}
                            const template_source = nodeInfo.template_source && nodeInfo.template_source === 'common' ? 'common' : 'project'
                            tpls.push({
                                id: item.template_id,
                                nodeId: item.subprocess_node_id,
                                version: item.version,
                                scheme_id_list: item.scheme_id_list,
                                template_source
                            })
                        }
                    })
                    const res = await this.getBatchForms({ tpls, projectId: this.projectId })
                    const subflowForms = []
                    tpls.forEach(tpl => {
                        const activity = this.activities[tpl.nodeId]
                        const { name, id, template_id, version } = activity
                        const latestForm = this.getNodeFormData(res.data[template_id].find(item => item.is_current))
                        const currentForm = this.getNodeFormData(res.data[template_id].find(item => item.version === version))

                        for (const key in latestForm.form) {
                            const latestFormItem = latestForm.form[key]
                            latestFormItem.id = id
                            if (!currentForm.form.hasOwnProperty(key) || latestFormItem.version !== currentForm.form[key].version) {
                                latestFormItem.status = 'added' // 标记最新版本子流程输入参数表单项是否为新增
                            }
                        }
                        latestForm.outputs.forEach(latestFormItem => {
                            const currentFormItem = currentForm.outputs.find(item => item.key === latestFormItem.key && item.version === latestFormItem.version)
                            latestFormItem.id = id
                            if (!currentFormItem) {
                                latestFormItem.status = 'added' // 标记最新版本子流程输出参数表单项是否为新增
                            }
                        })
                        for (const key in currentForm.form) {
                            const currentFormItem = currentForm.form[key]
                            if (!latestForm.form.hasOwnProperty(key) || currentFormItem.version !== latestForm.form[key].version) {
                                currentFormItem.status = 'deleted' // 标记当前版本子流程输入参数表单项是否被删除
                            }
                        }
                        currentForm.outputs.forEach(currentFormItem => {
                            const latestFormItem = latestForm.outputs.find(item => item.key === currentFormItem.key && item.version === currentFormItem.version)
                            if (!latestFormItem) {
                                currentFormItem.status = 'deleted' // 标记当前版本子流程输出参数表单项是否被删除
                            }
                        })
                        subflowForms.push({
                            name,
                            id,
                            template_id,
                            latestForm,
                            currentForm,
                            loading: false, // 输入参数表单是否在加载中
                            checked: false, // 是否选中更新
                            fold: false // 是否收起
                        })
                    })
                    this.subflowForms = subflowForms
                    this.getTplsFormConfig(subflowForms)
                } catch (e) {
                    console.error(e)
                } finally {
                    this.subflowFormsLoading = false
                }
            },
            // 加载当前版本和待更新版本流程的输入参数表单配置项
            async getTplsFormConfig (subflowForms) {
                const uniqueConfigMap = {}
                const variables = []
                const variablesConfig = {}
                const allSubflowInputForms = []
                subflowForms.forEach(subflow => {
                    const latestFormArr = Object.keys(subflow.latestForm.form).map(key => subflow.latestForm.form[key]).sort((a, b) => a.index - b.index)
                    const currentFormArr = Object.keys(subflow.currentForm.form).map(key => subflow.currentForm.form[key]).sort((a, b) => a.index - b.index)
                    allSubflowInputForms.push({
                        id: subflow.id,
                        latestFormArr,
                        currentFormArr
                    })
                })
                allSubflowInputForms.forEach(subflowItem => {
                    [...subflowItem.latestFormArr, ...subflowItem.currentFormArr].forEach(item => {
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        if (!uniqueConfigMap[`${formKey}_${item.version}`]) {
                            uniqueConfigMap[`${formKey}_${item.version}`] = true
                            item.id = subflowItem.id
                            variables.push(item)
                        }
                    })
                })
                await Promise.all(variables.map(async (variable) => {
                    const formKey = variable.custom_type || variable.source_tag.split('.')[0]
                    const { name, atom, classify } = atomFilter.getVariableArgs(variable)
                    const version = variable.version || 'legacy'
                    const isThird = Boolean(variable.plugin_code)
                    const config = await this.getAtomConfig({ plugin: atom, version, classify, name, isThird })
                    variablesConfig[`${formKey}_${variable.version}`] = config
                }))

                allSubflowInputForms.forEach((subflow, index) => {
                    const { constants } = this.activities[subflow.id]
                    subflow.latestFormArr.forEach(item => {
                        let formValue = item.value
                        const oldVariable = constants[item.key]
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        const formConfig = this.getSubflowInputFormItemConfig(item, variablesConfig[`${formKey}_${item.version}`])
                        this.subflowForms[index].latestForm.inputsConfig.push(formConfig)

                        // 节点当前输入参数表单存在与最新版本输入参数 key相同，且custom_type 或 source_tag 相同变量，则复用当前值
                        if (oldVariable && (item.custom_type === oldVariable.custom_type || item.source_tag === oldVariable.source_tag)) {
                            formValue = oldVariable.value
                        }
                        this.subflowForms[index].latestForm.inputsValue[item.key] = tools.deepClone(formValue)
                        this.$set(this.subflowForms[index].latestForm.inputsRenderConfig, item.key, true)
                    })
                    subflow.currentFormArr.forEach(item => {
                        const formKey = item.custom_type || item.source_tag.split('.')[0]
                        const formConfig = this.getSubflowInputFormItemConfig(item, variablesConfig[`${formKey}_${item.version}`])
                        this.subflowForms[index].currentForm.inputsConfig.push(formConfig)
                        this.subflowForms[index].currentForm.inputsValue[item.key] = tools.deepClone(constants[item.key].value)
                        const renderVal = 'need_render' in constants[item.key] ? constants[item.key].need_render : true
                        this.$set(this.subflowForms[index].currentForm.inputsRenderConfig, item.key, renderVal)
                    })
                })
            },
            async getAtomConfig (config) {
                const { plugin, version, classify, name, isThird } = config
                const project_id = this.common ? undefined : this.project_id
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
                        const { app, forms } = resp.data
                        // 获取host
                        const { host } = window.location
                        const hostUrl = app.urls.find(item => item.includes(host)) || app.url
                        $.context.bk_plugin_api_host[plugin] = hostUrl + '/'
                        // 输入参数
                        $.atoms[plugin] = {}
                        const renderFrom = forms.renderform
                        /* eslint-disable-next-line */
                        eval(renderFrom)
                    } else {
                        await this.loadAtomConfig({ atom: plugin, version, classify, name, project_id })
                    }
                    const config = $.atoms[plugin]
                    return config
                } catch (e) {
                    console.error(e)
                }
            },
            getNodeFormData (tplForm) {
                const { form, outputs, version } = tplForm
                const inputForms = {}
                for (const key in form) { // 去掉隐藏变量
                    const item = form[key]
                    if (item.show_type === 'show') {
                        inputForms[key] = tools.deepClone(item)
                    }
                }
                const outputParams = Object.keys(outputs).map(item => { // 输出参数
                    const output = outputs[item]
                    return {
                        name: output.name,
                        key: output.key,
                        version: output.hasOwnProperty('version') ? output.version : 'legacy'
                    }
                })
                return {
                    form: inputForms,
                    outputs: outputParams,
                    inputsConfig: [],
                    inputsValue: {},
                    inputsRenderConfig: {},
                    version
                }
            },
            getSubflowInputFormItemConfig (variable, atomConfig) {
                const { tagCode } = atomFilter.getVariableArgs(variable)
                let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                if (variable.is_meta || formItemConfig.meta_transform) {
                    formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                    if (!variable.meta) {
                        variable.meta = tools.deepClone(variable)
                        variable.value = formItemConfig.attrs.value
                    }
                }
                formItemConfig.attrs.name = variable.name
                if (formItemConfig.type === 'combine') {
                    formItemConfig.name = variable.name
                }
                formItemConfig.tag_code = variable.key
                formItemConfig.status = variable.status
                // 自定义输入框变量正则校验添加到插件配置项
                if (['input', 'textarea'].includes(variable.custom_type) && variable.validation !== '') {
                    formItemConfig.attrs.validation.push({
                        type: 'regex',
                        args: variable.validation,
                        error_message: i18n.t('默认值不符合正则规则：') + variable.validation
                    })
                }
                return formItemConfig
            },
            onSelectedAllChange (val) {
                this.subflowForms.forEach(item => {
                    item.checked = val
                })
            },
            // 是否渲染豁免切换
            onRenderConfigChange (id, data) {
                const [key, val] = data
                const subflow = this.subflowForms.find(item => item.id === id)
                subflow.latestForm.inputsRenderConfig[key] = val
            },
            // 输入、输出参数勾选状态变化
            onHookChange (type, data) {
                if (type === 'create') {
                    this.$set(this.localConstants, data.key, data)
                } else {
                    this.setVariableSourceInfo(data)
                }
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
                        this.variableCited = await this.getVariableCitedData(id) || {}
                    }
                    const { activities, conditions, constants } = this.variableCited[key]
                    const citedNum = activities.length + conditions.length + constants.length
                    if (citedNum <= 1) {
                        this.varReferenceDialogClick(true)
                    } else {
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
                        const index = this.subflowForms.findIndex(item => item.id === id)
                        const refDoms = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                        refDoms && refDoms[index].setFormData()
                    }
                }
            },
            async getVariableCitedData (nodeId) {
                try {
                    const nodeConfig = tools.deepClone(this.activities[nodeId])
                    const nodeForm = this.subflowForms.find(item => item.id === nodeId)
                    nodeConfig['constants'] = nodeForm.latestForm.form
                    const activities = Object.assign({}, this.activities, { [nodeId]: nodeConfig })
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
            varReferenceDialogClick (confirm) {
                const { key, source, id } = this.unhookingVarForm
                if (confirm) {
                    const constant = this.localConstants[key]
                    for (const key in this.localConstants) {
                        const varItem = this.localConstants[key]
                        if (varItem.index > constant.index) {
                            varItem.index = varItem.index - 1
                        }
                    }
                    this.$delete(this.localConstants, key)
                } else {
                    const constant = this.localConstants[key]
                    constant.source_info = {}
                }
                const index = this.subflowForms.findIndex(item => item.id === id)
                const refDoms = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                refDoms && refDoms[index].setFormData({ ...this.unhookingVarForm })
                this.isCancelGloVarDialogShow = false
            },
            updateInputsValue (subflowId, value) {
                const subflow = this.subflowForms.find(item => item.id === subflowId)
                subflow.latestForm.inputsValue = value
            },
            /**
             * 统一处理全局变量的字段信息
             * 1.删除全局变量source_info对应的引用情况（如果source_info为空，则需要删除变量）：
             * a.子流程节点未被选择，输入输出表单在当前版本未被勾选，在最新版本勾选
             * b.子流程节点被选择，输入输出表单在当前版本勾选，但是在最新版本中该对应表单被删除
             * 2.增加全局变量source_info的引用（如果变量被删除，则需要还原）：
             * a.子流程节点未被选择，输入输出表单在当前版本被勾选，在最新版本未被勾选
             */
            handleVariableChange () {
                const constants = {}
                Object.keys(this.$store.state.template.constants).forEach(key => {
                    if (!this.localConstants[key]) { // 注释2.a场景，当前版本全局变量被删除
                        const varItem = tools.deepClone(this.$store.state.template.constants[key])
                        const { source_type, source_info } = varItem
                        const sInfo = {}
                        if (['component_inputs', 'component_outputs'].includes(source_type)) {
                            Object.keys(source_info).forEach(id => {
                                if (this.subflowForms.find(subflow => subflow.id === id && !subflow.checked)) {
                                    sInfo[id] = source_info[id]
                                }
                            })
                        }
                        if (Object.keys(sInfo).length > 0) {
                            varItem.source_info = sInfo
                            constants[key] = varItem
                        }
                    }
                })
                Object.keys(this.localConstants).forEach(key => {
                    const varItem = tools.deepClone(this.localConstants[key]) // 最新版本变量
                    const curVar = this.$store.state.template.constants[key] // 当前版本key相同的变量
                    const { source_type, source_info } = varItem
                    if (['component_inputs', 'component_outputs'].includes(source_type)) {
                        this.subflowForms.forEach((subflow, index) => {
                            if (source_info[subflow.id]) { // 该节点最新版本输入输出参数有勾选
                                source_info[subflow.id].slice(0).forEach(nodeFormItem => {
                                    // 注释 1.a 场景
                                    if (!subflow.checked && (!curVar || !curVar.source_info || !curVar.source_info[subflow.id] || !curVar.source_info[subflow.id].includes(nodeFormItem))) {
                                        if (source_info[subflow.id].length === 1) {
                                            delete source_info[subflow.id]
                                        } else {
                                            source_info[subflow.id] = source_info[subflow.id].filter(s => s !== nodeFormItem)
                                        }
                                    }
                                })
                                if (curVar && curVar.source_info && curVar.source_info[subflow.id]) {
                                    curVar.source_info[subflow.id].slice(0).forEach(formKey => {
                                        if (subflow.checked) {
                                            // 注释 1.b 场景
                                            if ((source_type === 'component_inputs' && (!subflow.latestForm.form[formKey] || subflow.latestForm.form[formKey].source_tag !== varItem.source_tag))
                                                || (source_type === 'component_outputs' && !subflow.latestForm.outputs.find(item => item.key === formKey))
                                            ) {
                                                if (source_info[subflow.id].length === 1) {
                                                    delete source_info[subflow.id]
                                                } else {
                                                    source_info[subflow.id] = curVar.source_info[subflow.id].filter(s => s !== formKey)
                                                }
                                            }
                                        } else {
                                            // 注释 2.a 场景，变量未被删除，最新版本部分表单勾选部分未被勾选
                                            if (!source_info[subflow.id].includes(formKey) && ((source_type === 'component_inputs' && (subflow.latestForm.form[formKey] && subflow.latestForm.form[formKey].source_tag === varItem.source_tag))
                                                || (source_type === 'component_outputs' && subflow.latestForm.outputs.find(item => item.key === formKey)))
                                            ) {
                                                source_info[subflow.id].push(formKey)
                                            }
                                        }
                                    })
                                }
                            } else {
                                // 注释 2.a 场景，变量未被删除
                                if (curVar && curVar.source_info && curVar.source_info[subflow.id]) {
                                    curVar.source_info[subflow.id].slice(0).forEach(formKey => {
                                        if (
                                            (source_type === 'component_inputs' && (subflow.latestForm.form[formKey] && subflow.latestForm.form[formKey].source_tag === varItem.source_tag))
                                            || (source_type === 'component_outputs' && subflow.latestForm.outputs.find(item => item.key === formKey))
                                        ) {
                                            if (!source_info[subflow.id]) {
                                                source_info[subflow.id] = [formKey]
                                            } else {
                                                source_info[subflow.id].push(formKey)
                                            }
                                        }
                                    })
                                }
                            }

                            // 根据source_info中获取勾选的表单项code
                            const [formCode] = curVar?.source_info[subflow.id] || []
                            if (!formCode) return
                            const { form, inputsConfig } = subflow.latestForm
                            const formValue = form[formCode]
                            const inputRef = this.$refs.inputParams[index]
                            let hook = false
                            // 获取输入参数的勾选状态
                            if (inputRef && inputRef.hooked) {
                                hook = inputRef.hooked[formCode] || false
                            }
                            if (varItem.is_meta && formValue && hook) {
                                const schema = formSchema.getSchema(formValue.key, inputsConfig)
                                varItem['form_schema'] = schema
                                varItem.meta = formValue.meta
                                // 如果之前选中的下拉项被删除了，则删除对应的值
                                const curVal = varItem.value
                                const isMatch = curVal ? schema.attrs.items.find(item => item.value === curVal) : true
                                varItem.value = isMatch ? curVal : ''
                            }
                        })
                        if (Object.keys(source_info).length > 0) {
                            constants[key] = varItem
                        }
                    } else {
                        constants[key] = varItem
                    }
                })

                // 清理流程模板全局变量输出字段
                this.$store.state.template.outputs.slice(0).forEach(key => {
                    if (!constants[key]) {
                        this.setOutputs({ changeType: 'delete', key })
                    }
                })

                // 设置全局变量面板icon小红点
                const localConstantKeys = Object.keys(constants)
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

                this.setConstants(constants)
            },
            onConfirm () {
                const handleConfirmation = () => {
                    this.subflowForms.filter(item => item.checked).forEach(item => {
                        const activity = tools.deepClone(this.activities[item.id])
                        activity.version = item.latestForm.version
                        activity.constants = tools.deepClone(item.latestForm.form)
                        Object.keys(activity.constants).forEach(key => {
                            const varItem = activity.constants[key]
                            varItem.value = item.latestForm.inputsValue[key]
                            varItem.need_render = item.latestForm.inputsRenderConfig[key]
                        })
                        this.setActivities({ type: 'edit', location: activity })
                        this.setSubprocessUpdated({
                            subprocess_node_id: item.id
                        })
                    })
                    this.handleVariableChange()
                    this.onCloseDialog(true)
                }

                const selectedInputForms = this.$refs.inputParams ? this.$refs.inputParams.filter((item, index) => {
                    return this.subflowForms[index].checked
                }) : []

                if (selectedInputForms.every(item => item.validate())) {
                    if (this.isSourceList) {
                        this.showSaveConfirmation(handleConfirmation)
                    } else {
                        handleConfirmation()
                    }
                } else {
                    const errorEl = document.querySelector('.subflow-form-wrap .common-error-tip')
                    if (errorEl) {
                        errorEl.scrollIntoView()
                    }
                }
            },
            // 显示保存确认弹窗
            showSaveConfirmation (confirmHandler) {
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [this.$t('保存后子流程更新将立即生效，请谨慎操作')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmFn: () => {
                        confirmHandler()
                        this.$emit('confirm')
                    }
                })
            },
            onCancel () {
                if (this.isSourceList) {
                    this.$router.push({
                        name: 'templatePanel',
                        params: { type: 'edit' },
                        query: { template_id: this.templateId }
                    })
                }
                this.onCloseDialog(true)
            },
            onCloseDialog (updated = false) {
                this.$emit('close', updated)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .batch-update-dialog-content {
        position: relative;
        height: 100%;
    }
    .header-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 80px 0 26px;
        height: 54px;
        line-height: 1;
        border-bottom: 1px solid #dcdee5;
        background: #ffffff;
        z-index: 1;
        & > h4 {
            margin: 0;
            font-weight: normal;
            font-size: 14px;
            color: #313238;
        }
        .legend-item {
            position: relative;
            display: inline-block;
            margin-left: 18px;
            padding-left: 20px;
            font-size: 14px;
            color: #63656e;
            line-height: 1;
            &:before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 3px;
            }
            &.delete:before {
                border: 1px solid rgba(251,133,121,0.16);
                background: #ffeeed;
            }
            &.add:before {
                border: 1px solid rgba(76,164,90,0.22);
                background: #e5ffe9;
            }
        }
        .bk-dialog-close {
            position: absolute;
            right: 20px;
            top: 16px;
            width: 26px;
            height: 26px;
            line-height: 26px;
            text-align: center;
            border-radius: 50%;
            font-size: 24px;
            font-weight: bold;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                background-color: #f0f1f5;
            }
        }
    }
    .subflow-form-wrap {
        height: calc(100% - 162px);
        overflow: auto;
    }
    .subflow-item {
        border-bottom: 1px solid #ffffff;
        .header-area {
            position: relative;
            display: flex;
            align-items: center;
            padding: 14px 24px 14px 30px;
            background: #f4f4f4;
            cursor: pointer;
            & > h3 {
                margin: 0 0 0 8px;
                font-size: 14px;
                font-weight: bold;
            }
            .fold-icon {
                position: absolute;
                right: 20px;
                top: 12px;
                font-size: 24px;
                &.fold {
                    transform: rotate(180deg);
                }
            }
        }
        .form-area {
            display: flex;
            justify-content: space-between;
            overflow: hidden;
            .current-form,
            .latest-form {
                position: relative;
                width: 50%;
                padding-bottom: 38px;
                .config-section {
                    & > h4 {
                        margin: 26px 30px 20px;
                        padding-bottom: 10px;
                        color: #313238;
                        font-size: 14px;
                        font-weight: normal;
                        border-bottom: 1px solid #cacedb;
                    }
                }
                .outputs-wrapper {
                    margin: 0 30px;
                }
                /deep/ .rf-form-item {
                    margin: 0;
                    padding: 15px 20px;
                    .rf-tag-hook {
                        top: 20px;
                        right: 10px;
                    }
                }
                .version-tag {
                    position: absolute;
                    left: 0;
                    top: 0;
                    padding: 4px 7px;
                    font-size: 12px;
                    line-height: 1;
                    color: #ffffff;
                    background: #a8a8a8;
                    &:after {
                        content: '';
                        position: absolute;
                        top: 0;
                        right: -6px;
                        width: 0;
                        height: 0;
                        border-style: solid;
                        border-width: 20px 6px 0 0;
                        border-color: #a8a8a8 transparent transparent transparent;
                    }
                    &.lastest {
                        background: #1aaf41;
                        &:after {
                            border-color: #1aaf41 transparent transparent transparent;
                        }
                    }
                }
            }
            .current-form {
                background: #fcfcfc;
                .no-data-wrapper {
                    background: #fcfcfc;
                }
            }
        }
    }
    .selecte-all {
        position: absolute;
        bottom: 16px;
        left: 30px;
    }
    .action-btns {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        .selected-tips {
            margin-right: 12px;
            font-size: 14px;
            color: #313238;
        }
    }
    .diff-alert {
        display: flex;
        justify-content: space-between;
        align-items: center;
        /deep/ .bk-link-text {
            font-size: 12px;
        }
    }
</style>
<style lang="scss">
    .batch-update-dialog {
        .bk-dialog-tool {
            display: none;
        }
        .bk-dialog-header {
            padding: 0;
        }
        .bk-dialog-body {
            padding: 0;
        }
    }
    .cancel-global-variable-dialog {
        .bk-dialog-header {
            padding-bottom: 18px;
            .bk-dialog-header-inner {
                font-size: 20px;
            }
        }
        .bk-dialog-body {
            line-height: 24px;
        }
    }
</style>
