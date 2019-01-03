/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div :class="{
        'task-create-container': true,
        'fill-height': currentStep === 'selectnode'
    }">
        <TaskStep
            :list="stepList"
            :currentStep="currentStep">
        </TaskStep>
        <component
            :ref="currentComponent"
            :is="currentComponent"
            :currentStep="currentStep"
            :cc_id="cc_id"
            :template_id="template_id"
            :excludeNode="excludeNode"
            @setFunctionalStep="setFunctionalStep"
            @setExcludeNode="setExcludeNode">
        </component>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import TaskStep from '../TaskStep.vue'
import TaskSelectNode from './TaskSelectNode.vue'
import TaskParamFill from './TaskParamFill.vue'
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
    props: ['template_id', 'cc_id', 'step'],
    data () {
        return {
            stepList: STEP_DICT,
            excludeNode: [],
            hasFunctionalStep: false
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
        }
    },
    mounted () {
        if (this.userType === 'functor') {
            this.setFunctionalStep(true)
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
        setExcludeNode (excludeNode) {
            this.excludeNode = excludeNode
        }
    }
}
</script>
<style lang="scss" scoped>
    .task-create-container {
        min-width: 1200px;
        &.fill-height {
            height: calc(100% - 60px);
        }
        /deep/ .action-wrapper {
            height: 90px;
            line-height: 90px;
            text-align: center;
        }
    }

</style>
