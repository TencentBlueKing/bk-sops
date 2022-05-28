/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
                    <span @click="isPreview = false">{{ $t('编辑周期任务') }}</span>
                    <i class="common-icon-angle-right"></i>
                    {{ previewScheme }}
                </div>
                <template v-else>{{ isEdit ? $t('编辑周期任务') : $t('创建周期任务') }}</template>
            </div>
            <template slot="content" v-if="isPreview">
                <NodePreview
                    ref="nodePreview"
                    :preview-data-loading="previewDataLoading"
                    :canvas-data="formatCanvasData('perview', previewData)"
                    :preview-bread="previewBread"
                    @onNodeClick="onNodeClick"
                    @onSelectSubflow="onSelectSubFlow">
                </NodePreview>
                <div class="btn-footer">
                    <bk-button @click="isPreview = false">{{ $t('返回编辑') }}</bk-button>
                </div>
            </template>
            <div slot="content" v-show="!isPreview">
                <section class="config-section">
                    <p class="title">{{$t('基础信息')}}</p>
                    <bk-form
                        :label-width="90"
                        ref="basicConfigForm"
                        :rules="rules"
                        :model="formData">
                        <bk-form-item :label="$t('任务名称')" :required="true" property="taskName">
                            <bk-input :disabled="isEdit" v-model="formData.name"></bk-input>
                        </bk-form-item>
                        <bk-form-item :label="$t('流程')" :required="true" property="flow">
                            <div v-if="isEdit" class="select-box">
                                <div class="select-wrapper">
                                    <p>
                                        <span v-if="formData.is_latest === false" class="update-tip">[{{ $t('流程有更新') }}]</span>
                                        {{ formData.task_template_name }}
                                    </p>
                                    <i class="bk-icon icon-angle-down"></i>
                                </div>
                                <bk-button
                                    v-if="formData.is_latest === false"
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
                                v-model="formData.template_id"
                                :searchable="true"
                                :placeholder="$t('请选择')"
                                :clearable="true"
                                v-bkloading="{ isLoading: templateLoading, size: 'small', extCls: 'template-loading' }"
                                @clear="onClearTemplate"
                                @selected="onSelectTemplate">
                                <bk-option
                                    v-for="(option, index) in templateList"
                                    :key="index"
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
                        <bk-form-item v-if="!isEdit" :label="$t('执行方案')" property="scheme">
                            <div class="scheme-wrapper">
                                <bk-select
                                    v-model="formData.scheme"
                                    :searchable="true"
                                    :placeholder="$t('请选择')"
                                    :clearable="true"
                                    :disabled="!formData.template_id"
                                    :is-loading="isLoading || schemeLoading"
                                    @clear="onClearScheme"
                                    @selected="onSelectScheme">
                                    <bk-option
                                        v-for="(option, index) in schemeList"
                                        :key="index"
                                        :id="option.id"
                                        :name="option.name">
                                        <span>{{ option.name }}</span>
                                        <span v-if="option.isDefault" class="default-label">{{$t('默认')}}</span>
                                    </bk-option>
                                </bk-select>
                                <bk-button
                                    theme="primary"
                                    :disabled="isLoading || !formData.template_id"
                                    @click="togglePreviewMode">
                                    {{ $t('预览') }}
                                </bk-button>
                            </div>
                        </bk-form-item>
                        <bk-form-item :label="$t('周期表达式')" :required="true" property="loop">
                            <LoopRuleSelect
                                ref="loopRuleSelect"
                                class="loop-rule"
                                :manual-input-value="cron" />
                        </bk-form-item>
                    </bk-form>
                </section>
                <section class="config-section">
                    <p class="title">
                        <span>{{ $t('通知') }}</span>
                        <span v-if="!isLoading && formData.template_id" class="tip-desc">
                            {{ $t('通知方式统一在流程基础信息管理。如需修改，请') }}
                            <a
                                class="link"
                                @click="getJumpUrl()">
                                {{ $t('前往流程') }}
                            </a>
                        </span>
                    </p>
                    <NotifyTypeConfig
                        :notify-type-label="$t('启动失败') + ' ' + $t('通知方式')"
                        :label-width="87"
                        :table-width="570"
                        :notify-type="notifyType"
                        :is-view-mode="true"
                        :notify-type-list="[{ text: $t('任务状态') }]"
                        :receiver-group="receiverGroup">
                    </NotifyTypeConfig>
                </section>
                <section class="config-section mb20">
                    <p class="title">{{$t('执行参数')}}</p>
                    <div v-bkloading="{ isLoading: isLoading || previewDataLoading }">
                        <NoData v-if="isVariableEmpty"></NoData>
                        <TaskParamEdit
                            v-else
                            ref="TaskParamEdit"
                            class="task-param-edit"
                            :constants="periodicConstants">
                        </TaskParamEdit>
                    </div>
                </section>
                <div class="btn-footer">
                    <bk-button
                        theme="primary"
                        :loading="saveLoading"
                        :disabled="isLoading || previewDataLoading"
                        data-test-id="periodicList_form_saveBtn"
                        @click="onPeriodicConfirm">
                        {{ isEdit ? $t('保存') : $t('创建') }}
                    </bk-button>
                    <bk-button
                        theme="default"
                        :disabled="saveLoading"
                        data-test-id="periodicList_form_cancelBtn"
                        @click="onModifyPeriodicCancel">
                        {{ $t('取消') }}
                    </bk-button>
                </div>
            </div>
        </bk-sideslider>
        <bk-dialog
            width="400"
            ext-cls="edit-clocked-dialog"
            :theme="'primary'"
            :mask-close="false"
            :show-footer="false"
            :value="isShowDialog"
            @cancel="isShowDialog = false">
            <div class="edit-clocked-dialog">
                <div class="save-tips">{{ $t('保存已修改的信息吗？') }}</div>
                <div class="action-wrapper">
                    <bk-button theme="primary" :loading="saveLoading" @click="onPeriodicConfirm">{{ $t('保存') }}</bk-button>
                    <bk-button theme="default" :disabled="saveLoading" @click="onModifyPeriodicCancel">{{ $t('不保存') }}</bk-button>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import { PERIODIC_REG, NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import LoopRuleSelect from '@/components/common/Individualization/loopRuleSelect.vue'
    import TaskParamEdit from '@/pages/task/TaskParamEdit.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import NotifyTypeConfig from '@/pages/template/TemplateEdit/TemplateSetting/NotifyTypeConfig.vue'
    import permission from '@/mixins/permission.js'
    import NodePreview from '@/pages/task/NodePreview.vue'

    export default {
        name: 'ModifyPeriodicDialog',
        components: {
            TaskParamEdit,
            NoData,
            LoopRuleSelect,
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
                template_id = ''
            } = this.curRow
            return {
                formData: {
                    name,
                    is_latest,
                    task_template_name,
                    template_id,
                    scheme: ''
                },
                templateData: {},
                templateLoading: false,
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
                saveLoading: false,
                periodicRule: {
                    required: true,
                    regex: PERIODIC_REG
                },
                rules: {
                    taskName: [
                        {
                            required: true,
                            validator: (val) => {
                                return this.formData.name
                            },
                            message: i18n.t('任务名称不能为空'),
                            trigger: 'change'
                        },
                        {
                            validator: (val) => {
                                return NAME_REG.test(this.formData.name)
                            },
                            message: i18n.t('任务名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'change'
                        },
                        {
                            validator: (val) => {
                                return STRING_LENGTH.TASK_NAME_MAX_LENGTH > this.formData.name.length
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
                            trigger: 'change'
                        }
                    ]
                },
                periodicCronImg: require('@/assets/images/' + i18n.t('task-zh') + '.png'),
                periodicConstants: {},
                isUpdateTask: false, // 标识是否为更新任务
                isShowDialog: false,
                updateLoading: false
            }
        },
        computed: {
            isVariableEmpty () {
                return Object.keys(this.periodicConstants).length === 0
            },
            isCommon () {
                return this.curRow.template_source === 'common'
            },
            previewScheme () {
                const schemeId = this.formData.scheme
                if (!schemeId) return ''
                const schemeInfo = this.schemeList.find(item => item.id === schemeId)
                return i18n.t('预览') + '：' + schemeInfo.name
            },
            isLoading () {
                return this.templateLoading || this.templateDataLoading
            }
        },
        created () {
            if (this.isEdit) {
                this.periodicConstants = tools.deepClone(this.constants)
                const id = this.curRow.template_id
                this.onSelectTemplate(id)
            } else {
                this.getTemplateList()
            }
        },
        methods: {
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
                'createPeriodic'
            ]),
            ...mapActions('template/', [
                'loadTemplateData'
            ]),
            async getTemplateList () {
                this.templateLoading = true
                try {
                    const templateListData = await this.loadTemplateList({ project__id: this.project_id })
                    this.templateList = templateListData.results
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLoading = false
                }
            },
            onTempSelect (applyPerm = [], selectInfo) {
                if (!this.hasPermission(applyPerm, selectInfo.auth_actions)) {
                    const permissionData = {
                        project: [{
                            id: this.project_id,
                            name: this.formData.task_template_name
                        }],
                        flow: [selectInfo]
                    }
                    this.applyForPermission(applyPerm, selectInfo.auth_actions, permissionData)
                }
            },
            onClearTemplate () {
                this.formData.scheme = ''
                this.schemeList = []
                this.constants = {}
            },
            async onSelectTemplate (id) {
                // 获取模板详情
                try {
                    this.templateDataLoading = true
                    const params = { templateId: id, common: this.isCommon }
                    const templateData = await this.loadTemplateData(params)
                    // 获取流程模板的通知配置
                    const { notify_receivers, notify_type } = templateData
                    this.notifyType = [notify_type.success.slice(0), notify_type.fail.slice(0)]
                    this.receiverGroup = JSON.parse(notify_receivers).receiver_group.slice(0)
                    const pipelineDate = JSON.parse(templateData.pipeline_tree)
                    this.selectedNodes = Object.keys(pipelineDate.activities)
                    this.templateData = Object.assign({}, templateData, { pipeline_tree: pipelineDate })
                    // 新建模式拉取预览数据和流程对应的执行方案
                    if (!this.isEdit) {
                        const templateInfo = this.templateList.find(item => item.id === id)
                        await this.getPreviewNodeData(id, templateInfo.version, true)
                        // 获取模板对应的执行方案
                        this.getTemplateScheme()
                    }
                } catch (e) {
                    console.warn(e)
                } finally {
                    this.templateDataLoading = false
                }
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
                    this.schemeLoading = false
                } catch (e) {
                    console.log(e)
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
            onSelectScheme (id) {
                this.formData.scheme = Number(id)
                const schemeInfo = this.schemeList.find(item => item.id === id)
                this.selectedNodes = JSON.parse(schemeInfo.data)
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
                    common: this.isCommon,
                    version
                }
                try {
                    const resp = await this.loadPreviewNodeData(params)
                    if (resp.result) {
                        this.previewData = resp.data.pipeline_tree
                        if (updateConstants) {
                            this.periodicConstants = tools.deepClone(this.previewData.constants)
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
                const nodeList = Object.keys(activities)
                nodeList.forEach(id => {
                    if (this.selectedNodes.indexOf(id) === -1) {
                        nodes.push(id)
                    }
                })
                return nodes
            },
            /**
             * 格式化pipelineTree的数据，只输出一部分数据
             * @params {Object} data  需要格式化的pipelineTree
             * @return {Object} {lines（线段连接）, locations（节点默认都被选中）, branchConditions（分支条件）}
             */
            formatCanvasData (mode, data) {
                const { line, location, gateways, activities } = data
                const branchConditions = {}
                for (const gKey in gateways) {
                    const item = gateways[gKey]
                    if (item.conditions) {
                        branchConditions[item.id] = Object.assign({}, item.conditions)
                    }
                }
                return {
                    lines: line,
                    locations: location.map(item => {
                        const code = item.type === 'tasknode' ? activities[item.id].component.code : ''
                        return { ...item, mode, code }
                    }),
                    branchConditions
                }
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
            onModifyPeriodicCancel () {
                this.isShowDialog = false
                this.$emit('onModifyPeriodicCancel')
            },
            onPeriodicConfirm () {
                const loopRule = this.$refs.loopRuleSelect.validationExpression()
                if (!loopRule.check) return
                const paramEditComp = this.$refs.TaskParamEdit
                this.$refs.basicConfigForm.validate().then(async (result) => {
                    let formValid = true
                    let constantsValue = ''
                    if (paramEditComp) {
                        const formData = await paramEditComp.getVariableData()
                        constantsValue = Object.keys(formData).reduce((acc, key) => {
                            acc[key] = formData[key]['value']
                            return acc
                        }, {})
                        formValid = paramEditComp.validate()
                    }
                    const cronArray = loopRule.rule.split(' ')
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
                    this.saveLoading = !this.isUpdateTask
                    const jsonCron = {
                        'minute': cronArray[0],
                        'hour': cronArray[1],
                        'day_of_week': cronArray[2],
                        'day_of_month': cronArray[3],
                        'month_of_year': cronArray[4]
                    }
                    if (this.isUpdateTask) { // 更新流程模板
                        this.confirmUpdatedTask(jsonCron, constantsValue)
                        return
                    }

                    if (this.isEdit) { // 确认编辑周期任务
                        this.onModifyPeriodicConfirm(jsonCron, loopRule, constantsValue)
                    } else { // 确认创建周期任务
                        this.onCreatePeriodicConfirm(jsonCron, constantsValue)
                    }
                })
            },
            onModifyPeriodicConfirm (jsonCron, loopRule, constantsValue) {
                try {
                    const cronData = {
                        'taskId': this.taskId,
                        'cron': jsonCron
                    }
                    if (this.cron === loopRule.rule && constantsValue === '') {
                        // 没有改变表达式，且没有ramdomform内容
                        this.dialogFooterData[0].loading = false
                        this.$emit('onModifyPeriodicCancel')
                    } else if (constantsValue === '') {
                        this.modifyCron(cronData)
                    } else {
                        const constantsData = {
                            'taskId': this.taskId,
                            'constants': constantsValue
                        }
                        this.modifyPeriodic(cronData, constantsData)
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.saveLoading = false
                }
            },
            modifyPeriodic (cronData, constantsData) {
                try {
                    Promise.all([this.modifyPeriodicConstants(constantsData), this.modifyPeriodicCron(cronData)]).then((values) => {
                        if (values[0].result && values[1].result) {
                            this.$bkMessage({
                                'message': i18n.t('修改周期任务信息成功'),
                                'theme': 'success'
                            })
                        } else if (values[0].result) {
                            this.$bkMessage({
                                'message': i18n.t('修改周期任务参数成功，但表达式修改未成功，请重试'),
                                'theme': 'warning'
                            })
                        } else if (values[1].result) {
                            this.$bkMessage({
                                'message': i18n.t('修改周期任务表达式成功，但任务参数未修改成功，请重试'),
                                'theme': 'warning'
                            })
                        } else {
                            this.$bkMessage({
                                'message': i18n.t('修改周期任务失败，请联系管理员'),
                                'theme': 'error'
                            })
                        }
                        this.dialogFooterData[0].loading = false
                        this.$emit('onModifyPeriodicConfirm')
                    })
                } catch (e) {
                    console.log(e)
                }
            },
            async modifyCron (cronData) {
                const result = await this.modifyPeriodicCron(cronData)
                if (result.result) {
                    this.$bkMessage({
                        'message': i18n.t('修改周期任务表达式成功'),
                        'theme': 'success'
                    })
                } else {
                    this.$bkMessage({
                        'message': i18n.t('修改周期任务失败，请联系管理员'),
                        'theme': 'error'
                    })
                }
                this.saveLoading = false
                this.$emit('onModifyPeriodicConfirm')
            },
            onUpdatePeriodicTask () {
                this.isUpdateTask = true
                // 借用保存方法的周期校验和执行参数校验
                this.onPeriodicConfirm()
            },
            // 更新流程模板
            async confirmUpdatedTask (cronData, constantsData) {
                try {
                    this.updateLoading = true
                    const { pipeline_tree, template_id } = this.curRow
                    const pipelineDate = Object.assign({}, pipeline_tree, { constants: constantsData })
                    const params = {
                        taskId: this.taskId,
                        project: this.project_id,
                        cron: cronData,
                        name: this.formData.name,
                        template_id,
                        pipeline_tree: JSON.stringify(pipelineDate)
                    }
                    await this.updatePeriodicTask(params)
                    this.$bkMessage({
                        'message': i18n.t('流程更新成功'),
                        'theme': 'success'
                    })
                    this.formData.is_latest = true
                } catch (e) {
                    console.log(e)
                } finally {
                    this.updateLoading = false
                    this.isUpdateTask = false
                }
            },
            // 创建周期任务
            async onCreatePeriodicConfirm (cron, constantsValue) {
                const constants = Object.values(this.previewData.constants).reduce((acc, cur) => {
                    acc[cur.key] = { ...cur, value: constantsValue[cur.key] }
                    return acc
                }, {})
                const execData = {
                    ...this.templateData.pipeline_tree,
                    constants
                }
                const data = {
                    'name': this.formData.name,
                    'cron': cron,
                    'templateId': this.formData.template_id,
                    'execData': JSON.stringify(execData)
                }
                try {
                    const response = await this.createPeriodic(data)
                    if (!response.result) return
                    this.$bkMessage({
                        'message': i18n.t('创建周期任务成功'),
                        'theme': 'success'
                    })
                    this.$emit('onModifyPeriodicCancel', true)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.saveLoading = false
                }
            },
            onCloseConfig () {
                const taskParamEdit = this.$refs.TaskParamEdit
                const sameRenderData = taskParamEdit ? taskParamEdit.judgeDataEqual() : true
                const sameFormDate = Object.keys(this.formData).every(key => {
                    if (!(key in this.curRow) && !this.formData[key]) {
                        return true
                    } else if (this.curRow[key] === this.formData[key]) {
                        return true
                    }
                })
                const loopRule = this.$refs.loopRuleSelect.validationExpression()
                const sameCronDate = this.cron ? this.cron === loopRule.rule : true
                const same = sameFormDate && sameCronDate && sameRenderData
                if (same) {
                    this.onModifyPeriodicCancel()
                } else {
                    this.isShowDialog = true
                }
            }
        }
    }
</script>

<style lang="scss">
    .edit-clocked-dialog {
        .bk-dialog-body {
            padding: 0;
        }
        .edit-clocked-dialog {
            padding: 20px 0 40px 0;
            text-align: center;
            .save-tips {
                font-size: 24px;
                margin-bottom: 30px;
                padding: 0 10px;
            }
            .action-wrapper .bk-button {
                margin-right: 6px;
            }
        }
    }
</style>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

/deep/.bk-sideslider-content {
    height: calc(100% - 60px);
    position: relative;
    padding: 0 31px 48px 28px;
    overflow-y: auto;
    @include scrollbar;
}
/deep/.bk-sideslider-title {
    color: #313238;
    font-size: 16px;
    font-weight: normal;
}
/deep/.btn-footer {
    z-index: 2;
}
.loop-rule {
    width: 530px;
}

.config-section {
    .title {
        color: #313238;
        font-size: 14px;
        line-height: 19px;
        padding: 18px 0 11px;
        margin-bottom: 24px;
        border-bottom: 1px solid #cacedb;
        .tip-desc {
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
        .loop-rule-select {
            width: 555px;
        }
        .rule-tips {
            top: 6px;
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
    /deep/.notify-type-wrapper {
        .bk-form-content {
            margin-left: 90px !important;
        }
    }
    /deep/.template-loading {
        .bk-loading-wrapper {
            top: 65%;
        }
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
/deep/.no-data-wrapper {
    margin: 150px 0;
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
        margin: 0 5px;
    }
}
.node-preview-wrapper {
    height: calc(100% - 50px);
    margin: 25px 0;
}
</style>
