/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="functionalization-wrapper">
        <div class="task-info">
            <h3 class="common-section-title">{{ i18n.task_info }}</h3>
            <div class="common-form-item">
                <label>{{ i18n.task_name }}</label>
                <div class="common-form-content">
                    <BaseInput
                        name="taskName"
                        v-model="name"
                        v-validate="taskNameRule">
                    </BaseInput>
                    <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                </div>
            </div>
        </div>
        <div class="param-info">
            <h3 class="common-section-title">{{ i18n.params }}</h3>
            <NoData v-if="isVariableEmpty"></NoData>
            <TaskParamEdit
                v-else
                ref="TaskParamEdit"
                :constants="pipelineData.constants">
            </TaskParamEdit>
        </div>
         <div class="action-wrapper">
            <bk-button
                @click="onShowPreviewDialog">
                {{ i18n.preview }}
            </bk-button>
            <bk-button type="success" @click="onTaskClaim">{{ i18n.claim }}</bk-button>
        </div>
        <bk-dialog
            v-if="previewDialogShow"
            :quick-close="false"
            :has-header="true"
            :has-footer="false"
            :ext-cls="'common-dialog'"
            :title="i18n.task_preview"
            width="1000"
            :is-show.sync="previewDialogShow"
            @cancel="onCancel">
            <div slot="content">
                <NodePreview :canvasData="canvasData"></NodePreview>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import moment from 'moment'
import { mapState, mapActions, mapMutations } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { NAME_REG } from '@/constants/index.js'
import NoData from '@/components/common/base/NoData.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import TaskParamEdit from '../TaskParamEdit.vue'
import NodePreview from '../NodePreview.vue'

export default {
    name: 'TaskFunctionalization',
    components: {
        NoData,
        BaseInput,
        TaskParamEdit,
        NodePreview
    },
    props: ['cc_id', 'instance_id', 'instanceFlow', 'instanceName'],
    data () {
        return {
            i18n: {
                task_info: gettext("任务信息"),
                task_name: gettext("任务名称"),
                params: gettext("参数信息"),
                preview: gettext("预览"),
                claim: gettext("认领"),
                task_preview: gettext("任务流程预览")
            },
            isSubmit: false,
            previewDialogShow: false,
            name: this.instanceName,
            pipelineData: JSON.parse(this.instanceFlow),
            taskNameRule: {
                required: true,
                max: 50,
                regex: NAME_REG
            }
        }
    },
    computed: {
        canvasData () {
            const {lines, locations, gateways} = this.pipelineData
            const branchConditions = {}
            for (let gKey in gateways) {
                const item = gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            return {
                lines: this.pipelineData.line,
                locations: this.pipelineData.location.map(item => {return {...item, model: 'preview', checked: true}}),
                branchConditions
            }

        },
        isVariableEmpty () {
            return Object.keys(this.pipelineData.constants).length === 0
        }
    },
    methods: {
        ...mapActions('task/', [
            'claimFuncTask'
        ]),
        onShowPreviewDialog () {
            this.previewDialogShow = true
        },
        onCancel () {
            this.previewDialogShow = false
        },
        onTaskClaim () {
            if (this.isSubmit) return
            this.isSubmit = true
            this.$validator.validateAll().then(async (result) => {
                if (!result) return
                const formData = {}
                if (this.$refs.TaskParamEdit) {
                    const variables = this.$refs.TaskParamEdit.getVariableData()
                    for (let key in variables) {
                        formData[key] = variables[key].value
                    }
                }
                const data = {
                    name: this.name,
                    instance_id: this.instance_id,
                    constants: JSON.stringify(formData)
                }
                try {
                    const res = await this.claimFuncTask(data)
                    if (res.result) {
                        window.location.reload()
                    } else {
                        errorHandler(e, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            })
        }
    }
}
</script>
<style lang="scss" scoped>
.functionalization-wrapper {
    margin: 0 auto;
    padding-top: 30px;
    width: 1200px;
    /deep/ .no-data-wrapper {
        margin: 100px 0;
    }
}
.task-info {
    padding-bottom: 40px;
}
.common-section-title {
    margin-bottom: 24px;
}
.action-wrapper {
    margin: 40px 0;
    text-align: center;
}
</style>
