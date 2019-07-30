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
        <div
            :class="['node-config-panel',{ 'position-right-side': !isSettingPanelShow }]">
            <div class="node-title">
                <span>{{ i18n.baseInfo }}</span>
            </div>
            <div class="basic-info">
                <div class="section-form basic-info-form">
                    <div class="form-item form-name">
                        <label class="required">{{ atomNameType }}</label>
                        <div class="form-content">
                            <bk-select
                                v-model="currentAtom"
                                class="bk-select-inline"
                                :searchable="true"
                                @selected="onAtomSelect">
                                <bk-option
                                    v-for="(option, index) in atomList"
                                    :key="index"
                                    :id="option.id"
                                    :name="option.name">
                                    <span v-if="!isSingleAtom" class="bk-option-name">{{option.name}}</span>
                                    <i v-if="!isSingleAtom" class="bk-icon common-icon-box-top-right-corner" @click.stop="onJumpToProcess(index)"></i>
                                </bk-option>
                            </bk-select>
                            <!-- 标准插件节点说明 -->
                            <i class="bk-icon icon-info-circle desc-tooltip"
                                v-if="atomDesc"
                                v-bk-tooltips="{
                                    content: atomDesc,
                                    width: '400',
                                    placements: ['left'] }">
                            </i>
                            <!-- 子流程版本更新 -->
                            <i class="common-icon-clock-inversion update-tooltip"
                                v-if="subflowHasUpdate"
                                v-bk-tooltips="{
                                    content: i18n.update,
                                    placements: ['left'] }"
                                @click="onUpdateSubflowVersion">
                            </i>
                            <span v-show="taskTypeEmpty" class="common-error-tip error-msg">{{ atomNameType + i18n.typeEmptyTip}}</span>
                        </div>
                    </div>
                    <div class="form-item">
                        <label class="required">{{ i18n.node_name }}</label>
                        <div class="form-content">
                            <BaseInput v-model="nodeName" name="nodeName" v-validate="nodeNameRule" />
                            <span v-show="errors.has('nodeName')" class="common-error-tip error-msg">{{ errors.first('nodeName') }}</span>
                        </div>
                    </div>
                    <div class="form-item">
                        <label>{{ i18n.stage_tag }}</label>
                        <div class="form-content">
                            <BaseInput v-model="stageName" name="stageName" v-validate="stageNameRule" />
                            <span v-show="errors.has('stageName')" class="common-error-tip error-msg">{{ errors.first('stageName') }}</span>
                        </div>
                    </div>
                    <div class="form-item" v-if="isSingleAtom">
                        <label>{{ i18n.failureHandling }}</label>
                        <div class="form-content">
                            <el-checkbox
                                v-model="errorCouldBeIgnored"
                                @change="onIgnoredChange">
                                <i class="common-icon-dark-circle-i"></i>
                                {{i18n.ignore}}
                            </el-checkbox>
                            <el-checkbox
                                :disabled="isDisable"
                                v-model="isSkip">
                                <i class="common-icon-dark-circle-s"></i>
                                {{i18n.manuallySkip}}
                            </el-checkbox>
                            <el-checkbox
                                :disabled="isDisable"
                                v-model="isRetry">
                                <i class="common-icon-dark-circle-r"></i>
                                {{i18n.manuallyRetry}}
                            </el-checkbox>
                            <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                                <p>
                                    {{ i18n.failureHandlingDetails1 }}
                                </p>
                                <p>
                                    {{ i18n.failureHandlingDetails2 }}
                                </p>
                                <p>
                                    {{ i18n.failureHandlingDetails3 }}
                                </p>
                            </div>
                            <i v-bk-tooltips="htmlConfig" ref="tooltipsHtml" class="bk-icon icon-info-circle"></i>
                            <span v-show="manuallyEmpty" class="common-warning-tip">{{ i18n.manuallyEmpty}}</span>
                        </div>
                    </div>
                    <div class="form-item">
                        <label>{{ i18n.optional }}</label>
                        <div class="form-content">
                            <bk-switcher
                                on-text="ON"
                                off-text="OFF"
                                :show-text="showText"
                                :selected="nodeCouldBeSkipped"
                                @change="onSkippedChange">
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
        </div>
        <ReuseVarDialog
            v-if="isReuseVarDialogShow"
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
    import { mapActions, mapState, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import atomFilter from '@/utils/atomFilter.js'
    import { random4 } from '@/utils/uuid.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'

    const varKeyReg = /^\$\{(\w+)\}$/

    export default {
        /**
         * notice：provide为了兼容“job-执行作业（job_execute_task）标准插件”动态添加输出参数
         */
        provide () {
            return {
                nodeId: this.idOfNodeInConfigPanel
            }
        },
        name: 'NodeConfig',
        components: {
            NoData,
            RenderForm,
            BaseInput,
            ReuseVarDialog
        },
        props: [
            'isNodeConfigPanelShow',
            'isSettingPanelShow',
            'singleAtom',
            'subAtom',
            'idOfNodeInConfigPanel',
            'template_id',
            'common',
            'cc_id'
        ],
        data () {
            return {
                i18n: {
                    baseInfo: gettext('基础信息'),
                    flow: gettext('流程模板'),
                    node_name: gettext('节点名称'),
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
                    failureHandlingDetails1: gettext('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。'),
                    failureHandlingDetails2: gettext('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。'),
                    failureHandlingDetails3: gettext('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。'),
                    manuallyEmpty: gettext('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续')
                },
                htmlConfig: {
                    allowHtml: true,
                    width: 400,
                    trigger: 'mouseenter',
                    theme: 'dark',
                    content: '#html-error-ingored-tootip',
                    placement: 'left'
                },
                atomConfigLoading: false,
                errorCouldBeIgnored: false,
                nodeCouldBeSkipped: false,
                subflowHasUpdate: false, // 是否显示子流程更新 icon
                bkMessageInstance: null,
                subAtomConfigData: null,
                nodeConfigData: null,
                reuseVariable: {},
                isReuseVarDialogShow: false,
                taskTypeEmpty: false,
                reuseableVarList: [],
                nodeId: this.idOfNodeInConfigPanel,
                nodeName: '',
                stageName: gettext('步骤1'),
                currentAtom: '',
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
                showText: true,
                isAtomChanged: false, // 用于切换标准插件
                failureHandling: [], // 失败处理
                isDisable: false, // 是否禁用手动选项
                isSkip: true, // 是否手动跳过
                isRetry: true, // 是否手动重试
                manuallyEmpty: false // 手动选项为空
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'atomForm': state => state.atomForm.form,
                'atomFormConfig': state => state.atomForm.config,
                'atomFormOutput': state => state.atomForm.output,
                'subprocessInfo': state => state.template.subprocess_info
            }),
            /**
             * 标准插件节点、子节点列表
             */
            atomList () {
                if (this.isSingleAtom) {
                    return this.singleAtom.map(item => {
                        return {
                            id: item.code,
                            name: item.group_name + '-' + item.name
                        }
                    })
                } else {
                    return this.subAtom.filter(item => {
                        return item.template_id !== Number(this.template_id)
                    }).map(item => {
                        return {
                            id: item.template_id,
                            name: item.name
                        }
                    })
                }
            },
            /**
             * 标准插件节点描述
             */
            atomDesc () {
                if (this.singleAtom) {
                    return this.atomForm[this.currentAtom] && this.atomForm[this.currentAtom].desc
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

                outputConfig && outputConfig.forEach(item => {
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
                return this.isSingleAtom
                    ? this.getSingleAtomConfig()
                    : this.subAtomInput
            },
            /**
             * 输入参数数据
             */
            renderInputData () {
                return {
                    hook: this.inputAtomHook,
                    value: this.inputAtomData
                }
            }
        },
        watch: {
            idOfNodeInConfigPanel (val) {
                this.nodeId = val
                this.initData()
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
            if (this.errorCouldBeIgnored) {
                this.isDisable = true
            }
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
                    this.getConfig(this.nodeConfigData.version) // load node config data
                }
            },
            /**
             * 加载标准插件配置文件或子流程表单配置
             * @param {String} version 子流程版本
             */
            getConfig (version) {
                if (this.currentAtom !== '' && this.currentAtom !== undefined) {
                    if (this.isSingleAtom) {
                        return this.getAtomConfig(this.currentAtom)
                    } else {
                        return this.getSubflowConfig(this.currentAtom, version)
                    }
                } else {
                    this.markInvalidForm()
                }
            },
            /**
             * 加载标准插件节点数据
             */
            async getAtomConfig (atomType) {
                if ($.atoms[atomType]) {
                    this.setNodeConfigData(atomType)
                    return
                }
                this.atomConfigLoading = true
                try {
                    await this.loadAtomConfig({ atomType })
                    this.setAtomConfig({ atomType, configData: $.atoms[atomType] })
                    this.setNodeConfigData(atomType)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.atomConfigLoading = false
                    this.isAtomChanged = true
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

                        if (!this.atomFormConfig[atomType]) {
                            await this.loadAtomConfig({ atomType, classify })
                            this.setAtomConfig({ atomType: atom, configData: $.atoms[atom] })
                        }
                        
                        const atomConfig = this.atomFormConfig[atom]
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
                        this.markInvalidForm()
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
            setNodeConfigData (atomType) {
                const data = {}
                const config = this.atomFormConfig[atomType]
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
                this.getNodeFormData()
                this.$nextTick(() => {
                    this.updateActivities()
                    this.markInvalidForm()
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
                this.isSkip = formData.isSkipped
                this.isRetry = formData.can_retry
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
                const config = this.atomFormConfig[this.currentAtom]
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
                return this.isSingleAtom ? this.atomFormOutput[this.currentAtom] : this.subAtomOutput
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
                            tagCode: varKeyReg.test(key) ? key.match(varKeyReg)[1] : key
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
                    const sourceInfo = constant.source_info[this.nodeId]

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
            stopClickPropagation (e) {
            },
            /**
             * 处理节点配置面板和全局变量面板之外的点击事件
             */
            handleNodeConfigPanelShow (e) {
                if (!this.isNodeConfigPanelShow
                    || this.isReuseVarDialogShow
                    || e.target.className.indexOf('bk-option') > -1) {
                    return
                }
                const settingPanel = document.querySelector('.setting-area-wrap')
                const nodeConfig = document.querySelector('.node-config')
                if (settingPanel && this.isNodeConfigPanelShow) {
                    if ((!dom.nodeContains(settingPanel, e.target)
                        && !dom.nodeContains(nodeConfig, e.target))
                    ) {
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
                const nodeData = tools.deepClone(this.nodeConfigData)
                nodeData.name = this.nodeName
                nodeData.stage_name = this.stageName
                nodeData.optional = this.nodeCouldBeSkipped
                nodeData.isSkipped = this.isSkip
                nodeData.can_retry = this.isRetry
                if (this.isSingleAtom) {
                    nodeData.error_ignorable = this.errorCouldBeIgnored
                    for (const key in this.inputAtomData) {
                        nodeData.component.data[key] = {
                            hook: this.inputAtomHook[key] || false,
                            value: tools.deepClone(this.inputAtomData[key])
                        }
                    }
                } else {
                    const constants = tools.deepClone(this.subAtomConfigData.form)
                    for (const key in this.inputAtomData) {
                        constants[key] && (constants[key].value = tools.deepClone(this.inputAtomData[key]))
                    }
                    nodeData.constants = constants
                }
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
                        stage_name: this.stageName,
                        optional: this.nodeCouldBeSkipped,
                        error_ignorable: this.errorCouldBeIgnored,
                        can_retry: this.isRetry,
                        isSkipped: this.isSkip
                    })
                    this.$emit('hideConfigPanel')
                    return isValid
                })
            },
            markInvalidForm () {
                const nodeEls = document.querySelector('#' + this.nodeId).querySelector('.node-with-text')
                if (nodeEls && !this.isAtomChanged) {
                    const status = nodeEls.dataset.status
                    if (status === 'FAILED') {
                        this.$validator.validateAll()
                        this.$refs.renderForm && this.$refs.renderForm.validate()
                        if (!this.currentAtom) {
                            this.taskTypeEmpty = true
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
                        this.deleteVariable(variableKey)
                    }
                })
                this.taskTypeEmpty = false
                outputs.forEach(item => {
                    if (item.hook) {
                        this.deleteVariable(item.key)
                    }
                })
            },
            onAtomSelect (id, data) {
                this.isAtomChanged = true
                let nodeName
                this.clearHookedVaribles(this.getHookedInputVariables(), this.renderOutputData)
                this.currentAtom = id
                if (this.isSingleAtom) {
                    nodeName = data.name.split('-').slice(1).join().replace(/\s/g, '')
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
                    this.inputAtomHook = {}
                    this.inputAtomData = {}
                }
                this.nodeName = nodeName
                this.nodeConfigData.name = nodeName
                this.updateActivities()
                this.getConfig()
                this.$nextTick(() => {
                    this.isAtomChanged = false
                })
            },
            onJumpToProcess (index) {
                const item = this.atomList[index].id
                const { href } = this.$router.resolve({ path: `/template/edit/${this.cc_id}/?template_id=${item}` })
                window.open(href, '_blank')
            },
            /**
             * 更新子流程版本
             * 去掉节点小红点、模板刷新按钮
             * 更新 store 数据状态
             */
            onUpdateSubflowVersion () {
                const oldInputAtomHook = this.inputAtomHook
                const oldInputAtomData = this.inputAtomData

                // 清空 store 里的 constants 值
                this.subAtomConfigData.form = {}
                this.inputAtomHook = {}
                this.inputAtomData = {}
                this.updateActivities()

                this.getSubflowConfig(this.currentAtom).then(() => {
                    Object.keys(oldInputAtomData).forEach(key => {
                        if (this.inputAtomData.hasOwnProperty(key)) {
                            this.$set(this.inputAtomData, key, oldInputAtomData[key])
                        } else if (oldInputAtomHook[key]) {
                            const variable = [
                                {
                                    variableKey: key,
                                    formKey: key,
                                    id: this.nodeId,
                                    tagCode: key
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
                })
            },
            onErrorIngoredChange (selected) {
                this.errorCouldBeIgnored = selected
            },
            onSkippedChange (selected) {
                this.nodeCouldBeSkipped = selected
            },
            /**
             * 输入参数值更新
             */
            onInputDataChange (val) {
                this.inputAtomData = val
            },
            // 输入参数勾选、反勾选
            onInputHookChange (tagCode, val) {
                let key, source_tag, source_info, custom_type, value, validation
                // 变量 key 值
                let variableKey = /^\$\{[\w]*\}$/.test(tagCode) ? tagCode : '${' + tagCode + '}'
                const formConfig = this.renderInputConfig.filter(item => {
                    return item.tag_code === tagCode
                })[0]

                const name = formConfig.attrs.name.replace(/\s/g, '')

                if (this.isSingleAtom) {
                    key = tagCode
                    source_tag = this.nodeConfigData.component.code + '.' + tagCode
                    source_info = { [this.nodeId]: [tagCode] }
                    custom_type = ''
                    value = tools.deepClone(this.inputAtomData[tagCode])
                } else {
                    const variable = this.subAtomConfigData.form[variableKey]
                    key = variableKey
                    tagCode = tagCode.match(varKeyReg)[1]
                    source_info = { [this.nodeId]: [variableKey] }
                    custom_type = variable.custom_type
                    value = tools.deepClone(this.inputAtomData[key])
                    if (formConfig.type === 'combine') {
                        source_tag = variable.source_tag.split('.')[0] + '.' + variableKey
                    } else {
                        source_tag = variable.source_tag
                        validation = variable.validation
                    }
                }
                this.$set(this.inputAtomHook, key, val)

                if (val) { // hooked
                    const variableList = []
                    if (!source_tag) { // custom variable not include ip selector
                        const variableOpts = {
                            name, key: variableKey, source_info, custom_type, value, validation
                        }
                        this.$set(this.inputAtomData, key, variableKey)
                        this.createVariable(variableOpts)
                        return
                    }
                    for (const cKey in this.constants) {
                        const constant = this.constants[cKey]
                        const sTag = constant.source_tag
                        if (sTag) {
                            const tCode = sTag.split('.')[1]
                            tCode === tagCode && variableList.push({
                                name: `${constant.name}(${constant.key})`,
                                id: constant.key
                            })
                        }
                    }
                    const isKeyUsedInConstants = variableKey in this.constants

                    if (variableList.length) { // input arguments include ip selector have same soure_tag
                        this.reuseVariable = { name, key, source_tag, source_info, value, useNewKey: false }
                        this.reuseableVarList = variableList
                        this.isReuseVarDialogShow = true
                    } else if (isKeyUsedInConstants) { // the variable's key is used in other global variable
                        this.reuseVariable = { name, key, source_tag, source_info, value, useNewKey: true }
                        this.reuseableVarList = variableList
                        this.isReuseVarDialogShow = true
                    } else {
                        const variableOpts = {
                            name, key: variableKey, source_tag, source_info, custom_type, value
                        }
                        this.$set(this.inputAtomData, key, variableKey)
                        this.createVariable(variableOpts) // input arguments hook
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
                        this.deleteVariable(variableKey)
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
                        show_type: 'hide'
                    }
                    this.renderOutputData.some(item => {
                        if (item.key === key) {
                            this.$set(item, 'key', variableKey)
                            return true
                        }
                    })
                    this.createVariable(variableOpts)
                } else {
                    const constant = this.constants[key]
                    if (constant) {
                        this.deleteVariable(key)
                    }
                }
            },
            /**
             * 参数不复用，创建新变量
             */
            createVariable (variableOpts) {
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
                    index: len
                }
                const variable = Object.assign({}, defaultOpts, variableOpts)
                this.addVariable(Object.assign({}, variable))
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
                    this.createVariable(variableOpts)
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
                this.isDisable = updatedValue
                this.manuallyEmpty = !updatedValue
                this.isSkip = false
                this.isRetry = false
                this.errorCouldBeIgnored = updatedValue
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/clearfix.scss';
@import '@/scss/mixins/scrollbar.scss';
.node-config-panel {
    position: absolute;
    top: 60px;
    right: 476px;
    padding: 20px;
    width: 694px;
    height: calc(100% - 50px);
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    box-shadow: -4px 0 6px -4px rgba(0, 0, 0, 0.15);
    overflow-y: auto;
    z-index: 4;
    transition: right 0.5s ease-in-out;
    @include scrollbar;
    .node-title {
        height: 35px;
        border-bottom: 1px solid #cacecb;
        span {
            font-size: 14px;
            font-weight:600;
            color:#313238;
        }
    }
    &.position-right-side {
        right: 55px;
    }
    /deep/ .bk-selector .bk-selector-list {
        box-shadow: 0 0 8px 1px rgba(0, 0, 0, .2)
    }
    .common-icon-dark-circle-i {
        color: #a6b0c7;
    }
    .common-icon-dark-circle-s {
        color: #a6b0c7;
    }
    .common-icon-dark-circle-r {
        color: #a6b0c7;
    }
}
.form-item {
    margin-bottom: 20px;
    &:last-child {
        margin-bottom: 0;
    }
    @include clearfix;
    label {
        position: relative;
        float: left;
        margin-top: 8px;
        width: 100px;
        font-size: 14px;
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
        /deep/ .el-checkbox {
            width: 110px;
            padding-right: 11px;
        }
        .icon-info-circle {
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .common-warning-tip {
            margin-top: 15px;
        }
        .bk-switcher {
            top: 5px;
        }
        .common-icon-dark-circle-i,
        .common-icon-dark-circle-s,
        .common-icon-dark-circle-r {
            color: #a6b0c7;
        }
    }
    .desc-tooltip, .update-tooltip, .error-ingored-tootip {
        margin-left: 15px;
        position: absolute;
        right: 20px;
        color: #c4c6cc;
        cursor: pointer;
        &:hover {
            color: #f4aa1a;
        }
        /deep/ .bk-tooltip-rel {
            top: 7px;
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
            font-size: 14px;
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
/deep/.icon-edit2:before {
    content: '\e908';
    font-family: 'commonicon' !important;
    font-size: 16px;
    color: #546a9e;
    margin-right: 10px;
}
/deep/.bk-selector-tools {
    top: 13px !important;
}
/deep/.icon-close {
    display: none;
}
.common-icon-box-top-right-corner {
    position: absolute;
    right: 0;
    top: 0;
    margin-top: 10px;
    margin-right: 10px;
}
</style>
