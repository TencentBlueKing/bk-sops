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
    <div class="node-config-wrapper">
        <bk-sideslider
            ref="nodeConfigPanel"
            ext-cls="node-config-panel"
            :width="800"
            :is-show="isShow"
            :quick-close="true"
            :before-close="beforeClose">
            <div class="config-header" slot="header">
                <template v-if="isVariablePanelShow">
                    <i class="bk-icon icon-arrows-left variable-back-icon" @click="isVariablePanelShow = false"></i>
                    <span>
                        {{ variableData.key ? $t('编辑') : $t('新建') }}{{ $t('全局变量') }}
                    </span>
                </template>
                <template v-else>
                    <span
                        :class="['go-back', {
                            'active': isSelectorPanelShow && (basicInfo.plugin || basicInfo.tpl)
                        }]"
                        @click="goBackToConfig">
                        <i
                            v-if="backToVariablePanel"
                            class="bk-icon icon-arrows-left variable-back-icon"
                            @click="onClosePanel(true)">
                        </i>
                        {{ $t('节点配置') }}
                    </span>
                    <!-- 二级面包屑title，选择面板展开，并且标准插件或子流程不为空时显示 -->
                    <span
                        v-if="isSelectorPanelShow && (basicInfo.plugin || basicInfo.tpl)"
                        class="go-back">
                        <i class="common-icon-angle-right"></i>
                        {{ selectorTitle }}
                    </span>
                    <!-- 展示选择面板是隐藏 -->
                    <template v-if="!isSelectorPanelShow">
                        <!-- 全局变量popover -->
                        <div :class="['view-variable', { 'r30': isViewMode }]">
                            <bk-popover
                                v-if="!isSelectorPanelShow"
                                :key="randomKey"
                                ext-cls="variable-popover"
                                placement="bottom-end"
                                :tippy-options="{ hideOnClick: false }">
                                <div style="cursor: pointer;">{{ $t('全局变量') }}</div>
                                <div class="variable-list" slot="content">
                                    <div class="header-area">
                                        <span>{{ $t('全局变量') }}</span>
                                        <bk-link v-if="!isViewMode" theme="primary" icon="bk-icon icon-plus" @click="openVariablePanel">{{ $t('新建变量') }}</bk-link>
                                    </div>
                                    <bk-table :data="variableList" :outer-border="false" :max-height="400">
                                        <bk-table-column :label="$t('名称')" prop="name" width="165" :show-overflow-tooltip="true"></bk-table-column>
                                        <bk-table-column label="KEY" :show-overflow-tooltip="true" width="209">
                                            <template slot-scope="props" width="165">
                                                <div class="key">{{ props.row.key }}</div>
                                                <i class="copy-icon common-icon-double-paper-2" @click="onCopyKey(props.row.key)"></i>
                                            </template>
                                        </bk-table-column>
                                        <bk-table-column :label="$t('属性')" width="80">
                                            <div class="icon-wrap" slot-scope="props">
                                                <i
                                                    :class="[props.row.source_type !== 'component_outputs' ? 'common-icon-show-left' : 'common-icon-show-right color-org']"
                                                    v-bk-tooltips="{
                                                        content: props.row.source_type !== 'component_outputs' ? $t('输入') : $t('输出'),
                                                        placements: ['bottom']
                                                    }">
                                                </i>
                                                <i
                                                    :class="[props.row.show_type === 'show' ? 'common-icon-eye-show' : 'common-icon-eye-hide color-org']"
                                                    v-bk-tooltips="{
                                                        content: props.row.show_type === 'show' ? $t('必填') : $t('非必填'),
                                                        placements: ['bottom']
                                                    }">
                                                </i>
                                            </div>
                                        </bk-table-column>
                                        <bk-table-column :label="$t('操作')" width="80">
                                            <template slot-scope="props">
                                                <bk-link
                                                    :theme="props.row.source_type === 'system' ? 'default' : 'primary'"
                                                    :disabled="isViewMode || props.row.source_type === 'system'"
                                                    @click="openVariablePanel(props.row)">
                                                    {{ $t('编辑') }}
                                                </bk-link>
                                            </template>
                                        </bk-table-column>
                                    </bk-table>
                                </div>
                            </bk-popover>
                        </div>
                        <!-- 快捷操作按钮 -->
                        <div v-if="!isViewMode" class="quick-insert-btn" @click="quickOperateVariableVisable = true">
                            {{ $t('变量快捷处理') }}
                            <quick-operate-variable
                                v-if="quickOperateVariableVisable"
                                :variable-list="variableList"
                                @closePanel="quickOperateVariableVisable = false">
                            </quick-operate-variable>
                        </div>
                    </template>
                </template>
            </div>
            <template slot="content">
                <!-- 插件/子流程选择面板 -->
                <select-panel
                    v-if="isSelectorPanelShow"
                    :project_id="project_id"
                    :template-labels="templateLabels"
                    :node-config="nodeConfig"
                    :atom-type-list="atomTypeList"
                    :basic-info="basicInfo"
                    :common="common"
                    :is-third-party="isThirdParty"
                    :plugin-loading="pluginLoading"
                    @back="isSelectorPanelShow = false"
                    @viewSubflow="onViewSubflow"
                    @select="onPluginOrTplChange">
                </select-panel>
                <!-- 变量编辑面板 -->
                <div v-else-if="isVariablePanelShow" class="variable-edit-panel">
                    <variable-edit
                        ref="variableEdit"
                        :variable-data="variableData"
                        :common="common"
                        @closeEditingPanel="isVariablePanelShow = false"
                        @onSaveEditing="isVariablePanelShow = false">
                    </variable-edit>
                </div>
                <!-- 插件/子流程表单面板 -->
                <template v-else>
                    <div class="node-config" v-bkloading="{ isLoading: isSubflow && subflowListLoading, opacity: 1 }">
                        <template v-if="!isSubflow || !subflowListLoading">
                            <div class="config-form">
                                <!-- 基础信息 -->
                                <section class="config-section" data-test-id="templateEdit_form_nodeBaseInfo">
                                    <h3>{{$t('基础信息')}}</h3>
                                    <div class="basic-info-wrapper" v-bkloading="{ isLoading: isBaseInfoLoading }">
                                        <template v-if="!isBaseInfoLoading">
                                            <basic-info
                                                ref="basicInfo"
                                                :basic-info="basicInfo"
                                                :node-config="nodeConfig"
                                                :version-list="versionList"
                                                :is-subflow="isSubflow"
                                                :input-loading="inputLoading"
                                                :project-id="project_id"
                                                :form-enable="formEnable"
                                                :common="common"
                                                :subflow-updated="subflowUpdated"
                                                :is-view-mode="isViewMode"
                                                @openSelectorPanel="isSelectorPanelShow = true"
                                                @versionChange="versionChange"
                                                @selectScheme="onSelectSubflowScheme"
                                                @viewSubflow="onViewSubflow"
                                                @updateSubflowVersion="updateSubflowVersion"
                                                @update="updateBasicInfo">
                                            </basic-info>
                                        </template>
                                    </div>
                                </section>
                                <!-- 输入参数 -->
                                <section class="config-section" data-test-id="templateEdit_form_inputParamsInfo">
                                    <h3>
                                        {{$t('输入参数')}}
                                        <i
                                            v-if="isSubflow"
                                            v-bk-tooltips="{
                                                width: 500,
                                                placement: 'bottom-end',
                                                content: $t('如果选中执行方案更新增加了新的变量，请打开对应的子流程节点进行填写；在不打开子流程节点进行填写的情况下，会使用变量默认值')
                                            }"
                                            class="bk-icon icon-question-circle section-tips">
                                        </i>
                                    </h3>
                                    <p class="citations-waivers-guide">
                                        <bk-popover placement="top-end" theme="light" width="258" :ext-cls="'citations-waivers-guide-tip'">
                                            <i class="bk-icon icon-info-circle-shape"></i>
                                            {{ $t('设置为变量&变量免渲染使用指引') }}
                                            <div slot="content">
                                                <p>{{ $t('设置为变量：将节点的输入或输出设置为全局变量，可供其他节点使用') }}</p><br>
                                                <p>{{ $t('变量免渲染：忽略参数中的全局变量，将${}视为普通字符串') }}</p>
                                            </div>
                                        </bk-popover>
                                    </p>
                                    <div class="inputs-wrapper" v-bkloading="{ isLoading: inputLoading, zIndex: 100 }">
                                        <template v-if="!inputLoading">
                                            <template v-if="Array.isArray(inputs)">
                                                <input-params
                                                    v-if="inputs.length > 0"
                                                    ref="inputParams"
                                                    :node-id="nodeId"
                                                    :scheme="inputs"
                                                    :plugin="basicInfo.plugin"
                                                    :version="basicInfo.version"
                                                    :subflow-forms="subflowForms"
                                                    :forms-not-referred="formsNotReferred"
                                                    :value="inputsParamValue"
                                                    :render-config="inputsRenderConfig"
                                                    :is-subflow="isSubflow"
                                                    :is-view-mode="isViewMode"
                                                    :constants="localConstants"
                                                    :third-party-code="isThirdParty ? basicInfo.plugin : ''"
                                                    @hookChange="onHookChange"
                                                    @renderConfigChange="onRenderConfigChange"
                                                    @update="updateInputsValue">
                                                </input-params>
                                                <no-data v-else></no-data>
                                            </template>
                                            <template v-else>
                                                <jsonschema-input-params
                                                    v-if="inputs.properties && Object.keys(inputs.properties).length > 0"
                                                    :inputs="inputs"
                                                    :value="inputsParamValue"
                                                    @update="updateInputsValue">
                                                </jsonschema-input-params>
                                                <no-data v-else></no-data>
                                            </template>
                                        </template>
                                    </div>
                                </section>
                                <!-- 输出参数 -->
                                <section class="config-section" data-test-id="templateEdit_form_outputParamsInfo">
                                    <h3>{{$t('输出参数')}}</h3>
                                    <div class="outputs-wrapper" v-bkloading="{ isLoading: outputLoading, zIndex: 100 }">
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
                                            <no-data v-else></no-data>
                                        </template>
                                    </div>
                                </section>
                            </div>
                            <div class="btn-footer">
                                <bk-button
                                    v-if="!isViewMode"
                                    theme="primary"
                                    :disabled="inputLoading || (isSubflow && subflowListLoading)"
                                    data-test-id="templateEdit_form_saveNodeConfig"
                                    @click="onSaveConfig">
                                    {{ $t('保存') }}
                                </bk-button>
                                <bk-button
                                    theme="default"
                                    data-test-id="templateEdit_form_cancelNodeConfig"
                                    @click="onClosePanel()">
                                    {{ $t('取消') }}
                                </bk-button>
                            </div>
                        </template>
                    </div>
                </template>
            </template>
        </bk-sideslider>
        <bk-dialog
            width="480"
            ext-cls="cancel-global-variable-dialog"
            header-position="left"
            :mask-close="false"
            v-model="isCancelGloVarDialogShow"
            :title="$t('取消变量引用')">
            <p style="word-break: break-all;">{{ $t('全局变量【 x 】的引用数已为 0。如果不再使用，可立即删除变量; 也可以稍后在全局变量面板中删除', { key: unhookingVarForm.key })}}</p>
            <template slot="footer">
                <bk-button theme="primary" @click="deleteUnhookingVar">{{ $t('删除变量') }}</bk-button>
                <bk-button @click="onCancelVarConfirmClick">{{ $t('以后再说') }}</bk-button>
            </template>
        </bk-dialog>
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
    import SelectPanel from './SelectPanel/index.vue'
    import VariableEdit from '../TemplateSetting/TabGlobalVariables/VariableEdit.vue'
    import QuickOperateVariable from '../../common/QuickOperateVariable.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import bus from '@/utils/bus.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'NodeConfig',
        components: {
            BasicInfo,
            InputParams,
            JsonschemaInputParams,
            OutputParams,
            SelectPanel,
            VariableEdit,
            NoData,
            QuickOperateVariable
        },
        mixins: [permission],
        props: {
            project_id: [String, Number],
            nodeId: String,
            isShow: Boolean,
            isShowSelect: Boolean,
            atomList: Array,
            subflowList: Array,
            atomTypeList: Object,
            templateLabels: Array,
            common: [String, Number],
            subflowListLoading: Boolean,
            backToVariablePanel: Boolean,
            pluginLoading: Boolean,
            isViewMode: Boolean,
            formEnable: Boolean
        },
        data () {
            return {
                subflowUpdated: false, // 子流程是否更新
                taskNodeLoading: false, // 普通任务节点数据加载
                subflowLoading: false, // 子流程任务节点数据加载
                constantsLoading: false, // 子流程输入参数配置项加载
                subflowVersionUpdating: false, // 子流程更新
                isCancelGloVarDialogShow: false, // 取消勾选全局变量
                nodeConfig: {}, // 任务节点的完整 activity 配置参数
                isBaseInfoLoading: true, // 基础信息loading
                basicInfo: {}, // 基础信息模块
                versionList: [], // 标准插件版本
                inputs: [], // 输入参数表单配置项
                inputsParamValue: {}, // 输入参数值
                inputsRenderConfig: {}, // 输入参数是否配置渲染豁免
                outputs: [], // 输出参数
                subflowForms: {}, // 子流程输入参数
                formsNotReferred: {}, // 未被子流程引用的全局变量
                isSelectorPanelShow: false, // 是否显示选择插件(子流程)面板
                isVariablePanelShow: false, // 是否显示变量编辑面板
                variableData: {}, // 当前编辑的变量
                localConstants: {}, // 全局变量列表，用来维护当前面板勾选、反勾选后全局变量的变化情况，保存时更新到 store
                randomKey: new Date().getTime(), // 输入、输出参数勾选状态改变时更新popover
                isThirdParty: false, // 是否为第三方插件
                quickOperateVariableVisable: false,
                variableCited: {}, // 全局变量被任务节点、网关节点以及其他全局变量引用情况
                unhookingVarForm: {}, // 正被取消勾选的表单配置
                isUpdateConstants: false // 是否更新输入参数配置
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
            isSubflow () {
                return this.nodeConfig.type !== 'ServiceActivity'
            },
            atomGroup () { // 某一标准插件下所有版本分组
                return this.atomList.find(item => item.code === this.basicInfo.plugin)
            },
            inputLoading () { // 以下任一方法处于 pending 状态，输入参数展示 loading 效果
                return this.isBaseInfoLoading || this.taskNodeLoading || this.subflowLoading || this.constantsLoading || this.subflowVersionUpdating
            },
            outputLoading () {
                return this.isBaseInfoLoading || this.taskNodeLoading || this.subflowLoading
            },
            selectorTitle () {
                return this.isSubflow ? i18n.t('选择子流程') : i18n.t('选择标准插件')
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
            subflowListLoading (val) {
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
                console.log(nodeConfig)
                const isThirdParty = nodeConfig.component && nodeConfig.component.code === 'remote_plugin'
                if (nodeConfig.type === 'ServiceActivity') {
                    await this.setThirdPartyList(nodeConfig)
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
            async setThirdPartyList (nodeConfig) {
                try {
                    // 设置第三发插件缓存
                    const thirdPartyList = this.$parent.thirdPartyList
                    if (nodeConfig.component
                        && nodeConfig.component.code === 'remote_plugin'
                        && !thirdPartyList[this.nodeId]) {
                        const resp = await this.loadPluginServiceMeta({ plugin_code: nodeConfig.component.data.plugin_code.value })
                        const { code, versions, description } = resp.data
                        const versionList = versions.map(version => {
                            return { version }
                        })
                        const { data } = nodeConfig.component
                        let version = data && data.plugin_version
                        version = version && version.value
                        const group = {
                            code,
                            list: versionList,
                            version,
                            desc: description
                        }
                        thirdPartyList[this.nodeId] = group
                    }
                } catch (error) {
                    console.warn(error)
                    this.isBaseInfoLoading = false
                }
            },
            // 初始化节点数据
            async initData () {
                if (!this.basicInfo.plugin && !this.basicInfo.tpl) { // 未选择插件
                    return
                }
                if (!this.isSubflow) {
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
                    await this.getSubflowDetail(tpl, version)
                    this.inputs = await this.getSubflowInputsConfig()
                    this.inputsParamValue = this.getSubflowInputsValue(forms)
                    this.inputsRenderConfig = renderConfig
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
                        const { outputs: respsOutputs, forms, inputs } = resp.data
                        // 获取不同版本的描述
                        let desc = resp.data.desc || ''
                        if (desc && desc.includes('\n')) {
                            const descList = desc.split('\n')
                            desc = descList.join('<br>')
                        }
                        this.updateBasicInfo({ desc })
                        if (forms.renderFrom) {
                            if (!this.isSubflow) {
                                // 获取第三方插件公共输出参数
                                if (!this.pluginOutput['remote_plugin']) {
                                    await this.loadAtomConfig({ atom: 'remote_plugin', version: '1.0.0' })
                                }
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
            async getSubflowDetail (tpl, version = '') {
                this.subflowLoading = true
                try {
                    const params = {
                        template_id: tpl,
                        scheme_id_list: this.basicInfo.schemeIdList,
                        version
                    }
                    if (this.isCommonTpl) {
                        params.template_source = 'common'
                    } else {
                        params.project_id = this.project_id
                    }
                    const resp = await this.loadSubflowConfig(params)
                    // 子流程的输入参数包括流程引用的变量、自定义变量和未被引用的变量
                    this.subflowForms = { ...resp.data.pipeline_tree.constants, ...resp.data.custom_constants, ...resp.data.constants_not_referred }
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
                    if (component.code) {
                        if (component.code === 'remote_plugin') {
                            const atom = this.$parent.thirdPartyList[this.nodeId]
                            code = component.data.plugin_code.value
                            const resp = await this.loadPluginServiceAppDetail({ plugin_code: code })
                            basicInfoName = resp.data.name
                            version = atom.version
                            desc = atom.desc
                        } else {
                            const atom = this.atomList.find(item => item.code === component.code)
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
                        const subflowInfo = this.atomTypeList.subflow.find(item => item.template_id === Number(template_id))
                        if (subflowInfo) {
                            templateName = subflowInfo.name
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
                if (!code) {
                    return []
                }
                let atom
                if (isThirdParty) {
                    atom = this.$parent.thirdPartyList[this.nodeId]
                    return atom && atom.list
                } else {
                    atom = this.atomList.find(item => item.code === code)
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
                return Object.keys(this.localConstants).some(key => {
                    const varItem = this.localConstants[key]
                    const sourceInfo = varItem.source_info[this.nodeId]
                    return sourceInfo && sourceInfo.includes(form.tag_code)
                })
            },
            /**
             * 变量 key 复制
             */
            onCopyKey (key) {
                this.copyText = key
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            /**
             * 复制操作回调函数
             */
            copyHandler (e) {
                e.preventDefault()
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                this.$bkMessage({
                    message: i18n.t('已复制'),
                    theme: 'success'
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
                this.isSelectorPanelShow = false
                this.isThirdParty = val.id === 'remote_plugin'
                if (this.isSubflow) {
                    await this.$parent.getProcessOpenChd(val)
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
                    const atom = this.atomList.find(item => item.code === code)
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
                this.inputsRenderConfig = this.inputs.reduce((acc, crt) => {
                    acc[crt.tag_code] = true
                    return acc
                }, {})
                this.$refs.basicInfo && this.$refs.basicInfo.validate() // 清除节点保存报错时的错误信息
            },
            /**
             * 标准插件版本切换
             */
            async versionChange (val) {
                // 获取不同版本的描述
                let desc = this.basicInfo.desc
                if (!this.isThirdParty) {
                    const atom = this.atomList.find(item => item.code === this.basicInfo.plugin)
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
                this.inputsRenderConfig = this.inputs.reduce((acc, crt) => {
                    acc[crt.tag_code] = true
                    return acc
                }, {})
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
                    selectable: true,
                    alwaysUseLatest: false,
                    schemeIdList: []
                }
                this.updateBasicInfo(config)
                if ('project' in data && typeof data.project.id === 'number') {
                    this.$set(this.nodeConfig, 'template_source', 'business')
                } else {
                    this.$set(this.nodeConfig, 'template_source', 'common')
                }
                await this.getSubflowDetail(id, version)
                this.inputs = await this.getSubflowInputsConfig()
                this.inputsParamValue = this.getSubflowInputsValue(this.subflowForms)
                this.inputsRenderConfig = Object.keys(this.subflowForms).reduce((acc, crt) => {
                    const formItem = this.subflowForms[crt]
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
                this.subflowVersionUpdating = true
                const oldForms = Object.assign({}, this.subflowForms)
                await this.getSubflowDetail(this.basicInfo.tpl)
                await this.subflowUpdateParamsChange()
                this.inputs = await this.getSubflowInputsConfig()
                this.subflowVersionUpdating = false
                this.$nextTick(() => {
                    this.inputsParamValue = this.getSubflowInputsValue(this.subflowForms, oldForms)
                    this.inputsRenderConfig = Object.keys(this.subflowForms).reduce((acc, crt) => {
                        const formItem = this.subflowForms[crt]
                        if (formItem.show_type === 'show') {
                            acc[crt] = 'need_render' in formItem ? formItem.need_render : true
                        }
                        return acc
                    }, {})
                    this.subflowUpdated = true
                })
            },
            /**
             * 子流程版本更新后，输入、输出参数如果有变更，需要处理全局变量的 source_info 更新
             * 分为两种情况：
             * 1.输入、输出参数被勾选，并且对应变量在新流程模板中被删除或者变量 source_tag 有更新，需要在更新后修改全局变量 source_info 信息
             * 2.新增和修改输入、输出参数，不做处理
             */
            async subflowUpdateParamsChange () {
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
                                const newTplVar = this.subflowForms[nodeFormItem]

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
            async clearParamsSourceInfo () {
                this.isUpdateConstants = true
                this.variableCited = await this.getVariableCitedData() || {}
                const nodeId = this.nodeConfig.id
                for (const key in this.localConstants) {
                    const varItem = this.localConstants[key]
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
                this.variableCited = {}
                this.isUpdateConstants = false
            },
            // 查看子流程模板
            onViewSubflow (id) {
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
            async onSelectSubflowScheme () {
                const oldForms = Object.assign({}, this.subflowForms)
                await this.getSubflowDetail(this.basicInfo.tpl, this.basicInfo.version)
                await this.subflowUpdateParamsChange()
                this.inputs = await this.getSubflowInputsConfig()
                this.$nextTick(() => {
                    this.inputsParamValue = this.getSubflowInputsValue(this.subflowForms, oldForms)
                    this.inputsRenderConfig = Object.keys(this.subflowForms).reduce((acc, crt) => {
                        const formItem = this.subflowForms[crt]
                        if (formItem.show_type === 'show') {
                            acc[crt] = 'need_render' in formItem ? formItem.need_render : true
                        }
                        return acc
                    }, {})
                })
            },
            // 是否渲染豁免切换
            onRenderConfigChange (data) {
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
                        // 切换插件/切换版本/更新子流程时直接删除引用量为1变量
                        if (this.isUpdateConstants) {
                            this.deleteUnhookingVar()
                        } else {
                            this.isCancelGloVarDialogShow = true
                        }
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
                        const refDom = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                        refDom && refDom.setFromData()
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
                refDom && refDom.setFromData({ ...this.unhookingVarForm })
                this.isCancelGloVarDialogShow = false
            },
            onCancelVarConfirmClick () {
                const { key, source } = this.unhookingVarForm
                const constant = this.localConstants[key]
                constant.source_info = {}
                const refDom = source === 'input' ? this.$refs.inputParams : this.$refs.outputParams
                refDom && refDom.setFromData({ ...this.unhookingVarForm })
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
                if (this.isSubflow) {
                    const { nodeName, stageName, nodeLabel, selectable, alwaysUseLatest, schemeIdList, version, tpl, executor_proxy, retryable, skippable, ignorable, autoRetry, timeoutConfig } = this.basicInfo
                    const constants = {}
                    Object.keys(this.subflowForms).forEach(key => {
                        const constant = this.subflowForms[key]
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
                        scheme_id_list: schemeIdList,
                        retryable,
                        skippable,
                        error_ignorable: ignorable,
                        auto_retry: autoRetry,
                        timeout_config: timeoutConfig,
                        enable: this.formEnable
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
                this.atomList.some(group => {
                    if (group.code === this.basicInfo.plugin) {
                        return group.list.some(item => {
                            if (item.version === (this.basicInfo.version || 'legacy')) {
                                phase = item.phase
                            }
                        })
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
                    if (!(this.isSubflow ? this.basicInfo.tpl : this.basicInfo.plugin)) {
                        this.onClosePanel()
                        return true
                    }
                }
                if (this.isVariablePanelShow) { // 变量编辑时，点击遮罩需要确认是否保存变量
                    this.$refs.variableEdit.handleMaskClick()
                    return false
                }
                const config = this.getNodeFullConfig()
                if (tools.isDataEqual(config, this.nodeConfig) && !this.isOutputsChanged()) {
                    this.onClosePanel()
                    return true
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        cancelFn: () => {
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
                                desc, nodeName, autoRetry, timeoutConfig, executor_proxy
                        } = this.basicInfo
                        const nodeData = { status: '', skippable, retryable, optional, auto_retry: autoRetry, timeout_config: timeoutConfig }
                        if (this.common) {
                            nodeData['executor_proxy'] = executor_proxy.join(',')
                        }
                        if (!this.isSubflow) {
                            const phase = this.getAtomPhase()
                            nodeData.phase = phase
                        } else {
                            if (this.subflowUpdated || alwaysUseLatest) {
                                this.setSubprocessUpdated({
                                    expired: false,
                                    subprocess_node_id: this.nodeConfig.id
                                })
                            }
                            if (!alwaysUseLatest && latestVersion && latestVersion !== version) {
                                this.setSubprocessUpdated({ expired: true, subprocess_node_id: this.nodeConfig.id })
                            }
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
                this.$emit('close', openVariablePanel)
            }
        }
    }
</script>
<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
.node-config-panel {
    height: 100%;
    .config-header {
        position: relative;
        display: flex;
        align-items: center;
        .go-back {
            display: flex;
            align-items: center;
            &.active {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .quick-insert-btn {
            position: absolute;
            top: 14px;
            right: 20px;
            font-weight: normal;
            line-height: 19px;
            font-size: 14px;
            padding: 6px 13px;
            background: #f0f1f5;
            border-radius: 4px;
            cursor: pointer;
        }
        .view-variable {
            position: absolute;
            top: 20px;
            right: 140px;
            font-size: 14px;
            line-height: 19px;
            font-weight: normal;
            &:hover {
                color: #3a84ff;
            }
            &.r30 {
                right: 30px;
            }
        }
        .variable-back-icon {
            font-size: 32px;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
    .node-config {
        height: calc(100vh - 60px);
        overflow: hidden;
        .config-form {
            padding: 20px 30px 0 30px;
            height: calc(100% - 49px);
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
        position: relative;
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
        .citations-waivers-guide {
            position: absolute;
            right: 0;
            top: 0;
            color: #979ba5;
            font-size: 12px;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
        .basic-info-wrapper {
            min-height: 250px;
        }
        .inputs-wrapper,
        .outputs-wrapper {
            min-height: 80px;
        }
        .section-tips {
            font-size: 16px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    .bk-sideslider-content {
        overflow: initial;
    }
    .variable-edit-panel {
        height: calc(100vh - 60px);
        overflow: hidden;
    }
}
</style>
<style lang="scss">
    .variable-popover {
        .tippy-tooltip {
            padding: 0;
            .tippy-arrow {
                border: none;
            }
        }
        .variable-list {
            width: 536px;
            background: #ffffff;
            border: 1px solid #dcdee5;
            box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.2);
            /deep/ .bk-table-body-wrapper {
                overflow-y: auto;
            }
            .icon-wrap {
                i {
                    margin-right: 4px;
                    color: #219f42;
                    font-size: 14px;
                }
                .color-org {
                    color: #de9524;
                }
            }
            .header-area {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 14px;
                height: 48px;
                & > span {
                    font-size: 14px;
                    color: #313238;
                }
                i {
                    font-size: 18px;
                }
            }
            .bk-link-text {
                font-size: 12px;
            }
        }
        td {
            position: relative;
            &:hover {
                .copy-icon {
                    display: inline-block;
                }
            }
        }
        .copy-icon {
            display: none;
            position: absolute;
            top: 14px;
            right: 2px;
            font-size: 14px;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
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
