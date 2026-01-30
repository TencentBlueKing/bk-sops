<template>
    <div class="edit-clocked-task" data-test-id="clockedList_form_editTask">
        <bk-sideslider
            :width="800"
            ext-cls="edit-clocked-sideslider"
            :is-show.sync="isShowSideslider"
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
                    :common="false"
                    @onNodeClick="onNodeClick"
                    @onSelectSubflow="onSelectSubFlow">
                </NodePreview>
                <div class="btn-footer">
                    <bk-button @click="isPreview = false">{{ $t('返回编辑') }}</bk-button>
                </div>
            </template>
            <div slot="content" v-show="!isPreview">
                <bk-alert type="info" :title="$t('计划任务在执行时获取最新的流程和执行方案数据创建任务，流程和方案变更将影响未执行的计划任务，如增加参数可能导致计划任务启动失败。')"></bk-alert>
                <section class="config-section">
                    <p class="title mt0">{{$t('流程')}}</p>
                    <bk-form
                        :label-width="90"
                        ref="basicConfigForm"
                        :model="formData"
                        :rules="rules">
                        <bk-form-item :label="$t('流程模板')" :required="true" property="flow" data-test-id="clockedEdit_form_selectTemplate">
                            <div
                                v-if="isTplDeleted ? type === 'edit' : type !== 'create'"
                                class="select-box"
                                v-bkloading="{ isLoading: isLoading, size: 'small' }">
                                {{ curRow.template_name }}
                                <i class="bk-icon icon-angle-down"></i>
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
                                :allow-enter="false"
                                v-bkloading="{ isLoading: templateLoading, size: 'small', extCls: 'template-loading' }"
                                @clear="onClearTemplate"
                                @selected="onSelectTemplate"
                                @scroll-end="onSelectScrollLoad">
                                <bk-option
                                    v-for="option in templateList"
                                    :key="option.id"
                                    :disabled="!hasPermission(['flow_view'], option.auth_actions)"
                                    :id="option.id"
                                    :name="option.name">
                                    <p
                                        :title="option.name"
                                        v-cursor="{ active: !hasPermission(['flow_view'], option.auth_actions) }"
                                        @click="onTempSelect(['flow_view'], option)">
                                        {{ option.name }}
                                    </p>
                                </bk-option>
                            </bk-select>
                        </bk-form-item>
                        <bk-form-item
                            v-if="isTplDeleted ? type === 'clone' : !isPreview"
                            class="scheme-form-item"
                            data-test-id="clockedEdit_form_selectScheme"
                            :label="isLatest ? $t('执行方案') : $t('已排除节点')"
                            property="schemeId">
                            <div class="scheme-wrapper">
                                <bk-select
                                    v-if="isLatest"
                                    v-model="formData.schemeId"
                                    :searchable="true"
                                    :placeholder="schemeSelectPlaceholder"
                                    :clearable="false"
                                    :multiple="true"
                                    :disabled="!formData.template_id || !schemeList.length"
                                    :loading="isLoading || schemeLoading"
                                    @clear="onClearScheme"
                                    @selected="onSelectScheme">
                                    <bk-option
                                        v-for="(option, index) in schemeList"
                                        :key="index"
                                        :id="option.id"
                                        :name="option.name">
                                        <span>{{ option.name }}</span>
                                        <span v-if="option.isDefault" class="default-label">{{$t('默认')}}</span>
                                        <i v-if="formData.schemeId.includes(option.id)" class="bk-icon icon-check-line"></i>
                                    </bk-option>
                                </bk-select>
                                <p v-else class="exclude-wrapper" v-bk-overflow-tips>
                                    {{ excludeNodes }}
                                </p>
                                <bk-button
                                    v-if="!isTplDeleted"
                                    theme="default"
                                    :disabled="isLoading || !formData.template_id"
                                    @click="togglePreviewMode">
                                    {{ $t('预览') }}
                                </bk-button>
                            </div>
                            <p v-if="!isLatest" class="schema-disable-tip">
                                {{ $t('当前任务为旧数据，仅记录已排除节点，可重选执行方案获得跟随执行方案更新能力') }}
                            </p>
                            <p v-if="type === 'clone' && ('exclude_task_nodes_id' in curRow.task_parameters)" class="schema-disable-tip">
                                {{ $t('旧数据计划任务克隆，不再记录已排除节点，请重选执行方案') }}
                            </p>
                            <p v-if="hasDeleteScheme" class="schema-disable-tip">
                                {{ $t('选中的执行方案被删除，请重新选择执行方案') }}
                            </p>
                        </bk-form-item>
                        <p class="title">{{$t('任务信息')}}</p>
                        <bk-form-item :label="$t('计划名称')" :required="true" property="taskName" data-test-id="clockedEdit_form_taskName">
                            <bk-input
                                :clearable="true"
                                v-model="formData.task_name"
                                :maxlength="stringLength.TASK_NAME_MAX_LENGTH"
                                :show-word-limit="true">
                            </bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('任务时区')" :required="true" property="taskTimezone" data-test-id="clockedEdit_form_taskTimezone">
                            <TimezonePicker
                                v-model="localSelectTimezone"
                                @update:value="handleTimezoneChange"
                            />
                        </bk-form-item>
                        <bk-form-item :label="$t('启动时间')" :required="true" property="startTime" data-test-id="clockedEdit_form_startTime">
                            <bk-date-picker
                                :value="formData.plan_start_time"
                                :placeholder="`${$t('请选择启动时间')}`"
                                :clearable="false"
                                data-test-id="clockedList_form_startTime"
                                :type="'datetime'"
                                :options="pickerOptions"
                                @change="onPickerChange">
                            </bk-date-picker>
                            <span class="time-zone">{{ locTimeZone }}</span>
                        </bk-form-item>
                    </bk-form>
                </section>
                <section class="config-section">
                    <p class="title">{{$t('参数信息')}}</p>
                    <TaskParamEdit
                        v-bkloading="{ isLoading: isLoading || previewDataLoading, opacity: 1, zIndex: 100 }"
                        class="task-param-wrapper"
                        ref="TaskParamEdit"
                        :constants="constants">
                    </TaskParamEdit>
                </section>
                <section class="config-section mb20">
                    <p class="title">
                        <span>{{ $t('通知') }}</span>
                        <span v-if="!isLoading && formData.template_id && !isTplDeleted" class="tip-desc">
                            {{ $t('通知方式统一在流程基础信息管理。如需修改，请') }}
                            <a
                                class="link"
                                data-test-id="clockedEdit_form_jumpFlow"
                                @click="getJumpUrl()">
                                {{ $t('前往流程') }}
                            </a>
                        </span>
                    </p>
                    <div v-bkloading="{ isLoading: isLoading || schemeLoading, opacity: 1, zIndex: 100 }">
                        <NotifyTypeConfig
                            v-if="formData.template_id && !templateDataLoading"
                            :notify-type-label="$t('通知方式')"
                            :label-width="87"
                            :table-width="570"
                            :notify-type="notifyType"
                            :project_id="project_id"
                            :is-view-mode="true"
                            :notify-type-list="[{ text: $t('任务状态') }]"
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
                        data-test-id="clockedEdit_form_saveBtn"
                        :disabled="isLoading || previewDataLoading"
                        :class="{ 'btn-permission-disable': hasNoCreatePerm }"
                        v-cursor="{ active: hasNoCreatePerm }"
                        @click="onClockedConfirm">
                        {{ type === 'edit' ? $t('保存') : $t('提交') }}
                    </bk-button>
                    <bk-button
                        theme="default"
                        :disabled="saveLoading"
                        data-test-id="clockedEdit_form_cancelBtn"
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
    import TaskParamEdit from '../TaskParamEdit.vue'
    import NotifyTypeConfig from '@/pages/template/TemplateEdit/TemplateSetting/NotifyTypeConfig.vue'
    import permission from '@/mixins/permission.js'
    import tools from '@/utils/tools.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NodePreview from '@/pages/task/NodePreview.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import { formatCanvasData } from '@/utils/checkDataType'
    import moment from 'moment-timezone'
    import { TimezonePicker } from '@blueking/date-picker/vue2'
    import '@blueking/date-picker/vue2/vue2.css'

    export default {
        components: {
            TaskParamEdit,
            NotifyTypeConfig,
            NodePreview,
            NoData,
            TimezonePicker
        },
        mixins: [permission],
        props: {
            type: {
                type: String,
                default: ''
            },
            project_id: {
                type: [String, Number]
            },
            isShowSideslider: {
                type: Boolean,
                default: false
            },
            curRow: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            const {
                task_name = '',
                plan_start_time = '',
                template_id = '',
                task_parameters = {}
            } = this.curRow
            const taskName = this.type === 'clone' ? task_name + '_clone' : task_name
            const startTime = plan_start_time.split('+')[0]
            const tempSchemeId = task_parameters.template_schemes_id || []
            const schemeId = this.type === 'create' ? [] : tempSchemeId.length ? tempSchemeId : []
            return {
                formData: {
                    template_id,
                    task_name: taskName,
                    plan_start_time: startTime,
                    schemeId
                },
                initFormData: {},
                stringLength: STRING_LENGTH,
                taskNameRule: {
                    required: true,
                    max: STRING_LENGTH.TASK_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                rules: {
                    taskName: [
                        {
                            required: true,
                            validator: (val) => {
                                return this.formData.task_name
                            },
                            message: i18n.t('任务名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return NAME_REG.test(this.formData.task_name)
                            },
                            message: i18n.t('任务名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return STRING_LENGTH.TASK_NAME_MAX_LENGTH >= this.formData.task_name.length
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
                    ],
                    startTime: [
                        {
                            required: true,
                            message: i18n.t('请选择启动时间'),
                            trigger: 'blur'
                        },
                        {
                            validator: () => {
                                return !this.isDateBeforeToday(this.formData.plan_start_time)
                            },
                            message: i18n.t('启动时间不能小于当前时间'),
                            trigger: 'blur'
                        }
                    ]
                },
                saveLoading: false,
                constants: {},
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
                notifyType: [[], []],
                receiverGroup: [],
                notifyTypeExtraInfo: {},
                totalPage: 1,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                },
                flowName: '',
                isTplDeleted: false, // 旧数据模板是否被删除
                hasDeleteScheme: false, // 是否存在执行方案被删除
                localSelectTimezone: window.TIMEZONE
            }
        },
        computed: {
            ...mapState('project', {
                'projectName': state => state.projectName
            }),
            ...mapState({
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            sameTimeStamp () {
                const initTimeStamp = new Date(this.curRow.plan_start_time).getTime()
                const curTimeStamp = new Date(this.formData.plan_start_time).getTime()
                return initTimeStamp === curTimeStamp && window.TIMEZONE === this.localSelectTimezone
            },
            sideSliderTitle () {
                return this.type === 'edit' ? i18n.t('编辑计划任务')
                    : this.type === 'create' ? i18n.t('新建计划任务')
                        : i18n.t('克隆计划任务')
            },
            previewScheme () {
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
            isLatest () {
                if (this.type !== 'edit' || !('exclude_task_nodes_id' in this.curRow.task_parameters)) {
                    return true
                }
                return false
            },
            excludeNodes () {
                if (this.isLatest) return ''
                const nodes = []
                const { exclude_task_nodes_id = [] } = this.curRow.task_parameters
                const { activities = {} } = this.templateData.pipeline_tree || {}
                exclude_task_nodes_id.forEach(id => {
                    if (activities[id]) {
                        nodes.push(activities[id].name)
                    }
                })
                return nodes.join(',') || ('<' + i18n.t('无') + '>')
            },
            hasNoCreatePerm () {
                const { id, auth_actions } = this.templateData
                return this.type === 'edit' || !id ? false : !this.hasPermission(['flow_create_clocked_task'], auth_actions)
            },
            schemeSelectPlaceholder () {
                return this.formData.template_id && !this.schemeList.length ? i18n.t('此流程无执行方案，无需选择') : i18n.t('请选择')
            },
            canvasData () {
                return formatCanvasData('preview', this.previewData)
            },
            locTimeZone () {
                // 使用全局变量 window.TIMEZONE，如果没有则使用浏览器本地时区
                if (this.localSelectTimezone) {
                    try {
                        const offset = moment().tz(this.localSelectTimezone).format('ZZ')
                        return offset
                    } catch (e) {
                        console.warn(e)
                        return new Date().toTimeString().slice(12, 17)
                    }
                }
                return new Date().toTimeString().slice(12, 17)
            },
            pickerOptions () {
                return {
                    disabledDate: (date) => {
                        return this.isDateBeforeToday(date)
                    }
                }
            }
        },
        created () {
            this.initFormData = tools.deepClone(this.formData)
            if (this.type !== 'create') {
                const id = this.curRow.template_id
                this.getTemplateData(id)
            } else {
                this.templateLoading = true
                this.getTemplateList()
            }
            this.onTplSearch = tools.debounce(this.handleTplSearch, 500)
        },
        methods: {
            ...mapActions('templateList', [
                'loadTemplateList'
            ]),
            ...mapActions('task/', [
                'loadPreviewNodeData',
                'loadTaskScheme',
                'getDefaultTaskScheme'
            ]),
            ...mapActions('clocked/', [
                'updateClocked',
                'createClocked'
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
                        pipeline_template__name__icontains: this.flowName || undefined
                    }
                    const templateListData = await this.loadTemplateList(params)
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
                this.constants = {}
            },
            async getTemplateData (id) {
                // 获取模板详情
                try {
                    this.templateDataLoading = true
                    const params = { templateId: id }
                    const templateData = await this.loadTemplateData(params)
                    // 获取流程模板的通知配置
                    const { notify_receivers, notify_type } = templateData
                    this.notifyType = [notify_type.success.slice(0), notify_type.fail.slice(0)]
                    const { receiver_group: receiverGroup, extra_info: extraInfo = {} } = JSON.parse(notify_receivers)
                    this.receiverGroup = receiverGroup && receiverGroup.slice(0)
                    this.notifyTypeExtraInfo = { ...extraInfo }
                    const pipelineDate = JSON.parse(templateData.pipeline_tree)
                    this.templateData = Object.assign({}, templateData, { pipeline_tree: pipelineDate })
                    // 获取模板对应的执行方案
                    await this.getTemplateScheme()
                    // 根据执行方案获取预览数据
                    this.onSelectScheme(this.formData.schemeId)
                } catch (e) {
                    // 判断模板是否为删除
                    if (e.status === 404) {
                        this.isTplDeleted = true
                        let message = ''
                        if (this.type === 'edit') {
                            message = i18n.t('对应流程模板已被删除，仅提供修改任务名称，任务执行时间')
                        } else if (this.type === 'clone') {
                            message = i18n.t('对应流程模板已被删除，请重新选择模板创建计划任务')
                            this.formData.template_id = ''
                            this.formData.schemeId = []
                            this.templateLoading = true
                            this.getTemplateList()
                        }
                        this.$bkMessage({
                            theme: 'warning',
                            message
                        })
                    }
                    console.warn(e)
                } finally {
                    this.templateDataLoading = false
                    this.initFormData = tools.deepClone(this.formData)
                }
            },
            onSelectTemplate (id) {
                // 清除表单错误提示
                this.$refs.basicConfigForm.clearError()
                // 自动填充任务名称
                const templateInfo = this.templateList.find(item => item.id === id)
                this.formData.task_name = templateInfo ? templateInfo.name + '_' + i18n.t('计划执行') : ''
                this.formData.schemeId = []
                this.getTemplateData(id)
            },
            async getTemplateScheme () {
                this.schemeLoading = true
                try {
                    const defaultScheme = await this.loadDefaultSchemeList()
                    const data = {
                        project_id: this.project_id,
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
                        const { schemeId } = this.formData
                        this.formData.schemeId = schemeId.length ? schemeId : [0]
                    }
                    if (this.type === 'create') {
                        this.formData.schemeId = this.schemeList.length ? [0] : []
                    } else if (this.formData.schemeId.length) {
                        // 执行方案被删除逻辑
                        this.hasDeleteScheme = false
                        this.formData.schemeId = this.formData.schemeId.filter(id => {
                            const isMatch = this.schemeList.some(item => item.id === Number(id))
                            if (isMatch) {
                                return true
                            } else {
                                this.hasDeleteScheme = true
                            }
                        })
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
                        project_id: this.project_id,
                        template_id: this.formData.template_id
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
            onClearScheme () {
                // 更新执行参数
                const { id: templateId, version } = this.templateData
                this.getPreviewNodeData(templateId, version, true)
            },
            onSelectScheme (ids, options = []) {
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
                const { id: templateId, version } = this.templateData
                this.getPreviewNodeData(templateId, version, true)
            },
            togglePreviewMode () {
                this.previewBread = []
                this.isPreview = true
                const { id, name, version } = this.templateData
                this.previewBread.push({ id, name, version })
                this.getPreviewNodeData(id, version)
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
                    version
                }
                try {
                    const resp = await this.loadPreviewNodeData(params)
                    if (resp.result) {
                        this.previewData = resp.data.pipeline_tree
                        if (updateConstants) {
                            const { constants = {} } = this.curRow.task_parameters || {}
                            this.constants = Object.values(this.previewData.constants).reduce((acc, cur) => {
                                acc[cur.key] = {
                                    ...cur,
                                    value: constants[cur.key] || cur.value
                                }
                                if (this.type !== 'create' && cur.is_meta && !cur.meta) {
                                    acc[cur.key]['meta'] = { ...cur }
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
                        template_id: this.formData.template_id
                    }
                })
                window.open(href, '_blank')
            },
            onPickerChange (date) {
                this.formData.plan_start_time = date
            },
            onClockedConfirm () {
                if (this.type === 'edit') {
                    this.onEditClockedConfirm()
                } else {
                    this.onCreateClockedConfirm()
                }
            },
            onEditClockedConfirm () {
                try {
                    this.$refs.basicConfigForm.validate().then(async (result) => {
                        const taskParamEdit = this.$refs.TaskParamEdit
                        const formValid = taskParamEdit.validate()
                        if (!result || !formValid) {
                            this.saveLoading = false
                            return
                        }
                        this.saveLoading = true
                        const { task_name, plan_start_time: time } = this.formData
                        const { constants, exclude_task_nodes_id } = this.curRow.task_parameters
                        const params = {
                            id: this.curRow.id,
                            task_name,
                            plan_start_time: this.sameTimeStamp ? undefined : time + this.locTimeZone,
                            task_parameters: {
                                constants: this.isTplDeleted && this.type === 'edit' ? constants : taskParamEdit ? taskParamEdit.renderData : {}
                            }
                        }
                        if (this.isLatest) {
                            const schemeIds = this.formData.schemeId.filter(item => item)
                            params.task_parameters['template_schemes_id'] = schemeIds
                        } else {
                            params.task_parameters['exclude_task_nodes_id'] = exclude_task_nodes_id
                        }
                        await this.updateClocked(params)
                        this.$bkMessage({
                            'message': i18n.t('编辑计划任务成功'),
                            'theme': 'success'
                        })
                        this.$emit('onSaveConfig')
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.saveLoading = false
                }
            },
            onCreateClockedConfirm () {
                if (this.hasNoCreatePerm) {
                    const { id, name, auth_actions } = this.templateData
                    const resourceData = {
                        flow: [{ id, name }],
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['flow_create_clocked_task'], auth_actions, resourceData)
                    return
                }
                this.$refs.basicConfigForm.validate().then(async (result) => {
                    const taskParamEdit = this.$refs.TaskParamEdit
                    const formValid = taskParamEdit.validate()
                    if (!result || !formValid) {
                        this.saveLoading = false
                        return
                    }
                    this.saveLoading = true
                    const schemeIds = this.formData.schemeId.filter(item => item)
                    const taskParams = {
                        constants: taskParamEdit.renderData || {},
                        template_schemes_id: schemeIds
                    }
                    const { task_name, template_id, plan_start_time } = this.formData
                    const data = {
                        id: this.curRow.id,
                        task_parameters: taskParams,
                        project_id: this.project_id,
                        task_name,
                        template_id,
                        template_name: this.templateData.name,
                        template_source: 'project',
                        notify_receivers: {
                            receiver_group: this.receiverGroup,
                            more_receiver: []
                        },
                        notify_type: {
                            success: this.notifyType[0],
                            fail: this.notifyType[1]
                        },
                        plan_start_time: plan_start_time + this.locTimeZone
                    }
                    try {
                        await this.createClocked(data)
                        this.$bkMessage({
                            'message': this.type === 'clone' ? i18n.t('克隆计划任务成功') : i18n.t('创建计划任务成功'),
                            'theme': 'success'
                        })
                        this.$emit('onSaveConfig')
                    } catch (e) {
                        console.log(e)
                    } finally {
                        this.saveLoading = false
                    }
                })
            },
            onCloseConfig () {
                const taskParamEdit = this.$refs.TaskParamEdit
                const sameRenderData = taskParamEdit ? taskParamEdit.judgeDataEqual() : true
                const sameFormDate = tools.isDataEqual(this.formData, this.initFormData)
                const same = sameFormDate && sameRenderData
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
            },
            onCancelSave () {
                this.constants = {}
                this.$emit('onCloseConfig')
            },
            /**
             * 检查日期是否在项目时区的今天之前
             * @param {Date|string} date - 要检查的日期
             * @returns {boolean} - 如果日期在今天之前返回 true，否则返回 false
             */
            isDateBeforeToday (date) {
                if (!date) {
                    return false
                }
                const timezone = this.localSelectTimezone || moment.tz.guess()
                // 将两个日期都转换到UTC进行比较，避免时区转换的日期偏移
                const todayInSelectedTimezone = moment().tz(timezone).startOf('day')
                const todayUTC = moment.utc(todayInSelectedTimezone.format('YYYY-MM-DD')).startOf('day')
                const testDateUTC = moment.utc(moment(date).format('YYYY-MM-DD')).startOf('day')
                const isBeforeToday = testDateUTC.isBefore(todayUTC)
                return isBeforeToday
            },
            handleTimezoneChange (value) {
                this.localSelectTimezone = value
            }
        }
    }
</script>

<style lang="scss" scoped>
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
    z-index: 100;
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
        .bk-label {
            font-size: 12px;
            color: #63656e;
        }
        .bk-form-content,
        .bk-date-picker {
            width: 598px;
        }
        .loop-rule-select {
            width: 555px;
        }
        .rule-tips {
            top: 6px;
        }
        .scheme-form-item {
            .tooltips-icon {
                right: 132px !important;
            }
        }
        .time-zone {
            position: relative;
            font-size: 12px;
            margin: 0 8px 0 -50px;
            color: #979ba5;
        }
        margin-bottom: 17px;
    }
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
.select-box {
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
    .icon-angle-down {
        position: absolute;
        right: 7px;
        top: 5px;
        font-size: 20px;
        color: #c4c6cc;
        cursor: not-allowed;
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
}
.schema-disable-tip {
    font-size: 12px;
    line-height: 15px;
    color: #ff9c01;
    margin-top: 8px;
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
.preview-header {
    display: flex;
    align-items: center;
    font-size: 14px;
    > span {
        color: #3a84ff;
        cursor: pointer;
    }
    .common-icon-angle-right {
        color: #c4c6cc;
        font-size: 20px;
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
