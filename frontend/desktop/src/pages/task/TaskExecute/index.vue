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
    <div :class="['task-execute-container', { 'task-function-container': currentStep === 'functionalization' }]"
        v-if="!exception.code"
        v-bkloading="{ isLoading: loading, opacity: 1 }">
        <TaskStep
            :list="stepList"
            :current-step="currentStep"
            :task-status="'TaskExecute'"
            :common="common"
            :cc_id="cc_id"
            :instance-name="instanceName"
            :all-finished="isAllStepsFinished">
        </TaskStep>
        <TaskFunctionalization
            v-if="isFunctional && !loading"
            :cc_id="cc_id"
            :instance_id="instance_id"
            :instance-name="instanceName"
            :instance-flow="instanceFlow">
        </TaskFunctionalization>
        <TaskOperation
            v-if="!isFunctional && !loading"
            :cc_id="cc_id"
            :instance_id="instance_id"
            :instance-name="instanceName"
            :instance-flow="instanceFlow"
            :template_id="template_id"
            :template-source="templateSource"
            @taskStatusLoadChange="taskStatusLoadChange">
        </TaskOperation>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import TaskStep from '../TaskStep.vue'
    import TaskOperation from './TaskOperation.vue'
    import TaskFunctionalization from './TaskFunctionalization.vue'
    const STEP_DICT = [
        {
            step: 'selectnode',
            name: gettext('节点选择')
        },
        {
            step: 'paramfill',
            name: gettext('参数填写')
        },
        {
            step: 'taskexecute',
            name: gettext('任务执行')
        }
    ]
    export default {
        name: 'TaskExecute',
        components: {
            TaskStep,
            TaskOperation,
            TaskFunctionalization
        },
        props: ['cc_id', 'instance_id', 'common'],
        data () {
            return {
                taskDataLoading: true,
                taskStatusLoading: true,
                bkMessageInstance: null,
                exception: {},
                stepList: STEP_DICT.slice(),
                currentStep: 'taskexecute',
                isFunctional: false,
                isAllStepsFinished: false,
                instanceName: '',
                instanceFlow: '',
                templateSource: ''
            }
        },
        computed: {
            loading () {
                return this.isFunctional ? this.taskDataLoading : (this.taskDataLoading && this.taskStatusLoading)
            }
        },
        created () {
            this.getTaskData()
        },
        methods: {
            ...mapActions('task/', [
                'getTaskInstanceData'
            ]),
            appendFunctionalization () {
                const isHasFunctionalization = this.stepList.some(item => item.step === 'functionalization')
                if (!isHasFunctionalization) {
                    this.stepList.splice(2, 0, {
                        step: 'functionalization',
                        name: gettext('职能化认领')
                    })
                }
            },
            async getTaskData () {
                try {
                    const instanceData = await this.getTaskInstanceData(this.instance_id)
                    if (instanceData.flow_type === 'common_func') {
                        this.appendFunctionalization()
                        if (instanceData.current_flow === 'func_claim') {
                            this.isFunctional = true
                            this.currentStep = 'functionalization'
                        }
                    }
                    this.instanceFlow = instanceData.pipeline_tree
                    this.instanceName = instanceData.name
                    this.template_id = instanceData.template_id
                    this.templateSource = instanceData.template_source
                    if (instanceData.is_finished) {
                        this.isAllStepsFinished = true
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskDataLoading = false
                }
            },
            taskStatusLoadChange (status) {
                this.taskStatusLoading = status
            }
        }
    }
</script>
<style lang="scss" scoped>
    .task-execute-container {
        height: 100%;
    }
    .task-function-container {
        background-color: #ffffff;
    }
</style>
