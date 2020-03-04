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
    <div class="template-page" v-bkloading="{ isLoading: templateDataLoading }">
        <div v-if="!templateDataLoading" class="pipeline-canvas-wrapper">
            <TemplateHeader
                :name="name"
                :project_id="project_id"
                :type="type"
                :common="common"
                :template_id="template_id"
                :is-template-data-changed="isTemplateDataChanged"
                :template-saving="templateSaving"
                :create-task-saving="createTaskSaving"
                :tpl-resource="tplResource"
                :tpl-actions="tplActions"
                :tpl-operations="tplOperations"
                @onChangeName="onChangeName"
                @onNewDraft="onNewDraft"
                @onSaveTemplate="onSaveTemplate">
            </TemplateHeader>
            <TemplateCanvas
                ref="templateCanvas"
                class="template-canvas"
                :single-atom-list-loading="singleAtomListLoading"
                :sub-atom-list-loading="subAtomListLoading"
                :atom-type-list="atomTypeList"
                :name="name"
                :type="type"
                :common="common"
                :template_id="template_id"
                :canvas-data="canvasData"
                @hook:mounted="canvasMounted"
                @onConditionClick="onOpenConditionEdit"
                @variableDataChanged="variableDataChanged"
                @onNodeMousedown="onNodeMousedown"
                @onShowNodeConfig="onShowNodeConfig"
                @onLabelBlur="onLabelBlur"
                @onLocationChange="onLocationChange"
                @onLineChange="onLineChange"
                @onLocationMoveDone="onLocationMoveDone"
                @onFormatPosition="onFormatPosition"
                @onReplaceLineAndLocation="onReplaceLineAndLocation">
            </TemplateCanvas>
            <NodeConfig
                ref="nodeConfig"
                :project_id="project_id"
                v-show="isNodeConfigPanelShow"
                :is-show="isNodeConfigPanelShow"
                :setting-active-tab="settingActiveTab"
                :template_id="template_id"
                :single-atom="singleAtom"
                :sub-atom="subAtom"
                :is-setting-panel-show="isSettingPanelShow"
                :is-node-config-panel-show="isNodeConfigPanelShow"
                :id-of-node-in-config-panel="idOfNodeInConfigPanel"
                :common="common"
                @hideConfigPanel="hideConfigPanel"
                @globalVariableUpdate="globalVariableUpdate"
                @onUpdateNodeInfo="onUpdateNodeInfo">
            </NodeConfig>
            <ConditionEdit
                ref="conditionEdit"
                :condition-data="conditionData"
                :is-setting-panel-show="isSettingPanelShow"
                :is-show-condition-edit="isShowConditionEdit"
                v-show="isShowConditionEdit"
                @onCloseConditionEdit="onCloseConditionEdit">
            </ConditionEdit>
            <TemplateSetting
                ref="templateSetting"
                :draft-array="draftArray"
                :is-global-variable-update="isGlobalVariableUpdate"
                :project-info-loading="projectInfoLoading"
                :is-template-config-valid="isTemplateConfigValid"
                :is-setting-panel-show="isSettingPanelShow"
                :is-node-config-panel-show="isNodeConfigPanelShow"
                :variable-type-list="variableTypeList"
                :local-template-data="localTemplateData"
                :is-click-draft="isClickDraft"
                @toggleSettingPanel="toggleSettingPanel"
                @globalVariableUpdate="globalVariableUpdate"
                @onDeleteConstant="onDeleteConstant"
                @variableDataChanged="variableDataChanged"
                @onSelectCategory="onSelectCategory"
                @onDeleteDraft="onDeleteDraft"
                @onReplaceTemplate="onReplaceTemplate"
                @onNewDraft="onNewDraft"
                @onCitedNodeClick="onCitedNodeClick"
                @updateLocalTemplateData="updateLocalTemplateData"
                @modifyTemplateData="modifyTemplateData"
                @hideConfigPanel="hideConfigPanel"
                @updataConditionData="updataConditionData">
            </TemplateSetting>
            <bk-dialog
                width="400"
                ext-cls="common-dialog"
                :theme="'primary'"
                :mask-close="false"
                :header-position="'left'"
                :title="i18n.leave"
                :value="isLeaveDialogShow"
                @confirm="onLeaveConfirm"
                @cancel="onLeaveCancel">
                <div class="leave-tips">{{ i18n.tips }}</div>
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
    import validatePipeline from '@/utils/validatePipeline.js'
    import TemplateHeader from './TemplateHeader.vue'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import TemplateSetting from './TemplateSetting/index.vue'
    import NodeConfig from './NodeConfig.vue'
    import ConditionEdit from './ConditionEdit.vue'
    import draft from '@/utils/draft.js'
    import Guide from '@/utils/guide.js'
    import { STRING_LENGTH } from '@/constants/index.js'

    const i18n = {
        templateEdit: gettext('流程编辑'),
        leave: gettext('离开页面'),
        tips: gettext('系统不会保存您所做的更改，确认离开？'),
        saved: gettext('保存成功'),
        error: gettext('任务节点参数错误，请点击错误节点查看详情'),
        conditionError: gettext('分支节点参数错误，请点击错误节点查看详情'),
        deleteSuccess: gettext('删除本地缓存成功'),
        deleteFail: gettext('该本地缓存不存在，删除失败'),
        replaceSuccess: gettext('替换流程成功'),
        addCache: gettext('新增流程本地缓存成功'),
        replaceSave: gettext('替换流程自动保存'),
        layoutSave: gettext('排版完成，原内容在本地缓存中')
    }

    export default {
        name: 'TemplateEdit',
        components: {
            TemplateHeader,
            TemplateCanvas,
            NodeConfig,
            ConditionEdit,
            TemplateSetting
        },
        props: ['template_id', 'type', 'common'],
        data () {
            return {
                i18n,
                bkMessageInstance: null,
                exception: {},
                singleAtomListLoading: false,
                subAtomListLoading: false,
                projectInfoLoading: false,
                templateDataLoading: false,
                templateSaving: false,
                createTaskSaving: false,
                saveAndCreate: false,
                isGlobalVariableUpdate: false, // 全局变量是否有更新
                isTemplateConfigValid: true, // 模板基础配置是否合法
                isTemplateDataChanged: false,
                isSettingPanelShow: true,
                isNodeConfigPanelShow: false,
                isLeaveDialogShow: false,
                variableTypeList: [], // 自定义变量类型列表
                customVarCollectionLoading: false,
                allowLeave: false,
                isShowConditionEdit: false,
                settingActiveTab: 'globalVariableTab',
                lastOpenPanelName: '', // 最近一次打开的面板名
                leaveToPath: '',
                idOfNodeInConfigPanel: '',
                idOfNodeShortcutPanel: '',
                subAtomGrouped: [],
                draftArray: [],
                intervalSaveTemplate: null,
                intervalGetDraftArray: null,
                templateUUID: uuid(),
                localTemplateData: null,
                isClickDraft: false,
                tplOperations: [],
                tplActions: [],
                tplResource: {},
                conditionData: {},
                nodeGuideConfig: {
                    el: '',
                    width: 150,
                    placement: 'bottom',
                    once: true,
                    arrow: true,
                    img: {
                        height: 112,
                        url: require('@/assets/images/node-double-click-guide.gif')
                    },
                    text: [
                        {
                            type: 'name',
                            val: gettext('双击左键')
                        },
                        {
                            type: 'text',
                            val: gettext('可以快捷打开节点配置面板')
                        }
                    ]
                }
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
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'category': state => state.template.category,
                'subprocess_info': state => state.template.subprocess_info,
                'username': state => state.username,
                'site_url': state => state.site_url,
                'atomFormConfig': state => state.atomForm.config,
                'SingleAtomVersionMap': state => state.atomForm.SingleAtomVersionMap
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'project_id': state => state.project_id
            }),
            ...mapGetters('atomList/', [
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
            projectOrCommon () { // 画布数据缓存参数之一，公共流程没有 project_id，取 'common'
                return this.common ? 'common' : this.project_id
            },
            canvasData () {
                const branchConditions = {}
                for (const gKey in this.gateways) {
                    const item = this.gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                return {
                    activities: this.activities,
                    lines: this.lines,
                    locations: this.locations.map(location => {
                        let icon, group, code
                        const atom = this.singleAtom.find(item => {
                            if (location.type === 'tasknode') {
                                return this.activities[location.id].component.code === item.code
                            }
                        })
                        if (atom) {
                            icon = atom.group_icon
                            group = atom.group_name
                            code = atom.code
                        }
                        const data = { ...location, mode: 'edit', icon, group, code }
                        if (
                            this.subprocess_info
                            && this.subprocess_info.details
                            && location.type === 'subflow'
                        ) {
                            this.subprocess_info.details.some(subflow => {
                                if (subflow.subprocess_node_id === location.id && subflow.expired) {
                                    data.hasUpdated = true
                                    return true
                                }
                            })
                        }
                        return data
                    }),
                    branchConditions
                }
            },
            // draftProjectId
            draftProjectId () {
                return this.common ? 'common' : this.project_id
            }
        },
        async created () {
            this.initTemplateData()
            // 获取流程内置变量
            this.templateDataLoading = true
            const result = await this.loadInternalVariable()
            this.setInternalVariable(result.data || [])
            if (this.type === 'edit' || this.type === 'clone') {
                this.getTemplateData()
            } else {
                const name = 'new' + moment.tz(this.timeZone).format('YYYYMMDDHHmmss')
                this.setTemplateName(name)
                this.templateDataLoading = false
            }

            // 复制并替换本地缓存的内容
            if (this.type === 'clone') {
                draft.copyAndReplaceDraft(this.username, this.projectOrCommon, this.template_id, this.templateUUID)
                this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.templateUUID)
            } else {
                // 先执行一次获取本地缓存
                this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID())
            }
            // 五分钟进行存储本地缓存
            const fiveMinutes = 1000 * 60 * 5
            this.intervalSaveTemplate = setInterval(() => {
                draft.addDraft(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData())
            }, fiveMinutes)

            // 五分钟多5秒 为了用于存储本地缓存过程的时间消耗
            const fiveMinutesAndFiveSeconds = fiveMinutes + 5000
            this.intervalGetDraftArray = setInterval(() => {
                this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID())
            }, fiveMinutesAndFiveSeconds)
        },
        mounted () {
            this.getSingleAtomList()
            this.getProjectBaseInfo()
            this.getCustomVarCollection()
            window.onbeforeunload = function () {
                return i18n.tips
            }
            window.addEventListener('resize', this.onWindowResize, false)
        },
        beforeDestroy () {
            window.onbeforeunload = null
            this.resetTemplateData()
            this.hideGuideTips()
            window.removeEventListener('resize', this.onWindowResize, false)
        },
        methods: {
            ...mapActions('atomList/', [
                'loadSingleAtomList',
                'loadSubAtomList'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'loadTemplateData',
                'saveTemplateData',
                'loadCommonTemplateData',
                'loadCustomVarCollection',
                'loadInternalVariable',
                'getLayoutedPipeline'
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
                'setProjectBaseInfo',
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
                'setInternalVariable',
                'replaceTemplate',
                'replaceLineAndLocation',
                'setPipelineTree'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm',
                'setVersionMap'
            ]),
            ...mapGetters('template/', [
                'getLocalTemplateData',
                'getPipelineTree'
            ]),
            async getSingleAtomList () {
                this.singleAtomListLoading = true
                try {
                    const data = await this.loadSingleAtomList()
                    this.setSingleAtom(data)
                    this.updateStoreVersionMap(data)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.singleAtomListLoading = false
                }
            },
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                try {
                    const data = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(data)
                    const subAtomData = {
                        project_id: this.project_id,
                        common: this.common,
                        templateId: this.template_id
                    }
                    this.getSubAtomList(subAtomData)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.projectInfoLoading = false
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
            async getCustomVarCollection () {
                this.customVarCollectionLoading = true
                try {
                    const customVarCollection = await this.loadCustomVarCollection()
                    const listData = [
                        {
                            name: gettext('普通变量'),
                            children: []
                        },
                        {
                            name: gettext('元变量'),
                            children: []
                        }
                    ]
                    customVarCollection.forEach(item => {
                        if (item.type === 'general') {
                            listData[0].children.push(item)
                        } else {
                            listData[1].children.push(item)
                        }
                    })
                    this.variableTypeList = listData
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.customVarCollectionLoading = false
                }
            },
            async getTemplateData () {
                try {
                    const data = {
                        templateId: this.template_id,
                        common: this.common
                    }
                    const templateData = await this.loadTemplateData(data)
                    this.tplOperations = templateData.auth_operations
                    this.tplActions = templateData.auth_actions
                    this.tplResource = templateData.auth_resource
                    if (this.type === 'clone') {
                        templateData.name = templateData.name.slice(0, STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH - 6) + '_clone'
                    }
                    this.setTemplateData(templateData)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.templateDataLoading = false
                }
            },
            async getSingleAtomConfig (location) {
                const atomType = location.atomId
                const version = this.SingleAtomVersionMap[atomType]
                if (this.atomConfig[atomType] && this.atomConfig[atomType][version]) {
                    this.addSingleAtomActivities(location, this.atomConfig[atomType][version])
                    return
                }
                // 接口获取最新配置信息
                this.atomConfigLoading = true
                try {
                    await this.loadAtomConfig({ atomType, version })
                    this.addSingleAtomActivities(location, $.atoms[atomType])
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            async getSubflowConfig (location) { // get subflow constants and add node
                try {
                    const subflowConfig = await this.loadSubflowConfig({ templateId: location.atomId, version: location.atomVersion, common: this.common })
                    const constants = tools.deepClone(subflowConfig.form)
                    const activities = tools.deepClone(this.activities[location.id])
                    for (const key in constants) {
                        const form = constants[key]
                        const { atomType, atom, tagCode, classify } = atomFilter.getVariableArgs(form)
                        // 全局变量版本
                        const version = form.version || 'legacy'
                        if (!atomFilter.isConfigExists(atomType, version, this.atomFormConfig)) {
                            await this.loadAtomConfig({ atomType, classify, saveName: atom })
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
                        }
                    }
                    activities.constants = constants || {}
                    this.setActivities({ type: 'edit', location: activities })
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async saveTemplate () {
                const template_id = this.type === 'edit' ? this.template_id : undefined
                if (this.saveAndCreate) {
                    this.createTaskSaving = true
                } else {
                    this.templateSaving = true
                }

                try {
                    const data = await this.saveTemplateData({ 'templateId': template_id, 'projectId': this.project_id, 'common': this.common })
                    this.tplActions = data.auth_actions
                    this.tplOperations = data.auth_operations
                    this.tplResource = data.auth_resource
                    if (template_id === undefined) {
                        // 保存模板之前有本地缓存
                        draft.draftReplace(this.username, this.projectOrCommon, data.template_id, this.templateUUID)
                    }
                    this.$bkMessage({
                        message: i18n.saved,
                        theme: 'success'
                    })
                    this.isTemplateDataChanged = false
                    if (this.type !== 'edit') {
                        this.allowLeave = true
                        const url = { name: 'templatePanel', params: { type: 'edit' }, query: { 'template_id': data.template_id, 'common': this.common } }
                        if (this.common) {
                            url.name = 'commonTemplatePanel'
                        }
                        this.$router.push(url)
                    }
                    if (this.createTaskSaving) {
                        this.goToTaskUrl(data.template_id)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.saveAndCreate = false
                    this.templateSaving = false
                    this.createTaskSaving = false
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
                this.setActivities({ type: 'edit', location: activities })
            },
            // 子流程分组
            handleSubflowGroup () {
                const primaryData = this.subAtom
                const groups = []
                const atomGrouped = []
                this.projectBaseInfo.task_categories.forEach(item => {
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
            toggleSettingPanel (isSettingPanelShow, activeTab) {
                const clientX = document.body.clientWidth
                // 分辨率 1920 以下，显示 setting 面板时需隐藏节点配置面板
                if (isSettingPanelShow && this.isNodeConfigPanelShow && clientX < 1920) {
                    this.hideConfigPanel()
                }
                if (isSettingPanelShow) {
                    this.lastOpenPanelName = 'settingPanel'
                }
                this.isSettingPanelShow = isSettingPanelShow
                this.settingActiveTab = activeTab
            },
            showConfigPanel (id) {
                this.variableDataChanged()
                this.isNodeConfigPanelShow = true
                this.idOfNodeInConfigPanel = id
                this.lastOpenPanelName = 'nodeConfigPanel'
            },
            hideConfigPanel () {
                this.isNodeConfigPanelShow = false
                this.idOfNodeInConfigPanel = ''
            },
            onWindowResize () {
                const clientX = document.body.clientWidth
                // 在配置面板和setting面板双开时，屏幕突然改变保留最近打开的面板
                if (clientX < 1920
                    && this.isNodeConfigPanelShow
                    && this.isSettingPanelShow
                    && ['templateDataEditTab', 'globalVariableTab'].includes(this.settingActiveTab)) {
                    if (this.lastOpenPanelName === 'settingPanel') {
                        this.hideConfigPanel()
                    } else {
                        this.toggleSettingPanel(false)
                    }
                }
            },
            // 全局变量引用节点点击回调
            onCitedNodeClick (nodeId) {
                if (this.idOfNodeInConfigPanel === nodeId) {
                    const nodeType = this.locations.filter(item => {
                        return item.id === nodeId
                    })[0].type
                    if ((nodeType === 'tasknode' || nodeType === 'subflow') && this.isNodeConfigPanelShow) {
                        if (this.isNodeConfigPanelShow) {
                            this.$refs.nodeConfig.syncNodeDataToActivities().then(isValid => {
                                this.hideConfigPanel()
                            })
                        }
                    }
                } else {
                    this.onShowNodeConfig(nodeId, false)
                }
            },
            /**
             * 标识模板是否被编辑
             */
            variableDataChanged () {
                this.isTemplateDataChanged = true
            },
            /**
             * 任务节点校验
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
                    } else {
                        if (!node.name || node.template_id === undefined) {
                            isNodeValid = false
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
                const { code, data, version } = component
                if (!data) return false
                if (this.atomConfig[code] && this.atomConfig[code][version]) {
                    const config = this.atomConfig[code][version]
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
                this.onUpdateNodeInfo(id, { status: 'FAILED' })
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
             * 节点 Mousedown 回调
             */
            onNodeMousedown (id) {
                this.$refs.conditionEdit && this.$refs.conditionEdit.closeConditionEdit()
            },
            /**
             * 打开节点配置面板
             */
            onShowNodeConfig (id, hideSettingPanel = true) {
                if (this.isShowConditionEdit) {
                    this.$refs.conditionEdit && this.$refs.conditionEdit.closeConditionEdit()
                }
                if (document.body.clientWidth < 1920 || hideSettingPanel) { // 分辨率 1920 以下关闭 settting 面板，或者手动关闭
                    this.toggleSettingPanel(false)
                }
                const nodeType = this.locations.filter(item => {
                    return item.id === id
                })[0].type
                if (nodeType === 'tasknode' || nodeType === 'subflow') {
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
                this.setBranchCondition(labelData)
            },
            async onFormatPosition () {
                const validateMessage = validatePipeline.isNodeLineNumValid(this.canvasData)
                if (!validateMessage.result) {
                    errorHandler({ message: validateMessage.message }, this)
                    return
                }
                if (this.canvasDataLoading) {
                    return
                }
                this.canvasDataLoading = true // @todo 支持画布单独loading
                try {
                    const pipelineTree = this.getPipelineTree()
                    const canvasEl = document.getElementsByClassName('canvas-flow-wrap')[0]
                    const width = canvasEl.offsetWidth - 200
                    const res = await this.getLayoutedPipeline({ width, pipelineTree })
                    if (res.result) {
                        this.onNewDraft(undefined, false)
                        this.$refs.templateCanvas.removeAllConnector()
                        this.setPipelineTree(res.data.pipeline_tree)
                        this.$nextTick(() => {
                            this.$refs.templateCanvas.updateCanvas()
                            this.$refs.templateCanvas.onResetPosition()
                            this.variableDataChanged()
                            this.$bkMessage({
                                message: i18n.layoutSave,
                                theme: 'success'
                            })
                        })
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.canvasDataLoading = false
                }
            },
            onLocationChange (changeType, location) {
                this.setLocation({ type: changeType, location })
                switch (location.type) {
                    case 'tasknode':
                    case 'subflow':
                        // 添加任务节点
                        if (changeType === 'add' && location.atomId) {
                            this.setActivities({ type: 'add', location })
                            if (location.type === 'tasknode') {
                                this.getSingleAtomConfig(location)
                            } else {
                                this.getSubflowConfig(location)
                            }
                            return
                        }
                        // 删除任务节点
                        if (changeType === 'delete') {
                            if (this.idOfNodeInConfigPanel === location.id) {
                                this.idOfNodeInConfigPanel = ''
                            }
                            this.hideConfigPanel()
                        }
                        this.setActivities({ type: changeType, location })
                        break
                    case 'branchgateway':
                    case 'parallelgateway':
                    case 'convergegateway':
                        this.setGateways({ type: changeType, location })
                        break
                    case 'startpoint':
                        this.setStartpoint({ type: changeType, location })
                        break
                    case 'endpoint':
                        this.setEndpoint({ type: changeType, location })
                        break
                }
            },
            onLineChange (changeType, line) {
                this.setLine({ type: changeType, line })
            },
            onLocationMoveDone (location) {
                this.setLocationXY(location)
            },
            globalVariableUpdate (val) {
                this.isGlobalVariableUpdate = val
            },
            onUpdateNodeInfo (id, data) {
                const location = this.canvasData.locations.find(item => item.id === id)
                const updatedLocation = Object.assign(location, data)
                this.setLocation({ type: 'edit', location: updatedLocation })
                this.$refs.templateCanvas.onUpdateNodeInfo(id, data)
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
            // 跳转到节点选择页面
            goToTaskUrl (template_id) {
                this.$router.push({
                    name: 'taskStep',
                    params: { step: 'selectnode', project_id: this.project_id },
                    query: {
                        template_id,
                        common: this.common,
                        entrance: 'templateEdit'
                    }
                })
            },
            // 点击保存模板按钮回调
            onSaveTemplate (saveAndCreate) {
                if (this.templateSaving || this.createTaskSaving) {
                    return
                }
                this.saveAndCreate = saveAndCreate
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
                    this.templateSaving = false
                    this.createTaskSaving = false
                    templateSetting.setErrorTab('templateConfigTab')
                    return
                }
                this.asyncNodeConfig() // 节点配置面板
            },
            // 同步节点配置面板数据
            asyncNodeConfig () {
                if (this.isNodeConfigPanelShow) {
                    this.$refs.nodeConfig.syncNodeDataToActivities().then(isValid => {
                        if (!isValid) return
                        this.asyncConditionData()
                    })
                } else {
                    this.asyncConditionData()
                }
            },
            // 同步分支条件面板数据
            asyncConditionData () {
                if (this.isShowConditionEdit) {
                    this.onSaveConditionData().then(isValid => {
                        if (!isValid) return
                        this.checkNodeAndSaveTemplate()
                    })
                } else {
                    this.checkNodeAndSaveTemplate()
                }
            },
            // 校验节点配置
            checkNodeAndSaveTemplate () {
                // 校验节点数目
                const validateMessage = validatePipeline.isNodeLineNumValid(this.canvasData)
                if (!validateMessage.result) {
                    errorHandler({ message: validateMessage.message }, this)
                    return
                }
                // 节点配置是否错误
                const nodeWithErrors = document.querySelectorAll('.canvas-node-item .failed')
                if (nodeWithErrors && nodeWithErrors.length) {
                    this.templateSaving = false
                    this.createTaskSaving = false
                    errorHandler({ message: i18n.error }, this)
                    return
                }
                const isAllNodeValid = this.validateAtomNode()
                const isAllConditionValid = this.checkConditionData(true)
                if (isAllNodeValid && isAllConditionValid) {
                    this.saveTemplate()
                }
            },
            onLeaveConfirm () {
                this.allowLeave = true
                this.$router.push({ path: this.leaveToPath })
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
                        'message': i18n.deleteSuccess,
                        'theme': 'success'
                    })
                } else {
                    this.$bkMessage({
                        'message': i18n.deleteFail,
                        'theme': 'error'
                    })
                }
                // 删除后刷新
                this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID())
            },
            // 模板替换
            onReplaceTemplate (data) {
                const { templateData, type } = data
                if (type === 'replace') {
                    const nowTemplateSerializable = JSON.stringify(this.getLocalTemplateData())
                    const lastDraft = JSON.parse(draft.getLastDraft(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID()))
                    const lastTemplate = lastDraft['template']
                    const lastTemplateSerializable = JSON.stringify(lastTemplate)
                    // 替换之前进行保存
                    if (nowTemplateSerializable !== lastTemplateSerializable) {
                        draft.addDraft(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData(), i18n.replaceSave)
                    }
                    this.$bkMessage({
                        'message': i18n.replaceSuccess,
                        'theme': 'success'
                    })
                }
                this.templateDataLoading = true
                this.replaceTemplate(templateData)
                // 替换后后刷新
                this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID())
                this.$nextTick(() => {
                    this.templateDataLoading = false
                    this.$nextTick(() => {
                        this.isClickDraft = type === 'replace'
                        this.$refs.templateSetting.onTemplateSettingShow('localDraftTab')
                        this.upDataAllNodeInfo()
                    })
                })
            },
            // 新增本地缓存
            onNewDraft (message, isMessage = true) {
                // 创建本地缓存
                if (this.type === 'clone') {
                    draft.addDraft(this.username, this.projectOrCommon, this.templateUUID, this.getLocalTemplateData(), message)
                    // 创建后后刷新
                    this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.templateUUID)
                } else {
                    draft.addDraft(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID(), this.getLocalTemplateData(), message)
                    // 创建后后刷新
                    this.draftArray = draft.getDraftArray(this.username, this.projectOrCommon, this.getTemplateIdOrTemplateUUID())
                }
                if (isMessage) {
                    this.$bkMessage({
                        'message': i18n.addCache,
                        'theme': 'success'
                    })
                }
            },
            // 修改line和location
            onReplaceLineAndLocation (data) {
                this.replaceLineAndLocation(data)
            },
            getTemplateIdOrTemplateUUID () {
                if (this.template_id === undefined || this.template_id === '') {
                    return this.templateUUID
                }
                return this.template_id
            },
            updateLocalTemplateData () {
                this.localTemplateData = this.getLocalTemplateData()
            },
            // 重新获得缓存后，更新 dom data[raw]上绑定的数据
            upDataAllNodeInfo () {
                const nodes = this.activities
                Object.keys(nodes).forEach((node, index) => {
                    this.onUpdateNodeInfo(node, {
                        status: '',
                        name: nodes[node].name,
                        stage_name: nodes[node].stage_name,
                        optional: nodes[node].optional,
                        error_ignorable: nodes[node].error_ignorable,
                        retryable: nodes[node].can_retry || nodes[node].retryable,
                        skippable: nodes[node].isSkipped || nodes[node].skippable
                    })
                })
            },
            // 打开分支条件编辑
            onOpenConditionEdit (data) {
                this.toggleSettingPanel(false)
                this.isNodeConfigPanelShow = false
                this.isShowConditionEdit = true
                this.$refs.conditionEdit.updateConditionData(data)
            },
            // 更新分支数据
            updataConditionData (data) {
                // 更新 store 数据
                this.onLabelBlur(data)
                // 更新 cavans 页面数据
                this.$refs.templateCanvas.updataConditionCanvasData(data)
                this.$nextTick(() => {
                    this.checkConditionData()
                })
            },
            // 校验分支数据
            checkConditionData (isShowError = false) {
                let checkResult = true
                const branchConditionDoms = document.querySelectorAll('.jtk-overlay .branch-condition')
                branchConditionDoms.forEach(dom => {
                    const name = dom.textContent
                    const value = dom.dataset.value
                    if (!name || !value) {
                        dom.classList.add('failed')
                        checkResult = false
                    }
                })
                if (!checkResult && isShowError) {
                    this.$bkMessage({
                        'message': i18n.conditionError,
                        'theme': 'error'
                    })
                }
                return checkResult
            },
            onCloseConditionEdit (data) {
                if (this.isShowConditionEdit) {
                    this.isShowConditionEdit = false
                    this.updataConditionData(data)
                    // 删除分支条件节点选中样式
                    document.querySelectorAll('.branch-condition.editing').forEach(dom => {
                        dom.classList.remove('editing')
                    })
                }
            },
            onSaveConditionData () {
                return this.$refs.conditionEdit.checkCurrentConditionData()
            },
            // 更新标准插件最新版本列表
            updateStoreVersionMap (data) {
                const actions = {}
                data.forEach(atom => {
                    const value = actions[atom.code]
                    if (value) {
                        if (value < atom.version || value === 'legacy') actions[atom.code] = atom.version
                    } else {
                        actions[atom.code] = atom.version
                    }
                    // actions[atom.code] = atom.version
                })
                this.setVersionMap(actions)
            },
            // 流程模板数据编辑更新
            modifyTemplateData (data) {
                this.templateDataLoading = true
                this.setPipelineTree(data)
                this.$nextTick(() => {
                    this.templateDataLoading = false
                })
            },
            handlerGuideTips () {
                if (this.type === 'new') {
                    const config = this.nodeGuideConfig
                    this.nodeGuide = new Guide(config)
                    this.nodeGuide.mount(document.querySelector('.task-node'))
                    this.nodeGuide.instance.show(1000)
                }
            },
            hideGuideTips () {
                if (this.nodeGuide) {
                    this.nodeGuide.instance.hide()
                }
            },
            canvasMounted () {
                this.handlerGuideTips()
            }
        },
        beforeRouteLeave (to, from, next) { // leave or reload page
            if (this.allowLeave || !this.isTemplateDataChanged) {
                // 退出时需要关闭定时器
                clearInterval(this.intervalSaveTemplate)
                clearInterval(this.intervalGetDraftArray)
                const template_id = this.getTemplateIdOrTemplateUUID()
                // 如果是 uuid 或者克隆的模板会进行删除
                if (template_id.length === 28 || this.type === 'clone') {
                    draft.deleteAllDraftByUUID(this.username, this.projectOrCommon, this.templateUUID)
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
        height: 100%;
        overflow: hidden;
    }
    .pipeline-canvas-wrapper {
        height: 100%;
    }
    .template-canvas {
        height: calc(100% - 60px);
    }
    .leave-tips {
        padding: 30px;
    }
</style>
