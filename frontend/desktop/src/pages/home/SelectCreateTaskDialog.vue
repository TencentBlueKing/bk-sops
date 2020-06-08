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
    <bk-dialog
        width="600"
        :render-directive="'if'"
        :ext-cls="'common-dialog'"
        :title="$t('创建任务')"
        :mask-close="false"
        :value="isCreateTaskDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @cancel="onCancel">
        <div class="task-create-container" v-bkloading="{ isLoading: loadingStatus.taskContainer, opacity: 1 }">
            <bk-form :model="formData" :rules="rules" ref="taskCreateForm">
                <bk-form-item :label="$t('任务类型')" :required="true" :property="'taskType'">
                    <bk-select
                        class="bk-select-inline"
                        v-model="formData.taskType"
                        :loading="loadingStatus.taskType"
                        :popover-width="260"
                        :clearable="false"
                        :placeholder="$t('请选择任务类型')"
                        @change="checkPermission">
                        <bk-option
                            v-for="option in taskTypeList"
                            :key="option.value"
                            :id="option.value"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <div v-show="isShowtaskError" class="error-info">{{ $t('请选择任务类型') }}</div>
                </bk-form-item>
                <bk-form-item :label="$t('项目名称')" :required="true" :property="'selectedProject'">
                    <bk-select
                        class="bk-select-inline"
                        v-model="formData.selectedProject"
                        :loading="loadingStatus.project"
                        :popover-width="260"
                        :clearable="false"
                        :placeholder="$t('请选择项目')"
                        @change="checkPermission">
                        <bk-option
                            v-for="option in projectList"
                            :key="option.value"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <div v-show="isShowProjectError" class="error-info">{{ $t('请选择项目') }}</div>
                </bk-form-item>
            </bk-form>
        </div>
        <div class="dialog-footer" slot="footer">
            <bk-button
                theme="primary"
                :loading="permissionLoading"
                :class="{ 'btn-permission-disable': !hasUseCommonTplPerm }"
                v-cursor="{ active: !hasUseCommonTplPerm }"
                @click="onConfirm">
                {{ $t('确定') }}
            </bk-button>
            <bk-button @click="onCancel">{{ $t('取消') }}</bk-button>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import permission from '@/mixins/permission.js'
    import { mapGetters, mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    export default {
        name: 'SelectCreateTaskDialog',
        components: {
        },
        mixins: [permission],
        props: {
            isCreateTaskDialogShow: Boolean,
            createTaskItem: Object
        },
        data () {
            return {
                loadingStatus: {
                    taskType: false,
                    project: false,
                    taskContainer: false
                },
                taskTypeList: [
                    { name: i18n.t('普通任务'), value: 'taskflow' },
                    { name: i18n.t('周期任务'), value: 'periodic' }
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
                permissionLoading: false,
                hasUseCommonTplPerm: true // 公共流程创建普通任务、周期任务权限
            }
        },
        computed: {
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            createTaskPerm () {
                return this.formData.taskType === 'taskflow' ? ['common_flow_create_task'] : ['common_flow_create_periodic_task']
            }
        },
        watch: {
            isCreateTaskDialogShow (val) {
                if (val) {
                    this.formData.taskType = ''
                    this.formData.selectedProject = ''
                    this.isShowtaskError = false
                    this.isShowProjectError = false
                    this.hasUseCommonTplPerm = true
                }
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            onConfirm () {
                const templateId = this.createTaskItem.extra_info.template_id
                if (!this.checkEmpty()) {
                    return
                }
                // 权限查询过程中
                if (this.permissionLoading) {
                    return
                }
                // 没有创建任务权限
                if (!this.hasUseCommonTplPerm) {
                    this.applyUseCommonPerm()
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
            async checkPermission () {
                this.checkEmpty()
                const { taskType, selectedProject } = this.formData
                if (taskType && selectedProject) {
                    try {
                        this.permissionLoading = true
                        const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                        const data = {
                            action: this.createTaskPerm[0],
                            resources: [
                                {
                                    system: bkSops.id,
                                    type: 'project',
                                    id: this.formData.selectedProject,
                                    attributes: {}
                                },
                                {
                                    system: bkSops.id,
                                    type: 'common_flow',
                                    id: this.createTaskItem.id,
                                    attributes: {}
                                }
                            ]
                        }
                        const resp = await this.queryUserPermission(data)
                        if (resp.data.is_allow) {
                            this.hasUseCommonTplPerm = true
                        } else {
                            this.hasUseCommonTplPerm = false
                        }
                    } catch (error) {
                        errorHandler(error, this)
                    } finally {
                        this.permissionLoading = false
                    }
                }
            },
            // 申请公共流程使用权限
            applyUseCommonPerm () {
                const project = this.projectList.find(m => m.id === this.formData.selectedProject)
                const curPermission = [...this.createTaskItem.auth_actions, ...project.auth_actions]
                const resourceData = {
                    common_flow: [{
                        id: this.createTaskItem.extra_info.template_id,
                        name: this.createTaskItem.extra_info.name
                    }],
                    project: [{
                        id: project.name,
                        name: project.name
                    }]
                }
                this.applyForPermission(this.createTaskPerm, curPermission, resourceData)
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
