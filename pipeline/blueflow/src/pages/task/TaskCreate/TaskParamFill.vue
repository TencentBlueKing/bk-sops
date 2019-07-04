/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="param-fill-wrapper" v-bkloading="{isLoading: loading, opacity: 1}">
        <div class="task-info">
            <h3 class="common-section-title">{{ i18n.task_info }}</h3>
            <div class="common-form-item">
                <label>{{ i18n.task_name }}</label>
                <div class="common-form-content">
                    <BaseInput
                        name="taskName"
                        v-model="taskName"
                        v-validate="taskNameRule">
                    </BaseInput>
                    <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                </div>
            </div>
            <div class="common-form-item" v-if="isTaskTypeShow">
                <label>{{ i18n.flow_type }}</label>
                <div class="common-form-content">
                    <div class="bk-button-group">
                        <bk-button
                            @click="onSwitchTaskType(false)"
                            :type="isSelectFunctionalType ? 'default' : 'primary'">
                            {{ i18n.default_flow_type }}
                        </bk-button>
                        <bk-button
                            @click="onSwitchTaskType(true)"
                            :type="isSelectFunctionalType ? 'primary' : 'default'">
                            {{ i18n.function_flow_type }}
                        </bk-button>
                    </div>
                </div>
            </div>
        </div>
        <div class="param-info">
            <h3 class="common-section-title">{{ i18n.params_info }}</h3>
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
            <bk-button
                type="primary"
                @click="onGotoSelectNode">
                {{ i18n.previous }}
            </bk-button>
            <bk-button type="success" @click="onCreateTask">{{ i18n.new }}</bk-button>
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
                <NodePreview
                    :canvasData="canvasData"
                    :loading="loading">
                </NodePreview>
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
    name: 'TaskParamFill',
    components: {
        NoData,
        BaseInput,
        TaskParamEdit,
        NodePreview
    },
    props: ['cc_id', 'template_id', 'excludeNode'],
    data () {
        return {
            i18n: {
                task_info: gettext("任务信息"),
                task_name: gettext("任务名称"),
                flow_type: gettext("流程类型"),
                default_flow_type: gettext("默认任务流程"),
                function_flow_type: gettext("职能化任务流程"),
                params_info: gettext("参数信息"),
                preview: gettext("预览"),
                previous: gettext("上一步"),
                new: gettext("新建"),
                task_preview: gettext("任务流程预览")
            },
            loading: true,
            bkMessageInstance: null,
            previewDataLoading: true,
            isSubmit: false,
            isSelectFunctionalType: false,
            previewDialogShow: false,
            taskName: '',
            pipelineData: {
                location: [],
                line: [],
                gateways: {},
                constants: []
            },
            taskNameRule: {
                required: true,
                max: 50,
                regex: NAME_REG
            }
        }
    },
    computed: {
        ...mapState({
            'templateName': state => state.template.name,
            'userType': state => state.userType,
            'viewMode': state => state.view_mode,
            'run_ver': state => state.run_ver,
            'app_id': state => state.app_id
        }),
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
                locations: this.pipelineData.location.map(item => {return {...item, mode: 'preview', checked: true}}),
                branchConditions
            }
        },
        isSchemeShow () {
            return this.pipelineData.location.some(item => item.optional)
        },
        isTaskTypeShow () {
            return this.run_ver !== 'community' && this.userType !== 'functor'
        },
        isVariableEmpty () {
            return !this.loading && Object.keys(this.pipelineData.constants).length === 0
        }
    },
    mounted () {
        this.loadData()
    },
    methods: {
        ...mapActions('template/', [
            'loadTemplateData'
        ]),
        ...mapActions('task/', [
            'loadPreviewNodeData',
            'createTask'
        ]),
        ...mapMutations('template/', [
            'setTemplateData'
        ]),
        async loadData () {
            this.loading = true
            try {
                const templateData = await this.loadTemplateData(this.template_id)
                await this.getPreviewNodeData()
                this.setTemplateData(templateData)
                this.taskName = this.getDefaultTaskName()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        async getPreviewNodeData () {
            const params = {
                cc_id: this.cc_id,
                template_id: this.template_id,
                exclude_task_nodes_id: JSON.stringify(this.excludeNode)
            }
            try {
                const resp = await this.loadPreviewNodeData(params)
                if (resp.result) {
                    const previewNodeData = resp.data.pipeline_tree
                    this.setPipelineData(previewNodeData)
                } else {
                    errorHandler(resp, this)
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        setPipelineData (data) {
            this.pipelineData = JSON.parse(JSON.stringify(data))
        },
        getDefaultTaskName () {
            return this.templateName + '_' + moment().format('YYYYMMDDHHmmss')
        },
        onSwitchTaskType (isSelectFunctionalType) {
            this.isSelectFunctionalType = isSelectFunctionalType
            this.$emit('setFunctionalStep', isSelectFunctionalType)
        },
        onShowPreviewDialog () {
            this.previewDialogShow = true
        },
        onCancel () {
            this.previewDialogShow = false
        },
        onGotoSelectNode () {
            this.$emit('setFunctionalStep', false)
            if (this.viewMode === 'appmaker') {
                this.$router.push({path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/selectnode/`, query: {'template_id': this.template_id}})
            } else {
                this.$router.push({path: `/template/newtask/${this.cc_id}/selectnode/`, query: {'template_id': this.template_id}})
            }
        },
        onCreateTask () {
            if (this.isSubmit) return
            const paramEditComp = this.$refs.TaskParamEdit
            this.$validator.validateAll().then(async (result) => {
                let formValid = true
                const pipelineData = JSON.parse(JSON.stringify(this.pipelineData))
                if (paramEditComp) {
                    const formData = paramEditComp.getVariableData()
                    pipelineData.constants = formData
                    formValid = paramEditComp.validate()
                }

                if (!result || !formValid) return

                this.isSubmit = true
                let flowType
                if (this.userType === 'functor') {
                    flowType = 'common_func'
                } else {
                    flowType = this.isSelectFunctionalType ? 'common_func' : 'common'
                }
                const data = {
                    "name": this.taskName,
                    "description": '',
                    "template_id": this.template_id,
                    "exec_data": JSON.stringify(pipelineData),
                    "flow_type": flowType
                }
                try {
                    const taskData = await this.createTask(data)
                    if (this.viewMode === 'appmaker') {
                        if (this.isSelectFunctionalType) {
                            this.$router.push({path: `/appmaker/${this.app_id}/task_home/${this.cc_id}/`})
                            return
                        }
                        this.$router.push({path: `/appmaker/${this.app_id}/execute/${this.cc_id}/`, query: {instance_id: taskData.instance_id}})
                        return
                    }
                    if (this.isSelectFunctionalType) {
                        this.$router.push({path: `/taskflow/home/${this.cc_id}/`})
                    } else {
                        this.$router.push({path: `/taskflow/execute/${this.cc_id}/`, query: {instance_id: taskData.instance_id}})
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
.param-fill-wrapper {
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
.bk-button-group {
    .bk-button {
        width: 138px;
    }
}
</style>
