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
    <div
        :class="[
            'template-page',
            isViewMode ? 'tpl-view-model' : 'tpl-edit-model'
        ]"
        v-bkloading="{ isLoading: templateDataLoading || singleAtomListLoading , zIndex: 100 }">
        <div v-if="!templateDataLoading" class="pipeline-canvas-wrapper">
            <TemplateHeader
                ref="templateHeader"
                :name="name"
                :project_id="project_id"
                :type="type"
                :common="common"
                :template_id="template_id"
                :is-template-data-changed="isTemplateDataChanged"
                :template-saving="templateSaving"
                :tpl-actions="tplActions"
                :draft-update-info="draftUpdateInfo"
                :is-exec-schema-view="activeSettingTab === 'executeSchemaTab'"
                :is-exec-schema-preview="isExecSchemaPreview"
                :collect-info="collectInfo"
                :published="published"
                @templateDataChanged="templateDataChanged"
                @onClosePreview="onClosePreview"
                @goBackViewMode="goBackViewMode"
                @onChangePanel="activeSettingTab = $event"
                @onPublishDraft="onPublishDraft">
            </TemplateHeader>
            <!--执行方案-->
            <TaskSelectNode
                v-if="activeSettingTab === 'executeSchemaTab'"
                ref="taskSelectNode"
                :project_id="project_id"
                :common="common"
                :entrance="entrance"
                :template_id="template_id"
                :is-create-task="false"
                @togglePreviewMode="isExecSchemaPreview = $event">
            </TaskSelectNode>
            <!--模板-->
            <template v-else>
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
                    :name="name"
                    :show-palette="!isViewMode"
                    :editable="!isViewMode"
                    :common="common"
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
                <TemplateSidebar
                    :is-view-mode="isViewMode"
                    :is-node-config-panel-show="isNodeConfigPanelShow"
                    :atom-list="atomList"
                    :atom-type-list="atomTypeList"
                    :common="common"
                    :project_id="project_id"
                    :node-id="idOfNodeInConfigPanel"
                    @onCitedNodeClick="onCitedNodeClick"
                    @updateNodeInfo="onUpdateNodeInfo"
                    @close="closeConfigPanel">
                </TemplateSidebar>
            </template>
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
                v-if="activeSettingTab"
                :is-view-mode="isViewMode"
                :active-tab.sync="activeSettingTab"
                :common="common"
                @templateDataChanged="templateDataChanged"
                @modifyTemplateData="modifyTemplateData">
            </template-setting>
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
    import validatePipeline from '@/utils/validatePipeline.js'
    import TemplateHeader from './TemplateHeader/index.vue'
    import TemplateSidebar from './TemplateSidebar/index.vue'
    import TemplateCanvas from '@/components/common/TemplateCanvas/index.vue'
    import TemplateSetting from './TemplateSetting/index.vue'
    import ConditionEdit from './ConditionEdit.vue'
    import SubflowUpdateTips from './SubflowUpdateTips.vue'
    import Guide from '@/utils/guide.js'
    import permission from '@/mixins/permission.js'
    import { STRING_LENGTH } from '@/constants/index.js'
    import { NODES_SIZE_POSITION } from '@/constants/nodes.js'
    import TaskSelectNode from '../../task/TaskCreate/TaskSelectNode.vue'
    import BatchUpdateDialog from './BatchUpdateDialog.vue'
    import DealVarDirtyData from '@/utils/dealVarDirtyData.js'
    import bus from '@/utils/bus.js'

    export default {
        inject: ['reload'],
        name: 'TemplateEdit',
        components: {
            TemplateHeader,
            TemplateSidebar,
            TemplateCanvas,
            TaskSelectNode,
            ConditionEdit,
            TemplateSetting,
            SubflowUpdateTips,
            BatchUpdateDialog
        },
        mixins: [permission],
        props: ['template_id', 'type', 'common', 'entrance'],
        data () {
            return {
                isExecSchemaPreview: false,
                singleAtomListLoading: false,
                projectInfoLoading: false,
                templateDataLoading: false,
                templateSaving: false,
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
                collectInfo: {},
                published: false,
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
                isParallelGwErrorMsg: '', // 缺少汇聚网关的报错信息
                checkedNodes: [],
                checkedConvergeNodes: [],
                draftUpdateInfo: {}
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
                'start_event': state => state.template.start_event,
                'end_event': state => state.template.end_event,
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
                        branchConditions[item.id][nodeId] = {
                            ...item.default_condition,
                            default_condition: true
                        }
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
                        this.validateConnectFailList = [...new Set(this.validateConnectFailList)]
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
            isViewMode () {
                return this.type === 'view'
            },
            nodeTargetMaps () {
                return this.lines.reduce((acc, cur) => {
                    const { source, target } = cur
                    if (acc[source.id]) {
                        acc[source.id].push(target.id)
                    } else {
                        acc[source.id] = [target.id]
                    }
                    return acc
                }, {})
            },
            convergeGwNodes () {
                return Object.values(this.gateways).reduce((acc, cur) => {
                    if (cur.type === 'ConvergeGateway') {
                        acc.push(cur.id)
                    }
                    return acc
                }, [])
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
            async '$route.params.type' (val, oldVal) {
                this.templateDataLoading = true
                this.isTemplateDataChanged = false
                if (val === 'edit' && ['new', 'clone'].includes(oldVal)) {
                    await this.getTemplateData()
                }
                if (val === 'edit') {
                    this.getTplDraftData()
                } else {
                    this.getTemplateData()
                }
            }
        },
        created () {
            this.initType = this.type
            this.initData()
        },
        mounted () {
            window.addEventListener('beforeunload', this.handleBeforeUnload, false)
        },
        beforeDestroy () {
            window.removeEventListener('beforeunload', this.handleBeforeUnload, false)
            this.resetTemplateData()
            this.hideGuideTips()
        },
        methods: {
            ...mapActions('template/', [
                'loadProjectBaseInfo',
                'loadTemplateData',
                'loadTemplateDraft',
                'publishTemplateDraft',
                'loadCustomVarCollection',
                'getLayoutedPipeline',
                'loadInternalVariable',
                'getVariableCite',
                'getProcessOpenRetryAndTimeout'
            ]),
            ...mapActions('atomForm/', [
                'loadSingleAtomList',
                'loadSubflowList',
                'loadAtomConfig',
                'loadPluginServiceMeta'
            ]),
            ...mapActions('project/', [
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
                'setConstants',
                'setAtomList'
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
                'saveTaskSchemeList'
            ]),
            async initData () {
                this.initTemplateData()
                // 获取流程内置变量
                this.getSystemVars()
                this.getSingleAtomList()
                this.getProjectBaseInfo()
                this.templateDataLoading = true
                if (['edit', 'clone', 'view'].includes(this.type)) {
                    await this.getTemplateData()
                    if (this.type !== 'view') {
                        this.templateDataLoading = true
                        this.getTplDraftData()
                    }
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
            /**
             * 加载标准插件列表
             */
            async getSingleAtomList (val) {
                this.singleAtomListLoading = true
                try {
                    const params = { scope: 'flow' }
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
                    this.setAtomList(this.atomList)
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

                    // 如果查看模式下，流程未发布。则切到编辑模式
                    const { params, query } = this.$route
                    if (params.type === 'view' && !templateData.published) {
                        this.$router.replace({
                            name: 'templatePanel',
                            query,
                            params: {
                                ...params,
                                type: 'edit'
                            }
                        })
                        this.reload()
                    }
                    this.tplActions = templateData.auth_actions
                    this.collectInfo = {
                        isCollected: templateData.collected,
                        collectionId: templateData.collection_id
                    }
                    this.published = templateData.published
                    if (this.type === 'clone') {
                        templateData.name = templateData.name.slice(0, STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH - 6) + '_clone'
                    }
                    this.setTemplateData(templateData)
                } catch (e) {
                    if (e.status === 404) {
                        this.$router.push({ name: 'notFoundPage' })
                    }
                    console.log(e)
                } finally {
                    this.templateDataLoading = false
                }
            },
            // 获取草稿详情
            async getTplDraftData () {
                try {
                    const templateData = await this.loadTemplateDraft({
                        templateId: this.template_id,
                        common: this.common
                    })

                    const { edit_time, editor, pipeline_tree } = templateData
                    // 草稿更新信息
                    this.draftUpdateInfo = { edit_time, editor }
                    const pipelineTree = JSON.parse(pipeline_tree)
                    this.setPipelineTree(pipelineTree)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateDataLoading = false
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
            checkDirtyData () {
                const ins = new DealVarDirtyData(this.constants)
                const illegalKeys = ins.checkKeys()
                if (illegalKeys.length) {
                    const h = this.$createElement
                    this.$bkInfo({
                        extCls: 'var-dirty-data-dialog',
                        width: 500,
                        okText: this.$t('清除'),
                        cancelText: this.$t('取消'),
                        subHeader: h('p', { style: {} }, [
                            this.$t('自定义变量中存在系统变量/项目变量的key，需要清除后才能保存，是否一键清除？(可通过【模版数据-constants】进行确认)'),
                            h('p', { style: { marginTop: '10px' } }, [this.$t('问题变量有：'), illegalKeys.join(',')])
                        ]),
                        confirmFn: async () => {
                            const constants = ins.handleIllegalKeys()
                            this.setConstants(constants)
                            await this.publishDraft()
                        }
                    })
                    return true
                }
                return false
            },
            /**
             * 发布草稿
             */
            async publishDraft () {
                // 检查全局变量是否存在脏数据
                const hasDirtyData = this.checkDirtyData()
                if (hasDirtyData) return

                this.templateSaving = true
                try {
                    const resp = await this.publishTemplateDraft({
                        templateId: this.template_id,
                        common: this.common
                    })
                    if (!resp.result) {
                        // 前端校验返回数据包含errorId，此时采用message消息提醒
                        if ('errorId' in resp) {
                            this.$bkMessage({
                                message: resp.message,
                                theme: 'error',
                                delay: 10000
                            })
                            this.isParallelGwErrorMsg = resp.message
                            this.validateConnectFailList.push(resp.errorId)
                        }
                        return
                    }
                    // 切换路由到查看模式
                    const { params, query } = this.$route
                    this.$router.replace({
                        name: this.common ? 'commonTemplatePanel' : 'templatePanel',
                        query,
                        params: {
                            ...params,
                            type: 'view'
                        }
                    })
                    this.$bkMessage({
                        message: i18n.t('发布成功'),
                        theme: 'success'
                    })
                    this.isTemplateDataChanged = false
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateSaving = false
                }
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
                    this.activeSettingTab = 'globalVariableTab'
                }
            },
            /**
             * 设置流程模板为修改状态
             */
            templateDataChanged (val = true) {
                this.isTemplateDataChanged = val
            },
            /**
             * 任务节点校验
             * 校验项包含：标准插件类型，节点名称，输入参数
             * @return isAllValid {Boolean} 节点是否合法
             */
            validateAtomNode () {
                let isAllValid = true
                const errorId = []
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
                        errorId.push(node.id)
                        this.markInvalidNode(id)
                    }
                })
                if (!isAllValid) {
                    let message = this.isParallelGwErrorMsg || i18n.t('任务节点参数错误，请点击错误节点查看详情')
                    if (this.typeOfNodeNameEmpty) {
                        message = this.typeOfNodeNameEmpty === 'serviceActivity' ? i18n.t('请选择节点的插件类型') : i18n.t('请选择节点的子流程')
                    }
                    if (errorId.length) {
                        this.validateConnectFailList.push(...errorId)
                    }
                    this.$bkMessage({
                        message,
                        theme: 'error',
                        delay: 10000
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
                // 点击节点时，清除校验异常状态
                const index = this.validateConnectFailList.findIndex(val => val === id)
                if (index > -1) {
                    this.validateConnectFailList.splice(index, 1)
                }
                this.showConfigPanel(id)
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
                    if (validateMessage.errorId) {
                        this.validateConnectFailList.push(...validateMessage.errorId)
                    }
                    this.$bkMessage({
                        message: validateMessage.message,
                        theme: 'error',
                        ellipsisLine: 0,
                        delay: 10000
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
                        this.$refs.templateCanvas.removeAllConnector()
                        this.setPipelineTree(res.data.pipeline_tree)
                        this.$nextTick(() => {
                            this.$refs.templateCanvas.updateCanvas()
                            this.$refs.templateCanvas.onResetPosition()
                            this.templateDataChanged()
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
                // 节点编辑时只更新position不更新activities
                if (changeType === 'edit') return
                switch (location.type) {
                    case 'tasknode':
                    case 'subflow':
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
                // 异常节点状态处理
                if (!this.validateConnectFailList.length) return
                // 删除节点时，清除对应的校验失败节点
                if (changeType === 'delete') {
                    const index = this.validateConnectFailList.findIndex(val => val === location.id)
                    if (index > -1) {
                        this.validateConnectFailList.splice(index, 1)
                        this.isParallelGwErrorMsg = ''
                    }
                } else if (changeType === 'add' && location.type === 'convergegateway') { // 新增汇聚网关时，判断下是否有并行网关校验失败
                    this.$nextTick(() => {
                        this.checkParallelGwConnect()
                    })
                }
            },
            // 检查并行网关/条件并行网关的连线是否包含汇聚网关
            checkParallelGwConnect () {
                const index = this.validateConnectFailList.findIndex(val => {
                    const gateway = this.gateways[val]
                    if (gateway && ['ParallelGateway', 'ConditionalParallelGateway'].includes(gateway.type)) {
                        const nodeBranches = new Set([gateway.id]) // 分支上包含的节点
                        this.checkedNodes = []
                        this.checkedConvergeNodes = []
                        this.getNodeBranches(gateway.id, gateway.id, nodeBranches)
                        return nodeBranches.size === 1
                    }
                })
                if (index > -1) {
                    this.validateConnectFailList.splice(index, 1)
                    this.isParallelGwErrorMsg = ''
                }
            },
            getNodeBranches (id, branchId, nodeBranches) {
                // 重复节点
                if (this.checkedNodes.includes(id)) {
                    nodeBranches.delete(branchId)
                    return
                }
                this.checkedNodes.push(id)
                // 当前节点所有输出节点
                const targetIds = this.nodeTargetMaps[id] || []
                // 多个输出节点
                if (targetIds.length > 1) {
                    // 删除旧的分支branchId，添加新的分支
                    nodeBranches.delete(branchId)
                    targetIds.forEach(targetId => {
                        nodeBranches.add(targetId)
                        this.getNodeBranches(targetId, targetId, nodeBranches)
                    })
                } else if (targetIds.length === 1) {
                    // 汇聚网关
                    if (this.convergeGwNodes.includes(id)) {
                        // 如果这个汇聚网关之前被找到过，则表示当前分支和其他分支在该汇聚网关会合了，此时需要删掉当前分支branchId
                        if (this.checkedConvergeNodes.includes(id)) {
                            nodeBranches.delete(branchId)
                        } else {
                            // 将未找到过的汇聚网关记录下来
                            this.checkedConvergeNodes.push(id)
                            // 如果存在多个分支，则说明当前的汇聚节点不是分支的回合节点，所以需要用找到过的汇聚网关往下继续找
                            if (nodeBranches.size > 1) {
                                this.checkedConvergeNodes.forEach(nodeId => {
                                    // 汇聚网关只有一个输出节点所以用[0]取输出id
                                    const targetId = this.nodeTargetMaps[nodeId][0]
                                    this.getNodeBranches(targetId, branchId, nodeBranches)
                                })
                            }
                        }
                    } else {
                        const targetId = targetIds[0]
                        // 找到结束节点则退出递归
                        this.getNodeBranches(targetId, branchId, nodeBranches)
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
                if (!this.validateConnectFailList.length) return
                const idList = [line.target.id, line.source.id]
                const nodeList = this.validateConnectFailList.filter(val => idList.includes(val))
                // 新增连线时如果并行网关异常，检查网关的连线是否包含汇聚网关
                if (this.isParallelGwErrorMsg && changeType === 'add') {
                    this.checkParallelGwConnect()
                    return
                }
                // 没有直接修改与问题节点的连线则不进行后续处理
                if (!nodeList || !nodeList.length) return
                nodeList.forEach(node => {
                    let nodeInfo = this.activities[node] || this.locations[node] || this.gateways[node]
                    if (!nodeInfo) {
                        nodeInfo = node === this.start_event.id ? this.start_event : node === this.end_event.id ? this.end_event : {}
                    }
                    if (nodeInfo.id) {
                        const index = this.validateConnectFailList.findIndex(val => val === node)
                        this.validateConnectFailList.splice(index, 1)
                        this.isParallelGwErrorMsg = ''
                    }
                })
            },
            /**
             * 节点位置移动
             */
            onLocationMoveDone (location) {
                this.setLocationXY(location)
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
            onClosePreview () {
                this.$refs.taskSelectNode.togglePreviewMode(false)
            },
            goBackViewMode () {
                this.$bkInfo({
                    ...this.infoBasicConfig,
                    confirmFn: () => {
                        // 返回查看模式时初始化数据
                        this.isTemplateDataChanged = false
                        this.$router.back()
                        this.initData()
                    }
                })
            },
            // 发布草稿回调
            onPublishDraft () {
                if (this.templateSaving) return
                const isAllNodeValid = this.checkNodeAndSaveTemplate()
                if (!isAllNodeValid) return
                this.$bkInfo({
                    title: this.$t('确认发布流程'),
                    subTitle: `【${this.name}】?`,
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    okText: this.$t('发布'),
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.publishDraft()
                    }
                })
            },
            // 校验节点配置
            checkNodeAndSaveTemplate () {
                // 校验节点数目
                const validateMessage = validatePipeline.isNodeLineNumValid(this.canvasData)
                if (!validateMessage.result) {
                    // 获取检验不合格节点
                    const validateConnectFailList = []
                    if (validateMessage.errorId) {
                        validateConnectFailList.push(...validateMessage.errorId)
                    }
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
                        ellipsisLine: 2,
                        delay: 10000
                    })
                    return
                }
                // 节点配置是否错误
                const nodeWithErrors = document.querySelectorAll('.canvas-node-item .failed')
                if (nodeWithErrors && nodeWithErrors.length) {
                    this.templateSaving = false
                    let message = this.isParallelGwErrorMsg || i18n.t('任务节点参数错误，请点击错误节点查看详情')
                    if (this.typeOfNodeNameEmpty) {
                        message = this.typeOfNodeNameEmpty === 'serviceActivity' ? i18n.t('请选择节点的插件类型') : i18n.t('请选择节点的子流程')
                    }
                    this.$bkMessage({
                        message,
                        theme: 'error',
                        ellipsisLine: 2,
                        delay: 10000
                    })
                    return
                }
                return this.validateAtomNode()
            },
            // 修改line和location
            onReplaceLineAndLocation (data) {
                this.replaceLineAndLocation(data)
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
                    confirmFn: () => {
                        this.isShowConditionEdit = false
                    }
                })
            },
            onCloseConfigPanel (openVariablePanel) {
                this.isShowConditionEdit = false
                this.backToVariablePanel = false
                if (openVariablePanel) {
                    this.activeSettingTab = 'globalVariableTab'
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
                // 获取对应dom
                const nodeEl = document.querySelector(`#${id} .canvas-node-item`)
                // 判断dom是否存在当前视图中
                const isInViewPort = this.judgeInViewPort(nodeEl)
                // 如果存在只需要节点摇晃，不存在需要将节点挪到画布中间并节点摇晃
                if (!isInViewPort) {
                    const { width, height } = document.querySelector('#canvasContainer').getBoundingClientRect()
                    const { x, y } = this.locations.find(item => item.id === id)
                    const offsetX = (width - 154) / 2 - x
                    const offsetY = (height - 54) / 2 - y
                    this.$refs.templateCanvas.setCanvasPosition(offsetX, offsetY, true)
                }
                // 移动画布到选中节点位置的摇晃效果
                if (nodeEl) {
                    nodeEl.classList.add('node-shake')
                    setTimeout(() => {
                        nodeEl.classList.remove('node-shake')
                    }, 500)
                }
            },
            // dom是否存在当前视图中
            judgeInViewPort (element) {
                if (!element) return false
                const viewWidth = window.innerWidth || document.documentElement.clientWidth
                const viewHeight = window.innerHeight || document.documentElement.clientHeight
                const { top, right, bottom, left } = element.getBoundingClientRect()
                return top >= 0 && left >= 0 && right <= viewWidth && bottom <= viewHeight
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
            handleBeforeUnload (e) {
                e.returnValue = i18n.t('系统不会保存您所做的更改，确认离开？')
                return i18n.t('系统不会保存您所做的更改，确认离开？')
            },
            // 多 tab 打开同一流程模板
            onMultipleTabConfirm () {
                this.checkNodeAndSaveTemplate()
                this.multipleTabDialogShow = false
            }
        },
        beforeRouteLeave (to, from, next) { // leave or reload page
            if (this.allowLeave || !this.isTemplateDataChanged) {
                this.clearAtomForm()
                next()
            } else {
                this.leaveToPath = to.fullPath
                this.$bkInfo({
                    ...this.infoBasicConfig,
                    cancelFn: () => {
                        bus.$emit('cancelRoute')
                    },
                    confirmFn: () => {
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
    .tpl-edit-model {
        height: 100vh;
        /deep/.template-canvas {
            margin: 30px 60px;
            width: calc(100% - 120px);
            height: calc(100% - 120px);
            .canvas-wrapper {
                background: #fafbfd;
                border: 1px solid #dcdee5;
                border-radius: 2px;
                background-image: radial-gradient(#c5c7cd 2px, transparent 0);
                background-size: 70px 70px;
                background-position: -10px -10px;
            }
            .tool-panel-wrap {
                top: -20px;
                left: -43px;
            }
            .palette-panel-wrap {
                position: absolute;
                top: 93px;
                left: -43px;
                height: auto;
                width: 54px;
                border-right: none;
                box-shadow: 0 2px 4px 0 #0000001a;
                .palette-panel {
                    width: 54px;
                }
                .palette-container {
                    border-right: none;
                }
            }
        }
        /deep/.template-side {
            top: 60px;
            height: calc(100% - 60px);
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
