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
                :class="['save-canvas', {
                    'btn-permission-disable': !isSaveBtnEnable
                }]"
                :loading="templateSaving"
                v-cursor="{ active: !isSaveBtnEnable }"
                @click="onSaveTemplate(false)">
                {{i18n.save}}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !isSaveAndCreateBtnEnable
                }]"
                :loading="createTaskSaving"
                v-cursor="{ active: !isSaveAndCreateBtnEnable }"
                @click="onSaveTemplate(true)">
                {{createTaskBtnText}}
            </bk-button>
            <router-link class="bk-button bk-default" :to="getHomeUrl()">{{i18n.back}}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'

    export default {
        name: 'TemplateHeader',
        components: {
            BaseTitle
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
                return this.isTemplateDataChanged || this.type === 'new' || this.type === 'clone'
            },
            createTaskBtnText () {
                return this.isSaveAndCreateTaskType ? this.i18n.saveAndCreateTask : this.i18n.createTask
            },
            createTaskBtnIsPass () {
                if (this.type === 'new') {
                    return this.perm.create_task.isPass && this.perm.edit.isPass
                } else {
                    return this.hasPermission(this.saveAndCreateRequiredPerm, this.tplActions, this.tplOperations)
                }
            },
            saveRequiredPerm () {
                return this.type === 'new' ? ['create_template'] : ['edit']
            },
            saveAndCreateRequiredPerm () {
                if (this.type === 'new') {
                    return ['create_template']
                } else {
                    return this.isTemplateDataChanged ? ['create_task', 'edit'] : ['create_task']
                }
            },
            isSaveBtnEnable () {
                if (this.type === 'new') {
                    return this.hasPermission(this.saveRequiredPerm, this.authActions, this.authOperations)
                } else {
                    return this.hasPermission(this.saveRequiredPerm, this.tplActions, this.tplOperations)
                }
            },
            isSaveAndCreateBtnEnable () {
                if (this.type === 'new') {
                    return this.hasPermission(this.saveAndCreateRequiredPerm, this.authActions, this.authOperations)
                } else {
                    return this.hasPermission(this.saveAndCreateRequiredPerm, this.tplActions, this.tplOperations)
                }
            }
        },
        watch: {
            name (val) {
                this.tName = val
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setTemplateName'
            ]),
            onInputName (val) {
                this.$emit('onChangeName', val)
            },
            onSaveTemplate (saveAndCreate = false) {
                const { resourceData, operations, actions, resource } = this.getPermissionData()
                const required = saveAndCreate ? this.saveAndCreateRequiredPerm : this.saveRequiredPerm
                if (!this.hasPermission(required, actions, operations)) {
                    debugger
                    this.applyForPermission(required, resourceData, operations, resource)
                    return
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
                if (this.type === 'new') {
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
                let url = `/template/home/${this.project_id}/`
                const entrance = this.$route.query.entrance || ''
                const actions = [
                    { key: 'template_business', url: `/template/home/${this.project_id}/` },
                    { key: 'admin_common', url: '/admin/common/template/' }
                ]
                actions.forEach(action => {
                    if (entrance.indexOf(action.key) > -1) {
                        url = action.url
                    }
                })
                if (this.common) {
                    url += '?common=1'
                }
                return url
            },
            goToTaskUrl () {
                const entrance = this.$route.query.entrance
                this.$router.push({
                    path: `/template/newtask/${this.project_id}/selectnode/`,
                    query: {
                        template_id: this.template_id,
                        common: this.common ? '1' : undefined,
                        entrance: entrance || undefined
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
            }
        }
    }
</script>
<style lang="scss" scoped>
    .template-header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        height: 59px;
        background: #f4f7fa;
        border: 1px solid #cacedb;
        .template-name-input {
            position: relative;
            width: 430px;
            text-align: center;
        }
        .name-show-mode {
            display: inline-block;
        }
        .canvas-name {
            display: inline-block;
            margin: 0;
            max-width: 400px;
            height: 30px;
            line-height: 30px;
            font-size: 14px;
            font-weight: normal;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: #606266;
        }
        .common-icon-edit {
            float: right;
            margin: 6px 0 0 4px;
            color: #546a9e;
            vertical-align: 9px;
            cursor: pointer;
            &:hover {
                color: #3480ff;
            }
        }
        .name-error {
            position: absolute;
            margin: 7px 0 0 10px;
            right: 0;
            top: 6px;
            font-size: 12px;
        }
    }
</style>
