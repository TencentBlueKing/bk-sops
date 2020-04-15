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
                :placeholder="i18n.placeholder"
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
                    { 'btn-permission-disable': !isSaveBtnEnable }]"
                :loading="templateSaving"
                v-cursor="{ active: !isSaveBtnEnable }"
                @click.stop="onSaveClick(false)">
                {{i18n.save}}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !isSaveAndCreateBtnEnable
                }]"
                :loading="createTaskSaving"
                v-cursor="{ active: !isSaveAndCreateBtnEnable }"
                @click.stop="onSaveClick(true)">
                {{createTaskBtnText}}
            </bk-button>
            <router-link class="bk-button bk-default" :to="getHomeUrl()">{{i18n.back}}</router-link>
        </div>
        <ProjectSelectorModal
            :is-new-task="false"
            ref="ProjectSelectorModal">
        </ProjectSelectorModal>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import ProjectSelectorModal from '@/components/common/modal/ProjectSelectorModal.vue'
    export default {
        name: 'TemplateHeader',
        components: {
            BaseTitle,
            ProjectSelectorModal
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
            tplResource: {
                type: Object,
                default () {
                    return {}
                }
            },
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            },
            tplOperations: {
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
                hasCreateTplPerm: false, // 是否有创建公共流程权限
                i18n: {
                    placeholder: gettext('请输入名称'),
                    create: gettext('新建流程'),
                    edit: gettext('编辑流程'),
                    save: gettext('保存'),
                    createTask: gettext('新建任务'),
                    saveAndCreateTask: gettext('保存并新建任务'),
                    back: gettext('返回')
                }
            }
        },
        computed: {
            ...mapState('project', {
                'authActions': state => state.authActions,
                'authOperations': state => state.authOperations,
                'authResource': state => state.authResource
            }),
            title () {
                return this.$route.query.template_id === undefined ? this.i18n.create : this.i18n.edit
            },
            isSaveAndCreateTaskType () {
                return this.isTemplateDataChanged === true || this.type === 'new' || this.type === 'clone'
            },
            createTaskBtnText () {
                return this.isSaveAndCreateTaskType ? this.i18n.saveAndCreateTask : this.i18n.createTask
            },
            saveRequiredPerm () {
                if (['new', 'clone'].includes(this.type)) {
                    return this.common ? ['create'] : ['create_template'] // 新建、克隆流程保存按钮对公共流程和普通流程的权限要求
                } else {
                    return ['edit']
                }
            },
            saveAndCreateRequiredPerm () {
                if (['new', 'clone'].includes(this.type)) {
                    return this.common ? ['create'] : ['create_template']
                } else {
                    return this.isTemplateDataChanged ? ['create_task', 'edit'] : ['create_task']
                }
            },
            isSaveBtnEnable () {
                if (!this.common) { // 普通流程保存/新建按钮是否可用
                    if (['new', 'clone'].includes(this.type)) {
                        return this.hasPermission(this.saveRequiredPerm, this.authActions, this.authOperations)
                    } else {
                        return this.hasPermission(this.saveRequiredPerm, this.tplActions, this.tplOperations)
                    }
                } else { // 公共流程保存/新建按钮是否可用
                    if (['new', 'clone'].includes(this.type)) {
                        return this.hasCreateTplPerm
                    } else {
                        return this.hasPermission(this.saveRequiredPerm, this.tplActions, this.tplOperations)
                    }
                }
            },
            isSaveAndCreateBtnEnable () {
                if (!this.common) { // 普通流程新建任务/保存并新建按钮是否可用
                    if (['new', 'clone'].includes(this.type)) {
                        return this.hasPermission(this.saveAndCreateRequiredPerm, this.authActions, this.authOperations)
                    } else {
                        return this.hasPermission(this.saveAndCreateRequiredPerm, this.tplActions, this.tplOperations)
                    }
                } else { // 公共流程新建任务/保存并新建按钮是否可用
                    if (['new', 'clone'].includes(this.type)) {
                        return this.hasCreateTplPerm
                    } else {
                        return this.hasPermission(this.saveAndCreateRequiredPerm, this.tplActions, this.tplOperations)
                    }
                }
            }
        },
        watch: {
            name (val) {
                this.tName = val
            }
        },
        created () {
            if (['new', 'clone'].includes(this.type) && this.common) { // 公共流程新建、克隆需要单独查询权限
                this.queryCreateCommonTplPerm()
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
            onSaveClick (saveAndCreate = false) {
                if (saveAndCreate && this.common) {
                    this.$refs.ProjectSelectorModal.show()
                    this.$refs.ProjectSelectorModal.$on('confirm', (projectId) => {
                        this.saveTemplate(true)
                    })
                    return false
                }
                this.saveTemplate(saveAndCreate)
            },
            saveTemplate (saveAndCreate = false, projectId) {
                const { resourceData, operations, actions, resource } = this.getPermissionData()
                const required = saveAndCreate ? this.saveAndCreateRequiredPerm : this.saveRequiredPerm
                if (!this.common || !['new', 'clone'].includes(this.type)) { // 创建、克隆公共流程执行事后校验
                    if (!this.hasPermission(required, actions, operations)) {
                        this.applyForPermission(required, resourceData, operations, resource)
                        return
                    }
                }

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
                let resourceData, operations, actions, resource
                if (['new', 'clone'].includes(this.type)) {
                    resourceData = {
                        id: this.project_id,
                        name: gettext('项目'),
                        auth_actions: this.authActions
                    }
                    operations = this.authOperations
                    actions = this.authActions
                    resource = this.authResource
                } else {
                    resourceData = {
                        id: this.template_id,
                        name: this.name,
                        auth_actions: this.tplActions
                    }
                    operations = this.tplOperations
                    actions = this.tplActions
                    resource = this.tplResource
                }
                return { resourceData, operations, actions, resource }
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
            async queryCreateCommonTplPerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'common_flow',
                        action_ids: JSON.stringify(['create'])
                    })
                    this.hasCreateTplPerm = !!res.data.details.find(item => {
                        return item.action_id === 'create' && item.is_pass
                    })
                } catch (err) {
                    errorHandler(err, this)
                }
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
