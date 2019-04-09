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
    <div class="functionalization-wrapper">
        <div :class="['task-info', {'functor-task-info': this.userType === 'functor'}]">
            <span class="task-info-title">{{ i18n.task_info }}</span>
            <div class="task-info-division-line"></div>
            <div class="common-form-item">
                <label class="required">{{ i18n.taskName }}</label>
                <div class="common-form-content">
                    <BaseInput
                        class="common-form-content-size"
                        name="taskName"
                        v-model="name"
                        v-validate="taskNameRule">
                    </BaseInput>
                    <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                </div>
            </div>
        </div>
        <div class="param-info">
            <div class="param-info-title">
                <span>
                    {{ i18n.params }}
                </span>
            </div>
            <div class="param-info-division-line"></div>
            <NoData v-if="isVariableEmpty"></NoData>
            <TaskParamEdit
                v-else
                ref="TaskParamEdit"
                :constants="pipelineData.constants">
            </TaskParamEdit>
        </div>
         <div class="action-wrapper">
            <bk-button
                class="preview-button"
                @click="onShowPreviewDialog">
                {{ i18n.preview }}
            </bk-button>
            <bk-button
                class="task-claim-button"
                type="success"
                :loading="isSubmit"
                @click="onTaskClaim">
                {{ i18n.claim }}
            </bk-button>
        </div>
        <bk-dialog
            v-if="previewDialogShow"
            :quick-close="false"
            :has-header="true"
            :has-footer="false"
            :ext-cls="'common-dialog'"
            :title="i18n.taskPreview"
            width="1000"
            padding="0px"
            :is-show.sync="previewDialogShow"
            @cancel="onCancel">
            <div slot="content">
                <NodePreview
                    ref="nodePreviewRef"
                    :previewDataLoading="previewDataLoading"
                    :canvasData="formatCanvasData(previewData)"
                    :previewBread="previewBread"
                    @onNodeClick="onNodeClick"
                    @onSelectSubflow="onSelectSubflow">
                </NodePreview>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapActions, mapMutations } from 'vuex'
import tools from '@/utils/tools.js'
import { errorHandler } from '@/utils/errorHandler.js'
import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
import NoData from '@/components/common/base/NoData.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
import TaskParamEdit from '../TaskParamEdit.vue'
import NodePreview from '../NodePreview.vue'

export default {
    name: 'TaskFunctionalization',
    inject: ['reload'],
    components: {
        NoData,
        BaseInput,
        TaskParamEdit,
        NodePreview
    },
    props: ['cc_id','template_id','instance_id', 'instanceFlow', 'instanceName'],
    data () {
        return {
            i18n: {
                task_info: gettext('任务信息'),
                taskName: gettext('任务名称'),
                params: gettext('参数信息'),
                preview: gettext('预览'),
                claim: gettext('认领'),
                taskPreview: gettext('任务流程预览')
            },
            isSubmit: false,
            previewDialogShow: false,
            previewDataLoading: false,
            name: this.instanceName,
            nodeSwitching: false,
            pipelineData: JSON.parse(this.instanceFlow),
            previewData: JSON.parse(this.instanceFlow),
            taskNameRule: {
                required: true,
                max: STRING_LENGTH.TASK_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            previewBread: []
        }
    },
    computed: {
        ...mapState({
            'userType': state => state.userType
        }),
        isVariableEmpty () {
            return Object.keys(this.pipelineData.constants).length === 0
        }
    },
    methods: {
        ...mapActions('task/', [
            'claimFuncTask'
        ]),
        formatCanvasData (pipelineData) {
            const {lines, locations, gateways} = pipelineData
            const branchConditions = {}
            for (let gKey in gateways) {
                const item = gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            return {
                lines: pipelineData.line,
                locations: pipelineData.location.map(item => {return {...item, mode: 'preview', checked: true}}),
                branchConditions
            }
        },
        updateCanvas () {
            this.previewDataLoading = true
            this.$nextTick(() => {
                this.previewDataLoading = false
            })
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
                        this.reload()
                    } else {
                        errorHandler(e, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isSubmit = false
                }
            })
        },
        onShowPreviewDialog () {
            this.previewBread.push({
                name: this.name,
                data: this.previewData
            })
            this.previewDialogShow = true
        },
        onCancel () {
            this.previewDialogShow = false
            this.previewDataLoading = false
            this.previewData = tools.deepClone(this.pipelineData)
            this.previewBread = []
        },
        onSelectSubflow (data, index) {
            this.previewData = data
            this.previewBread.splice(index + 1)
            this.updateCanvas()
        },
        onNodeClick (id) {
            const activity = this.previewData.activities[id]
            if (!activity || activity.type !== 'SubProcess') {
                return
            }
            
            const templateId = activity.template_id
            const previewData = activity.pipeline
            this.previewBread.push({
                data: previewData,
                name: activity.name
            })
            this.previewData = previewData
            this.updateCanvas()
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.functionalization-wrapper {
    margin: 0 40px;
    padding-top: 30px;
    width: calc(100% - 80px);
    background-color: #ffffff;
    @media screen and (max-width: 1300px){
        width: calc(100% - 80px);
    }
    /deep/ .no-data-wrapper {
        margin: 100px 0;
    }
    .operation-header {
        margin-top: -20px;
        padding: 0 0 0 10px;
        height: 50px;
        border-bottom: 1px solid $commonBorderColor;
        line-height: 50px;
        background-color: $commonBgColor;
    .bread-crumbs-wrapper {
        display: inline-block;
        font-size: 14px;
        .path-item {
            display: inline-block;
            .node-name {
                margin: 0 4px;
                color: $blueDefault;
                cursor: pointer;
            }
            &:last-child {
                .node-name {
                    cursor: pointer;
                    &:last-child {
                        color: $greyDefault;
                        cursor: text;
                    }
                }
            }
        }
    }
    .operation-container {
        float: right;
        .operation-btn {
            float: left;
            width: 60px;
            height: 49px;
            line-height: 49px;
            font-size: 22px;
            text-align: center;
            color: $greyDisable;
            &.clickable {
                color: $greyDefault;
                cursor: pointer;
                &:hover {
                    color: $greenDefault;
                }
                &.actived {
                    color: $greenDefault;
                    background: $whiteDefault;
                }
            }
            &.common-icon-dark-paper {
                border-left: 1px solid $commonBorderColor;
            }
        }
    }
}
}
.task-info, .param-info {
    margin-top: 15px;
    padding-bottom: 20px;
    .task-info-title, .param-info-title {
        font-size: 14px;
        font-weight: 600;
        color: #313238;
    }
    .task-info-division-line, .param-info-division-line {
        margin: 5px 0 30px;
        height: 1px;
        border: 0px;
        background-color: #cacedb;
    }
    .common-form-item {
        label {
            color: #313238;
            font-weight: normal;
        }
    }
}
.param-info  {
    padding-bottom: 80px;
}
.functor-task-info {
    padding-bottom: 0px;
}
.task-param-wrapper {
    width: 720px;
}
.action-wrapper {
    height: 72px;
    line-height: 72px;
    margin: 0 -40px;
    border-top: 1px solid #cacedb;
    background-color: #ffffff;
    text-align: left;
    button {
        margin-top: -7px;
    }
    .preview-button {
        padding: 0px;
        margin-left: 40px;
        width: 90px;
        height: 32px;
        line-height: 32px;
        color: #313238;
    }
    .task-claim-button {
        width: 140px;
        height: 32px;
        line-height: 32px;
        background-color: #2dcb56;
        border-color: #2dcb56;
    }
}
.step-form-content-size {
    max-width: 500px;
}
/deep/ .el-input {
    .el-input__inner {
        max-width: 500px;
    }
}
/deep/ .el-textarea {
    .el-textarea__inner {
        width: 500px;
    }
}
/deep/ .bk-dialog-body {
    background-color: #f4f7fa;
}
/deep/ .pipeline-canvas{
    .tool-wrapper {
        top: 20px;
        left: 40px;
    }
}
</style>
