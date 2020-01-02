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
    <div :class="{
        'task-create-container': true,
        'fill-height': currentStep === 'selectnode'
    }">
        <TaskStep
            :cc_id="cc_id"
            :list="stepList"
            :common="common"
            :template_id="template_id"
            :task-status="'TaskCreate'"
            :current-step="currentStep">
        </TaskStep>
        <component
            :ref="currentComponent"
            :is="currentComponent"
            :current-step="currentStep"
            :cc_id="cc_id"
            :common="common"
            :entrance="entrance"
            :template_id="template_id"
            :exclude-node="excludeNode"
            :preview-data="previewData"
            @setFunctionalStep="setFunctionalStep"
            @setPeriodicStep="setPeriodicStep"
            @setPreviewData="setPreviewData"
            @setExcludeNode="setExcludeNode">
        </component>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    import TaskStep from '../TaskStep.vue'
    import TaskSelectNode from './TaskSelectNode.vue'
    import TaskParamFill from './TaskParamFill.vue'
    import tools from '@/utils/tools.js'

    const STEP_DICT = [
        {
            step: 'selectnode',
            name: gettext('节点选择'),
            component: 'TaskSelectNode'
        },
        {
            step: 'paramfill',
            name: gettext('参数填写'),
            component: 'TaskParamFill'
        },
        {
            step: 'taskexecute',
            name: gettext('任务执行')
        }
    ]
    export default {
        name: 'TaskCreate',
        components: {
            TaskStep,
            TaskSelectNode,
            TaskParamFill
        },
        props: ['template_id', 'cc_id', 'step', 'common', 'entrance'],
        data () {
            return {
                stepList: STEP_DICT.slice(),
                hasFunctionalStep: false,
                hasPeriodicTask: false,
                previewData: [],
                excludeNode: []
            }
        },
        computed: {
            ...mapState({
                locations: state => state.template.location,
                lines: state => state.template.line,
                userType: state => state.userType
            }),
            currentStep () {
                return this.step || 'selectnode'
            },
            currentComponent () {
                return this.stepList.filter(item => item.step === this.currentStep)[0].component
            }
        },
        watch: {
            hasFunctionalStep (val) {
                if (val) {
                    this.appendFunctionalization()
                } else {
                    let stepIndex
                    this.stepList.some((item, index) => {
                        if (item.step === 'functionalization') {
                            stepIndex = index
                            return true
                        }
                    })
                    if (stepIndex) {
                        this.stepList.splice(stepIndex, 1)
                    }
                }
            },
            hasPeriodicTask (val) {
                const taskExecution = {
                    step: 'taskexecute',
                    name: gettext('任务执行')
                }
                if (!val) {
                    this.stepList.push(taskExecution)
                } else if (!val.periodicType) {
                    this.deletePeriodicCurrentStep()
                } else if (val.periodicType && val.functionalType) {
                    this.stepList.splice(2, 0, {
                        step: 'functionalization',
                        name: gettext('职能化认领'),
                        component: 'TaskParamFill'
                    })
                    this.stepList.push(taskExecution)
                } else {
                    this.stepList.push(taskExecution)
                }
            }
        },
        mounted () {
            if (this.userType === 'functor') {
                this.setFunctionalStep(true)
            }
            if (this.entrance === 'periodicTask') {
                this.deletePeriodicCurrentStep()
            }
        },
        methods: {
            appendFunctionalization () {
                this.stepList.splice(2, 0, {
                    step: 'functionalization',
                    name: gettext('职能化认领'),
                    component: 'TaskParamFill'
                })
            },
            setFunctionalStep (isSelectFunctionalType) {
                this.hasFunctionalStep = isSelectFunctionalType
            },
            setPeriodicStep (isSelectPeriodicType) {
                this.hasPeriodicTask = isSelectPeriodicType
            },
            deletePeriodicCurrentStep () {
                while (this.stepList.length !== 2) {
                    this.stepList.pop()
                }
            },
            setPreviewData (previewData) {
                this.previewData = tools.deepClone(previewData)
            },
            setExcludeNode (excludeNode) {
                this.excludeNode = excludeNode
            }
        }
    }
</script>
<style lang="scss" scoped>
    .task-create-container {
       min-width: 1320px;
        &.fill-height {
            height: calc(100% - 50px);
        }
        /deep/ .action-wrapper {
            height: 72px;
            line-height: 72px;
            text-align: left;
        }
    }
</style>
