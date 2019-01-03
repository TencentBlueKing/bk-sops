/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="node-config">
        <div
            :class="{
                'node-config-panel': true,
                'position-right-side': !isSettingPanelShow
            }">
            <div class="basic-info">
                <h3 class="common-section-title">{{ i18n.base_info }}</h3>
                <div class="section-form basic-info-form">
                    <div class="form-item form-name">
                        <label class="required">{{ atomNameType }}</label>
                        <div class="form-content">
                            <bk-selector
                                :searchable="true"
                                :list="atomList"
                                :selected.sync="currentAtom"
                                @item-selected="onAtomSelect">
                            </bk-selector>
                            <span v-show="taskTypeEmpty" class="common-error-tip error-msg">{{ atomNameType + i18n.typeEmptyTip}}</span>
                        </div>
                        <bk-tooltip v-if="atomDesc" placement="left" width="400" class="desc-tooltip">
                            <i class="common-icon-warning atom-desc"></i>
                            <div slot="content" style="white-space: normal;">
                                <div class="">{{atomDesc}}</div>
                            </div>
                        </bk-tooltip>
                    </div>
                    <div class="form-item">
                        <label class="required">{{ i18n.node_name }}</label>
                        <div class="form-content">
                            <BaseInput v-model="nodeName" name="nodeName" v-validate="nodeNameRule"/>
                            <span v-show="errors.has('nodeName')" class="common-error-tip error-msg">{{ errors.first('nodeName') }}</span>
                        </div>
                    </div>
                    <div class="form-item">
                        <label>{{ i18n.stage_tag }}</label>
                        <div class="form-content">
                            <BaseInput v-model="stageName" name="stageName" v-validate="stageNameRule"/>
                            <span v-show="errors.has('stageName')" class="common-error-tip error-msg">{{ errors.first('stageName') }}</span>
                        </div>
                    </div>
                    <div class="form-item" v-if="this.isSingleAtom">
                        <label>{{ i18n.ignore }}</label>
                        <div class="form-content">
                            <bk-switcher
                                :selected="errorCouldBeIgnored"
                                :is-square="true"
                                @change="onErrorIngoredChange">
                            </bk-switcher>
                        </div>
                    </div>
                    <div class="form-item">
                        <label>{{ i18n.optional }}</label>
                        <div class="form-content">
                            <bk-switcher
                                :selected="nodeCouldBeSkipped"
                                :is-square="true"
                                @change="onSkippedChange">
                            </bk-switcher>
                        </div>
                    </div>
                </div>
            </div>
            <div class="inputs-info">
                <h3 class="common-section-title">{{ i18n.input }}</h3>
                <div class="section-form inputs-info-form" v-bkloading="{isLoading: atomConfigLoading, opacity: 1}">
                    <RenderForm
                        ref="renderForm"
                        v-if="renderInputConfig && renderInputConfig.length"
                        :config="renderInputConfig"
                        :option="renderInputOption"
                        :data="renderInputData"
                        @dataChange="onInputDataChange"
                        @hookChange="onInputHookChange">
                    </RenderForm>
                    <div class="no-data-wrapper" v-else>
                        <NoData></NoData>
                    </div>
                </div>
            </div>
            <div class="outputs-info">
                <h3 class="common-section-title">{{ i18n.output }}</h3>
                <div class="section-form outputs-info-form" v-bkloading="{isLoading: atomConfigLoading, opacity: 1}">
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
                                    <bk-tooltip
                                        :content="item.hook ? i18n.cancelHook : i18n.hook"
                                        placement="left">
                                        <BaseCheckbox
                                            :isChecked="item.hook"
                                            @checkCallback="onOutputHookChange(item.name, item.key, $event)">
                                        </BaseCheckbox>
                                    </bk-tooltip>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="no-data-wrapper" v-else>
                        <NoData/>
                    </div>
                </div>
            </div>

        </div>
        <ReuseVarDialog
            v-if="isReuseVarDialogShow"
            :isReuseVarDialogShow="isReuseVarDialogShow"
            :reuseVariable="reuseVariable"
            :reuseableVarList="reuseableVarList"
            @onConfirmReuseVar="onConfirmReuseVar"
            @onCancelReuseVar="onCancelReuseVar">
        </ReuseVarDialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapActions, mapState, mapMutations } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { checkDataType } from '@/utils/checkDataType.js'
import tools from '@/utils/tools.js'
import dom from '@/utils/dom.js'
import atomFilter from '@/utils/atomFilter.js'
import { random4 } from '@/utils/uuid.js'
import { NAME_REG } from '@/constants/index.js'
import NoData from '@/components/common/base/NoData.vue'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import BaseCheckbox from '@/components/common/base/BaseCheckbox.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import ReuseVarDialog from './ReuseVarDialog.vue'

const varKeyReg = /^\$\{(\w+)\}$/

export default {
    name: 'NodeConfig',
    components: {
        NoData,
        RenderForm,
        BaseCheckbox,
        BaseInput,
        ReuseVarDialog
    },
    props: [
        'isNodeConfigPanelShow',
        'isSettingPanelShow',
        'singleAtom',
        'subAtom',
        'idOfNodeInConfigPanel',
        'template_id'
    ],
    data () {
        return {
            i18n: {
                base_info: gettext("基础信息"),
                flow: gettext("流程模板"),
                node_name: gettext("节点名称"),
                stage_tag: gettext("步骤名称"),
                ignore: gettext("忽略错误"),
                optional: gettext("是否可选"),
                input: gettext("输入参数"),
                output: gettext("输出参数"),
                name: gettext("名称"),
                refer: gettext("引用"),
                hook: gettext("勾选参数作为全局变量"),
                cancelHook: gettext("取消勾选"),
                typeEmptyTip: gettext("不能为空")
            },
            atomConfigLoading: false,
            errorCouldBeIgnored: false,
            nodeCouldBeSkipped: false,
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
                showLabel: true
            },
            inputAtomHook: {},
            inputAtomData: undefined,
            nodeNameRule: {
                required: true,
                max: 20,
                regex: NAME_REG
            },
            stageNameRule: {
                max: 20,
                regex: NAME_REG
            }
        }
    },
    computed: {
        ...mapState({
            'activities': state => state.template.activities,
            'constants': state => state.template.constants,
            'atomForm': state => state.atomForm.form,
            'atomFormConfig': state => state.atomForm.config,
            'atomFormOutput': state => state.atomForm.output
        }),
        /**
         * 原子节点、子节点列表
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
         * 原子节点描述
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
            return this.isSingleAtom ? gettext('原子类型') : gettext('流程模板')
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
                for (let cKey in this.constants) {
                    if (this.constants[cKey].source_type === 'component_outputs' &&
                        this.constants[cKey].source_info[this.nodeId] &&
                        this.constants[cKey].source_info[this.nodeId].indexOf(key) > -1
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

            return outputData
        },
        /**
         * 输入参数表单配置项
         */
        renderInputConfig () {
            return  this.isSingleAtom ?
                this.getSingleAtomConfig() :
                this.subAtomInput
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
    created () {
        this.initData()
    },
    mounted () {
        window.addEventListener('click', this.handleNodeConfigPanelShow, false)
    },
    beforeDestroy (){
        window.removeEventListener('click', this.handleNodeConfigPanelShow, false)
    },
    watch: {
        idOfNodeInConfigPanel (val) {
            this.nodeId = val
            this.initData()
        }
    },
    methods: {
        ...mapMutations ('atomForm/', [
            'setAtomConfig'
        ]),
        ...mapMutations ('template/', [
            'addVariable',
            'deleteVariable',
            'setActivities',
            'setVariableSourceInfo'
        ]),
        ...mapActions('atomForm/', [
            'loadAtomConfig',
            'loadSubflowConfig'
        ]),
        initData () {
            this.nodeConfigData = JSON.parse(JSON.stringify(this.activities[this.nodeId]))
            this.getNodeFormData() // get template activity information
            this.getConfig() // load node config data
        },
        getConfig () {
            if (this.currentAtom !== '' && this.currentAtom !== undefined) {
                if ( this.isSingleAtom) {
                    return this.getAtomConfig(this.currentAtom)
                } else {
                    return this.getSubflowConfig(this.currentAtom)
                }
            } else {
                this.markInvalidForm()
            }
        },
        /**
         * 加载原子节点数据
         */
        async getAtomConfig (atomType) {
            if ($.atoms[atomType]) {
                this.setNodeConfigData(atomType)
                return
            }
            this.atomConfigLoading = true
            try {
                await this.loadAtomConfig({atomType})
                this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                this.setNodeConfigData(atomType)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.atomConfigLoading = false
            }
        },
        /**
        * 加载子流程节点数据
        */
        async getSubflowConfig (id) {
            this.atomConfigLoading = true
            this.nodeConfigData.template_id = id
            const isSubAtomChanged = this.currentAtom !== this.nodeConfigData.template_id
            try {
                this.subAtomConfigData = await this.loadSubflowConfig({id})
                const inputConfig = []
                const outputConfig = []
                let variableArray = []
                this.nodeConfigData.version = this.subAtomConfigData.version

                for (let cKey in this.subAtomConfigData.form) {
                    const variable = JSON.parse(JSON.stringify(this.subAtomConfigData.form[cKey]))
                    if (variable.show_type === 'show') {
                        variableArray.push(variable)
                    }
                }
                variableArray = variableArray.sort((a, b) => {
                    return a.index - b.index
                })
                for (let form of variableArray) {
                    let key = form.key
                    let constantData = {}
                    const sourceTag = form.source_tag
                    if (sourceTag) {
                        const [ atomType, tagCode ] = sourceTag.split('.')
                        if (!this.atomFormConfig[atomType]) {
                            await this.loadAtomConfig({atomType})
                            this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                        }
                        const atomConfig = this.atomFormConfig[atomType]
                        const currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                        currentFormConfig.variableKey = key
                        currentFormConfig.attrs.name = this.subAtomConfigData.form[key].name
                        inputConfig.push(currentFormConfig)
                    } else {
                        const currentFormConfig = {
                            tag_code: key,
                            type: form.custom_type,
                            variableKey: key,
                            attrs: {
                                name: form.name,
                                hookable: true
                            }
                        }
                        if (form.validation && checkDataType(form.validation) === 'String') {
                            const validation = {
                                type: 'regex',
                                args: form.validation,
                                error_message: gettext('输入值不满足校验规则') + form.validation
                            }
                            currentFormConfig.attrs.validation = [validation]
                        }
                        inputConfig.push(currentFormConfig)
                    }
                    // primary activities data maybe incomplete
                    constantData = this.activities[this.nodeId].constants[key] || form
                    this.$set(this.nodeConfigData.constants, key, JSON.parse(JSON.stringify(constantData)))
                }
                for ( let key in this.subAtomConfigData.outputs ) {
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
                const activityData = JSON.parse(JSON.stringify(this.activities[this.nodeId]))
                config.forEach(item => {
                    let value = activityData.component.data[item.tag_code].value
                    if (!value)  {
                        value = atomFilter.getFormItemDefaultValue(item)
                        activityData.component.data[item.tag_code].value = value
                    }
                })
                this.nodeConfigData = activityData
            } else {
                config.forEach(item => {
                    data[item.tag_code] =  {
                        hook: false,
                        value: atomFilter.getFormItemDefaultValue(item)
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
            const inputFormHooks = {}
            const inputFormData = {}
            if (this.isSingleAtom) {
                const data = tools.deepClone(formData.component.data)
                this.currentAtom = formData.component.code || ''
                this.errorCouldBeIgnored = formData.error_ignorable
                for (let form in data) {
                    inputFormHooks[form] = data[form].hook
                    inputFormData[form] = JSON.parse(JSON.stringify(data[form].value))
                }
            } else {
                this.currentAtom = formData.template_id
                for (let key in formData.constants) {
                    const form = formData.constants[key]
                    const tagCode = key.match(varKeyReg)[1]
                    const inputConfig = this.subAtomInput.filter(item => item.variableKey === key)[0]
                    form.hook = this.iskeyInSourceInfo(key, tagCode)
                    inputFormHooks[key] = form.hook
                    inputFormData[key] = JSON.parse(JSON.stringify(form.value))
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
            for (let key in this.renderInputData.hook){
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
            for (let cKey in this.constants) {
                let constant = this.constants[cKey]
                const sourceInfo = constant.source_info[this.nodeId]
                if (sourceInfo && (sourceInfo.indexOf(tagCode) > -1 || sourceInfo.indexOf(key) > -1)) {
                    return true
                }
            }
            return false
        },
        /**
         * the node type select change
         */
        isAtomChanged () {
            if (!this.currentAtom) {
                return false
            }
            if (this.isSingleAtom) {
                return this.currentAtom !== this.activities[this.nodeId].component.code
            } else {
                return this.currentAtom !== this.activities[this.nodeId].template_id
            }
        },
        /**
         * 处理节点配置面板和全局变量面板之外的点击时间
         */
        handleNodeConfigPanelShow (e) {
            if (!this.isNodeConfigPanelShow || this.isReuseVarDialogShow) {
                return
            }
            const settingPanel = document.querySelector(".setting-panel")
            const nodeConfig = document.querySelector(".node-config")
            if (settingPanel && nodeConfig) {
                if ((!dom.nodeContains(settingPanel, e.target) &&
                    !dom.nodeContains(nodeConfig, e.target))
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
            if (this.isSingleAtom) {
                nodeData.error_ignorable = this.errorCouldBeIgnored
                for (let key in this.inputAtomData) {
                    nodeData.component.data[key] = {
                        hook: this.inputAtomHook[key],
                        value: JSON.parse(JSON.stringify(this.inputAtomData[key]))
                    }
                }
            } else {
                const constants = tools.deepClone(this.subAtomConfigData.form)
                for (let key in this.inputAtomData) {
                    constants[key] && (constants[key].value = JSON.parse(JSON.stringify(this.inputAtomData[key])))
                }
                nodeData.constants = constants
            }
            this.setActivities({type: 'edit', location: nodeData})
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
                    error_ignorable: this.errorCouldBeIgnored
                })
                this.$emit('hideConfigPanel')
                return isValid
            })
        },
        markInvalidForm () {
            const nodeEls = document.querySelector('#' + this.nodeId).querySelector('.node-with-text')
            const atomChanged = this.isAtomChanged()
            if (nodeEls && !atomChanged) {
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
        onAtomSelect (id, data) {
            let nodeName
            const hookedVariables = this.getHookedInputVariables()
            hookedVariables.forEach(item => {
                const {id, variableKey, formKey, tagCode} = item
                const variable = this.constants[variableKey]
                this.setVariableSourceInfo({type: 'delete', id, key: variableKey, tagCode: formKey})
                if (variable && !Object.keys(variable.source_info).length) {
                    this.deleteVariable(variableKey)
                }
            })
            this.taskTypeEmpty = false
            this.renderOutputData.forEach(item => {
                if (item.hook) {
                    this.deleteVariable(item.key)
                }
            })
            this.currentAtom = id
            if (this.isSingleAtom) {
                nodeName = data.name.split('-').slice(1).join().replace(/\s/g, '')
            } else {
                nodeName = data.name.replace(/\s/g, '')
                this.nodeConfigData.constants = {}
                this.inputAtomHook = {}
                this.inputAtomData = {}
            }
            this.nodeConfigData.name = nodeName
            this.updateActivities()
            this.getConfig()
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
        onInputDataChange (val, tagCode, variableKey) {
            if (variableKey) {
                const dataType = checkDataType(this.inputAtomData[variableKey])
                if (dataType === 'Object') {
                    this.inputAtomData[variableKey][tagCode] = val
                } else {
                    this.inputAtomData[variableKey] = val
                }
            } else {
                const key = (tagCode in this.inputAtomData) ? tagCode : '${' + tagCode + '}'
                this.inputAtomData[key] = val
            }
        },
        onInputHookChange (val, tagCode, hookKey) {  // input arguments form element hook operation
            let name, key, source_tag, source_info, custom_type, value, validation
            let variableKey = /^\$\{[\w]*\}$/.test(tagCode) ? tagCode : '${' + tagCode + '}'
            const formConfig = this.renderInputConfig.filter(item => {
                return hookKey ? item.variableKey === hookKey : item.tag_code === tagCode
            })[0]
            source_info = {[this.nodeId]: [tagCode]}

            if (this.isSingleAtom) { // 原子任务节点
                key = tagCode
                name = formConfig.attrs.name.replace(/\s/g, '')
                source_tag = this.nodeConfigData.component.code + '.' + tagCode
                custom_type = ''
                value = JSON.parse(JSON.stringify(this.inputAtomData[key])) || ''
            } else { // 子流程任务节点
                if (formConfig.type === 'combine') {
                    key = hookKey
                    name = this.subAtomConfigData.form[hookKey].name.replace(/\s/g, '')
                    source_tag = this.subAtomConfigData.form[hookKey].source_tag.split('.')[0] + '.' + tagCode
                    source_info = {[this.nodeId]: [hookKey]}
                    custom_type = this.subAtomConfigData.form[hookKey].custom_type
                    variableKey = source_tag ? key : this.generateRandomKey(key)
                    value = JSON.parse(JSON.stringify(this.inputAtomData[hookKey])) || ''
                } else {
                    key = hookKey || variableKey
                    name = this.subAtomConfigData.form[key].name.replace(/\s/g, '')
                    source_tag = this.subAtomConfigData.form[key].source_tag
                    source_info = {[this.nodeId]: [hookKey]}
                    custom_type = this.subAtomConfigData.form[key].custom_type
                    validation = this.subAtomConfigData.form[key].validation
                    value = JSON.parse(JSON.stringify(this.inputAtomData[key])) || ''
                    variableKey = source_tag ? key : this.generateRandomKey(key)
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
                for (let cKey in this.constants) {
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

                if (variableList.length) {// input arguments include ip selector have same soure_tag
                    this.reuseVariable = {name, key, source_tag, source_info, value, useNewKey: false}
                    this.reuseableVarList = variableList
                    this.isReuseVarDialogShow = true
                } else if (isKeyUsedInConstants){ // the variable's key is used in other global variable
                    this.reuseVariable = {name, key, source_tag, source_info, value, useNewKey: true}
                    this.reuseableVarList = variableList
                    this.isReuseVarDialogShow = true
                } else {
                    const variableOpts = {
                        name, key: variableKey, source_tag, source_info, custom_type, value
                    }
                    this.$set(this.inputAtomData, key, variableKey)
                    this.createVariable(variableOpts) // input arguments hook
                    return
                }
            } else {  // cancel hook
                variableKey = this.inputAtomData[key] // variable key
                const variable = this.constants[variableKey]
                const formKey = this.isSingleAtom ? tagCode : key // input arguments form item key
                this.inputAtomHook[formKey] = val
                this.inputAtomData[formKey] = JSON.parse(JSON.stringify(this.constants[variableKey].value))
                this.setVariableSourceInfo({type: 'delete', id: this.nodeId, key: variableKey, tagCode: formKey})
                if (variable && !Object.keys(variable.source_info).length) {
                    this.deleteVariable(variableKey)
                }
            }
        },
        onOutputHookChange (name, key, checked) {
            if (checked) {
                let variableKey = this.generateRandomKey(key)

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
        onConfirmReuseVar (variableConfig) {
            let  { type, name, key, varKey, source_tag, source_info, value } = variableConfig
            if (type === 'create') {  // create new variable
                if (this.constants[varKey]) {
                    this.$bkMessage({
                        message: gettext('变量KEY已存在'),
                        theme: 'error'
                    })
                    return
                }

                this.$set(this.inputAtomHook, varKey, true)
                this.$set(this.inputAtomData, key, varKey)
                const variableOpts = {name, key: varKey, source_tag, source_info, value}
                this.createVariable(variableOpts)
            } else {
                this.$set(this.inputAtomHook, varKey, true)
                this.$set(this.inputAtomData, key, varKey)
                this.setVariableSourceInfo({type: 'add', id: this.nodeId, key: varKey, tagCode: key, value})
            }

            this.isReuseVarDialogShow = false
        },
        onCancelReuseVar (reuseVariable) {
            const  { key } = reuseVariable
            this.inputAtomHook[key] = false
            this.isReuseVarDialogShow = false
        },
        onDeleteConstant (constant) {
            let { source_info, source_type, value, key } = constant
            if (source_type === 'component_inputs') {
                const quotedByParams = source_info[this.nodeId]
                if (quotedByParams) {
                    quotedByParams.forEach(item => {
                        let key = item
                        if (!this.isSingleAtom) {
                            key = varKeyReg.test(item) ? item : '${' + item + '}'
                        }
                        this.inputAtomHook[key] = false
                        this.inputAtomData[key] = value
                    })
                }
            }
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
    top: 50px;
    right: 415px;
    padding: 20px;
    width: 700px;
    height: calc(100% - 50px);
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    box-shadow: -4px 0 6px -4px rgba(0, 0, 0, 0.15);
    overflow-y: auto;
    z-index: 4;
    transition: right 0.5s ease-in-out;
    @include scrollbar;
    &.position-right-side {
        right: 0;
    }
    /deep/ .bk-selector .bk-selector-list {
        box-shadow: 0 0 8px 1px rgba(0, 0, 0, .2)
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
        font-weight: bold;
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
    }
    &.form-name {
        position: relative;
        .desc-tooltip {
            position: absolute;
            right: 0;
            top: 4px;
            .atom-desc {
                color: #cac8c8;
            }
        }
    }
}
.section-form {
    padding: 30px 0 40px;
}
.inputs-info {
    /deep/ .render-form {
        .form-item {
            font-size: 14px;
            .tag-label {
                font-weight: bold;
                color: $greyDefault;
            }
        }
        & > .form-item,
        .form-group > .form-item {
            & > .tag-form {
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
            font-size: 14px;
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
</style>
