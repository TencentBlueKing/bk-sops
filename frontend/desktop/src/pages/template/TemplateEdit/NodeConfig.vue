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
    <div class="node-config" @click="e => e.stopPropagation()">
        <div>
            <bk-sideslider
                ref="nodeConfigPanel"
                :ext-cls="configClassString"
                :width="711"
                :is-show="isShow"
                :before-close="onBeforeClose"
                :quick-close="true">
                <div slot="header">
                    <span>{{ i18n.baseInfo }}</span>
                </div>
                <template slot="content">
                    <div class="basic-info">
                        <div class="section-form basic-info-form">
                            <div class="form-item form-name">
                                <label class="required">{{ atomNameType }}</label>
                                <div class="form-content">
                                    <bk-select
                                        v-model="currentAtom"
                                        class="node-select"
                                        :searchable="true"
                                        :clearable="false"
                                        :disabled="atomConfigLoading"
                                        @selected="onAtomSelect">
                                        <bk-option
                                            v-for="(option, index) in atomList"
                                            :key="option.id"
                                            :id="option.id"
                                            :name="option.name">
                                            <template v-if="!isSingleAtom">
                                                <span class="subflow-option-name">{{option.name}}</span>
                                                <i class="bk-icon common-icon-box-top-right-corner" @click.stop="onJumpToProcess(index)"></i>
                                            </template>
                                        </bk-option>
                                    </bk-select>
                                    <!-- 标准插件节点说明 -->
                                    <i class="common-icon-info desc-tooltip"
                                        v-if="atomDesc"
                                        v-bk-tooltips="{
                                            content: atomDesc,
                                            width: '400',
                                            placements: ['bottom-end'] }">
                                    </i>
                                    <!-- 子流程版本更新 -->
                                    <i
                                        :class="[
                                            'common-icon-clock-inversion',
                                            'update-tooltip',
                                            {
                                                'disabled': atomConfigLoading
                                            }
                                        ]"
                                        v-if="subflowHasUpdate"
                                        v-bk-tooltips="{
                                            content: i18n.update,
                                            placements: ['bottom-end'] }"
                                        @click="onUpdateSubflowVersion">
                                    </i>
                                    <span v-show="taskTypeEmpty" class="common-error-tip error-msg">{{ atomNameType + i18n.typeEmptyTip}}</span>
                                </div>
                            </div>
                            <div v-if="isSingleAtom" class="form-item">
                                <label class="required">{{ i18n.version_name }}</label>
                                <div class="form-content">
                                    <bk-select
                                        v-model="currentVersion"
                                        class="node-select"
                                        :searchable="true"
                                        :clearable="false"
                                        @selected="onVersionSelect">
                                        <bk-option
                                            v-for="option in currentVersionList"
                                            :key="option.version"
                                            :id="option.version"
                                            :name="option.version">
                                        </bk-option>
                                    </bk-select>
                                    <span v-show="taskVersionEmpty" class="common-error-tip error-msg">{{ i18n.version_name + i18n.typeEmptyTip}}</span>
                                </div>
                            </div>
                            <div class="form-item">
                                <label class="required">{{ i18n.node_name }}</label>
                                <div class="form-content">
                                    <bk-input
                                        v-model="nodeName"
                                        name="nodeName"
                                        class="node-name"
                                        v-validate="nodeNameRule" />
                                    <span v-show="errors.has('nodeName')" class="common-error-tip error-msg">{{ errors.first('nodeName') }}</span>
                                </div>
                            </div>
                            <div class="form-item">
                                <label>{{ i18n.stage_tag }}</label>
                                <div class="form-content">
                                    <bk-input v-model="stageName" name="stageName" class="stage-name" v-validate="stageNameRule" />
                                    <span v-show="errors.has('stageName')" class="common-error-tip error-msg">{{ errors.first('stageName') }}</span>
                                </div>
                            </div>
                            <div class="form-item" v-if="isSingleAtom">
                                <label>{{ i18n.failureHandling }}</label>
                                <div class="form-content error-handler">
                                    <bk-checkbox
                                        v-model="errorCouldBeIgnored"
                                        @change="onIgnoredChange">
                                        <div class="checkbox-text-wrapper">
                                            <i class="common-icon-dark-circle-i"></i>
                                            <span class="checkbox-text">{{i18n.ignore}}</span>
                                        </div>
                                    </bk-checkbox>
                                    <bk-checkbox v-model="isSkip" :disabled="isManulHandleErrrorDisable">
                                        <div class="checkbox-text-wrapper">
                                            <i class="common-icon-dark-circle-s"></i>
                                            <span class="checkbox-text">{{i18n.manuallySkip}}</span>
                                        </div>
                                    </bk-checkbox>
                                    <bk-checkbox v-model="isRetry" :disabled="isManulHandleErrrorDisable">
                                        <div class="checkbox-text-wrapper">
                                            <i class="common-icon-dark-circle-r"></i>
                                            <span class="checkbox-text">{{i18n.manuallyRetry}}</span>
                                        </div>
                                    </bk-checkbox>
                                    <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                                        <p>
                                            {{ i18n.failureHandlingIgnore }}
                                        </p>
                                        <p>
                                            {{ i18n.failureHandlingSkip }}
                                        </p>
                                        <p>
                                            {{ i18n.failureHandlingRetry }}
                                        </p>
                                    </div>
                                    <i v-bk-tooltips="htmlConfig" ref="tooltipsHtml" class="common-icon-info ui-failure-info"></i>
                                    <span v-show="manuallyEmpty" class="error-handler-warning-tip common-warning-tip">{{ i18n.manuallyEmpty}}</span>
                                </div>
                            </div>
                            <div class="form-item">
                                <label>{{ i18n.optional }}</label>
                                <div class="form-content">
                                    <bk-switcher
                                        size="small"
                                        v-model="nodeCouldBeSkipped">
                                    </bk-switcher>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="inputs-info">
                        <div class="node-title">
                            <span>{{ i18n.input }}</span>
                        </div>
                        <div class="section-form inputs-info-form" v-bkloading="{ isLoading: atomConfigLoading, opacity: 1 }">
                            <RenderForm
                                ref="renderForm"
                                v-if="!atomConfigLoading && renderInputConfig && renderInputConfig.length"
                                :scheme="renderInputConfig"
                                :form-data="renderInputData.value"
                                :form-option="renderInputOption"
                                :hooked="renderInputData.hook"
                                @change="onInputDataChange"
                                @onHookChange="onInputHookChange">
                            </RenderForm>
                            <div class="no-data-wrapper" v-else>
                                <NoData></NoData>
                            </div>
                        </div>
                    </div>
                    <div class="outputs-info">
                        <div class="node-title">
                            <span>{{ i18n.output }}</span>
                        </div>
                        <div class="section-form outputs-info-form" v-bkloading="{ isLoading: atomConfigLoading, opacity: 1 }">
                            <table class="outputs-table" v-if="renderOutputData && renderOutputData.length">
                                <thead>
                                    <tr>
                                        <th class="output-name">{{ i18n.name }}</th>
                                        <th class="output-key">KEY</th>
                                        <th class="output-checkbox">{{ i18n.refer }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="item in renderOutputData" :key="item.key">
                                        <td class="output-name">{{item.name}}</td>
                                        <td class="output-key">{{item.key}}</td>
                                        <td class="output-checkbox">
                                            <span
                                                v-bk-tooltips="{
                                                    content: item.hook ? i18n.cancelHook : i18n.hook,
                                                    placements: ['left'] }">
                                                <bk-checkbox :value="item.hook" @change="onOutputHookChange(item.name, item.key, $event)"></bk-checkbox>
                                            </span>

                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div class="no-data-wrapper" v-else>
                                <NoData />
                            </div>
                        </div>
                    </div>
                </template>
            </bk-sideslider>
        </div>
        <ReuseVarDialog
            :is-reuse-var-dialog-show="isReuseVarDialogShow"
            :reuse-variable="reuseVariable"
            :reuseable-var-list="reuseableVarList"
            @onConfirmReuseVar="onConfirmReuseVar"
            @onCancelReuseVar="onCancelReuseVar">
        </ReuseVarDialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import Vue from 'vue'
    import { mapActions, mapState, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import atomFilter from '@/utils/atomFilter.js'
    import formSchema from '@/utils/formSchema.js'
    import { random4 } from '@/utils/uuid.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'

    const varKeyReg = /^\$\{(\w+)\}$/

    /**
     * notice：provide为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
     */
    const reactiveNodeId = Vue.observable({ id: '' })

    export default {
        /**
         * notice：provide为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
         */
        provide () {
            return {
                node: reactiveNodeId
            }
        },
        name: 'NodeConfig',
        components: {
            NoData,
            RenderForm,
            ReuseVarDialog
        },
        props: [
            'isNodeConfigPanelShow',
            'isSettingPanelShow',
            'settingActiveTab',
            'singleAtom',
            'subAtom',
            'idOfNodeInConfigPanel',
            'template_id',
            'common',
            'project_id',
            'isShow'
        ],
        data () {
            return {
                i18n: {
                    baseInfo: gettext('基础信息'),
                    flow: gettext('流程模板'),
                    node_name: gettext('节点名称'),
                    version_name: gettext('插件版本'),
                    version: gettext('版本'),
                    stage_tag: gettext('步骤名称'),
                    ignore: gettext('自动忽略'),
                    optional: gettext('是否可选'),
                    input: gettext('输入参数'),
                    output: gettext('输出参数'),
                    name: gettext('名称'),
                    refer: gettext('引用'),
                    hook: gettext('勾选参数作为全局变量'),
                    cancelHook: gettext('取消勾选'),
                    typeEmptyTip: gettext('不能为空'),
                    update: gettext('版本更新'),
                    manuallySkip: gettext('手动跳过'),
                    manuallyRetry: gettext('手动重试'),
                    failureHandling: gettext('失败处理'),
                    details: gettext('说明：'),
                    failureHandlingIgnore: gettext('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。'),
                    failureHandlingSkip: gettext('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。'),
                    failureHandlingRetry: gettext('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。'),
                    manuallyEmpty: gettext('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续')
                },
                htmlConfig: {
                    allowHtml: true,
                    width: 400,
                    trigger: 'mouseenter',
                    theme: 'dark',
                    content: '#html-error-ingored-tootip',
                    placement: 'bottom-end'
                },
                atomConfigLoading: false,
                errorCouldBeIgnored: false,
                nodeCouldBeSkipped: false,
                subflowHasUpdate: false, // 是否显示子流程更新 icon
                bkMessageInstance: null,
                subAtomConfigData: {
                    form: {},
                    outputs: {}
                },
                nodeConfigData: null,
                reuseVariable: {},
                isReuseVarDialogShow: false,
                taskTypeEmpty: false,
                taskVersionEmpty: false,
                reuseableVarList: [],
                nodeId: this.idOfNodeInConfigPanel,
                nodeName: '',
                stageName: gettext('步骤1'),
                currentAtom: '',
                currentVersion: '',
                subAtomInput: [],
                subAtomOutput: [],
                renderInputOption: {
                    showGroup: false,
                    showHook: true,
                    showLabel: true,
                    showVarList: true
                },
                inputAtomHook: {},
                inputAtomData: undefined,
                nodeNameRule: {
                    required: true,
                    max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                stageNameRule: {
                    max: STRING_LENGTH.STAGE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isAtomChanged: false, // 用于切换标准插件
                failureHandling: [], // 失败处理
                isSkip: true, // 是否手动跳过
                isRetry: true, // 是否手动重试
                manuallyEmpty: false // 手动选项为空
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'location': state => state.template.location,
                'atomForm': state => state.atomForm.form,
                'atomFormConfig': state => state.atomForm.config,
                'atomFormOutput': state => state.atomForm.output,
                'subprocessInfo': state => state.template.subprocess_info,
                'SingleAtomVersionMap': state => state.atomForm.SingleAtomVersionMap
            }),
            /**
             * 标准插件节点、子节点列表
             */
            atomList () {
                if (this.isSingleAtom) {
                    const setGroup = []
                    const atomVersionGroup = []
                    this.singleAtom.forEach(atom => {
                        const code = atom.code
                        const index = setGroup.indexOf(code)
                        if (index > -1) {
                            const group = atomVersionGroup[index]
                            if (group.version < atom.version || group.version === 'legacy') {
                                group.version = atom.version
                            }
                            group.list.push(atom)
                        } else {
                            const item = {
                                id: code,
                                name: atom.group_name + '-' + atom.name,
                                list: [atom],
                                version: atom.version
                            }
                            setGroup.push(code)
                            atomVersionGroup.push(item)
                        }
                    })
                    return atomVersionGroup
                } else {
                    return this.subAtom.filter(item => {
                        return item.template_id !== Number(this.template_id)
                    }).map(item => {
                        return {
                            id: item.template_id,
                            name: item.name,
                            templateSource: item.template_source
                        }
                    })
                }
            },
            /**
             * 当前插件版本列表
             */
            currentVersionList () {
                let list = []
                this.atomList.some(atoms => {
                    if (atoms.id === this.currentAtom) {
                        list = atoms.list
                        return true
                    }
                })
                return list
            },
            /**
             * 标准插件节点描述
             */
            atomDesc () {
                if (
                    this.singleAtom
                    && this.atomForm[this.currentAtom]
                    && this.atomForm[this.currentAtom][this.currentVersion]
                ) {
                    return this.atomForm[this.currentAtom][this.currentVersion].desc
                }
                return ''
            },
            isSingleAtom () { // normal task node or subflow node
                return this.nodeConfigData && this.nodeConfigData.type === 'ServiceActivity'
            },
            atomNameType () {
                return this.isSingleAtom ? gettext('标准插件') : gettext('流程模板')
            },
            /**
             * 输出参数数据
             */
            renderOutputData () {
                const outputData = []
                const outputConfig = this.getOutputConfig()
                
                outputConfig.forEach(item => {
                    let hook = false
                    let key = item.key
                    for (const cKey in this.constants) {
                        const constant = this.constants[cKey]
                        if (constant.source_type === 'component_outputs'
                            && constant.source_info[this.nodeId]
                            && constant.source_info[this.nodeId].indexOf(key) > -1
                        ) {
                            hook = true
                            key = cKey
                        }
                    }
                    outputData.push({
                        name: item.name,
                        key,
                        hook
                    })
                })
                /**
                 * notice：兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
                 */
                if (this.currentAtom === 'job_execute_task') {
                    for (const cKey in this.constants) {
                        const constant = this.constants[cKey]
                        if ((this.nodeId in constant.source_info)
                            && constant.source_type === 'component_outputs'
                            && outputData.findIndex(item => item.key === cKey) === -1
                        ) {
                            outputData.push({
                                name: constant.name,
                                key: cKey,
                                hook: true
                            })
                        }
                    }
                }
                return outputData
            },
            /**
             * 输入参数表单配置项
             */
            renderInputConfig () {
                if (this.isSingleAtom) {
                    if (!this.currentAtom
                        || JSON.stringify(this.atomFormConfig) === '{}'
                        || !this.atomFormConfig[this.currentAtom]) {
                        return []
                    }
                    return this.getSingleAtomConfig()
                } else {
                    return this.subAtomInput
                }
            },
            /**
             * 输入参数数据
             */
            renderInputData () {
                const hook = this.inputAtomHook
                const value = this.inputAtomData
                return {
                    hook,
                    value
                }
            },
            groupInfo () {
                if (this.isSingleAtom && this.currentAtom) {
                    return this.singleAtom.find(item => item.code === this.currentAtom)
                }
                return {}
            },
            // 任务节点执行失败手动处理选项禁用
            isManulHandleErrrorDisable () {
                return this.errorCouldBeIgnored
            },
            // 动态设置面板的 class
            configClassString () {
                let base = 'common-template-setting-sideslider node-config-panel'
                if (this.isSettingPanelShow) {
                    if (this.settingActiveTab === 'globalVariableTab') {
                        base += ' position-right-var'
                    } else if (this.settingActiveTab === 'templateDataEditTab') {
                        base += ' position-right-tempalte-data-edit'
                    } else {
                        base += ' position-right-tempalte-config'
                    }
                }
                return base
            }
        },
        watch: {
            // 打开节点或切换节点
            idOfNodeInConfigPanel (val) {
                if (!val) return
                this.nodeId = val

                /**
                 * notice：provide为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
                 */
                reactiveNodeId.id = val

                // 清空验证
                this.currentVersion = ''
                this.taskTypeEmpty = false
                this.subflowHasUpdate = false
                this.taskVersionEmpty = false
                this.errors.clear()

                this.initData()
                this.$nextTick(() => {
                    // 只验证错误节点（正确节点关闭时会验证）
                    if (
                        document.querySelector(`#${val} .task-node.failed`)
                        || document.querySelector(`#${val} .subflow-node.failed`)
                    ) {
                        this.$validator.validateAll()
                        this.taskTypeEmpty = !this.currentAtom
                        this.taskVersionEmpty = !this.currentVersion
                    }
                })
            },
            isRetry (val) {
                this.manuallyEmpty = !val && !this.isSkip && !this.errorCouldBeIgnored
            },
            isSkip (val) {
                this.manuallyEmpty = !this.isRetry && !val && !this.errorCouldBeIgnored
            }
        },
        created () {
            this.initData()
        },
        mounted () {
            document.body.addEventListener('click', this.handleNodeConfigPanelShow, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('click', this.handleNodeConfigPanelShow, false)
        },
        methods: {
            ...mapMutations('atomForm/', [
                'setAtomConfig'
            ]),
            ...mapMutations('template/', [
                'addVariable',
                'deleteVariable',
                'setActivities',
                'setVariableSourceInfo',
                'setSubprocessUpdated'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadSubflowConfig'
            ]),
            initData () {
                this.nodeConfigData = tools.deepClone(this.activities[this.nodeId])
                if (this.nodeConfigData) {
                    this.getNodeFormData() // get template activity information
                    if (this.isSingleAtom) {
                        const component = this.nodeConfigData.component
                        const version = component.version || this.SingleAtomVersionMap[component.code]
                        if (version) {
                            this.getConfig(this.nodeConfigData.component.version)
                            this.currentVersion = version
                        }
                    } else {
                        this.getConfig(this.nodeConfigData.version) // load node config data
                    }
                }
            },
            /**
             * 加载标准插件配置文件或子流程表单配置
             * @param {String} version 子流程版本/标准插件配置文件版本
             */
            async getConfig (version) {
                if ((typeof this.currentAtom === 'string' && this.currentAtom !== '')
                    || (typeof this.currentAtom === 'number' && !isNaN(this.currentAtom))) {
                    if (this.isSingleAtom) {
                        await this.getAtomConfig(this.currentAtom, version)
                    } else {
                        await this.getSubflowConfig(this.currentAtom, version)
                    }
                    this.$nextTick(() => {
                        this.markInvalidForm()
                    })
                } else {
                    this.markInvalidForm()
                }
            },
            /**
             * 加载标准插件节点数据
             */
            async getAtomConfig (atomType, version) {
                this.atomConfigLoading = true
                if (atomFilter.isConfigExists(atomType, version, this.atomFormConfig)) {
                    this.setNodeConfigData(atomType, version)
                    this.$nextTick(() => {
                        this.atomConfigLoading = false
                    })
                    return
                }
                try {
                    await this.loadAtomConfig({ atomType, version })

                    // 节点配置面板收起后，不执行后续回调逻辑
                    if (!this.isNodeConfigPanelShow) {
                        return
                    }
                    this.setAtomConfig({ atomType, configData: $.atoms[atomType], version })
                    this.setNodeConfigData(atomType, version)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            /**
             * 加载子流程节点数据
             * @param {Number} id 子流程模板 id
             * @param {String} version 子流程版本 若不传
             */
            async getSubflowConfig (id, version) {
                this.atomConfigLoading = true
                this.nodeConfigData.template_id = id
                try {
                    this.subAtomConfigData = await this.loadSubflowConfig({ templateId: id, version, common: this.common })
                    // 节点配置面板收起后，不执行后续回调逻辑
                    if (!this.isNodeConfigPanelShow) {
                        return
                    }
                    const constants = {}
                    const inputConfig = []
                    const outputConfig = []
                    let variableArray = []
                    this.nodeConfigData.version = this.subAtomConfigData.version
                    // 检查流程是否更新，有更新则显示更新按钮
                    if (
                        this.subprocessInfo
                        && this.subprocessInfo.details
                    ) {
                        this.subprocessInfo.details.some(subflow => {
                            if (
                                subflow.expired
                                && subflow.template_id === Number(this.currentAtom)
                                && subflow.subprocess_node_id === this.nodeId
                            ) {
                                this.subflowHasUpdate = true
                            }
                        })
                    }

                    for (const cKey in this.subAtomConfigData.form) {
                        const variable = tools.deepClone(this.subAtomConfigData.form[cKey])
                        if (variable.show_type === 'show') {
                            variableArray.push(variable)
                        }
                    }
                    variableArray = variableArray.sort((a, b) => {
                        return a.index - b.index
                    })
                    // 遍历加载标准插件表单配置文件
                    for (const form of variableArray) {
                        const { key } = form
                        const { atomType, atom, tagCode, classify } = atomFilter.getVariableArgs(form)
                        // 全局变量版本
                        const version = form.version || 'legacy'
                        if (!atomFilter.isConfigExists(atomType, version, this.atomFormConfig)) {
                            await this.loadAtomConfig({ atomType, classify, version, saveName: atom })
                        }
                        const atomConfig = this.atomFormConfig[atom][version]
                        let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))

                        if (currentFormConfig) {
                            if (form.is_meta || currentFormConfig.meta_transform) {
                                currentFormConfig = currentFormConfig.meta_transform(form.meta || form)
                                if (!form.meta) {
                                    form.value = currentFormConfig.attrs.value
                                }
                            }
                            currentFormConfig.tag_code = key
                            currentFormConfig.attrs.name = this.subAtomConfigData.form[key].name

                            if (
                                this.subAtomConfigData.form[key].custom_type === 'input'
                                && this.subAtomConfigData.form[key].validation !== ''
                            ) {
                                currentFormConfig.attrs.validation.push({
                                    type: 'regex',
                                    args: this.subAtomConfigData.form[key].validation,
                                    error_message: gettext('默认值不符合正则规则：') + this.subAtomConfigData.form[key].validation
                                })
                            }
                            inputConfig.push(currentFormConfig)
                        }
                        // 子流程表单项的取值
                        // 首次添加、子流程切换、子流程更新时，取接口返回的 form
                        // 编辑时，取 activities 里对应的全局变量 form
                        constants[key] = this.activities[this.nodeId].constants[key] || form
                    }
                    this.$set(this.nodeConfigData, 'constants', tools.deepClone(constants))
                    for (const key in this.subAtomConfigData.outputs) {
                        const output = this.subAtomConfigData.outputs[key]
                        const item = {
                            key,
                            name: output.name
                        }
                        outputConfig.push(item)
                    }
                    this.subAtomInput = inputConfig
                    this.subAtomOutput = outputConfig
                    this.getNodeFormData()
                    this.$nextTick(() => {
                        this.updateActivities()
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            /**
             * normal task node render form value
             */
            setNodeConfigData (atomType, version) {
                const data = {}
                const config = this.atomFormConfig[atomType][version]
                if (atomType === this.activities[this.nodeId].component.code) {
                    this.nodeConfigData = tools.deepClone(this.activities[this.nodeId])
                } else {
                    config.forEach(item => {
                        data[item.tag_code] = {
                            hook: false
                        }
                    })
                    this.$set(this.nodeConfigData, 'component', {
                        code: atomType,
                        data
                    })
                }
                // 暂时注释
                // this.getNodeFormData()
                this.$nextTick(() => {
                    this.updateActivities()
                })
            },
            /**
             * configure node config fields
             */
            getNodeFormData () {
                const formData = tools.deepClone(this.nodeConfigData)
                this.nodeName = formData.name
                this.stageName = formData.stage_name
                this.nodeCouldBeSkipped = formData.optional
                this.isSkip = formData.isSkipped || formData.skippable
                this.isRetry = formData.can_retry || formData.retryable
                const inputFormHooks = {}
                const inputFormData = {}
                if (this.isSingleAtom) {
                    const data = tools.deepClone(formData.component.data)
                    this.currentAtom = formData.component.code || ''
                    this.errorCouldBeIgnored = formData.error_ignorable
                    for (const form in data) {
                        inputFormHooks[form] = data[form].hook || false
                        if ('value' in data[form]) {
                            inputFormData[form] = tools.deepClone(data[form].value)
                        }
                    }
                } else {
                    this.currentAtom = parseInt(formData.template_id)
                    for (const key in formData.constants) {
                        const form = formData.constants[key]
                        const tagCode = key.match(varKeyReg)[1]
                        form.hook = this.iskeyInSourceInfo(key, tagCode)
                        inputFormHooks[key] = form.hook
                        if ('value' in form) {
                            inputFormData[key] = tools.deepClone(form.value)
                        }
                    }
                }
                this.inputAtomHook = inputFormHooks
                this.inputAtomData = inputFormData
            },
            getSingleAtomConfig () {
                // 当前版本或最新版本
                const config = this.atomFormConfig[this.currentAtom][this.currentVersion]
                if (!config) {
                    return {}
                }
                return config.map(item => {
                    return {
                        variableKey: item.tag_code,
                        ...item
                    }
                })
            },
            getOutputConfig () {
                const version = this.currentVersion
                if (this.isSingleAtom) {
                    return (this.atomFormOutput
                        && this.currentAtom
                        && this.atomFormOutput[this.currentAtom]
                        && this.atomFormOutput[this.currentAtom][version])
                        || []
                } else {
                    return this.subAtomOutput || []
                }
            },
            getHookedInputVariables () {
                const variables = []
                for (const key in this.renderInputData.hook) {
                    if (this.renderInputData.hook[key]) {
                        const variableKey = this.inputAtomData[key]
                        variables.push({
                            variableKey,
                            formKey: key,
                            id: this.nodeId,
                            tagCode: varKeyReg.test(key) ? key.match(varKeyReg)[1] : key,
                            version: this.getVariableVersion(variableKey, 'input')
                        })
                    }
                }
                return variables
            },
            /**
             * the key is in the source_info field
             */
            iskeyInSourceInfo (key, tagCode) {
                for (const cKey in this.constants) {
                    const constant = this.constants[cKey]
                    const sourceInfo = JSON.stringify(constant.source_info)
                    if (
                        constant.source_type === 'component_inputs'
                        && sourceInfo
                        && (sourceInfo.indexOf(tagCode) > -1 || sourceInfo.indexOf(key) > -1)
                    ) {
                        return true
                    }
                }
                return false
            },
            /**
             * 处理节点配置面板和全局变量面板之外的点击事件
             */
            handleNodeConfigPanelShow (e) {
                // 节点参数面板未展开、有变量复用弹窗遮罩
                if (!this.isNodeConfigPanelShow || this.isReuseVarDialogShow) {
                    return
                }

                // 处理在面板区域里的 popup 上的点击，eg: select、tooltip
                const settingPanel = document.querySelector('.setting-area-wrap')
                const nodeConfig = document.querySelector('.node-config')
                const nodeConfigPanel = document.querySelector('.node-config-panel.bk-sideslider')
                const clientX = document.body.clientWidth
                const { left, right, top, bottom } = nodeConfigPanel.getBoundingClientRect()
                const baseRight = this.isSettingPanelShow ? clientX : right
                if (
                    (e.clientX === 0 || e.clientY === 0)
                    || (e.clientX > left
                    && e.clientX < baseRight
                    && e.clientY > top
                    && e.clientY < bottom)
                ) {
                    return
                }
                if (settingPanel && this.isNodeConfigPanelShow) {
                    // 节点配置面板 和 settingPanel 重叠
                    if (clientX < 1920 && !dom.nodeContains(nodeConfig, e.target)) {
                        this.subflowHasUpdate = false
                        this.syncNodeDataToActivities()
                    }
                    // 节点配置面板 和 settingPanel 并排
                    if (clientX >= 1920
                        && !dom.nodeContains(settingPanel, e.target)
                        && !dom.nodeContains(nodeConfig, e.target)) {
                        this.subflowHasUpdate = false
                        this.syncNodeDataToActivities()
                    }
                }
            },
            /**
             * 同步配置面板数据到store
             */
            syncNodeDataToActivities () {
                this.updateActivities()
                return this.updateNodeInfo()
            },
            updateActivities () {
                if (this.atomConfigLoading) {
                    return
                }
                const nodeData = tools.deepClone(this.nodeConfigData)
                nodeData.name = this.nodeName
                nodeData.stage_name = this.stageName
                nodeData.optional = this.nodeCouldBeSkipped
                
                if (this.isSingleAtom) {
                    nodeData.skippable = this.isSkip || false // 兼容脏数据该字段不存在
                    nodeData.retryable = this.isRetry || false // 兼容脏数据改字段不存在
                    nodeData.error_ignorable = this.errorCouldBeIgnored
                    nodeData.component.version = this.currentVersion
                    // can_retry、isSkipped 为就数据字段，点开编辑保存时删除
                    delete nodeData.can_retry
                    delete nodeData.isSkipped

                    for (const key in this.inputAtomData) {
                        nodeData.component.data[key] = {
                            hook: this.inputAtomHook[key] || false,
                            value: tools.deepClone(this.inputAtomData[key]) || ''
                        }
                    }
                } else {
                    const constants = tools.deepClone(this.subAtomConfigData.form)
                    for (const key in this.inputAtomData) {
                        constants[key] && (constants[key].value = tools.deepClone(this.inputAtomData[key]))
                    }
                    nodeData.constants = constants
                }
                // 任务节点参数编辑时，可能会修改输入输出连线，取最新的连线数据，防止被节点参数编辑时保存的旧数据覆盖
                const { incoming, outgoing } = this.activities[this.nodeId]
                Object.assign(nodeData, { incoming, outgoing })

                this.setActivities({ type: 'edit', location: nodeData })
            },
            /**
             * 更新节点信息，校验表单参数
             */
            updateNodeInfo () {
                let isValid = true
                return this.$validator.validateAll().then(result => {
                    let status = ''
                    let formValid = true
                    if (!this.currentAtom) {
                        this.taskTypeEmpty = true
                    }
                    if (!this.currentVersion) {
                        this.taskVersionEmpty = true
                    }
                    if (this.$refs.renderForm) {
                        formValid = this.$refs.renderForm.validate()
                    }
                    if (!this.currentAtom || !result || !formValid) {
                        isValid = false
                        status = 'FAILED'
                    }
                    this.$emit('onUpdateNodeInfo', this.nodeId, {
                        status,
                        name: this.nodeName,
                        mode: 'edit',
                        stage_name: this.stageName,
                        optional: this.nodeCouldBeSkipped,
                        error_ignorable: this.errorCouldBeIgnored,
                        retryable: this.isRetry,
                        skippable: this.isSkip,
                        group: this.groupInfo.group_name,
                        icon: this.groupInfo.group_icon
                    })
                    // 清空配置信息
                    this.subAtomConfigData = {
                        form: {},
                        outputs: {}
                    }
                    this.subAtomInput = []
                    this.subAtomOutput = []

                    this.$emit('hideConfigPanel')
                    return isValid
                })
            },
            markInvalidForm () {
                const nodeEl = this.location.find(item => item.id === this.idOfNodeInConfigPanel)
                if (nodeEl && !this.isAtomChanged) {
                    const status = nodeEl.status
                    if (status === 'FAILED') {
                        this.$validator.validateAll()
                        this.$refs.renderForm && this.$refs.renderForm.validate()
                        if (!this.currentAtom) {
                            this.taskTypeEmpty = true
                        }
                        if (!this.currentVersion) {
                            this.taskVersionEmpty = true
                        }
                    }
                }
            },
            /**
             * 切换标准插件节点，清空勾选的变量
             */
            clearHookedVaribles (hookedInputs, outputs) {
                hookedInputs.forEach(item => {
                    const { id, variableKey, formKey } = item
                    const variable = this.constants[variableKey]
                    this.setVariableSourceInfo({ type: 'delete', id, key: variableKey, tagCode: formKey })
                    if (variable && !Object.keys(variable.source_info).length) {
                        this.removeFromGlobal(variableKey)
                    }
                })
                this.taskTypeEmpty = false
                this.taskVersionEmpty = false
                outputs.forEach(item => {
                    if (item.hook) {
                        this.removeFromGlobal(item.key)
                    }
                })
            },
            onAtomSelect (id) {
                this.isAtomChanged = true
                const optionList = this.isSingleAtom ? this.atomList : this.subAtom
                const data = tools.deepClone(optionList.find(option => option.id === id))
                const currentAtomlastVeriosn = this.SingleAtomVersionMap[id]
                let nodeName
                this.clearHookedVaribles(this.getHookedInputVariables(), this.renderOutputData)
                this.currentAtom = id
                if (this.isSingleAtom) {
                    nodeName = data.name.split('-').slice(1).join().replace(/\s/g, '')
                    this.currentVersion = currentAtomlastVeriosn
                    this.nodeConfigData.skippable = true
                    this.nodeConfigData.retryable = true
                    this.nodeConfigData.error_ignorable = false
                } else {
                    // 切换子流程时，去掉节点小红点、刷新按钮、节点过期设为 false
                    this.$emit('onUpdateNodeInfo', this.idOfNodeInConfigPanel, { hasUpdated: false })
                    this.subflowHasUpdate = false
                    this.setSubprocessUpdated({
                        template_id: Number(this.currentAtom),
                        subprocess_node_id: this.idOfNodeInConfigPanel
                    })
                    nodeName = data.name.replace(/\s/g, '')
                    this.subAtomConfigData.form = {}
                }
                this.inputAtomHook = {}
                this.inputAtomData = {}
                this.nodeName = nodeName
                this.nodeConfigData.name = nodeName
                this.updateActivities()
                // 如果是单原子，这里取最新版本配置
                this.getConfig(currentAtomlastVeriosn)
                this.$nextTick(() => {
                    this.isAtomChanged = false
                })
            },
            /**
             * 版本选择
             * @param {String} id version
             */
            onVersionSelect (id) {
                this.isAtomChanged = true
                this.clearHookedVaribles(this.getHookedInputVariables(), this.renderOutputData)
                this.inputAtomHook = {}
                this.inputAtomData = {}
                this.updateActivities()
                this.getConfig(id)
                this.$nextTick(() => {
                    this.isAtomChanged = false
                })
            },
            onJumpToProcess (index) {
                const { id, templateSource } = this.atomList[index]
                const url = {
                    name: 'templatePanel',
                    params: { type: 'edit', project_id: this.project_id },
                    query: { template_id: id }
                }
                if (templateSource === 'common') {
                    url.name = 'commonTemplatePanel'
                }
                const { href } = this.$router.resolve(url)
                window.open(href, '_blank')
            },
            /**
             * 更新子流程版本
             * 去掉节点小红点、模板刷新按钮
             * 更新 store 数据状态
             */
            async onUpdateSubflowVersion () {
                if (this.atomConfigLoading) {
                    return
                }
                const oldInputAtomHook = { ...this.inputAtomHook }
                const oldInputAtomData = { ...this.inputAtomData }
                const oldConstants = { ...this.subAtomConfigData.form }

                // 清空 store 里的 constants 值
                this.subAtomConfigData.form = {}
                this.inputAtomHook = {}
                this.inputAtomData = {}
                this.updateActivities()

                await this.getSubflowConfig(this.currentAtom)
                Object.keys(oldInputAtomData).forEach(key => {
                    const newContants = { ...this.subAtomConfigData.form }
                    const newVar = newContants[key]
                    const oldVar = oldConstants[key]

                    /**
                     * 子流程更新后保留用户当前编辑的子流程变量的值，保留条件：
                     * 1.变量 key 相同
                     * 2.变量类型相同
                     *   - 变量为标准插件勾选的全局变量，需要满足 source_tag 相同（来自于同一个标准插件的表单项）
                     *   - 变量为自定义全局变量，需要满足变量的 custom_type 相同
                     */
                    if (newVar) {
                        const { custom_type: newCustomType, source_tag: newSourceTag } = newVar
                        const { custom_type: oldCustomType, source_tag: oldSourceTag } = oldVar
                        const canReplace = (newCustomType || oldCustomType) ? newCustomType === oldCustomType : newSourceTag === oldSourceTag
                        if (canReplace) {
                            this.$set(this.inputAtomData, key, oldInputAtomData[key])
                        }
                    }

                    if (oldInputAtomHook[key]) {
                        const variable = [
                            {
                                variableKey: key,
                                formKey: key,
                                id: this.nodeId,
                                tagCode: key,
                                version: this.getVariableVersion(oldInputAtomHook[key], 'input')
                            }
                        ]
                        this.clearHookedVaribles(variable, [])
                    }
                })
                this.updateActivities()
                this.subflowHasUpdate = false
                this.$emit('onUpdateNodeInfo', this.idOfNodeInConfigPanel, { hasUpdated: false })
                this.setSubprocessUpdated({
                    template_id: Number(this.currentAtom),
                    subprocess_node_id: this.idOfNodeInConfigPanel,
                    version: this.subAtomConfigData.version
                })
            },
            /**
             * 输入参数值更新
             */
            onInputDataChange (val) {
                this.inputAtomData = val
            },
            /**
             * 获取勾选 tag 的版本
             * @description
             * 1. [标准插件]勾选 取当前插件版本
             * 2.[子流程]勾选对应 tag 版本取原始 tag 版本 || 没有设置为 legacy
             * @param {String} variableKey key
             */
            getVariableVersion (variableKey, type) {
                if (this.isSingleAtom) {
                    return this.currentVersion
                } else if (type === 'input') {
                    return (this.subAtomConfigData.form[variableKey] && this.subAtomConfigData.form[variableKey].version) || 'legacy'
                } else if (type === 'outinput') {
                    return (this.subAtomConfigData.outputs[variableKey] && this.subAtomConfigData.outputs[variableKey].version) || 'legacy'
                }
            },
            // 输入参数勾选、反勾选
            onInputHookChange (tagCode, val) {
                let key, source_tag, source_info, custom_type, value
                let validation = ''
                // 变量 key 值，统一格式为 ${xxx}
                let variableKey = varKeyReg.test(tagCode) ? tagCode : '${' + tagCode + '}'
                const formConfig = this.renderInputConfig.filter(item => {
                    return item.tag_code === tagCode
                })[0]
                const name = formConfig.attrs.name.replace(/\s/g, '')
                const variableVersion = this.getVariableVersion(variableKey, 'input')
                if (this.isSingleAtom) {
                    key = tagCode
                    source_tag = this.nodeConfigData.component.code
                        + '.'
                        + tagCode
                    source_info = { [this.nodeId]: [tagCode] }
                    custom_type = ''
                    value = tools.deepClone(this.inputAtomData[tagCode])
                } else {
                    const variable = this.subAtomConfigData.form[variableKey]
                    key = variableKey
                    tagCode = tagCode.match(varKeyReg)[1]
                    source_info = { [this.nodeId]: [variableKey] }
                    source_tag = variable.source_tag
                    custom_type = variable.custom_type
                    value = tools.deepClone(this.inputAtomData[key])
                    if (formConfig.type !== 'combine') {
                        validation = variable.validation
                    }
                }
                this.$set(this.inputAtomHook, key, val)

                if (val) { // hooked
                    const variableList = []
                    if (!source_tag) { // custom variable not include ip selector
                        const variableOpts = {
                            name, key: variableKey, source_info, custom_type, value, validation, version: variableVersion
                        }
                        this.$set(this.inputAtomData, key, variableKey)
                        this.hookToGlobal(variableOpts)
                        return
                    }
                    // 获取全局变量中已有的 key + version 相同项列表
                    for (const cKey in this.constants) {
                        const constant = this.constants[cKey]
                        const sVersion = constant.version
                        const sTag = constant.source_tag
                        if (sTag) {
                            const tCode = sTag.split('.')[1]
                            tCode === tagCode && sVersion === variableVersion && variableList.push({
                                name: `${constant.name}(${constant.key})`,
                                id: constant.key
                            })
                        }
                    }
                    const isKeyUsedInConstants = variableKey in this.constants
                    /**
                     * 复用变量（全局变量中有key + version 都相同的项）
                     * 新建变量（全局变量中有key相同version不同的项）
                     */
                    if (variableList.length) { // input arguments include ip selector have same soure_tag
                        this.reuseVariable = { name, key, source_tag, source_info, value, validation, useNewKey: false }
                        this.reuseableVarList = variableList
                        this.isReuseVarDialogShow = true
                    } else if (isKeyUsedInConstants) { // the variable's key is used in other global variable
                        this.reuseVariable = { name, key, source_tag, source_info, value, validation, useNewKey: true }
                        this.reuseableVarList = variableList
                        this.isReuseVarDialogShow = true
                    } else {
                        const variableOpts = {
                            name, key: variableKey, source_tag, source_info, custom_type, value, validation, version: variableVersion
                        }
                        // 全局变量添加 form_schema
                        const atomType = source_tag.split('.')[0]
                        variableOpts.form_schema = formSchema.getSchema(
                            tagCode,
                            this.atomFormConfig[atomType][variableVersion]
                        )

                        this.$set(this.inputAtomData, key, variableKey)
                        this.hookToGlobal(variableOpts) // input arguments hook
                    }
                } else { // cancel hook
                    variableKey = this.inputAtomData[key] // variable key
                    const variable = this.constants[variableKey]
                    if (!variable) {
                        return
                    }
                    const formKey = this.isSingleAtom ? tagCode : key // input arguments form item key
                    this.inputAtomHook[formKey] = val
                    this.inputAtomData[formKey] = tools.deepClone(this.constants[variableKey].value)
                    this.setVariableSourceInfo({ type: 'delete', id: this.nodeId, key: variableKey, tagCode: formKey })
                    if (variable && !Object.keys(variable.source_info).length) {
                        this.removeFromGlobal(variableKey)
                    }
                }
            },
            onOutputHookChange (name, key, checked) {
                if (checked) {
                    const variableKey = this.generateRandomKey(key)
                    const variableOpts = {
                        name,
                        key: variableKey,
                        source_type: 'component_outputs',
                        source_info: {
                            [this.nodeId]: [key]
                        },
                        source_tag: '',
                        custom_type: '',
                        show_type: 'hide',
                        version: this.getVariableVersion(key, 'output')
                    }
                    this.renderOutputData.some(item => {
                        if (item.key === key) {
                            this.$set(item, 'key', variableKey)
                            return true
                        }
                    })
                    this.hookToGlobal(variableOpts)
                } else {
                    const constant = this.constants[key]
                    if (constant) {
                        this.removeFromGlobal(key)
                    }
                }
            },
            /**
             * 参数不复用，创建新变量
             */
            hookToGlobal (variableOpts) {
                const len = Object.keys(this.constants).length
                const defaultOpts = {
                    name: '',
                    key: '',
                    desc: '',
                    custom_type: '',
                    source_info: {},
                    source_tag: '',
                    value: '',
                    show_type: 'show',
                    source_type: 'component_inputs',
                    validation: '',
                    index: len,
                    version: 'legacy'
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.addVariable(Object.assign({}, variable))
                this.$emit('globalVariableUpdate', true)
            },
            removeFromGlobal (key) {
                this.deleteVariable(key)
                this.$emit('globalVariableUpdate', true)
            },
            generateRandomKey (key) {
                let variableKey = key.replace(/^\$\{/, '').replace(/(\}$)/, '').slice(0, 14)
                do {
                    variableKey = '${' + variableKey + '_' + random4() + '}'
                } while (this.constants[variableKey])
                return variableKey
            },
            // 变量复用弹窗确认
            onConfirmReuseVar (variableConfig) {
                const { type, name, key, varKey, source_tag, source_info, value } = variableConfig
                if (type === 'create') { // create new variable
                    if (this.constants[varKey]) {
                        this.$bkMessage({
                            message: gettext('变量KEY已存在'),
                            theme: 'error'
                        })
                        return
                    }

                    this.$set(this.inputAtomHook, varKey, true)
                    this.$set(this.inputAtomData, key, varKey)
                    const variableOpts = { name, key: varKey, source_tag, source_info, value }
                    // 全局变量添加 form_schema
                    const atomType = source_tag.split('.')[0]
                    const version = this.getVariableVersion(key, 'input')
                    variableOpts.form_schema = formSchema.getSchema(
                        key,
                        this.atomFormConfig[atomType][version]
                    )

                    this.hookToGlobal(variableOpts)
                } else {
                    this.$set(this.inputAtomHook, varKey, true)
                    this.$set(this.inputAtomData, key, varKey)
                    this.setVariableSourceInfo({ type: 'add', id: this.nodeId, key: varKey, tagCode: key, value })
                }

                this.isReuseVarDialogShow = false
            },
            onCancelReuseVar (reuseVariable) {
                const { key } = reuseVariable
                this.inputAtomHook[key] = false
                this.isReuseVarDialogShow = false
            },
            onDeleteConstant (constant) {
                const { source_info, source_type, value } = constant
                if (source_type === 'component_inputs') {
                    const quotedByParams = source_info[this.nodeId]
                    if (quotedByParams) {
                        quotedByParams.forEach(item => {
                            let key = item
                            if (!this.isSingleAtom) {
                                key = varKeyReg.test(item) ? item : '${' + item + '}'
                            }
                            this.inputAtomHook[key] = false
                            this.inputAtomData[key] = tools.deepClone(value)
                        })
                    }
                }
            },
            onIgnoredChange (updatedValue) {
                this.manuallyEmpty = !updatedValue
                this.isSkip = false
                this.isRetry = false
                this.errorCouldBeIgnored = updatedValue
            },
            // 关闭配置面板
            onBeforeClose () {
                this.subflowHasUpdate = false
                this.syncNodeDataToActivities()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/clearfix.scss';
@import '@/scss/mixins/scrollbar.scss';
.node-config-panel {
    top: 59px;
    left: calc(100% - 767px);
    width: 711px;
    z-index: 5;
    box-shadow: -4px 0 6px -4px rgba(0, 0, 0, 0.15);
    transition: left 0.3s ease-in-out;
    /deep/ .bk-sideslider-content {
        padding: 20px;
        overflow: scroll;
        @include scrollbar;
    }
    &.position-right-var {
        @media screen and (min-width: 1920px) {
            left: calc(100% - 1568px);
        }
    }
    &.position-right-tempalte-config {
        left: calc(100% - 1188px);
    }
    &.position-right-tempalte-data-edit{
        @media screen and (min-width: 1920px) {
            left: calc(100% - 1608px);
        }
    }
    .node-title {
        height: 54px;
        line-height: 54px;
        border-bottom: 1px solid #dcdee5;
        span {
            font-size: 14px;
            font-weight:600;
            color:#313238;
        }
    }
    .basic-info-form {
        .error-handler {
            position: relative;
            height: 32px;
            line-height: 32px;
        }
        .desc-tooltip,
        .update-tooltip,
        .error-ingored-tootip {
            position: absolute;
            right: 0;
            top: 8px;
            color: #c4c6cc;
            cursor: pointer;
            &:not(.disabled):hover {
                color: #f4aa1a;
            }
            &.disabled {
                color: #c4c6cc;
                cursor: not-allowed;
            }
        }
        .error-ingored-tootip {
            right: -30px;
        }
        .common-icon-dark-circle-i,
        .common-icon-dark-circle-s,
        .common-icon-dark-circle-r {
            padding-right: 4px;
            color: #a6b0c7;
        }
        .checkbox-text-wrapper {
            display: flex;
            align-items: center;
            .checkbox-text {
                font-size: 12px;
            }
        }
        .error-handler-warning-tip {
            position: absolute;
            top: 22px;
            left: 0;
            font-size: 12px;
        }
        .bk-switcher {
            top: 5px;
        }
    }
}
// 子流程选择下拉框字号
.form-item {
    margin-bottom: 20px;
    @include clearfix;
    &:last-child {
        margin-bottom: 0;
    }
    & > label {
        position: relative;
        float: left;
        margin-top: 8px;
        width: 100px;
        font-size: 12px;
        color: $greyDefault;
        text-align: right;
        &.required:before {
            content: '*';
            position: absolute;
            top: 0px;
            right: -10px;
            color: $redDark;
            font-family: "SimSun";
        }
    }
    .form-content {
        margin-left: 120px;
        margin-right: 30px;
        .bk-form-checkbox {
            width: 150px;
            padding-right: 11px;
        }
        .common-icon-info {
            display: inline-block;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .ui-failure-info {
            vertical-align: middle;
        }
    }
    &.form-name {
        position: relative;
        .desc-tooltip {
            right: 0;
            top: 6px;
        }
        .update-tooltip {
            right: 0;
            top: 9px;
        }
    }
}
.section-form {
    padding: 20px 0 40px;
}
.inputs-info {
    /deep/ .render-form {
        .rf-form-item {
            .rf-tag-label {
                color: $greyDefault;
            }
        }
        & > .rf-form-item,
        .rf-form-group > .rf-form-item {
            & > .rf-tag-form {
                margin-right: 30px;
            }
        }
    }

}
.outputs-info-form {
    padding-bottom: 0;
    .outputs-table {
        width: 100%;
        border: 1px solid $commonBorderColor;
        border-collapse: collapse;
        th, td {
            padding: 10px;
            font-size: 12px;
            font-weight: normal;
            border: 1px solid $commonBorderColor;
            text-align: center;
        }
        th {
            background: $whiteThinBg;
            font-weight: bold;
        }
        .output-name {
            width: 50%;
        }
        .output-checkbox {
            width: 20%;
        }
    }
}
.common-icon-box-top-right-corner {
    position: absolute;
    right: 0;
    top: 0;
    margin-top: 10px;
    margin-right: 10px;
}
</style>
