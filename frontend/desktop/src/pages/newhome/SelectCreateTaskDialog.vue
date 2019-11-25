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
                        @selected="onSelectTaskType">
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
                        @selected="onSelectProject">
                        <bk-option
                            v-for="option in projectList"
                            :key="option.value"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <div v-show="isShowprojectError" class="error-info">{{ i18n.projectPlaceholder }}</div>
                </bk-form-item>
            </bk-form>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import permission from '@/mixins/permission.js'
    import { mapGetters } from 'vuex'
    export default {
        name: 'SelectCreateTaskDialog',
        components: {
        },
        mixins: [permission],
        props: ['isCreateTaskDialogShow', 'createTaskTemplateId'],
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
                isShowprojectError: false
            }
        },
        computed: {
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            })
        },
        methods: {
            onSelectTaskType (type) {
                
            },
            onSelectProject () {

            },
            onConfirm () {
                if (!this.formData.taskType) {
                    this.isShowtaskError = true
                }
                if (!this.formData.selectedProject) {
                    this.isShowprojectError = true
                }
                const entrance = this.formData.taskType === 'periodic' ? 'periodicTask' : undefined
                this.$router.push({
                    name: 'taskStep',
                    params: { project_id: this.formData.selectedProject, step: 'selectnode' },
                    query: { template_id: this.createTaskTemplateId, common: '1', entrance }
                })
            },
            onCancel () {

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
