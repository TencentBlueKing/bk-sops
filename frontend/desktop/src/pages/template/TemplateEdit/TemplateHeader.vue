/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="template-header-wrapper">
        <base-title class="template-title" :title="title"></base-title>
        <div class="template-name-input">
            <div class="name-show-mode" v-if="isShowMode">
                <h3 class="canvas-name" :title="tName">{{tName}}</h3>
                <span class="common-icon-edit" @click="onNameEditing"></span>
            </div>
            <bk-input
                v-else
                ref="canvasNameInput"
                v-validate="templateNameRule"
                data-vv-name="templateName"
                :name="'templateName'"
                :has-error="errors.has('templateName')"
                :value="name"
                :placeholder="$t('请输入名称')"
                @input="onInputName"
                @enter="onInputBlur"
                @blur="onInputBlur">
            </bk-input>
            <span class="name-error common-error-tip error-msg">{{ errors.first('templateName') }}</span>
        </div>
        <div class="button-area">
            <bk-button
                theme="primary"
                :class="[
                    'save-canvas',
                    'task-btn',
                    { 'btn-permission-disable': !saveBtnActive }]"
                :loading="templateSaving"
                v-cursor="{ active: !saveBtnActive }"
                @click.stop="onSaveClick(false)">
                {{$t('保存')}}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !createTaskBtnActive
                }]"
                :loading="createTaskSaving"
                v-cursor="{ active: !createTaskBtnActive }"
                @click.stop="onSaveClick(true)">
                {{createTaskBtnText}}
            </bk-button>
            <router-link class="bk-button bk-default" :to="getHomeUrl()">{{$t('返回')}}</router-link>
        </div>
        <SelectProjectModal
            :title="$t('创建任务')"
            :show="isSelectProjectShow"
            :confirm-loading="commonTplCreateTaskPermLoading"
            :confirm-cursor="!hasCommonTplCreateTaskPerm"
            @onChange="handleProjectChange"
            @onConfirm="handleCreateTaskConfirm"
            @onCancel="handleCreateTaskCancel">
        </SelectProjectModal>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import SelectProjectModal from '@/components/common/modal/SelectProjectModal.vue'
    export default {
        name: 'TemplateHeader',
        components: {
            BaseTitle,
            SelectProjectModal
        },
        mixins: [permission],
        props: {
            type: {
                type: String,
                default: 'edit'
            },
            name: {
                type: String,
                default: ''
            },
            template_id: {
                type: [String, Number],
                default: ''
            },
            project_id: {
                type: [String, Number],
                default: ''
            },
            common: {
                type: String,
                default: ''
            },
            templateSaving: {
                type: Boolean,
                default: false
            },
            createTaskSaving: {
                type: Boolean,
                default: false
            },
            isTemplateDataChanged: {
                type: Boolean,
                default: false
            },
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                tName: this.name.trim(),
                templateNameRule: {
                    required: true,
                    max: STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isShowMode: true,
                isSelectProjectShow: false, // 是否显示项目选择弹窗
                saveBtnActive: false, // 保存按钮是否激活
                createTaskBtnActive: false, // 新建任务按钮是否激活
                hasCreateCommonTplPerm: false, // 创建公共流程权限
                hasCommonTplCreateTaskPerm: false, // 公共流程在项目下创建任务权限
                createCommonTplPermLoading: false,
                commonTplCreateTaskPermLoading: false,
                selectedProject: {} // 公共流程创建任务所选择的项目
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'authActions': state => state.authActions,
                'projectName': state => state.projectName
            }),
            title () {
                return this.$route.query.template_id === undefined ? i18n.t('新建流程') : i18n.t('编辑流程')
            },
            isSaveAndCreateTaskType () {
                return this.isTemplateDataChanged === true || this.type === 'new' || this.type === 'clone'
            },
            createTaskBtnText () {
                return this.isSaveAndCreateTaskType ? i18n.t('保存并新建任务') : i18n.t('新建任务')
            },
            saveRequiredPerm () {
                if (['new', 'clone'].includes(this.type)) {
                    return this.common ? ['common_flow_create'] : ['flow_create'] // 新建、克隆流程保存按钮对公共流程和普通流程的权限要求
                } else {
                    return this.common ? ['common_flow_edit'] : ['flow_edit']
                }
            },
            saveAndCreateRequiredPerm () {
                if (['new', 'clone'].includes(this.type)) {
                    return this.common ? ['common_flow_create'] : ['flow_create']
                } else {
                    if (this.isTemplateDataChanged) {
                        return this.common ? ['common_flow_edit'] : ['flow_edit', 'flow_create_task']
                    } else {
                        return this.common ? [] : ['flow_create_task']
                    }
                }
            }
        },
        watch: {
            name (val) {
                this.tName = val
            }
        },
        async mounted () {
            // 新建、克隆公共流程需要查询创建公共流程权限
            if (this.common) {
                await this.queryCreateCommonTplPerm()
                this.setSaveBtnPerm()
                this.setCreateTaskBtnPerm()
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapMutations('template/', [
                'setTemplateName'
            ]),
            onInputName (val) {
                this.$emit('onChangeName', val)
            },
            /**
             * 保存按钮，新建/保存并新建任务按钮点击
             * @param {Boolean} saveAndCreate 是否为新建/保存并新建任务按钮
             */
            onSaveClick (saveAndCreate = false) {
                if (this.createCommonTplPermLoading || this.commonTplCreateTaskPermLoading) {
                    return
                }

                if (saveAndCreate) {
                    if (this.createTaskBtnActive) {
                        if (this.common) {
                            this.isSelectProjectShow = true
                        } else {
                            this.saveTemplate(saveAndCreate)
                        }
                    } else {
                        if (this.common) {
                            this.applyCreateCommonTplPerm(this.saveAndCreateRequiredPerm)
                        } else {
                            this.applyTplPerm(this.saveAndCreateRequiredPerm)
                        }
                    }
                } else {
                    if (this.saveBtnActive) {
                        this.saveTemplate(saveAndCreate)
                    } else {
                        if (this.common) {
                            this.applyCreateCommonTplPerm(this.saveRequiredPerm)
                        } else {
                            this.applyTplPerm(this.saveRequiredPerm)
                        }
                    }
                }
            },
            saveTemplate (saveAndCreate = false) {
                this.$validator.validateAll().then((result) => {
                    if (!result) return
                    this.tName = this.tName.trim()
                    this.setTemplateName(this.tName)
                    if (saveAndCreate && !this.isSaveAndCreateTaskType) {
                        this.goToTaskUrl()
                    } else {
                        this.$emit('onSaveTemplate', saveAndCreate)
                    }
                })
            },
            getPermissionData () {
                let resourceData, actions
                if (['new', 'clone'].includes(this.type)) {
                    resourceData = {
                        id: this.project_id,
                        name: i18n.t('项目'),
                        auth_actions: this.authActions
                    }
                    actions = this.authActions
                } else {
                    resourceData = {
                        id: this.template_id,
                        name: this.name,
                        auth_actions: this.tplActions
                    }
                    actions = this.tplActions
                }
                return { resourceData, actions }
            },
            getHomeUrl () {
                const url = { name: 'process', params: { project_id: this.project_id } }
                if (this.common) {
                    url.name = 'commonProcessList'
                }
                return url
            },
            goToTaskUrl () {
                this.$router.push({
                    name: 'taskStep',
                    params: { step: 'selectnode', project_id: this.project_id },
                    query: {
                        template_id: this.template_id,
                        common: this.common || undefined,
                        entrance: 'templateEdit'
                    }
                })
            },
            onNameEditing () {
                this.isShowMode = false
                this.$nextTick(() => {
                    const inputEl = this.$refs.canvasNameInput.$el.getElementsByClassName('bk-form-input')[0]
                    this.$refs.canvasNameInput.focus()
                    inputEl.select()
                })
            },
            onInputBlur () {
                this.$validator.validateAll().then((result) => {
                    if (!result) {
                        return
                    }
                    this.isShowMode = true
                })
            },
            handleProjectChange (project) {
                this.selectedProject = project
                this.queryCommonTplCreateTaskPerm()
            },
            handleCreateTaskConfirm () {
                if (this.hasCommonTplCreateTaskPerm) {
                    this.saveTemplate(true)
                } else {
                    this.applyCommonTplCreateTaskPerm()
                }
            },
            handleCreateTaskCancel () {
                this.selectedProject = {}
                this.isSelectProjectShow = false
            },
            setSaveBtnPerm () {
                if (this.common && ['new', 'clone'].includes(this.type)) {
                    this.saveBtnActive = this.hasCreateCommonTplPerm
                } else {
                    const actions = [...this.authActions, ...this.tplActions]
                    this.saveBtnActive = this.hasPermission(this.saveRequiredPerm, actions)
                }
            },
            setCreateTaskBtnPerm () {
                if (this.common && ['new', 'clone'].includes(this.type)) {
                    this.createTaskBtnActive = this.hasCreateCommonTplPerm
                } else {
                    const actions = [...this.authActions, ...this.tplActions]
                    this.createTaskBtnActive = this.hasPermission(this.saveAndCreateRequiredPerm, actions)
                }
            },
            // 查询创建公共流程权限
            async queryCreateCommonTplPerm () {
                try {
                    this.createCommonTplPermLoading = true
                    const res = await this.queryUserPermission({
                        action: 'common_flow_create'
                    })
                    this.hasCreateCommonTplPerm = res.data.is_allow
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.createCommonTplPermLoading = false
                }
            },
            // 查询公共流程在项目下的创建任务权限
            async queryCommonTplCreateTaskPerm () {
                try {
                    this.commonTplCreateTaskPermLoading = true
                    const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                    const res = await this.queryUserPermission({
                        action: 'common_flow_create_task',
                        resoures: [
                            {
                                system: bkSops.id,
                                type: 'project',
                                id: this.selectedProject.id,
                                attributes: {}
                            },
                            {
                                system: bkSops.id,
                                type: 'common_flow',
                                id: this.template_id,
                                attributes: {}
                            }
                        ]
                    })
                    this.hasCommonTplCreateTaskPerm = res.data.is_allow
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.commonTplCreateTaskPermLoading = false
                }
            },
            applyCreateCommonTplPerm () {
                this.applyForPermission(['common_flow_create'])
            },
            applyCommonTplCreateTaskPerm () {
                const curPermission = [...this.tplActions, ...this.selectedProject.auth_actions]
                const resourceData = {
                    common_flow: [{
                        id: this.template_id,
                        name: this.name
                    }],
                    project: [{
                        id: this.selectedProject.id,
                        name: this.selectedProject.name
                    }]
                }
                this.applyForPermission(['common_flow_create_task'], curPermission, resourceData)
            },
            applyTplPerm (requiredPerm) {
                let curPermission = [...this.authActions]
                let resourceData = {
                    project: [{
                        id: this.project_id,
                        name: this.projectName
                    }]
                }
                if (this.type === 'edit') {
                    curPermission = [...this.tplActions]
                    resourceData = {
                        flow: [{
                            id: this.template_id,
                            name: this.name
                        }]
                    }
                }
                this.applyForPermission(requiredPerm, curPermission, resourceData)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .template-header-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        height: 59px;
        background: #f4f7fa;
        border: 1px solid #cacedb;
        .template-name-input {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 430px;
            text-align: center;
        }
        .name-show-mode {
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }
        .canvas-name {
            display: inline-block;
            margin: 0;
            max-width: 400px;
            font-size: 14px;
            font-weight: normal;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: #606266;
        }
        .common-icon-edit {
            margin-left: 4px;
            font-size: 12px;
            color: #546a9e;
            cursor: pointer;
            &:hover {
                color: #3480ff;
            }
        }
        .name-error {
            position: absolute;
            margin: 6px 0 0 4px;
            left: 100%;
            top: 6px;
            font-size: 12px;
            white-space: nowrap;
        }
        .task-btn {
            margin-right: 5px;
        }
    }
</style>
