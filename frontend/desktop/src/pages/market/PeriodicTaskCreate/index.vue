
<template>
    <div class="create-periodic-task">
        <NodePreview
            v-if="isPreview"
            ref="nodePreview"
            :preview-data-loading="previewDataLoading"
            :canvas-data="canvasData"
            :preview-bread="previewBread"
            :preview-data="previewData"
            :common="isCommon"
            @onNodeClick="onNodeClick"
            @onSelectSubflow="onSelectSubFlow">
        </NodePreview>
        <div v-show="!isPreview" class="content-wrapper">
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
                            :disabled="true"
                            :clearable="false"
                            class="flow-type-select">
                            <bk-option id="project" :name="$t('项目流程')"></bk-option>
                            <bk-option id="common" :name="$t('公共流程')"></bk-option>
                        </bk-select>
                        <div class="select-wrapper">
                            <p>
                                <span v-if="formData.is_latest === false" class="update-tip">[{{ $t('流程有更新') }}]</span>
                                {{ templateData.name }}
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
                                :disabled="isLoading || !templateId"
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
                            :key="taskLoading"
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
                    <span v-if="!isLoading && templateId && !isTplDeleted" class="tip-desc">
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
                        v-if="templateId"
                        :notify-type-label="$t('启动失败') + ' ' + $t('通知方式')"
                        :label-width="87"
                        :table-width="570"
                        :notify-type="notifyType"
                        :project_id="projectId"
                        :is-view-mode="true"
                        :notify-type-list="[{ text: $t('任务状态') }]"
                        :receiver-group="receiverGroup">
                    </NotifyTypeConfig>
                    <NoData v-else></NoData>
                </div>
            </section>
        </div>
        <div class="btn-footer">
            <bk-button
                v-if="isPreview"
                @click="isPreview = false">
                {{ $t('返回编辑') }}
            </bk-button>
            <template v-else>
                <bk-button
                    theme="primary"
                    :loading="saveLoading"
                    :disabled="isLoading || previewDataLoading"
                    data-test-id="periodicEdit_form_saveBtn"
                    :class="{ 'btn-permission-disable': hasNoCreatePerm }"
                    v-cursor="{ active: hasNoCreatePerm }"
                    @click="onPeriodicConfirm">
                    {{ taskId ? $t('保存') : $t('提交') }}
                </bk-button>
                <bk-button
                    theme="default"
                    :disabled="saveLoading"
                    data-test-id="periodicEdit_form_cancelBtn"
                    @click="onCancelSave">
                    {{ $t('取消') }}
                </bk-button>
            </template>
        </div>
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
        name: 'PeriodicTaskCrate',
        components: {
            TaskParamEdit,
            NoData,
            CronRuleSelect,
            NotifyTypeConfig,
            NodePreview
        },
        mixins: [permission],
        props: [
            'taskId',
            'templateId',
            'projectId',
            'isCommon'
        ],
        data () {
            return {
                taskData: {
                    pipeline_tree: {},
                    constants: {}
                },
                taskLoading: false,
                formData: {
                    name: '',
                    is_latest: '',
                    task_template_name: '',
                    template_source: 'project',
                    schemeId: []
                },
                initFormData: {},
                templateData: {},
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
                                return this.templateId
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
                isTplDeleted: false, // 旧数据模板是否被删除
                hasDeleteScheme: false, // 是否存在执行方案被删除
                cronExpression: '*/30 * * * *' // 周期表达式
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'projectName': state => state.projectName
            }),
            isVariableEmpty () {
                return Object.keys(this.periodicConstants).length === 0
            },
            flowPermission () {
                return this.isCommon ? 'common_flow_create_periodic_task' : 'flow_create_periodic_task'
            },
            isLoading () {
                return this.taskLoading || this.templateDataLoading
            },
            includeNodes () {
                if (this.formData.is_latest !== null) return ''
                const { activities = {} } = this.taskData.pipeline_tree || {}
                const nodes = Object.values(activities).map(item => item.name)
                return nodes.join(',')
            },
            schemeSelectPlaceholder () {
                return this.templateId && !this.schemeList.length ? i18n.t('此流程无执行方案，无需选择') : i18n.t('请选择')
            },
            isSelectSchemeDisable () {
                return this.formData.is_latest !== true || !this.templateId || this.previewDataLoading || !this.schemeList.length
            },
            canvasData () {
                return formatCanvasData('preview', this.previewData)
            }
        },
        async created () {
            this.initFormData = tools.deepClone(this.formData)

            if (this.taskId) {
                await this.getPeriodicTaskData()
            }

            this.getTemplateData(this.templateId)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
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
                'getPeriodic'
            ]),
            ...mapActions('template/', [
                'loadTemplateData'
            ]),
            async getPeriodicTaskData () {
                try {
                    this.taskLoading = true
                    const resp = await this.getPeriodic({ taskId: this.taskId })
                    const cron = this.splitPeriodicCron(resp.cron)
                    this.taskData = { ...resp, cron }
                    this.cronExpression = cron
                    this.periodicConstants = tools.deepClone(resp.form)
                    console.log(this.cronExpression)
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.taskLoading = false
                }
            },
            async getTemplateData (id) {
                // 获取模板详情
                try {
                    this.templateDataLoading = true
                    const params = { templateId: id, common: this.isCommon }
                    const templateData = await this.loadTemplateData(params)
                    // 获取流程模板的通知配置
                    const { notify_receivers, notify_type } = templateData
                    this.notifyType = [notify_type.success.slice(0), notify_type.fail.slice(0)]
                    const receiverGroup = JSON.parse(notify_receivers).receiver_group
                    this.receiverGroup = receiverGroup && receiverGroup.slice(0)
                    const pipelineDate = JSON.parse(templateData.pipeline_tree)
                    this.selectedNodes = Object.keys(pipelineDate.activities)
                    this.templateData = Object.assign({}, templateData, { pipeline_tree: pipelineDate })
                    // 判断当前模板是否有创建权限
                    await this.getCreatePeriodicTaskPerm(id)
                    // 获取模板对应的执行方案
                    await this.getTemplateScheme()
                    if (!this.taskId) { // 新建
                        this.formData.schemeId = this.schemeList.length ? [0] : []
                        await this.getPreviewNodeData(id, templateData.version, true)
                    } else if (this.formData.schemeId.length && this.formData.is_latest) {
                        // 只有最新流程才允许选择执行方案
                        this.onSelectScheme(this.formData.schemeId, [], false)
                    }
                } catch (e) {
                    // 判断模板是否为删除
                    if (e.status === 404 && this.taskId) {
                        this.isTplDeleted = true
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
            async getCreatePeriodicTaskPerm (templateId) {
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
                                id: this.projectId,
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
            async getTemplateScheme () {
                this.schemeLoading = true
                try {
                    const defaultScheme = await this.loadDefaultSchemeList()
                    const data = {
                        isCommon: this.isCommon || undefined,
                        project_id: this.isCommon ? undefined : this.projectId,
                        template_id: this.templateId
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
                        if (this.taskId) {
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
                        project_id: this.isCommon ? undefined : this.projectId,
                        template_id: this.templateId,
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
                const version = this.formData.is_latest ? latestVersion : this.taskData.template_version
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
                    const { template_id: id, task_template_name: name, template_version: version } = this.taskData
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
                                    value: this.taskData.constants[cur.key]?.value ?? cur.value
                                }
                                // 如果为元变量并且没有meta字段时自动补充上
                                if (this.taskId && cur.is_meta && !('meta' in cur)) {
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
                        template_id: this.templateId,
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
            onCancelSave () {
                this.postMessage()
            },
            // 周期任务保存
            onPeriodicConfirm () {
                if (this.hasNoCreatePerm) {
                    const { id, name, auth_actions } = this.templateData
                    const resourceData = {
                        [this.isCommon ? 'common_flow' : 'flow']: [{ id, name }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission([this.flowPermission], auth_actions, resourceData)
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
                    const { schemeId } = this.formData
                    let previewData
                    // 如果不存在执行方案或为<不使用执行方案>时使用
                    if (!schemeId.length || schemeId[0] === 0) {
                        previewData = tools.deepClone(this.templateData.pipeline_tree)
                    } else {
                        previewData = this.previewData
                    }
                    const pipelineData = {
                        ...previewData,
                        constants
                    }

                    if (this.taskId) { // 确认编辑周期任务
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
                        this.postMessage()
                    } else if (this.isUpdatePipelineTree) { // pipeline_tree被更新替换，调update接口
                        const schemeIds = this.formData.schemeId.filter(id => id)
                        const params = {
                            taskId: this.taskId,
                            project: this.projectId,
                            cron: jsonCron,
                            name: this.formData.name,
                            template_id: this.templateId,
                            template_scheme_ids: schemeIds,
                            pipeline_tree: JSON.stringify(pipelineData),
                            template_source: this.isCommon ? 'common' : undefined
                        }
                        await this.updatePeriodicTask(params)
                        this.postMessage(this.taskId)
                    } else { // 修改周期任务部分配置，调patch接口
                        const constantsData = Object.values(pipelineData.constants).reduce((acc, cur) => {
                            acc[cur.key] = cur.value
                            return acc
                        }, {})
                        const params = {
                            taskId: this.taskId,
                            project: this.projectId,
                            name: this.formData.name,
                            cron: jsonCron,
                            constants: constantsData
                        }
                        await this.updatePeriodicPartial(params)
                        this.postMessage(this.taskId)
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
                    templateId: this.templateId,
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
                    this.postMessage()
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
                const sameCronDate = !this.taskData.cron || this.taskData.cron === this.cronExpression
                const same = sameFormData && sameCronDate && sameRenderData
                return same
            },
            splitPeriodicCron (cron) {
                const values = cron.split('(')[0].trim().split(' ')
                const keys = cron.split('(')[1].split(')')[0].split('/')
                const cronMap = {}
                keys.forEach((key, index) => {
                    cronMap[key] = values[index] || '*'
                })
                const cronRule = cronMap['m'] + ' ' + cronMap['h'] + ' ' + cronMap['dM'] + ' ' + cronMap['MY'] + ' ' + cronMap['d']
                return cronRule
            },
            postMessage (periodicId) {
                // 向父页面发送事件
                window.parent.postMessage({
                    eventName: 'createPeriodicTaskEvent',
                    data: { periodic_id: periodicId }
                }, '*')
            }
        }
    }
</script>

<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.create-periodic-task {
    height: 100%;
    background: #fff;
    .content-wrapper {
        height: calc(100% - 48px);
        overflow-y: auto;
        @include scrollbar;
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
        /deep/.bk-form {
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
                .flow-type-select {
                    flex: 0 0 150px;
                    margin-right: 15px;
                }
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
            .scheme-form-item {
                .tooltips-icon {
                    right: 132px !important;
                }
            }
        }
        /deep/.notify-type-wrapper {
            .bk-form-content {
                margin-left: 90px !important;
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
        height: calc(100% - 48px);
        margin-bottom: 25px;
    }
}
</style>
