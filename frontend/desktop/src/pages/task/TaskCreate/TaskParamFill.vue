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
    <div class="param-fill-wrapper">
        <div :class="['task-info', { 'functor-task-info': userType === 'functor' }]">
            <div class="task-info-title">
                <span>{{ i18n.taskInfo }}</span>
            </div>
            <div>
                <div class="common-form-item">
                    <label class="required">{{ i18n.taskName }}</label>
                    <div class="common-form-content" v-bkloading="{ isLoading: taskMessageLoading, opacity: 1 }">
                        <BaseInput
                            v-model="taskName"
                            v-validate="taskNameRule"
                            class="step-form-content-size"
                            name="taskName">
                        </BaseInput>
                        <span class="common-error-tip error-msg">{{ errors.first('taskName') }}</span>
                    </div>
                </div>
                <div
                    v-if="!isExecuteSchemeHide"
                    class="common-form-item">
                    <label class="required">{{i18n.startMethod}}</label>
                    <div class="common-form-content">
                        <div class="bk-button-group">
                            <bk-button
                                :theme="!isStartNow ? 'default' : 'primary'"
                                @click="onChangeStartNow(true)">
                                {{ i18n.startNow }}
                            </bk-button>
                            <bk-button
                                :theme="!isStartNow ? 'primary' : 'default'"
                                @click="onChangeStartNow(false)">
                                {{ i18n.periodicStart }}
                            </bk-button>
                        </div>
                    </div>
                </div>
                <div
                    v-if="isTaskTypeShow"
                    class="common-form-item">
                    <label class="required">{{ i18n.flowType }}</label>
                    <div class="common-form-content">
                        <div class="bk-button-group">
                            <bk-button
                                :theme="isSelectFunctionalType ? 'default' : 'primary'"
                                @click="onSwitchTaskType(false)">
                                {{ i18n.defaultFlowType }}
                            </bk-button>
                            <bk-button
                                :theme="isSelectFunctionalType ? 'primary' : 'default'"
                                @click="onSwitchTaskType(true)">
                                {{ i18n.functionFlowType }}
                            </bk-button>
                        </div>
                    </div>
                </div>
                <div
                    v-if="!isStartNow"
                    class="common-form-item">
                    <label class="required">{{i18n.periodicCron}}</label>
                    <div class="common-form-content step-form-item-cron">
                        <LoopRuleSelect
                            ref="loopRuleSelect"
                            :manual-input-value="periodicCron">
                        </LoopRuleSelect>
                    </div>
                </div>
            </div>
        </div>
        <div class="param-info">
            <div class="param-info-title">
                <span>
                    {{ i18n.paramsInfo }}
                </span>
            </div>
            <div>
                <ParameterInfo
                    ref="ParameterInfo"
                    :referenced-variable="pipelineData.constants"
                    :un-referenced-variable="unreferenced"
                    :task-message-loading="taskMessageLoading"
                    @onParameterInfoLoading="onParameterInfoLoading">
                </ParameterInfo>
            </div>
        </div>
        <div class="action-wrapper">
            <bk-button
                class="preview-step-button"
                @click="onGotoSelectNode">
                {{ i18n.previous }}
            </bk-button>
            <bk-button
                class="next-step-button"
                theme="success"
                :disabled="disabledButton"
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
    import BaseInput from '@/components/common/base/BaseInput.vue'
    import ParameterInfo from '@/pages/task/ParameterInfo.vue'
    import LoopRuleSelect from '@/components/common/Individualization/loopRuleSelect.vue'
    export default {
        name: 'TaskParamFill',
        components: {
            BaseInput,
            ParameterInfo,
            LoopRuleSelect
        },
        props: ['cc_id', 'template_id', 'common', 'previewData', 'entrance', 'excludeNode'],
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
                bkMessageInstance: null,
                isSubmit: false,
                isSelectFunctionalType: false,
                taskName: '',
                pipelineData: {},
                unreferenced: {},
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
                taskParamEditLoading: true,
                taskMessageLoading: true,
                disabledButton: true
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
            isTaskTypeShow () {
                return this.userType !== 'functor' && this.isStartNow
            },
            // 不显示【执行计划】的情况
            isExecuteSchemeHide () {
                return this.common || this.viewMode === 'appmaker' || this.userType === 'functor' || (['periodicTask', 'taskflow'].indexOf(this.entrance) > -1)
            }
        },
        mounted () {
            this.loadData()
            this.period()
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
            ...mapActions('periodic/', [
                'createPeriodic'
            ]),
            period () {
                if (this.entrance === 'periodicTask') {
                    this.isStartNow = false
                }
            },
            async loadData () {
                this.taskMessageLoading = true
                try {
                    const data = {
                        templateId: this.template_id,
                        common: this.common
                    }
                    const templateSource = this.common ? 'common' : 'business'
                    const templateData = await this.loadTemplateData(data)
                    this.setTemplateData(templateData)
                    const params = {
                        templateId: this.template_id,
                        excludeTaskNodesId: JSON.stringify(this.excludeNode),
                        common: this.common,
                        cc_id: this.cc_id,
                        template_source: templateSource,
                        version: templateData.version
                    }
                    const previewData = await this.loadPreviewNodeData(params)
                    this.pipelineData = previewData.data.pipeline_tree
                    this.unreferenced = previewData.data.constants_not_referred
                    this.taskName = this.getDefaultTaskName()
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.taskMessageLoading = false
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
                    this.$router.push({ path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/selectnode/`, query: { 'template_id': this.template_id } })
                } else {
                    if (this.common) {
                        this.$router.push({ path: `/template/newtask/${this.cc_id}/selectnode/`, query: { 'template_id': this.template_id, common: this.common } })
                    } else {
                        if (this.entrance !== undefined) {
                            this.$router.push({ path: `/template/newtask/${this.cc_id}/selectnode/`, query: { 'template_id': this.template_id, entrance: this.entrance } })
                        } else {
                            this.$router.push({ path: `/template/newtask/${this.cc_id}/selectnode/`, query: { 'template_id': this.template_id } })
                        }
                    }
                }
            },
            onCreateTask () {
                const loopRule = !this.isStartNow ? this.$refs.loopRuleSelect.validationExpression() : { check: true, rule: '' }
                if (!loopRule.check) return
                if (this.isSubmit) return
                // 页面中是否有 TaskParamEdit 组件
                const paramEditComp = this.$refs.ParameterInfo.getTaskParamEdit()
                this.$validator.validateAll().then(async (result) => {
                    let formValid = true
                    const pipelineData = tools.deepClone(this.pipelineData)
                    // 取最新参数
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
                                    this.$router.push({ path: `/appmaker/${this.app_id}/task_home/${this.cc_id}/` })
                                } else {
                                    this.$router.push({ path: `/appmaker/${this.app_id}/execute/${this.cc_id}/`, query: { instance_id: taskData.instance_id } })
                                }
                            } else if (this.isSelectFunctionalType) {
                                if (this.common) {
                                    this.$router.push({ path: `/taskflow/home/${this.cc_id}/`, query: { common: this.common } })
                                } else {
                                    this.$router.push({ path: `/taskflow/home/${this.cc_id}/` })
                                }
                            } else {
                                if (this.common) {
                                    this.$router.push({ path: `/taskflow/execute/${this.cc_id}/`, query: { instance_id: taskData.instance_id, common: this.common } })
                                } else {
                                    this.$router.push({ path: `/taskflow/execute/${this.cc_id}/`, query: { instance_id: taskData.instance_id } })
                                }
                            }
                        } catch (e) {
                            errorHandler(e, this)
                        } finally {
                            this.isSubmit = false
                        }
                    } else {
                        // 创建周期任务
                        const cronArray = loopRule.rule.split(' ')
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
                        try {
                            await this.createPeriodic(data)
                            this.$bkMessage({
                                'message': gettext('创建周期任务成功'),
                                'theme': 'success'
                            })
                            this.$router.push({ path: `/periodic/home/${this.cc_id}/` })
                        } catch (e) {
                            errorHandler(e, this)
                        } finally {
                            this.isSubmit = false
                        }
                    }
                })
            },
            onChangeStartNow (value) {
                if (value === this.isStartNow) {
                    return
                }
                this.isStartNow = value
                this.$emit('setPeriodicStep', { 'periodicType': value, 'functionalType': this.isSelectFunctionalType })
                if (!value) {
                    this.lastTaskName = this.taskName
                    this.taskName = this.templateName
                } else {
                    this.taskName = this.lastTaskName
                }
            },
            onParameterInfoLoading (val) {
                if (this.taskMessageLoading === false && val === false) {
                    this.disabledButton = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
.param-fill-wrapper {
    position: relative;
    padding-top: 50px;
    padding-bottom: 72px;
    box-sizing: border-box;
    min-height: calc(100vh - 50px - 139px);
    background: #fff;
    /deep/ .no-data-wrapper {
        position: relative;
        top: 122px;
    }
}
.task-info,
.param-info {
    margin: 0 40px 20px 40px;
    .task-info-title,
    .param-info-title {
        font-size: 14px;
        line-height: 32px;
        font-weight: 600;
        color: #313238;
        border-bottom: 1px solid #cacedb;
        margin-bottom: 30px;
    }
    .common-form-item {
        label {
            color: #313238;
            font-weight: normal;
        }
    }
}
.param-info {
    margin: 0 20px 50px 20px;
}
.param-info-title {
    margin: 0 20px 0 20px;
}
.functor-task-info {
    padding-bottom: 0px;
}
.common-section-title {
    margin-bottom: 24px;
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
        border: 1px solid #3a84ff;
    }
    .bk-button:last-child {
        margin-left: -1px;
    }
}
.periodic-img-tooltip {
    position: absolute;
    right: 20px;
    top: 0;
    color: #c4c6cc;
    font-size: 14px;
    z-index: 4;
    &:hover {
        color: #f4aa1a;
    }
    /deep/ .bk-tooltip-arrow {
        display: none;
    }
}
.startnow-form-content,
.periodic-form-content {
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
    border: 1px solid #c4c6cc;
    background-color: #000;
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
    position: relative;
    input {
        vertical-align: top;
    }
}
.action-wrapper {
    position: absolute;
    bottom: 0;
    width: 100%;
    border-top: 1px solid #cacedb;
    background-color: #ffffff;
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
        color: #ffffff;
        background-color: #2dcb56;
        border-color: #2dcb56;
    }
}
</style>
