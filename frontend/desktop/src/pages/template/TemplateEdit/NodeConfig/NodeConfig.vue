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
            :ext-cls="configClassString"
            :width="711"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span>{{ atomName }}</span>
            </div>
            <template slot="content" v-if="isShow">
                <section class="config-section">
                    <h3>{{i18n.basicInfo}}</h3>
                    <basic-info
                        :form-data.sync="basicInfo"
                        :atom-name="atomName"
                        :node-config="nodeConfig"
                        :atom-list="atomList"
                        :subflow-list="subflowList"
                        :is-subflow="isSubflow"
                        @onShowChoosePluginPanel="onShowChoosePluginPanel"
                        @versionChange="versionChange"
                        @tplChange="tplChange">
                    </basic-info>
                </section>
                <section class="config-section">
                    <h3>{{i18n.inputParams}}</h3>
                    <div class="inputs-wrapper" v-bkloading="{ isLoading: inputLoading }">
                        <template v-if="!inputLoading">
                            <input-params
                                v-if="inputs.length > 0"
                                :node-config="nodeConfig"
                                :scheme="inputs"
                                :value="inputParamValue"
                                :hooked="inputHooked"
                                :is-subflow="isSubflow"
                                @inputsHookChange="inputsHookChange">
                            </input-params>
                            <no-data v-else></no-data>
                        </template>
                    </div>
                </section>
                <section class="config-section">
                    <h3>{{i18n.outputParams}}</h3>
                    <div class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading }">
                        <template v-if="!outputLoading">
                            <output-params
                                v-if="outputs.length"
                                :node-id="nodeId"
                                :params.sync="outputs"
                                :node-config="nodeConfig">
                            </output-params>
                            <no-data v-else></no-data>
                        </template>
                    </div>
                </section>
            </template>
        </bk-sideslider>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapState, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import atomFilter from '@/utils/atomFilter.js'
    import tools from '@/utils/tools.js'
    import BasicInfo from './BasicInfo.vue'
    import InputParams from './InputParams.vue'
    import outputParams from './outputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            outputParams,
            NoData
        },
        props: {
            nodeId: {
                type: String,
                default: ''
            },
            settingActiveTab: {
                type: String,
                default: ''
            },
            atomList: {
                type: Array,
                default () {
                    return []
                }
            },
            subflowList: {
                type: Array,
                default () {
                    return []
                }
            },
            common: {
                type: [Boolean, Number],
                required: false
            },
            isShow: {
                type: Boolean,
                required: false
            },
            isChoosePluginPanelShow: {
                type: Boolean,
                required: false
            }
        },
        data () {
            return {
                pluginLoading: false, // 普通任务节点数据加载
                subflowLoading: false, // 子流程任务节点数据加载
                constantsLoading: false, // 子流程输入参数配置项加载
                basicInfo: {},
                inputs: [],
                inputParamValue: {},
                inputHooked: {},
                outputs: [],
                outputHooked: {},
                subfowConstants: {}, // 子流程输入参数（引用的全局变量）
                i18n: {
                    basicInfo: gettext('基础信息'),
                    inputParams: gettext('输入参数'),
                    outputParams: gettext('输出参数'),
                    selectAtom: gettext('请选择插件'),
                    selectSubflow: gettext('请选择子流程')
                }
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'pluginConfigs': state => state.atomForm.config
            }),
            nodeConfig () { // 任务节点原始配置
                const config = this.activities[this.nodeId]
                return tools.deepClone(config)
            },
            isSubflow () {
                return this.isShow && this.nodeConfig.type && this.nodeConfig.type !== 'ServiceActivity'
            },
            atomGroup () { // 某一标准插件下所有版本分组
                return this.atomList.find(item => item.code === this.basicInfo.plugin)
            },
            atomName () { // 面板 title 和 插件名
                if (this.isSubflow) {
                    const templateId = this.nodeConfig.template_id
                    if (templateId || templateId === 0) {
                        return this.nodeConfig.name
                    }
                    return this.i18n.selectSubflow
                } else {
                    return !this.atomGroup ? this.i18n.selectAtom : `${this.atomGroup.type}-${this.atomGroup.name}`
                }
            },
            inputLoading () { // 以下任一方法处于 pending 状态，输入参数展示 loading 效果
                return this.pluginLoading || this.subflowLoading || this.constantsLoading
            },
            outputLoading () {
                return this.pluginLoading || this.subflowLoading
            },
            configClassString () { // 动态设置面板的 class
                let base = 'common-template-setting-sideslider node-config-base'
                switch (this.settingActiveTab) {
                    case 'globalVariableTab':
                        base += ' position-right-var'
                        break
                    case 'templateConfigTab':
                        base += ' position-right-basic-info'
                        break
                    case 'localDraftTab':
                        base += ' position-right-cache'
                        break
                    case 'templateDataEditTab':
                        base += ' position-right-template-data'
                }
                if (this.isChoosePluginPanelShow) {
                    base += ' position-right-choose-plugin'
                }
                return base
            }
        },
        watch: {
            nodeId (val) {
                if (!val || !this.isShow) {
                    return
                }
                // 更新配置信息
                this.resetNodeConfigData()
            }
        },
        methods: {
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadSubflowConfig'
            ]),
            ...mapMutations('template/', [
                'setNodeInputData'
            ]),
            // 初始化节点数据
            async initData () {
                if (!this.basicInfo.plugin && !this.basicInfo.tpl) { // 未选择插件
                    return
                }
                if (this.basicInfo.type === 'ServiceActivity') {
                    this.getPluginData()
                    Object.keys(this.nodeConfig.component.data || []).forEach(key => {
                        const val = tools.deepClone(this.nodeConfig.component.data[key].value)
                        this.$set(this.inputParamValue, key, val)
                    })
                } else {
                    this.subfowConstants = tools.deepClone(this.nodeConfig.constants)
                    const { version } = this.nodeConfig
                    const subflowData = await this.getSubflowData(version)
                    this.subfowConstants = this.getConstants(subflowData.form)
                    this.inputs = await this.getSubflowInputsConfig()
                    this.inputParamValue = this.getSubflowInputsValue()
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
             * 加载普通任务节点数据
             */
            async getPluginData () {
                const { plugin, version } = this.basicInfo
                this.pluginLoading = true
                try {
                    this.inputs = await this.getAtomConfig(plugin, version)
                    this.outputs = this.atomGroup.list.find(item => item.version === version).output
                    this.outputHooked = this.setVals
                    const setVals = this.inputs.reduce((acc, cur) => {
                        acc[cur.tag_code] = { value: '', hook: false }
                        return acc
                    }, {})

                    const data = this.nodeConfig.component.data
                    if (!data || !Object.keys(data).length) { // 同步 data 数据到 store
                        this.setNodeInputData({
                            id: this.nodeConfig.id,
                            type: this.nodeConfig.type,
                            updateType: 'all',
                            setVals: setVals
                        })
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pluginLoading = false
                }
            },
            /**
             * 加载子流程任务节点数据
             */
            async getSubflowData (version) {
                const { tpl } = this.basicInfo
                this.subflowLoading = true
                try {
                    const resp = await this.loadSubflowConfig({
                        templateId: tpl,
                        common: this.common,
                        version
                    })
                    // 输出变量
                    this.outputs = Object.keys(resp.outputs).map(item => {
                        const output = resp.outputs[item]
                        return {
                            name: output.name,
                            key: output.key,
                            version: output.version
                        }
                    })
                    return resp
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.subflowLoading = false
                }
            },
            /**
             * 加载子流程输入参数
             * @param {Object} forms 子流程输入参数配置数据
             * @description
             * 首次添加、子流程切换、子流程更新时，取接口返回的 form
             * 编辑时，取 activities 里对应的全局变量 form
             * @return {Object} 子流程表单项
             */
            getConstants (forms) {
                const keys = this.nodeConfig.constants ? Object.keys(this.nodeConfig.constants) : []
                if (!keys.length) { // 同步 constants 数据到 store
                    this.setNodeInputData({
                        id: this.nodeConfig.id,
                        type: this.nodeConfig.type,
                        updateType: 'all',
                        setVals: tools.deepClone(forms)
                    })
                }
                return keys.length ? this.nodeConfig.constants : forms
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
                let variables = []
                Object.keys(this.subfowConstants).forEach(item => {
                    const from = this.subfowConstants[item]
                    if (from.show_type === 'show') { // 隐藏变量不显示
                        variables.push(from)
                    }
                })
                variables = variables.sort((a, b) => a.index - b.index)
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
                            error_message: gettext('默认值不符合正则规则：') + variable.validation
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
            getNodeBasic () {
                if (this.nodeConfig.type === 'ServiceActivity') {
                    const {
                        type, component, name, stage_name, error_ignorable,
                        can_retry, retryable, isSkipped, skippable, optional
                    } = this.nodeConfig
                    // 空节点不存在 atom
                    const atom = this.atomList.find(item => item.code === component.code)
                    return {
                        plugin: component.code,
                        version: component.code ? component.version || 'legacy' : '',
                        versionList: this.getAtomVersions(component.code),
                        name: name,
                        desc: atom ? atom.desc : '',
                        step: stage_name,
                        ignorable: error_ignorable,
                        skippable: isSkipped || skippable,
                        retryable: retryable || can_retry,
                        selectable: optional,
                        type
                    }
                } else {
                    const { type, template_id, name, stage_name, optional } = this.nodeConfig
                    return {
                        tpl: template_id,
                        name: name,
                        step: stage_name,
                        selectable: optional,
                        type
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
             * 获取子流程任务节点输入参数值
             */
            getSubflowInputsValue () {
                return Object.keys(this.subfowConstants).reduce((acc, cur) => {
                    const variable = this.subfowConstants[cur]
                    acc[variable.key] = tools.deepClone(variable.value)
                    return acc
                }, {})
            },
            getInputHooked () {
                if (this.isSubflow) { // 子流程、遍历全局变量中是否有节点引用了
                    // return this.inputs.reduce((acc, cur) => {
                    //     acc[cur.tag_code] = Object.keys(this.constants).some(key => {
                    //         const sourceInfo = this.constants[key].source_info
                    //         for (const node in sourceInfo) {
                    //             console.log(sourceInfo[node], cur.tag_code, 'cscscscss')
                    //             if (sourceInfo[node].includes(cur.tag_code)) {
                    //                 return true
                    //             }
                    //         }
                    //     })
                    //     return acc
                    // }, {})
                    return Object.keys(this.subfowConstants).reduce((acc, cur) => {
                        const item = this.subfowConstants[cur]
                        const targetVar = this.constants[cur]
                        acc[cur] = targetVar && targetVar.version === item.version
                        return acc
                    }, {})
                }
                if (this.nodeConfig.component && this.nodeConfig.component.data) {
                    const data = this.nodeConfig.component.data
                    return Object.keys(data).reduce((acc, cur) => {
                        acc[cur] = data[cur].hook || false
                        return acc
                    }, {})
                }
                return {}
            },
            pluginChange () {
                const { name, desc, outputs } = this.atomGroup
                const versionList = this.getAtomVersions(this.basicInfo.plugin)
                const config = {
                    versionList: versionList,
                    version: versionList[versionList.length - 1].version,
                    name: name,
                    desc: desc,
                    ignorable: false,
                    skippable: true,
                    retryable: true,
                    selectable: false
                }
                Object.assign(this.basicInfo, config)
                this.outputs = outputs
                this.inputParamValue = {}
                this.getPluginData()
            },
            inputsHookChange ({ code, val }) {
                this.$set(this.inputHooked, code, val)
            },
            versionChange () {
                this.getPluginData()
                this.inputParamValue = {}
            },
            // 关闭配置面板
            onBeforeClose () {
                this.$emit('hide')
            },
            // 显示插件/子流程选择面板
            onShowChoosePluginPanel () {
                this.$emit('onShowChoosePluginPanel', this.nodeId)
            },
            /**
             * 根据 activities[nodeId] 中数据重置面板
             * 基础信息
             * 输入信息
             * 输出信息
             */
            async resetNodeConfigData () {
                this.inputs = []
                this.inputParamValue = {}
                this.outputs = []
                this.subfowConstants = {}
                this.basicInfo = this.getNodeBasic()
                await this.initData()
                this.inputHooked = this.getInputHooked()
            },
            async tplChange () {
                const tpl = this.subflowList.find(item => item.template_id === this.basicInfo.tpl)
                this.basicInfo.name = tpl.name
                this.basicInfo.selectable = false
                const subflowData = await this.getSubflowData()
                this.subfowConstants = this.getConstants(subflowData.form)
                this.inputs = await this.getSubflowInputsConfig()
                this.inputParamValue = this.getSubflowInputsValue()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
    .node-config-wrapper {
        height: 100%;
        background: #ffffff;
        overflow-y: auto;
        /deep/ {
            .bk-sideslider-wrapper {
                overflow: hidden;
            }
            .bk-sideslider-content {
                padding: 30px 20px;
                overflow: scroll;
                @include scrollbar;
            }
        }
        .node-config-base {
            /deep/ .bk-sideslider-wrapper {
                transition: right .3s ease-in-out;
                right: 56px;
            }
            &.position-right-var {
                /deep/ .bk-sideslider-wrapper {
                    right: 856px;
                }
            }
            &.position-right-basic-info{
                /deep/ .bk-sideslider-wrapper {
                    right: 477px;
                }
            }
            &.position-right-cache {
                /deep/ .bk-sideslider-wrapper {
                    right: 477px;
                }
            }
            &.position-right-template-data {
                /deep/ .bk-sideslider-wrapper {
                    right: 897px;
                }
            }
            &.position-right-choose-plugin {
                /deep/ .bk-sideslider-wrapper {
                    right: 768px;
                }
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
</style>
