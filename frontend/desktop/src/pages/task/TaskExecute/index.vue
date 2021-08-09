/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-execute-container" v-bkloading="{ isLoading: taskDataLoading, opacity: 1, zIndex: 100 }">
        <template v-if="!taskDataLoading">
            <TaskFunctionalization
                v-if="isFunctional && showParamsFill"
                :common="common"
                :project_id="project_id"
                :template-id="templateId"
                :instance-id="instance_id"
                :instance-name="instanceName"
                :instance-flow="instanceFlow"
                :instance-actions="instanceActions">
            </TaskFunctionalization>
            <TaskOperation
                v-else
                :project_id="project_id"
                :instance_id="instance_id"
                :router-type="routerType"
                :instance-name="instanceName"
                :instance-flow="instanceFlow"
                :template_id="templateId"
                :template-source="templateSource"
                :instance-actions="instanceActions">
            </TaskOperation>
        </template>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import TaskOperation from './TaskOperation.vue'
    import TaskFunctionalization from './TaskFunctionalization.vue'
    import dom from '@/utils/dom.js'

    export default {
        name: 'TaskExecute',
        components: {
            TaskOperation,
            TaskFunctionalization
        },
        props: {
            project_id: [Number, String],
            instance_id: [Number, String],
            common: [Number, String],
            routerType: String
        },
        data () {
            return {
                taskDataLoading: true,
                taskStatusLoading: true,
                isFunctional: this.routerType === 'function', // 是否为职能化任务
                showParamsFill: false, // 显示参数填写页面
                primaryTitle: '', // 浏览器tab页初始title
                instanceName: '',
                instanceFlow: '',
                templateSource: '',
                instanceActions: [],
                templateId: ''
            }
        },
        created () {
            this.getTaskData()
        },
        methods: {
            ...mapActions('task/', [
                'getTaskInstanceData'
            ]),
            async getTaskData () {
                try {
                    this.taskDataLoading = true
                    const instanceData = await this.getTaskInstanceData(this.instance_id)
                    const { flow_type, current_flow, pipeline_tree, name, template_id, template_source, auth_actions } = instanceData
                    if (this.isFunctional && current_flow === 'func_claim') {
                        this.showParamsFill = true
                    } else {
                        this.primaryTitle = document.title
                        document.title = name
                    }
                    this.instanceFlow = pipeline_tree
                    this.instanceName = name
                    this.templateId = template_id
                    this.templateSource = template_source
                    this.instanceActions = auth_actions
                    // 职能化任务通过普通任务执行链接访问时，重定向到职能化任务链接
                    if (this.$route.name === 'taskExecute' && flow_type === 'common_func') {
                        this.$router.replace({
                            name: 'functionTaskExecute',
                            params: { project_id: this.project_id },
                            query: { instance_id: this.$route.query.instance_id }
                        })
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.taskDataLoading = false
                }
            }
        },
        // 离开任务执行页面时，还原页面的title、icon
        beforeRouteLeave (to, from, next) {
            document.title = this.primaryTitle
            dom.setPageTabIcon(`${window.SITE_URL}static/core/images/bk_sops.png`)
            next()
        }
    }
</script>
<style lang="scss" scoped>
    .task-execute-container {
        height: 100%;
        background: #f4f7fa;
    }
    /deep/ .task-management-page {
        .canvas-wrapper.jsflow .tool-panel-wrap {
            left: 20px;
        }
    }
</style>
