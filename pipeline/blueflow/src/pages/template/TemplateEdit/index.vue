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
    <div class="template-page" v-bkloading="{isLoading: templateDataLoading}">
        <div v-if="!templateDataLoading" class="pipeline-canvas-wrapper">
            <PipelineCanvas
                ref="pipelineCanvas"
                :singleAtomListLoading="singleAtomListLoading"
                :subAtomListLoading="subAtomListLoading"
                :templateSaving="templateSaving"
                :canvasData="canvasData"
                :name="name"
                :cc_id="cc_id"
                :common="common"
                :atomTypeList="atomTypeList"
                :searchAtomResult="searchAtomResult"
                @onChangeName="onChangeName"
                @onSaveTemplate="onSaveTemplate"
                @onSearchAtom="onSearchAtom"
                @onBackToList="onBackToList"
                @onNodeClick="onNodeClick"
                @onLabelBlur="onLabelBlur"
                @onLocationChange="onLocationChange"
                @onLineChange="onLineChange"
                @onLocationMoveDone="onLocationMoveDone"
                @onNewDraft="onNewDraft"
                @onReplaceLineAndLocation="onReplaceLineAndLocation">
            </PipelineCanvas>
            <NodeConfig
                ref="nodeConfig"
                v-if="isNodeConfigPanelShow"
                :template_id="template_id"
                :singleAtom="singleAtom"
                :subAtom="subAtom"
                :isSettingPanelShow="isSettingPanelShow"
                :isNodeConfigPanelShow="isNodeConfigPanelShow"
                :idOfNodeInConfigPanel="idOfNodeInConfigPanel"
                :common="common"
                @hideConfigPanel="hideConfigPanel"
                @onUpdateNodeInfo="onUpdateNodeInfo">
            </NodeConfig>
            <TemplateSetting
                ref="templateSetting"
                :draftArray = "draftArray"
                :businessInfoLoading="businessInfoLoading"
                :isTemplateConfigValid="isTemplateConfigValid"
                :isSettingPanelShow="isSettingPanelShow"
                :localTemplateData="localTemplateData"
                :isClickDraft="isClickDraft"
                @toggleSettingPanel="toggleSettingPanel"
                @onDeleteConstant="onDeleteConstant"
                @variableDataChanged="variableDataChanged"
                @onSelectCategory="onSelectCategory"
                @onDeleteDraft="onDeleteDraft"
                @onReplaceTemplate="onReplaceTemplate"
                @onNewDraft="onNewDraft"
                @updateLocalTemplateData="updateLocalTemplateData"
                @hideConfigPanel="hideConfigPanel">
            </TemplateSetting>
            <bk-dialog
                :is-show.sync="isLeaveDialogShow"
                :quick-close="false"
                :ext-cls="'common-dialog'"
                :title="i18n.leave"
                width="400"
                padding="30px"
                @confirm="onLeaveConfirm"
                @cancel="onLeaveCancel">
                <div slot="content">{{ i18n.tips }}</div>
            </bk-dialog>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
// moment用于时区使用
import moment from 'moment-timezone'
import { uuid } from '@/utils/uuid.js'
import tools from '@/utils/tools.js'
import atomFilter from '@/utils/atomFilter.js'
import { errorHandler } from '@/utils/errorHandler.js'
import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
import TemplateSetting from './TemplateSetting/TemplateSetting.vue'
import NodeConfig from './NodeConfig.vue'
import draft from '@/utils/draft.js'
import { STRING_LENGTH } from '@/constants/index.js'
import { setAtomConfigApiUrls } from '@/config/setting.js'

const i18n = {
    templateEdit: gettext('流程编辑'),
    leave: gettext("离开页面"),
    tips: gettext("系统不会保存您所做的更改，确认离开？"),
    saved: gettext("保存成功"),
    error: gettext('任务节点参数错误，请点击错误节点查看详情'),
    delete_success: gettext('删除本地缓存成功'),
    delete_fail: gettext('该本地缓存不存在，删除失败'),
    replace_success: gettext('替换流程成功'),
    add_cache: gettext('新增流程本地缓存成功'),
    replace_save: gettext('替换流程自动保存')
}

export default {
    name: 'TemplateEdit',
    components: {
        PipelineCanvas,
        NodeConfig,
        TemplateSetting
    },
    props: ['cc_id', 'template_id', 'type', 'common'],
    data () {
        return {
            i18n,
            bkMessageInstance: null,
            exception: {},
            singleAtomListLoading: false,
            subAtomListLoading: false,
            businessInfoLoading: false,
            templateDataLoading: false,
            templateSaving: false,
            isTemplateConfigValid: true, // 模板基础配置是否合法
            isTemplateDataChanged: false,
            isSettingPanelShow: true,
            isNodeConfigPanelShow: false,
            isLeaveDialogShow: false,
            allowLeave: false,
            leaveToPath: '',
            idOfNodeInConfigPanel: '',
            subAtomGrouped: [],
            draftArray: [],
            intervalSaveTemplate: null,
            intervalGetDraftArray: null,
            templateUUID: uuid(),
            localTemplateData: null,
            isClickDraft: false
        }
    },
    computed: {
        ...mapState({
            'singleAtom': state => state.atomList.singleAtom,
            'subAtom': state => state.atomList.subAtom,
            'searchAtomResult': state => state.atomList.searchAtomResult,
            'atomConfig': state => state.atomForm.config,
            'name': state => state.template.name,
            'activities': state => state.template.activities,
            'locations': state => state.template.location,
            'lines': state => state.template.line,
            'constants': state => state.template.constants,
            'gateways': state => state.template.gateways,
            'businessBaseInfo': state => state.template.businessBaseInfo,
            'category': state => state.template.category,
            'subprocess_info': state => state.template.subprocess_info,
            'businessTimezone': state => state.businessTimezone,
            'username': state => state.username,
            'site_url': state => state.site_url,
            'atomFormConfig': state => state.atomForm.config
        }),
        ...mapGetters('atomList/',[
            'singleAtomGrouped'
        ]),
        atomTypeList () {
            const subAtomGrouped = tools.deepClone(this.subAtomGrouped)
            if (this.type !== 'new') {
                let theSameAtomIndex
                this.subAtomGrouped.some((group, groupIndex) => {
                    const inTheGroup = group.list.some((item, index) => {
                        if (item.id === Number(this.template_id)) {
                            theSameAtomIndex = index
                            return true
                        }
                    })
                    if (inTheGroup) {
                        subAtomGrouped[groupIndex].list.splice(theSameAtomIndex, 1)
                    }
                    return inTheGroup
                })
            }
            return {
                'tasknode': this.singleAtomGrouped,
                'subflow': subAtomGrouped
            }
        },
        canvasData () {
            const branchConditions = {}
            for (let gKey in this.gateways) {
                const item = this.gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            return {
                activities: this.activities,
                lines: this.lines,
                locations: this.locations.map(item => {
                    const data = {...item, mode: 'edit'}
                    if (
                        this.subprocess_info &&
                        this.subprocess_info.details &&
                        item.type === 'subflow'
                    ) {
                        this.subprocess_info.details.some(subflow => {
                            if (subflow.subprocess_node_id === item.id && subflow.expired) {
                                data.hasUpdated = true
                                return true
                            }
                        })
                    }
                    return data
                }),
                branchConditions
            }
        }
    },
    created () {
        if (this.common) {
            this.defaultCCId = this.cc_id
            setAtomConfigApiUrls(this.site_url, 0)
        }
        this.initTemplateData()
        if (this.type === 'edit' || this.type === 'clone') {
            this.getTemplateData()
        } else {
            const name = 'new' + moment.tz(this.businessTimezone).format('YYYYMMDDHHmmss')
            this.setTemplateName(name)
        }
        // 复制并替换本地缓存的内容
        if (this.type === 'clone') {
            draft.copyAndReplaceDraft(this.username, this.cc_id, this.template_id, this.templateUUID)
            this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.templateUUID)
        } else {
            // 先执行一次获取本地缓存
            this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID())
        }
        // 五分钟进行存储本地缓存
        const fiveMinutes = 1000 * 60 * 5
        this.intervalSaveTemplate = setInterval(() => {
            draft.addDraft(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData())
        }, fiveMinutes)

        // 五分钟多5秒 为了用于存储本地缓存过程的时间消耗
        const fiveMinutesAndFiveSeconds = fiveMinutes + 5000
        this.intervalGetDraftArray = setInterval(() => {
            this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID())
        }, fiveMinutesAndFiveSeconds)
    },
    mounted () {
        this.getSingleAtomList()
        this.getBusinessBaseInfo()
    },
    beforeDestroy () {
        this.resetTemplateData()
    },
    methods: {
        ...mapActions('atomList/', [
            'loadSingleAtomList',
            'loadSubAtomList'
        ]),
        ...mapActions('template/', [
            'loadBusinessBaseInfo',
            'loadTemplateData',
            'saveTemplateData',
            'loadCommonTemplateData'
        ]),
        ...mapActions('atomForm/', [
            'loadAtomConfig',
            'loadSubflowConfig'
        ]),
        ...mapMutations('atomList/', [
            'setSingleAtom',
            'setSubAtom',
            'searchAtom'
        ]),
        ...mapMutations('template/', [
            'initTemplateData',
            'resetTemplateData',
            'setBusinessBaseInfo',
            'setTemplateName',
            'setTemplateData',
            'setLocation',
            'setLocationXY',
            'setLine',
            'setActivities',
            'setGateways',
            'setStartpoint',
            'setEndpoint',
            'setBranchCondition',
            'replaceTemplate',
            'replaceLineAndLocation'
        ]),
        ...mapMutations('atomForm/', [
            'setAtomConfig',
            'clearAtomForm'
        ]),
        ...mapGetters('template/',[
            'getLocalTemplateData'
        ]),
        async getSingleAtomList () {
            this.singleAtomListLoading = true
            try {
                const data = await this.loadSingleAtomList()
                this.setSingleAtom(data)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.singleAtomListLoading = false
            }
        },
        async getBusinessBaseInfo () {
            this.businessInfoLoading = true
            try {
                const data = await this.loadBusinessBaseInfo()
                this.setBusinessBaseInfo(data)
                const subAtomData = {
                    ccId: this.cc_id,
                    common: this.common,
                    templateId: this.template_id
                }
                this.getSubAtomList(subAtomData)
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.businessInfoLoading = false
            }
        },
        async getSubAtomList (subAtomData) {
            this.subAtomListLoading = true
            try {
                const data = await this.loadSubAtomList(subAtomData)
                this.setSubAtom(data)
                this.handleSubflowGroup()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.subAtomListLoading = false
            }
        },
        async getTemplateData () {
            this.templateDataLoading = true
            try {
                const data = {
                    templateId: this.template_id,
                    common: this.common
                }
                const templateData = await this.loadTemplateData(data)
                if (this.type === 'clone') {
                    templateData.name = templateData.name.slice(0, STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH - 6) + '_clone'
                }
                this.setTemplateData(templateData)
                // const business = data.business
                // if (business !== undefined) {
                //     this.businessTimeZone = data.business.timezone
                // }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.templateDataLoading = false
            }
        },
        async getSingleAtomConfig (location) {
            const atomType = location.atomId
            if ($.atoms[atomType]) {
                this.addSingleAtomActivities(location, $.atoms[atomType])
                return
            }
            this.atomConfigLoading = true
            try {
                await this.loadAtomConfig({atomType})
                this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                this.addSingleAtomActivities(location, $.atoms[atomType])
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.atomConfigLoading = false
            }
        },
        async getSubflowConfig (location) { // get subflow constants and add node
            try {
                const subflowConfig = await this.loadSubflowConfig({templateId: location.atomId, version: location.atomVersion, common: this.common})
                const constants = tools.deepClone(subflowConfig.form)
                const activities = tools.deepClone(this.activities[location.id])
                for (let key in constants) {
                    const form = constants[key]
                    if (form.source_tag) {
                        const [ atomType, tagCode ] = form.source_tag.split('.')
                        if (!this.atomFormConfig[atomType]) {
                            await this.loadAtomConfig({atomType})
                            this.setAtomConfig({atomType, configData: $.atoms[atomType]})
                        }
                        const atomConfig = this.atomFormConfig[atomType]
                        let currentFormConfig = tools.deepClone(atomFilter.formFilter(tagCode, atomConfig))
                        if (currentFormConfig) {
                            if (form.is_meta || currentFormConfig.meta_transform) {
                                currentFormConfig = currentFormConfig.meta_transform(form.meta || form)
                                if (!form.meta) {
                                    form.value = currentFormConfig.attrs.value
                                }
                            }
                        }
                    }
                }
                activities.constants = constants || {}
                this.setActivities({type: 'edit', location: activities})
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async saveTemplate () {
            this.templateSaving = true
            const template_id = this.type === 'edit' ? this.template_id : undefined
            try {
                const data = await this.saveTemplateData({'templateId': template_id,'ccId': this.cc_id, 'common': this.common})
                if (template_id === undefined) {
                    // 保存模板之前有本地缓存
                    draft.draftReplace(this.username, this.cc_id, data.template_id, this.templateUUID)
                }
                this.$bkMessage({
                    message: i18n.saved,
                    theme: 'success'
                })
                this.isTemplateDataChanged = false
                if (this.type !== 'edit') {
                    this.allowLeave = true
                    this.$router.push({path: `/template/edit/${this.cc_id}/`, query: {'template_id': data.template_id, 'common': this.common}})
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.templateSaving = false
            }
        },
        addSingleAtomActivities (location, config) {
            const data = {}
            const defaultValue = atomFilter.getFormItemDefaultValue(config)
            config.forEach(item => {
                data[item.tag_code] = {
                    hook: false,
                    value: defaultValue[item.tag_code]
                }
            })
            const activities = tools.deepClone(this.activities[location.id])
            activities.component.data = data
            this.setActivities({type: 'edit', location: activities})
        },
        // 子流程分组
        handleSubflowGroup () {
            const primaryData = this.subAtom
            const groups = []
            const atomGrouped = []
            this.businessBaseInfo.task_categories.forEach(item => {
                groups.push(item.value)
                atomGrouped.push({
                    type: item.value,
                    group_name: item.name,
                    group_icon: '',
                    list: []
                })
            })
            primaryData.forEach(item => {
                const type = item.category
                const index = groups.indexOf(type)
                if (index > -1) {
                    atomGrouped[index].list.push(item)
                }
            })

            this.subAtomGrouped = atomGrouped
        },
        toggleSettingPanel (isSettingPanelShow){
            this.isSettingPanelShow = isSettingPanelShow
        },
        showConfigPanel (id) {
            this.variableDataChanged()
            this.isNodeConfigPanelShow = true
            this.idOfNodeInConfigPanel = id
        },
        hideConfigPanel () {
            if (this.idOfNodeInConfigPanel) {
                this.onUpdateNodeInfo(this.idOfNodeInConfigPanel, { isActived: false })
            }
            this.isNodeConfigPanelShow = false
            this.idOfNodeInConfigPanel = ''
        },
        /**
         * 标识模板是否被编辑
         */
        variableDataChanged () {
            this.isTemplateDataChanged = true
        },
        /**
         * 普通标准插件节点校验，不包括子流程节点
         * 校验项包含：标准插件类型，节点名称，输入参数
         * @return isAllValid {Boolean} 节点是否合法
         */
        validateAtomNode () {
            let isAllValid = true
            Object.keys(this.activities).forEach(id => {
                let isNodeValid = true
                const node = this.activities[id]
                if (node.type === 'ServiceActivity') {
                    if (!node.name) { // 节点名称为空
                        isNodeValid = false
                    }
                    if (node.component.code) {
                        if (!this.validateAtomInputForm(node.component)) {
                            isNodeValid = false // 输入参数校验不通过
                        }
                    } else {
                        isNodeValid = false // 节点标准插件类型为空
                    }
                }
                if (!isNodeValid) {
                    isAllValid = false
                    this.markInvalidNode(id)
                }
            })
            if (!isAllValid) {
                this.$bkMessage({
                    message: i18n.error,
                    theme: 'error'
                })
            }
            return isAllValid
        },
        // 校验输入参数是否满足标准插件配置文件正则校验
        validateAtomInputForm (component) {
            const { code, data } = component
            const config = this.atomConfig[code]
            if (!data) return false
            if (config) {
                const formData = {}
                Object.keys(data).forEach(key => {
                    formData[key] = data[key].value
                })
                return this.checkAtomData(config, formData)
            }
            return true
        },
        // tag 表单校验
        checkAtomData (config, formData) {
            let isValid = true
            config.forEach(item => {
                const { tag_code, type, attrs } = item
                const value = formData[tag_code]
                if (type === 'combine') {
                    if (!this.checkAtomData(attrs.children, value)) {
                        isValid = false
                    }
                } else {
                    if (attrs.validation && attrs.validation.length) {
                        attrs.validation.forEach(item => {
                            if (item.type === 'required') {
                                if (tools.isEmpty(value)) {
                                    isValid = false
                                }
                            }
                            if (item.type === 'regex') {
                                const reg = new RegExp(item.args)
                                if (!reg.test(value)) {
                                    isValid = false
                                }
                            }
                            if (item.type === 'custom') {
                                if (!/^\${[^${}]+}$/.test(value)) { // '${xxx}'格式的值不校验
                                    const validateInfo = item.args.call(this, value, formData)
                                    if (!validateInfo.result) {
                                        isValid = false
                                    }
                                }
                            }
                        })
                    }
                }
            })
            return isValid
        },
        /**
         * 参数错误节点标记为红色
         */
        markInvalidNode (id) {
            this.onUpdateNodeInfo(id, {status: 'FAILED'})
        },
        /**
         * 节点搜索
         */
        onSearchAtom (data) {
            const payload = {
                ...data,
                exclude: this.type !== 'new' ? [Number(this.template_id)] : []
            }
            this.searchAtom(payload)
        },
        /**
         * 任务节点点击
         */
        onNodeClick (id) {
            const currentId = this.idOfNodeInConfigPanel
            const nodeType = this.locations.filter(item => {return item.id === id})[0].type
            if (nodeType === 'tasknode' || nodeType === 'subflow'){
                // 清除当前节点选中态
                if (currentId) {
                    this.onUpdateNodeInfo(currentId, { isActived: false })
                }
                this.onUpdateNodeInfo(id, { isActived: true })

                if (this.isNodeConfigPanelShow) {
                    this.$refs.nodeConfig.syncNodeDataToActivities().then(isValid => {
                        this.showConfigPanel(id)
                    })
                } else {
                    this.showConfigPanel(id)
                }
            }
        },
        // 分支网关失焦
        onLabelBlur (labelData) {
            this.variableDataChanged()
            this.setBranchCondition(labelData)
        },
        onLocationChange (changeType, location) {
            this.setLocation({type: changeType, location})
            switch (location.type) {
                case 'tasknode':
                    if (changeType === 'add' && location.atomId) {  // drag new single node
                        this.setActivities({type: 'add', location})
                        this.getSingleAtomConfig(location)
                        return
                    }
                    if (changeType === 'delete') {
                        this.hideConfigPanel()
                    }
                    this.setActivities({type: changeType, location})
                    break
                case 'subflow':
                    if (changeType === 'add' && location.atomId) { // drag new subflow node
                        this.setActivities({type: 'add', location})
                        this.getSubflowConfig(location)
                        return
                    }
                    if (changeType === 'delete') {
                        this.hideConfigPanel()
                    }
                    this.setActivities({type: changeType, location})
                    break
                case 'branchgateway':
                case 'parallelgateway':
                case 'convergegateway':
                    this.setGateways({type: changeType, location})
                    break
                case 'startpoint':
                    this.setStartpoint({type: changeType, location})
                    break
                case 'endpoint':
                    this.setEndpoint({type: changeType, location})
                    break
            }
        },
        onLineChange (changeType, line) {
            this.setLine({type: changeType, line})
        },
        onLocationMoveDone (location) {
            this.variableDataChanged()
            this.setLocationXY(location)
        },
        onUpdateNodeInfo (id, data) {
            this.$refs.pipelineCanvas.onUpdateNodeInfo(id, data)
        },
        onDeleteConstant (key) {
            this.variableDataChanged()
            if (this.isNodeConfigPanelShow) {
                const constant = this.constants[key]
                this.$refs.nodeConfig.onDeleteConstant(constant)
            }
        },
        // 流程名称修改
        onChangeName (name) {
            this.variableDataChanged()
            this.setTemplateName(name)
        },
        // 基础属性-->模板分类修改
        onSelectCategory (value) {
            if (value) {
                this.isTemplateConfigValid = true
            }
        },
        // 点击保存模板按钮回调
        onSaveTemplate () {
            if (this.templateSaving) return
            this.checkVariable() // 全局变量是否合法
        },
        // 校验全局变量
        checkVariable () {
            const templateSetting = this.$refs.templateSetting
            if (templateSetting.isEditPanelOpen()) {
                templateSetting.saveVariable().then(result => {
                    if (!result) {
                        templateSetting.setErrorTab('globalVariableTab')
                        return
                    }
                    this.checkBasicProperty() // 基础属性是否合法
                })
            } else {
                this.checkBasicProperty() // 基础属性是否合法
            }
        },
        // 校验基础属性
        checkBasicProperty () {
            const templateSetting = this.$refs.templateSetting
            // 模板分类是否选择
            if (!this.category) {
                this.isTemplateConfigValid = false
                templateSetting.setErrorTab('templateConfigTab')
                return
            }
            this.asyncNodeConfig() // 节点配置面板
        },
        // 同步节点配置面板数据
        asyncNodeConfig () {
            if (this.isNodeConfigPanelShow) {
                this.$refs.nodeConfig.syncNodeDataToActivities().then((isValid) => {
                    if (!isValid) return
                    this.checkNodeAndSaveTemplate()
                })
            } else {
                this.checkNodeAndSaveTemplate()
            }
        },
        // 校验节点配置
        checkNodeAndSaveTemplate () {
            // 节点配置是否错误
            const nodeWithErrors = document.querySelectorAll('.node-with-text.FAILED')
            if (nodeWithErrors && nodeWithErrors.length) {
                this.templateSaving = false
                errorHandler({message: i18n.error}, this)
                return
            }
            const isAllNodeValid = this.validateAtomNode()

            if (isAllNodeValid) {
                this.saveTemplate()
            }
        },
        onBackToList () {
            this.$router.push({path: `/template/home/${this.cc_id}/`})
        },
        onLeaveConfirm () {
            this.allowLeave = true
            this.$router.push({path: this.leaveToPath})
        },
        onLeaveCancel () {
            this.allowLeave = false
            this.leaveToPath = ''
            this.isLeaveDialogShow = false
        },
        // 删除本地缓存
        onDeleteDraft (key) {
            if (draft.deleteDraft(key)) {
                this.$bkMessage({
                    'message': i18n.delete_success,
                    'theme': 'success'
                })
            } else {
                this.$bkMessage({
                    'message': i18n.delete_fail,
                    'theme': 'error'
                })
            }
            // 删除后刷新
            this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID())
        },
        // 模板替换
        onReplaceTemplate (data) {
            const {templateData, type} = data
            if (type === 'replace') {
                const nowTemplateSerializable = JSON.stringify(this.getLocalTemplateData())
                const lastDraft = JSON.parse(draft.getLastDraft(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID()))
                const lastTemplate = lastDraft['template']
                const lastTemplateSerializable = JSON.stringify(lastTemplate)
                // 替换之前进行保存
                if (nowTemplateSerializable !== lastTemplateSerializable) {
                    draft.addDraft(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData(), i18n.replace_save)
                }
                this.$bkMessage({
                    'message': i18n.replace_success,
                    'theme': 'success'
                })
            }
            this.templateDataLoading = true
            this.replaceTemplate(templateData)
            // 替换后后刷新
            this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID())
            this.$nextTick(() => {
                this.templateDataLoading = false
                this.$nextTick(() => {
                    this.isClickDraft = type === 'replace'
                    this.$refs.templateSetting.onTemplateSettingShow('localDraftTab')
                })
            })
        },
        // 新增本地缓存
        onNewDraft (message, isMessage = true) {
            // 创建本地缓存
            if (this.type === 'clone') {
                draft.addDraft(this.username, this.cc_id, this.templateUUID, this.getLocalTemplateData(), message)
                // 创建后后刷新
                this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.templateUUID)
            }
            else {
                draft.addDraft(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData(), message)
                // 创建后后刷新
                this.draftArray = draft.getDraftArray(this.username, this.cc_id, this.getTemplateIdOrTemplateUUID())
            }
            if (isMessage) {
                this.$bkMessage({
                    'message': i18n.add_cache,
                    'theme': 'success'
                })
            }
        },
        // 修改line和location
        onReplaceLineAndLocation (data) {
            this.replaceLineAndLocation(data)
        },
        getTemplateIdOrTemplateUUID () {
            let template_id = ''
            if (this.template_id === undefined || this.template_id === '') {
                return this.templateUUID
            }
            return this.template_id
        },
        updateLocalTemplateData () {
            this.localTemplateData =  this.getLocalTemplateData()
        }
    },
    beforeRouteLeave (to, from, next) { // leave or reload page
        if (this.allowLeave || !this.isTemplateDataChanged) {
            // 退出时需要关闭定时器
            clearInterval(this.intervalSaveTemplate)
            clearInterval(this.intervalGetDraftArray)
            let template_id = this.getTemplateIdOrTemplateUUID()
            // 如果是 uuid 或者克隆的模板会进行删除
            if (template_id.length === 28 || this.type === 'clone') {
                draft.deleteAllDraftByUUID(this.username, this.cc_id, this.templateUUID)
            }
            if (this.common) {
                to.params.cc_id = this.defaultCCId
            }
            this.clearAtomForm()
            next()
        } else {
            this.leaveToPath = to.fullPath
            this.isLeaveDialogShow = true
        }
    }
}
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    .template-page {
        position: relative;
        min-width: 1320px;
        min-height: 600px;
        height: calc(100% - 50px);
        overflow: hidden;
    }
    .pipeline-canvas-wrapper {
        height: 100%;
    }
</style>

