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
    <bk-dialog
        width="600"
        :render-directive="'if'"
        :ext-cls="'common-dialog'"
        :title="$t('新建任务')"
        :mask-close="false"
        :value="isCreateTaskDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @cancel="onCancel">
        <div class="task-create-container" v-bkloading="{ isLoading: loadingStatus.taskContainer, opacity: 1, zIndex: 100 }">
            <bk-form :model="formData" ref="taskCreateForm">
                <bk-form-item :label="$t('选择项目')" :property="'selectedProject'">
                    <bk-select
                        class="bk-select-inline"
                        v-model="formData.selectedProject"
                        :loading="loadingStatus.project"
                        :popover-width="260"
                        :clearable="false"
                        :searchable="true"
                        :placeholder="$t('请选择')"
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
    import permission from '@/mixins/permission.js'
    import { mapState, mapActions } from 'vuex'
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
                    project: false,
                    taskContainer: false
                },
                formData: {
                    selectedProject: ''
                },
                isShowProjectError: false,
                permissionLoading: false,
                hasUseCommonTplPerm: true // 公共流程创建普通任务、周期任务权限
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                projectList: state => state.userProjectList
            }),
            createTaskPerm () {
                return ['common_flow_create_task']
            }
        },
        watch: {
            isCreateTaskDialogShow (val) {
                if (val) {
                    this.formData.selectedProject = ''
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
                this.$router.push({
                    name: 'taskCreate',
                    params: { project_id: this.formData.selectedProject, step: 'selectnode' },
                    query: { template_id: templateId, common: '1' }
                })
            },
            onCancel () {
                this.$emit('cancel')
            },
            checkEmpty () {
                this.isShowProjectError = !this.formData.selectedProject
                if (!this.formData.selectedProject) {
                    return false
                }
                return true
            },
            async checkPermission () {
                this.checkEmpty()
                const { selectedProject } = this.formData
                if (selectedProject) {
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
                    } catch (e) {
                        console.log(e)
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
                        id: project.id,
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
