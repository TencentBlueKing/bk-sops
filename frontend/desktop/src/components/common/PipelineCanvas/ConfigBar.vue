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
    <div class="config-wrapper">
        <div class="config-title-wrapper">
            <span class="title-border">|</span>
            <span class="title-text">{{templateTitle}}</span>
        </div>
        <div class="config-name-wrapper">
            <div class="name-show-mode" v-if="isShowMode">
                <h3 class="canvas-name" :title="tName">{{tName}}</h3>
                <span class="common-icon-edit" @click="onNameEditing"></span>
            </div>
            <bk-input
                v-else
                class="canvas-name-input"
                ref="canvasNameInput"
                :title="tName"
                v-model="tName"
                :placeholder="i18n.placeholder"
                v-validate="templateNameRule"
                data-vv-name="templateName"
                :name="'templateName'"
                :has-error="errors.has('templateName')"
                @input="onInputName"
                @blur="onInputBlur"
                @enter="onInputBlur">
            </bk-input>
            <span class="name-error common-error-tip error-msg">{{ errors.first('templateName') }}</span>
        </div>
        <div class="canvas-operation-wrapper">
            <bk-button
                theme="primary"
                :class="['save-canvas', {
                    'btn-permission-disable': !isSaveBtnEnable
                }]"
                :loading="templateSaving"
                v-cursor="{ active: !isSaveBtnEnable }"
                @click="onSaveTemplate(false)">
                {{ i18n.save }}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !isSaveAndCreateBtnEnable
                }]"
                :loading="createTaskSaving"
                v-cursor="{ active: !isSaveAndCreateBtnEnable }"
                @click="onSaveTemplate(true)">
                {{ createTaskBtnText }}
            </bk-button>
            <router-link class="bk-button bk-default canvas-btn" :to="getHomeUrl()">{{ i18n.return }}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ConfigBar',
        mixins: [permission],
        props: [
            'name', 'project_id', 'template_id', 'type', 'common', 'templateSaving',
            'createTaskSaving', 'isTemplateDataChanged', 'tplResource', 'tplActions', 'tplOperations'
        ],
        data () {
            return {
                i18n: {
                    placeholder: gettext('请输入名称'),
                    NewProcess: gettext('新建流程'),
                    editProcess: gettext('编辑流程'),
                    addTask: gettext('新建任务'),
                    saveTplAndcreateTask: gettext('保存并新建任务'),
                    save: gettext('保存'),
                    return: gettext('返回')
                },
                tName: this.name.trim(),
                templateNameRule: {
                    required: true,
                    max: STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isShowMode: true
            }
        },
        computed: {
            ...mapState('project', {
                'authActions': state => state.authActions,
                'authOperations': state => state.authOperations,
                'authResource': state => state.authResource
            }),
            templateTitle () {
                return this.$route.query.template_id === undefined ? this.i18n.NewProcess : this.i18n.editProcess
            },
            isSaveAndCreateTaskType () {
                return this.isTemplateDataChanged || this.type === 'new' || this.type === 'clone'
            },
            createTaskBtnText () {
                return this.isSaveAndCreateTaskType ? this.i18n.saveTplAndcreateTask : this.i18n.addTask
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
                    this.$refs.canvasNameInput.focus()
                    this.$refs.canvasNameInput.select()
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
@import '@/scss/config.scss';
.config-wrapper {
    position: relative;
    height: 60px;
    background: #f4f7fa;
    border-bottom: 1px solid $commonBorderColor;
    text-align: center;
    .config-title-wrapper {
        float: left;
        margin: 19px 0 0 20px;
        .title-border {
            color: #a3c5fd;
        }
        .title-text {
            line-height: 20px;
            margin-left: 10px;
            font-size: 14px;
            font-weight: 600;
            color:#313238;
        }
    }
    .config-name-wrapper {
        margin: 0 auto;
        padding-top: 15px;
        width: 430px;
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
            text-overflow:ellipsis;
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
        .canvas-name-input {
            max-width: 400px;
            overflow: hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
        }
        .name-error {
            position: absolute;
            margin: 7px 0 0 10px;
            font-size: 12px;
        }
    }
    .canvas-operation-wrapper {
        position: absolute;
        top: 14px;
        right: 20px;
        .canvas-btn {
            min-width: 90px;
            &:not(:last-child) {
                margin-right: 10px;
            }
        }
    }
}
</style>
