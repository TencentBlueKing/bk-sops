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
    <div class="task-create-container">
        <task-create-header
            :title="$store.state.view_mode !== 'appmaker' ? $t('新建任务') : ''"
            :common="common"
            :steps="stepList"
            :current-step="curStepIndex"
            :project_id="project_id"
            :template_id="template_id">
        </task-create-header>
        <task-select-node
            v-if="currentStep === 'selectnode'"
            :project_id="project_id"
            :common="common"
            :entrance="entrance"
            :template_id="template_id"
            :exclude-node="excludeNode"
            @setExcludeNode="setExcludeNode">
        </task-select-node>
        <task-param-fill
            v-if="currentStep === 'paramfill'"
            :project_id="project_id"
            :common="common"
            :entrance="entrance"
            :template_id="template_id"
            :exclude-node="excludeNode"
            @togglePeriodicStep="togglePeriodicStep"
            @toggleFunctionalStep="toggleFunctionalStep"
            @setExcludeNode="setExcludeNode">
        </task-param-fill>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import TaskCreateHeader from '../TaskCreateHeader.vue'
    import TaskSelectNode from './TaskSelectNode.vue'
    import TaskParamFill from './TaskParamFill.vue'

    const STEP_DICT = [
        {
            step: 'selectnode',
            title: i18n.t('选择节点')
        },
        {
            step: 'paramfill',
            title: i18n.t('填写参数')
        },
        {
            step: 'taskexecute',
            title: i18n.t('去执行')
        }
    ]
    export default {
        name: 'TaskCreate',
        components: {
            TaskCreateHeader,
            TaskSelectNode,
            TaskParamFill
        },
        props: {
            template_id: [String, Number],
            project_id: [String, Number],
            step: String,
            common: [String, Number],
            entrance: String
        },
        data () {
            return {
                stepList: this.addStepIcon(STEP_DICT),
                currentStep: this.$route.params.step,
                excludeNode: []
            }
        },
        computed: {
            curStepIndex () {
                return this.stepList.findIndex(item => item.step === this.currentStep) + 1
            }
        },
        watch: {
            '$route.params.step' (val) {
                if (val === 'selectnode' && this.$route.name !== 'functionTemplateStep') {
                    this.stepList = this.addStepIcon(STEP_DICT)
                }
                this.currentStep = val
            }
        },
        created () {
            if (this.$route.name === 'functionTemplateStep') {
                this.toggleFunctionalStep(true)
            }
        },
        methods: {
            addStepIcon (steps) {
                return steps.map((item, index) => Object.assign({}, item, { icon: index + 1 }))
            },
            togglePeriodicStep (isPeriodicTask, isFunctional) {
                let steps = STEP_DICT.slice()
                if (isPeriodicTask) {
                    steps = STEP_DICT.filter(item => ['selectnode', 'paramfill'].includes(item.step))
                } else if (isFunctional) {
                    this.toggleFunctionalStep(true)
                    return
                }
                this.stepList = this.addStepIcon(steps)
            },
            toggleFunctionalStep (isFunctionalTask) {
                const steps = STEP_DICT.slice()
                if (isFunctionalTask) {
                    steps.splice(2, 0, {
                        step: 'functionalization',
                        title: i18n.t('职能化认领')
                    })
                }
                this.stepList = this.addStepIcon(steps)
            },
            setExcludeNode (excludeNode) {
                this.excludeNode = excludeNode
            }
        }
    }
</script>
<style lang="scss" scoped>
    .task-create-container {
       height: calc(100vh - 52px);
    }
</style>
