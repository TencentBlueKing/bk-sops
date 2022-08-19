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
    <div :class="['template-page', { 'tpl-view-model': isViewMode }]" v-bkloading="{ isLoading: templateDataLoading || singleAtomListLoading , zIndex: 100 }">
        <div v-if="!templateDataLoading" class="pipeline-canvas-wrapper">
            <TemplateHeader
                ref="templateHeader"
                :name="name"
                :project_id="project_id"
                :type="type"
                :common="common"
                :template_id="template_id"
                :is-global-variable-update="isGlobalVariableUpdate"
                :is-template-data-changed="isTemplateDataChanged"
                :template-saving="templateSaving"
                :create-task-saving="createTaskSaving"
                :active-tab="activeSettingTab"
                :tpl-actions="tplActions"
                :is-edit-process-page="isEditProcessPage"
                :is-preview-mode="isPreviewMode"
                :exclude-node="excludeNode"
                :execute-scheme-saving="executeSchemeSaving"
                @onDownloadCanvas="onDownloadCanvas"
                @goBackViewMode="goBackViewMode"
                @goBackToTplEdit="goBackToTplEdit"
                @onClosePreview="onClosePreview"
                @onOpenExecuteScheme="onOpenExecuteScheme"
                @onChangePanel="onChangeSettingPanel"
                @onSaveTemplate="onSaveTemplate">
            </TemplateHeader>
            <template v-if="isEditProcessPage">
                <SubflowUpdateTips
                    v-if="subflowShouldUpdated.length > 0"
                    class="update-tips"
                    :list="subflowShouldUpdated"
                    :locations="locations"
                    :is-view-mode="isViewMode"
                    @viewClick="viewUpdatedNode"
                    @batchUpdate="isBatchUpdateDialogShow = true"
                    @foldClick="clearDotAnimation">
                </SubflowUpdateTips>
                <TemplateCanvas
                    :key="isViewMode"
                    ref="templateCanvas"
                    class="template-canvas"
                    :atom-type-list="atomTypeList"
                    :name="name"
                    :show-palette="!isViewMode"
                    :editable="!isViewMode"
                    :common="common"
                    :template-labels="templateLabels"
                    :canvas-data="canvasData"
                    :node-variable-info="nodeVariableInfo"
                    @hook:mounted="canvasMounted"
                    @onConditionClick="onOpenConditionEdit"
                    @templateDataChanged="templateDataChanged"
                    @onLocationChange="onLocationChange"
                    @onLineChange="onLineChange"
                    @onLocationMoveDone="onLocationMoveDone"
                    @onFormatPosition="onFormatPosition"
                    @onReplaceLineAndLocation="onReplaceLineAndLocation"
                    @onShowNodeConfig="onShowNodeConfig"
                    @onTogglePerspective="onTogglePerspective"
                    @updateCondition="setBranchCondition($event)">
                </TemplateCanvas>
            </template>
            <TaskSelectNode
                v-else
                ref="taskSelectNode"
                :project_id="project_id"
                :common="common"
                :entrance="entrance"
                :template_id="template_id"
                :exclude-node="excludeNode"
                :is-edit-process-page="isEditProcessPage"
                :execute-scheme-saving="executeSchemeSaving"
                @onSaveExecuteSchemeClick="onSaveExecuteSchemeClick"
                @updateTaskSchemeList="updateTaskSchemeList"
                @togglePreviewMode="togglePreviewMode"
                @setExcludeNode="setExcludeNode">
            </TaskSelectNode>
            <div class="side-content">
                <node-config
                    ref="nodeConfig"
                    v-if="isNodeConfigPanelShow"
                    :is-view-mode="isViewMode"
                    :is-show="isNodeConfigPanelShow"
                    :atom-list="atomList"
                    :atom-type-list="atomTypeList"
                    :template-labels="templateLabels"
                    :common="common"
                    :form-enable="formEnable"
                    :project_id="project_id"
                    :node-id="idOfNodeInConfigPanel"
                    :back-to-variable-panel="backToVariablePanel"
                    @globalVariableUpdate="globalVariableUpdate"
                    @updateNodeInfo="onUpdateNodeInfo"
                    @templateDataChanged="templateDataChanged"
                    @close="closeConfigPanel">
                </node-config>
                <condition-edit
                    v-if="isShowConditionEdit"
                    ref="conditionEdit"
                    :is-show="isShowConditionEdit"
                    :is-readonly="isViewMode"
                    :gateways="gateways"
                    :condition-data="conditionData"
                    :back-to-variable-panel="backToVariablePanel"
                    @onBeforeClose="onBeforeClose"
                    @updataCanvasCondition="updataCanvasCondition"
                    @close="onCloseConfigPanel">
                </condition-edit>
                <template-setting
                    :is-view-mode="isViewMode"
                    :project-info-loading="projectInfoLoading"
                    :template-label-loading="templateLabelLoading"
                    :template-labels="templateLabels"
                    :active-tab.sync="activeSettingTab"
                    :snapshoots="snapshoots"
                    :common="common"
                    @viewClick="viewUpdatedNode"
                    @templateDataChanged="templateDataChanged"
                    @onCitedNodeClick="onCitedNodeClick"
                    @modifyTemplateData="modifyTemplateData"
                    @createSnapshoot="onCreateSnapshoot"
                    @useSnapshoot="onUseSnapshoot"
                    @updateTemplateLabelList="getTemplateLabelList"
                    @updateSnapshoot="onUpdateSnapshoot">
                </template-setting>
            </div>
            <bk-dialog
                class="batch-update-dialog"
                v-model="isBatchUpdateDialogShow"
                :close-icon="false"
                :fullscreen="true"
                data-test-id="templateEdit_form_batchUpdateDialog"
                :show-footer="false">
                <batch-update-dialog
                    v-if="isBatchUpdateDialogShow"
                    :project-id="project_id"
                    :common="common"
                    :list="subflowShouldUpdated"
                    @globalVariableUpdate="globalVariableUpdate"
                    @close="closeBatchUpdateDialog">
                </batch-update-dialog>
            </bk-dialog>
            <bk-dialog
                width="400"
                ext-cls="common-dialog"
                :theme="'primary'"
                :mask-close="false"
                :show-footer="false"
                :value="multipleTabDialogShow"
                data-test-id="templateEdit_form_commonDialog"
                @cancel="multipleTabDialogShow = false">
                <div class="multiple-tab-dialog-content">
                    <h3>{{ $t('确定保存修改的内容？') }}</h3>
                    <p><i class="bk-icon icon-exclamation-circle">{{ $t('当前流程模板在浏览器多个标签页打开') }}</i></p>
                    <div class="action-wrapper">
                        <bk-button theme="primary" @click="onMultipleTabConfirm">{{ $t('确定') }}</bk-button>
                        <bk-button theme="default" @click="multipleTabDialogShow = false">{{ $t('取消') }}</bk-button>
                    </div>
                </div>
            </bk-dialog>
            <bk-dialog
                ext-cls="template-edit-dialog"
                :theme="'primary'"
                :mask-close="false"
                :show-footer="false"
                :value="isExecuteSchemeDialog"
                data-test-id="templateEdit_form_tempEditDialog"
                @cancel="isExecuteSchemeDialog = false">
                <div class="template-edit-dialog-content">
                    <div class="save-tpl-tips">{{ tplEditDialogTip }}</div>
                    <p v-if="isMultipleTabCount > 1" class="multiple-tab-dialog-tip">
                        <i class="bk-icon icon-exclamation-circle">{{ $t('当前流程模板在浏览器多个标签页打开') }}</i>
                    </p>
                    <div class="action-wrapper">
                        <bk-button theme="primary" :loading="templateSaving || executeSchemeSaving" @click="onConfirmSave">{{ $t('确定') }}</bk-button>
                        <bk-button theme="default" :disabled="templateSaving || executeSchemeSaving" @click="onCancelSave">{{ $t('取消') }}</bk-button>
                    </div>
                </div>
            </bk-dialog>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
    // moment用于时区使用
    import moment from 'moment-timezone'
    import { uuid } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import validatePipeline from '@/utils/validatePipeline.js'
    import TemplateHeader from './TemplateHeader.vue'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import TemplateSetting from './TemplateSetting/index.vue'
    import NodeConfig from './NodeConfig/NodeConfig.vue'
    import ConditionEdit from './ConditionEdit.vue'
    import SubflowUpdateTips from './SubflowUpdateTips.vue'
    import tplSnapshoot from '@/utils/tplSnapshoot.js'
    import tplTabCount from '@/utils/tplTabCount.js'
    import Guide from '@/utils/guide.js'
    import permission from '@/mixins/permission.js'
    import { STRING_LENGTH } from '@/constants/index.js'
    import { NODES_SIZE_POSITION } from '@/constants/nodes.js'
    import TaskSelectNode from '../../task/TaskCreate/TaskSelectNode.vue'
    import BatchUpdateDialog from './BatchUpdateDialog.vue'
    import DealVarDirtyData from '@/utils/dealVarDirtyData.js'

    export default {
        name: 'TemplateEdit',
        components: {
            TemplateHeader,
            TemplateCanvas,
            TaskSelectNode,
            NodeConfig,
            ConditionEdit,
            TemplateSetting,
            SubflowUpdateTips,
            BatchUpdateDialog
        },
        mixins: [permission],
        props: ['template_id', 'type', 'common', 'entrance'],
        data () {
            return {
                isSchemaListChange: false,
                executeSchemeSaving: false,
                taskSchemeList: [],
                isPreviewMode: false,
                isExecuteSchemeDialog: false,
                isBackViewMode: false,
                isExecuteScheme: false, // 是否为执行方案
                isEditProcessPage: true,
                excludeNode: [],
                singleAtomListLoading: false,
                projectInfoLoading: false,
                templateDataLoading: false,
                templateSaving: false,
                createTaskSaving: false,
                saveAndCreate: false,
                pid: undefined, // 公共流程创建任务需要跳转到所选业务
                isGlobalVariableUpdate: false, // 全局变量是否有更新
                isTemplateDataChanged: false,
                isShowConditionEdit: false,
                isNodeConfigPanelShow: false, // 右侧模板是否展开
                isSelectorPanelShow: false, // 右侧子流程模板是否展开
                isLeaveDialogShow: false,
                activeSettingTab: '',
                allowLeave: false,
                leaveToPath: '',
                idOfNodeInConfigPanel: '',
                atomList: [],
                atomTypeList: {
                    tasknode: [],
                    subflow: []
                },
                thirdPartyList: {},
                snapshoots: [],
                snapshootTimer: null,
                templateLabels: [],
                templateLabelLoading: false,
                tplUUID: uuid(),
                tplActions: [],
                conditionData: {},
                multipleTabDialogShow: false,
                tplEditingTabCount: 0, // 正在编辑的模板在同一浏览器打开的数目
                isBatchUpdateDialogShow: false,
                backToVariablePanel: false,
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
                            val: i18n.t('双击左键')
                        },
                        {
                            type: 'text',
                            val: i18n.t('可以快捷打开节点配置面板')
                        }
                    ]
                },
                typeOfNodeNameEmpty: '', // 新建流程未选择插件的节点类型
                totalPage: 0,
                currentPage: 0,
                limit: 25,
                offset: 0,
                pollingTimer: null,
                isPageOver: false,
                isThrottled: false, // 滚动节流 是否进入cd
                envVariableData: {},
                validateConnectFailList: [], // 节点校验失败列表
                isPerspective: false, // 流程是否透视
                nodeVariableInfo: {}, // 节点输入输出变量
                initType: '', // 记录最初的流程类型
                isMultipleTabCount: 0,
                isRouterPush: false,
                formEnable: false // 子流程是否需要超时控制和异常处理
            }
        },
        computed: {
            ...mapState({
                'atomConfig': state => state.atomForm.config,
                'name': state => state.template.name,
                'activities': state => state.template.activities,
                'locations': state => state.template.location,
                'lines': state => state.template.line,
                'constants': state => state.template.constants,
                'gateways': state => state.template.gateways,
                'internalVariable': state => state.template.internalVariable,
                'category': state => state.template.category,
                'subprocess_info': state => state.template.subprocess_info,
                'username': state => state.username,
                'site_url': state => state.site_url,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone,
                'project_id': state => state.project_id
            }),
            canvasData () {
                const branchConditions = {}
                for (const gKey in this.gateways) {
                    const item = this.gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                    if (item.default_condition) {
                        const nodeId = item.default_condition.flow_id
                        branchConditions[item.id][nodeId] = item.default_condition
                    }
                }
                return {
                    activities: this.activities,
                    lines: this.lines,
                    locations: this.locations.map(location => {
                        let icon, group, code
                        if (location.type === 'tasknode') {
                            const nodeConfig = this.activities[location.id]
                            if (nodeConfig && nodeConfig.component.code === 'remote_plugin') {
                                icon = location.group_icon
                                group = location.group_name
                                code = nodeConfig.name
                            } else {
                                const atom = this.atomList.find(item => {
                                    return nodeConfig && nodeConfig.component.code === item.code
                                })
                                if (atom) {
                                    icon = atom.group_icon
                                    group = atom.group_name
                                    code = atom.code
                                }
                            }
                        }
                        const status = this.validateConnectFailList.includes(location.id) ? 'FAILED' : ''

                        const data = { ...location, mode: 'edit', icon, group, code, status }
                        if (
                            this.subprocess_info
                            && this.subprocess_info.details
                            && location.type === 'subflow'
                        ) {
                            this.subprocess_info.details.some(subflow => {
                                if (subflow.subprocess_node_id === location.id) {
                                    data.hasUpdated = subflow.expired
                                    return true
                                }
                            })
                        }
                        return data
                    }),
                    branchConditions
                }
            },
            subflowShouldUpdated () {
                if (this.subprocess_info) {
                    return this.subprocess_info.details.reduce((acc, cur) => {
                        const nodeId = cur.subprocess_node_id
                        if (!this.activities[nodeId]) {
                            return acc
                        }
                        const { scheme_id_list = [] } = this.activities[nodeId]
                        acc.push({
                            ...cur,
                            scheme_id_list
                        })
                        return acc
                    }, [])
                }
                return []
            },
            tplEditDialogTip () {
                let tip = this.$t('确定保存流程并去设置执行方案？')
                if (this.type === 'clone') {
                    tip = this.$t('确定保存克隆流程并去设置执行方案？')
                } else if (this.isBackViewMode || !this.isEditProcessPage) {
                    tip = this.$t('确定保存修改的内容？')
                }
                return tip
            },
            isViewMode () {
                return this.type === 'view'
            }
        },
        watch: {
            isNodeConfigPanelShow (val) {
                if (!val) {
                    this.atomTypeList.subflow.length = 0
                }
            },
            constants (val) {
                if (this.isPerspective) {
                    // 获取节点与变量的依赖关系
                    this.getNodeVariableCitedData()
                }
            },
            '$route.params.type' (val) {
                const data = this.getTplTabData()
                if (val === 'edit') {
                    tplTabCount.setTab(data, 'add')
                } else {
                    tplTabCount.setTab(data, 'del')
                }
            }
        },
        created () {
            this.initType = this.type
            this.initData()
        },
        mounted () {
            this.openSnapshootTimer()
            window.addEventListener('beforeunload', this.handleBeforeUnload, false)
            window.addEventListener('unload', this.handleUnload.bind(this), false)
            if (this.type === 'edit') {
                const data = this.getTplTabData()
                tplTabCount.setTab(data, 'add')
            }
        },
        beforeDestroy () {
            if (this.type === 'edit') {
                const data = this.getTplTabData()
                tplTabCount.setTab(data, 'del')
            }
            window.removeEventListener('beforeunload', this.handleBeforeUnload, false)
            window.removeEventListener('unload', this.handleUnload, false)
            this.resetTemplateData()
            this.hideGuideTips()
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'loadTemplateData',
                'saveTemplateData',
                'loadCustomVarCollection',
                'getLayoutedPipeline',
                'loadInternalVariable',
                'getVariableCite',
                'getProcessOpenChdProcess'
            ]),
            ...mapActions('task', [
                'loadSubflowConfig'
            ]),
            ...mapActions('atomForm/', [
                'loadSingleAtomList',
                'loadSubflowList',
                'loadAtomConfig',
                'loadPluginServiceMeta'
            ]),
            ...mapActions('project/', [
                'getProjectLabelsWithDefault',
                'loadEnvVariableList'
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
                'replaceTemplate',
                'replaceLineAndLocation',
                'setPipelineTree',
                'setInternalVariable',
                'setConstants'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            ...mapGetters('template/', [
                'getLocalTemplateData',
                'getPipelineTree'
            ]),
            ...mapActions('task/', [
                'loadTaskScheme',
                'saveTaskSchemList'
            ]),
            initData () {
                this.initTemplateData()
                // 获取流程内置变量
                this.getSystemVars()
                this.getSingleAtomList()
                this.getProjectBaseInfo()
                if (!this.common) {
                    this.getTemplateLabelList()
                }
                this.templateDataLoading = true
                this.snapshoots = this.getTplSnapshoots()
                if (['edit', 'clone', 'view'].includes(this.type)) {
                    this.getTemplateData()
                } else {
                    let name = 'new' + moment.tz(this.timeZone).format('YYYYMMDDHHmmss')
                    if (this.common) {
                        if (window.TIMEZONE) {
                            name = 'new' + moment.tz(window.TIMEZONE).format('YYYYMMDDHHmmss')
                        } else {
                            // 无时区的公共流程使用本地的时间
                            name = 'new' + moment().format('YYYYMMDDHHmmss')
                        }
                    }
                    this.setTemplateName(name)
                    this.templateDataLoading = false
                }
            },
            // 查询流程是否开启独立子流程
            async getProcessOpenChd (val) {
                const id = typeof val === 'number' ? val : val.id
                const res = await this.getProcessOpenChdProcess({
                    project_id: this.project_id,
                    id
                })
                this.formEnable = res.data.enable
            },
            /**
             * 加载标准插件列表
             */
            async getSingleAtomList (val) {
                this.singleAtomListLoading = true
                try {
                    const params = {}
                    if (!this.common) {
                        params.project_id = this.project_id
                    }
                    const data = await this.loadSingleAtomList(params)
                    // 内置插件
                    const atomList = []
                    data.forEach(item => {
                        const atom = atomList.find(atom => atom.code === item.code)
                        if (atom) {
                            atom.list.push(item)
                        } else {
                            const { code, desc, name, group_name, group_icon, sort_key_group_en } = item
                            atomList.push({
                                code,
                                desc,
                                name,
                                group_name,
                                group_icon,
                                type: group_name,
                                list: [item],
                                sort_key_group_en
                            })
                        }
                    })
                    this.atomList = this.handleAtomVersionOrder(atomList)
                    this.handleAtomGroup(tools.deepClone(this.atomList))
                    this.markNodesPhase()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.singleAtomListLoading = false
                }
            },
            async getProjectBaseInfo () {
                this.projectInfoLoading = true
                try {
                    const resp = await this.loadProjectBaseInfo()
                    this.setProjectBaseInfo(resp.data)
                    // this.getSubflowList()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectInfoLoading = false
                }
            },
            /**
             * 获取模板详情
             */
            async getTemplateData () {
                try {
                    const data = {
                        templateId: this.template_id,
                        common: this.common
                    }
                    const templateData = await this.loadTemplateData(data)
                    this.tplActions = templateData.auth_actions
                    if (this.type === 'clone') {
                        templateData.name = templateData.name.slice(0, STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH - 6) + '_clone'
                    }
                    // 登录成功后，使用最新的快照模板
                    if (localStorage.getItem('useSnapshot') && this.snapshoots.length) {
                        localStorage.removeItem('useSnapshot')
                        const data = this.snapshoots[0]
                        this.replaceTemplate(data.template)
                        this.$bkMessage({
                            'message': i18n.t('存在未保存内容，已自动载入'),
                            'theme': 'success'
                        })
                    } else {
                        this.setTemplateData(templateData)
                    }
                } catch (e) {
                    if (e.status === 404) {
                        this.$router.push({ name: 'notFoundPage' })
                    }
                    console.log(e)
                } finally {
                    this.templateDataLoading = false
                }
            },
            /**
             * 新增节点时取输入参数配置项
             * 优先取 store 里已保存的
             */
            async getSingleAtomConfig (location) {
                const code = location.atomId
                const version = location.version
                const atomConfig = this.atomConfig[code]
                const project_id = this.common ? undefined : this.project_id
                if (atomConfig && atomConfig[version]) {
                    this.addSingleAtomActivities(location, atomConfig[version])
                    return
                }
                // 接口获取最新配置信息
                this.atomConfigLoading = true
                try {
                    await this.loadAtomConfig({ atom: code, version, project_id })
                    const config = this.atomConfig[code] && this.atomConfig[code][version]
                    if (config) {
                        this.addSingleAtomActivities(location, config)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.atomConfigLoading = false
                }
            },
            /**
             * 加载子流程输入参数表单及配置项
             */
            async getSubflowConfig (location) { // get subflow constants and add node
                try {
                    const params = {
                        project_id: this.project_id,
                        template_id: location.atomId,
                        scheme_id_list: [],
                        version: ''
                    }
                    if (this.common || location.tplSource === 'common') {
                        params.template_source = 'common'
                    } else {
                        params.project_id = this.project_id
                    }
                    const res = await this.loadSubflowConfig(params)
                    const constants = tools.deepClone(res.data.pipeline_tree.constants)
                    const activity = tools.deepClone(this.activities[location.id])
                    const project_id = this.common ? undefined : this.project_id
                    for (const key in constants) {
                        const form = constants[key]
                        const { name, atom, tagCode, classify } = atomFilter.getVariableArgs(form)
                        // 全局变量版本
                        const version = form.version || 'legacy'
                        if (!atomFilter.isConfigExists(atom, version, this.atomConfig)) {
                            await this.loadAtomConfig({ name, atom, classify, version, project_id })
                        }
                        const atomConfig = this.atomConfig[atom][version]
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
                    activity.constants = constants || {}
                    this.setActivities({ type: 'edit', location: activity })
                } catch (e) {
                    console.log(e)
                }
            },
            /**
             * 加载系统内置变量
             */
            async getSystemVars () {
                try {
                    this.systemVarsLoading = true
                    const result = await this.loadInternalVariable()
                    const variableIndex = Object.keys(result.data).map(index => {
                        return result.data[index].index
                    })
                    let variableminIndex = Math.min(...variableIndex)
                    let internalVariable = { ...result.data }
                    if (!this.common) {
                        const resp = await this.loadEnvVariableList({ project_id: this.$route.params.project_id })
                        Object.keys(resp.data).forEach(item => {
                            const { name, value, desc } = resp.data[item]
                            const projectVar = {
                                key: '${_env_' + resp.data[item].key + '}',
                                name,
                                value,
                                desc,
                                index: --variableminIndex,
                                custom_type: 'input',
                                form_schema: {},
                                show_type: 'hide',
                                validation: '^.+$',
                                source_info: {},
                                source_type: 'project',
                                source_tag: 'input.input'
                            }
                            this.envVariableData['${_env_' + resp.data[item].key + '}'] = projectVar
                        })
                        internalVariable = Object.assign(this.envVariableData, result.data)
                    }
                    this.setInternalVariable(internalVariable)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.systemVarsLoading = false
                }
            },
            /**
             * 加载模板标签列表
             */
            async getTemplateLabelList () {
                try {
                    this.templateLabelLoading = true
                    const res = await this.getProjectLabelsWithDefault(this.project_id)
                    this.templateLabels = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLabelLoading = false
                }
            },
            checkDirtyData () {
                const ins = new DealVarDirtyData(this.constants)
                const illegalKeys = ins.checkKeys()
                if (illegalKeys.length) {
                    const h = this.$createElement
                    this.$bkInfo({
                        extCls: 'var-dirty-data-dialog',
                        width: 500,
                        okText: this.$t('清除'),
                        subHeader: h('p',
                                     { style: {} },
                                     [
                                         this.$t('自定义变量中存在系统变量/项目变量的key，需要清除后才能保存，是否一键清除？(可通过【模版数据-constants】进行确认)'),
                                         h('p',
                                           { style: { marginTop: '10px' } },
                                           [this.$t('问题变量有：'), illegalKeys.join(',')]
                                         )
                                     ]
                        ),
                        confirmFn: () => {
                            const constants = ins.handleIllegalKeys()
                            this.setConstants(constants)
                            this.saveTemplate()
                        }
                    })
                    return true
                }
                return false
            },
            /**
             * 保存流程模板
             */
            async saveTemplate () {
                // 检查全局变量是否存在脏数据
                const hasDirtyData = this.checkDirtyData()
                if (hasDirtyData) return

                const template_id = this.type === 'edit' ? this.template_id : undefined
                if (this.saveAndCreate) {
                    this.createTaskSaving = true
                } else {
                    this.templateSaving = true
                }

                try {
                    const resp = await this.saveTemplateData({ 'templateId': template_id, 'projectId': this.project_id, 'common': this.common })
                    if (!resp.result) return
                    const data = resp.data
                    this.tplActions = data.auth_actions
                    this.$bkMessage({
                        message: i18n.t('保存成功'),
                        theme: 'success'
                    })
                    this.isTemplateDataChanged = false
                    // 如果为克隆模式保存模板时需要保存执行方案
                    if (this.type === 'clone' && !this.common) {
                        // 当前为根据源模板id获取方案列表
                        this.taskSchemeList = await this.loadTaskScheme({
                            project_id: this.project_id,
                            template_id: this.template_id,
                            isCommon: this.common
                        }) || []
                        // 当前为根据已生成模板id保存方案列表
                        const schemes = this.taskSchemeList.map(item => {
                            return {
                                data: item.data,
                                name: item.name
                            }
                        })
                        await this.saveTaskSchemList({
                            project_id: this.project_id,
                            template_id: data.template_id,
                            schemes,
                            isCommon: this.common
                        })
                    }

                    if (this.type !== 'edit') {
                        this.saveTempSnapshoot(data.template_id)
                        this.allowLeave = true

                        // 新创建的流程模板需要增加本地浏览器计数信息
                        const tabQuerydata = {
                            user: this.username,
                            id: this.common ? 'common' : this.project_id,
                            tpl: data.template_id
                        }
                        tplTabCount.setTab(tabQuerydata, 'add')
                    }

                    if (this.createTaskSaving) {
                        this.goToTaskUrl(data.template_id)
                    } else { // 保存后需要切到查看模式(查看执行方案时不需要)
                        if (this.isExecuteScheme) return
                        if (this.initType === 'view') {
                            this.$router.back()
                            this.initData()
                        } else {
                            this.$router.push({
                                params: { type: 'view' },
                                query: { template_id: data.template_id }
                            })
                            this.isRouterPush = true
                            this.initType = 'view'
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.saveAndCreate = false
                    this.pid = undefined
                    this.templateSaving = false
                    this.createTaskSaving = false
                }
            },
            /**
             * 更新普通任务节点配置详情
             * @param {Object} location 节点对象
             * @param {Array} config 节点输入参数配置项
             */
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
            /**
             * 插件列表按照版本号递增排序，legacy 置为最前
             */
            handleAtomVersionOrder (atomList) {
                return atomList.map(atom => {
                    const index = atom.list.findIndex(item => item.version === 'legacy')
                    const list = atom.list.slice(0)
                    const legacyList = []
                    if (index > -1) {
                        legacyList.push(list[index])
                        list.splice(index, 1)
                    }
                    if (list.length > 1) {
                        list.sort((a, b) => a.version.localeCompare(b.version))
                    }
                    return {
                        ...atom,
                        list: legacyList.concat(list)
                    }
                })
            },
            /**
             * 标准插件分组
             */
            handleAtomGroup (data) {
                const grouped = []
                data.forEach(item => {
                    const group = grouped.find(atom => atom.type === item.type)
                    if (group) {
                        group.list.push(item)
                    } else {
                        const { type, group_name, group_icon, sort_key_group_en } = item
                        grouped.push({
                            group_name,
                            group_icon,
                            type,
                            sort_key_group_en,
                            list: [item]
                        })
                    }
                })
                grouped.sort((g1, g2) => {
                    if (g1.sort_key_group_en < g2.sort_key_group_en) {
                        return -1
                    }
                    if (g1.sort_key_group_en > g2.sort_key_group_en) {
                        return 1
                    }
                    return 0
                })
                this.atomTypeList.tasknode = grouped
            },
            // 获取节点与变量的依赖关系
            async getNodeVariableCitedData () {
                try {
                    const constants = { ...this.internalVariable, ...this.constants }
                    const data = {
                        activities: this.activities,
                        gateways: this.gateways,
                        constants
                    }
                    const resp = await this.getVariableCite(data)
                    if (!resp.result) return
                    const variableCited = resp.data.defined
                    const nodeCitedInfo = Object.keys(variableCited).reduce((acc, key) => {
                        const values = variableCited[key]
                        const nodeInfo = constants[key]
                        if (nodeInfo.source_type === 'component_outputs') {
                            const outputIds = Object.keys(nodeInfo.source_info) || []
                            outputIds.forEach(nodeId => {
                                if (!(nodeId in acc)) {
                                    acc[nodeId] = {
                                        'input': [],
                                        'output': []
                                    }
                                }
                                acc[nodeId]['output'].push(key)
                            })
                        } else {
                            values.activities.forEach(nodeId => {
                                if (!(nodeId in acc)) {
                                    acc[nodeId] = {
                                        'input': [],
                                        'output': []
                                    }
                                }
                                acc[nodeId]['input'].push(key)
                            })
                        }
                        return acc
                    }, {})
                    // 去重
                    Object.keys(nodeCitedInfo).forEach(key => {
                        const values = nodeCitedInfo[key]
                        values.input = [...new Set(values.input)]
                        values.output = [...new Set(values.output)]
                    })
                    this.nodeVariableInfo = nodeCitedInfo
                } catch (e) {
                    console.log(e)
                }
            },
            /**
            /**
             * 打开节点配置面板
             * @param {String} id 节点uuid
             */
            showConfigPanel (id) {
                this.isNodeConfigPanelShow = true
                this.idOfNodeInConfigPanel = id
            },
            /**
             * 关闭节点配置面板
             */
            closeConfigPanel (openVariablePanel) {
                this.isNodeConfigPanelShow = false
                this.idOfNodeInConfigPanel = ''
                this.backToVariablePanel = false
                if (openVariablePanel) {
                    this.onChangeSettingPanel('globalVariableTab')
                }
            },
            /**
             * 设置流程模板为修改状态
             */
            templateDataChanged () {
                this.isTemplateDataChanged = true
            },
            /**
             * 任务节点校验
             * 校验项包含：标准插件类型，节点名称，输入参数
             * @return isAllValid {Boolean} 节点是否合法
             */
            validateAtomNode () {
                let isAllValid = true
                this.typeOfNodeNameEmpty = ''
                Object.keys(this.activities).forEach(id => {
                    let isNodeValid = true
                    const node = this.activities[id]
                    if (node.type === 'ServiceActivity') {
                        if (!node.name) { // 节点名称为空
                            isNodeValid = false
                            this.typeOfNodeNameEmpty = 'serviceActivity'
                        }
                        if (node.component.code) {
                            if (!this.validateAtomInputForm(node.component)) {
                                isNodeValid = false // 输入参数校验不通过
                            }
                        } else {
                            isNodeValid = false // 节点标准插件类型为空
                        }
                    } else { // @todo 子流程节点只校验名称和模板id，输入参数未校验
                        if (!node.name || node.template_id === undefined) {
                            isNodeValid = false
                            this.typeOfNodeNameEmpty = 'subProcess'
                        }
                    }
                    if (!isNodeValid) {
                        isAllValid = false
                        this.markInvalidNode(id)
                    }
                })
                if (!isAllValid) {
                    let message = i18n.t('任务节点参数错误，请点击错误节点查看详情')
                    if (this.typeOfNodeNameEmpty) {
                        message = this.typeOfNodeNameEmpty === 'serviceActivity' ? i18n.t('请选择节点的插件类型') : i18n.t('请选择节点的子流程')
                    }
                    this.$bkMessage({
                        message,
                        theme: 'error'
                    })
                }
                return isAllValid
            },
            /**
             * 校验输入参数是否满足标准插件配置文件正则校验
             * @param {Object} component 普通任务节点 component 字段
             */
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
            /**
             * 校验节点输入参数
             * @param {Array} config 标准插件配置项
             * @param {Object} formData 输入参数表单值
             */
            checkAtomData (config, formData) {
                let isValid = true
                const formObj = {
                    // tag 组件的内置方法，未渲染 vue 组件时，在外层提供
                    get_tag_value: function (path, data = formData) {
                        const tag = path[0]
                        if (!(tag in data)) {
                            throw new Error(`表单值中不存在 ${tag} 属性`)
                        }
                        if (path.length === 1) {
                            return tools.deepClone(data[tag])
                        } else {
                            return this.get_tag_value(path.slice(1), data[tag])
                        }
                    }
                }
                config.forEach(item => {
                    const { tag_code, type, attrs } = item
                    const value = formData[tag_code]
                    if (type === 'combine') {
                        if (typeof value === 'object' && !this.checkAtomData(attrs.children, value)) { // 勾选为全局变量的 combine 不校验 value
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
                                        const validateInfo = item.args.call(formObj, value, formData)
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
             * 标记任务节点的生命周期
             */
            markNodesPhase () {
                Object.keys(this.canvasData.activities).forEach(id => {
                    const node = this.canvasData.activities[id]
                    if (node.type === 'ServiceActivity') {
                        let atom = ''
                        this.atomList.some(group => {
                            if (group.code === node.component.code) {
                                return group.list.some(item => {
                                    if (item.version === (node.component.version || 'legacy')) {
                                        atom = item
                                    }
                                })
                            }
                        })
                        if (atom && [1, 2].includes(atom.phase)) {
                            this.onUpdateNodeInfo(node.id, { phase: atom.phase })
                        }
                    }
                })
            },
            /**
             * 打开节点配置面板
             */
            async onShowNodeConfig (id) {
                // 判断节点配置的插件是否存在
                const nodeConfig = this.$store.state.template.activities[id]
                if (nodeConfig.type === 'SubProcess') {
                    this.formEnable = nodeConfig.enable
                }
                if (nodeConfig.type === 'ServiceActivity' && nodeConfig.name) {
                    let atom = true
                    if (nodeConfig.component.code !== 'remote_plugin') {
                        atom = this.atomList.find(item => item.code === nodeConfig.component.code)
                    }
                    if (!atom) {
                        this.$bkMessage({
                            message: '该节点配置的插件不存在，请检查流程数据',
                            theme: 'error'
                        })
                        return
                    }
                }
                const location = this.locations.find(item => item.id === id)
                if (['tasknode', 'subflow'].includes(location.type)) {
                    // 设置第三发插件缓存
                    const nodeConfig = this.$store.state.template.activities[id]
                    if (nodeConfig.component
                        && nodeConfig.component.code === 'remote_plugin'
                        && !this.thirdPartyList[id]) {
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
                        this.thirdPartyList[id] = group
                    }
                    this.showConfigPanel(id)
                }
            },
            // 流程透视
            onTogglePerspective (val) {
                this.isPerspective = val
                if (val) {
                    // 获取节点与变量的依赖关系
                    this.getNodeVariableCitedData()
                }
            },
            /**
             * 自动排版
             */
            async onFormatPosition () {
                window.reportInfo({
                    page: 'templateEdit',
                    zone: 'formatPositionIcon',
                    event: 'click'
                })
                const validateMessage = validatePipeline.isNodeLineNumValid(this.canvasData)
                if (!validateMessage.result) {
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'error',
                        ellipsisLine: 0
                    })
                    return
                }
                if (this.canvasDataLoading) {
                    return
                }
                this.canvasDataLoading = true // @todo 支持画布单独loading
                try {
                    const { ACTIVITY_SIZE, EVENT_SIZE, GATEWAY_SIZE, START_POSITION } = NODES_SIZE_POSITION
                    const pipelineTree = this.getPipelineTree()
                    const canvasEl = document.getElementsByClassName('canvas-flow-wrap')[0]
                    const width = canvasEl.offsetWidth - 200
                    const res = await this.getLayoutedPipeline({
                        canvas_width: width,
                        pipeline_tree: pipelineTree,
                        activity_size: ACTIVITY_SIZE,
                        event_size: EVENT_SIZE,
                        gateway_size: GATEWAY_SIZE,
                        start: START_POSITION
                    })
                    if (res.result) {
                        this.onCreateSnapshoot('isFormatPosition')
                        this.$refs.templateCanvas.removeAllConnector()
                        this.setPipelineTree(res.data.pipeline_tree)
                        this.$nextTick(() => {
                            this.$refs.templateCanvas.updateCanvas()
                            this.$refs.templateCanvas.onResetPosition()
                            this.templateDataChanged()
                            this.$bkMessage({
                                message: i18n.t('排版完成，原内容在本地快照中'),
                                theme: 'success'
                            })
                        })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.canvasDataLoading = false
                }
            },
            /**
             * 节点变更(添加、删除、编辑)
             * @param {String} changeType 变更类型,添加、删除、编辑
             * @param {Object} location 节点 location 字段
             */
            async onLocationChange (changeType, location) {
                this.setLocation({ type: changeType, location })
                switch (location.type) {
                    case 'tasknode':
                    case 'subflow':
                        // 添加任务节点
                        if (changeType === 'add' && location.atomId) {
                            if (location.type === 'tasknode') {
                                if (location.atomId === 'remote_plugin') {
                                    const resp = await this.loadPluginServiceMeta({ plugin_code: location.name })
                                    if (!resp.result) return
                                    const versionList = resp.data.versions
                                    location.version = versionList[versionList.length - 1]
                                    location.data = {
                                        plugin_code: {
                                            hook: false,
                                            value: location.name
                                        },
                                        plugin_version: {
                                            hook: false,
                                            value: location.version
                                        }
                                    }
                                } else {
                                    const atoms = this.atomList.find(item => item.code === location.atomId).list
                                    // @todo 需要确认插件最新版本的取值逻辑，暂时取最后一个
                                    const lastVersionAtom = atoms[atoms.length - 1]
                                    const version = lastVersionAtom.version
                                    location.version = version
                                }
                                this.setActivities({ type: 'add', location })
                                this.getSingleAtomConfig(location)
                            } else {
                                this.setActivities({ type: 'add', location })
                                this.getSubflowConfig(location)
                            }
                            return
                        }
                        this.setActivities({ type: changeType, location })
                        break
                    case 'branchgateway':
                    case 'parallelgateway':
                    case 'convergegateway':
                    case 'conditionalparallelgateway':
                        this.setGateways({ type: changeType, location })
                        break
                    case 'startpoint':
                        this.setStartpoint({ type: changeType, location })
                        break
                    case 'endpoint':
                        this.setEndpoint({ type: changeType, location })
                        break
                }
                // 删除节点时，清除对应的校验失败节点
                if (changeType === 'delete' && this.validateConnectFailList.length) {
                    const index = this.validateConnectFailList.findIndex(val => val === location.id)
                    if (index > -1) {
                        this.validateConnectFailList.splice(index, 1)
                    }
                }
            },
            /**
             * 连线变更(新增、删除)
             * @param {String} changeType 变更类型，新增、删除
             * @param {Object} line 连线对象
             */
            onLineChange (changeType, line) {
                this.setLine({ type: changeType, line })
                // 对校验失败节点进行处理
                if (changeType === 'add' && this.validateConnectFailList.length) {
                    const idList = [line.target.id, line.source.id]
                    const nodeList = this.validateConnectFailList.filter(val => idList.includes(val))
                    if (!nodeList || !nodeList.length) return
                    nodeList.forEach(node => {
                        const nodeInfo = this.activities[node] || this.gateways[node]
                        const outgoing = Array.isArray(nodeInfo.outgoing) ? nodeInfo.outgoing.length : nodeInfo.outgoing
                        if (nodeInfo.incoming.length && outgoing) {
                            const index = this.validateConnectFailList.findIndex(val => val === node)
                            this.validateConnectFailList.splice(index, 1)
                        }
                    })
                }
            },
            /**
             * 节点位置移动
             */
            onLocationMoveDone (location) {
                this.setLocationXY(location)
            },
            /**
             * 全局变量是否有更新，面板收起的情况下增加、删除变量时在 icon 处显示小红点
             */
            globalVariableUpdate (val) {
                this.isGlobalVariableUpdate = val
            },
            /**
             * 更新单个节点的信息
             */
            onUpdateNodeInfo (id, data) {
                const location = this.canvasData.locations.find(item => item.id === id)
                const updatedLocation = Object.assign(location, data)
                this.setLocation({ type: 'edit', location: updatedLocation })
                this.$refs.templateCanvas.onUpdateNodeInfo(id, data)
            },
            onDownloadCanvas () {
                this.$refs.templateCanvas.onDownloadCanvas()
            },
            async onSaveExecuteSchemeClick (isDefault) {
                try {
                    this.executeSchemeSaving = true
                    const schemes = this.taskSchemeList.map(item => {
                        return {
                            id: item.id || undefined,
                            data: item.data,
                            name: item.name
                        }
                    })
                    const resp = await this.saveTaskSchemList({
                        project_id: this.project_id,
                        template_id: this.template_id,
                        schemes,
                        isCommon: this.common
                    })
                    if (!resp.result) return
                    this.$bkMessage({
                        message: i18n.t('方案保存成功'),
                        theme: 'success'
                    })
                    this.isExecuteSchemeDialog = false
                    this.allowLeave = true
                    this.isTemplateDataChanged = false
                    this.isSchemaListChange = false
                    this.isEditProcessPage = !isDefault
                    if (isDefault) {
                        this.$refs.taskSelectNode.loadSchemeList()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.executeSchemeSaving = false
                }
            },
            goBackViewMode () {
                this.isBackViewMode = true
                this.$bkInfo({
                    ...this.infoBasicConfig,
                    cancelFn: () => {
                        // 返回查看模式时初始化数据
                        this.isTemplateDataChanged = false
                        this.isGlobalVariableUpdate = false
                        this.$router.back()
                        this.initData()
                    }
                })
            },
            goBackToTplEdit () {
                const { isDefaultSchemeIng, judgeDataEqual } = this.$refs.taskSelectNode
                const isEqual = isDefaultSchemeIng ? judgeDataEqual() : !this.isSchemaListChange
                if (isEqual) {
                    this.isEditProcessPage = true
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        cancelFn: () => {
                            this.isEditProcessPage = true
                            this.isTemplateDataChanged = false
                        }
                    })
                }
            },
            updateTaskSchemeList (val, isChange) {
                this.taskSchemeList = val
                this.allowLeave = false
                this.isTemplateDataChanged = isChange
                this.isSchemaListChange = isChange
            },
            onClosePreview () {
                this.$refs.taskSelectNode.togglePreviewMode(false)
            },
            onOpenExecuteScheme (val) {
                this.isExecuteScheme = val
            },
            // 选择侧滑面板
            onChangeSettingPanel (val) {
                this.activeSettingTab = val
                if (this.isGlobalVariableUpdate && val === 'globalVariableTab') {
                    this.isGlobalVariableUpdate = false
                }
            },
            // 跳转到节点选择页面
            goToTaskUrl (template_id) {
                this.$router.push({
                    name: 'taskCreate',
                    params: { step: 'selectnode', project_id: this.pid },
                    query: {
                        template_id,
                        common: this.common,
                        entrance: 'templateEdit'
                    }
                })
            },
            // 点击保存模板按钮回调
            onSaveTemplate (saveAndCreate, pid) {
                if (this.templateSaving || this.createTaskSaving) {
                    return
                }
                this.saveAndCreate = saveAndCreate
                this.pid = pid
                this.isMultipleTabCount = tplTabCount.getCount(this.getTplTabData())
                if (this.type === 'edit' && this.isMultipleTabCount > 1) {
                    if (!this.isExecuteScheme) {
                        this.multipleTabDialogShow = true
                    } else {
                        this.isExecuteSchemeDialog = true
                    }
                } else {
                    this.checkNodeAndSaveTemplate()
                }
            },
            // 校验节点配置
            checkNodeAndSaveTemplate () {
                // 校验节点数目
                const validateMessage = validatePipeline.isNodeLineNumValid(this.canvasData)
                if (!validateMessage.result) {
                    // 获取检验不合格节点
                    const validateConnectFailList = []
                    const nodeObject = Object.assign({}, this.activities, this.gateways)
                    Object.values(nodeObject).forEach(node => {
                        const outgoing = Array.isArray(node.outgoing) ? node.outgoing.length : node.outgoing
                        if (!node.incoming.length || !outgoing) {
                            validateConnectFailList.push(node.id)
                        }
                    })
                    this.validateConnectFailList = validateConnectFailList
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'error',
                        ellipsisLine: 2
                    })
                    return
                }
                // 节点配置是否错误
                const nodeWithErrors = document.querySelectorAll('.canvas-node-item .failed')
                if (nodeWithErrors && nodeWithErrors.length) {
                    this.templateSaving = false
                    this.createTaskSaving = false
                    let message = i18n.t('任务节点参数错误，请点击错误节点查看详情')
                    if (this.typeOfNodeNameEmpty) {
                        message = this.typeOfNodeNameEmpty === 'serviceActivity' ? i18n.t('请选择节点的插件类型') : i18n.t('请选择节点的子流程')
                    }
                    this.$bkMessage({
                        message,
                        theme: 'error',
                        ellipsisLine: 2
                    })
                    return
                }
                const isAllNodeValid = this.validateAtomNode()
                if (isAllNodeValid) {
                    if (this.common && this.saveAndCreate && this.pid === undefined) { // 公共流程保存并创建任务，没有选择项目
                        this.$refs.templateHeader.setProjectSelectDialogShow()
                    } else {
                        if (this.isExecuteScheme) {
                            if (this.type === 'clone' || this.isTemplateDataChanged) {
                                this.isExecuteSchemeDialog = true
                            } else {
                                this.isEditProcessPage = false
                            }
                        } else {
                            this.saveTemplate()
                        }
                    }
                }
            },
            // 修改line和location
            onReplaceLineAndLocation (data) {
                this.replaceLineAndLocation(data)
            },
            // 重新获得缓存后，更新 dom data[raw]上绑定的数据
            updateAllNodeInfo () {
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
            closeBatchUpdateDialog (updated) {
                this.isBatchUpdateDialogShow = false
                if (updated) {
                    this.templateDataChanged()
                }
            },
            // 打开分支条件编辑
            onOpenConditionEdit (data) {
                this.isShowConditionEdit = true
                this.conditionData = { ...data }
            },
            // 分支条件侧滑点击遮罩事件
            onBeforeClose () {
                this.$bkInfo({
                    ...this.infoBasicConfig,
                    cancelFn: () => {
                        this.isShowConditionEdit = false
                    }
                })
            },
            onCloseConfigPanel (openVariablePanel) {
                this.isShowConditionEdit = false
                this.backToVariablePanel = false
                if (openVariablePanel) {
                    this.onChangeSettingPanel('globalVariableTab')
                }
            },
            // 更新分支数据
            updataCanvasCondition (data) {
                // 更新 cavans 页面数据
                this.$refs.templateCanvas.updataConditionCanvasData(data)
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
            },
            // 查看需要更新的子流程
            viewUpdatedNode (id) {
                this.moveNodeToView(id)
                this.showDotAnimation(id)
            },
            // 全局变量引用详情点击回调
            onCitedNodeClick (data) {
                const { group, id } = data
                this.backToVariablePanel = true
                if (group === 'activities') {
                    this.activeSettingTab = ''
                    this.showConfigPanel(id)
                } else if (group === 'conditions') {
                    const nodeId = this.lines.find(line => line.id === id).source.id
                    const lineCondition = this.gateways[nodeId].conditions[id]
                    const { evaluate, name } = lineCondition
                    const conditionData = {
                        id,
                        name,
                        nodeId,
                        overlayId: `condition${id}`,
                        value: evaluate
                    }
                    this.activeSettingTab = ''
                    this.onOpenConditionEdit(conditionData)
                }
            },
            /**
             * 移动画布，将节点放到画布左上角
             */
            moveNodeToView (id) {
                const { x, y } = this.locations.find(item => item.id === id)
                const offsetX = 200 - x
                const offsetY = 200 - y
                this.$refs.templateCanvas.setCanvasPosition(offsetX, offsetY, true)

                // 移动画布到选中节点位置的摇晃效果
                const nodeEl = document.querySelector(`#${id} .canvas-node-item`)
                if (nodeEl) {
                    nodeEl.classList.add('node-shake')
                    setTimeout(() => {
                        nodeEl.classList.remove('node-shake')
                    }, 500)
                }
            },
            // 开启子流程更新的小红点动画效果
            showDotAnimation (id) {
                this.clearDotAnimation()
                if (!Array.isArray(id)) {
                    id = [id]
                }
                id.forEach(item => {
                    const nodeDot = document.querySelector(`#${item} .updated-dot`)
                    if (nodeDot) {
                        nodeDot.classList.add('show-animation')
                    }
                })
            },
            // 关闭所有子流程更新的小红点动画效果
            clearDotAnimation () {
                const updateNodesDot = document.querySelectorAll('.subflow-node .updated-dot')
                updateNodesDot.forEach(item => {
                    item.classList.remove('show-animation')
                })
            },
            // 本地快照面板新增快照
            onCreateSnapshoot (type) {
                this.snapshootTimer && clearTimeout(this.snapshootTimer)
                this.setTplSnapshoot()
                if (!type) {
                    this.$bkMessage({
                        message: i18n.t('新增流程本地快照成功'),
                        theme: 'success'
                    })
                }
                this.snapshoots = this.getTplSnapshoots()
                this.openSnapshootTimer()
            },
            // 使用快照还原流程模板
            onUseSnapshoot (args) {
                const [template, index] = args
                const name = i18n.t('最近快照已保存，并恢复至原序号为') + index + i18n.t('的快照')
                this.setTplSnapshoot(name)
                this.replaceTemplate(template)
                this.templateDataLoading = true
                // this.hideConfigPanel()
                this.$nextTick(() => {
                    this.templateDataLoading = false
                    this.snapshoots = this.getTplSnapshoots()
                    this.$bkMessage({
                        'message': i18n.t('替换流程成功'),
                        'theme': 'success'
                    })
                    // 更新画布节点状态，需要画布数据更新到 DOM 后再执行
                    this.$nextTick(() => {
                        this.updateAllNodeInfo()
                    })
                })
            },
            // 更新快照名称
            onUpdateSnapshoot (data) {
                const id = this.common ? 'common' : this.project_id
                const tpl = this.type === 'edit' ? this.template_id : this.tplUUID
                tplSnapshoot.update(this.username, id, tpl, data)
                this.snapshoots = this.getTplSnapshoots()
            },
            // 设置快照定时器
            openSnapshootTimer () {
                this.snapshootTimer && clearTimeout(this.snapshootTimer)
                this.snapshootTimer = setTimeout(() => {
                    this.setTplSnapshoot()
                    this.snapshoots = this.getTplSnapshoots()
                    this.openSnapshootTimer()
                }, 5 * 60 * 1000)
            },
            // 添加快照
            setTplSnapshoot (name = i18n.t('自动保存')) {
                const id = this.common ? 'common' : this.project_id
                const tpl = this.type === 'edit' ? this.template_id : this.tplUUID
                const data = {
                    name,
                    timestamp: new Date().getTime(),
                    template: this.getLocalTemplateData()
                }
                tplSnapshoot.create(this.username, id, tpl, data)
            },
            // 获取快照列表
            getTplSnapshoots () {
                const id = this.common ? 'common' : this.project_id
                const tpl = this.type === 'edit' ? this.template_id : this.tplUUID
                return tplSnapshoot.getTplSnapshoots(this.username, id, tpl).slice().reverse()
            },
            // 清除临时快照
            clearTempSnapshoot () {
                const id = this.common ? 'common' : this.project_id
                tplSnapshoot.deleteTplSnapshoots(this.username, id, this.tplUUID)
            },
            // 保存临时快照为改流程模板快照
            saveTempSnapshoot (templateId) {
                const id = this.common ? 'common' : this.project_id
                tplSnapshoot.replaceSnapshootTplKey(this.username, id, this.tplUUID, templateId)
            },
            handleBeforeUnload (e) {
                e.returnValue = i18n.t('系统不会保存您所做的更改，确认离开？')
                return i18n.t('系统不会保存您所做的更改，确认离开？')
            },
            handleUnload (queryData, type) {
                if (this.type === 'edit') {
                    const data = this.getTplTabData()
                    tplTabCount.setTab(data, 'del')
                }
            },
            // 多 tab 打开同一流程模板
            onMultipleTabConfirm () {
                this.checkNodeAndSaveTemplate()
                this.multipleTabDialogShow = false
            },
            getTplTabData () {
                return {
                    user: this.username,
                    id: this.common ? 'common' : this.project_id,
                    tpl: this.template_id
                }
            },
            togglePreviewMode (isPreview) {
                this.isPreviewMode = isPreview
            },
            setExcludeNode (val) {
                this.excludeNode = val
            },
            // 编辑执行方案弹框 确定事件
            async onConfirmSave () {
                if (this.isEditProcessPage) {
                    await this.saveTemplate()
                    this.isExecuteSchemeDialog = false
                    this.isEditProcessPage = false
                    this.isTemplateDataChanged = false
                }
            },
            // 编辑执行方案弹框 取消事件
            onCancelSave () {
                this.isExecuteSchemeDialog = false
                this.isExecuteScheme = false
            }
        },
        beforeRouteLeave (to, from, next) { // leave or reload page
            if (this.allowLeave || !this.isTemplateDataChanged) {
                this.clearAtomForm()
                // 清除快照定时器
                this.snapshootTimer && clearTimeout(this.snapshootTimer)
                // 流程模板为克隆和新建状态且为保存时，退出需要清除快照
                this.type !== 'edit' && this.clearTempSnapshoot()
                next()
            } else {
                this.leaveToPath = to.fullPath
                this.$bkInfo({
                    ...this.infoBasicConfig,
                    cancelFn: () => {
                        this.allowLeave = true
                        this.$router.push({ path: this.leaveToPath })
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .template-page {
        position: relative;
        height: 100%;
        overflow: hidden;
    }
    .tpl-view-model {
        /deep/ .jsflow .tool-panel-wrap {
            left: 40px;
        }
        /deep/ .small-map {
            left: 40px;
        }
    }
    .update-tips {
        position: absolute;
        top: 64px;
        left: 450px;
        min-height: 40px;
        overflow: hidden;
        z-index: 4;
        transition: left 0.5s ease;
    }
    .pipeline-canvas-wrapper {
        height: 100%;
    }
    .template-canvas {
        position: relative;
        height: calc(100vh - 100px);
    }
    .side-content {
        position: absolute;
        top: 59px;
        right: 0px;
        height: calc(100% - 58px);
    }
    .leave-tips {
        padding: 30px;
    }
    /deep/ .multiple-tab-dialog-content {
        padding: 40px 0;
        text-align: center;
        h3 {
            margin: 0;
            font-size: 24px;
            font-weight: normal;
        }
        p {
            margin: 6px 0 20px;
            font-size: 14px;
            color: #ff9c01;
        }
        .action-wrapper .bk-button {
            margin-right: 6px;
        }
    }
</style>
<style lang="scss">
    .template-edit-dialog {
        .bk-dialog-body {
            padding: 0;
        }
        .template-edit-dialog-content {
            padding: 20px 0 40px 0;
            text-align: center;
            .save-tpl-tips {
                font-size: 24px;
                margin-bottom: 20px;
                padding: 0 10px;
            }
            .multiple-tab-dialog-tip {
                margin-bottom: 10px;
                font-size: 14px;
                color: #ff9c01;
            }
            .action-wrapper .bk-button {
                margin: 10px 6px 0 0;
            }
        }
    }
    .var-dirty-data-dialog {
        .bk-dialog-sub-header {
            font-size: 14px;
            line-height: 1.5;
            padding: 5px 25px 15px;
            color: #63656e;
        }
        .bk-info-box .bk-dialog-footer {
            text-align: right;
            padding: 0 25px 15px;
        }
    }

</style>
