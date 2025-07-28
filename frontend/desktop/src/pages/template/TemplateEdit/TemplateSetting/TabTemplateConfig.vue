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
    <bk-sideslider
        :title="$t('基础信息')"
        :is-show="true"
        :width="800"
        :quick-close="true"
        :before-close="beforeClose">
        <div class="config-wrapper" slot="content">
            <bk-form
                ref="configForm"
                class="form-area"
                :model="formData"
                :label-width="120"
                :rules="rules">
                <section class="form-section">
                    <h4>{{ $t('基础') }}</h4>
                    <bk-form-item :property="'name'" :label="$t('流程名称')" :required="true" data-test-id="tabTemplateConfig_form_name">
                        <bk-input
                            :readonly="isViewMode"
                            ref="nameInput"
                            v-model.trim="formData.name"
                            :placeholder="$t('请输入流程模板名称')"
                            :maxlength="stringLength.TEMPLATE_NAME_MAX_LENGTH"
                            :show-word-limit="true">
                        </bk-input>
                    </bk-form-item>
                    <bk-form-item v-if="!common" :label="$t('标签')" data-test-id="tabTemplateConfig_form_label">
                        <bk-select
                            :key="templateLabels.length"
                            v-model="formData.labels"
                            ext-popover-cls="label-select-popover"
                            :display-tag="true"
                            :multiple="true"
                            searchable
                            :popover-options="{
                                onHide: () => !labelDialogShow
                            }"
                            :disabled="isViewMode"
                            @toggle="onSelectLabel">
                            <div class="label-select-content" v-bkloading="{ isLoading: templateLabelLoading }">
                                <bk-option
                                    v-for="(item, index) in templateLabels"
                                    :key="index"
                                    :id="item.id"
                                    :name="item.name">
                                    <div class="label-select-option">
                                        <span
                                            class="label-select-color"
                                            :style="{ background: item.color }">
                                        </span>
                                        <span>{{item.name}}</span>
                                        <i class="bk-option-icon bk-icon icon-check-1"></i>
                                    </div>
                                </bk-option>
                            </div>
                            <div slot="extension" class="label-select-extension">
                                <div
                                    class="add-label"
                                    data-test-id="tabTemplateConfig_form_editLabel"
                                    v-cursor="{ active: !hasPermission(['project_edit'], authActions) }"
                                    @click="onEditLabel">
                                    <i class="bk-icon icon-plus-circle"></i>
                                    <span>{{ $t('新建标签') }}</span>
                                </div>
                                <div
                                    class="label-manage"
                                    data-test-id="tabTemplateConfig_form_LabelManage"
                                    v-cursor="{ active: !hasPermission(['project_view'], authActions) }"
                                    @click="onManageLabel">
                                    <i class="common-icon-label"></i>
                                    <span>{{ $t('标签管理') }}</span>
                                </div>
                                <div
                                    class="refresh-label"
                                    data-test-id="process_list__refreshLabel"
                                    @click="$emit('updateTemplateLabelList')">
                                    <i class="bk-icon icon-right-turn-line"></i>
                                </div>
                            </div>
                        </bk-select>
                    </bk-form-item>
                    <bk-form-item property="category" :label="$t('分类')" data-test-id="tabTemplateConfig_form_category">
                        <bk-select
                            v-model="formData.category"
                            class="category-select"
                            :clearable="false"
                            :disabled="isViewMode"
                            @toggle="onSelectCategory">
                            <bk-option
                                v-for="(item, index) in taskCategories"
                                :key="index"
                                :id="item.id"
                                :data-test-id="`tabTemplateConfig_form_category${item.id}`"
                                :name="item.name">
                            </bk-option>
                        </bk-select>
                        <i
                            v-if="!common"
                            class="common-icon-info category-tips"
                            v-bk-tooltips="{
                                content: $t('模板分类即将下线，建议使用标签'),
                                placement: 'bottom',
                                theme: 'light',
                                showOnInit: true
                            }">
                        </i>
                    </bk-form-item>
                    <bk-form-item v-if="common" property="project_scope" :label="$t('可见范围')" :required="true"
                        data-test-id="tabTemplateConfig_form_projectScope">
                        <bk-checkbox
                            v-model="isOutermostBaseInfoAllProjectScope"
                            :disabled="isViewMode"
                            @change="handleBaseInfoSelectAllProjectScope">
                            {{ $t('全选') }}
                        </bk-checkbox>
                        <bk-select class="project-select"
                            :searchable="true"
                            :clearable="true"
                            :multiple="true"
                            :display-tag="true"
                            :auto-height="false"
                            :readonly="isViewMode"
                            ref="projectSelectRef"
                            :disabled="isOutermostBaseInfoAllProjectScope || isViewMode"
                            @change="handleBaseInfoProjectVisibleChange"
                            v-model="baseInfoProjectScopeList">
                            <bk-option-group
                                v-for="(group, index) in projects"
                                :name="group.name"
                                :key="index"
                                :show-select-all="true">
                                <bk-option v-for="item in group.children"
                                    :key="item.id"
                                    :id="item.id"
                                    :name="item.name">
                                </bk-option>
                            </bk-option-group>
                        </bk-select>
                    </bk-form-item>
                </section>
                <section class="form-section">
                    <h4>
                        <span>{{ $t('通知') }}</span>
                        <span class="tip-desc">{{ $t('选择通知方式后，将默认通知到任务执行人；可选择同时通知其他分组人员') }}</span>
                    </h4>
                    <NotifyTypeConfig
                        ref="notifyTypeConfig"
                        :label-width="120"
                        :notify-type="formData.notifyType"
                        :notify-type-list="[{ text: $t('任务状态') }]"
                        :notify-type-extra-info="formData.notifyTypeExtraInfo"
                        :receiver-group="formData.receiverGroup"
                        :project_id="projectId"
                        :common="common"
                        :is-view-mode="isViewMode"
                        @change="onSelectNotifyConfig">
                    </NotifyTypeConfig>
                </section>
                <section class="form-section">
                    <h4>{{ $t('其他') }}</h4>
                    <bk-form-item v-if="!common" :label="$t('执行代理人')" data-test-id="tabTemplateConfig_form_executorProxy">
                        <member-select
                            :multiple="false"
                            :disabled="isViewMode"
                            :placeholder="proxyPlaceholder"
                            :value="formData.executorProxy"
                            @change="onSelectedExecutorProxy">
                        </member-select>
                        <p v-if="isProxyValidateError" class="form-error-tip">{{ $t('代理人仅可设置为本人') }}</p>
                        <div class="executor-proxy-desc">
                            {{ $t('推荐留空使用') }}
                            <span
                                :class="{ 'project-management': authActions && authActions.length, 'disabled': isViewMode }"
                                @click="jumpProjectManagement">
                                {{ $t('项目执行代理人设置') }}
                            </span>
                            {{ $t('以便统一管理，也可单独配置流程执行代理人覆盖项目的设置') }}
                        </div>
                    </bk-form-item>
                    <bk-form-item property="notifyType" :label="$t('备注')" data-test-id="tabTemplateConfig_form_notifyType">
                        <bk-input type="textarea" :readonly="isViewMode" v-model.trim="formData.description" :rows="5" :placeholder="$t('请输入流程模板备注信息')"></bk-input>
                    </bk-form-item>
                    <bk-form-item property="defaultFlowType" :label="$t('任务类型偏好')" data-test-id="tabTemplateConfig_form_defaultFlowType">
                        <bk-select v-model="formData.defaultFlowType" :clearable="false" :disabled="isViewMode">
                            <bk-option id="common" :name="$t('常规')"></bk-option>
                            <bk-option id="common_func" :name="$t('task_职能化')"></bk-option>
                        </bk-select>
                    </bk-form-item>
                </section>
            </bk-form>
            <div class="btn-wrap">
                <bk-button v-if="!isViewMode" class="save-btn" theme="primary" data-test-id="tabTemplateConfig_form_saveBtn" @click="onSaveConfig">{{ $t('确定') }}</bk-button>
                <bk-button theme="default" data-test-id="tabTemplateConfig_form_cancelBtn" @click="closeTab">{{ isViewMode ? $t('关闭') : $t('取消') }}</bk-button>
            </div>
            <bk-dialog
                width="600"
                ext-cls="common-dialog label-dialog"
                header-position="left"
                render-directive="if"
                :mask-close="false"
                :auto-close="false"
                :title="$t('新建标签')"
                :loading="labelLoading"
                :value="labelDialogShow"
                :cancel-text="$t('取消')"
                @confirm="editLabelConfirm"
                @cancel="labelDialogShow = false">
                <bk-form ref="labelForm" :model="labelDetail" :rules="labelRules">
                    <bk-form-item property="name" :label="$t('标签名称')" :required="true">
                        <bk-input v-model="labelDetail.name"></bk-input>
                    </bk-form-item>
                    <bk-form-item property="color" :label="$t('标签颜色')" :required="true">
                        <bk-dropdown-menu
                            ref="dropdown"
                            trigger="click"
                            class="color-dropdown"
                            @show="colorDropdownShow = true"
                            @hide="colorDropdownShow = false">
                            <div class="dropdown-trigger-btn" slot="dropdown-trigger">
                                <span class="color-block" :style="{ background: labelDetail.color }"></span>
                                <i :class="['bk-icon icon-angle-down',{ 'icon-flip': colorDropdownShow }]"></i>
                            </div>
                            <div class="color-list" slot="dropdown-content">
                                <div class="tip">{{ $t('选择颜色') }}</div>
                                <div>
                                    <span
                                        v-for="color in colorList"
                                        :key="color"
                                        class="color-item color-block"
                                        :style="{ background: color }"
                                        @click="labelDetail.color = color">
                                    </span>
                                </div>
                            </div>
                        </bk-dropdown-menu>
                    </bk-form-item>
                    <bk-form-item :label="$t('标签描述')">
                        <bk-input type="textarea" v-model="labelDetail.description"></bk-input>
                    </bk-form-item>
                </bk-form>
            </bk-dialog>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import tools from '@/utils/tools.js'
    import { NAME_REG, STRING_LENGTH, TASK_CATEGORIES, LABEL_COLOR_LIST } from '@/constants/index.js'
    import i18n from '@/config/i18n/index.js'
    import NotifyTypeConfig from './NotifyTypeConfig.vue'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'TabTemplateConfig',
        components: {
            MemberSelect,
            NotifyTypeConfig
        },
        mixins: [permission],
        props: {
            projectInfoLoading: Boolean,
            templateLabelLoading: Boolean,
            templateLabels: Array,
            isShow: Boolean,
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            const {
                name, category, notify_type, notify_receivers, description,
                executor_proxy, template_labels, default_flow_type, project_scope, template_id
            } = this.$store.state.template
            const { extra_info: extraInfo = {} } = notify_receivers

            return {
                formData: {
                    name,
                    category,
                    description,
                    executorProxy: executor_proxy ? [executor_proxy] : [],
                    receiverGroup: notify_receivers.receiver_group.slice(0),
                    notifyType: [notify_type.success.slice(0), notify_type.fail.slice(0)],
                    notifyTypeExtraInfo: { ...extraInfo },
                    labels: template_labels,
                    defaultFlowType: default_flow_type,
                    project_scope: project_scope,
                    template_id: template_id
                },
                stringLength: STRING_LENGTH,
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH,
                            message: i18n.t('流程名称长度不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('流程名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ],
                    project_scope: [
                        {
                            required: true,
                            message: i18n.t('请选择可见范围'),
                            trigger: 'blur'
                        }
                    ]
                },
                isProxyValidateError: false,
                taskCategories: TASK_CATEGORIES,
                labelDialogShow: false,
                labelRules: {
                    color: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ],
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('标签名称不能超过') + 50 + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                return this.templateLabels.every(label => label.name !== val)
                            },
                            message: i18n.t('标签已存在，请重新输入'),
                            trigger: 'blur'
                        }
                    ]
                },
                labelDetail: {},
                colorDropdownShow: false,
                colorList: LABEL_COLOR_LIST,
                labelLoading: false,
                proxyPlaceholder: '',
                isBaseInfoSelectAllProjectScope: false,
                baseInfoProjectScopeList: [],
                isOutermostBaseInfoAllProjectScope: false,
                projects: [],
                isDropdownOpen: false,
                isFirstOpen: false
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'timeout': state => state.template.time_out,
                'infoBasicConfig': state => state.infoBasicConfig
            }),
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName,
                'authActions': state => state.authActions,
                'projectList': state => state.userProjectList
            }),
            allProjectIds () {
                const allIds = []
                this.projects.forEach((group) => {
                    group.children.forEach((item) => {
                        allIds.push(item.id)
                    })
                })
                return allIds
            }
        },
        watch: {
            isDropdownOpen: {
                handler (val) {
                    if (!val) {
                        if (this.formData.project_scope.length > 0) {
                            this.processingProjectsToTop(this.formData.project_scope, this.projects)
                        }
                    }
                }
            }
        },

        created () {
            if (this.common) {
                this.initProjects()
                if (this.formData.project_scope.includes('*')) {
                    this.baseInfoProjectScopeList = this.allProjectIds
                    this.formData.project_scope = this.baseInfoProjectScopeList
                    this.isOutermostBaseInfoAllProjectScope = true
                } else {
                    this.baseInfoProjectScopeList = this.formData.project_scope.map(item => typeof item === 'number' ? item : Number(item))
                    this.formData.project_scope = this.baseInfoProjectScopeList
                    this.isOutermostBaseInfoAllProjectScope = this.baseInfoProjectScopeList.length === this.allProjectIds.length
                }
            }
        },
      
        mounted () {
            // 模板没有设置执行代理人时，默认使用项目下的执行代理人
            if (!this.formData.executorProxy.length) {
                this.setExecutorProxy()
            }
            this.$refs.nameInput.focus()
            document.addEventListener('click', this.handleClickOutside)
        },
        methods: {
            ...mapMutations('template/', [
                'setTplConfig',
                'setProjectScope'
            ]),
            ...mapActions('project', [
                'getProjectConfig',
                'createTemplateLabel'
            ]),
            processingProjectsToTop (val, projects) {
                val.forEach((item) => {
                    item = typeof item === 'number' ? item : Number(item)
                    projects.map((group) => {
                        group.children.map((project, index) => {
                            if (project.id === item) {
                                const tempItem = group.children.splice(index, 1)[0]
                                group.children.unshift(tempItem)
                            }
                        })
                    })
                })
                return projects
            },
            initProjects () {
                const projects = []
                const projectsGroup = [
                    {
                        name: i18n.t('业务'),
                        id: 1,
                        children: []
                    },
                    {
                        id: 2,
                        name: i18n.t('项目'),
                        children: []
                    }
                ]
                this.projectList.forEach(item => {
                    if (item.from_cmdb) {
                        projectsGroup[0].children.push(item)
                    } else {
                        projectsGroup[1].children.push(item)
                    }
                })
                projectsGroup.forEach(group => {
                    if (group.children.length) {
                        projects.push(group)
                    }
                })
                if (this.formData.project_scope.length > 0 && !this.formData.project_scope.includes('*')) {
                    this.projects = this.processingProjectsToTop(this.formData.project_scope, projects)
                } else {
                    this.projects = projects
                }
            },
            handleClickOutside (event) {
                const isHaveSomeClassName = event.target.classList.contains('bk-option-name') || event.target.classList.contains('bk-group-options') || event.target.classList.contains('bk-option-content-default')
                if (!isHaveSomeClassName) {
                    if (this.$refs.projectSelectRef && this.$refs.projectSelectRef.$el.contains(event.target)) {
                        if (this.isFirstOpen) {
                            this.isDropdownOpen = true
                            this.isFirstOpen = false
                        } else {
                            this.isDropdownOpen = false
                            this.isFirstOpen = true
                        }
                    } else {
                        this.isDropdownOpen = false
                        this.isFirstOpen = true
                    }
                }
            },
            handleBaseInfoSelectAllProjectScope (row) {
                if (row) {
                    this.isOutermostBaseInfoAllProjectScope = true
                    this.baseInfoProjectScopeList = this.allProjectIds
                    this.formData.project_scope = this.baseInfoProjectScopeList
                } else {
                    this.isOutermostBaseInfoAllProjectScope = false
                    this.baseInfoProjectScopeList = []
                    this.formData.project_scope = []
                }
                this.setProjectScope(row ? ['*'] : this.baseInfoProjectScopeList)
            },
            handleBaseInfoProjectVisibleChange (row) {
                const filterList = [...new Set(row)]
                this.baseInfoProjectScopeList = filterList
                const changeAllProjectScope = filterList.length === this.allProjectIds.length
                this.formData.project_scope = filterList
                this.setProjectScope(changeAllProjectScope ? ['*'] : filterList.map(item => typeof item === 'number' ? String(item) : item))
            },
            onSelectCategory (val) {
                if (val) {
                    window.reportInfo({
                        page: 'templateEdit',
                        zone: 'selectCategory',
                        event: 'click'
                    })
                }
            },
            onSelectLabel (val) {
                if (val) {
                    window.reportInfo({
                        page: 'templateEdit',
                        zone: 'selectLabel',
                        event: 'click'
                    })
                }
            },
            onEditLabel () {
                if (!this.hasPermission(['project_edit'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.authActions, resourceData)
                    return
                }
                this.labelDetail = { color: '#1c9574', name: '', description: '' }
                this.labelDialogShow = true
                this.colorDropdownShow = false
            },
            onManageLabel () {
                if (!this.hasPermission(['project_view'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_view'], this.authActions, resourceData)
                    return
                }
                const { href } = this.$router.resolve({
                    name: 'projectConfig',
                    params: { id: this.projectId },
                    query: { configActive: 'label_config' }
                })
                window.open(href, '_blank')
            },
            getTemplateConfig () {
                const { name, category, description, executorProxy, receiverGroup, notifyType, labels, defaultFlowType, notifyTypeExtraInfo } = this.formData
                const localProjectList = this.baseInfoProjectScopeList.length === this.allProjectIds.length ? ['*'] : this.baseInfoProjectScopeList.map(item => typeof item === 'number' ? String(item) : item)
                return {
                    name,
                    category,
                    description,
                    template_labels: labels,
                    executor_proxy: executorProxy.length === 1 ? executorProxy[0] : '',
                    receiver_group: receiverGroup,
                    notify_type: { success: notifyType[0], fail: notifyType[1] },
                    notify_type_extra_info: notifyTypeExtraInfo,
                    default_flow_type: defaultFlowType,
                    project_scope: localProjectList
                }
            },
            onSelectedExecutorProxy (val) {
                this.formData.executorProxy = val
                this.isProxyValidateError = val.length === 1 && val[0] !== this.username
            },
            jumpProjectManagement () {
                if (this.isViewMode) return
                if (this.authActions.includes('project_edit')) {
                    const { href } = this.$router.resolve({
                        name: 'projectConfig',
                        params: { id: this.projectId }
                    })
                    window.open(href, '_blank')
                } else {
                    const resourceData = {
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.authActions, resourceData)
                }
            },
            onSelectNotifyConfig (formData) {
                const { notifyType, notifyTypeExtraInfo, receiverGroup } = formData
                this.formData.notifyType = notifyType
                this.formData.notifyTypeExtraInfo = notifyTypeExtraInfo
                this.formData.receiverGroup = receiverGroup
            },
            async onSaveConfig () {
                try {
                    if (this.isProxyValidateError) {
                        return
                    }
                    const validations = await Promise.all([
                        this.$refs.configForm.validate(),
                        this.$refs.notifyTypeConfig.validate()
                    ])
                    if (validations.includes(false)) return

                    const data = this.getTemplateConfig()
                    this.setTplConfig(data)
                    this.closeTab()
                    this.$emit('templateDataChanged')
                } catch (error) {
                    console.warn(error)
                }
            },
            beforeClose () {
                if (this.isViewMode) {
                    this.closeTab()
                    return true
                }
                const { name, category, description, template_labels, executor_proxy, notify_receivers, notify_type, default_flow_type } = this.$store.state.template
                const originData = {
                    name,
                    category,
                    description,
                    template_labels,
                    executor_proxy,
                    receiver_group: notify_receivers.receiver_group,
                    notify_type,
                    default_flow_type
                }
                const editingData = this.getTemplateConfig()
                if (tools.isDataEqual(originData, editingData)) {
                    this.closeTab()
                    return true
                } else {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.closeTab()
                        }
                    })
                    return false
                }
            },
            closeTab () {
                this.$emit('closeTab')
            },
            editLabelConfirm () {
                if (this.labelLoading) {
                    return
                }
                this.labelLoading = true
                try {
                    this.$refs.labelForm.validate().then(async result => {
                        if (result) {
                            const { color, name, description } = this.labelDetail
                            const { project_id } = this.$route.params
                            const data = {
                                creator: this.username,
                                project_id: Number(project_id),
                                color,
                                name,
                                description
                            }
                            const resp = await this.createTemplateLabel(data)
                            if (resp.result) {
                                this.$emit('updateTemplateLabelList')
                                this.labelDialogShow = false
                                this.formData.labels.push(resp.data.id)
                                this.$bkMessage({
                                    message: i18n.t('标签新建成功'),
                                    theme: 'success'
                                })
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
                }
            },
            // 获取代理人设置数据
            async setExecutorProxy () {
                try {
                    const resp = await this.getProjectConfig(this.projectId)
                    if (resp.result) {
                        const { executor_proxy, executor_proxy_exempts } = resp.data
                        this.proxyPlaceholder = i18n.t('项目执行代理人(n)；免代理用户(m)', {
                            n: executor_proxy || '--',
                            m: executor_proxy_exempts || '--'
                        })
                    }
                } catch (e) {
                    console.log(e)
                }
            }
        },
        unmounted () {
            document.removeEventListener('click', this.handleClickOutside)
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.config-wrapper {
    height: calc(100vh - 60px);
    background: none;
    border: none;
    .form-area {
        padding: 30px 30px 0;
        height: calc(100% - 49px);
        overflow-y: auto;
        @include scrollbar;
    }
    .form-section {
        margin-bottom: 30px;
        & > h4 {
            margin: 0 0 24px 0;
            padding-bottom: 10px;
            color: #313238;
            font-weight: bold;
            font-size: 14px;
            border-bottom: 1px solid #cacedb;
        }
        .tip-desc {
            font-size: 12px;
            font-weight: normal;
            margin-left: 20px;
            color: #979ba5;
        }
    }
    .btn-wrap {
        padding: 8px 30px;
        border-top: 1px solid #cacedb;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }
    }
    ::v-deep .bk-label {
        font-size: 12px;
    }
    .user-selector {
        display: block;
    }
    .category-tips {
        position: absolute;
        right: -20px;
        top: 10px;
        font-size: 16px;
        color: #c4c6cc;
        cursor: pointer;
        &:hover {
            color: #f4aa1a;
        }
    }
}
.executor-proxy-desc {
    font-size: 12px;
    line-height: 16px;
    margin-top: 5px;
    color: #b8b8b8;
    .project-management {
        color: #3a84ff;
        cursor: pointer;
    }
    .disabled {
        color: #dcdee5;
        cursor: not-allowed;
    }
    .bloack {
        display: block;
    }
}
    .select-all-project-scope{
        margin: 0 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #dcdee5;
    }
    .select-all-project-scope-checkbox{
        margin-right: 14px;
    }
</style>
