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
    <bk-dialog
        width="850"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        :ok-text="okText"
        :mask-close="false"
        :value="isCreateTaskDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="task-create-container" v-bkloading="{ isLoading: loadingStatus.taskContainer, opacity: 1 }">
            <bk-form :model="formData" :rules="rules" ref="taskCreateForm" form-type="inline">
                <bk-form-item :label="i18n.taskName" :required="true" :property="'taskType'">
                    <bk-select
                        class="bk-select-inline"
                        v-model="formData.taskType"
                        :loading="loadingStatus.taskType"
                        :popover-width="260"
                        :clearable="false"
                        :placeholder="i18n.taskPlaceholder"
                        @change="checkPermission">
                        <bk-option
                            v-for="option in taskTypeList"
                            :key="option.value"
                            :id="option.value"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <div v-show="isShowtaskError" class="error-info">{{ i18n.taskPlaceholder }}</div>
                </bk-form-item>
                <bk-form-item :label="i18n.projectName" :required="true" :property="'selectedProject'">
                    <bk-select
                        class="bk-select-inline"
                        v-model="formData.selectedProject"
                        :loading="loadingStatus.project"
                        :popover-width="260"
                        :clearable="false"
                        :placeholder="i18n.projectPlaceholder"
                        @change="checkPermission">
                        <bk-option
                            v-for="option in projectList"
                            :key="option.value"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <div v-show="isShowProjectError" class="error-info">{{ i18n.projectPlaceholder }}</div>
                </bk-form-item>
            </bk-form>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import permission from '@/mixins/permission.js'
    import { mapGetters, mapState } from 'vuex'
    export default {
        name: 'SelectCreateTaskDialog',
        components: {
        },
        mixins: [permission],
        props: ['isCreateTaskDialogShow', 'createTaskItem', 'tplOperations', 'tplResource'],
        data () {
            return {
                i18n: {
                    title: gettext('创建任务'),
                    taskName: gettext('任务类型'),
                    projectName: gettext('项目名称'),
                    taskPlaceholder: gettext('请选择任务类型'),
                    projectPlaceholder: gettext('请选择项目')
                },
                loadingStatus: {
                    taskType: false,
                    project: false,
                    taskContainer: false
                },
                taskTypeList: [
                    { name: gettext('普通任务'), value: 'taskflow' },
                    { name: gettext('周期任务'), value: 'periodic' }
                ],
                rules: {
                    taskType: [{
                        required: true,
                        message: '必填项',
                        trigger: 'blur'
                    }],
                    selectedProject: [{
                        required: true,
                        message: '必填项',
                        trigger: 'blur'
                    }]
                },
                formData: {
                    taskType: '',
                    selectedProject: ''
                },
                isShowtaskError: false,
                isShowProjectError: false,
                hasCreateTaskPer: true, // 新建任务权限
                hasUseCommonTplPer: true // 使用公共流程权限
            }
        },
        computed: {
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            ...mapState('project', {
                'authOperations': state => state.authOperations
            }),
            okText () {
                return this.hasCreateTaskPer && this.hasUseCommonTplPer ? gettext('确定') : gettext('去申请')
            }
        },
        watch: {
            isCreateTaskDialogShow (val) {
                if (val) {
                    this.formData.taskType = ''
                    this.formData.selectedProject = ''
                    this.isShowtaskError = false
                    this.isShowProjectError = false
                    this.hasCreateTaskPer = true
                    this.hasUseCommonTplPer = true
                }
            }
        },
        methods: {
            onConfirm () {
                const templateId = this.createTaskItem.extra_info.template_id
                if (!this.checkEmpty()) {
                    return false
                }
                if (!this.hasCreateTaskPer) {
                    this.applyForPermission(['create_task'], this.createTaskItem, this.tplOperations, this.tplResource)
                    return
                }
                if (!this.hasUseCommonTplPer) {
                    this.applyUseCommonPer()
                    return
                }
                const entrance = this.formData.taskType === 'periodic' ? 'periodicTask' : undefined
                this.$router.push({
                    name: 'taskStep',
                    params: { project_id: this.formData.selectedProject, step: 'selectnode' },
                    query: { template_id: templateId, common: '1', entrance }
                })
            },
            onCancel () {
                this.$emit('cancel')
            },
            checkEmpty () {
                this.isShowtaskError = !this.formData.taskType
                this.isShowProjectError = !this.formData.selectedProject
                if (!this.formData.taskType || !this.formData.selectedProject) {
                    return false
                }
                return true
            },
            checkPermission () {
                this.checkEmpty()
                const { taskType, selectedProject } = this.formData
                if (taskType && selectedProject) {
                    const { auth_actions } = this.createTaskItem
                    const hasPer = this.hasPermission(['create_task'], auth_actions, this.tplOperations)
                    const action = this.projectList.find(m => m.id === selectedProject)
                    this.hasCreateTaskPer = !!hasPer
                    this.hasUseCommonTplPer = action.auth_actions.indexOf('use_common_template') > -1
                }
            },
            // 申请公共流程使用权限
            applyUseCommonPer () {
                const project = this.projectList.find(m => m.id === this.formData.selectedProject)
                const resourceData = {
                    name: gettext('项目'),
                    id: project.id,
                    auth_actions: project.auth_actions
                }
                this.applyForPermission(['use_common_template'], resourceData, this.authOperations, this.authResource)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-create-container {
    padding: 30px;
    .error-info {
        position: absolute;
        left: 0;
        bottom: -22px;
        font-size: 12px;
        color: #ff5757;
    }
}
</style>
