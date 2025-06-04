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
    <div class="edit-periodic-task">
        <bk-sideslider
            :width="800"
            ext-cls="edit-periodic-sideslider"
            :is-show.sync="isModifyDialogShow"
            :quick-close="true"
            :before-close="onCloseConfig">
            <div slot="header">
                <div class="preview-header" v-if="isPreview && previewScheme">
                    <span @click="isPreview = false">{{ sideSliderTitle }}</span>
                    <i class="common-icon-angle-right"></i>
                    {{ previewScheme }}
                </div>
                <template v-else>{{ sideSliderTitle }}</template>
            </div>
            <template slot="content" v-if="isPreview">
                <NodePreview
                    ref="nodePreview"
                    :preview-data-loading="previewDataLoading"
                    :canvas-data="canvasData"
                    :preview-bread="previewBread"
                    :preview-data="previewData"
                    :common="isCommon"
                    @onNodeClick="onNodeClick"
                    @onSelectSubflow="onSelectSubFlow">
                </NodePreview>
                <div class="btn-footer">
                    <bk-button @click="isPreview = false">{{ $t('返回编辑') }}</bk-button>
                </div>
            </template>
            <div slot="content" v-show="!isPreview">
                <bk-alert type="info" :title="$t('周期任务根据创建时的流程和执行方案数据生成快照保存，流程变更后不影响周期任务，可手动更新到使用流程最新数据。')"></bk-alert>
                <section class="config-section">
                    <p class="title mt0">{{$t('流程')}}</p>
                    <bk-form
                        :label-width="90"
                        ref="basicConfigForm"
                        :rules="rules"
                        :model="formData">
                        <bk-form-item :label="$t('流程')" :required="true" property="flow" class="flow-form-item" data-test-id="periodicEdit_form_selectTemplate">
                            <bk-select
                                v-model="formData.template_source"
                                :disabled="isEdit"
                                :clearable="false"
                                class="flow-type-select"
                                @selected="onFlowTypeChange">
                                <bk-option id="project" :name="$t('项目流程')"></bk-option>
                                <bk-option id="common" :name="$t('公共流程')"></bk-option>
                            </bk-select>
                            <div v-if="isEdit" class="select-box">
                                <div class="select-wrapper">
                                    <p>
                                        <span v-if="formData.is_latest === false" class="update-tip">[{{ $t('流程有更新') }}]</span>
                                        {{ formData.task_template_name }}
                                    </p>
                                    <i class="bk-icon icon-angle-down"></i>
                                </div>
                                <bk-button
                                    v-if="formData.is_latest !== true"
                                    ext-cls="update-btn"
                                    theme="primary"
                                    data-test-id="periodicList_form_update"
                                    :loading="updateLoading"
                                    @click="onUpdatePeriodicTask">
                                    <i class="common-icon-update"></i>
                                    {{ $t('更新流程') }}
                                </bk-button>
                            </div>
                            <bk-select
                                v-else
                                ref="tplSelect"
                                v-model="formData.template_id"
                                :searchable="true"
                                :placeholder="$t('请选择')"
                                :clearable="false"
                                enable-scroll-load
                                :scroll-loading="{ isLoading: tplScrollLoading }"
                                ext-popover-cls="tpl-popover"
                                :remote-method="onTplSearch"
                                v-bkloading="{ isLoading: templateLoading, size: 'small', extCls: 'template-loading' }"
                                @clear="onClearTemplate"
                                @selected="onSelectTemplate"
                                @scroll-end="onSelectScrollLoad">
                                <bk-option
                                    v-for="option in templateList"
                                    :key="option.id"
                                    :disabled="!hasPermission([flowPermission.view], option.auth_actions)"
                                    :id="option.id"
                                    :name="option.name">
                                    <p
                                        :title="option.name"
                                        v-cursor="{ active: !hasPermission([flowPermission.view], option.auth_actions) }"
                                        @click="onTempSelect([flowPermission.view], option)">
                                        {{ option.name }}
                                    </p>
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item
                            class="scheme-form-item"
                            data-test-id="periodicEdit_form_selectScheme"
                            v-if="!isPreview && !isTplDeleted"
                            :label="formData.is_latest === null ? $t('已选节点') : $t('执行方案')"
                            property="schemeId">
                            <div class="scheme-wrapper">
                                <p v-if="formData.is_latest === null" class="exclude-wrapper" v-bk-overflow-tips>
                                    {{ includeNodes }}
                                </p>
                                <bk-select
                                    v-else
                                    v-model="formData.schemeId"
                                    :searchable="true"
                                    :placeholder="schemeSelectPlaceholder"
                                    :multiple="true"
                                    :clearable="false"
                                    :disabled="isSelectSchemeDisable"
                                    :loading="isLoading || schemeLoading"
                                    @selected="onSelectScheme">
                                    <bk-option
                                        v-for="(option, index) in schemeList"
                                        :key="index"
                                        :id="option.id"
                                        :name="option.name"
                                        :disabled="previewDataLoading">
                                        <span>{{ option.name }}</span>
                                        <span v-if="option.isDefault" class="default-label">{{$t('默认')}}</span>
                                        <i v-if="formData.schemeId.includes(option.id)" class="bk-icon icon-check-line"></i>
                                    </bk-option>
                                </bk-select>
                                <bk-button
                                    theme="default"
                                    :disabled="isLoading || !formData.template_id"
                                    @click="togglePreviewMode">
                                    {{ $t('预览') }}
                                </bk-button>
                            </div>
                            <p v-if="formData.schemeId.length && formData.is_latest === false" class="schema-disable-tip">
                                {{ $t('当前流程非最新，执行方案不可更改，请先更新流程') }}
                            </p>
                            <p v-if="formData.is_latest === null" class="schema-disable-tip">
                                {{ $t('当前任务为旧数据，仅记录已选节点，强制更新后可选执行方案并获得提示更新能力') }}
                            </p>
                            <p v-if="hasDeleteScheme" class="schema-disable-tip">
                                {{ $t('选中的执行方案被删除，请重新选择执行方案') }}
                            </p>
                        </bk-form-item>
                        <p class="title">{{$t('任务信息')}}</p>
                        <bk-form-item :label="$t('任务名称')" :required="true" property="taskName" data-test-id="periodicEdit_form_taskName">
                            <bk-input
                                :clearable="true"
                                v-model="formData.name"
                                :maxlength="stringLength.TASK_NAME_MAX_LENGTH"
                                :show-word-limit="true">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('周期表达式')" :required="true" property="loop" data-test-id="periodicEdit_form_loop">
                            <CronRuleSelect
                                ref="cronRuleSelect"
                                class="loop-rule"
                                v-model="cronExpression" />
                        </bk-form-item>
                    </bk-form>
                </section>
                <section class="config-section">
                    <p class="title">{{$t('参数信息')}}</p>
                    <div v-bkloading="{ isLoading: isLoading || previewDataLoading }">
                        <NoData v-if="isVariableEmpty" :message="$t('暂无参数')"></NoData>
                        <TaskParamEdit
                            v-else
                            ref="TaskParamEdit"
                            class="task-param-edit"
                            :constants="periodicConstants">
                        </TaskParamEdit>
                    </div>
                </section>
                <section class="config-section mb20">
                    <p class="title">
                        <span>{{ $t('通知') }}</span>
                        <span v-if="!isLoading && formData.template_id && !isTplDeleted" class="tip-desc">
                            {{ $t('通知方式统一在流程基础信息管理。如需修改，请') }}
                            <a
                                class="link"
                                data-test-id="periodicEdit_form_jumpFlow"
                                @click="getJumpUrl()">
                                {{ $t('前往流程') }}
                            </a>
                        </span>
                    </p>
                    <div v-bkloading="{ isLoading: isLoading || schemeLoading, opacity: 1, zIndex: 100 }">
                        <NotifyTypeConfig
                            v-if="formData.template_id && !templateDataLoading"
                            :notify-type-label="$t('启动失败') + ' ' + $t('通知方式')"
                            :label-width="87"
                            :table-width="570"
                            :notify-type="notifyType"
                            :project_id="project_id"
                            :is-view-mode="true"
                            :notify-type-list="[{ text: $t('任务状态') }]"
                            :common="formData.template_source === 'common' ? 1 : 0"
                            :notify-type-extra-info="notifyTypeExtraInfo"
                            :receiver-group="receiverGroup">
                        </NotifyTypeConfig>
                        <NoData v-else></NoData>
                    </div>
                </section>
                <div class="btn-footer">
                    <bk-button
                        theme="primary"
                        :loading="saveLoading"
                        :disabled="isLoading || previewDataLoading"
                        data-test-id="periodicEdit_form_saveBtn"
                        :class="{ 'btn-permission-disable': hasNoCreatePerm }"
                        v-cursor="{ active: hasNoCreatePerm }"
                        @click="onPeriodicConfirm">
                        {{ isEdit ? $t('保存') : $t('提交') }}
                    </bk-button>
                    <bk-button
                        theme="default"
                        :disabled="saveLoading"
                        data-test-id="periodicEdit_form_cancelBtn"
                        @click="onCancelSave">
                        {{ $t('取消') }}
                    </bk-button>
                </div>
            </div>
        </bk-sideslider>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import { PERIODIC_REG, NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import CronRuleSelect from '@/components/common/Individualization/cronRuleSelect.vue'
    import TaskParamEdit from '@/pages/task/TaskParamEdit.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import NotifyTypeConfig from '@/pages/template/TemplateEdit/TemplateSetting/NotifyTypeConfig.vue'
    import permission from '@/mixins/permission.js'
    import NodePreview from '@/pages/task/NodePreview.vue'
    import { formatCanvasData } from '@/utils/checkDataType'

    export default {
        name: 'ModifyPeriodicDialog',
        components: {
            TaskParamEdit,
            NoData,
            CronRuleSelect,
            NotifyTypeConfig,
            NodePreview
        },
        mixins: [permission],
        props: [
            'isModifyDialogShow',
            'taskId',
            'cron',
            'constants',
            'loading',
            'curRow',
            'isEdit',
            'project_id'
        ],
        data () {
            const {
                name = '',
                is_latest = '',
                task_template_name = '',
                template_source = 'project',
                template_id = '',
                template_scheme_ids = []
            } = this.curRow
            const schemeId = template_scheme_ids || []
            return {
                formData: {
                    name,
                    is_latest: this.isEdit ? is_latest : true,
                    template_source,
                    task_template_name,
                    template_id,
                    schemeId: this.isEdit && schemeId.length ? schemeId : []
                },
                initFormData: {},
                templateData: {},
                templateLoading: false,
                tplScrollLoading: false,
                templateList: [],
                templateDataLoading: false,
                schemeLoading: false,
                schemeList: [],
                isPreview: false,
                previewDataLoading: false,
                previewBread: [],
                previewData: {
                    location: [],
                    line: [],
                    gateways: {},
                    constants: []
                },
                selectedNodes: [],
                notifyType: [[]],
                receiverGroup: [],
                notifyTypeExtraInfo: {},
                hasNoCreatePerm: false,
                saveLoading: false,
                periodicRule: {
                    required: true,
                    regex: PERIODIC_REG
                },
                stringLength: STRING_LENGTH,
                rules: {
                    taskName: [
                        {
                            required: true,
                            validator: (val) => {
                                return this.formData.name
                            },
                            message: i18n.t('任务名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return NAME_REG.test(this.formData.name)
                            },
                            message: i18n.t('任务名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return STRING_LENGTH.TASK_NAME_MAX_LENGTH >= this.formData.name.length
                            },
                            message: i18n.t('任务名称不能超过') + STRING_LENGTH.TASK_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'change'
                        }
                    ],
                    flow: [
                        {
                            required: true,
                            validator: (val) => {
                                return this.formData.template_id
                            },
                            message: i18n.t('请选择流程模板'),
                            trigger: 'blur'
                        }
                    ]
                },
                periodicCronImg: require('@/assets/images/' + i18n.t('task-zh') + '.png'),
                periodicConstants: {},
                updateLoading: false,
                isUpdatePipelineTree: false, // pipeline_tree是否被更新替换
                totalPage: 1,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                },
                flowName: '',
                isTplDeleted: false, // 旧数据模板是否被删除
                hasDeleteScheme: false, // 是否存在执行方案被删除
                cronExpression: this.cron // 周期表达式
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'projectName': state => state.projectName
            }),
            ...mapState({
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            isVariableEmpty () {
                return Object.keys(this.periodicConstants).length === 0
            },
            isCommon () {
                return this.formData.template_source === 'common'
            },
            flowPermission () {
                return {
                    view: this.isCommon ? 'common_flow_view' : 'flow_view',
                    create: this.isCommon ? 'common_flow_create_periodic_task' : 'flow_create_periodic_task'
                }
            },
            sideSliderTitle () {
                return this.isEdit ? i18n.t('编辑周期任务') : i18n.t('新建周期任务')
            },
            previewScheme () {
                if (this.formData.is_latest === null) {
                    return ''
                }
                const schemeId = this.formData.schemeId
                if (!schemeId.length) return ''
                const schemeNames = this.schemeList.reduce((acc, cur) => {
                    if (schemeId.includes(cur.id)) {
                        acc.push(cur.name)
                    }
                    return acc
                }, [])
                return i18n.t('预览') + '：' + schemeNames.join(' , ')
            },
            isLoading () {
                return this.templateLoading || this.templateDataLoading
            },
            includeNodes () {
                if (this.formData.is_latest !== null) return ''
                const { activities = {} } = this.curRow.pipeline_tree || {}
                const nodes = Object.values(activities).map(item => item.name)
                return nodes.join(',')
            },
            schemeSelectPlaceholder () {
                return this.formData.template_id && !this.schemeList.length ? i18n.t('此流程无执行方案，无需选择') : i18n.t('请选择')
            },
            isSelectSchemeDisable () {
                const { is_latest, template_id } = this.formData
                return is_latest !== true || !template_id || this.previewDataLoading || !this.schemeList.length
            },
            canvasData () {
                return formatCanvasData('preview', this.previewData)
            }
        },
        created () {
            this.initFormData = tools.deepClone(this.formData)

            if (this.isEdit) {
                this.hasNoCreatePerm = false
                this.periodicConstants = tools.deepClone(this.constants)
                const id = this.curRow.template_id
                this.getTemplateDate(id)
            } else {
                this.templateLoading = true
                this.getTemplateList()
            }
            this.onTplSearch = tools.debounce(this.handleTplSearch, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('templateList', [
                'loadTemplateList'
            ]),
            ...mapActions('task/', [
                'loadTaskScheme',
                'getDefaultTaskScheme',
                'loadPreviewNodeData'
            ]),
            ...mapActions('periodic/', [
                'modifyPeriodicCron',
                'modifyPeriodicConstants',
                'updatePeriodicTask',
                'updatePeriodicPartial',
                'createPeriodic',
                'loadCommonTemplateList'
            ]),
            ...mapActions('template/', [
                'loadTemplateData'
            ]),
            async getTemplateList (add) {
                try {
                    const offset = (this.pagination.current - 1) * this.pagination.limit
                    const params = {
                        project__id: this.project_id,
                        limit: 15,
                        offset,
                        pipeline_template__name__icontains: this.flowName || undefined,
                        common: this.isCommon
                    }
                    const templateListData = this.isCommon
                        ? await this.loadCommonTemplateList(params)
                        : await this.loadTemplateList(params)
                    if (add) {
                        this.templateList.push(...templateListData.results)
                    } else { // 搜索
                        this.templateList = templateListData.results
                    }
                    this.pagination.count = templateListData.count
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.tplScrollLoading = false
                    this.templateLoading = false
                }
            },
            onTempSelect (applyPerm = [], selectInfo) {
                if (!this.hasPermission(applyPerm, selectInfo.auth_actions)) {
                    const permissionData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }],
                        flow: [selectInfo]
                    }
                    this.applyForPermission(applyPerm, selectInfo.auth_actions, permissionData)
                }
            },
            // 下拉框搜索
            handleTplSearch (val) {
                this.pagination.current = 1
                this.flowName = val
                this.getTemplateList()
            },
            // 下拉框滚动加载
            onSelectScrollLoad () {
                if (this.totalPage !== this.pagination.current) {
                    this.tplScrollLoading = true
                    this.pagination.current += 1
                    this.getTemplateList(true)
                }
            },
            onClearTemplate () {
                this.formData.schemeId = []
                this.schemeList = []
                this.templateData = {}
                this.periodicConstants = {}
            },
            onFlowTypeChange () {
                this.templateLoading = true
                this.formData.template_id = ''
                this.formData.name = ''
                this.formData.task_template_name = ''
                this.onClearTemplate()
                this.handleTplSearch()
            },
            async getTemplateDate (id) {
                // 获取模板详情
                try {
                    this.templateDataLoading = true
                    const params = { templateId: id, common: this.isCommon }
                    const templateData = await this.loadTemplateData(params)
                    // 获取流程模板的通知配置
                    const { notify_receivers, notify_type } = templateData
                    this.notifyType = [notify_type.success.slice(0), notify_type.fail.slice(0)]
                    const { receiver_group: receiverGroup, extra_info: extraInfo = {} } = JSON.parse(notify_receivers)
                    this.receiverGroup = receiverGroup && receiverGroup.slice(0)
                    this.notifyTypeExtraInfo = { ...extraInfo }
                    const pipelineDate = JSON.parse(templateData.pipeline_tree)
                    this.selectedNodes = Object.keys(pipelineDate.activities)
                    this.templateData = Object.assign({}, templateData, { pipeline_tree: pipelineDate })
                    // 获取模板对应的执行方案
                    await this.getTemplateScheme()
                    if (this.formData.schemeId.length) {
                        if (this.formData.is_latest) { // 只有最新流程才允许选择执行方案
                            this.onSelectScheme(this.formData.schemeId, [], false)
                            this.isUpdatePipelineTree = false
                        } else {
                            this.previewData = tools.deepClone(this.curRow.pipeline_tree)
                            this.selectedNodes = Object.values(this.previewData.activities).map(item => item.template_node_id)
                        }
                    } else if (!this.isEdit) {
                        this.formData.schemeId = this.schemeList.length ? [0] : []
                        const templateInfo = this.templateList.find(item => item.id === id)
                        await this.getPreviewNodeData(id, templateInfo.version, true)
                    } else {
                        this.previewData = tools.deepClone(this.curRow.pipeline_tree)
                    }
                } catch (e) {
                    // 判断模板是否为删除
                    if (e.status === 404 && this.isEdit) {
                        this.isTplDeleted = true
                        this.previewData = tools.deepClone(this.curRow.pipeline_tree)
                        this.$bkMessage({
                            theme: 'warning',
                            message: i18n.t('对应流程模板已被删除，仅提供修改任务名称，任务执行时间')
                        })
                    }
                    console.warn(e)
                } finally {
                    this.templateDataLoading = false
                    this.initFormData = tools.deepClone(this.formData)
                }
            },
            async onSelectTemplate (id) {
                // 清除表单错误提示
                this.$refs.basicConfigForm.clearError()
                // 自动填充任务名称
                const templateInfo = this.templateList.find(item => item.id === id)
                this.formData.name = templateInfo ? templateInfo.name + '_' + i18n.t('周期执行') : ''
                this.formData.schemeId = []
                await this.getTemplateDate(id)
                this.queryCreatePeriodicTaskPerm(id)
            },
            async getTemplateScheme () {
                this.schemeLoading = true
                try {
                    const defaultScheme = await this.loadDefaultSchemeList()
                    const data = {
                        isCommon: this.isCommon || undefined,
                        project_id: this.isCommon ? undefined : this.project_id,
                        template_id: this.formData.template_id
                    }
                    const resp = await this.loadTaskScheme(data)
                    this.schemeList = resp.map(item => {
                        item.isDefault = defaultScheme.includes(item.id)
                        return item
                    })
                    const { activities } = this.templateData.pipeline_tree
                    const nodeList = Object.keys(activities)
                    if (this.schemeList.length) {
                        this.schemeList.unshift({
                            data: JSON.stringify(nodeList),
                            id: 0,
                            idDefault: false,
                            name: '<' + i18n.t('不使用执行方案') + '>'
                        })
                        if (this.isEdit) {
                            const { schemeId } = this.formData
                            this.formData.schemeId = schemeId.length ? schemeId : [0]
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.schemeLoading = false
                }
            },
            // 获取默认方案列表
            async loadDefaultSchemeList () {
                try {
                    const resp = await this.getDefaultTaskScheme({
                        project_id: this.isCommon ? undefined : this.project_id,
                        template_id: this.formData.template_id,
                        template_type: this.isCommon ? 'common' : undefined
                    })
                    if (resp.data.length) {
                        const { scheme_ids: schemeIds } = resp.data[0]
                        return schemeIds
                    }
                    return []
                } catch (error) {
                    console.error(error)
                }
            },
            onSelectScheme (ids, options, updateConstants = true) {
                if (this.previewDataLoading) return
                this.isUpdatePipelineTree = true
                // 切换执行方案时取消<不使用执行方案>
                const lastId = options.length ? options[options.length - 1].id : undefined
                ids = lastId === 0 ? [0] : lastId ? ids.filter(id => id) : ids
                this.formData.schemeId = ids
                if (options.length) {
                    this.hasDeleteScheme = false // 清除执行方案被删除提示
                }
                if (ids.length) {
                    const nodeList = this.schemeList.reduce((acc, cur) => {
                        if (ids.includes(cur.id)) {
                            acc.push(...JSON.parse(cur.data))
                        }
                        return acc
                    }, [])
                    this.selectedNodes = [...new Set(nodeList)]
                } else {
                    const { activities } = this.templateData.pipeline_tree
                    const nodeList = Object.keys(activities)
                    this.selectedNodes = nodeList
                }
                // 更新执行参数
                const { id: templateId, version: latestVersion } = this.templateData
                const version = this.formData.is_latest ? latestVersion : this.curRow.template_version
                this.getPreviewNodeData(templateId, version, updateConstants)
            },
            togglePreviewMode () {
                this.previewBread = []
                this.isPreview = true
                if (this.formData.is_latest) {
                    const { id, name, version } = this.templateData
                    this.previewBread.push({ id, name, version })
                    this.getPreviewNodeData(id, version)
                } else {
                    const { template_id: id, task_template_name: name, template_version: version } = this.curRow
                    this.previewBread.push({ id, name, version })
                }
            },
            /**
             * 获取画布预览节点和全局变量表单项(接口已去掉未选择的节点、未使用的全局变量)
             * @params {Number|String} templateId  模板 ID
             * @params {String} version  模板版本
             * @params {Boolean} updateConstants  更新执行参数
             */
            async getPreviewNodeData (templateId, version, updateConstants) {
                this.previewDataLoading = true
                const excludeNodes = this.getExcludeNode()
                const params = {
                    templateId: Number(templateId),
                    excludeTaskNodesId: excludeNodes,
                    common: this.isCommon,
                    version
                }
                try {
                    const resp = await this.loadPreviewNodeData(params)
                    if (resp.result) {
                        this.previewData = resp.data.pipeline_tree
                        if (updateConstants) {
                            this.periodicConstants = Object.values(this.previewData.constants).reduce((acc, cur) => {
                                // 切换执行方案时需要保留修改的变量值
                                acc[cur.key] = {
                                    ...cur,
                                    value: this.constants[cur.key] ? this.constants[cur.key].value : cur.value
                                }
                                // 如果为元变量并且没有meta字段时自动补充上
                                if (this.isEdit && cur.is_meta && !('meta' in cur)) {
                                    acc[cur.key]['meta'] = cur
                                }
                                return acc
                            }, {})
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.previewDataLoading = false
                }
            },
            getExcludeNode () {
                const nodes = []
                const { activities } = this.templateData.pipeline_tree
                Object.values(activities).forEach(item => {
                    if (this.selectedNodes.indexOf(item.id) === -1 && item.optional) {
                        nodes.push(item.id)
                    }
                })
                return nodes
            },
            /**
             * 点击预览模式下的面包屑
             * @params {String} id  点击的节点id（可能为父节点或其他子流程节点）
             * @params {Number} index  点击的面包屑的下标
             */
            onSelectSubFlow (id, version, index) {
                this.getPreviewNodeData(id, version)
                this.previewBread.splice(index + 1, this.previewBread.length)
            },
            /**
             * 点击子流程节点，并进入新的canvas画面
             * @params {String} id  点击的子流程节点id
             */
            onNodeClick (id) {
                const activity = this.previewData.activities[id]
                if (!activity || activity.type !== 'SubProcess') {
                    return
                }
                const { template_id, name, version } = activity
                this.previewBread.push({
                    id: template_id,
                    name,
                    version
                })
                this.getPreviewNodeData(template_id, activity.version)
            },
            getJumpUrl () {
                const { href } = this.$router.resolve({
                    name: 'templatePanel',
                    params: {
                        type: 'view'
                    },
                    query: {
                        template_id: this.formData.template_id,
                        common: this.isCommon ? 1 : undefined
                    }
                })
                window.open(href, '_blank')
            },
            async onUpdatePeriodicTask () {
                try {
                    this.updateLoading = true
                    this.isUpdatePipelineTree = true
                    const { id, version } = this.templateData
                    await this.getPreviewNodeData(id, version, true)
                    this.formData.is_latest = true
                    this.$bkMessage({
                        'message': i18n.t('流程更新成功'),
                        'theme': 'success'
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.updateLoading = false
                }
            },
            async queryCreatePeriodicTaskPerm (templateId) {
                try {
                    if (!this.isCommon) {
                        const { auth_actions } = this.templateData
                        this.hasNoCreatePerm = !auth_actions.includes(this.flowPermission.create)
                        return
                    }
                    const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                    const data = {
                        action: this.flowPermission.create,
                        resources: [
                            {
                                system: bkSops.id,
                                type: 'project',
                                id: this.project_id,
                                attributes: {}
                            },
                            {
                                system: bkSops.id,
                                type: 'common_flow',
                                id: templateId,
                                attributes: {}
                            }
                        ]
                    }
                    const res = await this.queryUserPermission(data)
                    this.hasNoCreatePerm = !res.data.is_allow
                } catch (e) {
                    console.log(e)
                }
            },
            onCancelSave () {
                this.$emit('onCancelSave')
            },
            // 周期任务保存
            onPeriodicConfirm () {
                if (this.hasNoCreatePerm) {
                    const { id, name, auth_actions } = this.templateData
                    const resourceData = {
                        [this.isCommon ? 'common_flow' : 'flow']: [{ id, name }],
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission([this.flowPermission.create], auth_actions, resourceData)
                    return
                }
                const isCronError = this.$refs.cronRuleSelect.isError
                if (isCronError) return
                const paramEditComp = this.$refs.TaskParamEdit
                this.$refs.basicConfigForm.validate().then(async (result) => {
                    let formValid = true
                    let constants = {}
                    if (paramEditComp) {
                        const formData = await paramEditComp.getVariableData()
                        constants = formData
                        formValid = paramEditComp.validate()
                    }
                    const cronArray = this.cronExpression.split(' ')
                    if (cronArray.length !== 5) {
                        this.$bkMessage({
                            'message': i18n.t('输入周期表达式非法，请校验'),
                            'theme': 'error'
                        })
                        return
                    }
                    if (!result || !formValid) {
                        return
                    }
                    this.saveLoading = true
                    const jsonCron = {
                        'minute': cronArray[0],
                        'hour': cronArray[1],
                        'day_of_week': cronArray[4],
                        'day_of_month': cronArray[2],
                        'month_of_year': cronArray[3]
                    }
                    const pipelineData = {
                        ...this.previewData,
                        constants
                    }

                    if (this.isEdit) { // 确认编辑周期任务
                        this.onModifyPeriodicTask(jsonCron, pipelineData)
                    } else { // 确认创建周期任务
                        this.onCreatePeriodicTask(jsonCron, pipelineData)
                    }
                })
            },
            async onModifyPeriodicTask (jsonCron, pipelineData) {
                try {
                    const same = this.judgeDataEqual()
                    if (same) {
                        this.$emit('onCancelSave')
                    } else if (this.isUpdatePipelineTree) { // pipeline_tree被更新替换，调update接口
                        const schemeIds = this.formData.schemeId.filter(id => id)
                        const params = {
                            taskId: this.taskId,
                            project: this.project_id,
                            cron: jsonCron,
                            name: this.formData.name,
                            template_id: this.curRow.template_id,
                            template_scheme_ids: schemeIds,
                            pipeline_tree: JSON.stringify(pipelineData),
                            template_source: this.isCommon ? 'common' : undefined
                        }
                        await this.updatePeriodicTask(params)
                        this.$emit('onConfirmSave')
                    } else { // 修改周期任务部分配置，调patch接口
                        const constantsData = Object.values(pipelineData.constants).reduce((acc, cur) => {
                            acc[cur.key] = cur.value
                            return acc
                        }, {})
                        const params = {
                            taskId: this.taskId,
                            project: this.project_id,
                            name: this.formData.name,
                            cron: jsonCron,
                            constants: constantsData
                        }
                        await this.updatePeriodicPartial(params)
                        this.$emit('onConfirmSave')
                    }
                    this.$bkMessage({
                        'message': i18n.t('编辑周期任务成功'),
                        'theme': 'success'
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.saveLoading = false
                }
            },
            // 创建周期任务
            async onCreatePeriodicTask (cron, pipelineData) {
                const schemeIds = this.formData.schemeId.filter(id => id)
                const data = {
                    name: this.formData.name,
                    cron: cron,
                    templateId: this.formData.template_id,
                    schemeIds,
                    execData: JSON.stringify(pipelineData),
                    templateSource: this.isCommon ? 'common' : undefined
                }
                try {
                    const response = await this.createPeriodic(data)
                    if (!response.result) return
                    this.$bkMessage({
                        'message': i18n.t('创建周期任务成功'),
                        'theme': 'success'
                    })
                    this.$emit('onConfirmSave')
                } catch (e) {
                    console.log(e)
                } finally {
                    this.saveLoading = false
                }
            },
            judgeDataEqual () {
                const taskParamEdit = this.$refs.TaskParamEdit
                const sameRenderData = taskParamEdit ? taskParamEdit.judgeDataEqual() : true
                const sameFormData = tools.isDataEqual(this.formData, this.initFormData)
                const sameCronDate = this.cron ? this.cron === this.cronExpression : true
                const same = sameFormData && sameCronDate && sameRenderData
                return same
            },
            onCloseConfig () {
                const same = this.judgeDataEqual()
                if (same) {
                    this.onCancelSave()
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.onCancelSave()
                        }
                    })
                }
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

::v-deep .bk-sideslider-content {
    height: calc(100% - 60px);
    position: relative;
    padding: 18px 31px 48px 28px;
    overflow-y: auto;
    @include scrollbar;
}
::v-deep .bk-sideslider-title {
    color: #313238;
    font-size: 16px;
    font-weight: normal;
}
::v-deep .btn-footer {
    z-index: 3000;
}
.loop-rule {
    padding: 16px 20px;
}

.config-section {
    .title {
        color: #313238;
        font-size: 14px;
        line-height: 19px;
        padding: 16px 0 11px;
        margin: 20px 0 24px;
        border-bottom: 1px solid #cacedb;
        .tip-desc {
            line-height: 1;
            font-size: 12px;
            font-weight: normal;
            margin-left: 20px;
            color: #979ba5;
        }
        .link {
            color: #3a84ff;
            cursor: pointer;
        }
    }
    ::v-deep .bk-form {
        margin-bottom: 17px;
        .bk-label {
            font-size: 12px;
            color: #63656e;
        }
        .bk-form-content {
            width: 598px;
        }
        .flow-form-item .bk-form-content {
            display: flex;
            .bk-select,
            .select-box {
                flex: 1;
            }
            .flow-type-select {
                flex: 0 0 150px;
                margin-right: 15px;
            }
        }
        .scheme-form-item {
            .tooltips-icon {
                right: 132px !important;
            }
        }
    }
    .select-box {
        display: flex;
        align-items: center;
        .select-wrapper {
            flex: 1;
            height: 32px;
            position: relative;
            font-size: 12px;
            line-height: 20px;
            color: #63656e;
            padding: 5px 8px;
            background: #fafbfd;
            border: 1px solid #dcdee5;
            border-radius: 2px;
            cursor: not-allowed;
            .update-tip {
                color: #ea3636;
            }
            .icon-angle-down {
                position: absolute;
                right: 7px;
                top: 5px;
                font-size: 20px;
                color: #c4c6cc;
                cursor: not-allowed;
            }
        }
        .update-btn {
            width: 108px;
            flex-shrink: 0;
            margin-left: 16px;
        }
    }
    ::v-deep .notify-type-wrapper {
        .bk-form-content {
            margin-left: 90px !important;
        }
    }
    ::v-deep .template-loading {
        .bk-loading-wrapper {
            top: 65%;
        }
    }
    .exclude-wrapper {
        flex: 1;
        height: 32px;
        font-size: 12px;
        padding: 5px 10px;
        line-height: 1.5;
        color: #63656e;
        border: 1px solid #dcdee5;
        border-radius: 2px;
        background-color: #fafbfd;
        cursor: default;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        white-space: nowrap;
    }
    .scheme-wrapper {
        display: flex;
        align-items: center;
        .bk-select {
            flex: 1;
        }
        .bk-button {
            width: 108px;
            margin-left: 16px;
        }
    }
    .schema-disable-tip {
        font-size: 12px;
        line-height: 15px;
        color: #ff9c01;
        margin-top: 8px;
    }
}
.default-label {
    height: 22px;
    line-height: 22px;
    font-size: 12px;
    padding: 0 10px;
    border-radius: 2px;
    margin-left: 10px;
    color: #14a568;
    background: #e4faf0;
}
.icon-check-line {
    position: absolute;
    right: 16px;
    top: 8px;
    font-size: 16px;
}
.btn-footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #fafbfd;
    padding: 8px 0 8px 24px;
    margin-left: -28px;
    box-shadow: 0 -1px 0 0 #dcdee5;
    .bk-button {
        margin-right: 10px;
        padding: 0 25px;
    }
}
.preview-header {
    display: flex;
    align-self: center;
    font-size: 14px;
    > span {
        color: #3a84ff;
        cursor: pointer;
    }
    .common-icon-angle-right {
        color: #c4c6cc;
        font-size: 20px;
        line-height: inherit;
        margin: 0 5px;
    }
}
.node-preview-wrapper {
    height: calc(100% - 25px);
    margin-bottom: 25px;
}
.tpl-popover {
    .bk-spin-title {
        font-size: 12px;
    }
}
</style>
