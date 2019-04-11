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
    <div class="param-fill-wrapper" v-bkloading="{isLoading: templateLoading, opacity: 1}" v-show="!templateLoading">
        <div :class="['task-info', {'functor-task-info': this.userType === 'functor'}]">
            <span class="task-info-title">{{ i18n.taskInfo }}</span>
            <div class="task-info-division-line"></div>
            <div class="common-form-item">
                <label class="required">{{ i18n.taskName }}</label>
                <div class="common-form-content">
                    <BaseInput
                        class="step-form-content-size"
                        name="taskName"
                        v-model="taskName"
                        v-validate="taskNameRule">
                    </BaseInput>
                    <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                </div>
            </div>
            <div class="common-form-item" v-if="isStartNowShow">
                <label class="required">{{i18n.startMethod}}</label>
                <div class="common-form-content">
                    <div class="bk-button-group">
                        <bk-button
                            @click="onChangeStartNow(true)"
                            :type="!isStartNow ? 'default' : 'primary'">
                            {{ i18n.startNow }}
                        </bk-button>
                        <bk-button
                            @click="onChangeStartNow(false)"
                            :type="!isStartNow ? 'primary' : 'default'">
                            {{ i18n.periodicStart }}
                        </bk-button>
                    </div>
                </div>
            </div>
            <div class="common-form-item" v-if="isTaskTypeShow">
                <label class="required">{{ i18n.flowType }}</label>
                <div class="common-form-content">
                    <div class="bk-button-group">
                        <bk-button
                            @click="onSwitchTaskType(false)"
                            :type="isSelectFunctionalType ? 'default' : 'primary'">
                            {{ i18n.defaultFlowType }}
                        </bk-button>
                        <bk-button
                            @click="onSwitchTaskType(true)"
                            :type="isSelectFunctionalType ? 'primary' : 'default'">
                            {{ i18n.functionFlowType }}
                        </bk-button>
                    </div>
                </div>
            </div>
            <div class="common-form-item" v-if="!isStartNow">
                <label class="required">{{i18n.periodicCron}}</label>
                <div class="common-form-content step-form-item-cron">
                    <BaseInput
                        class="step-form-content-size"
                        name="periodicCron"
                        v-model="periodicCron"
                        v-validate="periodicRule"/>
                    <bk-tooltip placement="left-end" class="periodic-img-tooltip" v-if="!templateLoading">
                        <i class="common-icon-tooltips"></i>
                        <div slot="content">
                            <img :src="periodicCronImg" class="">
                        </div>
                    </bk-tooltip>
                    <span v-show="errors.has('periodicCron')" class="common-error-tip error-msg">{{ errors.first('periodicCron') }}</span>
                </div>
            </div>
        </div>
        <div class="param-info">
            <div class="param-info-title">
                <span>
                    {{ i18n.paramsInfo }}
                </span>
            </div>
            <div class="param-info-division-line"></div>
            <template >
                <TaskParamEdit
                    v-if="!taskParamEditLoading"
                    ref="TaskParamEdit"
                    :constants="pipelineData.constants"
                    @onChangeConfigLoading="onChangeConfigLoading">
                </TaskParamEdit>
            </template>
        </div>
        <div class="action-wrapper" v-if="!templateLoading">
            <bk-button
                class="preview-step-button"
                @click="onGotoSelectNode">
                {{ i18n.previous }}
            </bk-button>
            <bk-button
                class="next-step-button"
                type="success"
                :loading="isSubmit"
                @click="onCreateTask">
                {{i18n.new}}
            </bk-button>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
// moment用于时区使用
import moment from 'moment-timezone'
import { mapState, mapActions, mapMutations } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { NAME_REG, PERIODIC_REG, STRING_LENGTH } from '@/constants/index.js'
import tools from '@/utils/tools.js'
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
    props: ['cc_id', 'template_id', 'common', 'previewData'],
    data () {
        return {
            i18n: {
                taskInfo: gettext('任务信息'),
                taskName: gettext('任务名称'),
                flowType: gettext('流程类型'),
                defaultFlowType: gettext('默认任务流程'),
                functionFlowType: gettext('职能化任务流程'),
                paramsInfo: gettext('参数信息'),
                previous: gettext('上一步'),
                new: gettext('下一步'),
                startNow: gettext('立即执行'),
                periodicStart: gettext('周期执行'),
                periodicCron: gettext('周期表达式'),
                startMethod: gettext('执行计划')
            },
            templateLoading: true,
            bkMessageInstance: null,
            isSubmit: false,
            isSelectFunctionalType: false,
            taskName: '',
            pipelineData: {},
            taskNameRule: {
                required: true,
                max: STRING_LENGTH.TASK_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            isStartNow: true,
            periodicCron: '*/5 * * * *',
            periodicRule: {
                required: true,
                regex: PERIODIC_REG
            },
            periodicCronImg: require('@/assets/images/' + gettext('task-zh') + '.png'),
            lastTaskName: '',
            node: {},
            templateData: {},
            configLoading: true,
            taskParamEditLoading: true
        }
    },
    computed: {
        ...mapState({
            'templateName': state => state.template.name,
            'userType': state => state.userType,
            'viewMode': state => state.view_mode,
            'app_id': state => state.app_id,
            'businessTimezone': state => state.businessTimezone
        }),
        isSchemeShow () {
            return this.pipelineData.location.some(item => item.optional)
        },
        isTaskTypeShow () {
            return this.userType !== 'functor' && this.isStartNow
        },
        isVariableEmpty () {
            return !this.pipelineData.constants || Object.keys(this.pipelineData.constants).length === 0
        },
        isStartNowShow () {
            return !this.common && this.viewMode === 'app' && this.userType !== 'functor'
        }
    },
    watch: {
        configLoading (loading){
            if (!loading) {
                this.templateLoading = false
            }
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
        ...mapActions('periodic/',[
            'createPeriodic'
        ]),
        async loadData () {
            this.templateLoading = true
            try {
                const data = {
                    templateId: this.template_id,
                    common: this.common
                }
                const templateSource = this.common ? 'common' : 'business'
                const templateData = await this.loadTemplateData(data)
                this.setTemplateData(templateData)
                // 用户直接刷新当前页面 可选数据丢失，可直接获取pipelineTree
                if (this.previewData.length === 0) {
                    const params = {
                        templateId: this.template_id,
                        excludeTaskNodesId: JSON.stringify([]),
                        common: this.common,
                        cc_id: this.cc_id,
                        template_source: templateSource,
                        version: templateData.version
                    }
                    const previewData = await this.loadPreviewNodeData(params)
                    this.pipelineData = previewData.data.pipeline_tree
                } else {
                    this.pipelineData = tools.deepClone(this.previewData)
                }
                this.taskName = this.getDefaultTaskName()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.taskParamEditLoading = false
            }
        },
        getDefaultTaskName () {
            let nowTime = ''
            if (this.common) {
                // 无时区的公共流程使用本地的时间
                nowTime = moment().format('YYYYMMDDHHmmss')
            } else {
                nowTime = moment.tz(this.businessTimezone).format('YYYYMMDDHHmmss')
            }
            return this.templateName + '_' + nowTime
        },
        onSwitchTaskType (isSelectFunctionalType) {
            this.isSelectFunctionalType = isSelectFunctionalType
            this.$emit('setFunctionalStep', isSelectFunctionalType)
        },
        onGotoSelectNode () {
            this.$emit('setFunctionalStep', false)
            if (this.viewMode === 'appmaker') {
                this.$router.push({path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/selectnode/`, query: {'template_id': this.template_id}})
            } else {
                if (this.common) {
                    this.$router.push({path: `/template/newtask/${this.cc_id}/selectnode/`, query: {'template_id': this.template_id, common: this.common}})
                } else {
                    this.$router.push({path: `/template/newtask/${this.cc_id}/selectnode/`, query: {'template_id': this.template_id}})
                }
            }
        },
        onCreateTask () {
            if (this.isSubmit) return
            const paramEditComp = this.$refs.TaskParamEdit
            this.$validator.validateAll().then(async (result) => {
                let formValid = true
                const pipelineData = tools.deepClone(this.pipelineData)
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
                if (this.isStartNow) {
                    const data = {
                        'name': this.taskName,
                        'description': '',
                        'templateId': this.template_id,
                        'execData': JSON.stringify(pipelineData),
                        'flowType': flowType,
                        'common': this.common
                    }
                    try {
                        const taskData = await this.createTask(data)

                        if (this.viewMode === 'appmaker') {
                            if (this.isSelectFunctionalType) {
                                this.$router.push({path: `/appmaker/${this.app_id}/task_home/${this.cc_id}/`})
                            } else {
                                this.$router.push({path: `/appmaker/${this.app_id}/execute/${this.cc_id}/`, query: {instance_id: taskData.instance_id}})
                            }
                        } else if (this.isSelectFunctionalType) {
                            if (this.common) {
                                this.$router.push({path: `/taskflow/home/${this.cc_id}/`, query: {common: this.common}})
                            } else {
                                this.$router.push({path: `/taskflow/home/${this.cc_id}/`})
                            }
                        } else {
                            this.$router.push({path: `/taskflow/execute/${this.cc_id}/`, query: {instance_id: taskData.instance_id}})
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    }
                } else {
                    // 创建周期任务
                    const cronArray = this.periodicCron.split(' ')
                    const cron = JSON.stringify({
                        'minute': cronArray[0],
                        'hour': cronArray[1],
                        'day_of_week': cronArray[2],
                        'day_of_month': cronArray[3],
                        'month_of_year': cronArray[4]
                    })
                    const data = {
                        'name': this.taskName,
                        'cron': cron,
                        'templateId': this.template_id,
                        'execData': JSON.stringify(pipelineData)
                    }
                    const periodicData = await this.createPeriodic(data)
                    this.$bkMessage({
                        'message': gettext('创建周期任务成功'),
                        'theme': 'success'
                    })
                    this.$router.push({path: `/periodic/home/${this.cc_id}/`})
                }
            })
        },
        onChangeStartNow (value) {
            if (value === this.isStartNow) {
                return
            }
            this.isStartNow = value
            this.$emit('setPeriodicStep', {'periodicType': value, 'functionalType': this.isSelectFunctionalType})
            if (!value) {
                this.lastTaskName = this.taskName
                this.taskName = this.templateName
            } else {
                this.taskName = this.lastTaskName
            }
        },
        onChangeConfigLoading (loading) {
            this.configLoading = loading
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.param-fill-wrapper {
    margin: 0 40px;
    padding-top: 30px;
    width: calc(100% - 80px);
    @media screen and (max-width: 1300px){
        width: calc(100% - 80px);
    }
    /deep/ .no-data-wrapper {
        margin: 50px 0;
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
.common-section-title {
    margin-bottom: 24px;
}
.task-param-wrapper {
    width: 720px;
}
.bk-button-group {
    .bk-button {
        width: 150px;
        margin: 0px;
    }
    .bk-button.bk-primary {
        position: relative;
        z-index: 4;
        color: #3a84ff;
        background-color: #c7dcff;
        border-radius: 2px;
        border:1px solid #3a84ff;
    }
    .bk-button:last-child {
        margin-left: -1px;
    }
}
.periodic-img-tooltip {
    position: relative;
    bottom: -6px;
    left: 5px;
    color: #c4c6cc;
    font-size: 14px;
    &:hover {
        color: #f4aa1a;
    }
    /deep/ .bk-tooltip-arrow {
        display: none;
    }
}
.startnow-form-content, .periodic-form-content {
    margin-top: 10px;
}
.radio-input {
    margin-right: 30px;
}
.step-form-content-size {
    max-width: 500px;
}
/deep/ .bk-tooltip-inner {
    max-width: 600px;
    border:1px solid #c4c6cc;
    background-color: #ffffff;
}
.step-form-content {
    /deep/ .bk-tooltip-arrow {
        position: absolute;
        bottom: 6px;
    }
    img {
        position: relative;
        bottom: -4px;
        left: 13px;
        background-color: $whiteDefault;
        border: 1px solid #dddddd;
    }
}
.step-form-item-cron {
    input {
        vertical-align: top;
    }
}
.action-wrapper {
    border-top: 1px solid #cacedb;
    background-color: #ffffff;
    margin: 0 -40px;
    button {
        margin-top: -7px;
    }
    .preview-step-button {
        padding: 0px;
        margin-left: 40px;
        width: 90px;
        height: 32px;
        line-height: 32px;
        color: #313238;
    }
    .next-step-button {
        width: 140px;
        height: 32px;
        line-height: 32px;
        background-color: #2dcb56;
        border-color: #2dcb56;
    }
}
/deep/ .el-input {
    .el-input__inner {
        max-width: 500px;
        height: 36px;
    }
}
/deep/ .el-textarea {
    .el-textarea__inner {
        width: 500px;
    }
}
/deep/ .el-select {
    max-width: 500px;
}
</style>
