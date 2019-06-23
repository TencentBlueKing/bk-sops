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
            <BaseInput
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
            </BaseInput>
            <span class="name-error common-error-tip error-msg">{{ errors.first('templateName') }}</span>
        </div>
        <div class="canvas-operation-wrapper">
            <bk-button
                type="primary"
                :class="['save-canvas', {
                    'btn-permission-disable': !perm.edit.isPass
                }]"
                :loading="templateSaving"
                :disabled="perm.edit.pending"
                v-cursor="{ action: !perm.edit.isPass }"
                @click="onSaveTemplate(false)">
                {{ i18n.save }}
            </bk-button>
            <bk-button
                type="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !createTaskBtnIsPass
                }]"
                :loading="createTaskSaving"
                :disabled="perm.create_task.pending"
                v-cursor="{ action: !createTaskBtnIsPass }"
                @click="onSaveTemplate(true)">
                {{ createTaskBtnText }}
            </bk-button>
            <router-link class="bk-button bk-button-default" :to="getHomeUrl()">{{ i18n.return }}</router-link>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ConfigBar',
        components: {
            BaseInput
        },
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
                isShowMode: true,
                perm: {
                    'create_task': {
                        pending: true,
                        isPass: true
                    },
                    'edit': {
                        pending: true,
                        isPass: true
                    }
                }
            }
        },
        computed: {
            templateTitle () {
                return this.$route.query.template_id === undefined ? this.i18n.NewProcess : this.i18n.editProcess
            },
            createTaskBtnText () {
                return (this.isTemplateDataChanged || this.type === 'new') ? this.i18n.saveTplAndcreateTask : this.i18n.addTask
            },
            createTaskBtnIsPass () {
                if (this.isTemplateDataChanged || this.type === 'new') {
                    return this.perm.create_task.isPass && this.perm.edit.isPass
                } else {
                    return this.perm.create_task.isPass
                }
            },
            saveAndCreateBtnPerm () {
                return (this.isTemplateDataChanged || this.type === 'new') ? ['create_task', 'edit'] : ['create_task']
            }
        },
        watch: {
            name (val) {
                this.tName = val
            }
        },
        created () {
            if (this.type !== 'edit') {
                this.getUserTplPerm()
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
            async getUserTplPerm () {
                const permissions = ['edit', 'create_task']
                const res = await this.queryUserPermission({
                    resource_type: 'flow-template',
                    action_ids: JSON.stringify(permissions)
                })
                permissions.forEach(p => {
                    const detail = res.data.details.find(d => d.action_id === p)
                    const perm = {
                        pending: false,
                        isPass: detail.is_pass
                    }
                    this.$set(this.perm, p, perm)
                })
            },
            /**
             * 单个模板操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 模板数据对象
             */
            onTemplatePermissonCheck (required, template) {
                const actions = []
                this.tplOperations.filter(item => {
                    return required.includes(item.operate_id)
                }).forEach(perm => {
                    perm.actions.forEach(action => {
                        if (!actions.find(item => action.id === item.id)) {
                            actions.push(action)
                        }
                    })
                })
                const { scope_id, scope_name, scope_type, system_id, system_name, resource } = this.tplResource
                const permissions = []
                actions.forEach(item => {
                    const res = []
                    res.push([{
                        resource_id: template.id,
                        resource_name: template.name,
                        resource_type: resource.resource_type,
                        resource_type_name: resource.resource_type_name
                    }])
                    permissions.push({
                        scope_id,
                        scope_name,
                        scope_type,
                        system_id,
                        system_name,
                        resources: res,
                        action_id: item.id,
                        action_name: item.name
                    })
                })

                this.triggerPermisionModal(permissions)
            },
            onSaveTemplate (saveAndCreate = false) {
                const required = saveAndCreate ? this.saveAndCreateBtnPerm : ['edit']
                if (!this.hasPermission(required, this.tplActions, this.tplOperations)) {
                    const template = {
                        id: this.template_id,
                        name: this.name
                    }
                    this.onTemplatePermissonCheck(required, template)
                    return
                }

                this.$validator.validateAll().then((result) => {
                    if (!result) return
                    this.tName = this.tName.trim()
                    this.setTemplateName(this.tName)
                    if (saveAndCreate && !this.isTemplateDataChanged && this.type !== 'new') {
                        const taskUrl = this.getTaskUrl()
                        this.$router.push(taskUrl)
                    } else {
                        this.$emit('onSaveTemplate', saveAndCreate)
                    }
                })
            },
            getHomeUrl () {
                let url = `/template/home/${this.project_id}/`
                if (this.common) {
                    url += '?common=1'
                }
                return url
            },
            getTaskUrl () {
                let url = `/template/newtask/${this.project_id}/selectnode/?template_id=${this.template_id}`
                if (this.common) {
                    url += '&common=1'
                }
                return url
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
            padding: 4px 10px;
            max-width: 400px;
            height: auto;
            line-height: 12px;
            font-size: 14px;
            overflow: hidden;
            text-overflow:ellipsis;
            white-space: nowrap;
            border: 1px solid $commonBorderColor;
            outline: none;
            &:focus {
                border-color: $blueDefault;
            }
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
        .save-canvas {
            width: 90px;
            height: 32px;
            line-height: 32px;
            margin-left: 36px;
        }
        .bk-button-default {
            width: 90px;
            height: 32px;
            line-height: 32px;
            margin-left: 10px;
        }
        .bk-button.bk-primary {
            height: 32px;
            line-height: 32px;
            margin-left: 10px;
        }
    }
}
</style>
