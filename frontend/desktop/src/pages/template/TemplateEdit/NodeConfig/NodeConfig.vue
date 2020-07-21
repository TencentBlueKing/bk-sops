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
    <div class="node-config-wrapper">
        <bk-sideslider
            ref="nodeConfigPanel"
            ext-cls="node-config-panel"
            :width="800"
            :is-show="isShow"
            :before-close="beforeClose">
            <div slot="header">
                <span
                    :class="['go-back', {
                        'active': isSelectorPanelShow && (basicInfo.plugin || basicInfo.tpl)
                    }]"
                    @click="goBackToConfig">
                    {{ $t('节点配置') }}
                </span>
                <!-- 选择面板展开，并且标准插件或子流程不为空时，显示 -->
                <span
                    v-if="isSelectorPanelShow && (basicInfo.plugin || basicInfo.tpl)"
                    class="go-back">
                    <i class="common-icon-angle-right"></i>
                    {{ selectorTitle }}
                </span>
            </div>
            <template slot="content">
                <template v-if="!isSelectorPanelShow">
                    <div class="node-config">
                        <div class="config-form">
                            <!-- 基础信息 -->
                            <section class="config-section">
                                <h3>{{$t('基础信息')}}</h3>
                                <basic-info
                                    ref="basicInfo"
                                    :basic-info="basicInfo"
                                    :node-config="nodeConfig"
                                    :version-list="versionList"
                                    :is-subflow="isSubflow"
                                    :input-loading="inputLoading"
                                    @openSelectorPanel="isSelectorPanelShow = true"
                                    @versionChange="versionChange"
                                    @viewSubflow="onViewSubflow"
                                    @updateSubflowVersion="updateSubflowVersion"
                                    @update="updateBasicInfo">
                                </basic-info>
                            </section>
                            <!-- 输入参数 -->
                            <section class="config-section">
                                <h3>{{$t('输入参数')}}</h3>
                                <div class="inputs-wrapper" v-bkloading="{ isLoading: inputLoading }">
                                    <template v-if="!inputLoading">
                                        <input-params
                                            v-if="inputs.length > 0"
                                            ref="inputParams"
                                            :node-id="nodeId"
                                            :scheme="inputs"
                                            :plugin="basicInfo.plugin"
                                            :version="basicInfo.version"
                                            :subflow-forms="subflowForms"
                                            :value="inputsParamValue"
                                            :is-subflow="isSubflow"
                                            @globalVariableUpdate="$emit('globalVariableUpdate', true)"
                                            @update="updateInputsValue">
                                        </input-params>
                                        <no-data v-else></no-data>
                                    </template>
                                </div>
                            </section>
                            <!-- 输出参数 -->
                            <section class="config-section">
                                <h3>{{$t('输出参数')}}</h3>
                                <div class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading }">
                                    <template v-if="!outputLoading">
                                        <output-params
                                            v-if="outputs.length"
                                            :params="outputs"
                                            :version="basicInfo.version"
                                            :node-id="nodeId"
                                            @globalVariableUpdate="$emit('globalVariableUpdate', true)">
                                        </output-params>
                                        <no-data v-else></no-data>
                                    </template>
                                </div>
                            </section>
                        </div>
                        <div class="btn-footer">
                            <bk-button theme="primary" @click="onSaveConfig">{{ $t('保存') }}</bk-button>
                            <bk-button theme="default" @click="$emit('update:isShow', false)">{{ $t('取消') }}</bk-button>
                        </div>
                    </div>
                </template>
                <selector-panel
                    v-else
                    :is-subflow="isSubflow"
                    :atom-type-list="atomTypeList"
                    :basic-info="basicInfo"
                    @back="isSelectorPanelShow = false"
                    @viewSubflow="onViewSubflow"
                    @select="onPluginOrTplChange">
                </selector-panel>
            </template>
        </bk-sideslider>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapState, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import BasicInfo from './BasicInfo.vue'
    import InputParams from './InputParams.vue'
    import OutputParams from './OutputParams.vue'
    import SelectorPanel from './SelectorPanel.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import bus from '@/utils/bus.js'

    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            OutputParams,
            SelectorPanel,
            NoData
        },
        props: {
            project_id: [String, Number],
            nodeId: String,
            isShow: Boolean,
            atomList: Array,
            subflowList: Array,
            atomTypeList: Object,
            common: [String, Number],
            isSettingPanelShow: Boolean
        },
        data () {
            const nodeConfig = this.$store.state.template.activities[this.nodeId]
            const basicInfo = this.getNodeBasic(nodeConfig)
            const versionList = nodeConfig.type === 'ServiceActivity' ? this.getAtomVersions(nodeConfig.component.code) : []
            const isSelectorPanelShow = nodeConfig.type === 'ServiceActivity' ? !basicInfo.plugin : !basicInfo.tpl
            return {
                pluginLoading: false, // 普通任务节点数据加载
                subflowLoading: false, // 子流程任务节点数据加载
                constantsLoading: false, // 子流程输入参数配置项加载
                nodeConfig, // 任务节点的完整 activity 配置参数
                basicInfo, // 基础信息模块
                versionList, // 标准插件版本
                inputs: [], // 输入参数表单配置项
                inputsParamValue: {}, // 输入参数值
                outputs: [], // 输出参数
                subflowForms: {}, // 子流程输入参数
                isSelectorPanelShow // 是否显示选择插件(子流程)面板
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'locations': state => state.template.location,
                'pluginConfigs': state => state.atomForm.config,
                'pluginOutput': state => state.atomForm.output
            }),
            isSubflow () {
                return this.nodeConfig.type !== 'ServiceActivity'
            },
            atomGroup () { // 某一标准插件下所有版本分组
                return this.atomList.find(item => item.code === this.basicInfo.plugin)
            },
            inputLoading () { // 以下任一方法处于 pending 状态，输入参数展示 loading 效果
                return this.pluginLoading || this.subflowLoading || this.constantsLoading
            },
            outputLoading () {
                return this.pluginLoading || this.subflowLoading
            },
            selectorTitle () {
                return this.isSubflow ? i18n.t('选择子流程') : i18n.t('选择标准插件')
            }
        },
        created () {
            /**
             * notice: 该方法为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
             * description: 切换作业模板时，将当前作业的全局变量表格数据部分添加到输出参数
             */
            bus.$on('jobExecuteTaskOutputs', args => {
                const { plugin, version } = this.basicInfo
                if (!this.isSubflow && plugin === 'job_execute_task') {
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
                                Object.keys(this.constants).some(key => {
                                    const constant = this.constants[key]
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
        },
        mounted () {
            this.initData()
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadSubflowConfig'
            ]),
            ...mapMutations('template/', [
                'setVariableSourceInfo',
                'setSubprocessUpdated',
                'setActivities',
                'deleteVariable'
            ]),
            // 初始化节点数据
            async initData () {
                if (!this.basicInfo.plugin && !this.basicInfo.tpl) { // 未选择插件
                    return
                }
                if (!this.isSubflow) {
                    const paramsVal = {}
                    Object.keys(this.nodeConfig.component.data || {}).forEach(key => {
                        const val = tools.deepClone(this.nodeConfig.component.data[key].value)
                        paramsVal[key] = val
                    })
                    this.inputsParamValue = paramsVal
                    this.getPluginDetail()
                } else {
                    const { tpl, version } = this.basicInfo
                    const forms = {}
                    Object.keys(this.nodeConfig.constants).forEach(key => {
                        const form = this.nodeConfig.constants[key]
                        if (form.show_type === 'show') {
                            forms[key] = form
                        }
                    })
                    await this.getSubflowDetail(tpl, version)
                    this.inputs = await this.getSubflowInputsConfig()
                    this.inputsParamValue = this.getSubflowInputsValue(forms)
                }
                // 节点参数错误时，配置项加载完成后，执行校验逻辑，提示用户错误信息
                const location = this.locations.find(item => item.id === this.nodeConfig.id)
                if (location && location.status === 'FAILED') {
                    this.validate()
                }
            },
            /**
             * 加载标准插件节点输入参数表单配置项，获取输出参数列表
             */
            async getPluginDetail () {
                const { plugin, version } = this.basicInfo
                this.pluginLoading = true
                try {
                    this.inputs = await this.getAtomConfig(plugin, version)
                    this.outputs = this.atomGroup.list.find(item => item.version === version).output
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pluginLoading = false
                }
            },
            /**
             * 加载标准插件表单配置项文件
             * 优先取 store 里的缓存
             */
            async getAtomConfig (plugin, version, classify, name) {
                const pluginGroup = this.pluginConfigs[plugin]
                if (pluginGroup && pluginGroup[version]) {
                    return pluginGroup[version]
                }
                try {
                    await this.loadAtomConfig({ atom: plugin, version, classify, name })
                    const config = $.atoms[plugin]
                    return config
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 加载子流程任务节点输入、输出、版本配置项
             */
            async getSubflowDetail (tpl, version) {
                this.subflowLoading = true
                try {
                    const params = {
                        templateId: tpl,
                        common: this.common
                    }
                    if (version) {
                        params.version = version
                    }
                    const resp = await this.loadSubflowConfig({ ...params })
                    const data = resp.data
                    this.subflowForms = data.form
                    // 子流程模板版本更新时，未带版本信息，需要请求接口后获取最新版本
                    this.updateBasicInfo({ version: data.version })

                    // 输出变量
                    this.outputs = Object.keys(data.outputs).map(item => {
                        const output = data.outputs[item]
                        return {
                            name: output.name,
                            key: output.key,
                            version: output.hasOwnProperty('version') ? output.version : 'legacy'
                        }
                    })
                    return data
                } catch (error) {
                    errorHandler(error, this)
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
                    const atomConfig = await this.getAtomConfig(atom, version, classify, name)
                    let formItemConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                    if (variable.is_meta || formItemConfig.meta_transform) {
                        formItemConfig = formItemConfig.meta_transform(variable.meta || variable)
                        if (!variable.meta) {
                            variable.value = formItemConfig.attrs.value
                        }
                    }
                    formItemConfig.tag_code = key
                    formItemConfig.attrs.name = variable.name
                    // 自定义输入框变量正则校验添加到插件配置项
                    if (variable.custom_type === 'input' && variable.validation !== '') {
                        formItemConfig.attrs.validation.push({
                            type: 'regex',
                            args: variable.validation,
                            error_message: i18n.t('默认值不符合正则规则：') + variable.validation
                        })
                    }
                    inputs.push(formItemConfig)
                }))
                this.constantsLoading = false
                return inputs
            },
            /**
             * 获取任务节点基础信息数据
             */
            getNodeBasic (config) {
                if (config.type === 'ServiceActivity') {
                    const {
                        component, name, labels, error_ignorable, can_retry,
                        retryable, isSkipped, skippable, optional
                    } = config
                    let basicInfoName = i18n.t('请选择插件')
                    let desc = ''
                    let version = ''
                    // 节点已选择标准插件
                    if (component.code) {
                        const atom = this.atomList.find(item => item.code === component.code)
                        basicInfoName = `${atom.group_name}-${atom.name}`
                        version = component.hasOwnProperty('version') ? component.version : 'legacy'
                        desc = atom.desc
                    }

                    return {
                        plugin: component.code || '',
                        name: basicInfoName,
                        nodeName: name,
                        nodeLabel: labels || [], // 兼容旧数据，节点标签字段为后面新增
                        version, // 标准插件版本
                        desc, // 空节点不存在插件描述信息
                        ignorable: error_ignorable,
                        // isSkipped 和 can_retry 为旧数据字段，后来分别变更为 skippable、retryable，节点点开编辑保存后会删掉旧字段
                        // 这里取值做兼容处理，新旧数据不可能同时存在，优先取旧数据字段
                        skippable: isSkipped === undefined ? skippable : isSkipped,
                        retryable: can_retry === undefined ? retryable : can_retry,
                        selectable: optional
                    }
                } else {
                    const { template_id, name, labels, optional } = config
                    let templateName = i18n.t('请选择子流程')

                    if (config.template_id || config.template_id === 0) {
                        this.atomTypeList.subflow.groups.some(group => {
                            return group.list.some(item => {
                                if (item.template_id === Number(template_id)) {
                                    templateName = item.name
                                    return true
                                }
                            })
                        })
                    }
                    return {
                        tpl: template_id || '',
                        name: templateName,
                        nodeName: name,
                        nodeLabel: labels || [], // 兼容旧数据，节点标签字段为后面新增
                        selectable: optional,
                        version: config.hasOwnProperty('version') ? config.version : '' // 子流程版本，区别于标准插件版本
                    }
                }
            },
            /**
             * 获取某一标准插件所有版本列表
             */
            getAtomVersions (code) {
                if (!code) {
                    return []
                }
                const atom = this.atomList.find(item => item.code === code)
                return atom.list.map(item => {
                    return {
                        version: item.version
                    }
                })
            },
            /**
             * 获取子流程任务节点输入参数值，有三种情况：
             * 1.节点点开编辑时取 activitity 里的 constants 数据
             * 2.切换子流程时，取接口返回的 form 数据
             * 3.子流程更新时，先判断表单项是否为勾选状态，勾选取旧表单项数据，
             * 未勾选则判断新旧表单项数据 custom_type(自定义全局变量)或者 source_tag(标准插件表单项)是否相同，
             * 相同取旧数据里的表单值，否则取新数据
             */
            getSubflowInputsValue (forms, oldForms = {}) {
                return Object.keys(forms).reduce((acc, cur) => { // 遍历新表单项
                    const variable = forms[cur]
                    if (variable.show_type === 'show') {
                        let canReuse = false
                        const oldVariable = oldForms[cur]
                        const isHooked = this.isParamsInConstants(variable)
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
            // 输入参数是否勾选
            isParamsInConstants (form) {
                return Object.keys(this.constants).some(key => {
                    const varItem = this.constants[key]
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
            onPluginOrTplChange (val) {
                this.isSelectorPanelShow = false
                this.clearParamsSourceInfo()
                if (this.isSubflow) {
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
                const { code, group_name, name, desc, list } = atomGroup
                this.versionList = this.getAtomVersions(code)
                const config = {
                    plugin: code,
                    version: list[list.length - 1].version,
                    name: `${group_name}-${name}`,
                    nodeName: name,
                    nodeLabel: [],
                    desc: desc,
                    ignorable: false,
                    skippable: true,
                    retryable: true,
                    selectable: false
                }
                this.updateBasicInfo(config)
                this.inputsParamValue = {}
                await this.getPluginDetail()
                this.$refs.basicInfo && this.$refs.basicInfo.validate() // 清除节点保存报错时的错误信息
            },
            /**
             * 标准插件版本切换
             */
            async versionChange (val) {
                this.updateBasicInfo({ version: val })
                this.clearParamsSourceInfo()
                this.inputsParamValue = {}
                await this.getPluginDetail()
            },
            /**
             * 子流程切换
             * - 清除勾选变量与全局变量关联
             * - 请求子流程模板详情，组装 scheme 和 value，更新基础信息
             * - 清除子流程更新（每次都调用，store 里方法对不存在新版本的模板有做兼容）
             * - 校验基础信息
             */
            async tplChange (data) {
                const { id, name, version } = data
                const config = {
                    name,
                    version,
                    tpl: id,
                    nodeName: name,
                    nodeLabel: [],
                    selectable: false
                }
                this.updateBasicInfo(config)
                await this.getSubflowDetail(id, version)
                this.inputs = await this.getSubflowInputsConfig()
                this.inputsParamValue = this.getSubflowInputsValue(this.subflowForms)
                this.setSubprocessUpdated({
                    subprocess_node_id: this.nodeConfig.id
                })
                this.$refs.basicInfo && this.$refs.basicInfo.validate() // 清除节点保存报错时的错误信息
            },
            /**
             * 更新基础信息
             * 填写基础信息表单，切换插件/子流程，选择插件版本，子流程更新
             */
            updateBasicInfo (data) {
                this.basicInfo = Object.assign({}, this.basicInfo, data)
            },
            // 输入参数表单值更新
            updateInputsValue (val) {
                this.inputsParamValue = val
            },
            /**
             * 子流程版本更新
             */
            async updateSubflowVersion () {
                const oldForms = Object.assign({}, this.subflowForms)
                await this.getSubflowDetail(this.basicInfo.tpl)
                this.inputs = await this.getSubflowInputsConfig()
                this.inputsParamValue = this.getSubflowInputsValue(this.subflowForms, oldForms)
                this.subflowUpdateParamsChange()
                this.setSubprocessUpdated({
                    subprocess_node_id: this.nodeConfig.id
                })
            },
            /**
             * 子流程版本更新后，输入、输出参数如果有变更，需要处理全局变量的 source_info 更新
             * 分为两种情况：
             * 1.输入、输出参数被勾选，并且在新流程模板中被删除，需要在更新后修改全局变量 source_info 信息
             * 2.新增和修改输入、输出参数，不做处理
             */
            subflowUpdateParamsChange () {
                const nodeId = this.nodeConfig.id
                for (const key in this.constants) {
                    const varItem = this.constants[key]
                    const { source_type, source_info } = varItem
                    const sourceInfo = source_info[this.nodeId]
                    if (sourceInfo) {
                        if (source_type === 'component_inputs') {
                            sourceInfo.forEach(nodeFormItem => {
                                if (!this.inputs.find(item => item.tag_code === nodeFormItem)) {
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
            },
            // 取消已勾选为全局变量的输入、输出参数勾选状态
            clearParamsSourceInfo () {
                const nodeId = this.nodeConfig.id
                for (const key in this.constants) {
                    const varItem = this.constants[key]
                    const { source_type, source_info } = varItem
                    const sourceInfo = source_info[this.nodeId]
                    if (sourceInfo) {
                        if (source_type === 'component_inputs') {
                            this.inputs.forEach(formItem => {
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
            },
            // 查看子流程模板
            onViewSubflow (id) {
                let pathData = {}
                if (this.common) {
                    pathData = {
                        name: 'commonTemplatePanel',
                        params: {
                            type: 'edit'
                        },
                        query: {
                            template_id: id,
                            common: '1'
                        }
                    }
                } else {
                    pathData = {
                        name: 'templatePanel',
                        params: {
                            type: 'edit',
                            project_id: this.project_id
                        },
                        query: {
                            template_id: id
                        }
                    }
                }
                const { href } = this.$router.resolve(pathData)
                window.open(href, '_blank')
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
            /**
             * 同步节点配置面板数据到 store.activities
             */
            syncActivity () {
                let config
                if (this.isSubflow) {
                    const { nodeName, nodeLabel, selectable, version, tpl } = this.basicInfo
                    const constants = {}
                    Object.keys(this.subflowForms).forEach(key => {
                        const constant = this.subflowForms[key]
                        if (constant.show_type === 'show') {
                            constant.value = tools.deepClone(this.inputsParamValue[key])
                        }
                        constants[key] = constant
                    })
                    config = Object.assign({}, this.nodeConfig, {
                        constants,
                        version,
                        name: nodeName,
                        labels: nodeLabel,
                        template_id: tpl,
                        optional: selectable
                    })
                } else {
                    const { ignorable, nodeName, nodeLabel, plugin, retryable, skippable, selectable, version } = this.basicInfo
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
                            value: tools.deepClone(formVal)
                        }
                    })
                    const component = {
                        code: plugin,
                        data,
                        version
                    }
                    config = Object.assign({}, this.nodeConfig, {
                        component,
                        retryable,
                        skippable,
                        name: nodeName,
                        labels: nodeLabel,
                        error_ignorable: ignorable,
                        optional: selectable
                    })
                    delete config.can_retry
                    delete config.isSkipped
                }
                this.nodeConfig = config
                this.setActivities({ type: 'edit', location: config })
            },
            // 由父组件调用，获取节点基础信息
            getBasicInfo () {
                return this.basicInfo
            },
            beforeClose () {
                this.$emit('update:isShow', false)
                return true
            },
            onSaveConfig () {
                this.validate().then(result => {
                    if (result) {
                        console.log('result', result)
                        const { skippable, retryable, selectable: optional } = this.basicInfo
                        this.syncActivity() // @todo 更新节点状态
                        this.$emit('updateNodeInfo', this.nodeId, { status: '', skippable, retryable, optional })
                        this.$emit('close')
                    }
                })
            }
        }
    }
</script>
<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
.node-config-panel {
    height: 100%;
    .go-back.active {
        color: #3a84ff;
        cursor: pointer;
    }
    .node-config {
        height: calc(100vh - 60px);
        overflow: hidden;
        .config-form {
            padding: 20px 30px 0 30px;
            max-height: calc(100% - 49px);
            overflow-y: auto;
            @include scrollbar;
        }
        .btn-footer {
            padding: 8px 30px;
            border-top: 1px solid #cacedb;
            .bk-button {
                margin-right: 10px;
                padding: 0 25px;
            }
        }
    }
    .config-section {
        margin-bottom: 50px;
        & > h3 {
            margin: 0 0 20px 0;
            padding-bottom: 14px;
            font-size: 14px;
            font-weight: bold;
            line-height: 1;
            color: #313238;
            border-bottom: 1px solid #cacecb;
        }
        .inputs-wrapper,
        .outputs-wrapper {
            min-height: 80px;
        }
    }
    .bk-sideslider-content {
        overflow: initial;
    }
}
</style>
